// Agent Dashboard JavaScript

let currentAgentId = null;

// Show Deploy Agent Modal
function showDeployAgentModal() {
    showModal('deployAgentModal');
    loadConnections();
}

// Load connections for deployment
async function loadConnections() {
    const connectionType = document.getElementById('connectionType').value;
    const connectionSelect = document.getElementById('connectionName');
    
    try {
        const connections = await apiRequest(`/connections/api/${connectionType}`);
        
        // Clear existing options
        connectionSelect.innerHTML = '<option value="">Select a connection...</option>';
        
        // Add connections
        Object.keys(connections).forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            connectionSelect.appendChild(option);
        });
    } catch (error) {
        showNotification('Failed to load connections', 'error');
    }
}

// View Metrics
async function viewMetrics(agentId) {
    currentAgentId = agentId;
    showModal('metricsModal');
    
    // Load metrics
    await updateMetrics();
    
    // Auto-refresh metrics every 5 seconds
    const refreshInterval = setInterval(async () => {
        if (document.getElementById('metricsModal').style.display === 'none') {
            clearInterval(refreshInterval);
            return;
        }
        await updateMetrics();
    }, 5000);
}

// Update metrics display
async function updateMetrics() {
    if (!currentAgentId) return;
    
    try {
        const metrics = await apiRequest(`/agent/api/${currentAgentId}/metrics`);
        
        // Update CPU
        document.getElementById('cpuPercent').textContent = `${metrics.cpu_percent.toFixed(1)}%`;
        document.getElementById('cpuBar').style.width = `${metrics.cpu_percent}%`;
        
        // Update Memory
        document.getElementById('memoryPercent').textContent = `${metrics.memory.percent.toFixed(1)}%`;
        document.getElementById('memoryBar').style.width = `${metrics.memory.percent}%`;
        
        // Update Disk
        document.getElementById('diskPercent').textContent = `${metrics.disk.percent.toFixed(1)}%`;
        document.getElementById('diskBar').style.width = `${metrics.disk.percent}%`;
        
        // Color bars based on usage
        const cpuBar = document.getElementById('cpuBar');
        const memoryBar = document.getElementById('memoryBar');
        const diskBar = document.getElementById('diskBar');
        
        [cpuBar, memoryBar, diskBar].forEach(bar => {
            const percent = parseFloat(bar.style.width);
            if (percent > 80) {
                bar.style.background = 'linear-gradient(90deg, #f44336, #d32f2f)';
            } else if (percent > 60) {
                bar.style.background = 'linear-gradient(90deg, #ff9800, #f57c00)';
            } else {
                bar.style.background = 'linear-gradient(90deg, #4caf50, #00bcd4)';
            }
        });
    } catch (error) {
        showNotification('Failed to load metrics', 'error');
    }
}

// Browse Files
async function browseFiles(agentId, path = '/') {
    currentAgentId = agentId;
    showModal('filesModal');
    
    try {
        const data = await apiRequest(`/agent/api/${agentId}/files?path=${encodeURIComponent(path)}`);
        
        // Update current path
        document.getElementById('currentPath').textContent = data.path;
        
        // Update file list
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';
        
        data.files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                ${file.type === 'directory' ? '📁' : '📄'} ${file.name}
                <span style="float: right; color: #888;">${formatFileSize(file.size)}</span>
            `;
            
            if (file.type === 'directory') {
                fileItem.onclick = () => browseFiles(agentId, `${data.path}/${file.name}`.replace('//', '/'));
            }
            
            fileList.appendChild(fileItem);
        });
    } catch (error) {
        showNotification('Failed to load files', 'error');
    }
}

// View Processes
async function viewProcesses(agentId) {
    currentAgentId = agentId;
    showModal('processesModal');
    
    try {
        const processes = await apiRequest(`/agent/api/${agentId}/processes`);
        
        const tableBody = document.getElementById('processTableBody');
        tableBody.innerHTML = '';
        
        processes.forEach(proc => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${proc.pid}</td>
                <td>${proc.name}</td>
                <td>${proc.cpu_percent ? proc.cpu_percent.toFixed(1) : '0.0'}%</td>
                <td>${proc.memory_percent ? proc.memory_percent.toFixed(1) : '0.0'}%</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        showNotification('Failed to load processes', 'error');
    }
}

// Remove Agent
async function removeAgent(agentId) {
    if (!confirm('Are you sure you want to remove this agent?')) {
        return;
    }
    
    try {
        await apiRequest(`/agent/api/${agentId}`, {
            method: 'DELETE'
        });
        
        showNotification('Agent removed successfully', 'success');
        
        // Reload page after a short delay
        setTimeout(() => {
            location.reload();
        }, 1000);
    } catch (error) {
        // Error already shown by apiRequest
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Handle Deploy Agent Form
document.addEventListener('DOMContentLoaded', function() {
    const deployAgentForm = document.getElementById('deployAgentForm');
    if (deployAgentForm) {
        deployAgentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(deployAgentForm);
            
            const data = {
                connection_type: formData.get('connection_type'),
                connection_name: formData.get('connection_name')
            };
            
            try {
                await apiRequest('/agent/api/deploy', {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
                
                showNotification('Agent deployment initiated', 'success');
                closeModal('deployAgentModal');
                
                // Reload page after a short delay
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } catch (error) {
                // Error already shown by apiRequest
            }
        });
    }
});
