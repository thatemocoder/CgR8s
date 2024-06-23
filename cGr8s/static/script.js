document.addEventListener('DOMContentLoaded', (event) => {
    const togglePasswordElements = document.querySelectorAll('.toggle-password');

    togglePasswordElements.forEach(togglePassword => {
        togglePassword.addEventListener('click', function () {
            const passwordFieldId = this.getAttribute('data-target');
            const passwordField = document.getElementById(passwordFieldId);

            if (passwordField) {
                const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordField.setAttribute('type', type);

                this.classList.toggle('fa-eye');
                this.classList.toggle('fa-eye-slash');
            }
        });
    });
});