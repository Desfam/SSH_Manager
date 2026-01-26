# SSH & RDP Manager - Quick Start Guide

## Overview

SSH & RDP Manager is now available in two modes:
1. **Terminal Interface** - Original Windows console application
2. **Web Interface** - New browser-based dashboard with agent system

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Desfam/SSH_Manager.git
cd SSH_Manager
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Getting Started

### Using the Web Interface (Recommended)

1. **Start the Web Server**
   ```bash
   python start_web_server.py
   ```

2. **Access the Dashboard**
   - Open your browser and navigate to: http://localhost:5000
   - Login with default credentials:
     - Username: `admin`
     - Password: `admin`
   - **Important:** Change the password immediately after first login!

3. **Add Connections**
   - Click "Add SSH" or "Add RDP" on the dashboard
   - Fill in the connection details:
     - Name: A friendly name for the connection
     - User: SSH/RDP username
     - Host: IP address or hostname
     - Port: 22 (SSH) or 3389 (RDP)
     - Tags: Optional tags for organization
     - Favorite: Mark as favorite for quick access

4. **Connect to SSH Server**
   - Click "Connect" on any SSH connection
   - A web-based terminal will open
   - You can type commands just like a regular SSH session

5. **Deploy an Agent**
   - Go to the "Agents" page
   - Click "Deploy Agent"
   - Select a connection
   - The agent will be deployed (note: manual installation may be required)

6. **Monitor with Agent**
   - Once an agent is deployed, you can:
     - View performance metrics (CPU, memory, disk)
     - Browse files on the remote system
     - View running processes
     - Monitor system health in real-time

### Using the Terminal Interface (Windows Only)

1. **Start the Application**
   ```bash
   python Manager_file/main.py
   ```

2. **Navigate the Menu**
   - Use number keys to select options
   - Follow the prompts for each action

## Features Comparison

| Feature | Terminal Interface | Web Interface |
|---------|-------------------|---------------|
| SSH Connection | ✓ (via SSH client) | ✓ (in-browser) |
| RDP Connection | ✓ (via mstsc.exe) | ✗ (display only) |
| File Transfer | ✓ (SCP) | ✗ (view only) |
| Agent Deployment | ✗ | ✓ |
| Performance Monitoring | Basic | Advanced |
| File Browser | ✗ | ✓ |
| Process Viewer | Basic | Advanced |
| Multi-user | ✗ | ✓ |
| Remote Access | ✗ | ✓ |
| Platform | Windows only | Cross-platform |

## Agent Deployment Guide

### Automatic Deployment (Coming Soon)
The web interface will automatically deploy agents via SSH.

### Manual Deployment

1. **Download the Agent**
   - In the web interface, go to Agents → Deploy Agent
   - Download the agent script

2. **Copy to Remote Host**
   ```bash
   scp agent.py user@host:/opt/ssh_manager/
   ```

3. **Install Dependencies**
   ```bash
   ssh user@host
   pip install psutil
   ```

4. **Run the Agent**
   ```bash
   python /opt/ssh_manager/agent.py
   ```

5. **Configure Firewall (if needed)**
   ```bash
   # Allow agent port
   sudo ufw allow 9876/tcp
   ```

6. **Run as Service (Optional)**
   Create a systemd service:
   ```bash
   sudo nano /etc/systemd/system/ssh-manager-agent.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=SSH Manager Agent
   After=network.target

   [Service]
   Type=simple
   User=your-user
   ExecStart=/usr/bin/python3 /opt/ssh_manager/agent.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start:
   ```bash
   sudo systemctl enable ssh-manager-agent
   sudo systemctl start ssh-manager-agent
   ```

## Configuration

### Web Server Configuration

Environment variables:
- `PORT` - Server port (default: 5000)
- `HOST` - Server host (default: 0.0.0.0)
- `DEBUG` - Debug mode (default: False)
- `SECRET_KEY` - Flask secret key (required for production)

Example:
```bash
export SECRET_KEY="your-random-secret-key-here"
export PORT=8080
python start_web_server.py
```

### Connection Configuration

All connections are stored in: `~/.ssh_manager.json`

Example format:
```json
{
  "ssh": {
    "server1": {
      "user": "root",
      "host": "10.0.0.10",
      "port": "22",
      "tags": ["production", "web"],
      "favorite": true
    }
  },
  "rdp": {
    "workstation1": {
      "user": "DOMAIN\\Admin",
      "host": "10.0.0.50",
      "port": "3389",
      "mac": "AA:BB:CC:DD:EE:FF",
      "tags": ["windows"],
      "favorite": false
    }
  }
}
```

## Security Best Practices

1. **Change Default Password**
   - Immediately change the default admin password
   - Use a strong, unique password

2. **Use SSH Keys**
   - Prefer SSH keys over passwords
   - Use the built-in SSH key setup feature

3. **Secure the Web Interface**
   - Use HTTPS in production (configure reverse proxy)
   - Restrict access to trusted networks
   - Set a strong SECRET_KEY

4. **Agent Security**
   - Only deploy agents on trusted hosts
   - Review agent permissions
   - Use firewall rules to restrict agent access

5. **Regular Updates**
   - Keep dependencies updated
   - Monitor security advisories

## Troubleshooting

### Web Server Won't Start

**Problem:** Server fails to start
**Solution:** 
- Check if port 5000 is already in use
- Verify all dependencies are installed
- Check logs for error messages

### Can't Connect to SSH Server

**Problem:** SSH connection fails
**Solution:**
- Verify host is reachable (ping test)
- Check SSH port (default 22)
- Verify credentials
- Check SSH key configuration

### Agent Not Responding

**Problem:** Agent shows as offline
**Solution:**
- Verify agent is running on remote host
- Check firewall rules (port 9876)
- Verify network connectivity
- Check agent logs

### WebSocket Connection Failed

**Problem:** SSH terminal doesn't work
**Solution:**
- Check browser WebSocket support
- Verify no proxy is blocking WebSocket
- Check browser console for errors

## Advanced Usage

### Running on Custom Port
```bash
PORT=8080 python start_web_server.py
```

### Running with HTTPS (Production)
Use a reverse proxy like Nginx:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Multi-User Setup
- Each user should have their own account
- Create users through the web interface (coming soon)
- Currently, all users share the same connection pool

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/Desfam/SSH_Manager/issues
- Documentation: See README.md and web_server/README.md

## License

See LICENSE file for details.
