# managers/utils.py
import json
import os
import platform
import shutil
import subprocess
import time
from datetime import datetime

from colorama import init, Fore, Style

init(autoreset=True)

# ---------------------------------------------------------------------
# Pfade / Dateien
# ---------------------------------------------------------------------
CONFIG_PATH = os.path.expanduser("~/.ssh_manager.json")
SESSION_LOG_PATH = os.path.expanduser("~/.ssh_manager_sessions.log")
SSH_DIR = os.path.join(os.environ.get("USERPROFILE", ""), ".ssh")
PRIV_KEY = os.path.join(SSH_DIR, "id_ed25519")
PUB_KEY = PRIV_KEY + ".pub"
SSH_CONFIG_FILE = os.path.join(SSH_DIR, "config")

# ---------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------
THEME = {
    "title": Fore.CYAN + Style.BRIGHT,
    "subtitle": Fore.MAGENTA + Style.BRIGHT,
    "ok": Fore.GREEN,
    "warn": Fore.YELLOW,
    "err": Fore.RED,
    "info": Fore.CYAN,
    "ssh": Fore.CYAN,
    "rdp": Fore.GREEN,
    "tag": Fore.BLUE,
    "fav": Fore.YELLOW,
    "dim": Style.DIM + Fore.WHITE,
}


# ---------------------------------------------------------------------
# Konsole / UI
# ---------------------------------------------------------------------
def set_console_large():
    """Große Konsole für Vollbild-Feeling (nur Windows)."""
    if os.name == "nt":
        try:
            os.system("mode con: cols=200 lines=60")
        except Exception:
            pass


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print(THEME["title"] + r"""
███████╗███████╗██╗  ██╗      ████╗ ███╗
██╔════╝██╔════╝██║  ██║     ██╔══██╗╚██║
███████╗█████╗  ███████║     ╚═╝ ██╔╝ ██║
╚════██║██╔══╝  ██╔══██║     █████╔╝  ██║
███████║███████╗██║  ██║     ╚═══╝    ██║
╚══════╝╚══════╝╚═╝  ╚═╝              ╚═╝
""" + Style.RESET_ALL)
    print(THEME["subtitle"] + "        🗝  SSH & RDP Manager PRO – Windows\n")


def pause(msg="Weiter mit Enter..."):
    input(THEME["subtitle"] + msg)


# ---------------------------------------------------------------------
# Config / Storage / Logging
# ---------------------------------------------------------------------
def load_config():
    """
    Schema:
    {
      "ssh": {...},
      "rdp": {...}
    }
    Backwards kompatibel zu alter Struktur (nur ssh).
    """
    if not os.path.exists(CONFIG_PATH):
        return {"ssh": {}, "rdp": {}}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and ("ssh" in data or "rdp" in data):
        data.setdefault("ssh", {})
        data.setdefault("rdp", {})
        return data
    return {"ssh": data, "rdp": {}}


def save_config(cfg):
    cfg.setdefault("ssh", {})
    cfg.setdefault("rdp", {})
    if os.path.exists(CONFIG_PATH):
        backup = CONFIG_PATH + ".bak"
        try:
            shutil.copy2(CONFIG_PATH, backup)
        except Exception:
            pass
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


def get_ssh_cfg():
    cfg = load_config()
    return cfg, cfg["ssh"]


def get_rdp_cfg():
    cfg = load_config()
    return cfg, cfg["rdp"]


def update_ssh_cfg(ssh_cfg):
    cfg = load_config()
    cfg["ssh"] = ssh_cfg
    save_config(cfg)


def update_rdp_cfg(rdp_cfg):
    cfg = load_config()
    cfg["rdp"] = rdp_cfg
    save_config(cfg)


