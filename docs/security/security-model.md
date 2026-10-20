# Security Model

Security in this project is part of the delivery pipeline, not a separate project. This page says what is enforced today, what is planned, and how to run each check by hand.

## Threats addressed and controls

| Threat | Control | Status |
|---|---|---|
| Secrets committed to Git | `.gitignore` for key, env, tfvars, tfstate and kubeconfig files; Gitleaks on tree and history | `.gitignore` in place; Gitleaks run manually (clean), Jenkins stage opt-in |
| Vulnerable dependencies | Trivy filesystem and image scans; optional Snyk | Trivy run manually; 8 high/critical CVEs found and fixed. Jenkins stage opt-in |
| Insecure code patterns, low coverage | SonarQube quality gate, JaCoCo coverage | JaCoCo report produced; SonarQube planned (Phase 2) |
| Image tampering between build and deploy | Immutable Git-SHA tags, deploy by digest, Cosign signature verified at admission | Planned (Phases 2-4) |
| Unknown image contents | Syft SBOM attached to the image | Planned (Phase 2) |
| Container breakout impact | Non-root UID 10001, no build tools in runtime image; Kubernetes `runAsNonRoot`, read-only root FS, dropped capabilities | Image part verified; Kubernetes part planned |
| Exposed admin UIs | Jenkins, SonarQube, Grafana bound to localhost and reached through SSH tunnels | Documented; Jenkins setup to re-verify in Phase 1 |
| Over-privileged cloud identities | Separate ACR tokens per purpose (push for CI, pull-only for AKS), scoped to one repository; managed identities with roles in a normal subscription | Planned (Phase 3); role assignments are blocked in the playground (ADR-0007) |
| Information leak from the app | Only `health`, `info`, `prometheus` actuator endpoints exposed; health details hidden; input sanitised | Verified by tests |

## Running the scanners locally with Docker

No local install is needed. Run from the repository root.

### Gitleaks (secrets)

```bash
# Working tree
docker run --rm -v "$PWD":/src:ro zricethezav/gitleaks:latest \
  dir /src --config /src/ci/security/gitleaks.toml --redact --no-banner

# Full Git history (what the Jenkins stage does)
docker run --rm -v "$PWD":/src:ro zricethezav/gitleaks:latest \
  git /src --config /src/ci/security/gitleaks.toml --redact --no-banner
```

Expected: `no leaks found`, exit code 0. Exit code 1 means a finding; the output shows file, line and rule with the secret redacted.

If a real secret is found: revoke or rotate it first, then remove it from history (`git filter-repo`), then force-push with team agreement. Deleting the line in a new commit is not enough.

### Trivy (image vulnerabilities)

```bash
cd application && ./mvnw -B clean package && docker build -t enterprise-devops-app:local . && cd ..
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$HOME/.cache/trivy":/root/.cache aquasec/trivy:latest \
  image --severity HIGH,CRITICAL enterprise-devops-app:local
```

### Trivy (Dockerfile and IaC misconfiguration)

```bash
docker run --rm -v "$PWD":/src:ro aquasec/trivy:latest config /src
```

Current result: one LOW finding, `DS-0026: Add HEALTHCHECK instruction`. Accepted: the image will run on Kubernetes, which uses the liveness and readiness probes at `/actuator/health/*` and ignores Docker `HEALTHCHECK`. Revisit if the image is run under plain Docker or Compose.

## Handling a vulnerable transitive dependency

The Phase 0 baseline scan found CVEs in Tomcat 11.0.24 and Jackson 3.1.5, the versions Spring Boot 4.1.1 manages. The fix used:

1. Check that a patched release exists in the same minor line (`tomcat-embed-core` 11.0.27, `jackson-bom` 3.1.8).
2. Override Spring Boot's managed version property in `application/pom.xml` (`tomcat.version`, `jackson-bom.version`) with a comment that says why and when to remove it.
3. Rebuild, re-run all tests, rebuild the image, rescan. Result: 0 high or critical.
4. Remove the override once a Spring Boot release ships an equal or newer version.

This is the standard approach when the framework's next patch is not out yet. Upgrading the framework itself is preferred when available.

## Secrets in Jenkins

- Store secrets as Jenkins Credentials and bind them per step with `withCredentials`, so they are masked in the log and exist only for that step.
- Never `echo` a credential, never pass one as a build parameter, never put one in an environment block.
- Jenkins encrypts credentials on disk with keys in `$JENKINS_HOME/secrets/`. Treat a backup of `JENKINS_HOME` as sensitive.

## Planned (with the phase that delivers it)

- Phase 1: GitHub branch protection on `main`, required Jenkins status check, Dependabot alerts, private vulnerability reporting.
- Phase 2: SonarQube quality gate, Gitleaks and Trivy mandatory on `main`, Syft SBOM, base-image digest pinning.
- Phase 3: Cosign signing (locally generated key stored as a Key Vault secret, or keyless), ACR admin user disabled, repository-scoped ACR tokens instead of role assignments (ADR-0007).
- Phase 4: Pod security (restricted profile), network policies, signature verification before deploy.
