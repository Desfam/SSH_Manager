"""Keyring helper for SSH_Manager

This module provides simple helpers to store and retrieve passwords/secret tokens
in the OS keyring instead of keeping them in plaintext in the JSON config.
"""

from pathlib import Path
import json
import keyring

CONFIG_PATH = Path.home() / ".ssh_manager.json"
KEYRING_SERVICE = "ssh_manager"


def set_password(entry_name: str, password: str) -> None:
    """Store a secret in the OS keyring."""
    keyring.set_password(KEYRING_SERVICE, entry_name, password)


def get_password(entry_name: str):
    """Retrieve a secret from the OS keyring. Returns None if not found."""
    return keyring.get_password(KEYRING_SERVICE, entry_name)


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text())


def save_config(cfg: dict):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
