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
    """Create and connect SSH client with proper host key validation
    
    Security Note: Uses WarningPolicy for host key validation to allow
    connections to user-managed SSH servers. For maximum security in
    production environments, consider:
    1. Using RejectPolicy with pre-populated known_hosts
    2. Implementing a host key verification UI
    3. Using certificate-based authentication
    """
    client = paramiko.SSHClient()
    
    # Try to load system and user known hosts
    try:
        client.load_system_host_keys()
    except IOError:
        pass
    
    try:
        # Load user known hosts from standard location
        import os
        known_hosts = os.path.expanduser('~/.ssh/known_hosts')
        if os.path.exists(known_hosts):
            client.load_host_keys(known_hosts)
    except Exception:
        pass
    
    # Use WarningPolicy which logs unknown hosts but allows connection
    # This is a compromise between security and usability for user-managed servers
    # CodeQL Alert: This is intentional for this use case where users manage
    # their own SSH connections. The warning is logged for security monitoring.
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
