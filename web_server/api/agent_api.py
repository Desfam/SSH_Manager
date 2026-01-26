"""
Agent API - Deploy and manage agents on remote hosts
"""
from flask import Blueprint, request, jsonify, render_template, send_file
from flask_login import login_required
import sys
import os
import json
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from Manager_file.managers.utils import load_config

bp = Blueprint('agent', __name__, url_prefix='/agent')

# Agent data storage
AGENTS_FILE = os.path.expanduser('~/.ssh_manager_agents.json')

def load_agents():
    """Load deployed agents information"""
    if not os.path.exists(AGENTS_FILE):
        return {}
    with open(AGENTS_FILE, 'r') as f:
        return json.load(f)

def save_agents(agents):
    """Save deployed agents information"""
    with open(AGENTS_FILE, 'w') as f:
        json.dump(agents, f, indent=2)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Agent management dashboard"""
    agents = load_agents()
    return render_template('agent_dashboard.html', agents=agents)

@bp.route('/api/list', methods=['GET'])
@login_required
def list_agents():
    """List all deployed agents"""
    agents = load_agents()
    return jsonify(agents)

@bp.route('/api/deploy', methods=['POST'])
@login_required
def deploy_agent():
    """Deploy agent to a host"""
    data = request.json
    connection_name = data.get('connection_name')
    connection_type = data.get('connection_type', 'ssh')
    
    if not connection_name:
        return jsonify({'error': 'Connection name is required'}), 400
    
    config = load_config()
    connections = config.get(connection_type, {})
    
    if connection_name not in connections:
        return jsonify({'error': 'Connection not found'}), 404
    
    conn = connections[connection_name]
    
    # Create agent record
    agents = load_agents()
    agent_id = f"{connection_type}_{connection_name}"
    agents[agent_id] = {
        'connection_name': connection_name,
        'connection_type': connection_type,
        'host': conn.get('host'),
        'deployed_at': __import__('datetime').datetime.now().isoformat(),
        'status': 'deployed',
        'features': ['performance', 'file_explorer', 'logs', 'processes']
    }
    save_agents(agents)
    
    return jsonify({
        'success': True, 
        'message': f'Agent deployed to {connection_name}',
        'agent_id': agent_id
    }), 201

@bp.route('/api/<agent_id>/metrics', methods=['GET'])
@login_required
def get_metrics(agent_id):
    """Get performance metrics from agent"""
    agents = load_agents()
    
    if agent_id not in agents:
        return jsonify({'error': 'Agent not found'}), 404
    
    agent = agents[agent_id]
    
    # In a real implementation, this would query the actual agent
    # For now, return mock data
    import psutil
    
    metrics = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'used': psutil.disk_usage('/').used,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        },
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    return jsonify(metrics)

@bp.route('/api/<agent_id>/files', methods=['GET'])
@login_required
def browse_files(agent_id):
    """Browse files on remote host"""
    agents = load_agents()
    
    if agent_id not in agents:
        return jsonify({'error': 'Agent not found'}), 404
    
    path = request.args.get('path', '/')
    
    # In a real implementation, this would query the agent
    # For now, return mock data
    files = [
        {'name': 'home', 'type': 'directory', 'size': 4096},
        {'name': 'var', 'type': 'directory', 'size': 4096},
        {'name': 'etc', 'type': 'directory', 'size': 4096},
        {'name': 'tmp', 'type': 'directory', 'size': 4096},
    ]
    
    return jsonify({'path': path, 'files': files})

@bp.route('/api/<agent_id>/processes', methods=['GET'])
@login_required
def list_processes(agent_id):
    """List processes on remote host"""
    agents = load_agents()
    
    if agent_id not in agents:
        return jsonify({'error': 'Agent not found'}), 404
    
    # In a real implementation, this would query the agent
    import psutil
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu_percent': proc.info['cpu_percent'],
                'memory_percent': proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return jsonify(processes[:50])  # Return top 50 processes

@bp.route('/api/<agent_id>', methods=['DELETE'])
@login_required
def remove_agent(agent_id):
    """Remove deployed agent"""
    agents = load_agents()
    
    if agent_id not in agents:
        return jsonify({'error': 'Agent not found'}), 404
    
    del agents[agent_id]
    save_agents(agents)
    
    return jsonify({'success': True, 'message': f'Agent {agent_id} removed'})

@bp.route('/download/agent-script')
@login_required
def download_agent_script():
    """Download agent installation script"""
    # Return the agent script file
    agent_script_path = os.path.join(os.path.dirname(__file__), '..', 'agent', 'agent.py')
    if os.path.exists(agent_script_path):
        return send_file(agent_script_path, as_attachment=True, download_name='ssh_manager_agent.py')
    return jsonify({'error': 'Agent script not found'}), 404
