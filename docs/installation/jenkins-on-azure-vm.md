# Jenkins on an Azure VM (KodeKloud Playground)

## Objective

Recreate `vm-jenkins-lab`: an Ubuntu 24.04 VM in an Azure playground running Jenkins LTS with JDK 21 and Git, reachable only through an SSH tunnel.

> **Status.** This VM was built by hand before this repository existed (see [IMPLEMENTATION_LOG](../../progress/IMPLEMENTATION_LOG.md)). The commands below are the reproducible version of that work. They have **not yet been re-run end to end** from this document; the first run on a fresh playground is Phase 1's verification task. Record any differences in this file.

## Why this design

- A VM is the simplest Jenkins host a playground allows. Running Jenkins in AKS comes later, once AKS itself is proven in the playground.
- No public Jenkins port: Jenkins has full access to credentials and build agents, so an exposed login page is a high-value target. The SSH tunnel reuses the one port that must be open anyway.

## Prerequisites

- Active KodeKloud Azure playground and its credentials.
- Azure CLI logged in to the playground: `az login` (use the playground's user, or Cloud Shell from the Azure portal).
- An SSH key pair on your workstation (created in step 1).

## 1. Create an SSH key on your workstation

Generating the key locally avoids the portal's private-key download, which failed in an earlier session (see [known issues](../troubleshooting/known-issues.md#3-ssh-private-key-download-failed)).

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vm-jenkins-lab -C "vm-jenkins-lab" -N ""
chmod 600 ~/.ssh/vm-jenkins-lab
```

The private key never leaves your machine and is never committed.

## 2. Find the playground's resource group

Playgrounds provide one resource group; creating another was refused.

```bash
az group list --query "[].{name:name, location:location}" -o table
export RG=<resource-group-from-the-list>
export LOCATION=$(az group show -n "$RG" --query location -o tsv)
export MY_IP=$(curl -s https://api.ipify.org)
```

## 3. Create the VM

```bash
az vm create \
  --resource-group "$RG" \
  --name vm-jenkins-lab \
  --location "$LOCATION" \
  --image Ubuntu2404 \
  --size Standard_B2s \
  --storage-sku StandardSSD_LRS \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/vm-jenkins-lab.pub \
  --public-ip-sku Standard \
  --nsg-rule NONE \
  --output table
```

- `--storage-sku StandardSSD_LRS`: Premium was rejected by playground policy. If Standard SSD is also refused, use `Standard_LRS`.
- `--size`: if `Standard_B2s` is not allowed, list permitted sizes with `az vm list-sizes -l "$LOCATION" -o table` and pick 2 vCPU / 4 GiB or larger.
- `--image Ubuntu2404`: if your Azure CLI does not know the alias, use `Canonical:ubuntu-24_04-lts:server:latest`.
- `--nsg-rule NONE`: no inbound rule is created; step 4 adds SSH from your IP only.

## 4. Allow SSH from your IP only

```bash
NSG=$(az network nsg list -g "$RG" --query "[?contains(name,'vm-jenkins-lab')].name | [0]" -o tsv)
az network nsg rule create -g "$RG" --nsg-name "$NSG" -n allow-ssh-my-ip \
  --priority 1000 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes "$MY_IP/32" --destination-port-ranges 22

export VM_IP=$(az vm show -d -g "$RG" -n vm-jenkins-lab --query publicIps -o tsv)
ssh -i ~/.ssh/vm-jenkins-lab azureuser@"$VM_IP" 'lsb_release -ds'
# Ubuntu 24.04.x LTS
```

Do not paste `$VM_IP` into any committed file.

## 5. Install JDK 21, Git and Jenkins LTS on the VM

Run on the VM (`ssh -i ~/.ssh/vm-jenkins-lab azureuser@"$VM_IP"`):

```bash
sudo apt-get update
sudo apt-get install -y openjdk-21-jdk git fontconfig curl

# Jenkins LTS apt repository. Check https://www.jenkins.io/doc/book/installing/linux/
# for the current signing-key URL before running; Jenkins rotates it periodically.
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL -o /etc/apt/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install -y jenkins
```

Install a full JDK (`openjdk-21-jdk`), not only a JRE: the pipeline compiles code. Maven itself is optional on the VM because the repository's wrapper downloads Maven 3.9.11 into the `jenkins` user's `~/.m2`.

### Bind Jenkins to localhost only

The tunnel connects to `localhost`, so Jenkins does not need to listen on the VM's network interface.

```bash
sudo systemctl edit jenkins
```

Add, then save:

```ini
[Service]
Environment="JENKINS_LISTEN_ADDRESS=127.0.0.1"
# Uncomment if 8080 is already taken on this VM (see known issues #4):
# Environment="JENKINS_PORT=8081"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart jenkins
sudo systemctl status jenkins --no-pager | head -5     # active (running)
sudo ss -ltnp | grep java                               # 127.0.0.1:8080
```

## 6. Open the SSH tunnel and unlock Jenkins

On your workstation:

```bash
ssh -i ~/.ssh/vm-jenkins-lab -N -L 8080:localhost:8080 azureuser@"$VM_IP"
```

Leave it running. If local port 8080 is busy, use `-L 9090:localhost:8080` and browse to `http://localhost:9090`.

Get the initial admin password on the VM:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Open `http://localhost:8080`, paste the password, choose **Install suggested plugins**, and create an admin user with a strong password stored in your password manager.

## 7. Configure the built-in node

**Manage Jenkins → Nodes → Built-In Node → Configure → Node Properties → Environment variables**:

| Name | Value |
|---|---|
| `JAVA_HOME` | `/usr/lib/jvm/java-21-openjdk-amd64` |

The Maven wrapper prefers `JAVA_HOME`; setting it explicitly removes any doubt about which JDK the build uses. The pipeline's "Verify Environment" stage fails clearly if it is wrong.

## 8. Create the pipeline job

Follow [cicd/jenkins-pipeline.md](../cicd/jenkins-pipeline.md).

## Verification checklist

```bash
# On the VM
java -version                    # openjdk version "21..."
git --version
systemctl is-active jenkins      # active
sudo ss -ltnp | grep 8080        # 127.0.0.1:8080, not 0.0.0.0:8080
```

From your workstation without the tunnel, `curl -m 5 http://$VM_IP:8080` must time out.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `RequestDisallowedByPolicy` on VM create | Disk SKU or VM size not allowed | Use `StandardSSD_LRS` / `Standard_LRS`, try another size |
| `AuthorizationFailed` on `az group create` | Playground forbids new resource groups | Use the existing group from step 2 |
| `Permission denied (publickey)` | Wrong key or user | `ssh -v -i ~/.ssh/vm-jenkins-lab azureuser@...`; check key permissions are `600` |
| Jenkins fails to start, `Address already in use` | Port 8080 taken | `sudo ss -ltnp 'sport = :8080'`; set `JENKINS_PORT` (step 5) |
| Tunnel says `bind: Address already in use` | Local 8080 busy | Use another local port: `-L 9090:localhost:8080` |
| Jenkins UI is slow or builds are killed | VM too small | At least 2 vCPU / 4 GiB; check `free -h` and `dmesg | grep -i oom` |

## Security considerations

- Inbound only TCP 22, only from your current IP. Update the rule if your IP changes instead of widening it.
- Jenkins listens on 127.0.0.1.
- Use a strong admin password; disable sign-up (default in new installs).
- The initial admin password file is deleted by Jenkins after setup; do not copy it anywhere.

## Cleanup and rollback

Playgrounds delete everything at expiry. To clean up earlier:

```bash
az vm delete -g "$RG" -n vm-jenkins-lab --yes
# Then delete the leftover NIC, public IP, NSG and OS disk shown by:
az resource list -g "$RG" --query "[?contains(name,'vm-jenkins-lab')].{name:name,type:type}" -o table
```

These are destructive: run them yourself, only in the playground resource group, and only after exporting anything you want to keep (job configs: `/var/lib/jenkins/jobs/*/config.xml`).

## Interview questions

- Why bind Jenkins to localhost and tunnel instead of opening port 8080 with an NSG rule for your IP?
- What is in `JENKINS_HOME` and how would you back it up and restore it?
- How do you keep the controller from running builds in a real setup (agents, `numExecutors=0`)?
- What changes if Jenkins must receive GitHub webhooks?
