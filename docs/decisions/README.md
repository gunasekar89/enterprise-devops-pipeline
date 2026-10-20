# Architecture Decision Records

Each ADR records one significant decision: the context, the options considered, the choice and its consequences. ADRs are not edited after acceptance; a new ADR supersedes an old one.

| ADR | Title | Status | Date |
|---|---|---|---|
| [0001](0001-single-repository.md) | Single repository for application, CI, infrastructure and GitOps | Accepted | 2026-10-19 |
| [0002](0002-java-21-spring-boot-4.md) | Java 21 with Spring Boot 4.1 | Accepted | 2026-10-19 |
| [0003](0003-argo-cd-gitops.md) | Argo CD as the GitOps controller | Accepted (implementation in Phase 4) | 2026-10-19 |
| [0004](0004-jenkins-with-scm-polling.md) | Jenkins CI behind an SSH tunnel, triggered by SCM polling | Accepted | 2026-10-19 |
| [0005](0005-container-image-from-ci-jar.md) | Build the container image from the CI-tested JAR | Accepted | 2026-10-19 |
| [0006](0006-terraform-for-azure.md) | Terraform rather than Bicep for Azure infrastructure | Proposed | 2026-10-19 |
| [0007](0007-registry-auth-without-role-assignments.md) | Registry access without Azure role assignments | Accepted (implementation in Phases 3-4) | 2026-10-20 |
| [0008](0008-build-once-promote-digest.md) | Build once, promote by image digest | Accepted (implementation in Phases 2-4) | 2026-10-20 |

Template: copy any ADR and keep the headings *Context, Options, Decision, Consequences*.
