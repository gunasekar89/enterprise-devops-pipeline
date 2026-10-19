# Evidence: Security Baseline (Phase 0)

- **Date:** 2026-10-19
- **Tools:** Gitleaks v8.30.1 (`zricethezav/gitleaks`), Trivy 0.76.0 (`aquasec/trivy`), both run as Docker containers by hand. Neither is wired into Jenkins yet.

## Gitleaks: full Git history at commit `1ff7816`

```text
$ gitleaks git . --config ci/security/gitleaks.toml --redact   (via zricethezav/gitleaks:v8.30.1)
7:29PM INF 1 commits scanned.
7:29PM INF scanned ~142144 bytes (142.14 KB) in 80.3ms
7:29PM INF no leaks found
exit code: 0
```

Negative control, to prove the scanner and the allowlist in `ci/security/gitleaks.toml` still catch real-looking secrets (fake AWS key pair in a throwaway directory outside the repository):

```text
$ # negative control: fake AWS key pair planted in a throwaway directory
7:29PM WRN leaks found: 2
exit code: 1
```

## Trivy: image vulnerabilities, before remediation

Image built from Spring Boot 4.1.1's default managed dependency versions. `trivy image --severity HIGH,CRITICAL`:

```text
Total: 8 (HIGH: 5, CRITICAL: 3)

Library                                   CVE             Severity  Installed  Fixed in
org.apache.tomcat.embed:tomcat-embed-core CVE-2026-65182  CRITICAL  11.0.24    11.0.25
                                          CVE-2026-65905  CRITICAL
                                          CVE-2026-68525  CRITICAL
tools.jackson.core:jackson-core           CVE-2026-89407  HIGH      3.1.5      3.1.7
                                          CVE-2026-89425  HIGH                 3.1.7
tools.jackson.core:jackson-databind       CVE-2026-68497  HIGH      3.1.5      3.1.6
                                          CVE-2026-91776  HIGH                 3.1.7
                                          CVE-2026-91777  HIGH                 3.1.7
```

(Condensed from the Trivy table; the operating-system layer had no high or critical findings.)

## Remediation

`application/pom.xml` overrides `tomcat.version` to `11.0.27` and `jackson-bom.version` to `3.1.8`, with a comment on when to remove them. All 12 tests pass with the new versions.

## Trivy: image vulnerabilities, after remediation (commit `1ff7816`)

```text
HIGH/CRITICAL: 0
All severities: Ubuntu OS packages only, MEDIUM 27, LOW 22. Java libraries: 0.
```

The remaining medium and low findings are in the Ubuntu base image and are not fixable from this repository except by changing or updating the base image (Phase 2 hardening).

## Trivy: misconfiguration scan of the repository

```text
application/Dockerfile: Tests 27, successes 26, failures 1
DS-0026 (LOW): Add HEALTHCHECK instruction in your Dockerfile
```

Accepted risk: Kubernetes ignores Docker `HEALTHCHECK` and will use the actuator liveness/readiness probes. See [security-model.md](../../../docs/security/security-model.md).

Note: vulnerability databases update daily, so a later scan of the same image may report new CVEs.
