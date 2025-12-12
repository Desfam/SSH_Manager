"""Migration script: move plaintext "password" fields from ~/.ssh_manager.json into OS keyring.

Usage: python scripts/migrate_credentials_to_keyring.py
It will prompt for confirmation before modifying files.
"""
import json
from pathlib import Path
import getpass
import keyring

CONFIG_PATH = Path.home() / ".ssh_manager.json"
SERVICE = "ssh_manager"

if not CONFIG_PATH.exists():
    print("No config file found at", CONFIG_PATH)
    exit(0)

with open(CONFIG_PATH) as f:
    cfg = json.load(f)

modified = False

for section in ("ssh", "rdp"):
    entries = cfg.get(section, {})
    for name, entry in entries.items():
        if isinstance(entry, dict) and entry.get("password"):
            pw = entry.get("password")
            print(f"Entry {section}/{name} has a stored password.")
            confirm = input("Migrate this password to keyring and remove it from JSON? [y/N]: ")
            if confirm.lower() == "y":
                keyring.set_password(SERVICE, f"{section}:{name}", pw)
                del entry["password"]
                modified = True

if modified:
    backup = CONFIG_PATH.with_suffix('.bak.json')
    CONFIG_PATH.rename(backup)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)
    print("Migration complete. Original backed up at", backup)
else:
    print("No passwords migrated.")
