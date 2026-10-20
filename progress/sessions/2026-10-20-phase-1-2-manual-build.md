# Session log 2026-10-20: Phase 1 and Phase 2A built by hand

Every step taken in today's KodeKloud Azure playground, in order, with the exact commands that worked. The goal for the next session is to turn this list into scripts, so that a fresh playground reaches the same state in one run instead of about two hours of clicking.

Placeholders: `<VM_IP>` is the VM's public IP, `<MY_IP>` is the workstation's public IP. Neither belongs in committed files.

Result at the end of the session: Jenkins 2.580.1 on `vm-jenkins-lab`, reachable only through an SSH tunnel, building `main` on every push with tests, Gitleaks, Trivy and a Docker image. Evidence: [phase-1](../evidence/phase-1/jenkins-first-builds.md), [phase-2](../evidence/phase-2/security-gates-and-image.md).

## 0. Workstation (macOS, done once, survives playgrounds)

| Step | Command or setting | Notes |
|---|---|---|
| JDK 21 | `brew install openjdk@21` plus `JAVA_HOME` lines in `~/.zshrc` | [local-development.md](../../docs/installation/local-development.md) |
| Clone | `git clone https://github.com/gunasekar89/enterprise-devops-pipeline.git` | |
| SSH key | `ssh-keygen -t ed25519 -f ~/.ssh/vm-jenkins-lab -C vm-jenkins-lab -N ""` | Private key never leaves the Mac |
| GitHub push auth | `gh auth setup-git` | `git push` with a password fails: GitHub only accepts tokens. `gh` was already logged in |

## 1. VM through the Azure portal (manual today)

Portal → Virtual machines → Create, in the playground subscription `azurekmlprod` and its single resource group. Values used:

| Setting | Value | Why |
|---|---|---|
| Name | `vm-jenkins-lab` | Matches the runbook |
| Region / zone | Central US, zone 1 | The resource group's region |
| Image | Ubuntu Server 24.04 LTS | |
| Security type | Trusted launch | Default |
| Size | `Standard_D2s_v3` (2 vCPU, 8 GiB) | Largest the playground allows; room for SonarQube |
| OS disk | Standard SSD | Premium is blocked |
| Authentication | SSH public key, user `azureuser`, key = contents of `~/.ssh/vm-jenkins-lab.pub` | |
| Inbound ports | None at creation, then an NSG rule: TCP 22 from `<MY_IP>/32` only | Never 8080 |

Check: `ssh -i ~/.ssh/vm-jenkins-lab azureuser@<VM_IP>`.

## 2. Software on the VM

```bash
sudo apt-get update
sudo apt-get install -y openjdk-21-jdk git fontconfig curl

# Jenkins LTS repo. The 2023 key expired on 2026-03-26; the 2026 key is 7198F4B714ABFC68.
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL -o /etc/apt/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update && sudo apt-get install -y jenkins

# Listen on localhost only
sudo mkdir -p /etc/systemd/system/jenkins.service.d
printf '[Service]\nEnvironment="JENKINS_LISTEN_ADDRESS=127.0.0.1"\n' \
  | sudo tee /etc/systemd/system/jenkins.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart jenkins
sudo ss -ltnp | grep 8080          # [::ffff:127.0.0.1]:8080 only

# Phase 2 tools
sudo apt-get install -y docker.io
sudo usermod -aG docker jenkins
curl -fsSL -o /tmp/gitleaks.tgz \
  https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz
sudo tar -xzf /tmp/gitleaks.tgz -C /usr/local/bin gitleaks
curl -fsSL -o /tmp/trivy.deb \
  https://github.com/aquasecurity/trivy/releases/download/v0.76.0/trivy_0.76.0_Linux-64bit.deb
sudo dpkg -i /tmp/trivy.deb
sudo systemctl restart jenkins     # picks up the docker group
sudo -u jenkins docker ps          # header only, no "permission denied"
```

Versions installed: OpenJDK 21.0.12.1, Git 2.43.0, Jenkins 2.580.1, Docker 29.1.3, Gitleaks 8.30.1, Trivy 0.76.0.

Gaps to close when scripting: verify the Gitleaks and Trivy downloads against their published SHA-256 checksums; consider `docker-buildx` to remove the legacy-builder warning.

## 3. Reach Jenkins from the Mac

