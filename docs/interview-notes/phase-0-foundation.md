# Interview Notes: Phase 0 (Foundation)

Questions a senior DevOps, SRE or platform interviewer could ask about what exists in this phase, with the points a strong answer covers. Answer from what you actually built and point to the file.

## CI design

**Why is the Jenkinsfile in the repository instead of configured in the Jenkins UI?**
Versioned with the code, reviewed in PRs, reproducible on a new Jenkins, and branch-specific. UI-configured jobs drift and cannot be rebuilt after a playground expires. (`ci/Jenkinsfile`)

**Your later stages are in the Jenkinsfile but off. Isn't that dead code?**
They document the target pipeline and are safe: they show as skipped, and when turned on without their tool they fail with an explanation (`ci/scripts/require-tool.sh`). The anti-pattern is a stage that echoes "scan passed" without scanning. Turned on per phase, then made mandatory on `main`.

**Why poll SCM instead of a webhook?**
Jenkins is private behind an SSH tunnel; inbound webhooks cannot reach it. `H/5` spreads load. Trade-off: up to 5 minutes latency, does not scale to many jobs. Enterprise alternatives: ingress with TLS and GitHub IP allow-listing, a GitHub App, or outbound-only agents. (ADR-0004)

**What does `fingerprint: true` give you?**
An MD5 of the JAR recorded per build, so you can find which build and commit produced a given file, and which downstream jobs used it. It is traceability, not integrity protection; for that use signatures.

**Why `test` then `package -DskipTests` instead of one `mvn verify`?**
Separate stages make failures easier to read in the stage view and let JUnit publish after the test stage even on failure. Cost: an extra Maven start-up. Alternatively run `verify` once and parse reports.

## Build and test

**What does the Maven wrapper solve?**
Every machine and agent uses the same Maven version (3.9.11 here) without installing it; removes "works on my machine" from the build tool. The Enforcer plugin adds a check for Java 21+.

**You hit a case where Maven used Java 8 although Java 21 was on PATH. Why?**
Maven and the wrapper use `JAVA_HOME` when set. The verify script now checks the JDK Maven will really use. (known-issues #7)

**Explain your test pyramid.**
Unit tests without Spring (fast, logic and sanitising), a `@WebMvcTest` slice (HTTP mapping and JSON without starting the whole app), one `@SpringBootTest` (wiring, config, actuator exposure). More unit than integration tests; each layer catches failures the others cannot.

**Why is there a test that `/actuator/env` is not reachable?**
Security requirements regress silently when someone adds `include: "*"`. A test turns a policy into an enforced contract.

## Containers

**Why build the image from the CI JAR instead of compiling in Docker?**
Build once, promote the same artifact; no second compile, no Maven network access during image build; the shipped bytes are the tested bytes. (ADR-0005)

**Why a numeric UID?**
Kubernetes `runAsNonRoot` can only verify a numeric user; a name like `app` would make the kubelet refuse to start the pod.

**What does `MaxRAMPercentage=75` do?**
Sizes the heap from the container's memory limit instead of the host's RAM, leaving room for metaspace, threads and native memory so the pod is not OOM-killed.

**How did you handle CVEs in a dependency your framework manages?**
Trivy found 3 critical (Tomcat) and 5 high (Jackson) CVEs in Spring Boot 4.1.1's managed versions. Overrode the version properties to patched releases in the same minor line, re-ran tests, rescanned clean, and documented when to remove the override.

## Security and operations

**How do you keep secrets out of Git?**
Prevention (`.gitignore`), detection (Gitleaks on history, in CI), and process (credentials only in Jenkins Credentials or Key Vault, referenced by ID). If one leaks: rotate first, then rewrite history.

**How do you know you are not claiming more than you built?**
Every capability has a status, and "Verified" needs evidence in `progress/evidence/`. Manual historical work is marked as reported, not verified.

**Liveness versus readiness?**
Liveness failing restarts the container; readiness failing removes it from Service endpoints without restarting. Never put downstream dependency checks in liveness, or an outage cascades into restart loops.

## Architecture decisions

**Why one repository?** See ADR-0001: simplicity for one maintainer, with a planned split into app, infra and GitOps repos and the CI-loop risk called out.

**Why Spring Boot 4.1 instead of 3.5?** See ADR-0002: 3.5's open-source support window has ended; 4.1 is current. Know the renamed starters and test packages.
