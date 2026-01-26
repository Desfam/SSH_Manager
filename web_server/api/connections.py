"""
Connections API - Manage SSH and RDP connections
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from Manager_file.managers.utils import load_config, save_config, ping_host, check_tcp_port

bp = Blueprint('connections', __name__, url_prefix='/connections')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing all connections"""
    config = load_config()
    ssh_connections = config.get('ssh', {})
    rdp_connections = config.get('rdp', {})
    
    return render_template('dashboard.html', 
                         ssh_connections=ssh_connections,
                         rdp_connections=rdp_connections)

@bp.route('/api/ssh', methods=['GET'])
@login_required
def list_ssh():
    """List all SSH connections"""
    config = load_config()
    ssh_connections = config.get('ssh', {})
    return jsonify(ssh_connections)

@bp.route('/api/ssh/<name>', methods=['GET'])
@login_required
def get_ssh(name):
    """Get specific SSH connection"""
    config = load_config()
    ssh_connections = config.get('ssh', {})
    if name in ssh_connections:
        return jsonify(ssh_connections[name])
    return jsonify({'error': 'Connection not found'}), 404

@bp.route('/api/ssh', methods=['POST'])
@login_required
def add_ssh():
    """Add new SSH connection"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    config = load_config()
    ssh_connections = config.get('ssh', {})
    
    if name in ssh_connections:
        return jsonify({'error': 'Connection already exists'}), 409
    
    ssh_connections[name] = {
        'user': data.get('user', ''),
        'host': data.get('host', ''),
        'port': data.get('port', '22'),
        'tags': data.get('tags', []),
        'favorite': data.get('favorite', False)
    }
    
    config['ssh'] = ssh_connections
    save_config(config)
    
    return jsonify({'success': True, 'message': f'SSH connection {name} added'}), 201

@bp.route('/api/ssh/<name>', methods=['PUT'])
@login_required
def update_ssh(name):
    """Update SSH connection"""
    config = load_config()
    ssh_connections = config.get('ssh', {})
    
    if name not in ssh_connections:
        return jsonify({'error': 'Connection not found'}), 404
    
    data = request.json
    ssh_connections[name].update({
        'user': data.get('user', ssh_connections[name].get('user')),
        'host': data.get('host', ssh_connections[name].get('host')),
        'port': data.get('port', ssh_connections[name].get('port')),
        'tags': data.get('tags', ssh_connections[name].get('tags')),
        'favorite': data.get('favorite', ssh_connections[name].get('favorite'))
    })
    
    config['ssh'] = ssh_connections
    save_config(config)
    
    return jsonify({'success': True, 'message': f'SSH connection {name} updated'})

@bp.route('/api/ssh/<name>', methods=['DELETE'])
@login_required
def delete_ssh(name):
    """Delete SSH connection"""
    config = load_config()
    ssh_connections = config.get('ssh', {})
    
    if name not in ssh_connections:
        return jsonify({'error': 'Connection not found'}), 404
    
    del ssh_connections[name]
    config['ssh'] = ssh_connections
    save_config(config)
    
    return jsonify({'success': True, 'message': f'SSH connection {name} deleted'})

@bp.route('/api/rdp', methods=['GET'])
@login_required
def list_rdp():
    """List all RDP connections"""
    config = load_config()
    rdp_connections = config.get('rdp', {})
    return jsonify(rdp_connections)

@bp.route('/api/rdp/<name>', methods=['GET'])
@login_required
def get_rdp(name):
    """Get specific RDP connection"""
    config = load_config()
    rdp_connections = config.get('rdp', {})
    if name in rdp_connections:
        return jsonify(rdp_connections[name])
    return jsonify({'error': 'Connection not found'}), 404

@bp.route('/api/rdp', methods=['POST'])
@login_required
def add_rdp():
    """Add new RDP connection"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    config = load_config()
    rdp_connections = config.get('rdp', {})
    
    if name in rdp_connections:
        return jsonify({'error': 'Connection already exists'}), 409
    
    rdp_connections[name] = {
        'user': data.get('user', ''),
        'host': data.get('host', ''),
        'port': data.get('port', '3389'),
        'mac': data.get('mac', ''),
        'tags': data.get('tags', []),
        'favorite': data.get('favorite', False)
    }
    
    config['rdp'] = rdp_connections
    save_config(config)
    
    return jsonify({'success': True, 'message': f'RDP connection {name} added'}), 201

@bp.route('/api/rdp/<name>', methods=['PUT'])
@login_required
def update_rdp(name):
    """Update RDP connection"""
    config = load_config()
    rdp_connections = config.get('rdp', {})
    
    if name not in rdp_connections:
        return jsonify({'error': 'Connection not found'}), 404
    
    data = request.json
    rdp_connections[name].update({
        'user': data.get('user', rdp_connections[name].get('user')),
        'host': data.get('host', rdp_connections[name].get('host')),
        'port': data.get('port', rdp_connections[name].get('port')),
        'mac': data.get('mac', rdp_connections[name].get('mac')),
        'tags': data.get('tags', rdp_connections[name].get('tags')),
        'favorite': data.get('favorite', rdp_connections[name].get('favorite'))
    })
    
    config['rdp'] = rdp_connections
    save_config(config)
    
    return jsonify({'success': True, 'message': f'RDP connection {name} updated'})

@bp.route('/api/rdp/<name>', methods=['DELETE'])
@login_required
def delete_rdp(name):
    """Delete RDP connection"""
    config = load_config()
    rdp_connections = config.get('rdp', {})
    
    if name not in rdp_connections:
        return jsonify({'error': 'Connection not found'}), 404
    
    del rdp_connections[name]
    config['rdp'] = rdp_connections
    save_config(config)
    
    return jsonify({'success': True, 'message': f'RDP connection {name} deleted'})

@bp.route('/api/check-status/<connection_type>/<name>', methods=['GET'])
@login_required
def check_status(connection_type, name):
    """Check if a connection is online"""
    config = load_config()
    connections = config.get(connection_type, {})
    
    if name not in connections:
        return jsonify({'error': 'Connection not found'}), 404
    
    conn = connections[name]
    host = conn.get('host')
    port = int(conn.get('port', 22 if connection_type == 'ssh' else 3389))
    
    # Check if host is reachable
    ping_result = ping_host(host)
    port_result = check_tcp_port(host, port)
    
    return jsonify({
        'online': ping_result and port_result,
        'ping': ping_result,
        'port_open': port_result
    })
