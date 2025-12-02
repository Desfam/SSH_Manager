🗝 SSH & RDP Manager PRO
Central terminal-based management tool for SSH & RDP connections on Windows

This project is a full-featured interactive console dashboard that lets you manage SSH and RDP connections, run remote commands, transfer files, generate SSH configs, wake Windows machines via WOL, monitor system health, and much more.

Everything runs in a clean, colored menu-driven interface with a persistent JSON configuration.

📌 Key Features
🟦 SSH Manager

Add / edit / delete SSH connections

Search & filter (by name, host, tags)

Tag & favorite system

Online-status check (ping + key check)

Automatic Ed25519 key generation

Automatic public key installation (passwordless SSH)

SCP file upload/download

Folder sync (recursive)

SSH port forwarding (local tunnels)

Live-Ping monitor (with latency)

Mini-Top monitor (top output over SSH)

Full server health check (uptime, load, memory, disk)

Auto-generate ~/.ssh/config file

🟩 RDP Manager

Add / edit / delete RDP hosts

Tag & favorite system

DNS resolution & port checks

Start RDP sessions using MSTSC

Windows info: sessions (qwinsta), OS info (CIM)

Wake-on-LAN support (Magic Packet)

Auto-start RDP after WOL once the host is online

PowerShell Remoting (WinRM)

Automatic matching of SSH & RDP entries

🛠 Admin Tools

ARP, DNS lookup, ping, port testing

Additional network utilities (via network_tools module)

🖥 UI & Dashboard

Large console layout

Colorful theme (colorama)

Last session activity panel

Live status bar showing favorite SSH & RDP host status

Clean, modern ASCII banner

📁 Project Structure
main.py
managers/
 ├── utils.py
 ├── ssh_manager.py
 ├── rdp_manager.py
 └── network_tools.py   (optional)

Configuration & Log Files

~/.ssh_manager.json → Persistent storage for SSH + RDP hosts

~/.ssh_manager_sessions.log → Connection history

SSH key files:

~/.ssh/id_ed25519

~/.ssh/id_ed25519.pub

Auto-generated SSH config:

~/.ssh/config

🚀 Technical Overview of Modules
🔧 main.py – Core entrypoint

Handles:

Drawing banner

Status bar

Recent sessions dashboard

Startup health-check

Main menu + routing to managers

📎 Source:

🧩 utils.py – Core utilities
Configuration handling

Load & save JSON config

Backward compatible structure

Backup .bak automatic creation

Session logging

Stores: timestamp, connect type, host, extra info

Dashboard shows last 5 activities

Network checks

Ping wrapper

TCP-port checks

SSH key generation / verification

Auto-create Ed25519 key

Check if key-auth works via BatchMode

UI helpers

Banner, clear, pause

Live status bar

Startup status check

📎 Source:

🐧 ssh_manager.py – SSH management
Host management

Add / edit tags / delete

Sorting by favorites

Searching and filtering

Live online-status + key-status icons

Connecting

Direct SSH using system ssh

Logs session automatically

File transfer

SCP upload

SCP download

Directory sync (recursive)

Monitoring

Live-ping monitor

Mini-top monitor (top over SSH every 3s)

Server checks

Uptime

Load

Memory

Disk usage

Others

SSH config generator

SSH key installation (authorized_keys)

Remote command menu (docker ps, systemctl, reboot, dmesg, etc.)

📎 Source:

🪟 rdp_manager.py – RDP & Windows management
Host management

Add/edit/delete RDP entries

Store MAC for WOL

Tag + favorite sorting

RDP operations

Start RDP session (mstsc)

DNS resolution and RDP port check

Logging

Windows information

Sessions via qwinsta

OS info via PowerShell CIM

Wake-on-LAN

Magic packet sending

Auto-RDP launch when:

Host responds to ping

RDP port becomes reachable

WinRM

Start a PowerShell Remoting session

SSH matching

Automatically detects if SSH host matches same IP/hostname

📎 Source:

⚙️ File Locations & Purpose
File	Purpose
~/.ssh_manager.json	Stores SSH & RDP entries
~/.ssh_manager_sessions.log	Saves history of all connections
~/.ssh/id_ed25519	Private SSH key
~/.ssh/id_ed25519.pub	Public SSH key
~/.ssh/config	Auto-generated SSH config
▶ How to Run
python main.py


On startup:

Large console mode (Windows)

Global status check (ping + ports)

Show dashboard with last sessions

Show main menu

💡 Why this tool is useful

Combines SSH + RDP + WOL + Monitoring in ONE interface

Uses clean JSON config

Works offline

Ideal for homelabs & corporate sysadmin work

Extremely fast interaction via native system tools

Easy to extend / customize

Colored UI with clear structure

Portable and Windows-friendly
