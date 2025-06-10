document.addEventListener('DOMContentLoaded', function() {
    const chatList = document.getElementById('chat-list');
    const chatWindow = document.getElementById('chat-window');
    const chatListItems = document.getElementById('chat-list-items');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const backButton = document.getElementById('back-button');

    // Connect to the Socket.IO server
    const socket = io('http://127.0.0.1:5000');

    // Assuming user ID is passed from the server and stored in a global variable
    const sender_id = localStorage.getItem('user_id');  // Retrieve user ID from local storage
    const userRole = localStorage.getItem('user_role'); // Retrieve user role from local storage

    // if (!sender_id || !userRole) {
    //     alert('User not authenticated. Please log in.');
    //     return;
    // }

    // Sample chat data
    const chats = [
        { id: 1, name: "Property 1", lastMessage: "Hello, is this available?", lastSender: "Buyer" },
        { id: 2, name: "Property 2", lastMessage: "What's the final price?", lastSender: "Buyer" },
        { id: 3, name: "Property 3", lastMessage: "I can offer $500,000.", lastSender: "Seller" },
    ];

    // Render chat list
    chats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.classList.add('chat-item');
        chatItem.innerHTML = `
            <h3>${chat.name}</h3>
            <p><strong>${chat.lastSender}:</strong> ${chat.lastMessage}</p>
        `;
        chatItem.addEventListener('click', () => openChat(chat.id));
        chatListItems.appendChild(chatItem);
    });

    // Open chat function
    function openChat(chatId) {
        chatMessages.innerHTML = `
            <div class="message seller">
                You can chat to bargain the property price.
                <span class="timestamp">${getCurrentTimestamp()}</span>
            </div>
        `;

        // Toggle visibility for mobile
        if (window.innerWidth <= 768) {
            chatList.classList.add('active');
            chatWindow.classList.add('active');
        }
    }

    // Back button functionality
    backButton.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            chatWindow.classList.remove('active');
            chatList.classList.remove('active');
        }
    });

    // Function to add a message to the chat window
    function addMessage(message, sender_id, timestamp) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(sender_id == localStorage.getItem('user_id') ? 'buyer' : 'seller');

        messageElement.innerHTML = `
            <p>${message}</p>
            <span class="timestamp">${timestamp}</span>
        `;

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to send a message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            const timestamp = getCurrentTimestamp();

            // Emit message to server
            socket.emit('message', {
                sender_id: sender_id,
                receiver_id: receiver_id, // This should be determined dynamically
                message: message,
                timestamp: timestamp
            });

            // Display message instantly
            addMessage(message, sender_id, timestamp);

            chatInput.value = ''; // Clear input
        }
    }

    // Event listener for the send button
    sendButton.addEventListener('click', sendMessage);

    // Event listener for the Enter key
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Listen for incoming messages from the server
    socket.on('message', function(data) {
        addMessage(data.message, data.sender_id, data.timestamp);
    });

    // Listen for errors from the server
    socket.on('error', function(data) {
        alert(data.error);  // Show error message
    });

    // Request stored messages when the page loads
    socket.emit('request_messages');

    // Function to get current timestamp
    function getCurrentTimestamp() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ', ' + now.toLocaleDateString();
    }
});
