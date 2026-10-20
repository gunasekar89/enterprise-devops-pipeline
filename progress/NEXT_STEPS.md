# Next Steps

Last updated: 2026-10-20, after Phase 1 and Phase 2A were built by hand. Every step from that session is in [sessions/2026-10-20-phase-1-2-manual-build.md](sessions/2026-10-20-phase-1-2-manual-build.md).

## Next session: automate the rebuild, then validate

1. Start a fresh KodeKloud Azure playground.
2. Write and run a VM provisioning script (`az vm create` + NSG rule for your IP) with a cloud-init file that installs JDK 21, Git, Jenkins (2026 key, localhost only), Docker, Gitleaks and Trivy, with checksum checks.
3. Configure Jenkins as code: pinned `plugins.txt`, Configuration as Code for the admin user and `JAVA_HOME`, the setup wizard disabled, and the `enterprise-devops-pipeline` job defined in code.
4. Open the tunnel, push a commit, and confirm the first full-pipeline build, including the new **Image Scan (Trivy)** and **Container Smoke Test** stages (commit 5eb2650, not yet run in Jenkins).
5. Save evidence in `progress/evidence/phase-2/`.
6. If time allows: SonarQube (server in a container on the VM, Scanner plugin, quality gate).

## Needs Guna

- Protect `main` on GitHub: Settings → Rules → Rulesets → New branch ruleset (restrict deletions, block force pushes, require a pull request). This is P1-2, the last Phase 1 item.
- Optional: screenshots of the Pipeline Overview, Test Result and Artifacts pages for the portfolio.

## Later

- Syft SBOM, Cosign signing, ACR push (Phase 3), then AKS, Helm and Argo CD (Phase 4). See the [roadmap](../docs/roadmap.md).