def log_session(host_name, entry_type="CONNECT", extra=None):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts};{entry_type};{host_name};{extra or ''}\n"
    try:
        with open(SESSION_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def get_recent_sessions(limit=5):
    if not os.path.exists(SESSION_LOG_PATH):
        return []
    try:
        with open(SESSION_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [l.strip() for l in lines[-limit:]]
    except Exception:
        return []


# ---------------------------------------------------------------------
# Netzwerk / Status
# ---------------------------------------------------------------------
def ping_host(host, count=1, timeout=1):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = ["ping", param, str(count), host]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout
        )
        return result.returncode == 0
    except Exception:
        return False


def check_tcp_port(host, port, timeout=1.5):
    import socket
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def ssh_key_works(entry):
    """Prüft, ob Key-Login ohne Passwort funktioniert."""
    host = entry["host"]
    user = entry["user"]
    port = entry.get("port", "22")

    cmd = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=3",
        "-p", str(port),
        f"{user}@{host}",
        "echo OK"
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return result.returncode == 0 and "OK" in (result.stdout or "")
    except Exception:
        return False


# ---------------------------------------------------------------------
# SSH-Key Handling
# ---------------------------------------------------------------------
def ensure_ssh_dir():
    if not os.path.exists(SSH_DIR):
        os.makedirs(SSH_DIR, exist_ok=True)


def ensure_ssh_key():
    ensure_ssh_dir()
    if not os.path.exists(PRIV_KEY):
        print(THEME["info"] + "➡ Kein SSH-Key gefunden – erstelle neuen Ed25519-Key...")
        subprocess.run([
            "ssh-keygen",
            "-t", "ed25519",
            "-f", PRIV_KEY,
            "-N", ""
        ], shell=True)
        print(THEME["ok"] + "✔ SSH-Key erzeugt.")
    else:
        print(THEME["ok"] + "✔ SSH-Key bereits vorhanden.")
    if not os.path.exists(PUB_KEY):
        print(THEME["err"] + "⚠ Public-Key fehlt – irgendwas stimmt nicht mit dem Key-Setup.")
        return False
    return True


# ---------------------------------------------------------------------
# Dashboard / Startstatus
# ---------------------------------------------------------------------
def print_recent_dashboard():
    print(THEME["subtitle"] + "Letzte Aktivitäten:" + Style.RESET_ALL)
    sessions = get_recent_sessions(5)
    if not sessions:
        print(THEME["dim"] + "  (noch keine Einträge)")
    else:
        for line in sessions:
            try:
                ts, etype, host, extra = line.split(";", 3)
            except ValueError:
                print("  " + line)
                continue
            print(
                THEME["dim"]
                + f"  [{ts}] "
                + THEME["info"]
                + f"{etype:<12}"
                + Style.RESET_ALL
                + " → "
                + host
            )
    print()


def print_status_bar():
    cfg = load_config()
    ssh_cfg = cfg["ssh"]
    rdp_cfg = cfg["rdp"]

    def pick_favs(d, limit):
        items = list(d.items())
        items.sort(key=lambda x: (not x[1].get("favorite", False), x[0].lower()))
        return items[:limit]

    ssh_favs = pick_favs(ssh_cfg, 3)
    rdp_favs = pick_favs(rdp_cfg, 3)

    line_parts = []

    for name, entry in ssh_favs:
        host = entry["host"]
        online = ping_host(host)
        s = (THEME["ssh"] + f"SSH:{name} " +
             (THEME["ok"] + "●" if online else THEME["err"] + "●"))
        line_parts.append(s)

    for name, entry in rdp_favs:
        host = entry["host"]
        port = entry.get("port", "3389")
        online = ping_host(host)
        rdp_ok = check_tcp_port(host, port)
        s = (THEME["rdp"] + f"RDP:{name} " +
             (THEME["ok"] + "●" if online else THEME["err"] + "●") +
             "/" +
             (THEME["ok"] + "R" if rdp_ok else THEME["err"] + "R"))
        line_parts.append(s)

    if line_parts:
        print(" | ".join(line_parts))
    print()


def startup_status_check():
    cfg = load_config()
    ssh_cfg = cfg["ssh"]
    rdp_cfg = cfg["rdp"]

    print(THEME["subtitle"] + "Start-Statuscheck (SSH & RDP)" + Style.RESET_ALL)
    if not ssh_cfg and not rdp_cfg:
        print(THEME["dim"] + "Keine Einträge vorhanden.")
        pause()
        return

    if ssh_cfg:
        print(THEME["ssh"] + "\nSSH Hosts:")
        for name, entry in ssh_cfg.items():
            host = entry["host"]
            online = ping_host(host)
            s = f"  {name:<20} {host:<15} "
            s += THEME["ok"] + "[ONLINE]" if online else THEME["err"] + "[OFFLINE]"
            print(s)

    if rdp_cfg:
        print(THEME["rdp"] + "\nRDP Hosts:")
        for name, entry in rdp_cfg.items():
            host = entry["host"]
            port = entry.get("port", "3389")
            online = ping_host(host)
            rdp_ok = check_tcp_port(host, port)
            s = f"  {name:<20} {host}:{port:<6} "
            s += THEME["ok"] + "[NET]" if online else THEME["err"] + "[NET]"
            s += " "
            s += THEME["ok"] + "[RDP]" if rdp_ok else THEME["err"] + "[RDP]"
            print(s)
    print()
    pause("Statuscheck fertig. Weiter mit Enter...")
