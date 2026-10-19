# Evidence Checklist

What to capture for each milestone before marking it Verified. Store text logs as Markdown in `progress/evidence/<phase>/`; store screenshots as PNG next to them. Before committing, remove IPs, subscription and tenant IDs, usernames you do not want public, and tokens.

## Phase 0

- [x] `./mvnw -B clean verify` output with test counts → `phase-0/build-and-test.md`
- [x] Endpoint responses (`/api/hello`, health, info, prometheus) → `phase-0/build-and-test.md`
- [x] Docker image build, `id` inside container, health → `phase-0/docker-image.md`
- [x] Jenkinsfile Runner console: success run and two expected-failure runs → `phase-0/jenkins-pipeline-run.md`
- [x] Gitleaks and Trivy results before and after remediation → `phase-0/security-baseline.md`

## Historical manual work (add if you still have them)

- [ ] Screenshot or `az vm show -o table` of `vm-jenkins-lab` (redact IPs)
- [ ] Console log of the first Jenkins pipeline run
- [ ] `mvn clean package` output for `jenkins-java-lab`
- [ ] The exact policy error messages (resource group, Premium disk)

## Phase 1

- [ ] GitHub repository page and branch protection rule
- [ ] Jenkins job configuration page (SCM, Script Path)
- [ ] Stage view of a green build, Test Result page (12 tests), Build Artifacts
- [ ] Git Polling Log showing an automatic build after a push
- [ ] `ss -ltnp` showing Jenkins bound to 127.0.0.1

## Phase 2

- [ ] SonarQube project dashboard and quality gate result
- [ ] Failing build caused by a planted fake secret or a vulnerable dependency, and the green build after removing it
- [ ] Archived SBOM

## Phase 3-5

- [ ] `terraform plan` summary, ACR repository with digest, `cosign verify` output
- [ ] Argo CD application synced/healthy, rollback drill before and after
- [ ] Grafana dashboard, fired alert, RCA document
