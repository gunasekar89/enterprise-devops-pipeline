# ADR-0008: Build once, promote by image digest

- Status: Accepted (implementation in Phases 2-4)
- Date: 2026-10-20

## Context

Dev and prod must run exactly what was tested. Tags such as `:latest` or even `:<git-sha>` are mutable pointers in a registry; anyone with push rights can move them.

## Options

1. **Rebuild per environment.** Simple, but prod runs bytes that were never tested in dev.
2. **Promote by tag.** One build, but the tag can be overwritten between dev and prod.
3. **Promote by digest.** One build; Git records `image@sha256:...`, which is immutable.

## Decision

Option 3. Jenkins builds and tests once, pushes the image tagged with the Git SHA for readability, records the digest returned by the push, and commits that digest to the dev values in `gitops/`. Promotion to prod is a pull request that copies the same digest. Cosign signs the digest, and the SBOM is attached to it.

## Consequences

- A running pod can be traced to its digest, signature, SBOM and commit.
- Rollback is a Git revert to the previous digest.
- Helm values must take a digest field, and humans read the Git SHA tag alongside it.
- Later, a Kyverno policy can refuse any image that is not referenced by a signed digest.
