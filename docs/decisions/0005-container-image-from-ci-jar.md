# ADR-0005: Build the container image from the CI-tested JAR

- Status: Accepted
- Date: 2026-10-19

## Context

The image can either compile the code itself (multi-stage build with Maven inside Docker) or package the JAR produced and tested by the earlier pipeline stages.

## Options

1. **Multi-stage build with Maven inside the Dockerfile.** Self-contained `docker build`, but compiles and tests a second time, needs network access to Maven Central during the image build, and the shipped bytes are not the bytes that passed CI.
2. **Copy `target/enterprise-devops-app.jar` into a runtime image.** Build once, test once, package what was tested.
3. Cloud Native Buildpacks (`spring-boot:build-image`). Good defaults, less transparent for learning.

## Decision

Option 2, with a small extraction stage that splits the JAR into Spring Boot layers for better caching.

## Consequences

- The image contains exactly the archived, fingerprinted JAR from the same build.
- `docker build` requires `./mvnw package` first; the Dockerfile says so and `.dockerignore` sends only the JAR as build context.
- No Maven, JDK or source in the runtime image.
- Buildpacks remain an option to compare in Phase 2 (they also produce an SBOM).
