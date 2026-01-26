#!/usr/bin/env python3
"""
Startup script for SSH & RDP Web Manager
"""
import os
import sys

def main():
    print("=" * 60)
    print("SSH & RDP Web Manager")
    print("=" * 60)
    print()
    
    # Check if running in correct directory
    if not os.path.exists('web_server'):
        print("Error: Please run this script from the repository root directory")
        sys.exit(1)
    
    # Check if dependencies are installed
    try:
        import flask
        import flask_socketio
        import flask_login
        import paramiko
        import psutil
        print("✓ All dependencies installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print()
        print("Please install dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print()
    print("Starting web server...")
    print()
    
    # Import and run the app
    from web_server.app import socketio, app
    
    # Configuration
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Server: http://{host}:{port}")
    print()
    print("Default credentials:")
    print("  Username: admin")
    print("  Password: admin")
    print()
    print("⚠️  Please change the default password after first login!")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print()
        print("Shutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
