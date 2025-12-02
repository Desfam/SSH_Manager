# main.py
from managers.utils import (
    banner, clear, pause, THEME,
    print_recent_dashboard, print_status_bar,
    set_console_large, startup_status_check,
)
from managers import ssh_manager, rdp_manager, network_tools

def menu():
    while True:
        clear()
        banner()
        print_recent_dashboard()
        print_status_bar()

        print(THEME["info"] + """
=== SSH ===
 1. SSH-Verbindung hinzufügen
 2. SSH-Verbindung starten
 3. SSH-Verbindungen anzeigen
 4. SSH Datei-Transfer / Ordner-Sync
 5. SSH-Verbindung löschen
 6. SSH-Key automatisch einrichten
 7. SSH Suche / Filter
 8. SSH Host-Info anzeigen
 9. SSH Port-Forward Manager
10. SSH Live-Ping Monitor
11. SSH Health-Check aller Server
12. SSH Remote-Befehle (Reboot, Docker, etc.)
13. SSH Tags / Favoriten bearbeiten
14. SSH-Config generieren
15. SSH Mini-Top Monitor

=== RDP / Windows ===
16. RDP-Verbindung hinzufügen
17. RDP-Verbindung starten
18. RDP-Verbindungen anzeigen
19. RDP Infos / Sessions anzeigen
20. Wake-on-LAN senden
21. RDP Suche / Filter
22. RDP Tags / Favoriten / MAC bearbeiten
23. PowerShell Remoting (WinRM)

=== Tools ===
24. Admin Tools (ARP, DNS, Ports, Ping)

 0. Beenden
""")
        choice = input("Auswahl: ").strip()

        if choice == "1":
            ssh_manager.ssh_add_connection()
        elif choice == "2":
            ssh_manager.ssh_connect()
        elif choice == "3":
            ssh_manager.ssh_list_connections()
            pause()
        elif choice == "4":
            ssh_manager.ssh_file_transfer_menu()
        elif choice == "5":
            ssh_manager.ssh_delete_connection()
        elif choice == "6":
            ssh_manager.ssh_setup_ssh_key()
        elif choice == "7":
            ssh_manager.ssh_search_menu()
        elif choice == "8":
            ssh_manager.ssh_show_host_info()
        elif choice == "9":
            ssh_manager.ssh_port_forward_menu()
        elif choice == "10":
            ssh_manager.ssh_live_ping_monitor()
        elif choice == "11":
            ssh_manager.ssh_all_servers_health_check()
        elif choice == "12":
            ssh_manager.ssh_remote_commands_menu()
        elif choice == "13":
            ssh_manager.ssh_edit_tags_and_favorite()
        elif choice == "14":
            ssh_manager.ssh_generate_ssh_config()
        elif choice == "15":
            ssh_manager.ssh_mini_top_monitor()
        elif choice == "16":
            rdp_manager.rdp_add_connection()
        elif choice == "17":
            rdp_manager.rdp_connect()
        elif choice == "18":
            rdp_manager.rdp_list_connections()
            pause()
        elif choice == "19":
            rdp_manager.rdp_show_info()
        elif choice == "20":
            rdp_manager.rdp_wake_on_lan()
        elif choice == "21":
            rdp_manager.rdp_search_menu()
        elif choice == "22":
            rdp_manager.rdp_edit_tags_and_favorite()
        elif choice == "23":
            rdp_manager.rdp_winrm_powershell()
        elif choice == "24":
            network_tools.tools_menu()
        elif choice == "0":
            break
        else:
            print(THEME["err"] + "❌ Ungültige Auswahl.")
            pause()


if __name__ == "__main__":
    set_console_large()
    startup_status_check()
    menu()
