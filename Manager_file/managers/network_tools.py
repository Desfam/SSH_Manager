# managers/network_tools.py
import subprocess

from .utils import THEME, clear, pause, check_tcp_port

def tools_menu():
    while True:
        clear()
        print(THEME["warn"] + "\n🧰 Admin Tools\n")
        print(THEME["info"] + """
1. ARP-Tabelle anzeigen
2. DNS Lookup (nslookup)
3. Portcheck (TCP)
4. Ping-Serie (10 Pings)
0. Zurück
""")
        opt = input("Auswahl: ").strip()
        if opt == "0":
            break
        elif opt == "1":
            print(THEME["info"] + "\nARP -a:\n")
            subprocess.call(["arp", "-a"])
            print()
            pause()
        elif opt == "2":
            host = input("Hostname oder IP: ").strip()
            subprocess.call(["nslookup", host])
            print()
            pause()
        elif opt == "3":
            host = input("Host: ").strip()
            port = input("Port: ").strip()
            if not port.isdigit():
                print(THEME["err"] + "Ungültiger Port.")
                pause()
                continue
            ok = check_tcp_port(host, int(port), timeout=2)
            if ok:
                print(THEME["ok"] + f"Port {port} auf {host} ist ERREICHBAR.")
            else:
                print(THEME["err"] + f"Port {port} auf {host} ist NICHT erreichbar.")
            pause()
        elif opt == "4":
            host = input("Host: ").strip()
            print(THEME["info"] + f"\nPing 10x {host}:\n")
            param = "-n" if hasattr(subprocess, "CREATE_NEW_CONSOLE") else "-c"
            subprocess.call(["ping", param, "10", host])
            print()
            pause()
        else:
            print(THEME["err"] + "❌ Ungültige Auswahl.")
            pause()
