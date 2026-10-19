# Evidence: Jenkins Pipeline Run (Phase 0)

- **Date:** 2026-10-19
- **Commit under test:** `1ff7816`
- **Runner:** `jenkins/jenkinsfile-runner` Docker image (Jenkins core 2.346.1 with bundled Pipeline, Git and JUnit plugins), plus Git added to the image. A full Jenkins LTS server could not be used because the Jenkins plugin update site was unreachable from this environment.
- **Not yet done:** running the job on `vm-jenkins-lab` (Phase 1).

## Harness-only differences from `ci/Jenkinsfile`

These edits were applied to a temporary copy only. The committed Jenkinsfile is unchanged.

```diff
17d16
<         timestamps()
43a43
>         JAVA_HOME  = '/opt/jdk21'  // harness only: stands in for the node's JAVA_HOME setting
54c54
<                     def scmVars = checkout scm
---
>                     def scmVars = checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'file:///repo/src.git']]])
```

1. `timestamps()` removed: the Timestamper plugin is not bundled in the runner image. It is part of Jenkins' suggested plugins on a normal install.
2. `JAVA_HOME` set: the runner itself needs Java 8; this stands in for setting `JAVA_HOME` on the Jenkins node (installation guide step 7).
3. `checkout scm` replaced: the runner has no job SCM configuration, so the commit is checked out explicitly from a local bare clone.

## Run 1: default parameters (expected SUCCESS)

```text
[Pipeline] { (1. Checkout)
Building 1ff781666f8844c2f020c0c3e9348d4ffe2d94f1 from unknown branch
[Pipeline] { (2. Verify Environment)
user: root (0)  host: vm  workspace: /build
commit: 1ff781666f8844c2f020c0c3e9348d4ffe2d94f1
openjdk version "21.0.12.1" 2026-08-18 LTS
Apache Maven 3.9.11 (3e54c93a704957b63ee3494413a2b544fd3d825b)
Environment OK
[Pipeline] { (3. Compile)
[INFO] Building enterprise-devops-app 0.1.0-SNAPSHOT
[INFO] BUILD SUCCESS
[Pipeline] { (4. Unit Tests)
[INFO] Building enterprise-devops-app 0.1.0-SNAPSHOT
[INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
Recording test results
[Pipeline] { (5. Package)
[INFO] Building enterprise-devops-app 0.1.0-SNAPSHOT
[INFO] BUILD SUCCESS
[Pipeline] { (6. Archive Artifacts)
Archiving artifacts
Recording fingerprints
Archiving artifacts
[Pipeline] { (Secret Scan (Gitleaks))
Stage "Secret Scan (Gitleaks)" skipped due to when conditional
[Pipeline] { (Dependency Scan (Trivy))
Stage "Dependency Scan (Trivy)" skipped due to when conditional
[Pipeline] { (SonarQube Analysis)
Stage "SonarQube Analysis" skipped due to when conditional
[Pipeline] { (Docker Build)
Stage "Docker Build" skipped due to when conditional
[Pipeline] { (Push to ACR)
Stage "Push to ACR" skipped due to when conditional
[Pipeline] { (Declarative: Post Actions)
CI passed for 1ff7816. Artifact: application/target/enterprise-devops-app.jar
Finished: SUCCESS
```

## Run 2: `RUN_SECRET_SCAN=true` without Gitleaks installed (expected FAILURE)

```text
[Pipeline] { (Secret Scan (Gitleaks))
+ bash ci/scripts/require-tool.sh gitleaks
ERROR: 'gitleaks' is not installed on this Jenkins agent.
Install it or untick the matching build parameter. See docs/security/security-model.md.
Finished: FAILURE
```

## Run 3: `PUSH_TO_ACR=true` (expected FAILURE, not implemented)

```text
[Pipeline] { (Push to ACR)
ERROR: PUSH_TO_ACR is planned for Phase 3 and is not implemented yet. See docs/roadmap.md.
Finished: FAILURE
```

## Run 4: `BUILD_IMAGE=true` without Docker on the agent (expected FAILURE)

```text
[Pipeline] { (Docker Build)
+ bash ci/scripts/require-tool.sh docker
ERROR: 'docker' is not installed on this Jenkins agent.
Finished: FAILURE
```

Conclusion: the baseline stages pass, test results and fingerprinted artifacts are recorded, and opt-in stages fail with an explanation instead of reporting success.

## Finding during this run

The first attempt failed in "Compile": Maven used Java 8 from `JAVA_HOME` although Java 21 was first on `PATH`. The Maven Enforcer rule stopped the build. `verify-environment.sh` was changed to check the JDK that Maven will use. See known-issues #7.
