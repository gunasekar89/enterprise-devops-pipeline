# Rebuild Guide: from clone to a monitored deployment

This is the fresh-start path for a new engineer. Each step links to its runbook and states whether it works today.

| # | Step | Status | Runbook |
|---|---|---|---|
| 1 | Clone the repository | Ready | below |
| 2 | Read prerequisites, create accounts | Ready | [prerequisites.md](prerequisites.md) |
| 3 | Configure credentials securely | Documented; first credentials needed in Phase 1-2 | [prerequisites.md#credentials-to-prepare-never-commit-them](prerequisites.md#credentials-to-prepare-never-commit-them), [security-model.md](security/security-model.md) |
| 4 | Build and test the Java application | **Verified** | [installation/local-development.md](installation/local-development.md) |
| 5 | Install and configure Jenkins | Documented, re-run pending (Phase 1) | [installation/jenkins-on-azure-vm.md](installation/jenkins-on-azure-vm.md) |
| 6 | Configure and run CI | Jenkinsfile verified in Jenkinsfile Runner; job on the VM pending (Phase 1) | [cicd/jenkins-pipeline.md](cicd/jenkins-pipeline.md) |
| 7 | Create and scan the Docker image | **Verified locally** (manual scans) | [local-development.md#container](installation/local-development.md#container), [security-model.md](security/security-model.md) |
| 8 | Provision permitted infrastructure | Planned (Phase 3) | [roadmap.md](roadmap.md) |
| 9 | Deploy the application | Planned (Phase 4) | [roadmap.md](roadmap.md) |
| 10 | Verify health, monitoring and rollback | Health endpoints verified locally; the rest planned (Phases 4-5) | [roadmap.md](roadmap.md) |

## Step 1: Clone

```bash
git clone https://github.com/gunasekar89/enterprise-devops-pipeline.git
cd enterprise-devops-pipeline
```

## Step 4 in one block (copy and paste)

```bash
cd application
./mvnw -B clean verify
java -jar target/enterprise-devops-app.jar &
sleep 15
curl -s localhost:8080/api/hello          # {"message":"Hello, World!","environment":"local"}
curl -s localhost:8080/actuator/health    # {"groups":["liveness","readiness"],"status":"UP"}
kill %1
```

## Step 7 in one block

```bash
cd application
./mvnw -B clean package
docker build -t enterprise-devops-app:local .
docker run --rm -d --name edp -p 8080:8080 enterprise-devops-app:local
sleep 15 && curl -s localhost:8080/actuator/health/readiness   # {"status":"UP"}
docker exec edp id                                              # uid=10001(app) ...
docker rm -f edp
cd ..
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest \
  image --severity HIGH,CRITICAL enterprise-devops-app:local
docker run --rm -v "$PWD":/src:ro zricethezav/gitleaks:latest \
  dir /src --config /src/ci/security/gitleaks.toml --redact --no-banner
```

Vulnerability databases change daily, so Trivy may report new CVEs that did not exist on 2026-10-19. That is the scan working, not the guide being wrong; see [security-model.md](security/security-model.md#handling-a-vulnerable-transitive-dependency) for how to respond.

## When the playground expires

Nothing in this repository depends on a running playground. Start a new one and continue from step 5. Before expiry, export anything you want to keep, for example `sudo tar czf jobs.tgz -C /var/lib/jenkins jobs` and copy it back with `scp`, and save console logs or screenshots into `progress/evidence/`.
