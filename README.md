Disclaimer of Liability

The provided software is distributed on an “as is” basis, without warranties of any kind, either express or implied.
No guarantee is made regarding functionality, accuracy, security, reliability, or fitness for a particular purpose.

The author/developer shall not be held liable for any direct or indirect damages, including but not limited to:

loss of data

system malfunctions

hardware or software damage

security breaches

service interruptions

financial loss

damages resulting from improper use or misconfiguration

The user is solely responsible for:

proper configuration

maintaining backups and security measures

ensuring legal compliance

adhering to internal company policies

using the tool only on systems they are authorized to access

By using this software, the user acknowledges and accepts this disclaimer and all associated terms.



🗝 SSH & RDP Manager PRO
Central Terminal-Based Manager for SSH & RDP Connections (Windows)

SSH & RDP Manager PRO is a powerful interactive console tool for managing SSH and RDP hosts, automating connections, transferring files, running remote commands, monitoring system health, sending Wake-on-LAN packets, generating SSH configs, and more.

Everything is handled through a modern menu interface with colored output and persistent JSON configuration.

📌 Features
🟦 SSH Management

Add, edit, delete SSH hosts

Tags & favorites

Full-text search (name/host/tags)

Online status: ping + SSH-key authentication check

Automatic Ed25519 SSH key creation

Automatic authorized_keys installation

SCP-based:

File upload

File download

Directory sync (recursive)

SSH Port Forwarding (ssh -L)

Live Ping Monitor

“Mini-Top” monitor (remote top)

Full health check (uptime, load, disk, memory)

Auto-generate ~/.ssh/config

🟩 RDP / Windows Management

Add, edit, delete RDP hosts

Tags & favorites

DNS resolution & TCP port testing

Start RDP via mstsc.exe

Windows info:

qwinsta active sessions

OS info (CIM: Caption, LastBootUpTime)

Wake-on-LAN (Magic Packet)

Auto-RDP after WOL (wait until online & port open)

PowerShell Remoting (WinRM)

SSH–RDP host matching (same IP/host)

🛠 Additional Tools

Network utilities (ARP, DNS, ping, port scanning)

Integrated session log viewer

🖥 User Interface

Large console layout

Color-coded theme (colorama)

Dashboard with recent activities

Live favorite host status bar

Clean ASCII banner

📁 Project Structure
main.py
managers/
 ├── utils.py
 ├── ssh_manager.py
 ├── rdp_manager.py
 └── network_tools.py

📂 Configuration & Log Files
Location	Description
~/.ssh_manager.json	Stores all SSH & RDP entries
~/.ssh_manager_sessions.log	History of all connections
~/.ssh/id_ed25519	Auto-generated SSH private key
~/.ssh/id_ed25519.pub	SSH public key
~/.ssh/config	Auto-generated SSH config

The JSON structure looks like:

{
    "ssh": {
        "server1": {
            "user": "root",
            "host": "10.0.0.10",
            "port": "22",
            "tags": ["lab", "proxmox"],
            "favorite": true
        }
    },
    "rdp": {
        "Client-PC": {
            "host": "10.0.0.50",
            "user": "DOMAIN\\Admin",
            "port": "3389",
            "mac": "AA:BB:CC:DD:EE:FF",
            "tags": ["windows"],
            "favorite": false
        }
    }
}

🚀 Running the Program
Start application
python main.py

Startup sequence

Console switches to large mode (Windows)

All hosts are ping + port-tested

Recent activities displayed

Status bar shows favorite server health

Main menu opens

🔧 Requirements

Windows 10/11

Python 3.9+

Installed tools:

OpenSSH client (ssh, scp)

RDP client (mstsc.exe)

PowerShell (built-in)

Python packages:

pip install colorama

🧩 Main Modules Overview
main.py

Central menu system

Dashboard + status bar

Startup health check

utils.py

Configuration loader/saver

Logging system

SSH key manager

Network checks (ping + TCP port)

UI helpers (banner, clear, pause)

ssh_manager.py

All SSH functions (connections, file transfer, monitoring)

Key installation

Port forwarding

Server health checks

SSH config generator

rdp_manager.py

All RDP functions

Wake-on-LAN logic

Windows system queries

PowerShell Remoting

Auto-matching SSH hosts

📦 Packaging (Optional)

If you want to create an executable:

pip install pyinstaller
pyinstaller --onefile --console main.py


The EXE will use all local modules automatically.

🧑‍💻 Why This Tool Is Awesome

Perfect for homelabs, sysadmins, IT departments, and developers

Extremely fast and clean workflow

One tool for SSH, RDP, WOL, monitoring, and more

Fully offline-capable

Portable — everything in a single folder

Clear JSON configuration

Easy to extend
