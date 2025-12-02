# managers/rdp_manager.py
import subprocess
import time

from .utils import (
    THEME, clear, pause,
    ping_host, check_tcp_port,
    get_rdp_cfg, update_rdp_cfg,
    get_ssh_cfg, log_session,
)

# ---------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------
def resolve_host(host):
    import socket
    try:
        ip = socket.gethostbyname(host)
        return ip
    except Exception:
        return None


# ---------------------------------------------------------------------
# RDP – Host Management
# ---------------------------------------------------------------------
def rdp_add_connection():
    clear()
    print(THEME["warn"] + "\n➕ Neue RDP-Verbindung speichern:\n")

    name = input(THEME["info"] + "Name (Alias): ").strip()
    host = input(THEME["info"] + "Host/IP oder DNS: ").strip()
    user = input(THEME["info"] + "Benutzername (optional, z.B. ARZW\\user): ").strip()
    port = input(THEME["info"] + "Port (default 3389): ").strip() or "3389"
    mac = input(THEME["info"] + "MAC für Wake-on-LAN (optional, AA:BB:CC:DD:EE:FF): ").strip()
    tags_raw = input(THEME["info"] + "Tags (z.B. windows,client): ").strip()
    favorite_raw = input(THEME["info"] + "Favorit? (j/N): ").strip().lower()

    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
    favorite = favorite_raw == "j"

    cfg, rdp_cfg = get_rdp_cfg()
    rdp_cfg[name] = {
        "host": host,
        "user": user,
        "port": port,
        "mac": mac,
        "tags": tags,
        "favorite": favorite
    }
    update_rdp_cfg(rdp_cfg)
    print(THEME["ok"] + f"\n✔ RDP-Verbindung '{name}' gespeichert.\n")
    pause()


