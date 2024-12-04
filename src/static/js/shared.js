// static/js/shared.js

// Initialize toastr options
toastr.options = {
    closeButton: true,
    progressBar: true,
    positionClass: "toast-bottom-right",
};

// Initialize Lucide icons
lucide.createIcons();

// Utility function for handling error messages
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
