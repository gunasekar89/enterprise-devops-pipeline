# Evidence: first Jenkins builds on `vm-jenkins-lab` (Phase 1)

Date: 2026-10-20. Jenkins 2.580.1 LTS on Ubuntu 24.04 (`Standard_D2s_v3`, KodeKloud Azure playground), built by hand through the Azure portal and [jenkins-on-azure-vm.md](../../../docs/installation/jenkins-on-azure-vm.md). Jenkins listens on `127.0.0.1:8080` only and is reached through an SSH tunnel. Console logs were copied from the Jenkins UI by Guna; excerpts below are verbatim.

Console timestamps of build #2 show browser local time (IST, UTC+5:30); Maven's `Finished at` lines are UTC.

## Listener check

```
$ sudo ss -ltnp | grep 8080
LISTEN 0      50     [::ffff:127.0.0.1]:8080            *:*    users:(("java",pid=5468,fd=9))
```

## Build #1: manual, commit 4636e5a

```
Started by user admin
Obtained ci/Jenkinsfile from git https://github.com/gunasekar89/enterprise-devops-pipeline.git
05:51:16  Checking out Revision 4636e5a0e6cc42820b56a93afbdc6cbfc11f303c (refs/remotes/origin/main)
05:51:17  JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
05:51:17  openjdk version "21.0.12.1" 2026-08-18
05:51:18  Apache Maven 3.9.11 (3e54c93a704957b63ee3494413a2b544fd3d825b)
05:51:18  Environment OK
05:51:35  [INFO] Rule 0: org.apache.maven.enforcer.rules.version.RequireJavaVersion passed
05:52:09  [INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
05:52:21  [INFO] Building jar: .../application/target/enterprise-devops-app.jar
05:52:21  Archiving artifacts
05:52:21  Recording fingerprints
Stage "Secret Scan (Gitleaks)" skipped due to when conditional
Stage "Dependency Scan (Trivy)" skipped due to when conditional
Stage "SonarQube Analysis" skipped due to when conditional
Stage "Docker Build" skipped due to when conditional
Stage "Push to ACR" skipped due to when conditional
05:52:23  CI passed for 4636e5a. Artifact: application/target/enterprise-devops-app.jar
Finished: SUCCESS
```

## Build #2: triggered by SCM polling, commit bb4df03

Guna pushed `bb4df03 docs: test Jenkins SCM polling` from the workstation at about 06:03 UTC and did not touch Jenkins. `pollSCM('H/5 * * * *')` picked it up:

```
Started by an SCM change
11:37:12  Checking out Revision bb4df039f2ccc2436df65728b71f37a8f0ce8cb4 (refs/remotes/origin/main)
11:37:12  Commit message: "docs: test Jenkins SCM polling"
11:37:12   > git rev-list --no-walk 4636e5a0e6cc42820b56a93afbdc6cbfc11f303c # timeout=10
11:37:13  Environment OK
11:37:45  [INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
11:37:46  [INFO] Finished at: 2026-10-20T06:07:46Z
11:38:00  CI passed for bb4df03. Artifact: application/target/enterprise-devops-app.jar
Finished: SUCCESS
```

## Harmless log lines

| Line | Meaning |
|---|---|
| `Selected Git installation does not exist. Using Default` | No Git tool configured in Global Tool Configuration; the system `git` 2.43.0 is used |
| `from unknown branch` | `BRANCH_NAME` is only set in Multibranch jobs; this is a single Pipeline job |
| `[Checks API] No suitable checks publisher found.` | No GitHub Checks integration yet |

## Not yet captured

Screenshots of the stage view, test result trend and archived artifact.
