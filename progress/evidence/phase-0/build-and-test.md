# Evidence: Build and Test (Phase 0)

- **Date:** 2026-10-19
- **Commit:** `1ff7816` (fresh `git clone` of the local repository)
- **Environment:** Linux x86_64 cloud workspace, OpenJDK 21.0.12.1, Maven 3.9.11 via `./mvnw`
- **Who ran it:** Claude (AI assistant) on Guna's behalf. Not yet reproduced on Guna's machine or on `vm-jenkins-lab`.

## `./mvnw -B -ntp clean verify`

```text
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.458 s -- in io.github.gunasekar89.pipeline.api.HelloControllerUnitTest
[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 4.913 s -- in io.github.gunasekar89.pipeline.api.HelloControllerWebTest
[INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 1.434 s -- in io.github.gunasekar89.pipeline.ApplicationIntegrationTest
[INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
[INFO] Total time:  12.730 s
```

Coverage (JaCoCo, `target/site/jacoco/index.html`): 93% instructions (71 of 76), 100% branches (4 of 4).

Artifact: `target/enterprise-devops-app.jar`, 24,494,857 bytes.

## Running the JAR (`java -jar target/enterprise-devops-app.jar`)

```text
INFO 10557 --- [enterprise-devops-app] [           main] o.s.boot.tomcat.TomcatWebServer          : Tomcat started on port 8080 (http) with context pa
INFO 10557 --- [enterprise-devops-app] [           main] i.g.gunasekar89.pipeline.Application     : Started Application in 2.419 seconds (process runn

$ curl -s localhost:8080/api/hello
{"message":"Hello, World!","environment":"local"}
$ curl -s localhost:8080/api/hello?name=Guna
{"message":"Hello, Guna!","environment":"local"}
$ curl -s localhost:8080/actuator/health
{"groups":["liveness","readiness"],"status":"UP"}
$ curl -s localhost:8080/actuator/health/liveness
{"status":"UP"}
$ curl -s localhost:8080/actuator/health/readiness
{"status":"UP"}
$ curl -s localhost:8080/actuator/info
{"build":{"artifact":"enterprise-devops-app","name":"enterprise-devops-app","time":"2026-10-19T19:27:54.822Z","version":"0.1.0-SNAPSHOT","group":"io.github.gunasekar89"}}
$ curl -s localhost:8080/actuator/prometheus | grep -E "^(http_server_requests_seconds_count|jvm_memory_used_bytes\{.*heap)" | head -3
http_server_requests_seconds_count{application="enterprise-devops-app",environment="local",error="none",exception="none",method="GET",outcome="SUCCESS",status="200",uri="/actuator/health"} 1
http_server_requests_seconds_count{application="enterprise-devops-app",environment="local",error="none",exception="none",method="GET",outcome="SUCCESS",status="200",uri="/actuator/health/**"} 2
http_server_requests_seconds_count{application="enterprise-devops-app",environment="local",error="none",exception="none",method="GET",outcome="SUCCESS",status="200",uri="/actuator/info"} 1
$ curl -s -o /dev/null -w '%{http_code}' localhost:8080/actuator/env
404
$ curl -s -o /dev/null -w '%{http_code}' localhost:8080/actuator/heapdump
404
$ curl -s -o /dev/null -w '%{http_code}' localhost:8080/actuator/beans
404
```

The `404` responses confirm that sensitive actuator endpoints are not exposed.
