"""
SSH Manager Agent
Deployable agent for remote monitoring and management
"""
import os
import sys
import json
import time
import socket
import psutil
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

AGENT_VERSION = "1.0.0"
AGENT_PORT = 9876

class AgentHandler(BaseHTTPRequestHandler):
    """HTTP handler for agent API"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_json_response({'status': 'ok', 'version': AGENT_VERSION})
        elif self.path == '/metrics':
            self.send_json_response(self.get_system_metrics())
        elif self.path.startswith('/files'):
            path = self.path.replace('/files?path=', '') or '/'
            self.send_json_response(self.list_files(path))
        elif self.path == '/processes':
            self.send_json_response(self.list_processes())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        if self.path == '/execute':
            try:
                data = json.loads(body)
                command = data.get('command')
                result = self.execute_command(command)
                self.send_json_response(result)
            except Exception as e:
                self.send_json_response({'error': str(e)}, status=500)
        else:
            self.send_error(404)
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Override to control logging"""
        pass
    
    def get_system_metrics(self):
        """Get system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'uptime': time.time() - psutil.boot_time()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def list_files(self, path='/'):
        """List files in directory"""
        try:
            if not os.path.exists(path):
                return {'error': 'Path not found'}
            
            files = []
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                try:
                    stat = os.stat(full_path)
                    files.append({
                        'name': entry,
                        'type': 'directory' if os.path.isdir(full_path) else 'file',
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
                except:
                    pass
            
            return {'path': path, 'files': files}
        except Exception as e:
            return {'error': str(e)}
    
    def list_processes(self):
        """List running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'username': proc.info['username'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent'],
                        'status': proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {'processes': processes}
        except Exception as e:
            return {'error': str(e)}
    
    def execute_command(self, command):
        """Execute shell command (dangerous - should be restricted)"""
        # For security, this should be heavily restricted in production
        return {'error': 'Command execution disabled for security'}

def main():
    """Main agent function"""
    print(f"SSH Manager Agent v{AGENT_VERSION}")
    print(f"Starting agent on port {AGENT_PORT}...")
    
    try:
        server = HTTPServer(('0.0.0.0', AGENT_PORT), AgentHandler)
        print(f"Agent running on http://0.0.0.0:{AGENT_PORT}")
        print("Press Ctrl+C to stop")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down agent...")
        server.shutdown()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
