# ADR-0006: Terraform rather than Bicep for Azure infrastructure

- Status: Proposed (to be accepted when Phase 3 starts)
- Date: 2026-10-19

## Context

Phase 3 provisions the network, Jenkins VM, ACR, AKS and identities. The brief allows Terraform or Bicep.

## Options

1. **Terraform with the `azurerm` provider.** Multi-cloud skill, large ecosystem, explicit plan/apply, state must be stored somewhere.
2. **Bicep.** Azure-native, no state file, day-zero support for new Azure features, Azure-only.

## Decision (proposed)

Terraform, because it is the more transferable skill for the target roles and the brief lists it first. State stays local for each session (never committed; `*.tfstate` is in `.gitignore`), or goes to the Terraform Cloud free tier when it must be shared. A storage account backend in the playground would be deleted with the session, so it adds nothing.

## Consequences

- Must handle the playground's pre-created resource group as a data source, not a resource.
- State is lost when the playground expires; that is acceptable because the playground resources are lost too. The code, not the state, is the asset.
- A short Bicep example may be added for comparison in interview notes.
- No role assignments are possible in the playground, so Terraform must not create any (`azurerm_role_assignment` would fail with `AuthorizationFailed`). Registry access follows ADR-0007.
- Disk types must be set explicitly to `StandardSSD_LRS` or `Standard_LRS`, because the Premium default is blocked by policy.
