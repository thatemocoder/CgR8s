document.addEventListener('DOMContentLoaded', function() {
    var hamburgerMenu = document.getElementById('hamburger-menu');
    var navList = document.getElementById('nav-list');
    var loginBtn = document.querySelector('.btn.login');

    // Toggle hamburger menu
    hamburgerMenu.addEventListener('click', function() {
        navList.classList.toggle('show');
    });

    // Function to handle resizing of the window
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            nav
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
});
