// Dashboard JavaScript

// Show Add SSH Modal
function showAddSSHModal() {
    showModal('addSSHModal');
}

// Show Add RDP Modal
function showAddRDPModal() {
    showModal('addRDPModal');
}

// Connect to SSH server
function connectSSH(name) {
    window.location.href = `/terminal/ssh/${name}`;
}

// Edit connection
function editConnection(type, name) {
    // TODO: Implement edit modal
    showNotification(`Edit ${type.toUpperCase()} connection: ${name}`, 'info');
}

// Delete connection
async function deleteConnection(type, name) {
    if (!confirm(`Are you sure you want to delete ${name}?`)) {
        return;
    }
    
    try {
        await apiRequest(`/connections/api/${type}/${name}`, {
            method: 'DELETE'
        });
        
        showNotification(`${type.toUpperCase()} connection ${name} deleted`, 'success');
        
        // Reload page after a short delay
        setTimeout(() => {
            location.reload();
        }, 1000);
    } catch (error) {
        // Error already shown by apiRequest
    }
}

// Handle Add SSH Form
document.addEventListener('DOMContentLoaded', function() {
    const addSSHForm = document.getElementById('addSSHForm');
    if (addSSHForm) {
        addSSHForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(addSSHForm);
            const tags = formData.get('tags');
            
            const data = {
                name: formData.get('name'),
                user: formData.get('user'),
                host: formData.get('host'),
                port: formData.get('port'),
                tags: tags ? tags.split(',').map(t => t.trim()) : [],
                favorite: formData.get('favorite') === 'on'
            };
            
            try {
                await apiRequest('/connections/api/ssh', {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
                
                showNotification('SSH connection added successfully', 'success');
                closeModal('addSSHModal');
                
                // Reload page after a short delay
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } catch (error) {
                // Error already shown by apiRequest
            }
        });
    }
    
    const addRDPForm = document.getElementById('addRDPForm');
    if (addRDPForm) {
        addRDPForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(addRDPForm);
            const tags = formData.get('tags');
            
            const data = {
                name: formData.get('name'),
                user: formData.get('user'),
                host: formData.get('host'),
                port: formData.get('port'),
                mac: formData.get('mac'),
                tags: tags ? tags.split(',').map(t => t.trim()) : [],
                favorite: formData.get('favorite') === 'on'
            };
            
            try {
                await apiRequest('/connections/api/rdp', {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
                
                showNotification('RDP connection added successfully', 'success');
                closeModal('addRDPModal');
                
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
