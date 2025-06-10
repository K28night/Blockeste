// Theme Toggle Logic
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-theme');
    if (body.classList.contains('dark-theme')) {
        themeToggle.textContent = 'Light Theme';
    } else {
        themeToggle.textContent = 'Dark Theme';
    }
});

// Mock data for total interests and property rating
let totalInterests = 0;
let propertyRating = 4.5; // Default rating

// Update the DOM with initial data
document.getElementById('totalInterests').textContent = totalInterests;
document.getElementById('propertyRating').textContent = propertyRating;

// Handle form submission
document.getElementById('requestForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Get form values
    const userRate = document.getElementById('userRate').value;
    const message = document.getElementById('message').value;

    // Validate user rate
    if (!userRate || isNaN(userRate)) {
        alert('Please enter a valid rate.');
        return;
    }

    // Increment total interests
    totalInterests++;
    document.getElementById('totalInterests').textContent = totalInterests;

    // Display confirmation (you can replace this with an API call)
    alert(`Request submitted!\nYour Rate: $${userRate}\nMessage: ${message}`);

    // Reset form
    document.getElementById('requestForm').reset();

    // Simulate updating the rating (optional)
    propertyRating += 0.1;
    if (propertyRating > 5) propertyRating = 5; // Cap the rating at 5
    document.getElementById('propertyRating').textContent = propertyRating.toFixed(1);
});