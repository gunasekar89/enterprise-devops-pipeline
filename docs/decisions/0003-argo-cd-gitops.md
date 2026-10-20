# ADR-0003: Argo CD as the GitOps controller

- Status: Accepted (implementation in Phase 4)
- Date: 2026-10-19

## Context

Deployments to AKS must be auditable, repeatable and easy to roll back. Jenkins should not hold cluster-admin credentials.

## Options

1. **Jenkins runs `helm upgrade` / `kubectl apply`** (push model).
2. **Argo CD** watches Git and reconciles the cluster (pull model).
3. **Flux CD**, also pull-based.

## Decision

Argo CD. Jenkins's job ends at "image pushed and signed, Helm values updated in Git". Argo CD in the cluster applies the change.

## Consequences

- No cluster credentials in Jenkins; the cluster pulls from Git. This is the trust boundary between the CI plane and the CD plane in the architecture diagram.
- Git history is the deployment history. Rollback = revert the values commit, or roll back in Argo CD's history.
- Drift (manual `kubectl edit`) is detected and can be self-healed.
- Argo CD has a UI that is useful for demos and interviews; Flux is CLI-first. Both are CNCF graduated.
- Extra component to run and secure (its UI must not be public; use port-forward or the SSH tunnel pattern).
- Production promotion becomes a pull request to the prod values file, which gives a natural approval gate.
