# Local Development

## Objective

Build, test and run the service on your own machine exactly as Jenkins does, so a failure in CI can always be reproduced locally.

## Prerequisites

- JDK 21 on `PATH` or in `JAVA_HOME`. The Maven wrapper uses `JAVA_HOME` first when it is set.
- Git. Internet access to `repo.maven.apache.org` for the first build.
- Optional: Docker.

## Build and test

```bash
cd application
./mvnw -B clean verify
```

Expected output (abridged):

```
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0 -- in io.github.gunasekar89.pipeline.api.HelloControllerUnitTest
[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0 -- in io.github.gunasekar89.pipeline.api.HelloControllerWebTest
[INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0 -- in io.github.gunasekar89.pipeline.ApplicationIntegrationTest
[INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

Outputs:

| Path | What it is |
|---|---|
| `target/enterprise-devops-app.jar` | Executable Spring Boot JAR (about 24 MB) |
| `target/surefire-reports/*.xml` | JUnit XML, published by Jenkins |
| `target/site/jacoco/index.html` | Coverage report (input for SonarQube in Phase 2) |

### Test layers

| Test class | Type | What it proves |
|---|---|---|
| `HelloControllerUnitTest` | Plain JUnit, no Spring | Greeting logic and input sanitising (blank, control characters, length cap) |
| `HelloControllerWebTest` | `@WebMvcTest` slice | URL mapping, query parameter binding, JSON shape, 404 for unknown paths |
| `ApplicationIntegrationTest` | `@SpringBootTest` full context | Wiring and configuration, health and probe groups, Prometheus output with tags, `env`/`heapdump` not exposed |

## Run

```bash
java -jar target/enterprise-devops-app.jar
```

Configuration through environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `SERVER_PORT` | `8080` | HTTP port |
| `APP_GREETING` | `Hello` | Greeting prefix |
| `APP_ENVIRONMENT` | `local` | Returned by the API and added as a metric tag |

Example: `APP_GREETING=Hi APP_ENVIRONMENT=dev SERVER_PORT=8085 java -jar target/enterprise-devops-app.jar`

## Verify

```bash
curl -s localhost:8080/api/hello?name=Guna
# {"message":"Hello, Guna!","environment":"local"}

curl -s localhost:8080/actuator/health
# {"groups":["liveness","readiness"],"status":"UP"}

curl -s localhost:8080/actuator/health/readiness
# {"status":"UP"}

curl -s localhost:8080/actuator/info
# {"build":{"artifact":"enterprise-devops-app", ... "version":"0.1.0-SNAPSHOT", ...}}

curl -s localhost:8080/actuator/prometheus | grep '^http_server_requests_seconds_count'
# http_server_requests_seconds_count{application="enterprise-devops-app",environment="local",...,uri="/api/hello"} 1

curl -s -o /dev/null -w '%{http_code}\n' localhost:8080/actuator/env
# 404  (sensitive endpoint is not exposed)
```

## Container

The Dockerfile packages the JAR that was already built and tested, so build the JAR first.

```bash
cd application
./mvnw -B clean package
docker build -t enterprise-devops-app:local .
docker run --rm -p 8080:8080 -e APP_ENVIRONMENT=docker enterprise-devops-app:local
```

Verify it runs as a non-root user:

```bash
docker run -d --name edp -p 8080:8080 enterprise-devops-app:local
docker exec edp id          # uid=10001(app) gid=10001(app) groups=10001(app)
docker rm -f edp
```

Image design: two stages from `eclipse-temurin:21-jre-noble`. The first extracts Spring Boot layers (dependencies change rarely, application code often, so rebuilds reuse cached layers). The runtime stage has no JDK, no Maven and no source, runs as UID 10001, and sets `-XX:MaxRAMPercentage=75` so the JVM respects container memory limits. The image is about 450 MB, most of it the Ubuntu-based JRE; a distroless or Alpine base is a Phase 2 option.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Rule 0: RequireJavaVersion failed ... version 1.8` (or 17) | `JAVA_HOME` points at an older JDK. The wrapper prefers `JAVA_HOME` over `PATH`. | `export JAVA_HOME=/path/to/jdk-21` or unset it. `bash ci/scripts/verify-environment.sh` shows which JDK is used. |
| `./mvnw: Permission denied` | Executable bit lost (for example after a ZIP download on Windows) | `chmod +x mvnw` or `git update-index --chmod=+x application/mvnw` |
| `Port 8080 was already in use` | Another process (often a local Jenkins) | `SERVER_PORT=8085 java -jar ...` or find the process with `sudo ss -ltnp 'sport = :8080'` |
| Wrapper cannot download Maven | No Internet or a proxy | Set `MVNW_REPOURL` to an internal mirror, or configure the proxy in `~/.m2/settings.xml` |
| `COPY failed: ... target/enterprise-devops-app.jar not found` | Docker build before Maven package | Run `./mvnw -B clean package` first |

## Cleanup

```bash
cd application && ./mvnw -B clean
docker rmi enterprise-devops-app:local
```

## Security considerations

- Only three actuator endpoints are exposed, and a test fails if `env` or `heapdump` become reachable.
- The `name` parameter is sanitised before use.
- Container runs as a numeric non-root UID, which lets Kubernetes enforce `runAsNonRoot: true`.
- Base images are pinned by tag only. Digest pinning and automated update PRs are planned (Phase 2).
