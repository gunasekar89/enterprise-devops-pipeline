# Known Issues and Fixes

Issues met while building this project. Each entry separates what is **confirmed** (observed, with the fix proven) from what is **assumed** (likely cause, not yet proven). Where the original error text was not captured, the entry says so; add the exact message the next time it happens.

Historical entries 1-6 come from the manual exercises on KodeKloud before this repository existed. They were reported by Guna; logs and screenshots were not captured, so details marked *to confirm* should be filled in from memory or the next reproduction.

---

## 1. Resource group creation refused

- **Context:** Creating a resource group in a KodeKloud Azure playground.
- **Confirmed:** Creating a new resource group was not allowed.
- **Assumed cause:** The playground grants rights only inside one pre-created resource group (scope-limited role assignment or Azure Policy). Exact error text *to confirm*; usually `AuthorizationFailed` for `Microsoft.Resources/subscriptions/resourcegroups/write`.
- **Fix:** Use the existing resource group: `az group list -o table`.
- **Design impact:** Terraform in Phase 3 takes the resource group name as an input variable and reads it with a `data "azurerm_resource_group"` block instead of creating it.

## 2. Premium OS disk rejected by policy

- **Context:** Creating `vm-jenkins-lab` with the portal or CLI default disk type.
- **Confirmed:** A Premium SSD OS disk was rejected by policy.
- **Assumed cause:** An Azure Policy in the playground subscription denies `Premium_LRS` to control cost. The policy name and exact message are *to confirm* (`RequestDisallowedByPolicy`).
- **Fix:** Choose Standard SSD (`--storage-sku StandardSSD_LRS`) or Standard HDD (`Standard_LRS`). Which of the two was used for `vm-jenkins-lab` is *to confirm*.
- **Check allowed values:** `az policy assignment list -o table` (may itself be restricted).

## 3. SSH private key download failed

