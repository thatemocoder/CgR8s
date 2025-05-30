document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const otpLoginForm = document.getElementById('otp-login');
    const emailPhoneInput = document.getElementById('otp-email-phone');
    const sendOtpButton = document.getElementById('send-otp');
    const otpGroup = document.getElementById('otp-group');
    const otpCodeInput = document.getElementById('otp-code');
    const verifyOtpButton = document.getElementById('verify-otp');
    const loginOtpLink = document.querySelector('.login-otp');
    const loginPasswordLink = document.getElementById('login-password');
    const togglePasswordIcons = document.querySelectorAll('.toggle-password');
    const registerBtn = document.querySelector('.register-btn');
    const registerLink = document.querySelector('.register-link a');

    // Toggle password visibility
    function togglePasswordVisibility(e) {
        const passwordInput = e.target.previousElementSibling;
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            e.target.classList.remove('fa-eye-slash');
            e.target.classList.add('fa-eye');
        } else {
            passwordInput.type = 'password';
            e.target.classList.remove('fa-eye');
            e.target.classList.add('fa-eye-slash');
        }
    }

    togglePasswordIcons.forEach(icon => {
        icon.addEventListener('click', togglePasswordVisibility);
    });

    // Handle form submission for login
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
    
        fetch('login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, password: password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Login Successful");
                window.location.href = 'job_search';  // Redirect to job_search.html
            } else {
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    // Send OTP
    sendOtpButton.addEventListener('click', function(e) {
        e.preventDefault();
        const emailPhone = emailPhoneInput.value;
        fetch('send_otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email_phone: emailPhone })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                sendOtpButton.style.display = 'none';
                otpGroup.style.display = 'block';
                verifyOtpButton.style.display = 'block';
            } else {
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    // Verify OTP
    otpLoginForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const emailPhone = emailPhoneInput.value;
        const otpCode = otpCodeInput.value;

        fetch('verify_otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email_phone: emailPhone, otp: otpCode })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Login Successful");
                window.location.href = '/';
            } else {
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    // Redirect to the registration page on button click
    registerBtn.addEventListener('click', function() {
        window.location.href = 'register';
    });

    // Redirect to the registration page on link click
    registerLink.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = 'register';
    });

    // Social login buttons
    document.querySelectorAll('.social-login button').forEach(button => {
        button.addEventListener('click', function() {
            alert(`${this.textContent.trim()} login would be initiated here.`);
        });
    });

    // // Toggle to OTP login form
    // loginOtpLink.addEventListener('click', (e) => {
    //     e.preventDefault();
    //     loginForm.style.display = 'none';
    //     otpLoginForm.style.display = 'block';
    // });

    // // Toggle back to password login form
    // loginPasswordLink.addEventListener('click', (e) => {
    //     e.preventDefault();
    //     otpLoginForm.style.display = 'none';
    //     loginForm.style.display = 'block';
    // });
});
