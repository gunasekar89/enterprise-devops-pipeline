# Project Highlights

For README badges, interviews and CV bullets. Every line must stay true; each links to its evidence.

## Problem statement

Teams often have CI that builds code, security tools run occasionally, and deployments done by hand. This project shows one integrated path from commit to monitored workload where every gate is automated, every artifact is traceable to a commit, and the whole platform can be rebuilt from Git, under the constraints of a restricted, short-lived cloud sandbox.

## Verified highlights (Phase 0)

| Highlight | Evidence |
|---|---|
| Java 21 / Spring Boot 4.1 service with liveness, readiness and Prometheus endpoints | [build-and-test](../progress/evidence/phase-0/build-and-test.md) |
| 12 tests over three layers, including a test that enforces hidden sensitive endpoints | [build-and-test](../progress/evidence/phase-0/build-and-test.md) |
| Jenkinsfile verified end-to-end in a headless Jenkins; opt-in stages proven to fail rather than fake success | [jenkins-pipeline-run](../progress/evidence/phase-0/jenkins-pipeline-run.md) |
| Found and fixed 3 critical and 5 high CVEs present in the newest Spring Boot release's managed dependencies | [security-baseline](../progress/evidence/phase-0/security-baseline.md) |
| Non-root (UID 10001), layered container image built from the tested artifact | [docker-image](../progress/evidence/phase-0/docker-image.md) |
| Pipeline self-check caught a `JAVA_HOME`/`PATH` JDK mismatch before it reached the real Jenkins | [known-issues #7](../docs/troubleshooting/known-issues.md) |

## Reported (manual, evidence pending)

- Jenkins on an Ubuntu 24.04 Azure VM in a KodeKloud sandbox, first pipeline and Maven build succeeded, working around resource-group and Premium-disk policy restrictions.

## Technical challenges and resolutions

1. **Restricted sandbox IAM and policy** → reuse the provided resource group, Standard disks, design IaC around inputs.
2. **No inbound access to Jenkins** → SSH tunnel plus SCM polling (ADR-0004).
3. **Framework-managed CVEs** → targeted version overrides with removal criteria.
4. **No Jenkins server in the build environment** → Jenkinsfile Runner to test the pipeline itself.

## Not claimed

No production traffic, no high availability, no AKS deployment, no certifications or performance gains. These will appear here only with evidence.
