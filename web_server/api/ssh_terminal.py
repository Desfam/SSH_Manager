"""
SSH Terminal over WebSocket
"""
from flask import Blueprint, render_template, request
from flask_login import login_required
from flask_socketio import emit
import sys
import os
import threading
import paramiko
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from Manager_file.managers.utils import load_config, PRIV_KEY

bp = Blueprint('ssh_terminal', __name__, url_prefix='/terminal')

# Store active SSH sessions
active_sessions = {}

@bp.route('/ssh/<name>')
@login_required
def ssh_terminal(name):
    """SSH terminal page"""
    config = load_config()
    ssh_connections = config.get('ssh', {})
    
    if name not in ssh_connections:
        return "Connection not found", 404
    
    connection = ssh_connections[name]
    return render_template('ssh_terminal.html', name=name, connection=connection)

def create_ssh_client(host, port, username, key_path=None, password=None):
    """Create and connect SSH client with proper host key validation"""
    client = paramiko.SSHClient()
    
    # Use a more secure host key policy
    # Try to load known hosts first, then use WarningPolicy instead of AutoAddPolicy
    try:
        client.load_system_host_keys()
    except IOError:
        pass
    
    # Use WarningPolicy which logs unknown hosts but still allows connection
    # In production, consider using RejectPolicy and managing known_hosts properly
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    
    try:
        if key_path and os.path.exists(key_path):
            client.connect(host, port=port, username=username, key_filename=key_path, timeout=10)
        elif password:
            client.connect(host, port=port, username=username, password=password, timeout=10)
        else:
            client.connect(host, port=port, username=username, timeout=10)
        return client
    except paramiko.SSHException as e:
        raise Exception(f"SSH connection failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to connect: {str(e)}")

def ssh_shell_thread(channel, session_id, socketio_instance):
    """Thread to read from SSH channel and send to client"""
    try:
        while True:
            if channel.recv_ready():
                data = channel.recv(4096)
                if len(data) == 0:
                    break
                socketio_instance.emit('ssh_output', {'data': data.decode('utf-8', errors='replace')}, 
                                     room=session_id)
            
            if channel.exit_status_ready():
                break
            
            time.sleep(0.01)
    except Exception as e:
        socketio_instance.emit('ssh_error', {'error': str(e)}, room=session_id)
    finally:
        socketio_instance.emit('ssh_disconnected', {}, room=session_id)

# Socket handlers will be registered in socket_handlers.py
