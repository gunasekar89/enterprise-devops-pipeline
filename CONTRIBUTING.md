# Contributing

This is a learning and portfolio project, but it follows the same workflow a production team would.

## Workflow

1. Branch from `main`: `feature/<short-name>`, `fix/<short-name>` or `docs/<short-name>`.
2. Keep each change small and focused on one milestone.
3. Run the local checks before pushing:
   ```bash
   cd application && ./mvnw -B clean verify
   bash ci/scripts/verify-environment.sh        # from the repository root
   ```
4. Open a pull request into `main`. Jenkins must be green before merge. Once branch protection is enabled (Phase 1), direct pushes to `main` are blocked.
5. Squash-merge with a [Conventional Commits](https://www.conventionalcommits.org/) title, for example `feat(ci): add Gitleaks stage`.

## Definition of done

A change is done when all of these are true:

- Code builds and tests pass locally and in Jenkins.
- The relevant runbook in `docs/` is updated: objective, prerequisites, commands, expected output, verification, troubleshooting, security notes, cleanup and rollback.
- `progress/PROJECT_STATUS.md` and `progress/IMPLEMENTATION_LOG.md` are updated. A status of **Verified** requires evidence in `progress/evidence/`.
- Significant choices are captured as an ADR in `docs/decisions/`.
- `CHANGELOG.md` has an entry under "Unreleased".

## Rules that are never broken

- No secrets, private keys, kubeconfigs, Terraform state, `.tfvars`, subscription IDs or public IPs in Git. Use Jenkins Credentials or Azure Key Vault and document the credential ID instead.
- No stage may report success when its tool or credentials are missing. Fail loudly with an explanation.
- No chargeable or destructive cloud operation runs automatically. It is documented and run by a person, with cleanup steps beside it.
