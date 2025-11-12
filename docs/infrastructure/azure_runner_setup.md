# Azure VM Setup for GitHub Self-Hosted Runner

This document provides a comprehensive guide for setting up a GitHub self-hosted runner on an Azure Virtual Machine.

## 1. Prerequisites

- An active Azure subscription.
- A GitHub repository where you want to add the self-hosted runner.
- Owner or admin privileges for the GitHub repository.
- Azure CLI or access to the Azure Portal.

## 2. VM Creation

We will create an Ubuntu 22.04 LTS VM with a `Standard_D4s_v3` instance type.

### Using Azure Portal

1.  Navigate to the Azure Portal and select "Create a resource".
2.  Search for "Virtual machine" and click "Create".
3.  **Basics:**
    *   **Subscription:** Select your subscription.
    *   **Resource group:** Create a new or select an existing one.
    *   **Virtual machine name:** `github-runner-vm`
    *   **Region:** Choose a region that is geographically close to you.
    *   **Image:** Ubuntu Server 22.04 LTS - Gen2.
    *   **Size:** `Standard_D4s_v3` (4 vCPUs, 16 GiB memory).
    *   **Authentication type:** SSH public key.
    *   **Username:** `azureuser`
4.  **Disks:** Standard SSD is sufficient for the OS disk.
5.  **Networking:** Accept the defaults or configure according to your network policies.
6.  **Management:** Accept the defaults.
7.  **Review + create:** Review the settings and click "Create".

### Using Azure CLI

```bash
az vm create \
  --resource-group <YourResourceGroup> \
  --name github-runner-vm \
  --image Ubuntu2204 \
  --size Standard_D4s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys
```

## 3. Software Installation

Connect to your VM using SSH:

```bash
ssh azureuser@<YourVMPublicIP>
```

Run the setup script from the repository:

```bash
./scripts/infrastructure/setup_azure_runner.sh
```

This script will:

1.  Update the package list.
2.  Install `make`.
3.  Install Docker and the Docker CLI.
4.  Add the current user to the `docker` group.
5.  Install Python 3.11.

## 4. GitHub Runner Setup

1.  Navigate to your GitHub repository's **Settings > Actions > Runners**.
2.  Click "New self-hosted runner".
3.  Follow the on-screen instructions to download, configure, and run the runner.

## 5. Security Hardening

- **Network Security Group (NSG):** Restrict inbound traffic to only allow SSH from trusted IP addresses.
- **System Updates:** Regularly update the OS and installed packages.
- **User Access:** Use the principle of least privilege. Do not run the runner as a user with `sudo` privileges without a password.
- **Firewall:** Configure `ufw` (Uncomplicated Firewall) to restrict outbound traffic to only what is necessary for the runner to function.

## 6. Cost Analysis

The cost of this setup primarily depends on the VM uptime.

-   **VM:** The `Standard_D4s_v3` instance type has an estimated monthly cost. Refer to the Azure Pricing Calculator for the most up-to-date pricing in your region.
-   **Disk:** The cost of the OS disk (Standard SSD) is minimal.
-   **Data Transfer:** Outbound data transfer may incur additional charges.

To reduce costs, consider using Azure Spot Virtual Machines for non-critical workflows or implementing a schedule to automatically start and stop the VM when it's needed.
