# Jenkins Pipeline

## Objective

Run `ci/Jenkinsfile` from this repository on every change to `main`: build, test, publish test results, and archive a fingerprinted JAR. Later DevSecOps and delivery stages already exist in the file but are switched off until their tools and credentials are set up.

## Stages

| # | Stage | What it does | Fails when |
|---|---|---|---|
| 1 | Checkout | `checkout scm`, records the full and short Git SHA, sets the build description | Repository unreachable or credentials wrong |
| 2 | Verify Environment | `ci/scripts/verify-environment.sh`: agent user, Git, the JDK Maven will use, Maven wrapper version | No Java, or Java older than 21 |
| 3 | Compile | `./mvnw -B -ntp clean compile` | Compilation error, enforcer rule broken |
| 4 | Unit Tests | `./mvnw -B -ntp test`; `junit` publishes `target/surefire-reports/*.xml` in `post { always }` | Any test fails (results are still published) |
| 5 | Package | `./mvnw -B -ntp package -DskipTests` (tests already ran on the same sources) | Packaging error |
| 6 | Archive Artifacts | Archives `enterprise-devops-app.jar` with fingerprint, plus the JaCoCo HTML report | JAR missing |
| - | Secret Scan (Gitleaks) | `RUN_SECRET_SCAN` (default on): scans Git history with `ci/security/gitleaks.toml` | Tool missing, or a secret found |
| - | Dependency Scan (Trivy) | `RUN_DEPENDENCY_SCAN` (default on): `trivy fs` for HIGH/CRITICAL vulnerabilities and misconfigurations | Tool missing, or findings |
| - | SonarQube Analysis | `RUN_SONARQUBE` (default off): analysis plus `waitForQualityGate` | Plugin missing (clear message) or server `sonarqube` not configured, or gate fails |
| - | Docker Build | `BUILD_IMAGE` (default on): `docker build -t enterprise-devops-app:<git-sha>` | Docker not available to the `jenkins` user |
| - | Image Scan (Trivy) | `BUILD_IMAGE`: `trivy image` on the new tag, HIGH/CRITICAL, report archived | Tool missing, or findings in OS packages or libraries |
| - | Container Smoke Test | `BUILD_IMAGE`: `ci/scripts/smoke-test.sh` starts the image on a random localhost port, waits up to 60 s for readiness, calls `/api/hello`, checks the UID is not 0, removes the container, archives its log | Not ready in time, API error, or running as root |
| - | Push to ACR | `PUSH_TO_ACR`: deliberately fails with "planned for Phase 3" | Always, until implemented |

Gitleaks, Trivy and the image stages are on by default since Phase 2 (2026-10-20), so SCM-triggered builds run them; SonarQube and ACR stay off until they exist. Jenkins stores parameter defaults from the last build, so the first build after a default changes still uses the old values. Stages show as *skipped* when their parameter is off. When switched on without their tool, `ci/scripts/require-tool.sh` fails the stage with an explanation. Nothing reports green without doing the work.

Pipeline options: no concurrent builds, 30-minute timeout, keep 20 builds and the artifacts of 5, timestamps on every log line.

## Prerequisites

- Jenkins LTS with the **suggested plugins** (provides Pipeline, Git, JUnit, Timestamper). See [jenkins-on-azure-vm.md](../installation/jenkins-on-azure-vm.md).
- `JAVA_HOME` for the agent pointing at JDK 21.
- Outbound HTTPS from the agent to `github.com` and `repo.maven.apache.org`.

## Create the job

