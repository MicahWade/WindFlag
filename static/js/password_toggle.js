document.addEventListener('DOMContentLoaded', function() {
    function setupPasswordToggle(inputId, toggleButtonId) {
        const passwordInput = document.getElementById(inputId);
        const toggleButton = document.getElementById(toggleButtonId);

        if (passwordInput && toggleButton) {
            toggleButton.addEventListener('click', function() {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);

                // Toggle the eye icon
                const icon = toggleButton.querySelector('svg');
                if (type === 'password') {
                    // Eye icon (visible)
                    icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>';
                } else {
                    // Eye-slash icon (hidden)
                    icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7 .96-3.02 3.26-5.31 5.91-6.97M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.257 12.257a4 4 0 114.586 4.586M17.25 12.25a4 4 0 10-4.586-4.586"/>';
                }
            });
        }
    }

    // Setup for login page
    setupPasswordToggle('loginPassword', 'toggleLoginPassword');

    // Setup for registration page
    setupPasswordToggle('registerPassword', 'toggleRegisterPassword');
    setupPasswordToggle('confirmPassword', 'toggleConfirmPassword');
});
