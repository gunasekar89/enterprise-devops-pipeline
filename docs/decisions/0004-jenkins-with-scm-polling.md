# ADR-0004: Jenkins CI behind an SSH tunnel, triggered by SCM polling

- Status: Accepted
- Date: 2026-10-19

## Context

The project brief names Jenkins. Jenkins runs on a temporary playground VM. Exposing Jenkins to the Internet so GitHub can send webhooks would publish a high-value admin UI.

## Options

1. Open port 8080 to the Internet for webhooks.
2. Open 8080 only to GitHub's published hook IP ranges.
3. **Keep Jenkins private and poll GitHub every few minutes.**
4. Webhook relay (smee.io or similar) from inside the VM.
5. Use GitHub Actions instead of Jenkins.

## Decision

Option 3. Jenkins binds to 127.0.0.1, people reach it through `ssh -L`, and the Jenkinsfile declares `pollSCM('H/5 * * * *')`.

## Consequences

- No inbound port beyond SSH. Simple and safe for a lab.
- Builds start up to 5 minutes after a push. Acceptable for one developer.
- Polling does not scale to hundreds of jobs; in an enterprise you would use webhooks through an ingress with TLS and allow-listing, or the GitHub App integration with a reverse proxy.
- GitHub PR status checks need Jenkins to call the GitHub API outbound (GitHub Branch Source plugin with a GitHub App or token). That is outbound only and stays compatible with this decision; evaluated in Phase 1.
- Option 5 is noted for later comparison in interviews: Actions removes the CI server entirely but the brief targets Jenkins skills.
