"""
SSH & RDP Web Manager - Main Application
Web interface for managing SSH and RDP connections with agent deployment
"""
import os
import sys
from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO
from flask_login import LoginManager, login_required, current_user

# Add parent directory to path to import Manager_file modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Manager_file.managers.utils import load_config, THEME

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Flask-SocketIO for real-time SSH/RDP connections
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize Flask-Login for authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from web_server.api import auth, connections, ssh_terminal, agent_api
from web_server.socket_handlers import register_socket_handlers

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(connections.bp)
app.register_blueprint(ssh_terminal.bp)
app.register_blueprint(agent_api.bp)

# Register socket handlers
register_socket_handlers(socketio)

@app.route('/')
def index():
    """Main dashboard page"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('connections.dashboard'))

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'SSH & RDP Web Manager'}), 200

@login_manager.user_loader
def load_user(user_id):
    from web_server.api.auth import User
    return User.get(user_id)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

def create_app():
    """Application factory"""
    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting SSH & RDP Web Manager on {host}:{port}")
    
    # Only allow unsafe werkzeug in debug mode for development
    # In production, use a proper WSGI server like gunicorn
    if debug:
        print("⚠️  WARNING: Running in DEBUG mode with unsafe werkzeug - DO NOT use in production!")
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    else:
        socketio.run(app, host=host, port=port, debug=debug)
