/* global, toastr, $ */

// State management
let isLoading = false;
let hasMore = true;
let currentSkip = 0;
const LIMIT = 10;

// Helper function to format time difference (reused from dashboard)
function formatTimeDiff(seconds) {
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
    }
    if (seconds < 86400) {
        const hours = Math.floor(seconds / 3600);
        return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
    }
    const days = Math.floor(seconds / 86400);
    return `${days} ${days === 1 ? 'day' : 'days'} ago`;
}

// Create table row for requests (modified from dashboard)
function createRequestRow(request) {
    const methodColors = {
        GET: 'bg-emerald-500/10 text-emerald-300',
        POST: 'bg-violet-500/10 text-violet-300',
        PUT: 'bg-amber-500/10 text-amber-300',
        DELETE: 'bg-rose-500/10 text-rose-300'
    };

    const statusColor = request.status_code < 400 ? 'text-emerald-400' : 'text-rose-400';
    const timeDiff = Math.floor(Date.now() / 1000 - request.timestamp);

    return `
        <tr class="border-b border-white/5 fade-in">
            <td class="py-4 px-6">
                <span class="font-mono text-sm">${request.route}</span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm px-2.5 py-1 rounded-full ${methodColors[request.method]}">
                    ${request.method}
                </span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm ${statusColor}">${request.status_code}</span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm text-zinc-400">${formatTimeDiff(timeDiff)}</span>
            </td>
        </tr>
    `;
}

// Fetch and append logs
async function fetchLogs() {
    if (isLoading || !hasMore) return;

    try {
        isLoading = true;
        document.getElementById('loadingIndicator').classList.remove('hidden');

        const response = await $.ajax({
            url: `/api/me/all-api-logs/${LIMIT}/${currentSkip}`,
            method: 'GET',
            dataType: 'json'
        });

        if (response.status === 'success') {
            const tableBody = document.getElementById('requestsTableBody');
            
            // Clear skeleton loaders if this is the first load
            if (currentSkip === 0) {
                tableBody.innerHTML = '';
            }

            // Append new rows
            response.data.forEach(log => {
                tableBody.insertAdjacentHTML('beforeend', createRequestRow(log));
            });

            // Update state
            currentSkip += LIMIT;
            
            // Check if we have more items to load
            if (response.data.length < LIMIT) {
                hasMore = false;
                document.getElementById('noMoreRequests').classList.remove('hidden');
            } else {
                // Peek next page to check if there are more items
                const peekResponse = await $.ajax({
                    url: `/api/me/all-api-logs/${LIMIT}/${currentSkip}`,
                    method: 'GET',
                    dataType: 'json'
                });
                
                if (peekResponse.data.length === 0) {
                    hasMore = false;
                    document.getElementById('noMoreRequests').classList.remove('hidden');
                }
            }

            // Show new items with fade-in animation
            setTimeout(() => {
                document.querySelectorAll('.fade-in').forEach(el => el.classList.add('visible'));
            }, 100);
        } else {
            toastr.error(response.message);
        }
    } catch (err) {
        console.error(err);
        toastr.error('Failed to fetch API logs, please try again.');
    } finally {
        isLoading = false;
        document.getElementById('loadingIndicator').classList.add('hidden');
    }
}

// Infinite scroll handler
function handleScroll() {
    if (isLoading || !hasMore) return;

    const scrollPosition = window.innerHeight + window.scrollY;
    const bodyHeight = document.body.offsetHeight;
    const buffer = 200; // Start loading 200px before reaching bottom

    if (bodyHeight - scrollPosition < buffer) {
        fetchLogs();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initial load
    fetchLogs();
    
    // Set up infinite scroll
    window.addEventListener('scroll', handleScroll);
});