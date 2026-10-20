# Evidence: Repository Published and Workstation Set Up (Phase 1)

- **Date:** 2026-10-20
- **Machine:** Guna's MacBook Pro (Apple silicon, macOS 27.0.1)
- **Who ran it:** Claude, through a Remote Control session in Guna's terminal, with Guna's approval for each outward step

## GitHub repository

| Step | Result |
|---|---|
| Check the name is free: `gh repo view gunasekar89/enterprise-devops-pipeline` | Not found, so nothing was overwritten |
| `gh repo create gunasekar89/enterprise-devops-pipeline --public --description "..."` | Created, empty (no README, license or .gitignore) |
| Push `main` | `main` at `6557d93` (6 commits) on https://github.com/gunasekar89/enterprise-devops-pipeline |

## Workstation

| Item | Result |
|---|---|
| `git clone` into `~/enterprise-devops-pipeline` | Latest commit `6557d93` |
| Git | 2.51.0 |
| GitHub CLI | 2.98.0, logged in as gunasekar89 |
| Azure CLI | 2.90.0 |
| Docker | 29.8.1 installed (engine state not checked) |
| JDK | Homebrew `openjdk@21`, `openjdk version "21.0.12.1"` |
| `cd application && ./mvnw -B -ntp clean verify` | Tests run: 12, Failures: 0, Errors: 0, Skipped: 0 · BUILD SUCCESS (Maven 3.9.11 downloaded by the wrapper) |
| `bash ci/scripts/verify-environment.sh` | `Environment OK` (Git 2.51.0, Java 21.0.12.1, Maven 3.9.11) |
| SSH key `~/.ssh/vm-jenkins-lab` | Created (ed25519, mode 600). The private key was not displayed. |

## Notes

- `brew install --cask temurin@21` needs the Mac password, so Homebrew's `openjdk@21` (no password) was installed instead. Either JDK works for this project.
- The Homebrew JDK is not the default `java` in new terminals until `JAVA_HOME` and `PATH` are set (see `docs/installation/local-development.md`).
- This confirms the build is reproducible on a second platform (macOS arm64) in addition to the Linux runs in Phase 0.
