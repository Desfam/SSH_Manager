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

- Always change default credentials
- Use HTTPS in production (configure reverse proxy)
- Set strong SECRET_KEY in production
- Restrict network access to the web interface
- Use SSH keys instead of passwords for SSH connections
- Review agent permissions before deployment

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
