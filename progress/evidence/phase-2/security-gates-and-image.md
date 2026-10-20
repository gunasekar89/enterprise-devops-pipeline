# Evidence: security gates and Docker image in Jenkins (Phase 2A)

Date: 2026-10-20. Jenkins 2.580.1 on `vm-jenkins-lab`. Tools installed on the VM: Docker 29.1.3 (Ubuntu `docker.io`), Gitleaks 8.30.1 (release tarball in `/usr/local/bin`), Trivy 0.76.0 (release `.deb`). The `jenkins` user is in the `docker` group; humans use `sudo docker`. Logs copied from the Jenkins UI and the VM by Guna; excerpts verbatim.

## Build on 56714ca with RUN_SECRET_SCAN, RUN_DEPENDENCY_SCAN and BUILD_IMAGE

```
Started by user admin
12:00:28  Checking out Revision 56714ca5bcf2f7dda8849567bfc65d2c095304d7 (refs/remotes/origin/main)
12:01:01  [INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
12:01:12  gitleaks version 8.30.1
12:01:12  + gitleaks git . --config ci/security/gitleaks.toml --redact --report-format json --report-path gitleaks-report.json
12:01:13  INF 12 commits scanned.
12:01:13  INF no leaks found
12:01:14  Version: 0.76.0
12:01:14  + trivy fs --scanners vuln,misconfig --severity HIGH,CRITICAL --exit-code 1 --format table --output trivy-fs-report.txt .
12:01:17  INFO  [pom] Detecting vulnerabilities...
12:01:17  INFO  Detected config files  num=1
Stage "SonarQube Analysis" skipped due to when conditional
12:01:18  + docker build -t enterprise-devops-app:56714ca .
12:01:24  Digest: sha256:35501d3f93173b420ac9001658eb68157e813316b865087e345c187fca422c4c
12:01:54  Successfully tagged enterprise-devops-app:56714ca
Stage "Push to ACR" skipped due to when conditional
12:01:55  CI passed for 56714ca. Artifact: application/target/enterprise-devops-app.jar
Finished: SUCCESS
```

Trivy exits 1 on any HIGH or CRITICAL finding, so a passing stage means none were found in `pom.xml` dependencies or the Dockerfile. The digest above is the `eclipse-temurin:21-jre-noble` base image pulled at build time.

The preceding run (build #4 on 13063db) passed Gitleaks (11 commits) and Trivy too, but failed because `RUN_SONARQUBE` was ticked without the plugin (known-issues #12).

## Image smoke test and image scan (on the VM)

```
$ sudo docker run -d --name edp -p 8085:8080 enterprise-devops-app:56714ca
$ curl -s localhost:8085/actuator/health
{"groups":["liveness","readiness"],"status":"UP"}
$ sudo docker exec edp id
uid=10001(app) gid=10001(app) groups=10001(app)
$ sudo trivy image --severity HIGH,CRITICAL --quiet enterprise-devops-app:56714ca
Report Summary
│ enterprise-devops-app:56714ca (ubuntu 24.04)       │ ubuntu │ 0 │ - │
│ app/BOOT-INF/lib/HdrHistogram-2.2.2.jar            │  jar   │ 0 │ - │
│ app/BOOT-INF/lib/commons-logging-1.3.6.jar         │  jar   │ 0 │ - │
...
│ app/BOOT-INF/lib/spring-web-7.0.9.jar              │  jar   │ 0 │ - │
│ app/BOOT-INF/lib/spring-webmvc-7.0.9.jar           │  jar   │ 0 │ - │
│ app/BOOT-INF/lib/tomcat-embed-core-11.0.27.jar     │  jar   │ 0 │ - │
$ sudo docker rm -f edp
```

Columns are Target, Type, Vulnerabilities, Secrets; `-` in the Secrets column means secret scanning was not requested (Gitleaks covers secrets).

## Harmless log lines

| Line | Meaning |
|---|---|
| `DEPRECATED: The legacy builder is deprecated` | Ubuntu's `docker.io` has no buildx; install `docker-buildx` to use BuildKit |
| `useradd warning: app's uid 10001 is greater than SYS_UID_MAX 999` | Intentional high UID for the non-root user |

## Not yet done

- The image scan runs by hand; a `trivy image` stage in the Jenkinsfile is the next step.
- SonarQube, Syft SBOM and Cosign.
