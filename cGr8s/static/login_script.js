document.addEventListener('DOMContentLoaded', function () {
    const signUpButton = document.getElementById('signUpButton');
    const signInButton = document.getElementById('signInButton');
    const signUpContainer = document.getElementById('signup');
    const signInContainer = document.getElementById('signIn');
    const loginButton = document.getElementById('login-btn');
    const navLinks = document.querySelector('nav ul');
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const header = document.querySelector('header');

    signUpButton.addEventListener('click', function () {
        signInContainer.style.display = 'none';
        signUpContainer.style.display = 'block';
    });

    signInButton.addEventListener('click', function () {
        signUpContainer.style.display = 'none';
        signInContainer.style.display = 'block';
    });

    loginButton.addEventListener('click', function () {
        signUpContainer.style.display = 'none';
        signInContainer.style.display = 'block';
    });

    hamburgerMenu.addEventListener('click', function () {
        navLinks.classList.toggle('show');
    });

    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
});
