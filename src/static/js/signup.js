/* global lucide, grecaptcha */

// Constants
const RECAPTCHA_SITE_KEY = '6LdKgI8qAAAAAFCPWoutXxb3bRw2CdEAzRHnYP5P';

// Utility functions
function setButtonLoading(button, isLoading) {
    const text = button.querySelector('span');
    const originalText = text.textContent;

    if (isLoading) {
        text.textContent = 'Creating account...';
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
    if (!errorDiv) return;
    const errorText = errorDiv.querySelector('p');
    if (errorText) {
        errorText.textContent = message;
        errorDiv.classList.remove('hidden');
    }
}

// reCAPTCHA handling
let recaptchaToken = null;

async function refreshRecaptcha() {
    if (typeof grecaptcha === 'undefined') {
        console.error('reCAPTCHA not loaded');
        return null;
    }

    try {
        const token = await grecaptcha.execute(RECAPTCHA_SITE_KEY, { action: 'signup' });
        recaptchaToken = token;
        return token;
    } catch (error) {
        console.error('reCAPTCHA error:', error);
        return null;
    }
}

window.onRecaptchaLoad = async function () {
    if (typeof grecaptcha === 'undefined') {
        console.error('reCAPTCHA not loaded');
        return;
    }

    await grecaptcha.ready(async function () {
        await refreshRecaptcha();
        // Refresh token every 110 seconds (tokens expire after 120 seconds)
        setInterval(refreshRecaptcha, 110000);
    });
};

document.addEventListener('DOMContentLoaded', function () {
    // Password visibility toggle
    document.querySelectorAll('.toggle-password').forEach((button) => {
        button.addEventListener('click', function () {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            if (!input || !icon) return;

            input.type = input.type === 'password' ? 'text' : 'password';
            icon.setAttribute('data-lucide', input.type === 'password' ? 'eye' : 'eye-off');
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        });
    });

    // Password strength checker
    function checkPasswordStrength(password) {
        if (!password) return { strength: 0, hints: ['Password is required'] };

        let strength = 0;
        let hints = [];

        if (password.length >= 8) {
            strength += 25;
        } else {
            hints.push('Use at least 8 characters');
        }

        if (password.match(/[A-Z]/)) {
            strength += 25;
        } else {
            hints.push('Add uppercase letters');
        }

        if (password.match(/[0-9]/)) {
            strength += 25;
        } else {
            hints.push('Add numbers');
        }

        if (password.match(/[^A-Za-z0-9]/)) {
            strength += 25;
        } else {
            hints.push('Add special characters');
        }

        return { strength, hints };
    }

    const form = document.getElementById('signupForm');
    if (!form) return;

    const passwordInput = document.getElementById('password');
    const meter = document.getElementById('strengthMeter');
    const hint = document.getElementById('passwordHint');
    const submitButton = form.querySelector('button[type="submit"]');

    if (passwordInput && meter && hint) {
        passwordInput.addEventListener('input', function () {
            const { strength, hints } = checkPasswordStrength(this.value);

            meter.style.width = `${strength}%`;
            meter.style.backgroundColor =
                strength <= 25
                    ? '#ef4444'
                    : strength <= 50
                      ? '#f97316'
                      : strength <= 75
                        ? '#eab308'
                        : '#22c55e';

            hint.textContent = hints.join(' • ');
        });
    }

    // Form validation
    function validateForm() {
        const password = passwordInput?.value || '';
        const confirmPassword = document.getElementById('confirmPassword')?.value || '';
        const name = document.getElementById('name')?.value || '';
        const email = document.getElementById('email')?.value || '';
        const { strength } = checkPasswordStrength(password);

        let isValid = true;
        let errorMessage = '';

        if (!name || !email || !password || !confirmPassword) {
            isValid = false;
            errorMessage = 'Please fill in all required fields';
        } else if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        } else if (strength < 75) {
            isValid = false;
            errorMessage = 'Please create a stronger password';
        } else if (password !== confirmPassword) {
            isValid = false;
            errorMessage = 'Passwords do not match';
        }

        if (!isValid) {
            showError('#signupForm', errorMessage);
        } else {
            const errorDiv = document.getElementById('errorMessage');
            if (errorDiv) errorDiv.classList.add('hidden');
        }

        if (submitButton) {
            submitButton.disabled = !isValid;
        }
        return isValid;
    }

    // Validate on input
    form.querySelectorAll('input').forEach((input) => {
        input.addEventListener('input', validateForm);
    });

    // Handle form submission
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (!validateForm() || !submitButton) return;

        // Get a fresh token right before submission
        const token = await refreshRecaptcha();
        if (!token) {
            showError(
                '#signupForm',
                'Unable to verify reCAPTCHA. Please refresh the page and try again.'
            );
            return;
        }

        const originalText = setButtonLoading(submitButton, true);

        try {
            const formData = {
                name: document.getElementById('name')?.value.trim(),
                email: document.getElementById('email')?.value.trim(),
                password: passwordInput?.value,
                password_confirmation: document.getElementById('confirmPassword')?.value,
                org: document.getElementById('organization')?.value.trim() || null,
                recaptcha_token: token,
            };

            // Validate all required fields are present
            if (
                !formData.name ||
                !formData.email ||
                !formData.password ||
                !formData.password_confirmation
            ) {
                throw new Error('Missing required fields');
            }

            const response = await fetch('/api/accounts/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Accept: 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'An error occurred during signup');
            }

            const data = await response.json();

            if (data.status === 'success') {
                window.location.href = escape('/login');
            } else {
                throw new Error(data.message || 'Signup failed');
            }
        } catch (error) {
            showError('#signupForm', error.message);
        } finally {
            setButtonLoading(submitButton, false);
        }
    });
});
