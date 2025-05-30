document.addEventListener('DOMContentLoaded', function() {
    const formTabs = document.querySelectorAll('.form-tabs button');
    
    formTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            formTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

    document.querySelector('#login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.querySelector('#email').value;
        const password = document.querySelector('#password').value;

        fetch(loginUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, password: password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector('.hero').style.display = 'none';
                document.querySelector('.services').style.display = 'none';
                document.querySelector('.dashboard').style.display = 'block';
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
