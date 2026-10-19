# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added (Phase 0, 2026-10-19)
- Spring Boot 4.1.1 / Java 21 REST API with `/api/hello`, actuator health (liveness and readiness groups), info and Prometheus endpoints, configured through environment variables.
- 12 tests: plain unit tests, a `@WebMvcTest` web-layer slice and a full-context integration test that also checks sensitive actuator endpoints stay hidden.
- Maven wrapper (Maven 3.9.11), Maven Enforcer (Java 21+, Maven 3.9+), JaCoCo coverage report, build-info for `/actuator/info`.
- Layered, non-root (UID 10001) Docker image built from the CI-tested JAR.
- Baseline declarative `ci/Jenkinsfile` with SCM polling and opt-in DevSecOps stages that fail loudly when their tools are missing.
- `ci/scripts/verify-environment.sh`, `ci/scripts/require-tool.sh`, `ci/security/gitleaks.toml`.
- Documentation: README, architecture, prerequisites, local and Jenkins runbooks, security model, known issues, rebuild guide, roadmap, six ADRs, interview notes.
- Progress tracker, implementation log, lessons learned, next steps, Phase 0 evidence.
- Portfolio pack: LinkedIn project text, highlights, evidence checklist.

### Security
- Overrode Tomcat to 11.0.27 and Jackson 3 to 3.1.8 after the Trivy baseline scan found 8 CVEs (3 critical in Tomcat, 5 high in Jackson) in the versions managed by Spring Boot 4.1.1. The rescan reports 0 high or critical findings.