```bash
ssh -i ~/.ssh/vm-jenkins-lab -N -L 8080:localhost:8080 azureuser@<VM_IP>
```

Leave it running and browse to `http://localhost:8080`.

## 4. Jenkins setup wizard (manual today)

1. Unlock with `sudo cat /var/lib/jenkins/secrets/initialAdminPassword` (never paste it anywhere).
2. Install suggested plugins (92 plugins, includes Pipeline, Git, JUnit, Timestamper, Pipeline Graph View).
3. Create the admin user; keep the URL `http://localhost:8080/`.
4. Manage Jenkins → Nodes → Built-In Node → Configure → Environment variables: `JAVA_HOME` = `/usr/lib/jvm/java-21-openjdk-amd64`. Executors stay at 2.

Warnings shown on a fresh controller and accepted for the lab: building on the built-in node, Java 21 support ending 2027-09-30, CSP disabled ([known-issues #11](../../docs/troubleshooting/known-issues.md)).

## 5. Pipeline job (manual today)

New Item → `enterprise-devops-pipeline` → Pipeline:

| Field | Value |
|---|---|
| Definition | Pipeline script from SCM |
| SCM | Git, `https://github.com/gunasekar89/enterprise-devops-pipeline.git`, no credentials |
| Branch | `*/main` |
| Script Path | `ci/Jenkinsfile` |

Polling (`H/5 * * * *`) comes from the Jenkinsfile and starts working after the first build.

## 6. Builds run

| Build | Commit | Trigger | Parameters | Result |
|---|---|---|---|---|
| #1 | 4636e5a | manual | all off | SUCCESS, 12 tests |
| #2 | bb4df03 | SCM change (push from the Mac) | all off | SUCCESS: polling proven |
| #3 | 13063db | SCM change | all off | SUCCESS |
| #4 | 13063db | manual | Gitleaks, Trivy, SonarQube (by mistake), image | FAILURE in SonarQube: plugin missing ([known-issues #12](../../docs/troubleshooting/known-issues.md)) |
| #5 | 56714ca | SCM change | all off | (not checked) |
| #6 | 56714ca | manual | Gitleaks, Trivy, image | SUCCESS: no leaks, no HIGH/CRITICAL, image `enterprise-devops-app:56714ca` |

Build numbers #5 and #6 are inferred from the order of events.

Checks run by hand on the VM: the container starts, health UP, runs as uid 10001, `trivy image` 0 HIGH/CRITICAL on Ubuntu 24.04 and all jars; Gitleaks exits 1 on a fake AWS key in a throwaway repository.

## 7. Changed after the hand checks, not yet run in Jenkins

Commit 5eb2650 adds the **Image Scan (Trivy)** and **Container Smoke Test** stages and turns Gitleaks, Trivy and the image stages on by default. The smoke test script passed locally and was parse-checked in Jenkinsfile Runner, but its first real Jenkins run is still to come. Jenkins keeps the old parameter defaults until one build has run with the new Jenkinsfile.

## Automation plan for the next session

| Manual step today | Automated replacement | Notes |
|---|---|---|
| 1. Portal VM creation and NSG rule | `az vm create` script with `--nsg-rule NONE` plus one `az network nsg rule create` for `<MY_IP>/32` (already drafted in [jenkins-on-azure-vm.md](../../docs/installation/jenkins-on-azure-vm.md)); Terraform in Phase 3 | Inputs: resource group, `MY_IP`, public key path |
| 2. Software install | cloud-init file passed with `az vm create --custom-data`, containing the commands in section 2 plus checksum checks | Runs on first boot, no SSH needed |
| 4. Wizard, plugins, admin user | `jenkins-plugin-manager` with a pinned `plugins.txt`; Configuration as Code (`jenkins.yaml`) for the admin user, `JAVA_HOME` and security settings; `-Djenkins.install.runSetupWizard=false` | Admin password read from a prompt or environment variable, never committed |
| 5. Job creation | Job DSL or a CasC `jobs:` entry for `enterprise-devops-pipeline` | |
| 6. First build and checks | A verify script: listener on 127.0.0.1 only, tool versions, `curl` the job's last build status through the tunnel | Turns this log's checks into one command |

Order for tomorrow: start a new playground → run the VM script with cloud-init → open the tunnel → confirm Jenkins comes up already configured with the job → push a commit → confirm the first full-pipeline build (including the two new stages) → save evidence. Then SonarQube if time allows.
