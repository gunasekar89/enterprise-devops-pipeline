# Security Policy

## Reporting a problem

If you find a vulnerability or a committed secret in this repository, please do not open a public issue. Use GitHub's private vulnerability reporting (Security tab → "Report a vulnerability") on `gunasekar89/enterprise-devops-pipeline`. If a real credential was exposed, it will be revoked first and removed from history second.

## Supported versions

Only the `main` branch is maintained.

## How secrets are handled

| Secret | Where it lives | Never |
|---|---|---|
| SSH private key for the lab VM | The engineer's workstation, `chmod 600` | In Git, in Jenkins job config, in chat |
| GitHub access for Jenkins (when the repo is private) | Jenkins Credentials, ID `github-token` (planned) | In the Jenkinsfile |
| SonarQube token | Jenkins Credentials via the SonarQube server config (planned) | In `pom.xml` or `sonar-project.properties` |
| Azure service principal / workload identity | Jenkins Credentials or Azure Key Vault (planned) | In Terraform files or `.tfvars` committed to Git |
| Cosign signing key | Azure Key Vault or keyless OIDC (planned) | On the Jenkins disk unencrypted |

`.gitignore` blocks common secret files (`*.pem`, `*.key`, `.env`, `*.tfvars`, `*.tfstate`, `kubeconfig*`). Gitleaks (`ci/security/gitleaks.toml`) scans the tree and history; see [`docs/security/security-model.md`](docs/security/security-model.md).

## Exposure defaults

Jenkins, SonarQube and Grafana are not exposed to the Internet by default. Access is through an SSH tunnel from the engineer's machine. The application exposes only the `health`, `info` and `prometheus` actuator endpoints.
