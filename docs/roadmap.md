# Roadmap

Each phase ends with evidence in `progress/evidence/<phase>/` and an updated tracker. A phase can be split across several playground sessions; the repository carries the state between them.

## Phase 0: Foundation (current)

Repository, Spring Boot service with tests, Dockerfile, baseline Jenkinsfile, documentation framework, tracker, portfolio skeleton. **No cloud resources.**

## Phase 1: Source control and CI on Azure

- Publish the repository to GitHub; enable branch protection on `main` (PR required, Jenkins check required, no force-push), Dependabot alerts, private vulnerability reporting, CODEOWNERS.
- Rebuild `vm-jenkins-lab` in a fresh playground from [installation/jenkins-on-azure-vm.md](installation/jenkins-on-azure-vm.md), correcting the runbook where reality differs.
- Create the `enterprise-devops-pipeline` job, confirm polling triggers a build after a push, capture console log and screenshots as evidence.
- Evaluate GitHub Branch Source / multibranch pipeline so PRs get a Jenkins status check (outbound API only).
- **Exit criteria:** a commit pushed to GitHub produces a green Jenkins build without manual action; evidence committed.

## Phase 2: DevSecOps gates and container

- SonarQube (container on the VM, bound to localhost) with a quality gate; `RUN_SONARQUBE` on by default.
- Gitleaks and Trivy installed on the agent; stages mandatory on `main`.
- Optional Snyk with a `snyk-token` credential.
- Docker on the agent; image tagged with the Git SHA; Trivy image scan; Syft SBOM archived.
- Pin base images by digest; consider a smaller runtime base.
- **Exit criteria:** a deliberately vulnerable dependency or planted fake secret fails the build; removing it turns it green.

## Phase 3: Azure infrastructure as code and registry

- Terraform (ADR-0006) for VNet, NSG, Jenkins VM, ACR (admin user disabled), identities; resource group as a data source.
- Push the image to ACR, record the digest; Cosign sign (Key Vault key or keyless).
- Document what the playground allows (role assignments, storage for state) before depending on it.
- **Exit criteria:** `terraform plan` is clean against the playground; image in ACR with a verifiable signature.

## Phase 4: Kubernetes, Helm and GitOps

- AKS (smallest permitted node pool) via Terraform, attached to ACR with `AcrPull`.
- `kubernetes/helm/enterprise-devops-app` chart: Deployment with probes on `/actuator/health/liveness|readiness`, resources, `runAsNonRoot`, read-only root FS; Service; values per environment.
- Argo CD (ADR-0003) with `dev` auto-sync and `prod` promoted by pull request.
- Post-deploy smoke test; rollback drill via Git revert and Argo CD history.
- **Exit criteria:** a commit reaches `dev` automatically; a bad release is rolled back and the drill is documented.

## Phase 5: Observability and SRE

- kube-prometheus-stack (Prometheus, Grafana, Alertmanager) via Helm; ServiceMonitor for the app.
- Grafana dashboard for the RED metrics (rate, errors, duration) and JVM health; SLO and error-budget panel.
- Alert rules (high error rate, latency, pod restarts, target down) and a runbook per alert.
- Structured JSON logs and trace IDs (Micrometer Tracing / OpenTelemetry), with a log backend if the playground allows.
- **Exit criteria:** an injected fault fires an alert, and the incident is investigated and written up as an RCA.

## Phase 6: Resilience and disaster recovery

- Jenkins backup and restore (JCasC for configuration, job definitions from Git).
- Full rebuild drill in a brand-new playground using only this repository; time it.
- Chaos exercises (kill pods, drain a node, break a dependency) with RCAs.
- **Exit criteria:** documented RTO for a full rebuild, and at least two RCAs.

## Later options

Split repositories (ADR-0001), Jenkins agents on Kubernetes, policy-as-code (Kyverno or Gatekeeper) to verify signatures, a database with backup/restore, cost reporting.
