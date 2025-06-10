// Fetch real-time ETH price from Flask backend
function fetchEthPrice() {
    fetch("/get_eth_price")
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            if (data.eth_price) {
                // Update the displayed ETH price
                document.getElementById("real-time-eth-price").textContent = data.eth_price;
                console.log("ETH price updated:", data.eth_price); // Log for debugging
                // Update the ETH amount based on the current input
                updateETHAmount();
            } else {
                console.error("Error fetching ETH price:", data.error);
                document.getElementById("real-time-eth-price").textContent = "Error";
            }
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById("real-time-eth-price").textContent = "Error";
        });
}

// Convert INR to ETH using the formula: ETH = INR / Exchange Rate
function updateETHAmount() {
    const amount = parseFloat(document.getElementById("amount").value);
    const exchangeRate = parseFloat(document.getElementById("real-time-eth-price").textContent);

    // Check if both amount and exchange rate are valid numbers
    if (!isNaN(amount) && amount > 0 && !isNaN(exchangeRate) && exchangeRate > 0) {
        const ethAmount = amount / exchangeRate; // ETH = INR / Exchange Rate
        document.getElementById("eth-amount").textContent = ethAmount.toFixed(6) + " ETH";
    } else {
        document.getElementById("eth-amount").textContent = "0 ETH";
    }
}

// Handle UPI Payment
document.getElementById("pay-button").addEventListener("click", () => {
    const amount = parseFloat(document.getElementById("amount").value);
    const walletAddress = document.getElementById("wallet-address").value;

    // Validate inputs
    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid amount in INR.");
        return;
    }

    if (!walletAddress && !confirm("You haven’t provided a wallet address. The ETH will be held in your Blockeste account. Continue?")) {
        return;
    }

    // Create a Razorpay order
    fetch("/create_order", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ amount: amount }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            // Open Razorpay payment modal
            const options = {
                key: "your_razorpay_api_key_here", // Replace with your Razorpay API key
                amount: data.amount,
                currency: data.currency,
                order_id: data.id,
                name: "Blockeste",
                description: "Convert INR to ETH",
                handler: function (response) {
                    // Handle payment success
                    fetch("/payment_success", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(response),
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === "success") {
                                alert("Payment successful! Your ETH will be processed shortly.");
                            } else {
                                throw new Error(data.error);
                            }
                        })
                        .catch(error => {
                            console.error("Error:", error);
                            alert("Payment failed. Please try again.");
                        });
                },
                prefill: {
                    email: "user@example.com", // Prefill user email (optional)
                },
                theme: {
                    color: "#4caf50", // Green theme
                },
            };

            const rzp = new Razorpay(options);
            rzp.open();
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to create payment order. Please try again.");
        });
});

// Update ETH price every 10 seconds
setInterval(fetchEthPrice, 10000);

// Initial fetch
fetchEthPrice();

// Add event listener for real-time updates as the user types
document.getElementById("amount").addEventListener("input", updateETHAmount);