- **Context:** Creating the VM in the portal with "Generate new key pair", which offers the private key as a one-time download.
- **Confirmed:** The private key download failed.
- **Assumed cause:** Browser pop-up or download blocking, or the download window being lost. *To confirm.*
- **Workaround actually used:** *to confirm* (for example: reset the SSH key from the portal's "Reset password" blade, or recreate the VM with your own public key).
- **Recommended practice (adopted in the runbook):** generate the key pair on your workstation with `ssh-keygen` and give Azure only the public key. If access is lost to an existing VM:
  ```bash
  az vm user update -g "$RG" -n vm-jenkins-lab -u azureuser --ssh-key-value ~/.ssh/vm-jenkins-lab.pub
  ```

## 4. Jenkins port 8080 conflict (separate playground)

- **Context:** Installing Jenkins in a different KodeKloud playground, not on `vm-jenkins-lab`.
- **Confirmed:** Port 8080 was already in use, so Jenkins could not use its default port.
- **Assumed cause:** Another service preinstalled in that playground image listened on 8080. *To confirm which process.*
- **Diagnose:** `sudo ss -ltnp 'sport = :8080'` shows the owning process.
- **Fix:** Run Jenkins on another port with a systemd override, as in the [installation guide](../installation/jenkins-on-azure-vm.md#bind-jenkins-to-localhost-only):
  ```ini
  [Service]
  Environment="JENKINS_PORT=8081"
  ```
  then `sudo systemctl daemon-reload && sudo systemctl restart jenkins`. Editing `/etc/default/jenkins` no longer works on systemd-based packages.

## 5. Maven warnings caused by user permissions

- **Context:** Running `mvn` for `jenkins-java-lab` on the VM.
- **Confirmed:** Maven printed warnings related to user permissions. The build still succeeded. Exact text *to confirm*.
- **Assumed cause (most likely):** Mixed users. The project lived under `/home/azureuser/...` and was built both as `azureuser` and as `jenkins` (or with `sudo`), so `~/.m2` or `target/` contained files owned by a different user.
- **Fix:**
  - Never run Maven with `sudo`.
  - Let Jenkins build in its own workspace (`/var/lib/jenkins/workspace/...`) with its own `~/.m2`, by checking code out from Git instead of pointing the job at `/home/azureuser`.
  - Repair ownership if needed: `sudo chown -R azureuser:azureuser ~/.m2 ~/devops-labs` or `sudo chown -R jenkins:jenkins /var/lib/jenkins/.m2`.
- **Prevention:** the new pipeline checks out from GitHub into the Jenkins workspace, which removes the cause.

## 6. KodeKloud sandbox limitations

- **Confirmed:** Playgrounds are time-limited and resources are deleted at expiry; resource group creation and Premium disks are restricted (entries 1 and 2).
- **Documented by KodeKloud or reported on its forum** (researched 2026-10-20, not yet observed in this project):
  - Sessions last 3 hours; restarting gives a fresh, empty subscription.
  - Regions: West US, East US, Central US, South Central US.
  - VM sizes: `Standard_B1s`, `Standard_B2s`, `Standard_DS1_v2`, `Standard_D2s_v3` (largest: 2 vCPU / 8 GB). Disks: Standard SSD or HDD (LRS), max 128 GB.
  - **No role definitions or assignments.** `az aks update --attach-acr`, `az ad sp create-for-rbac --role` and managed-identity role grants fail. See [ADR-0007](../decisions/0007-registry-auth-without-role-assignments.md).
  - AKS: one node pool, max 2 nodes, Container Insights and alerting off. The node size is listed as `Standard_D2s_v3` on one KodeKloud page and `Standard_B2s` on another.
  - ACR: Basic or Standard SKU, no ACR Tasks (`az acr build` fails).
  - Key Vault: Standard SKU, no purge protection. RBAC-mode vaults are unusable without role assignments, so use access-policy mode.
  - Anything outside the allow-list fails with `RequestDisallowedByPolicy`.
- **Unconfirmed, test in the first session:** NSG creation (one 2024 report of "You do not have access"), public IPs, user-assigned managed identities, Key Vault access-policy mode, ACR tokens:
  ```bash
  RG=$(az group list --query "[0].name" -o tsv)
  az network nsg create -g "$RG" -n t-nsg
  az network public-ip create -g "$RG" -n t-pip --sku Standard
  az identity create -g "$RG" -n t-mi
  az keyvault create -g "$RG" -n "kv$RANDOM" --enable-rbac-authorization false
  az acr create -g "$RG" -n "acr$RANDOM" --sku Standard
  ```
  Record each result here, then delete the test resources.
- **Mitigation:** everything is reproducible from this repository; no state lives only in the playground. Export Jenkins job configs before expiry. Each later phase starts with a short feasibility check of the services it needs. Kubernetes work stays runnable on kind or k3d as a fallback.

---

## Found during Phase 0 (2026-10-19)

## 7. Maven used Java 8 although Java 21 was on PATH

- **Confirmed:** In the Jenkinsfile Runner test, `java -version` on `PATH` reported 21 but the build failed with `Detected JDK /opt/java/openjdk/jre is version 1.8.0-262 which is not in the allowed range [21,)`.
- **Confirmed cause:** The Maven wrapper (like `mvn`) uses `JAVA_HOME` when it is set, ignoring `PATH`.
- **Fix:** `ci/scripts/verify-environment.sh` now checks the JDK in `JAVA_HOME` when set, and the Jenkins guide sets `JAVA_HOME` on the node. The Maven Enforcer rule caught it before any compilation happened.

## 8. Spring Boot 4.1.1 shipped with vulnerable Tomcat and Jackson

- **Confirmed:** Trivy found 3 critical CVEs in `tomcat-embed-core` 11.0.24 and 5 high CVEs in `jackson-core`/`jackson-databind` 3.1.5.
- **Fix:** Version overrides in `application/pom.xml`; rescan clean. See [security-model.md](../security/security-model.md#handling-a-vulnerable-transitive-dependency).

## 9. JDK 21 warnings about dynamically loaded agents in tests

- **Confirmed:** `WARNING: A Java agent has been loaded dynamically (byte-buddy-agent...)` during tests. Mockito (pulled in by `spring-boot-starter-test`) attaches its agent at runtime, which JDK 21 warns about.
- **Fix:** Surefire `argLine` adds `-XX:+EnableDynamicAgentLoading -Xshare:off` while keeping JaCoCo's `@{argLine}`.

## Found during Phase 1 (2026-10-20)

## 10. Jenkins apt signing key rotated

- **Confirmed:** On a fresh Ubuntu 24.04 VM, `apt-get update` failed with `NO_PUBKEY 7198F4B714ABFC68` and `The repository 'https://pkg.jenkins.io/debian-stable binary/ Release' is not signed`.
- **Confirmed cause:** `jenkins.io-2023.key` (`5BA31D57EF5975CA`) expired on 2026-03-26. The repository is now signed with `jenkins.io-2026.key` (`7198F4B714ABFC68`, valid until 2028-12), checked with `gpg --show-keys`.
- **Fix:** Download `https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key` into `/etc/apt/keyrings/jenkins-keyring.asc`, keeping the `signed-by=` line in `jenkins.list`, then `apt-get update`.
- **Interview point:** apt refusing an unsigned repository is supply-chain protection working as intended. The fix is to verify the new key's ID against the error and pin it to that one repository with `signed-by`, never to add `trusted=yes`.

## 11. Jenkins 2.580.1 warnings on a fresh install

- **Confirmed:** After the setup wizard, Manage Jenkins shows three warnings: building on the built-in node is a security issue; Java 21 support ends on or after 2027-09-30; Content Security Policy is disabled.
- **Decision:** Accepted for the lab. Builds stay on the built-in node until agents are added; the controller moves to Java 25 before the 2027 deadline (builds keep JDK 21 via the node's `JAVA_HOME`); CSP is enabled once the plugin set is final and tested.
- **Interview point:** A new controller's hardening warnings are a backlog, not noise: agents with `executors = 0` on the controller, CSP after plugin testing, JDK upgrades planned against the Jenkins Java support policy.

## 12. `No such DSL method 'withSonarQubeEnv'` when RUN_SONARQUBE is ticked

- **Confirmed:** Build #4 on `vm-jenkins-lab` (2026-10-20) failed in the SonarQube stage with `java.lang.NoSuchMethodError: No such DSL method 'withSonarQubeEnv' found among steps [...]`, so Docker Build was skipped. Gitleaks (11 commits, no leaks) and Trivy fs (no HIGH/CRITICAL) had passed.
- **Confirmed cause:** `RUN_SONARQUBE` was ticked before the SonarQube Scanner plugin was installed. `No such DSL method 'X'` always means the plugin providing step `X` is missing.
- **Fix:** Untick `RUN_SONARQUBE` until SonarQube is set up. The stage now catches the error and fails with a one-line explanation instead of a stack trace.
