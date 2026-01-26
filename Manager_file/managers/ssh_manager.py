# managers/ssh_manager.py
import os
import subprocess
import time

from .utils import (
    THEME, clear, pause,
    ping_host, ssh_key_works,
    get_ssh_cfg, update_ssh_cfg,
    log_session, ensure_ssh_dir, ensure_ssh_key, PRIV_KEY, PUB_KEY, SSH_CONFIG_FILE,
    validate_port, validate_hostname, sanitize_path, set_secure_permissions
) #SSH_DIR check_tcp_port,

# ---------------------------------------------------------------------
# SSH – Host Management
# ---------------------------------------------------------------------
def ssh_add_connection():
    clear()
    print(THEME["warn"] + "\n➕ Neue SSH-Verbindung speichern:\n")

    name = input(THEME["info"] + "Name (Alias): ").strip()
    user = input(THEME["info"] + "Benutzername: ").strip()
    host = input(THEME["info"] + "Host/IP: ").strip()
    port = input(THEME["info"] + "Port (default 22): ").strip() or "22"
    tags_raw = input(THEME["info"] + "Tags (z.B. proxmox,lab): ").strip()
    favorite_raw = input(THEME["info"] + "Favorit? (j/N): ").strip().lower()

    # Validate inputs
    if not validate_hostname(host):
        print(THEME["err"] + "❌ Ungültiger Hostname/IP.")
        pause()
        return
    
    if not validate_port(port):
        print(THEME["err"] + "❌ Ungültiger Port (muss zwischen 1-65535 sein).")
        pause()
        return

    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
    favorite = favorite_raw == "j"

    cfg, ssh_cfg = get_ssh_cfg()
    ssh_cfg[name] = {
        "user": user,
        "host": host,
        "port": port,
        "tags": tags,
        "favorite": favorite
    }
    update_ssh_cfg(ssh_cfg)
    print(THEME["ok"] + f"\n✔ SSH-Verbindung '{name}' gespeichert.\n")
    pause()


