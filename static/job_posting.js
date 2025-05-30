document.getElementById('jobForm').addEventListener('submit', function(event) {
    event.preventDefault();
    alert('Job posted successfully!');
    this.submit();  // Submit the form
});

function postJob() {
    document.getElementById('jobForm').submit();
}

