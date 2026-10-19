# Prerequisites

What you need before each phase. Install only what the phase you are working on requires.

## Accounts

| Account | Needed from | Notes |
|---|---|---|
| GitHub | Phase 1 | Repository `enterprise-devops-pipeline`. A fine-grained personal access token only if the repository is private (read-only `Contents` scope for Jenkins). |
| KodeKloud with Azure Playground access | Phase 1 | Playgrounds are temporary (session length depends on your plan). Expect every resource to disappear. |
| SonarCloud or self-hosted SonarQube | Phase 2 | Self-hosted runs as a container on the Jenkins VM or locally. |
| Snyk (optional) | Phase 2 | Free tier token. |

## Workstation tools

| Tool | Version | Phase | Check |
|---|---|---|---|
| Git | 2.40+ | 0 | `git --version` |
| JDK | 21 (any vendor: Temurin, Ubuntu OpenJDK, Microsoft Build of OpenJDK) | 0 | `java -version` shows `21` |
| Maven | not required; `./mvnw` downloads 3.9.11 | 0 | `cd application && ./mvnw -v` |
| curl | any | 0 | `curl --version` |
| Docker Engine or Docker Desktop (or Colima on macOS) | 24+ | 0 (optional) / 2 | `docker version` |
| OpenSSH client | any | 1 | `ssh -V` |
| Azure CLI | 2.60+ | 1 | `az version` |
| Terraform | 1.9+ | 3 | `terraform version` |
| kubectl, Helm | current stable | 4 | `kubectl version --client`, `helm version` |

Scanners (Gitleaks, Trivy, Syft, Cosign) can run as Docker images, so they do not need to be installed locally. Commands are in [security-model.md](security/security-model.md).

## Jenkins VM (Phase 1)

| Item | Value used |
|---|---|
| OS | Ubuntu 24.04 LTS |
| Size | A 2 vCPU / 4-8 GiB size permitted by the playground (Maven builds plus Jenkins need at least 2 GiB free) |
| OS disk | Standard SSD (`StandardSSD_LRS`). Premium was rejected by playground policy. |
| Packages | `openjdk-21-jdk`, `git`, `jenkins` (LTS); Maven comes from the wrapper |
| Network | Inbound TCP 22 from your IP only. 8080 is not opened. |
| Jenkins plugins | Suggested plugins (includes Pipeline, Git, JUnit, Timestamper, Credentials Binding) |

Step-by-step: [installation/jenkins-on-azure-vm.md](installation/jenkins-on-azure-vm.md).

## Credentials to prepare (never commit them)

| Jenkins credential ID | Type | Used by | Phase |
|---|---|---|---|
| `github-token` | Username with password (GitHub user + PAT) | Checkout of a private repository | 1, only if private |
| SonarQube server token | Secret text, referenced by the `sonarqube` server entry | `SonarQube Analysis` stage | 2 |
| `snyk-token` | Secret text | Snyk stage | 2 (optional) |
| `azure-sp` or workload identity | Azure service principal | ACR push, Terraform | 3 |
| `cosign-key` / keyless | Secret file or OIDC | Image signing | 3 |

The Jenkinsfile only refers to these IDs; the values live in Jenkins.
