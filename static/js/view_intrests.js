// Theme Toggle Logic
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-theme');
    if (body.classList.contains('dark-theme')) {
        themeToggle.textContent = 'Switch to Light Theme';
    } else {
        themeToggle.textContent = 'Switch to Dark Theme';
    }
});

// Handle Accept and Reject Buttons
const acceptButtons = document.querySelectorAll('.accept-btn');
const rejectButtons = document.querySelectorAll('.reject-btn');

acceptButtons.forEach(button => {
    button.addEventListener('click', () => {
        alert('Interest accepted!');
    });
});

rejectButtons.forEach(button => {
    button.addEventListener('click', () => {
        alert('Interest rejected!');
    });
});