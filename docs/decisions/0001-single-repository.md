# ADR-0001: Single repository for application, CI, infrastructure and GitOps

- Status: Accepted
- Date: 2026-10-19

## Context

The project spans application code, a Jenkins pipeline, Terraform, Kubernetes manifests, Helm charts and Argo CD configuration. One person builds it across many short playground sessions, and it must be easy to clone and rebuild.

## Options

1. **One repository** with top-level folders per concern.
2. **Several repositories** (app, infrastructure, GitOps config), the usual enterprise split.
3. App repository plus a separate GitOps repository from day one.

## Decision

Option 1 for now. Folders are created only when they get real content (no empty placeholders), so `infrastructure/`, `kubernetes/`, `gitops/` and `observability/` arrive in their phases.

## Consequences

- One clone gives a reader everything; documentation links stay simple.
- Argo CD will watch a path in the same repository. CI commits that bump image tags then trigger CI polling again; Phase 4 must exclude the GitOps path from CI triggers (or use `[skip ci]`) to avoid loops.
- Access control is coarser than with split repositories: anyone who can change the app can change prod config. Acceptable for a single-maintainer project; compensated by branch protection and PR review.
- **Revisit** when the GitOps config needs different reviewers or release cadence. The split will be: `enterprise-devops-pipeline` (app + CI), `enterprise-devops-infra` (Terraform), `enterprise-devops-gitops` (Helm values + Argo CD apps).
