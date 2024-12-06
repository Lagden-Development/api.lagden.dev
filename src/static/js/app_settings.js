/* global lucide, toastr, $ */

let userData = null;

async function fetchUserData() {
    try {
        const response = await $.ajax({
            url: '/api/me',
            method: 'GET',
            dataType: 'json'
        });

        if (response.status === 'success') {
            userData = response.data;
            loadUserData();
        } else {
            toastr.error('Failed to fetch user data');
        }
    } catch (error) {
        console.error('Error fetching user data:', error);
        toastr.error('Failed to fetch user data');
    }
}

function loadUserData() {
    // Update profile information
    document.getElementById('currentName').textContent = userData.name;
    document.getElementById('currentOrg').textContent = userData.organization;
    document.getElementById('nameInput').value = userData.name;
    document.getElementById('orgInput').value = userData.organization;

    // Load emails
    loadEmails();

    // Load sessions
    loadSessions();

    // Initialize Lucide icons
    lucide.createIcons();
}

function loadEmails() {
    const emailList = document.getElementById('emailList');
    emailList.innerHTML = '';

    userData.emails.forEach(email => {
        const emailDiv = document.createElement('div');
        emailDiv.className = 'flex items-center justify-between py-4 border-b border-white/5 last:border-0';
        emailDiv.innerHTML = `
            <div>
                <div class="flex items-center space-x-2">
                    <span class="font-medium">${email.address}</span>
                    ${email.primary ? '<span class="text-xs bg-violet-500/10 text-violet-300 px-2 py-1 rounded">Primary</span>' : ''}
                    ${email.verified ? '<span class="text-xs bg-emerald-500/10 text-emerald-300 px-2 py-1 rounded">Verified</span>' : '<span class="text-xs bg-rose-500/10 text-rose-300 px-2 py-1 rounded">Unverified</span>'}
                </div>
            </div>
            <div class="flex items-center space-x-4">
                ${!email.primary ? `
                    <button onclick="setPrimaryEmail('${email.address}')" class="text-sm text-violet-400 hover:text-violet-300 transition-colors">
                        Make Primary
                    </button>
                    <button onclick="removeEmail('${email.address}')" class="text-sm text-rose-400 hover:text-rose-300 transition-colors">
                        Remove
                    </button>
                ` : ''}
            </div>
        `;
        emailList.appendChild(emailDiv);
    });
}

function loadSessions() {
    const sessionsTable = document.getElementById('sessionsTable');
    sessionsTable.innerHTML = '';

    userData.sessions.forEach(session => {
        const row = document.createElement('tr');
        row.className = 'border-b border-white/5 last:border-0';
        
        // Add a subtle background to the current session
        if (session.current) {
            row.classList.add('bg-violet-500/5');
        }

        row.innerHTML = `
            <td class="py-4 px-6">
                <div class="flex items-center space-x-2">
                    <span class="text-sm">${session.ip}</span>
                    ${session.current ? '<span class="text-xs bg-violet-500/10 text-violet-300 px-2 py-1 rounded">Current Session</span>' : ''}
                </div>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm text-zinc-400">${formatDate(session.last_used)}</span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm text-zinc-400">${formatDate(session.created_at)}</span>
            </td>
            <td class="py-4 px-6 text-right">
                <button onclick="deleteSession('${session._id}')" 
                        class="text-rose-400 hover:text-rose-300 transition-colors ${session.current ? 'opacity-50 cursor-not-allowed' : ''}" 
                        ${session.current ? 'disabled' : ''}>
                    <i data-lucide="trash-2" class="w-5 h-5"></i>
                </button>
            </td>
        `;
        sessionsTable.appendChild(row);
    });

    lucide.createIcons();
}

function formatDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleString();
}

// Name editing functions
function toggleNameEdit() {
    const form = document.getElementById('nameEditForm');
    form.classList.toggle('hidden');
}

/* exported updateName */
async function updateName() {
    const newName = document.getElementById('nameInput').value.trim();
    if (!newName) {
        toastr.error('Name cannot be empty');
        return;
    }

    try {
        const response = await $.ajax({
            url: `/api/me/details/name/${encodeURIComponent(newName)}`,
            method: 'PATCH',
            dataType: 'json'
        });

        if (response.status === 'success') {
            userData.name = newName;
            document.getElementById('currentName').textContent = newName;
            toggleNameEdit();
            toastr.success('Name updated successfully');
        } else {
            toastr.error('Failed to update name');
        }
    } catch (error) {
        console.error('Error updating name:', error);
        toastr.error('Failed to update name');
    }
}

// Organization editing functions
function toggleOrgEdit() {
    const form = document.getElementById('orgEditForm');
    form.classList.toggle('hidden');
}