1. **New Item** → name `enterprise-devops-pipeline` → **Pipeline** → OK.
2. **Build Triggers**: leave empty. The `triggers { pollSCM(...) }` block in the Jenkinsfile registers polling after the first run.
3. **Pipeline** section:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/gunasekar89/enterprise-devops-pipeline.git`
   - Credentials: none for a public repository; `github-token` for a private one (Username with password: GitHub username + fine-grained PAT with read-only *Contents*).
   - Branch Specifier: `*/main`
   - Script Path: `ci/Jenkinsfile`
   - Lightweight checkout: ticked
4. Save → **Build Now**. The first run also registers the parameters, so later runs show **Build with Parameters**.

### Moving from the existing `jenkins-java-lab` job

The job created during the manual exercise builds the original `jenkins-java-lab` project. Keep it until the new job is green, then disable it (**Disable Project**) rather than deleting it, so its build history remains as evidence.

## Polling instead of webhooks

Jenkins is reachable only through an SSH tunnel, so GitHub cannot call a webhook. The Jenkinsfile polls instead:

```groovy
triggers {
    pollSCM('H/5 * * * *')
}
```

- `H` spreads the start minute by job name, so many jobs do not poll at the same second.
- Every 5 minutes Jenkins runs `git ls-remote` against GitHub; a build starts only when `main` has a new commit.
- The trigger takes effect after one manual build, because Jenkins reads it from the Jenkinsfile.
- Check it under the job's **Git Polling Log**.
- Cost: up to 5 minutes delay and a small amount of polling traffic. GitHub's API rate limits are not involved, because polling uses Git, not the REST API.

Ways to get push-based triggers later: expose a narrow `/github-webhook/` path through a reverse proxy with TLS and IP allow-listing of GitHub's hook ranges; use a webhook relay; or move CI to an agent that dials out.

## Expected result

A green build with six executed stages, five skipped ones, a **Test Result** link showing 12 passed tests, and the JAR under **Build Artifacts**. The Jenkinsfile Runner run that verified this is recorded in [jenkins-pipeline-run.md](../../progress/evidence/phase-0/jenkins-pipeline-run.md).

## Verification

```text
Job page → last build → Console Output ends with:
  CI passed for <sha>. Artifact: application/target/enterprise-devops-app.jar
  Finished: SUCCESS
Job page → Test Result → 12 tests, 0 failures
Job page → Build Artifacts → application/target/enterprise-devops-app.jar
Job page → Git Polling Log → shows polling every ~5 minutes after the first build
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `No such DSL method 'timestamps'` | Timestamper plugin missing | Install it, or remove `timestamps()` |
| `RequireJavaVersion failed ... 1.8` / `17` | Agent `JAVA_HOME` points at an old JDK | Set `JAVA_HOME` on the node (installation guide step 7) |
| `./mvnw: Permission denied` | File lost its executable bit in Git | `git update-index --chmod=+x application/mvnw` and commit |
| Maven warnings about `/home/azureuser/.m2` or `Permission denied` writing the local repository | Build runs as `jenkins` but files are owned by `azureuser` (or the reverse after a `sudo mvn`) | Let Jenkins use its own `~/.m2` (`/var/lib/jenkins/.m2`); never run Maven with `sudo`; fix ownership with `sudo chown -R jenkins:jenkins /var/lib/jenkins/.m2` |
| `Couldn't find any revision to build` | Branch specifier wrong | `*/main` |
| No automatic builds | Polling not registered yet | Run the job once manually; check **Git Polling Log** |
| `waitForQualityGate` hangs | SonarQube cannot call back to Jenkins (tunnel setup) | Phase 2 will document the webhook from SonarQube to Jenkins on the same VM |

## Security considerations

- The Jenkinsfile contains no credentials, subscription IDs, hostnames or IPs. Credentials are referenced by ID only.
- `disableConcurrentBuilds()` stops two builds writing the same workspace.
- Scanner reports are archived as artifacts, not committed.
- `archiveArtifacts ... fingerprint: true` lets you trace a JAR back to the exact build and commit.

## Rollback

Pipeline changes are code: revert the commit that changed `ci/Jenkinsfile` and the next poll builds with the previous version. To stop builds immediately, **Disable Project** on the job.

## Interview questions

- Why `skipDefaultCheckout()` plus an explicit `checkout scm` stage?
- Why run `test` and then `package -DskipTests` instead of a single `mvn verify`? What is the trade-off?
- What does `H` mean in a Jenkins cron expression and why does it matter at scale?
- How would you make the opt-in security stages mandatory on `main` but optional on feature branches?
- What is the difference between `archiveArtifacts` with fingerprints and publishing to an artifact repository such as Nexus or Azure Artifacts?
