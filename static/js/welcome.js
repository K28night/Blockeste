
document.getElementById("profileToggle").addEventListener("click", function() {
    let profileSection = document.getElementById("profileSection");
    profileSection.classList.toggle("hidden");
});

document.getElementById("darkModeToggle").addEventListener("click", function() {
    document.body.classList.toggle("bg-gray-900");
    document.body.classList.toggle("text-white");
});


    // Notifications Dropdown
    const notifications = document.getElementById('notifications');
    const notificationsDropdown = document.getElementById('notificationsDropdown');
    notifications.addEventListener('click', () => {
        notificationsDropdown.classList.toggle('hidden');
    });

    // Profile Section Toggle
    const profileToggle = document.getElementById('profileToggle');
    const profileSection = document.getElementById('profileSection');
    profileToggle.addEventListener('click', () => {
        profileSection.classList.toggle('hidden');
    });

    // Property Listing Modal
    const sellRentButton = document.getElementById('sellRentButton');
    const propertyModal = document.getElementById('propertyModal');
    sellRentButton.addEventListener('click', () => {
        propertyModal.classList.toggle('hidden');
    });

    const ctx = document.getElementById('investmentChart').getContext('2d');

const investmentChart = new Chart(ctx, {
    type: 'line', // You can change this to 'bar', 'pie', etc.
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], // X-axis labels
        datasets: [{
            label: 'Investment Growth',
            data: [1000, 1500, 2000, 2500, 3000, 3500], // Y-axis data
            borderColor: '#28ba07',
            backgroundColor: 'rgba(40, 186, 7, 0.2)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    display: true
                }
            }
        }
    }
});
