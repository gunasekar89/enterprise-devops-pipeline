# ADR-0007: Registry access without Azure role assignments

- Status: Accepted (implementation in Phases 3 and 4)
- Date: 2026-10-20

## Context

The standard Azure design gives AKS's kubelet identity the `AcrPull` role on the registry (`az aks update --attach-acr`) and gives the CI identity `AcrPush`. KodeKloud playgrounds do not allow creating or modifying role assignments; `--attach-acr`, `az ad sp create-for-rbac --role` and managed-identity role grants are all reported to fail. Source: [KodeKloud supported resources](https://support.kodekloud.com/cloud-playground-support) and forum reports from 2024 to 2026.

## Options

1. **ACR repository-scoped tokens** (`az acr token create`, Standard SKU): a push token for Jenkins and a pull-only token for the cluster. Uses ACR's own permission model, no Azure RBAC.
2. **ACR admin user**: one username/password with full push and pull on the whole registry.
3. **`AcrPull` role assignment** (the production pattern). Not possible in the playground.
4. **Public registry** (Docker Hub, GHCR). Avoids Azure auth but drops ACR from the project.

## Decision

Option 1. Jenkins pushes with a token scoped to `enterprise-devops-app` with `content/write`, stored in Jenkins Credentials. The cluster pulls with a separate pull-only token, stored as a Kubernetes `docker-registry` secret and referenced as `imagePullSecrets` through Helm values. The admin user (option 2) is the fallback if tokens turn out to be unavailable, and stays disabled otherwise.

## Consequences

- Least privilege is kept within ACR: CI can push only one repository; the cluster can only pull.
- Tokens are long-lived secrets that must be rotated; managed identities would avoid that. This is a documented gap compared with production.
- The Helm chart takes `imagePullSecrets` as a value, so the same chart works with `AcrPull` (empty value) in a normal subscription.
- Interview point: explain both designs, and why the production one (managed identity + `AcrPull`, no secrets) is better.
