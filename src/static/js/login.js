// Helper functions for UI manipulation
function setButtonLoading(button, isLoading) {
    const text = button.querySelector('span');
    const originalText = text.textContent;

    if (isLoading) {
        text.textContent = 'Signing in...';
        button.disabled = true;
        button.classList.add('opacity-75', 'cursor-not-allowed');
    } else {
        text.textContent = originalText;
        button.disabled = false;
        button.classList.remove('opacity-75', 'cursor-not-allowed');
    }

    return originalText;
}

function showError(formSelector, message) {
    const errorDiv = document.querySelector(`${formSelector} #errorMessage`);
    const errorText = errorDiv.querySelector('p');
    errorText.textContent = message;
    errorDiv.classList.remove('hidden');
}

// Initialize reCAPTCHA
let recaptchaToken = null;
window.onRecaptchaLoad = function () {
    grecaptcha.ready(function () {
        grecaptcha
            .execute('6LdKgI8qAAAAAFCPWoutXxb3bRw2CdEAzRHnYP5P', { action: 'login' })
            .then(function (token) {
                recaptchaToken = token;
            });
    });
};

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    const submitButton = form.querySelector('button[type="submit"]');

    // Password visibility toggle
    const togglePassword = document.getElementById('togglePassword');
    if (togglePassword) {
        togglePassword.addEventListener('click', function () {
            const input = document.getElementById('password');
            const icon = this.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.setAttribute('data-lucide', 'eye-off');
            } else {
                input.type = 'password';
                icon.setAttribute('data-lucide', 'eye');
            }
            lucide.createIcons();
        });
    }

    // Form validation and submission
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;

        // Basic validation
        if (!email || !password) {
            showError('#loginForm', 'Please fill in all fields');
            return;
        }

        if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
            showError('#loginForm', 'Please enter a valid email address');
            return;
        }

        // Set loading state
        const originalText = setButtonLoading(submitButton, true);

        try {
            const response = await fetch('/api/accounts/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // This ensures cookies are sent and received
                body: JSON.stringify({
                    email,
                    password,
                    remember,
                    recaptcha_token: recaptchaToken,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred during login');
            }

            // On successful login, redirect to dashboard
            if (data.status === 'success') {
                window.location.href = '/app';
            } else {
                throw new Error(data.message || 'Login failed');
            }
        } catch (error) {
            showError('#loginForm', error.message);
            // Refresh reCAPTCHA token
            if (window.grecaptcha) {
                grecaptcha
                    .execute('6LdKgI8qAAAAAFCPWoutXxb3bRw2CdEAzRHnYP5P', { action: 'login' })
                    .then(function (token) {
                        recaptchaToken = token;
                    });
            }
        } finally {
            setButtonLoading(submitButton, false);
        }
    });

    // Reset error message when input changes
    form.querySelectorAll('input').forEach((input) => {
        input.addEventListener('input', function () {
            const errorDiv = document.getElementById('errorMessage');
            if (!errorDiv.classList.contains('hidden')) {
                errorDiv.classList.add('hidden');
            }
        });
    });
});
