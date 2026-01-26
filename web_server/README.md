# SSH & RDP Web Manager

Web-based interface for managing SSH and RDP connections with deployable agent system.

## Features

### Core Features
- 🌐 **Web-Based Dashboard** - Modern, responsive web interface
- 🔐 **Secure Authentication** - Login system with password management
- 🔵 **SSH Management** - Add, edit, delete, and connect to SSH servers
- 🟢 **RDP Management** - Manage RDP connections
- 💻 **Web SSH Terminal** - Browser-based SSH terminal using xterm.js
- 🤖 **Agent System** - Deploy agents to remote hosts for monitoring

### Agent Features
- 📊 **Performance Monitoring** - Real-time CPU, memory, disk usage
- 📁 **File Browser** - Browse remote filesystem
- ⚙️ **Process Management** - View running processes
- 📈 **System Metrics** - Detailed system information

## Installation

### Prerequisites
- Python 3.9+
- pip (Python package manager)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the web server:
```bash
python -m web_server.app
```

Or use the startup script:
```bash
python start_web_server.py
```

3. Access the web interface:
```
http://localhost:5000
```

Default credentials:
- Username: `admin`
- Password: `admin`

**⚠️ Change the default password immediately after first login!**

**⚠️ IMPORTANT:** The development server is NOT suitable for production use. See "Production Deployment" below.

## Production Deployment

For production environments, use a proper WSGI server:

### Using Gunicorn (Recommended)

1. Install gunicorn and eventlet:
```bash
pip install gunicorn eventlet
```

2. Run with gunicorn:
```bash
gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 web_server.app:app
```

### Using uWSGI

1. Install uWSGI:
```bash
pip install uwsgi
```

2. Run with uWSGI:
```bash
uwsgi --http :5000 --gevent 1000 --http-websockets --module web_server.app:app
```

### Production Checklist
- [ ] Set a strong SECRET_KEY environment variable
- [ ] Disable DEBUG mode (DEBUG=False)
- [ ] Use HTTPS (configure reverse proxy)
- [ ] Configure firewall rules
- [ ] Set up proper logging
- [ ] Regular security updates
- [ ] Strong authentication credentials
- [ ] Regular backups of configuration

## Configuration

Environment variables:
- `PORT` - Server port (default: 5000)
- `HOST` - Server host (default: 0.0.0.0)
- `DEBUG` - Debug mode (default: False)
- `SECRET_KEY` - Flask secret key (required for production)

Example:
```bash
export SECRET_KEY="your-secret-key-here"
export PORT=8080
python -m web_server.app
```

## Agent Deployment

### Automatic Deployment (Coming Soon)
1. Go to Agent Dashboard
2. Click "Deploy Agent"
3. Select a connection
4. Agent will be automatically deployed

### Manual Deployment
1. Download the agent script from the web interface
2. Copy to remote host:
   ```bash
   scp agent.py user@host:/path/to/agent/
   ```
3. Install dependencies on remote host:
   ```bash
   pip install psutil
   ```
4. Run the agent:
   ```bash
   python agent.py
   ```

The agent will run on port 9876 by default.

## Security Considerations

### Authentication & Access
- Always change default credentials immediately
- Use strong, unique passwords
- Implement SSH key-based authentication when possible
- Consider adding multi-factor authentication for production

### Network Security
- Use HTTPS in production (configure reverse proxy)
- Set strong SECRET_KEY environment variable
- Restrict network access to the web interface
- Configure firewall rules appropriately
- Consider using VPN for remote access

### SSH Connections
- The web terminal uses WarningPolicy for SSH host keys
- In production, consider implementing RejectPolicy with proper known_hosts management
- Use SSH keys instead of passwords whenever possible
- Regularly rotate SSH keys
- Review SSH configurations regularly

### Agent Deployment
- Review agent permissions before deployment
- Only deploy agents on trusted hosts
- Use firewall rules to restrict agent port access
- Monitor agent activity and logs
- Consider network segmentation

### General Best Practices
- Keep all dependencies updated
- Regular security audits
- Monitor logs for suspicious activity
- Regular backups of configuration
- Implement rate limiting for API endpoints
- Use production WSGI server (not Flask development server)

## Architecture

```
web_server/
├── app.py                 # Main Flask application
├── api/                   # API endpoints
│   ├── auth.py           # Authentication
│   ├── connections.py    # SSH/RDP management
│   ├── ssh_terminal.py   # SSH terminal via WebSocket
│   └── agent_api.py      # Agent management
├── templates/            # HTML templates
├── static/              # CSS, JavaScript, images
├── agent/               # Agent scripts
│   └── agent.py         # Deployable agent
└── socket_handlers.py   # WebSocket handlers
```

## API Endpoints

### Authentication
- `POST /auth/login` - Login
- `GET /auth/logout` - Logout
- `POST /auth/change-password` - Change password

### Connections
- `GET /connections/api/ssh` - List SSH connections
- `POST /connections/api/ssh` - Add SSH connection
- `PUT /connections/api/ssh/<name>` - Update SSH connection
- `DELETE /connections/api/ssh/<name>` - Delete SSH connection
- Similar endpoints for RDP connections

### Agent
- `GET /agent/api/list` - List deployed agents
- `POST /agent/api/deploy` - Deploy agent
- `GET /agent/api/<id>/metrics` - Get performance metrics
- `GET /agent/api/<id>/files` - Browse files
- `GET /agent/api/<id>/processes` - List processes
- `DELETE /agent/api/<id>` - Remove agent

## Troubleshooting

### Connection Issues
- Ensure SSH/RDP hosts are reachable
- Check firewall rules
- Verify credentials

### Agent Issues
- Ensure agent is running on remote host
- Check agent port (9876) is accessible
- Verify psutil is installed on remote host

### WebSocket Issues
- Ensure browser supports WebSocket
- Check for proxy/firewall blocking WebSocket connections

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for details.

## License

See LICENSE file for details.
