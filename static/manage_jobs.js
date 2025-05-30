document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('searchButton');
    const postJobButton = document.getElementById('postJobButton');

    searchButton.addEventListener('click', () => {
        alert('Search CVs across all jobs clicked!');
    });

    postJobButton.addEventListener('click', () => {
        alert('Post a job clicked!');
    });

    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            document.querySelector('.tab-button.active').classList.remove('active');
            button.classList.add('active');
        });
    });
});
