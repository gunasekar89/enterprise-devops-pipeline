# Roadmap

Each phase ends with evidence in `progress/evidence/<phase>/` and an updated tracker. A phase can be split across several playground sessions; the repository carries the state between them.

## Playground constraints that shape every phase

From KodeKloud's published limits and forum reports (researched 2026-10-20; see [known-issues #6](troubleshooting/known-issues.md#6-kodekloud-sandbox-limitations)):

- **3-hour sessions**, wiped at the end. Every session starts from an empty subscription, so each phase's setup must be scripted and fast.
- **One fixed resource group**; no new ones.
- **VMs up to `Standard_D2s_v3`** (2 vCPU / 8 GB); **Standard SSD/HDD disks only**, max 128 GB.
- **No role assignments.** AKS cannot get `AcrPull`, service principals and managed identities cannot be granted roles. Registry access uses an ACR token or the admin user instead ([ADR-0007](decisions/0007-registry-auth-without-role-assignments.md)).
- **AKS: one node pool, max 2 small nodes, monitoring add-ons off.**
- **Terraform state** cannot outlive the session in Azure, so it stays local per session or goes to Terraform Cloud ([ADR-0006](decisions/0006-terraform-for-azure.md)).
- Unconfirmed and to test in the first session: whether NSGs, public IPs, user-assigned managed identities and Key Vault access-policy mode are allowed.

## Phase 0: Foundation (current)

Repository, Spring Boot service with tests, Dockerfile, baseline Jenkinsfile, documentation framework, tracker, portfolio skeleton. **No cloud resources.**

## Phase 1: Source control and CI on Azure

- Publish the repository to GitHub; enable branch protection on `main` (PR required, Jenkins check required, no force-push), Dependabot alerts, private vulnerability reporting, CODEOWNERS.
- Run the 5-minute feasibility check in the first session (NSG, public IP, managed identity, Key Vault, ACR token) and record the results in known-issues #6.
- Rebuild `vm-jenkins-lab` (`Standard_D2s_v3`, `StandardSSD_LRS`) in a fresh playground from [installation/jenkins-on-azure-vm.md](installation/jenkins-on-azure-vm.md), correcting the runbook where reality differs.
- Script the VM and Jenkins setup (cloud-init or a bootstrap script) so it can be rebuilt inside a 3-hour session, and keep job definitions in Git.
- Create the `enterprise-devops-pipeline` job, confirm polling triggers a build after a push, capture console log and screenshots as evidence.
- Evaluate GitHub Branch Source / multibranch pipeline so PRs get a Jenkins status check (outbound API only).
- **Exit criteria:** a commit pushed to GitHub produces a green Jenkins build without manual action; evidence committed.

## Phase 2: DevSecOps gates and container

- SonarQube (container on the VM, bound to localhost) with a quality gate; `RUN_SONARQUBE` on by default. Jenkins, SonarQube and Docker builds share 8 GB, so cap SonarQube's heaps (about 2 GB total) and set `vm.max_map_count=524288`.
- Gitleaks and Trivy installed on the agent; stages mandatory on `main`.
- Optional Snyk with a `snyk-token` credential.
- Docker on the agent; image tagged with the Git SHA; Trivy image scan; Syft SBOM archived.
- Pin base images by digest; consider a smaller runtime base.
- **Exit criteria:** a deliberately vulnerable dependency or planted fake secret fails the build; removing it turns it green.

## Phase 3: Azure infrastructure as code and registry

- Terraform (ADR-0006) for VNet, NSG (if allowed), Jenkins VM and ACR (Standard SKU); resource group as a data source; disk type set explicitly to `StandardSSD_LRS`; local state per session or Terraform Cloud.
- No role-based identities: Jenkins pushes to ACR with a repository-scoped ACR token stored in Jenkins Credentials ([ADR-0007](decisions/0007-registry-auth-without-role-assignments.md)). ACR Tasks (`az acr build`) are not available, so images are built on Jenkins and pushed with `docker push`.
- Push the image to ACR, record the digest; Cosign sign with a locally generated key stored as a Key Vault secret (access-policy mode), or keyless.
- **Exit criteria:** `terraform plan` is clean against the playground; image in ACR with a verifiable signature.

## Phase 4: Kubernetes, Helm and GitOps

- AKS via Terraform: one system node pool, 2 nodes (`Standard_D2s_v3`, fall back to `Standard_B2s`), manual scale, default networking, no monitoring add-ons.
- Image pulls through an `imagePullSecret` built from a pull-only ACR token, wired in through Helm values (`AcrPull` attach is blocked, ADR-0007).
- Keep the same Helm chart and Argo CD apps runnable on kind or k3d, so Kubernetes work is not blocked by the 3-hour clock or AKS limits.
- `kubernetes/helm/enterprise-devops-app` chart: Deployment with probes on `/actuator/health/liveness|readiness`, resources, `runAsNonRoot`, read-only root FS; Service; values per environment.
- Argo CD (ADR-0003) with `dev` auto-sync and `prod` promoted by pull request.
- Post-deploy smoke test; rollback drill via Git revert and Argo CD history.
- **Exit criteria:** a commit reaches `dev` automatically; a bad release is rolled back and the drill is documented.

## Phase 5: Observability and SRE

- kube-prometheus-stack (Prometheus, Grafana, Alertmanager) via Helm; ServiceMonitor for the app. Two small nodes are tight alongside Argo CD: trim the stack (short retention, explicit requests, fewer exporters) or run the monitoring demo on kind/k3d. Azure Monitor Container Insights is blocked.
- Grafana dashboard for the RED metrics (rate, errors, duration) and JVM health; SLO and error-budget panel.
- Alert rules (high error rate, latency, pod restarts, target down) and a runbook per alert.
- Structured JSON logs and trace IDs (Micrometer Tracing / OpenTelemetry), with a log backend if the playground allows.
- **Exit criteria:** an injected fault fires an alert, and the incident is investigated and written up as an RCA.

## Phase 6: Resilience and disaster recovery

- Jenkins backup and restore (JCasC for configuration, job definitions from Git).
- Full rebuild drill in a brand-new playground using only this repository; time it. Every 3-hour session is effectively a DR drill, so record the rebuild time each session.
- Keep all Jenkins state outside Azure (JCasC and job definitions in Git), because nothing in the playground survives the session.
- Chaos exercises (kill pods, drain a node, break a dependency) with RCAs.
- **Exit criteria:** documented RTO for a full rebuild, and at least two RCAs.

## Later options

Split repositories (ADR-0001), Jenkins agents on Kubernetes, policy-as-code (Kyverno or Gatekeeper) to verify signatures, a database with backup/restore, cost reporting.
