/* global lucide, toastr, $ */

const dashboardData = {
    user: {
        name: 'Failed to fetch user data',
    },
    stats: {
        totalRequests: 0,
        activeApiKeys: 0,
        latestRequest: {
            time: 'Never',
            endpoint: 'No requests yet',
        },
        requestGrowth: {
            value: 0,
            trend: '',
            isIncrease: true,
            percentage: 0,
        },
    },
    recentRequests: [],
};

async function fetchDashboardData() {
    try {
        // Fetch user data
        const userResponse = await $.ajax({
            url: '/api/me',
            method: 'GET',
            dataType: 'json',
        });

        if (userResponse.status === 'success') {
            dashboardData.user.name = userResponse.data.name;
        } else {
            toastr.error(userResponse.message);
        }

        // Fetch API keys
        const keysResponse = await $.ajax({
            url: '/api/me/api-keys',
            method: 'GET',
            dataType: 'json',
        });

        if (keysResponse.status === 'success') {
            dashboardData.stats.activeApiKeys = keysResponse.data.length;
        } else {
            toastr.error(keysResponse.message);
        }

        // Fetch total API logs count using new endpoint
        const totalLogsResponse = await $.ajax({
            url: '/api/me/total-api-logs',
            method: 'GET',
            dataType: 'json',
        });

        if (totalLogsResponse.status === 'success') {
            const { total, this_month, last_month } = totalLogsResponse.data;
            const difference = this_month - last_month;
            let percentageChange = 0;

            if (last_month === 0 && this_month > 0) {
                // Handle case where last month was 0
                percentageChange = this_month * 100;
            } else if (last_month > 0) {
                // Calculate percentage change when last month wasn't 0
                percentageChange = ((this_month - last_month) / last_month) * 100;
            }

            dashboardData.stats.totalRequests = total;
            dashboardData.stats.requestGrowth = {
                value: Math.abs(difference),
                isIncrease: difference >= 0,
                percentage: Math.abs(Math.round(percentageChange)),
                trend: `${difference >= 0 ? '↑' : '↓'} ${Math.abs(Math.round(percentageChange))}% from last month`,
            };
        } else {
            toastr.error(totalLogsResponse.message);
        }

        // Fetch recent API logs
        const logsResponse = await $.ajax({
            url: '/api/me/recent-api-logs',
            method: 'GET',
            dataType: 'json',
        });

        if (logsResponse.status === 'success') {
            // Update latest request info from the most recent log
            if (logsResponse.data.length > 0) {
                const latestLog = logsResponse.data[0];
                const timeDiff = Math.floor(Date.now() / 1000 - latestLog.timestamp);

                dashboardData.stats.latestRequest = {
                    time: formatTimeDiff(timeDiff),
                    endpoint: latestLog.route,
                };

                // Format recent requests for the table
                dashboardData.recentRequests = logsResponse.data.map((log) => ({
                    endpoint: log.route,
                    method: log.method,
                    status: log.status_code,
                    time: formatTimeDiff(Math.floor(Date.now() / 1000 - log.timestamp)),
                }));
            }
        } else {
            toastr.error(logsResponse.message);
        }
    } catch (err) {
        console.error(err);
        toastr.error('Failed to fetch dashboard data, please try again.');
    }

    // Load the dashboard with fetched data
    loadDashboardData();
}

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

// Helper function to create table row for requests
function createRequestRow(request) {
    const methodColors = {
        GET: 'bg-emerald-500/10 text-emerald-300',
        POST: 'bg-violet-500/10 text-violet-300',
        PUT: 'bg-amber-500/10 text-amber-300',
        DELETE: 'bg-rose-500/10 text-rose-300',
    };

    const statusColor = request.status < 400 ? 'text-emerald-400' : 'text-rose-400';

    return `
        <tr class="border-b border-white/5 fade-in">
            <td class="py-4 px-6">
                <span class="font-mono text-sm">${request.endpoint}</span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm px-2.5 py-1 rounded-full ${methodColors[request.method]}">
                    ${request.method}
                </span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm ${statusColor}">${request.status}</span>
            </td>
            <td class="py-4 px-6">
                <span class="text-sm text-zinc-400">${request.time}</span>
            </td>
        </tr>
    `;
}

// Function to load and display data
function loadDashboardData() {
    // Update name only
    document.querySelector('h1 span.skeleton-loader').outerHTML = dashboardData.user.name;

    // Update stats using IDs
    document.getElementById('totalRequests').outerHTML =
        `<h3 class="text-2xl font-bold">${dashboardData.stats.totalRequests.toLocaleString()}</h3>`;
    document.getElementById('requestGrowth').outerHTML = `<div class="text-sm text-zinc-400">
            <span class="${dashboardData.stats.requestGrowth.isIncrease ? 'text-emerald-400' : 'text-rose-400'}">
                ${dashboardData.stats.requestGrowth.trend}
            </span>
        </div>`;

    document.getElementById('activeKeys').outerHTML =
        `<h3 class="text-2xl font-bold">${dashboardData.stats.activeApiKeys}</h3>`;
    document.getElementById('manageKeys').outerHTML =
        `<a href="/app/api-keys" class="text-sm text-fuchsia-400 hover:text-fuchsia-300 transition-colors">Manage keys →</a>`;

    document.getElementById('latestRequestTime').outerHTML =
        `<h3 class="text-lg font-bold">${dashboardData.stats.latestRequest.time}</h3>`;
    document.getElementById('latestRequestEndpoint').outerHTML =
        `<p class="text-sm text-zinc-400 truncate">${dashboardData.stats.latestRequest.endpoint}</p>`;

    // Update recent requests table
    const tableBody = document.querySelector('#requestsTableBody');
    if (dashboardData.recentRequests.length > 0) {
        tableBody.innerHTML = dashboardData.recentRequests.map(createRequestRow).join('');
    } else {
        tableBody.innerHTML = `
            <tr class="border-b border-white/5">
                <td colspan="4" class="py-8 px-6 text-center text-zinc-400">
                    No recent requests found
                </td>
            </tr>
        `;
    }

    // Show view all link
    document.querySelector('.flex.items-center.justify-between div').outerHTML =
        `<a href="/app/requests" class="text-violet-400 hover:text-violet-300 transition-colors text-sm">View all →</a>`;

    // Reinitialize Lucide icons
    lucide.createIcons();

    // Show all elements with fade-in animation
    setTimeout(() => {
        document.querySelectorAll('.fade-in').forEach((el) => el.classList.add('visible'));
    }, 100);
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();
});
