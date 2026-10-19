# Evidence: Docker Image (Phase 0)

- **Date:** 2026-10-19
- **Commit:** `1ff7816`
- **Environment:** Docker Engine 29.8.2 in the cloud workspace; base image `eclipse-temurin:21-jre-noble` (`sha256:35501d3f93173b420ac9001658eb68157e813316b865087e345c187fca422c4c` at time of build)
- **Command:** `./mvnw -B clean package && docker build -t enterprise-devops-app:1ff7816 .` from `application/`

## Results

```text
$ docker exec edp id
uid=10001(app) gid=10001(app) groups=10001(app)
$ docker inspect -f '{{.Config.User}}' enterprise-devops-app:1ff7816
10001:10001
$ curl -s localhost:8086/actuator/health/readiness
{"status":"UP"}
$ curl -s localhost:8086/api/hello
{"message":"Hello, World!","environment":"docker"}
$ docker image inspect -f "{{.Id}} {{.Size}}" enterprise-devops-app:1ff7816
sha256:193d04f9af5a6f104b039b3430bad56b5d3cc6cd1eab47f6af8b175728e926a4 450070717
$ docker history --format "{{.Size}}\t{{.CreatedBy}}" enterprise-devops-app:1ff7816 | head -8
0B	ENTRYPOINT ["java" "org.springframework.boot…
0B	EXPOSE [8080/tcp]
0B	ENV SERVER_PORT=8080 JAVA_TOOL_OPTIONS=-XX:M…
0B	USER 10001:10001
115kB	COPY --chown=app:app /workspace/extracted/ap…
4.1kB	COPY --chown=app:app /workspace/extracted/sn…
696kB	COPY --chown=app:app /workspace/extracted/sp…
24.4MB	COPY --chown=app:app /workspace/extracted/de…
$ docker stop edp  (graceful shutdown log)
INFO 1 --- [enterprise-devops-app] [ionShutdownHook] o.s.boot.tomcat.GracefulShutdown         : Commencing graceful shutdown. Waiting for ac
INFO 1 --- [enterprise-devops-app] [tomcat-shutdown] o.s.boot.tomcat.GracefulShutdown         : Graceful shutdown complete
```

Observations:
- Runs as UID/GID 10001, not root.
- The application layer is 115 kB; the 24.4 MB dependency layer is reused between builds when only code changes.
- Graceful shutdown completes on `docker stop`.
- Image size is about 450 MB uncompressed, mostly the Ubuntu-based JRE. A smaller base is a Phase 2 option.
- The image has not been pushed to any registry.
