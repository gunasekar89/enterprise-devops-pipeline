# Enterprise DevOps Pipeline

An end-to-end, reproducible software delivery platform for a Java service on Microsoft Azure:
GitHub → Jenkins CI → quality and security gates → Docker → Azure Container Registry → Helm/Argo CD → AKS → Prometheus/Grafana.

The project is built incrementally on short-lived [KodeKloud](https://kodekloud.com) Azure playgrounds. Every step is documented so that any engineer can clone this repository and rebuild the setup from nothing, even after the playground that produced it has expired.

> **Honesty rule.** Each capability below carries a status. "Verified" means there is evidence in [`progress/evidence/`](progress/evidence/). Nothing is claimed as deployed, scanned or production-ready without it.

## Current status (Phase 0, 2026-10-19)

| Capability | Status | Evidence |
|---|---|---|
| Spring Boot REST API (`/api/hello`, health, Prometheus metrics) | Verified | [build-and-test](progress/evidence/phase-0/build-and-test.md) |
| 12 unit, web-layer and integration tests, JaCoCo coverage report | Verified | [build-and-test](progress/evidence/phase-0/build-and-test.md) |
| Non-root Docker image (built from the CI-tested JAR) | Verified locally | [docker-image](progress/evidence/phase-0/docker-image.md) |
| Baseline Jenkinsfile (checkout → env check → compile → test → package → JUnit → archive) | Verified in Jenkinsfile Runner; not yet run on `vm-jenkins-lab` | [jenkins-pipeline-run](progress/evidence/phase-0/jenkins-pipeline-run.md) |
| Gitleaks secret scan and Trivy image scan (run manually) | Verified locally, not yet wired into Jenkins | [security-baseline](progress/evidence/phase-0/security-baseline.md) |
| Jenkins on Azure VM `vm-jenkins-lab`, first pipeline, `jenkins-java-lab` app | Implemented manually (reported; logs not yet in repo) | [IMPLEMENTATION_LOG](progress/IMPLEMENTATION_LOG.md) |
| SonarQube, Snyk, Syft SBOM, Cosign, ACR, Terraform, AKS, Helm, Argo CD, Prometheus, Grafana | Planned | [roadmap](docs/roadmap.md) |

Full tracker: [`progress/PROJECT_STATUS.md`](progress/PROJECT_STATUS.md).

## Architecture at a glance

```mermaid
flowchart LR
    dev[Developer] -->|PR| gh[GitHub<br/>protected main]
    gh -->|poll SCM| jenkins[Jenkins CI]
    subgraph CI[Jenkins pipeline]
        build[Maven build<br/>+ unit tests] --> gates[SonarQube · Gitleaks<br/>Trivy · Snyk]
        gates --> image[Docker build<br/>Git-SHA tag]
        image --> scan[Trivy image scan<br/>Syft SBOM · Cosign sign]
    end
    jenkins --> build
    scan -->|push by digest| acr[(Azure Container<br/>Registry)]
    scan -->|bump image tag| gitops[GitOps repo<br/>Helm values]
    gitops --> argo[Argo CD]
    acr --> aks
    argo -->|sync| aks[AKS]
    aks --> prom[Prometheus] --> graf[Grafana / alerts]
```

Solid boxes up to "Maven build + unit tests" exist today; everything after is the target design described in [`docs/architecture/overview.md`](docs/architecture/overview.md).

## Quick start (local, about 5 minutes)

Prerequisites: JDK 21 and Git. Maven is not required; the wrapper downloads Maven 3.9.11. Docker is optional.

```bash
git clone https://github.com/gunasekar89/enterprise-devops-pipeline.git
cd enterprise-devops-pipeline/application

./mvnw -B clean verify          # compile, 12 tests, JaCoCo report, JAR
java -jar target/enterprise-devops-app.jar
```

In a second terminal:

```bash
curl -s localhost:8080/api/hello?name=Guna
# {"message":"Hello, Guna!","environment":"local"}
curl -s localhost:8080/actuator/health
# {"groups":["liveness","readiness"],"status":"UP"}
curl -s localhost:8080/actuator/prometheus | grep http_server_requests_seconds_count
```

Container (optional):

```bash
docker build -t enterprise-devops-app:local .     # run from application/ after ./mvnw package
docker run --rm -p 8080:8080 -e APP_ENVIRONMENT=docker enterprise-devops-app:local
```

Details, configuration variables and troubleshooting: [`docs/installation/local-development.md`](docs/installation/local-development.md).

## Rebuild the whole project from scratch

Follow [`docs/rebuild-guide.md`](docs/rebuild-guide.md). It lists the ten steps from clone to rollback, marks which ones work today, and links to the runbook for each.

## Repository layout

```
application/          Spring Boot 4.1 / Java 21 service, Maven wrapper, Dockerfile
ci/Jenkinsfile        Declarative pipeline (Script Path for the Jenkins job)
ci/scripts/           Shell helpers used by the pipeline
ci/security/          Scanner configuration (Gitleaks)
docs/                 Architecture, runbooks, security model, troubleshooting, ADRs, interview notes
progress/             Status tracker, implementation journal, lessons learned, next steps, evidence
portfolio/            LinkedIn summary, highlights, evidence checklist
```

Directories for `infrastructure/`, `kubernetes/`, `gitops/` and `observability/` are deliberately not created yet. Each is added in the phase that puts real, tested content in it (see [ADR-0001](docs/decisions/0001-single-repository.md) and the [roadmap](docs/roadmap.md)).

## Documentation map

| Topic | Document |
|---|---|
| Prerequisites and accounts | [docs/prerequisites.md](docs/prerequisites.md) |
| Target architecture | [docs/architecture/overview.md](docs/architecture/overview.md) |
| Local development | [docs/installation/local-development.md](docs/installation/local-development.md) |
| Jenkins on an Azure VM (KodeKloud) | [docs/installation/jenkins-on-azure-vm.md](docs/installation/jenkins-on-azure-vm.md) |
| Jenkins pipeline and job setup | [docs/cicd/jenkins-pipeline.md](docs/cicd/jenkins-pipeline.md) |
| Security model and secrets handling | [docs/security/security-model.md](docs/security/security-model.md) |
| Known issues and fixes | [docs/troubleshooting/known-issues.md](docs/troubleshooting/known-issues.md) |
| Architecture decisions | [docs/decisions/](docs/decisions/README.md) |
| Roadmap | [docs/roadmap.md](docs/roadmap.md) |
| Interview preparation | [docs/interview-notes/](docs/interview-notes/phase-0-foundation.md) |

## Security

No credentials, keys, subscription IDs or IP addresses belong in this repository. See [SECURITY.md](SECURITY.md) for how secrets are handled and how to report a problem.

## License

[MIT](LICENSE)