def ssh_edit_tags_and_favorite():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Nummer zum Bearbeiten: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültige Auswahl.")
        pause()
        return
    name = names[int(choice) - 1]
    entry = ssh_cfg[name]

    print(THEME["warn"] + f"\nBearbeite SSH: {name}")
    print(THEME["info"] + f"Aktuelle Tags: {', '.join(entry.get('tags', [])) or '-'}")
    tags_raw = input("Neue Tags (leer = unverändert): ").strip()
    if tags_raw:
        entry["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]

    fav = entry.get("favorite", False)
    print(THEME["info"] + f"Aktueller Favorit-Status: {'JA' if fav else 'NEIN'}")
    fav_raw = input("Favorit umschalten? (j = toggle, Enter = nein): ").strip().lower()
    if fav_raw == "j":
        entry["favorite"] = not fav

    ssh_cfg[name] = entry
    update_ssh_cfg(ssh_cfg)
    print(THEME["ok"] + "\n✔ Aktualisiert.\n")
    pause()


def ssh_delete_connection():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Nummer löschen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Falsche Nummer.")
        pause()
        return

    name = names[int(choice) - 1]
    del ssh_cfg[name]
    update_ssh_cfg(ssh_cfg)
    print(THEME["err"] + f"\n🗑 SSH '{name}' gelöscht.\n")
    pause()


# ---------------------------------------------------------------------
# SSH – Listing / Suche
# ---------------------------------------------------------------------
def ssh_list_connections(show_header=True, filter_text=None, tag=None, with_status=True):
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen.")
        return []

    items = list(ssh_cfg.items())

    if filter_text:
        ft = filter_text.lower()
        items = [
            (n, e) for n, e in items
            if ft in n.lower()
            or ft in e["host"].lower()
            or any(ft in t.lower() for t in e.get("tags", []))
        ]

    if tag:
        t = tag.lower()
        items = [
            (n, e) for n, e in items
            if any(t == x.lower() for x in e.get("tags", []))
        ]

    items.sort(key=lambda x: (not x[1].get("favorite", False), x[0].lower()))

    if not items:
        print(THEME["err"] + "❌ Keine passenden SSH-Verbindungen gefunden.")
        return []

    if show_header:
        print(THEME["ssh"] + "\n🐧 SSH-Verbindungen:\n")

    names = []
    for idx, (name, entry) in enumerate(items, start=1):
        names.append(name)
        host = entry["host"]
        port = entry.get("port", "22")
        user = entry["user"]
        tags = ",".join(entry.get("tags", [])) or "-"
        fav = "★" if entry.get("favorite", False) else " "

        base_color = THEME["ssh"]
        tags_lower = [t.lower() for t in entry.get("tags", [])]
        if "proxmox" in tags_lower:
            base_color = THEME["subtitle"]
        elif "docker" in tags_lower:
            base_color = THEME["tag"]
        elif "router" in tags_lower:
            base_color = THEME["warn"]
        elif "test" in tags_lower:
            base_color = THEME["dim"]

        status_str = ""
        if with_status:
            online = ping_host(host)
            key_ok = ssh_key_works(entry)
            s_ping = THEME["ok"] + "● ONLINE" if online else THEME["err"] + "● OFFLINE"
            s_key = THEME["ok"] + "🔑 OK" if key_ok else THEME["err"] + "🔑 FEHLT"
            status_str = f" {s_ping}  {s_key}"

        print(
            f"{idx:2d}. "
            + base_color + f"{name:<20}"
            + os.linesep.join([]),
        )
        print(
            "   "
            + f"{user}@{host}:{port:<5} "
            + THEME["tag"] + f"[{tags}] "
            + THEME["fav"] + fav
            + status_str
        )
    print()
    return names


def ssh_search_menu():
    clear()
    print(THEME["warn"] + "\n🔍 SSH Suche/Filter\n")
    text = input(THEME["info"] + "Suchtext (Name/Host/Tag, leer = alle): ").strip()
    tag = input(THEME["info"] + "Nur Tag (z.B. proxmox, leer = egal): ").strip()
    ssh_list_connections(filter_text=text or None, tag=tag or None)
    pause()


# ---------------------------------------------------------------------
# SSH – Key Setup
# ---------------------------------------------------------------------
def ssh_setup_ssh_key():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Nummer für Key-Setup wählen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültige Auswahl.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = ssh_cfg[name]

    ensure_ssh_dir()
    if not ensure_ssh_key():
        pause()
        return

    user = entry["user"]
    host = entry["host"]
    port = entry.get("port", "22")

    print(THEME["info"] + f"\n➡ Installiere Public-Key auf {user}@{host} ...\n")

    # Use ssh-copy-id if available, otherwise fallback to manual method
    # ssh-copy-id is the standard, secure way to install SSH keys
    try:
        cmd = [
            "ssh-copy-id",
            "-i", PUB_KEY,
            "-p", port,
            f"{user}@{host}"
        ]
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print(THEME["ok"] + "\n✔ Passwortfreier Login sollte jetzt funktionieren.\n")
        else:
            print(THEME["err"] + "\n❌ Fehler beim Key-Setup.\n")
    except FileNotFoundError:
        # Fallback if ssh-copy-id is not available
        print(THEME["warn"] + "ssh-copy-id nicht gefunden, verwende manuelle Methode...\n")
        
        # Read the public key content
        try:
            with open(PUB_KEY, 'r') as f:
                pub_key_content = f.read().strip()
        except Exception as e:
            print(THEME["err"] + f"❌ Fehler beim Lesen des Public Keys: {e}")
            pause()
            return

        # Create a static script to safely handle the key installation
        # This script is hardcoded with no user input - it reads the key from stdin
        # This completely avoids command injection through the key content
        # The script:
        # 1. Sets secure umask
        # 2. Creates .ssh directory with proper permissions
        # 3. Creates authorized_keys with proper permissions  
        # 4. Reads key from stdin (via 'read key') and appends to authorized_keys
        install_script = (
            "umask 077 && "
            "mkdir -p ~/.ssh && "
            "touch ~/.ssh/authorized_keys && "
            "chmod 700 ~/.ssh && "
            "chmod 600 ~/.ssh/authorized_keys && "
            'read key && echo "$key" >> ~/.ssh/authorized_keys'
        )
        
        cmd = [
            "ssh",
            "-p", port,
            f"{user}@{host}",
            install_script
        ]
        
        # Pass the key through stdin to avoid shell injection
        result = subprocess.run(cmd, input=pub_key_content, text=True)
        
        if result.returncode == 0:
            print(THEME["ok"] + "\n✔ Passwortfreier Login sollte jetzt funktionieren.\n")
        else:
            print(THEME["err"] + "\n❌ Fehler beim Key-Setup.\n")
    
    pause()


# ---------------------------------------------------------------------
# SSH – Connect & Info
# ---------------------------------------------------------------------
def ssh_connect():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Nummer auswählen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültige Auswahl.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = ssh_cfg[name]

    user = entry["user"]
    host = entry["host"]
    port = entry.get("port", "22")

    log_session(name, "SSH_CONNECT")

    print(THEME["ok"] + f"\n🔌 SSH zu {name} ({user}@{host}:{port})\n")
    subprocess.call(["ssh", "-p", str(port), f"{user}@{host}"])
    pause()


def ssh_show_host_info():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Nummer für Host-Info wählen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültig.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = ssh_cfg[name]
    user = entry["user"]
    host = entry["host"]
    port = entry.get("port", "22")

    print(THEME["warn"] + f"\nℹ SSH Host-Info für {name} ({user}@{host})\n")

    cmd = [
        "ssh",
        "-p", str(port),
        f"{user}@{host}",
        "echo 'HOST:' $(hostname); "
        "echo 'OS:' $(uname -a); "
        "echo 'UPTIME:' $(uptime -p || uptime); "
        "echo 'LOAD:' $(uptime); "
        "echo 'DISK:'; df -h / | tail -n +2"
    ]
    subprocess.call(cmd)
    print()
    pause()


# ---------------------------------------------------------------------
# SSH – Datei-Transfer & Sync
# ---------------------------------------------------------------------
def ssh_file_transfer_menu():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Nummer wählen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültig.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = ssh_cfg[name]
    user = entry["user"]
    host = entry["host"]
    port = entry.get("port", "22")

    while True:
        clear()
        print(THEME["warn"] + f"\n📁 SSH Datei-Transfer für {name}\n")
        print(THEME["info"] + """
1. Datei hochladen (Upload)
2. Datei herunterladen (Download)
3. Ordner synchronisieren (rekursiv, SCP)
0. Zurück
""")
        opt = input("Auswahl: ").strip()

        if opt == "1":
            local = input("Lokale Datei: ").strip()
            remote = input("Remote Pfad: ").strip()
            
            # Validate local path
            local_safe = sanitize_path(local)
            if not local_safe or not os.path.exists(local_safe):
                print(THEME["err"] + "❌ Ungültiger oder nicht existierender lokaler Pfad.")
                pause()
                continue
            
            cmd = ["scp", "-P", str(port), local_safe, f"{user}@{host}:{remote}"]
            print(THEME["ok"] + "\n→ Upload läuft...\n")
            subprocess.call(cmd)
            pause()

        elif opt == "2":
            remote = input("Remote Datei: ").strip()
            local = input("Lokaler Pfad: ").strip()
            
            # Validate local path
            local_safe = sanitize_path(local)
            if not local_safe:
                print(THEME["err"] + "❌ Ungültiger lokaler Pfad.")
                pause()
                continue
            
            # Check if parent directory exists and is writable
            parent_dir = os.path.dirname(local_safe)
            # Handle case where file is in current directory (parent_dir is empty)
            if not parent_dir:
                parent_dir = os.getcwd()
            
            if not os.path.exists(parent_dir):
                print(THEME["err"] + "❌ Übergeordnetes Verzeichnis existiert nicht.")
                pause()
                continue
            
            if not os.access(parent_dir, os.W_OK):
                print(THEME["err"] + "❌ Keine Schreibrechte für das Zielverzeichnis.")
                pause()
                continue
            
            cmd = ["scp", "-P", str(port), f"{user}@{host}:{remote}", local_safe]
            print(THEME["ok"] + "\n→ Download läuft...\n")
            subprocess.call(cmd)
            pause()

        elif opt == "3":
            local = input("Lokaler Ordner: ").strip()
            remote = input("Remote Ordner: ").strip()
            
            # Validate local path
            local_safe = sanitize_path(local)
            if not local_safe or not os.path.exists(local_safe):
                print(THEME["err"] + "❌ Ungültiger oder nicht existierender lokaler Pfad.")
                pause()
                continue
            
            cmd = ["scp", "-r", "-P", str(port), local_safe, f"{user}@{host}:{remote}"]
            print(THEME["ok"] + "\n→ Ordner-Sync (SCP -r) läuft...\n")
            subprocess.call(cmd)
            pause()

        elif opt == "0":
            break
        else:
            print(THEME["err"] + "❌ Ungültig.")
            pause()


# ---------------------------------------------------------------------
# SSH – Port Forwarding
# ---------------------------------------------------------------------
def ssh_port_forward_menu():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Nummer für Port-Forward wählen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültig.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = ssh_cfg[name]
    user = entry["user"]
    host = entry["host"]
    port = entry.get("port", "22")

    clear()
    print(THEME["warn"] + f"\n🔀 SSH Port-Forward für {name}\n")
    lport = input("Lokaler Port (z.B. 8080): ").strip()
    rhost = input("Remote Host (default localhost): ").strip() or "localhost"
    rport = input("Remote Port (z.B. 80): ").strip()

    if not lport.isdigit() or not rport.isdigit():
        print(THEME["err"] + "❌ Ungültige Ports.")
        pause()
        return

    print(THEME["ok"] + f"\n→ Tunnel: localhost:{lport} → {rhost}:{rport} auf {user}@{host}")
    print(THEME["warn"] + "Beenden mit STRG+C.\n")

    cmd = [
        "ssh",
        "-L", f"{lport}:{rhost}:{rport}",
        "-p", str(port),
        f"{user}@{host}"
    ]
    subprocess.call(cmd)
    pause()


# ---------------------------------------------------------------------
# SSH – Live-Ping & Health-Check
# ---------------------------------------------------------------------
def ssh_live_ping_monitor():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = list(ssh_cfg.keys())

    print(THEME["warn"] + "\n📡 SSH Live-Ping Monitor – STRG+C zum Beenden\n")
    try:
        while True:
            clear()
            print(THEME["warn"] + "📡 SSH Live-Ping Monitor (CTRL+C zum Beenden)\n")
            for name in names:
                entry = ssh_cfg[name]
                host = entry["host"]
                start = time.time()
                online = ping_host(host, count=1, timeout=1.5)
                duration = (time.time() - start) * 1000
                if online:
                    print(THEME["ok"] + f"{name:<20} {host:<15} {duration:5.1f} ms")
                else:
                    print(THEME["err"] + f"{name:<20} {host:<15}  TIMEOUT")
            time.sleep(1.5)
    except KeyboardInterrupt:
        print()
        pause()


def ssh_all_servers_health_check():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    clear()
    print(THEME["warn"] + "\n🩺 SSH Health-Check aller Server\n")

    for name, entry in ssh_cfg.items():
        user = entry["user"]
        host = entry["host"]
        port = entry.get("port", "22")

        print(THEME["info"] + f"\n=== {name} ({user}@{host}:{port}) ===")
        online = ping_host(host)
        if not online:
            print(THEME["err"] + "HOST OFFLINE (Ping fehlgeschlagen)")
            continue

        cmd = [
            "ssh", "-p", str(port), f"{user}@{host}",
            "echo 'UPTIME:' $(uptime -p || uptime); "
            "echo 'LOAD:' $(uptime); "
            "echo 'MEM:' $(free -h 2>/dev/null | grep Mem || echo 'n/a'); "
            "echo 'DISK:'; df -h / | tail -n +2"
        ]
        subprocess.call(cmd)
    print()
    pause()


# ---------------------------------------------------------------------
# SSH – Config Generator
# ---------------------------------------------------------------------
def ssh_generate_ssh_config():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    ensure_ssh_dir()
    lines = []
    lines.append("# Generated by ssh_manager\n")
    for name, entry in ssh_cfg.items():
        user = entry["user"]
        host = entry["host"]
        port = entry.get("port", "22")
        lines.append(f"Host {name}")
        lines.append(f"    HostName {host}")
        lines.append(f"    User {user}")
        lines.append(f"    Port {port}")
        lines.append(f"    IdentityFile {PRIV_KEY}")
        lines.append("")
    with open(SSH_CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    # Set secure permissions on SSH config file
    set_secure_permissions(SSH_CONFIG_FILE, is_private=True)

    print(THEME["ok"] + f"\n✔ SSH Config geschrieben nach: {SSH_CONFIG_FILE}\n")
    pause()


# ---------------------------------------------------------------------
# SSH – Remote Commands & Mini-Top
# ---------------------------------------------------------------------
def ssh_remote_commands_menu():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen gespeichert.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Nummer für Remote-Command wählen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültig.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = ssh_cfg[name]
    user = entry["user"]
    host = entry["host"]
    port = entry.get("port", "22")

    while True:
        clear()
        print(THEME["warn"] + f"\n🛠 SSH Remote-Befehle für {name}\n")
        print(THEME["info"] + """
1. Neustart (reboot)
2. Docker-Container (docker ps)
3. Systemd Services (systemctl --failed)
4. Speicherplatz (df -h)
5. Dmesg (letzte 20 Zeilen)
6. „Hardening“-Info (nur Befehle anzeigen, nicht ausführen)
0. Zurück
""")
        opt = input("Auswahl: ").strip()

        if opt == "0":
            break

        if opt == "6":
            print(THEME["warn"] + "\nBeispiel-Hardening-Befehle (NICHT automatisch ausgeführt):\n")
            print("""\
- SSH Root Login deaktivieren:
    sudo sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    sudo systemctl restart sshd

- Passwort-Auth deaktivieren (nur mit Keys!):
    sudo sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    sudo systemctl restart sshd

- Fail2Ban installieren:
    sudo apt install fail2ban
""")
            pause()
            continue

        cmd_map = {
            "1": "sudo reboot",
            "2": "docker ps || echo 'docker nicht installiert'",
            "3": "systemctl --failed || echo 'systemd Info nicht verfügbar'",
            "4": "df -h",
            "5": "dmesg | tail -n 20"
        }
        cmd = cmd_map.get(opt)
        if not cmd:
            print(THEME["err"] + "❌ Ungültig.")
            pause()
            continue

        full = ["ssh", "-p", str(port), f"{user}@{host}", cmd]
        subprocess.call(full)
        pause()


def ssh_mini_top_monitor():
    cfg, ssh_cfg = get_ssh_cfg()
    if not ssh_cfg:
        print(THEME["err"] + "❌ Keine SSH-Verbindungen für Mini-Top.")
        pause()
        return

    names = ssh_list_connections(show_header=True, with_status=False)
    choice = input("Host für Mini-Top wählen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültig.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = ssh_cfg[name]
    user = entry["user"]
    host = entry["host"]
    port = entry.get("port", "22")

    print(THEME["warn"] + f"\nMini-Top für {name} – STRG+C zum Beenden\n")
    try:
        while True:
            clear()
            print(THEME["warn"] + f"Mini-Top: {name} ({user}@{host})\n")
            cmd = [
                "ssh", "-p", str(port), f"{user}@{host}",
                "top -b -n1 | head -n 10 || (ps aux --sort=-%mem | head -n 10)"
            ]
            subprocess.call(cmd)
            time.sleep(3)
    except KeyboardInterrupt:
        print()
        pause()