def rdp_edit_tags_and_favorite():
    cfg, rdp_cfg = get_rdp_cfg()
    if not rdp_cfg:
        print(THEME["err"] + "❌ Keine RDP-Verbindungen gespeichert.")
        pause()
        return

    names = rdp_list_connections(show_header=True, with_status=False)
    choice = input("Nummer zum Bearbeiten: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültige Auswahl.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = rdp_cfg[name]

    print(THEME["warn"] + f"\nBearbeite RDP: {name}")
    print(THEME["info"] + f"Aktuelle Tags: {', '.join(entry.get('tags', [])) or '-'}")
    tags_raw = input("Neue Tags (leer = unverändert): ").strip()
    if tags_raw:
        entry["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]

    fav = entry.get("favorite", False)
    print(THEME["info"] + f"Aktueller Favorit-Status: {'JA' if fav else 'NEIN'}")
    fav_raw = input("Favorit umschalten? (j = toggle, Enter = nein): ").strip().lower()
    if fav_raw == "j":
        entry["favorite"] = not fav

    print(THEME["info"] + f"Aktuelle MAC: {entry.get('mac') or '-'}")
    mac_new = input("Neue MAC (leer = unverändert): ").strip()
    if mac_new:
        entry["mac"] = mac_new

    rdp_cfg[name] = entry
    update_rdp_cfg(rdp_cfg)
    print(THEME["ok"] + "\n✔ Aktualisiert.\n")
    pause()


def rdp_delete_connection():
    cfg, rdp_cfg = get_rdp_cfg()
    if not rdp_cfg:
        print(THEME["err"] + "❌ Keine RDP-Verbindungen gespeichert.")
        pause()
        return

    names = rdp_list_connections(show_header=True, with_status=False)
    choice = input("Nummer löschen: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Falsche Nummer.")
        pause()
        return

    name = names[int(choice) - 1]
    del rdp_cfg[name]
    update_rdp_cfg(rdp_cfg)
    print(THEME["err"] + f"\n🗑 RDP '{name}' gelöscht.\n")
    pause()


# ---------------------------------------------------------------------
# RDP – Listing / Suche
# ---------------------------------------------------------------------
def rdp_list_connections(show_header=True, filter_text=None, tag=None, with_status=True):
    cfg, rdp_cfg = get_rdp_cfg()
    if not rdp_cfg:
        print(THEME["err"] + "❌ Keine RDP-Verbindungen.")
        return []

    items = list(rdp_cfg.items())

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
        print(THEME["err"] + "❌ Keine passenden RDP-Verbindungen gefunden.")
        return []

    if show_header:
        print(THEME["rdp"] + "\n🪟 RDP-Verbindungen:\n")

    names = []
    for idx, (name, entry) in enumerate(items, start=1):
        names.append(name)
        host = entry["host"]
        user = entry.get("user", "")
        port = entry.get("port", "3389")
        tags = ",".join(entry.get("tags", [])) or "-"
        fav = "★" if entry.get("favorite", False) else " "
        mac = entry.get("mac") or "-"

        status_str = ""
        if with_status:
            online = ping_host(host)
            rdp_ok = check_tcp_port(host, port)
            s_ping = THEME["ok"] + "● ONLINE" if online else THEME["err"] + "● OFFLINE"
            s_rdp = THEME["ok"] + "🟢 RDP" if rdp_ok else THEME["err"] + "🔴 RDP"
            status_str = f" {s_ping}  {s_rdp}"

        print(
            f"{idx:2d}. "
            + THEME["rdp"] + f"{name:<20}"
            + " "
            + f"{host}:{port:<6} "
            + THEME["tag"] + f"[{tags}] "
            + THEME["fav"] + fav
            + THEME["info"] + f" MAC:{mac:<17}"
            + status_str
        )
    print()
    return names


def rdp_search_menu():
    clear()
    print(THEME["warn"] + "\n🔍 RDP Suche/Filter\n")
    text = input(THEME["info"] + "Suchtext (Name/Host/Tag, leer = alle): ").strip()
    tag = input(THEME["info"] + "Nur Tag (z.B. windows, leer = egal): ").strip()
    rdp_list_connections(filter_text=text or None, tag=tag or None)
    pause()


# ---------------------------------------------------------------------
# RDP – Connect & Info
# ---------------------------------------------------------------------
def rdp_connect():
    cfg, rdp_cfg = get_rdp_cfg()
    if not rdp_cfg:
        print(THEME["err"] + "❌ Keine RDP-Verbindungen gespeichert.")
        pause()
        return

    names = rdp_list_connections(show_header=True, with_status=True)
    choice = input("Nummer für RDP-Verbindung: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültige Auswahl.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = rdp_cfg[name]
    host = entry["host"]
    port = entry.get("port", "3389")

    ip = resolve_host(host)
    if ip and ip != host:
        print(THEME["info"] + f"\nHostname {host} → {ip}")

    log_session(name, "RDP_CONNECT")

    mstsc_cmd = ["mstsc", "/v:" + f"{host}:{port}", "/f"]
    print(THEME["ok"] + f"\n🔒 Starte RDP zu {name} ({host}:{port}) ...\n")
    subprocess.Popen(mstsc_cmd)
    pause("RDP gestartet. Weiter mit Enter...")


def rdp_show_info():
    cfg, rdp_cfg = get_rdp_cfg()
    if not rdp_cfg:
        print(THEME["err"] + "❌ Keine RDP-Verbindungen gespeichert.")
        pause()
        return

    names = rdp_list_connections(show_header=True, with_status=True)
    choice = input("Nummer für RDP-Info: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültige Auswahl.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = rdp_cfg[name]
    host = entry["host"]

    rdp_show_info_for_entry(name, entry)
    pause()


def rdp_show_info_for_entry(name, entry):
    host = entry["host"]
    cfg, ssh_cfg = get_ssh_cfg()  # für Matching

    clear()
    print(THEME["warn"] + f"\nℹ RDP / Windows Info für {name} ({host})\n")

    ip = resolve_host(host)
    if ip and ip != host:
        print(THEME["info"] + f"DNS-Resolve: {host} → {ip}\n")

    print(THEME["info"] + "→ Aktive Sessions (qwinsta):\n")
    try:
        subprocess.call(["qwinsta", "/server:" + host])
    except FileNotFoundError:
        print(THEME["err"] + "qwinsta nicht gefunden (nur auf manchen Windows-Versionen verfügbar).")

    print(THEME["info"] + "\n→ Systeminfo (Win32_OperatingSystem):\n")
    ps_cmd = [
        "powershell",
        "-NoLogo",
        "-Command",
        f"try {{ Get-CimInstance Win32_OperatingSystem -ComputerName '{host}' | "
        "Select-Object CSName, Caption, LastBootUpTime }} catch { Write-Host 'Zugriff nicht möglich.' }"
    ]
    subprocess.call(ps_cmd)

    # Matching SSH-Host
    print(THEME["info"] + "\n→ Passenden SSH-Host suchen (gleiche IP/Host)...")
    matches = []
    for ssh_name, ssh_entry in cfg["ssh"].items():
        if ssh_entry["host"].lower() == host.lower():
            matches.append(ssh_name)
        elif ip and ssh_entry["host"] == ip:
            matches.append(ssh_name)
    matches = list(dict.fromkeys(matches))
    if matches:
        print(THEME["ok"] + "Gefunden: " + ", ".join(matches))
        opt = input("SSH auf einen davon direkt öffnen? (Name eingeben / Enter = nein): ").strip()
        if opt and opt in matches:
            ssh_entry = cfg["ssh"][opt]
            user = ssh_entry["user"]
            h = ssh_entry["host"]
            p = ssh_entry.get("port", "22")
            print(THEME["ok"] + f"\nSSH zu {opt} ({user}@{h}:{p})...\n")
            subprocess.call(["ssh", "-p", str(p), f"{user}@{h}"])
    else:
        print(THEME["dim"] + "Kein passender SSH-Host gefunden.")


# ---------------------------------------------------------------------
# Wake-on-LAN
# ---------------------------------------------------------------------
def send_wol(mac, broadcast="255.255.255.255", port=9):
    import socket
    mac_clean = mac.replace(":", "").replace("-", "").lower()
    if len(mac_clean) != 12:
        raise ValueError("Ungültige MAC-Adresse")
    data = bytes.fromhex("FF" * 6 + mac_clean * 16)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(data, (broadcast, port))


def rdp_wake_on_lan():
    cfg, rdp_cfg = get_rdp_cfg()
    if not rdp_cfg:
        print(THEME["err"] + "❌ Keine RDP-Verbindungen gespeichert.")
        pause()
        return

    names = rdp_list_connections(show_header=True, with_status=False)
    choice = input("Nummer für Wake-on-LAN: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültige Auswahl.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = rdp_cfg[name]
    mac = entry.get("mac")
    host = entry["host"]
    port = entry.get("port", "3389")

    if not mac:
        print(THEME["err"] + "❌ Keine MAC-Adresse für diesen Host gespeichert.")
        pause()
        return

    print(THEME["info"] + f"\n➡ Sende Wake-on-LAN an {name} ({mac})...\n")
    try:
        send_wol(mac)
        print(THEME["ok"] + "✔ Magic Packet gesendet.\n")
    except Exception as e:
        print(THEME["err"] + f"❌ Fehler beim Senden: {e}")
        pause()
        return

    auto = input("Auf Online-Status + RDP-Port warten und dann automatisch RDP starten? (j/N): ").strip().lower()
    if auto != "j":
        pause()
        return

    print(THEME["warn"] + f"\nWarte auf {name} ({host}) ... (STRG+C zum Abbrechen)\n")
    try:
        while True:
            online = ping_host(host)
            rdp_ok = check_tcp_port(host, port)
            status = (THEME["ok"] + "[NET OK]" if online else THEME["err"] + "[NET OFF]") + " "
            status += (THEME["ok"] + "[RDP OK]" if rdp_ok else THEME["err"] + "[RDP OFF]")
            print("  " + status, end="\r", flush=True)
            if online and rdp_ok:
                print()
                print(THEME["ok"] + "\nHost ist online & RDP-Port offen – RDP wird gestartet...\n")
                log_session(name, "RDP_CONNECT_AFTER_WOL")
                mstsc_cmd = ["mstsc", "/v:" + f"{host}:{port}", "/f"]
                subprocess.Popen(mstsc_cmd)
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nAbgebrochen.")
    pause()


# ---------------------------------------------------------------------
# WinRM / PowerShell Remoting
# ---------------------------------------------------------------------
def rdp_winrm_powershell():
    cfg, rdp_cfg = get_rdp_cfg()
    if not rdp_cfg:
        print(THEME["err"] + "❌ Keine RDP/Windows-Verbindungen gespeichert.")
        pause()
        return

    names = rdp_list_connections(show_header=True, with_status=False)
    choice = input("Nummer für PowerShell Remoting: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print(THEME["err"] + "❌ Ungültige Auswahl.")
        pause()
        return

    name = names[int(choice) - 1]
    entry = rdp_cfg[name]
    host = entry["host"]

    print(THEME["info"] + f"\n➡ Starte PowerShell Remoting zu {name} ({host})\n")
    print(THEME["warn"] + "Hinweis: WinRM muss auf dem Zielrechner aktiviert sein.\n")
    cmd = [
        "powershell",
        "-NoLogo",
        "-NoExit",
        "-Command",
        f"Enter-PSSession -ComputerName '{host}'"
    ]
    subprocess.Popen(cmd)
    pause()
