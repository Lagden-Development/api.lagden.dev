/* global lucide, toastr */

// Modal elements
const createKeyModal = document.getElementById('createKeyModal');
const createKeyBtn = document.getElementById('createKeyBtn');
const cancelCreateKey = document.getElementById('cancelCreateKey');
const confirmCreateKey = document.getElementById('confirmCreateKey');
const keyDescription = document.getElementById('keyDescription');

// Modal handlers
createKeyBtn.addEventListener('click', () => {
    createKeyModal.classList.add('active');
    keyDescription.focus();
});

cancelCreateKey.addEventListener('click', () => {
    createKeyModal.classList.remove('active');
    keyDescription.value = '';
});

// Close modal when clicking outside
createKeyModal.addEventListener('click', (e) => {
    if (e.target === createKeyModal) {
        createKeyModal.classList.remove('active');
        keyDescription.value = '';
    }
});

// Create new API key
confirmCreateKey.addEventListener('click', async () => {
    const description = keyDescription.value.trim();
    if (!description) {
        toastr.error('Please provide a description for your API key');
        return;
    }

    try {
        const response = await fetch('/api/me/api-keys', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
        });

        const result = await response.json();

        if (result.status === 'success') {
            createKeyModal.classList.remove('active');
            keyDescription.value = '';
            toastr.success('API key created successfully');
            fetchApiKeys(); // Refresh the list
        } else {
            toastr.error(result.message || 'Failed to create API key');
        }
    } catch (err) {
        console.error(err);
        toastr.error('Failed to create API key');
    }
});

// Format timestamp
function formatDate(timestamp) {
    if (!timestamp) return 'Never';
    // Convert to milliseconds if needed
    const date = new Date(timestamp * 1000);
    // Check if the date is valid
    if (isNaN(date.getTime())) return 'Invalid date';

    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

// Create table row for API key
function createKeyRow(key) {
    return `
        <tr class="border-b border-white/5 fade-in">
            <td class="py-4 px-6">
                <span class="text-sm">${key.description || 'No description'}</span>
            </td>
            <td class="py-4 px-6">
                <div class="flex items-center space-x-2">
                    <span class="font-mono text-sm key-secret">${key._id}</span>
                    <button onclick="toggleKeyVisibility(this)" class="text-zinc-400 hover:text-white transition-colors">
                        <i data-lucide="eye" class="w-4 h-4"></i>
                    </button>
                    <button onclick="copyKey('${key._id}')" class="text-zinc-400 hover:text-white transition-colors">
                        <i data-lucide="copy" class="w-4 h-4"></i>
                    </button>
                </div>
            </td>
            <td class="py-4 px-6">
                <div class="roles-container">
                    ${
                        Array.isArray(key.roles)
                            ? key.roles
                                  .map(
                                      (role) => `
                        <span class="role-badge ${role.toLowerCase()}" title="${getRoleDescription(role)}">
                            ${role}
                        </span>
                    `
                                  )
                                  .join('')
                            : ''
                    }
                </div>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm text-zinc-400">${formatDate(key.created_at)}</span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm text-zinc-400">${formatDate(key.last_used)}</span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm text-zinc-400">${key.uses.toLocaleString()}</span>
            </td>
            <td class="py-4 px-6 text-right">
                <button onclick="deleteKey('${key._id}')" class="text-rose-400 hover:text-rose-300 transition-colors">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            </td>
        </tr>
    `;
}

// Helper function to get role descriptions
function getRoleDescription(role) {
    const descriptions = {
        default: 'Access to all public endpoints',
        cms: 'Access to CMS system endpoints',
        '*': 'Wildcard role with access to all endpoints',
        // Add more role descriptions as needed
    };
    return descriptions[role.toLowerCase()] || role;
}

// Toggle API key visibility
function toggleKeyVisibility(button) {
    const keyElement = button.parentElement.querySelector('.key-secret');
    keyElement.classList.toggle('visible');
    const icon = button.querySelector('i');
    icon.dataset.lucide = keyElement.classList.contains('visible') ? 'eye-off' : 'eye';
    lucide.createIcons();
}

// Copy API key to clipboard
async function copyKey(key) {
    try {
        await navigator.clipboard.writeText(key);
        toastr.success('API key copied to clipboard');
    } catch (err) {
        console.error(err);
        toastr.error('Failed to copy API key');
    }
}

// Delete API key
async function deleteKey(keyId) {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/me/api-keys/${keyId}`, {
            method: 'DELETE',
        });

        const result = await response.json();

        if (result.status === 'success') {
            toastr.success('API key deleted successfully');
            fetchApiKeys(); // Refresh the list
        } else {
            toastr.error(result.message || 'Failed to delete API key');
        }
    } catch (err) {
        console.error(err);
        toastr.error('Failed to delete API key');
    }
}

// Fetch and display API keys
async function fetchApiKeys() {
    const tableBody = document.getElementById('apiKeysTableBody');

    try {
        const response = await fetch('/api/me/api-keys');
        const result = await response.json();

        if (result.status === 'success' && Array.isArray(result.data)) {
            if (result.data.length > 0) {
                tableBody.innerHTML = result.data.map(createKeyRow).join('');
            } else {
                tableBody.innerHTML = `
                    <tr class="border-b border-white/5">
                        <td colspan="7" class="py-8 px-6 text-center text-zinc-400">
                            No API keys found. Create one to get started.
                        </td>
                    </tr>
                `;
            }
        } else {
            toastr.error('Invalid response format');
        }
    } catch (err) {
        console.error(err);
        toastr.error('Failed to fetch API keys');
    }

    // Initialize icons
    lucide.createIcons();

    // Show all elements with fade-in animation
    setTimeout(() => {
        document.querySelectorAll('.fade-in').forEach((el) => el.classList.add('visible'));
    }, 100);
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    fetchApiKeys();
});