/* exported updateOrg */
async function updateOrg() {
    const newOrg = document.getElementById('orgInput').value.trim();
    if (!newOrg) {
        toastr.error('Organization name cannot be empty');
        return;
    }

    try {
        const response = await $.ajax({
            url: `/api/me/details/org/${encodeURIComponent(newOrg)}`,
            method: 'PATCH',
            dataType: 'json'
        });

        if (response.status === 'success') {
            userData.organization = newOrg;
            document.getElementById('currentOrg').textContent = newOrg;
            toggleOrgEdit();
            toastr.success('Organization updated successfully');
        } else {
            toastr.error('Failed to update organization');
        }
    } catch (error) {
        console.error('Error updating organization:', error);
        toastr.error('Failed to update organization');
    }
}

// Session management
/* exported deleteSession */
async function deleteSession(sessionId) {
    // Check if trying to delete current session (shouldn't be possible from UI, but adding as safety)
    const session = userData.sessions.find(s => s._id === sessionId);
    if (session?.current) {
        toastr.error('Cannot delete current session');
        return;
    }

    try {
        const response = await $.ajax({
            url: `/api/me/sessions/${sessionId}`,
            method: 'DELETE',
            dataType: 'json'
        });

        if (response.status === 'success') {
            userData.sessions = userData.sessions.filter(session => session._id !== sessionId);
            loadSessions();
            toastr.success('Session deleted successfully');
        } else {
            toastr.error('Failed to delete session');
        }
    } catch (error) {
        console.error('Error deleting session:', error);
        toastr.error('Failed to delete session');
    }
}

/* exported showAddEmailForm, setPrimaryEmail, removeEmail, showChangePasswordForm */

// Placeholder functions for email management UI
function showAddEmailForm() {
    // To be implemented when email management endpoints are available
    toastr.info('Email management coming soon');
}

function setPrimaryEmail(email) {
    // To be implemented when email management endpoints are available
    toastr.info('Email management coming soon');
}

function removeEmail(email) {
    // To be implemented when email management endpoints are available
    toastr.info('Email management coming soon');
}

function showChangePasswordForm() {
    // To be implemented when password management endpoints are available
    toastr.info('Password management coming soon');
}

// Show/hide password fields
/* exported togglePasswordVisibility */
function togglePasswordVisibility(inputId, buttonId) {
    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);
    
    if (input.type === 'password') {
        input.type = 'text';
        button.innerHTML = '<i data-lucide="eye-off" class="w-5 h-5"></i>';
    } else {
        input.type = 'password';
        button.innerHTML = '<i data-lucide="eye" class="w-5 h-5"></i>';
    }
    
    lucide.createIcons();
}

// Confirmation dialog for destructive actions
/* exported confirmAction */
function confirmAction(message, onConfirm) {
    const confirmDialog = document.createElement('div');
    confirmDialog.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
    confirmDialog.innerHTML = `
        <div class="bg-zinc-900 p-6 rounded-lg max-w-md w-full mx-4 card-glow">
            <h3 class="text-lg font-semibold mb-4">${message}</h3>
            <div class="flex justify-end space-x-4">
                <button class="px-4 py-2 text-zinc-400 hover:text-zinc-300 transition-colors" onclick="this.closest('.fixed').remove()">
                    Cancel
                </button>
                <button class="px-4 py-2 bg-rose-500 hover:bg-rose-600 text-white rounded-lg transition-colors confirm-button">
                    Confirm
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(confirmDialog);
    
    confirmDialog.querySelector('.confirm-button').addEventListener('click', () => {
        onConfirm();
        confirmDialog.remove();
    });
}

// Form validation helpers
/* exported validateEmail, validatePassword */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

function validatePassword(password) {
    // Minimum 8 characters, at least one uppercase letter, one lowercase letter, and one number
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
    return re.test(password);
}

// Auto-refresh session data periodically
function startSessionRefresh() {
    setInterval(() => {
        fetchUserData();
    }, 60000); // Refresh every minute
}

// Initialize the settings page
document.addEventListener('DOMContentLoaded', () => {
    // Configure toastr options
    toastr.options = {
        closeButton: true,
        progressBar: true,
        positionClass: "toast-bottom-right",
        timeOut: 3000
    };
    
    fetchUserData();
    startSessionRefresh();
    
    // Add event listeners for form submissions
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // Close any open edit forms when pressing Escape
            document.getElementById('nameEditForm').classList.add('hidden');
            document.getElementById('orgEditForm').classList.add('hidden');
        }
    });
    
    // Initialize form inputs
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    inputs.forEach(input => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const form = input.closest('div');
                const saveButton = form.querySelector('button[class*="bg-violet-500"]');
                if (saveButton) {
                    saveButton.click();
                }
            }
        });
    });
});