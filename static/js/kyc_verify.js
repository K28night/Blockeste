
const canvas = document.getElementById("signature-pad");
const ctx = canvas.getContext("2d");
let drawing = false;

// Set up drawing properties
ctx.lineWidth = 2;
ctx.strokeStyle = "#000";

// Start drawing
canvas.addEventListener("mousedown", (e) => {
    drawing = true;
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
});

// Draw lines
canvas.addEventListener("mousemove", (e) => {
    if (drawing) {
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
    }
});

// Stop drawing
canvas.addEventListener("mouseup", () => {
    drawing = false;
    ctx.closePath();
    saveSignature(); // Save the signature when drawing stops
});

// Save the signature
function saveSignature() {
    document.getElementById("signature_data").value = canvas.toDataURL("image/png");
}

// Clear the canvas
function clearSignature() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    document.getElementById("signature_data").value = ""; // Clear stored data
}

// Set up the clear button
document.getElementById("sig-clearBtn").addEventListener("click", clearSignature);
   
        // Validate Name (must be in uppercase)
      

        // Validate Form (age and signature)
        function validateForm() {
            var fullName = document.getElementById("full_name").value;
            var nameError = document.getElementById("nameError");
            if (fullName !== fullName.toUpperCase()) {
                nameError.textContent = "Name must be in ALL CAPITAL LETTERS.";
            } else {
                nameError.textContent = "";
            }
            var dob = document.getElementById("dob").value;
            var dobError = document.getElementById("dobError");

            // Calculate age
            var today = new Date();
            var birthDate = new Date(dob);
            var age = today.getFullYear() - birthDate.getFullYear();
            var monthDiff = today.getMonth() - birthDate.getMonth();
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }

            // Check if user is at least 18 years old
            if (age < 18) {
                dobError.textContent = "You must be at least 18 years old.";
                return false;
            } else {
                dobError.textContent = "";
            }

            // Check if signature is provided
            if (canvas.isEmpty()) {
                alert("Please provide a signature.");
                return false;
            }

            // // Save signature data
            // document.getElementById("signature-data").value = signaturePad.toDataURL();
            // return true;
        }

        // View Profile (placeholder)
        function viewProfile() {
            alert("Redirecting to profile page...");
            window.location.href="/dashboard"
        }

        // Logout (placeholder)
        function logout() {
            alert("Logging out...");
            window.location.href="/logout"
        }
