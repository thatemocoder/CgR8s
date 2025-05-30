// Add interactivity here
document.querySelectorAll('.quick-apply').forEach(button => {
    button.addEventListener('click', () => {
        alert('Application submitted!');
    });
});



document.addEventListener('DOMContentLoaded', function() {
    var loginBtn = document.querySelector('.btn.login');

    // Toggle hamburger menu
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const navList = document.getElementById('nav-list');
    const logo = document.querySelector('.logo');
    const header = document.getElementById('header');

    hamburgerMenu.addEventListener('click', function() {
        navList.classList.toggle('show');
        if (navList.classList.contains('show')) {
            // Move the logo to the top of the nav list when menu is active
            navList.insertBefore(logo, navList.firstChild);
        } else {
            // Move the logo back to the header when menu is not active
            header.querySelector('.header-content').insertBefore(logo, header.querySelector('nav'));
        }
    });

    // Function to handle resizing of the window
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            // Ensure navList is hidden on larger screens
            navList.classList.remove('show');
        }
    });

    // Highlight the active link based on the current URL
    const currentURL = window.location.href;
    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => {
        if (link.href === currentURL) {
            link.classList.add('active');
        }
    });

    // Functionality to close the hamburger menu when a link is clicked
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navList.classList.remove('show');
            // Move the logo back to the header when menu is closed (if necessary)
            if (!navList.classList.contains('show')) {
                header.querySelector('.header-content').insertBefore(logo, header.querySelector('nav'));
            }
        });
    });
});
