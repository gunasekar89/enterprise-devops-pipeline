# ADR-0006: Terraform rather than Bicep for Azure infrastructure

- Status: Proposed (to be accepted when Phase 3 starts)
- Date: 2026-10-19

## Context

Phase 3 provisions the network, Jenkins VM, ACR, AKS and identities. The brief allows Terraform or Bicep.

## Options

1. **Terraform with the `azurerm` provider.** Multi-cloud skill, large ecosystem, explicit plan/apply, state must be stored somewhere.
2. **Bicep.** Azure-native, no state file, day-zero support for new Azure features, Azure-only.

## Decision (proposed)

Terraform, because it is the more transferable skill for the target roles and the brief lists it first. State goes to an Azure Storage account in the playground resource group when allowed, otherwise local state that is never committed (`*.tfstate` is in `.gitignore`).

## Consequences

- Must handle the playground's pre-created resource group as a data source, not a resource.
- State is lost when the playground expires; that is acceptable because the playground resources are lost too. The code, not the state, is the asset.
- A short Bicep example may be added for comparison in interview notes.
- Open question to test in Phase 3: whether the playground allows creating a storage account and the role assignments AKS needs.
