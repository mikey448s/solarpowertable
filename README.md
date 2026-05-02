# solarpowertable.com



# 1 Brief Description

## 1.1 Objective


## 1.2 Computer Engineering


## 1.2 Mechanical Engineering



# 2 Detailed Installation Steps


## 2.1 Computer Engineering

### 2.1.1 Home Assistant (Necessary)
> The local telemetry hub is hosted on a Raspberry Pi 4B running the dedicated Home Assistant OS appliance. Initial configuration requires a direct hardware interface. Process may look different due to strict AP isolation on the campus network if you cannot initialize on a home network.

Home Assistant is not an app. It is a full operating system that specializes in interfacing with smart devices. It faces its inner-workings towards port :8123 which can be access and rendered by another machine on the same network. Accessing Home Assistant on the browser from another machine is the main strength of the software.

*Steps 1-11 **Preparing and Deploying the Home Assistant OS***
- Download the Home Assistant OS: Go to the official Home Assistant (https://www.home-assistant.io/installation/) and download the latest installer specific to your hardware. e.g. "Get Raspberry Pi".
- Download a Flashing Tool: Download and install balenaEtcher or Rufus on your current working computer.
- Flash the Drive: Insert a blank USB flash drive (at least 8GB).
	- Open balenaEtcher, select "Flash from file," and choose the Proxmox ISO.
	- Select your USB drive as the target.
	- Click Flash! and wait for the validation to complete. Flash HAOS to the RPi's microSD card.
- Boot the Pi with a physical keyboard and HDMI monitor connected.
- At the initial prompt, type login to access the HA CLI.
- To bind the Pi to the local Wi-Fi hotspot (or a WPA-PSK campus network), execute the following network manager override. Do not replace spaces or quotation marks:
	- `network update wlan0 --ipv4-method auto --ipv6-method auto --wifi-auth wpa-psk --wifi-mode infrastructure --wifi-ssid "YOUR_WIFI_NAME" --wifi-psk "YOUR_PASSWORD"`
	- Run `network info` to verify the assigned IP address.

*Steps 12-20 **Kiosk Mode & Smart Device Integration***

> HAOS does not natively support an X11 windowing system or desktop environment, meaning the HDMI port outputs a static terminal. To provide a user-facing dashboard on the table without requiring a secondary computer, we utilized a containerized kiosk workaround.

- Navigate to Settings > Add-ons > Add-on Store.
- Add the custom repository for HAOS-kiosk (Local Dashboard).
	- Install and start the add-on.
- Set the target URL to http://localhost:8123. The add-on spins up a minimal Chromium container mapped directly to the Pi's framebuffer, serving the UI directly to the HDMI touchscreen while keeping the underlying OS completely locked down.
- Connect the Sonoff Zigbee 3.0 USB Dongle via a USB 2.0 extension cable to mitigate electromagnetic interference from the Pi's USB 3.0 bus. I also found you cannot keep it near a Wireless Wi-Fi router.
- Enable the ZHA (Zigbee Home Automation) integration and pair the four Eightree ET12 smart plugs and the custom FSR-modified contact sensor.
	- For now, the devices will sit in the area you choose, and further customization will be required.

*Steps 21-31 **Power-Saving Automations & SOC Inference Model***

> We introduced a feature to disconnect the 7-inch LCD touchscreen from power using a Smart Plug and Home Assistant Automation. The Raspberry Pi consumes about 3.5W at idle, and the screen consumes about 3W. By correlating the usage status and screen status, we can halve our power footprint when not in use.

- Determine your 'usage' factor. Ours is the Zigbee 3.0 Contact Sensor embedded inside the 3" cushion (detailed in 2.2.2 Other Schematics). This can be an FSR (force sensor) or camera (computer vision).
	- Use the GUI or custom YAML code to define the action and reaction. Our custom YAML block is located here **[screen_on.yaml](https://github.com/mikey448s/solarpowertable/blob/main/screen_on.yaml) | [screen_saver.yaml](https://github.com/mikey448s/solarpowertable/blob/main/screen_saver.yaml)**.

> We developed a preliminary prototype for inferring the State of Charge of the Lead-Acid battery installed to the Solar-Powered Study Table. Because the table's inverter converts the DC signal to a constant 120V AC, we cannot monitor the upstream DC voltage of the battery to determine the State of Charge.

- To infer SOC, our team provides a blueprint for inferring charge using Home Assistant Automations.
- Drain Test: establish the baseline capacity of the battery by charging close to 100%.
	- Reset or note the energy consumption totals of the smart plugs at this state.
	- Apply a heavy load to the plugs until the battery is depleted and the inverter shuts off.
	- The new total consumption represents the maximum usable capacity of the battery (we expect approximately 800Wh based on Sunbolt documentation).
- Implement an automation that resets the daily total energy consumed variable at sunset, assuming that the SOC is at its maximum after generating solar power all day.
	- Use the GUI or custom YAML code to define the action and reaction. Our custom YAML block is located here **[configurations.yaml](https://github.com/mikey448s/solarpowertable/blob/main/configurations.yaml) | [battery_soc_alerts.yaml](https://github.com/mikey448s/solarpowertable/blob/main/battery_soc_alerts.yaml)**.
- Implement another automation using YAML to provide notifications at critical charge states (100%, 50%, 20%).

### 2.1.2 Remote Server (Optional)

> This part of the process may look very different depending on existing IoT and webapp infrastructure. This guide will detail all steps true to the FY26 Solar-Powered Study Table's process, and many of the steps below will likely need to be remediated if the existing infrastructure already exists.


#### 2.1.2 (A) Proxmox Server

> For the FY26 Solar-Powered Study Table team, converting an old laptop as a server will help extend the reach of the dashboard's telemetry. Users will not have to be physically at the table to learn, and the computer engineers have a chance to show software development and IoT competence.

Configuring the server was a necessary precursor to 2.1.2 (B) Flask Web App and 2.1.2 (C) Tailscale Mesh VPN. Setting up the server properly will allow connections and interactions with the website from anywhere in the world.
Proxmox is not an app. It is a full operating system that replaces Windows/macOS on the laptop to manage virtual machines with maximum efficiency. It handles the QEMU under the hood to manage multiple Virtual Machines & Containers, which we will take advantage of for the Web App & Mesh VPN.

*Steps 1-19 **Preparing and Installing the Bare Metal Hypervisor (Proxmox VE)***

> Before modifying the laptop, you must create a bootable disk for installation.

- Download the Proxmox VE ISO: Go to the official Proxmox website (proxmox.com) and download the latest "Proxmox VE ISO Installer."
- Download a Flashing Tool: Download and install balenaEtcher or Rufus on your current working computer.
- Flash the Drive: Insert a blank USB flash drive (at least 8GB).
	- Open balenaEtcher, select "Flash from file," and choose the Proxmox ISO.
	- Select your USB drive as the target.
	- Click Flash! and wait for the validation to complete.
- Boot the Server Laptop: Plug the USB drive into the old laptop.
	- Turn the laptop on and immediately tap the Boot Menu key (usually F12, F2, or Del depending on the manufacturer).
	- Select the USB drive from the boot options to launch the Proxmox installer.
- Start the Installer: At the Proxmox boot screen, select Install Proxmox VE and press Enter. EULA: Read and click I Agree to the End User License Agreement.
- Target Hard Disk: Select the laptop's internal hard drive from the dropdown. **This step will completely permanently erase all existing data.**
- Administrator Credentials: Type a strong password for the root (superadmin) account. Write this down; there is no password recovery.
- Management Network Configuration: This is critical. Proxmox needs a static **wired** address so you can always find it on your home network.
	- Management Interface: Select the laptop's Ethernet port or Wi-Fi card (Ethernet is highly recommended for servers).
	- Hostname: Name the server (e.g., solar-proxmox.local).
	- IP Address: Assign a static IP outside of your home router's normal DHCP range (e.g., 192.168.1.200).
	- Gateway & DNS: Usually your home router's IP (e.g., 192.168.1.1). Likely largely different for existing infrastructure (IT question).
- Install: Review the summary screen and click Install.
- Reboot: Once the installation hits 100%, remove the USB drive and click Reboot. The laptop screen will eventually just show a black terminal with a login prompt. Your work on the physical laptop is now done.

*Steps 20-49 **Initializing Proxmox for Virtualization***

> You will now control the server entirely from your main computer's web browser. Changes made from the command-line interface should only be done by those who know exactly what they're doing, in my experience.

- Access the Dashboard: On your main computer (connected to the same home network), open a web browser and type: https://[host IP]:8006 (use the IP you assigned in the setup). e.g. https://192.168.1.200:8006.
- Bypass the Security Warning: Your browser will warn you that the connection is not private. This is normal for local servers. Click Advanced and then Proceed to 192.168.1.200 (unsafe).
- Login: Enter Username: root and the password you created. Keep the Realm as Linux PAM.
- Subscription Prompt: You will see a popup saying "You do not have a valid subscription." Proxmox is free; this just means you don't have paid enterprise support. Click OK to dismiss it.

> I will cover the steps for provisioning resources to our VM and Container here, since these steps are specific to Proxmox VE. You will need to specify the exact CPU, RAM, and Storage that the virtual computers will have access to. The steps specific to the VM and Container themselves are found in 2.1.2 (B) and 2.1.2 (C).

- Download the Ubuntu Server LTS ISO from Ubuntu.com to your main computer.
	- In Proxmox, expand your node (e.g., solar-proxmox) on the left sidebar.
	- Click on local (solar-proxmox).
	- Click ISO Images > Upload > Select the Ubuntu ISO > Click Upload.
- Create the Virtual Machine: Click the blue Create VM button in the top right corner.
- General Tab: Name the VM Ubuntu-Flask-VPN. Click Next.
- OS Tab: Select the Ubuntu ISO you just uploaded. Click Next.
- System Tab: Check the box for QEMU Guest Agent (This allows Proxmox to accurately read the VM's RAM usage). Click Next.
- Dsks Tab: Disk Size: 32 GB is plenty for Ubuntu Server and a Flask app. Leave everything else default. Click Next.
- CU Tab: Cores: If the laptop is a low-end dual-core, assign 1-2 cores. If it is a high-end i7/Ryzen, assign 4 cores. Click Next.
- Memory Tab: Low-end laptop: 1500-2500 MB (~2GB). High-end laptop: 4000-8000 MB (~6GB). Memory sizes do not need to be of 2^n increments, as QEMU handles it under the hood from the GUI. Click Next.
- Network Tab: Leave defaults (VirtIO model). Click Next.
-- Cnfirm: Click Finish. You will see the new VM appear in the left sidebar.

> An LXC container shares the host server's (Proxmox) existing Linux kernel, isolating the application in a lightweight sandbox. This drops the idle RAM consumption from ~2048MB to roughly ~128MB and eliminates CPU scheduling conflicts, leaving maximum compute power for our Flask web server VM.

- In the Proxmox UI, navigate to local (solar-proxmox) > CT Templates.
- Click Templates, search for ubuntu-22.04-standard, and click Download.
- Click Create CT (top right).
	- General: Name it Tailscale-Node. Ensure Unprivileged container is checked (crucial for security).
	- Template: Select the downloaded Ubuntu 22.04 template.
	- Disks: Assign 8GB (vastly smaller than a VM requirement).
	- CPU/Memory: Assign 1 Core and 512MB RAM.
	- Network: Set IPv4 to DHCP. Click Finish.
- Enable TUN/TAP for VPN Routing: Critical Step: Tailscale requires access to network tunnel interfaces to route traffic.
	- In the Proxmox shell for the host node, edit the container's configuration file: `nano /etc/pve/lxc/<Container_ID>.conf`
	- Append this line to allow the unprivileged container to use the `/dev/net/tun` device: `lxc.cgroup2.devices.allow: c 10:200 rwm`


#### 2.1.2 (B) Flask Web App
*Steps 1-19 **Initializing the Web App VM***

> Installing the operating system inside the newly created virtual container.

- Start the VM: Right-click Ubuntu-Flask-VPN in the sidebar and select Start. Open the Screen: Click Console in the top right corner. You are now looking at the VM's monitor.
- Follow the Ubuntu Setup Wizard with your preferred settings. Only the following require extra attention:
	- Ubuntu Server (minimized) is recommended for efficiency, but standard Ubuntu Server is fine.
	- Network: Leave it as DHCP. (Tailscale will handle our permanent IP later).
	- Storage: Select Use an entire disk. Press down to Done and confirm the destructive action (it is only formatting the 32GB virtual disk, not the laptop).
	- Decide your own server name and username as preferred.
	- SSH Setup: Check the box to Install OpenSSH server. This is critical for connecting to the server remotely later.
- Install & Reboot: Wait for the installation to finish (it will download security updates). When prompted, select Reboot Now.
	- If it says "Please remove the installation medium," just press Enter. This is because it is virtualized boot media.

> To run the web dashboard, the Ubuntu server needs a dedicated, isolated Python environment. This prevents our project libraries from conflicting with the underlying operating system's critical functions.

- Open the Proxmox console for your Ubuntu VM.
- Run the following command to download Python and the virtual environment manager: `sudo apt install python3 python3-pip python3-venv -y`
- Create a folder to hold your code and navigate into it: `mkdir ~/solarpower-app && cd ~/solarpower-app`
- Run the command to create an isolated sandbox named solar-venv: `python3 -m venv solar-venv`
- Before installing anything, you must "step inside" (activate) the sandbox. `source solar-venv/bin/activate`
	- You will know it worked because your command line prompt will now start with (solar-venv).
- With the environment active, install the required web framework and HTTP request libraries: `pip install Flask requests`
- Using the code available on this Github page developed by our team, place the **[app.py](https://github.com/mikey448s/solarpowertable/blob/main/app.py), [index.html](https://github.com/mikey448s/solarpowertable/blob/main/index.html), and [ha_cache.json](https://github.com/mikey448s/solarpowertable/blob/main/ha_cache.json)** files into this `~/solarpower-app` folder.

*Steps 20-40 **Enabling & Initializing Cloudflare Zero Trust Tunneling for External Access***

> Standard web hosting requires opening router ports (Port Forwarding), which is a massive security risk and explicitly blocked by the university network. To safely expose the local localhost:3333 dashboard to a public domain, we deployed a reverse tunnel using Cloudflare.

- Prerequisites: You must own a domain name (e.g. solarpower.com) and have its DNS managed by Cloudflare (a free service). Justin Ellis of the Office of Sustainability mentioned the sustainability website is no longer managed on-prem, so this process may look very different.
- Fetch the cloudflare daemon installation package (cloudflared) directly to the Ubuntu server: `wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb`
	- Run the Debian package manager: `sudo dpkg -i cloudflared-linux-amd64.deb`
- Run the login command: `cloudflared tunnel login`
	- The terminal will output a URL. Copy it, open it on your laptop's browser, log into your Cloudflare account, and select your domain to authorize the tunnel.
- Run the command to generate the secure tunnel (we will name it solarpower): `cloudflared tunnel create solarpower`
	- Note: This will output a unique Tunnel ID (a long string of letters and numbers). Save this.
- Route the domain: Tell Cloudflare what URL people should type in to access this tunnel: `cloudflared tunnel route dns solarpower solarpowertable.com`
- We need to tell the tunnel where to look locally when internet traffic arrives. Create a config file: `nano ~/.cloudflared/config.yml`
	- Paste the following routing logic (replace `<Tunnel-ID>` with your actual ID):
	- ```tunnel: <Tunnel-ID>
	credentials-file: /home/solaradmin/.cloudflared/<Tunnel-ID>.json

	ingress:
	- hostname: dashboard.yourdomain.com
	service: http://localhost:3333
	- service: http_status:404```
	- Save and exit the text editor (Ctrl+O, Enter, Ctrl+X).

> To prevent the need for manual developer intervention every time the server restarts, we consolidated the startup sequence into a single bash executable.

- Ensure you are in your home directory: `cd ~`. Open a new file: `nano reboot_sequence.sh`
- Paste this code snippet to launch the cloudflared tunnel and the Flask app in one fell swoop:
	- ```#!/bin/bash

	# 1. Activate the isolated Python environment
	source /home/solaradmin/solarpower-app/solar-venv/bin/activate

	# 2. Launch the Cloudflare secure tunnel in the background (&)
	cloudflared tunnel run solarpower &

	# 3. Launch the Flask web server
	python /home/solaradmin/solarpower-app/app.py```
- By default, Linux text files cannot be run as programs. We must grant execution permissions: `chmod +x reboot_sequence.sh`

> To truly make it "just work," we can tell the server to run this script automatically whenever it powers on.

- Open the crontab editor: `crontab -e`
	- Add this line to the very bottom of the file: `@reboot /home/solaradmin/reboot_sequence.sh > /home/solaradmin/startup.log 2>&1`
	- Now, if the old laptop loses power and boots back up, your website and public tunnel will automatically restore themselves without you ever having to log in.


#### 2.1.2 (C) Tailscale Mesh VPN
> Allows your team to connect to the Home Assistant Dashboard and the Remote Server anywhere in the world with higher performance than Hub-and-Spoke or ZTNA.

*Steps 1-5 **Installation and Authentication***
- Install & Authenticate Tailscale: Start the LXC and open the console.
	- Update repositories: `apt update && apt upgrade -y`
- Run the installer: `curl -fsSL https://tailscale.com/install.sh | sh`
- Bring the node online: `tailscale up`
- Copy the provided URL, log in via a browser, and authenticate the node to the mesh network.
	- All devices you wish to connect to the mesh network with (computers, phones) must install the Tailscale VPN and be approved by the admin account.


## 2.2 Mechanical Engineering

### 2.2.1 CAD Files

### 2.2.2 Other Schematics