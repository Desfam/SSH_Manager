"""
WebSocket handlers for SSH terminal
"""
import sys
import os
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import after app is created
def register_socket_handlers(socketio_instance):
    """Register all socket handlers"""
    from web_server.api.ssh_terminal import create_ssh_client, ssh_shell_thread, active_sessions
    from Manager_file.managers.utils import load_config, PRIV_KEY
    
    @socketio_instance.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            emit('connected', {'status': 'connected'})
    
    @socketio_instance.on('disconnect')
    def handle_disconnect():
        # Clean up any active SSH sessions for this user
        pass
    
    @socketio_instance.on('ssh_connect')
    def handle_ssh_connect(data):
        """Establish SSH connection"""
        if not current_user.is_authenticated:
            emit('ssh_error', {'error': 'Not authenticated'})
            return
        
        connection_name = data.get('name')
        session_id = data.get('session_id')
        
        config = load_config()
        ssh_connections = config.get('ssh', {})
        
        if connection_name not in ssh_connections:
            emit('ssh_error', {'error': 'Connection not found'})
            return
        
        conn = ssh_connections[connection_name]
        
        try:
            # Create SSH client
            client = create_ssh_client(
                host=conn.get('host'),
                port=int(conn.get('port', 22)),
                username=conn.get('user'),
                key_path=PRIV_KEY if os.path.exists(PRIV_KEY) else None
            )
            
            # Create interactive shell
            channel = client.invoke_shell(term='xterm', width=80, height=24)
            
            # Store session
            active_sessions[session_id] = {
                'client': client,
                'channel': channel,
                'thread': None
            }
            
            # Join socket room
            join_room(session_id)
            
            # Start thread to read from SSH
            thread = threading.Thread(
                target=ssh_shell_thread,
                args=(channel, session_id, socketio_instance)
            )
            thread.daemon = True
            thread.start()
            
            active_sessions[session_id]['thread'] = thread
            
            emit('ssh_connected', {'status': 'connected'}, room=session_id)
            
        except Exception as e:
            emit('ssh_error', {'error': str(e)})
    
    @socketio_instance.on('ssh_input')
    def handle_ssh_input(data):
        """Send input to SSH session"""
        if not current_user.is_authenticated:
            return
        
        session_id = data.get('session_id')
        input_data = data.get('data')
        
        if session_id in active_sessions:
            try:
                channel = active_sessions[session_id]['channel']
                channel.send(input_data)
            except Exception as e:
                emit('ssh_error', {'error': str(e)}, room=session_id)
    
    @socketio_instance.on('ssh_resize')
    def handle_ssh_resize(data):
        """Resize SSH terminal"""
        if not current_user.is_authenticated:
            return
        
        session_id = data.get('session_id')
        width = data.get('width', 80)
        height = data.get('height', 24)
        
        if session_id in active_sessions:
            try:
                channel = active_sessions[session_id]['channel']
                channel.resize_pty(width=width, height=height)
            except Exception as e:
                emit('ssh_error', {'error': str(e)}, room=session_id)
    
    @socketio_instance.on('ssh_disconnect_session')
    def handle_ssh_disconnect(data):
        """Disconnect SSH session"""
        if not current_user.is_authenticated:
            return
        
        session_id = data.get('session_id')
        
        if session_id in active_sessions:
            try:
                session = active_sessions[session_id]
                session['channel'].close()
                session['client'].close()
                leave_room(session_id)
                del active_sessions[session_id]
                emit('ssh_disconnected', {}, room=session_id)
            except Exception as e:
                emit('ssh_error', {'error': str(e)})
