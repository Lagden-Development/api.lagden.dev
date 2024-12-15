/* global lucide, toastr, $ */

// static/js/shared.js

// Initialize toastr options
toastr.options = {
    closeButton: true,
    progressBar: true,
    positionClass: 'toast-bottom-right',
};

// Initialize Lucide icons
lucide.createIcons();

// Utility function for handling error messages
/* exported showError */
function showError(formId, message) {
    const errorDiv = document.querySelector(`${formId} #errorMessage`);
    const errorText = errorDiv.querySelector('p');

    errorDiv.classList.remove('hidden');
    errorDiv.classList.add('shake');
    errorText.textContent = message;

    // Remove shake class after animation
    setTimeout(() => {
        errorDiv.classList.remove('shake');
    }, 500);
}

// Utility function for showing loading state on submit buttons
/* exported setButtonLoading */
function setButtonLoading(button, isLoading) {
    const span = button.querySelector('span');
    const originalText = span.textContent;

    button.disabled = isLoading;

    if (isLoading) {
        span.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 mx-auto animate-spin"></i>';
        lucide.createIcons();
    } else {
        span.textContent = originalText;
    }

    return originalText;
}

// Utility function for handling form submission
/* exported handleLogout */
function handleLogout() {
    $.ajax({
        url: '/api/accounts/logout',
        method: 'POST',
        xhrFields: {
            withCredentials: true, // Include cookies in the request
        },
        success: function (response) {
            console.log(response.message);
            window.location.href = '/';
        },
        error: function (xhr, status, error) {
            const errorMessage = xhr.responseJSON?.detail || 'Logout failed. Please try again.';
            toastr.error(errorMessage, 'Error');
            console.error('Logout error:', error);
        },
    });
}
