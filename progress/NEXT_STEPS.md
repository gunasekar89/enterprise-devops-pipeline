# Next Steps

## Needs Guna

1. **Approve publishing to GitHub.** Then either link GitHub to Claude so it can push, or run the commands in "Publish" below yourself.
2. **Confirm or correct the historical details** marked *to confirm* in [known-issues.md](../docs/troubleshooting/known-issues.md): exact error messages, which disk SKU was accepted, how SSH access was recovered, what occupied port 8080, the Maven warning text, and the date of the manual work.
3. **Optional:** if you still have the original `jenkins-java-lab` source or the earlier documentation starter pack, share it so useful parts can be merged instead of rewritten.
4. **Review the author identity** on the local commits (`git log --format='%an <%ae>'`). Change it before pushing if you prefer your GitHub no-reply address.

## Publish (after approval)

If the repository does **not** exist yet, create it empty (no README, license or .gitignore, to avoid a merge):

```bash
gh repo create gunasekar89/enterprise-devops-pipeline --public \
  --description "End-to-end enterprise DevOps pipeline on Azure: Jenkins, DevSecOps, ACR, AKS, Helm, Argo CD, Prometheus, Grafana"
```

or on github.com → New repository → name `enterprise-devops-pipeline` → leave all "initialize" boxes unticked.

Then from the repository root:

```bash
git remote add origin https://github.com/gunasekar89/enterprise-devops-pipeline.git
git push -u origin main
```

If the repository **already exists with commits**, do not force-push. Fetch first and decide how to merge:

```bash
git remote add origin https://github.com/gunasekar89/enterprise-devops-pipeline.git
git fetch origin
git log --oneline origin/main | head
```

After pushing: Settings → Branches → add a rule for `main` (require a pull request, block force-push); Settings → Code security → enable Dependabot alerts and private vulnerability reporting.

## Recommended next implementation step: Phase 1

1. Start a fresh KodeKloud Azure playground.
2. Rebuild `vm-jenkins-lab` by following [jenkins-on-azure-vm.md](../docs/installation/jenkins-on-azure-vm.md) exactly; fix the runbook wherever reality differs.
3. Create the `enterprise-devops-pipeline` job ([jenkins-pipeline.md](../docs/cicd/jenkins-pipeline.md)), run it once, push a small commit, and confirm polling starts a build within about 5 minutes.
4. Save the console log and screenshots (stage view, test results, artifacts, polling log) into `progress/evidence/phase-1/`, then mark P1-3 Verified.
