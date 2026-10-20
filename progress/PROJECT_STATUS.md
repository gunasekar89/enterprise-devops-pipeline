# Project Status

Last updated: 2026-10-20 (Phase 1)

**States:** Planned · In Progress · Implemented · Verified · Blocked.
**Verified** requires evidence in `progress/evidence/`. Work done by hand before this repository existed is marked *Implemented (reported)* until logs or screenshots are added.

## Phase summary

| Phase | Scope | State |
|---|---|---|
| 0 | Foundation: repo, app, tests, Dockerfile, baseline Jenkinsfile, docs | **Verified** (local and Jenkinsfile Runner) |
| 1 | GitHub, branch protection, Jenkins on Azure VM running this pipeline | **Verified** except branch protection (P1-2) |
| 2 | SonarQube, Gitleaks, Trivy, Snyk, Docker in CI, SBOM | Planned (Gitleaks and Trivy run manually in Phase 0) |
| 3 | Terraform, ACR, Cosign, identities | Planned |
| 4 | AKS, Helm, Argo CD, rollback | Planned |
| 5 | Prometheus, Grafana, alerting, RCA | Planned (app metrics endpoint ready) |
| 6 | Backup, full rebuild drill, chaos | Planned |

## Capability tracker

| ID | Capability | State | Date | Evidence / notes |
|---|---|---|---|---|
| H-1 | Azure VM `vm-jenkins-lab` (Ubuntu 24.04) in KodeKloud playground | Implemented (reported) | before 2026-10-19 (exact date to confirm) | Manual. **VM deleted by Guna on 2026-10-19**; to be rebuilt from the runbook in Phase 1. |
| H-2 | SSH access to the VM | Implemented (reported) | before 2026-10-19 | Private-key download failed; workaround to confirm (known-issues #3) |
| H-3 | Java 21, Git, Maven, Jenkins installed on the VM | Implemented (reported) | before 2026-10-19 | |
| H-4 | Initial Jenkins pipeline executed successfully | Implemented (reported) | before 2026-10-19 | Console log not captured |
| H-5 | `jenkins-java-lab` Maven app: `mvn clean package`, 1 test passed, JAR produced | Implemented (reported) | before 2026-10-19 | Source was on the VM at `/home/azureuser/devops-labs/jenkins-java-lab`; **lost with the VM** (replaced by `application/`) |
| P0-1 | Repository structure, license, contribution and security policies | Verified | 2026-10-19 | This repository |
| P0-2 | Spring Boot 4.1.1 / Java 21 REST API with env-based config | Verified | 2026-10-19 | [build-and-test](evidence/phase-0/build-and-test.md) |
| P0-3 | Health (liveness/readiness), info, Prometheus endpoints; sensitive endpoints hidden | Verified | 2026-10-19 | [build-and-test](evidence/phase-0/build-and-test.md) |
| P0-4 | 12 tests (unit, web slice, integration), JaCoCo report | Verified | 2026-10-19 | [build-and-test](evidence/phase-0/build-and-test.md) |
| P0-5 | Non-root layered Docker image | Verified (local Docker) | 2026-10-19 | [docker-image](evidence/phase-0/docker-image.md) |
| P0-6 | Baseline Jenkinsfile, stages 1-6 | Verified (Jenkinsfile Runner, then on `vm-jenkins-lab` in P1-3) | 2026-10-19 | [jenkins-pipeline-run](evidence/phase-0/jenkins-pipeline-run.md) |
| P0-7 | Opt-in stages fail when tools are missing | Verified (Gitleaks, Docker and ACR stages tested) | 2026-10-19 | [jenkins-pipeline-run](evidence/phase-0/jenkins-pipeline-run.md) |
| P0-8 | Gitleaks scan of tree and history | Verified (manual, Docker) | 2026-10-19 | [security-baseline](evidence/phase-0/security-baseline.md) |
| P0-9 | Trivy image and config scan; CVEs remediated | Verified (manual, Docker) | 2026-10-19 | [security-baseline](evidence/phase-0/security-baseline.md) |
| P0-10 | Documentation set, ADRs, rebuild guide, roadmap | Implemented | 2026-10-19 | Runbooks for Phases 1+ not yet re-run |
| P1-1 | Publish to GitHub `gunasekar89/enterprise-devops-pipeline` | Verified | 2026-10-20 | Public repo created with `gh`; `main` at 6557d93 pushed. [workstation-setup](evidence/phase-1/workstation-setup.md) |
| P1-0 | Engineer workstation (macOS, Apple silicon): clone, JDK 21, build and 12 tests pass | Verified | 2026-10-20 | [workstation-setup](evidence/phase-1/workstation-setup.md) |
| P1-2 | Branch protection on `main` | Planned | | |
| P1-3 | Jenkins job on `vm-jenkins-lab` running `ci/Jenkinsfile` via polling | Verified | 2026-10-20 | Jenkins 2.580.1 on a portal-built VM, localhost-only behind an SSH tunnel. Build #1 manual and build #2 started by an SCM change, both green with 12 tests. [jenkins-first-builds](evidence/phase-1/jenkins-first-builds.md) |
| P2-x | SonarQube, Snyk, Syft, Gitleaks/Trivy in CI | Planned | | |
| P3-x | Terraform, ACR, Cosign | Planned | | |
| P4-x | AKS, Helm, Argo CD, rollback | Planned | | |
| P5-x | Prometheus, Grafana, alerts | Planned | | |

## Open risks

- Playground blocks role assignments (documented by KodeKloud): registry access uses scoped ACR tokens (ADR-0007), a known gap versus production managed identities.
- 3-hour sessions: every phase's setup must be scripted to fit inside one session.
- AKS is capped at 2 small nodes; Argo CD plus kube-prometheus-stack may not fit, so kind/k3d is the fallback.
- NSG, public IP and managed identity support is unconfirmed until the first-session feasibility check.
- The Jenkins VM is wiped with each playground; Jenkins configuration (node `JAVA_HOME`, job) is still manual until Configuration as Code is added.
- Historical details (exact errors, which disk SKU, SSH workaround) are incomplete until Guna confirms them.
