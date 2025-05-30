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

    // Function to handle scroll events
    window.addEventListener('scroll', function() {
        var header = document.getElementById('header');
        var scrolledClass = 'scrolled';
        var heroLoginBtn = document.querySelector('.hero .btn.login');
        var headerLoginBtn = document.querySelector('.header-content .login-btn');

        if (window.scrollY > 50) {
            header.classList.add(scrolledClass);

            // Move login button to header if it doesn't already exist there
            if (!headerLoginBtn) {
                var newLoginBtn = heroLoginBtn.cloneNode(true);
                newLoginBtn.classList.add('login-btn');
                document.querySelector('.header-content').appendChild(newLoginBtn);
            }

            // Hide the login button in the hero section
            heroLoginBtn.style.display = 'none';
        } else {
            header.classList.remove(scrolledClass);

            // Remove login button from header
            if (headerLoginBtn) {
                headerLoginBtn.remove();
            }

            // Show the login button in the hero section
            heroLoginBtn.style.display = 'block';
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

    // Job categories scroll functionality
    const leftButton = document.querySelector('.left-btn');
    const rightButton = document.querySelector('.right-btn');
    const categoriesGrid = document.querySelector('.categories-grid');

    leftButton.addEventListener('click', function() {
        categoriesGrid.scrollBy({
            left: -300,
            behavior: 'smooth'
        });
    });

    rightButton.addEventListener('click', function() {
        categoriesGrid.scrollBy({
            left: 300,
            behavior: 'smooth'
        });
    });
});
