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
- **Assumed / to test before relying on them:** limits on VM sizes, public IPs, AKS node counts and SKUs, role assignments (needed for AKS `AcrPull` and CI identities), Key Vault, and outbound network rules.
- **Mitigation:** everything is reproducible from this repository; no state lives only in the playground. Export Jenkins job configs before expiry. Each later phase starts with a short feasibility check of the services it needs.

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
