# Implementation Log

Chronological journal. Newest entries at the bottom. Each entry: objective, what was done, validation, issues, resolution, next step.

---

## Before 2026-10-19: Manual Azure, Jenkins and Maven exercises (reported by Guna)

*Recorded from Guna's description on 2026-10-19. No logs or screenshots were captured, so these are "Implemented (reported)", not "Verified". Fill in dates and exact messages when known.*

**Objective:** Learn the baseline: an Azure VM running Jenkins that builds a Maven project.

**Done:**
1. Provisioned Ubuntu 24.04 VM `vm-jenkins-lab` in a KodeKloud Azure Playground.
2. Configured SSH connectivity.
3. Installed Java 21, Git, Maven and Jenkins.
4. Configured and ran an initial Jenkins Pipeline successfully.
5. Created a sample Maven Java application `jenkins-java-lab` at `/home/azureuser/devops-labs/jenkins-java-lab`.
6. Ran `mvn clean package`: one unit test passed and a JAR was produced.

**Issues encountered:**
- Resource group creation was not allowed → used the playground's existing group.
- Premium OS disk rejected by policy → used a Standard disk type.
- SSH private-key download failed → workaround to confirm.
- In a separate playground, Jenkins could not use port 8080 because it was already in use.
- Maven printed warnings caused by user permissions.
- Playground resources are temporary.

Details, confirmed versus assumed causes: [known-issues.md](../docs/troubleshooting/known-issues.md).

**Relationship to this repository:** the original `jenkins-java-lab` source stayed on the VM and is not available here. Phase 0 replaces it with a new Spring Boot service in `application/` (see 2026-10-19 entry). Differences: Spring Boot instead of a plain Maven quickstart; REST endpoints, actuator and metrics; 12 tests instead of 1; Maven wrapper; Dockerfile. If the original source is recovered, it can be added under `docs/history/` for reference, not as the build.

---

## 2026-10-19: Phase 0 foundation

**Objective:** A buildable, documented foundation that survives the loss of any playground.

**Workspace inspection:** the working environment was empty: no earlier source, no Enterprise DevOps documentation starter pack, no Git repository. The GitHub repository `gunasekar89/enterprise-devops-pipeline` could not be checked because GitHub access was not linked to the session, so it is unknown whether it already exists. Everything below was created new; nothing existing was overwritten.

**Done:**
1. Created the repository layout (only folders with real content).
2. Built a Spring Boot 4.1.1 / Java 21 API: `/api/hello`, actuator health with liveness/readiness groups, info with build metadata, Prometheus metrics with `application` and `environment` tags, env-var configuration, graceful shutdown.
3. Wrote 12 tests across three layers; added JaCoCo, Maven Enforcer (Java 21+, Maven 3.9+) and the Maven wrapper (3.9.11).
4. Wrote a two-stage Dockerfile that packages the CI-built JAR into a layered, non-root (UID 10001) image.
5. Wrote `ci/Jenkinsfile` (checkout, environment check, compile, test + JUnit, package, archive + fingerprint; SCM polling; opt-in Gitleaks, Trivy, SonarQube, Docker and ACR stages) plus `verify-environment.sh`, `require-tool.sh`, `gitleaks.toml`.
6. Ran the Jenkinsfile in Jenkinsfile Runner (a headless Jenkins in Docker), because no Jenkins server was available in this environment.
7. Ran Gitleaks and Trivy via Docker; remediated CVEs.
8. Wrote documentation, ADRs, tracker, portfolio.

**Validation:** see `progress/evidence/phase-0/`. Summary: `./mvnw -B clean verify` → 12 tests, 0 failures, BUILD SUCCESS. Jenkinsfile Runner → `Finished: SUCCESS`, 6 stages executed, 5 opt-in stages skipped; with `RUN_SECRET_SCAN=true` and no Gitleaks → `Finished: FAILURE` with a clear message; with `PUSH_TO_ACR=true` → `Finished: FAILURE` "planned for Phase 3"; with `BUILD_IMAGE=true` and no Docker on the agent → `Finished: FAILURE`. Container runs as `uid=10001(app)`, health `UP`. Gitleaks: no leaks. Trivy: 0 high/critical after fixes.

**Issues and resolutions:**
- Maven used Java 8 from `JAVA_HOME` although Java 21 was on `PATH` → verify script now checks `JAVA_HOME`'s JDK; Jenkins guide sets `JAVA_HOME` on the node (known-issues #7).
- Trivy found 3 critical CVEs in Tomcat 11.0.24 and 5 high in Jackson 3.1.5 (managed by Spring Boot 4.1.1) → overrode to Tomcat 11.0.27 and Jackson 3.1.8; tests and rescan clean (known-issues #8).
- JDK 21 dynamic agent warnings in tests → Surefire `argLine` flags (known-issues #9).
- The Jenkins plugin update site was unreachable from this environment, so a full Jenkins LTS server with chosen plugins could not be started. Used the `jenkins/jenkinsfile-runner` image (older Jenkins with bundled Pipeline, Git and JUnit plugins) instead. Two harness-only edits, listed in the evidence: `checkout scm` replaced by an explicit Git checkout of the local snapshot, and `timestamps()` removed (Timestamper not bundled). `JAVA_HOME` was injected to stand in for the node setting.

**Next:** see [NEXT_STEPS.md](NEXT_STEPS.md).

---

## 2026-10-19: Fresh start confirmed

Guna confirmed that the GitHub account has no existing repository for this project and that the Azure VM `vm-jenkins-lab` has been deleted. Consequences:
- The original `jenkins-java-lab` source is gone; `application/` is now the only codebase.
- Phase 1 rebuilds Jenkins from scratch by following `docs/installation/jenkins-on-azure-vm.md`, which also serves as the first real test of that runbook.
- Publishing Phase 0 to a new, empty `gunasekar89/enterprise-devops-pipeline` repository was approved.

---

## 2026-10-20: Phase 1 VM rebuilt through the Azure portal

- Guna created `vm-jenkins-lab` by hand in the portal (to learn each setting): Ubuntu 24.04, `Standard_D2s_v3`, Standard SSD, SSH key from the workstation, inbound SSH only from the engineer's IP. SSH from the Mac works.
- Installing Jenkins failed with `NO_PUBKEY 7198F4B714ABFC68`: the runbook still used `jenkins.io-2023.key`, which expired on 2026-03-26. Switched the runbook to `jenkins.io-2026.key` (known-issues #10). First real finding from re-running the runbook.
- 2026-10-20: first push-triggered build test
