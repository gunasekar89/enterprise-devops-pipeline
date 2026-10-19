# syntax=docker/dockerfile:1
#
# Packages the JAR that CI has already built and tested (build once, promote the
# same artifact). Run `./mvnw -B clean package` first, then from application/:
#   docker build -t enterprise-devops-app:local .
#
# Base images are pinned by tag. Digest pinning is planned with the Phase 2
# container hardening work (see docs/roadmap.md).

ARG JAVA_IMAGE=eclipse-temurin:21-jre-noble

# Stage 1: split the Spring Boot fat JAR into layers so dependency layers are
# cached between builds and only the small application layer changes.
FROM ${JAVA_IMAGE} AS layers
WORKDIR /workspace
COPY target/enterprise-devops-app.jar app.jar
RUN java -Djarmode=tools -jar app.jar extract --layers --launcher --destination extracted

# Stage 2: minimal runtime with no build tools and no source code.
FROM ${JAVA_IMAGE}

ARG APP_UID=10001
RUN groupadd --system --gid ${APP_UID} app \
 && useradd --system --uid ${APP_UID} --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=layers --chown=app:app /workspace/extracted/dependencies/ ./
COPY --from=layers --chown=app:app /workspace/extracted/spring-boot-loader/ ./
COPY --from=layers --chown=app:app /workspace/extracted/snapshot-dependencies/ ./
COPY --from=layers --chown=app:app /workspace/extracted/application/ ./

# Numeric UID lets Kubernetes enforce runAsNonRoot without resolving names.
USER ${APP_UID}:${APP_UID}

ENV SERVER_PORT=8080 \
    JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75 -XX:+ExitOnOutOfMemoryError"
EXPOSE 8080

ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
