document.addEventListener('DOMContentLoaded', () => {
    const candidateForm = document.getElementById('addCandidateForm');
    const interviewerForm = document.getElementById('addInterviewerForm');
    const messageSection = document.getElementById('messageSection');

    candidateForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const name = document.getElementById('candidateName').value;
        const slots = document.getElementById('candidateSlots').value;
        showMessage(`Candidate ${name} added with slots: ${slots}`);
    });

    interviewerForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const name = document.getElementById('interviewerName').value;
        const slots = document.getElementById('interviewerSlots').value;
        showMessage(`Interviewer ${name} added with slots: ${slots}`);
    });

    function showMessage(message) {
        messageSection.innerHTML = `<p>${message}</p>`;
        setTimeout(() => {
            messageSection.innerHTML = '';
        }, 5000);
    }
});
