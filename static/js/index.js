const button = document.getElementById("login");
const tab = document.querySelector(".tab");


button.addEventListener("click", function () {
    tab.style.display = 'block'; // Show login modal
});

// Close modal when clicking outside login panel
window.addEventListener("click", (e) => {
    if (e.target == tab) {
        tab.style.display = 'none';
    }
});
// let alogin=document.querySelector(".ulogin");
// alogin.addEventListener("click",()=>{
//     tab.style.display="block"
   
// })
// Handle success message and form visibility
window.onload = function () {
    let successMessage = document.querySelector(".success");
    let errorMessage = document.querySelector(".danger");
    let registerForm = document.getElementById("registerForm");
let logoutmsg=document.querySelector(".info")
   
if(logoutmsg){
    logoutmsg.style.display = 'block';
    tab.style.display='block'
    setTimeout(()=>{
        logoutmsg.style.display="none";
    },1000);
   
}
    if (successMessage) {
        successMessage.style.display = "block"; 
        tab.style.display = 'block';// Ensure message appears
        setTimeout(function() {
           // Hide after 5 seconds
           successMessage.style.display = "none";
            window.location.href = "/dashboard"; // Redirect to dashboard
        }, 1000);
    }

    if (errorMessage) {
            errorMessage.style.display = "block";
            tab.style.display = 'block'; // Ensure error appears
        
       
        
    }
};

const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
    // Toggle tabs
    loginTab.addEventListener("click", () => {
        loginTab.classList.add("active");
        registerTab.classList.remove("active");
        loginForm.classList.add("active");
        registerForm.classList.remove("active");
      });
  
      registerTab.addEventListener("click", () => {
        registerTab.classList.add("active");
        loginTab.classList.remove("ulogin");
        loginTab.classList.remove("active");
        registerForm.classList.add("active");
        loginForm.classList.remove("active");
      });
let activeMenu = null; // Keep track of the currently open dropdown

document.querySelectorAll(".dropdown-btn").forEach(button => {
    const menu = button.nextElementSibling; // Get the corresponding dropdown menu

    button.addEventListener("click", (event) => {
        event.stopPropagation(); // Prevent immediate closing

        // Close the currently active menu (if any) before opening a new one
        if (activeMenu && activeMenu !== menu) {
            activeMenu.style.display = "none";
        }

        // Toggle the clicked menu
        menu.style.display = menu.style.display === "grid" ? "none" : "grid";

        // Update activeMenu based on current state
        activeMenu = menu.style.display === "grid" ? menu : null;
    });
    menu.addEventListener("mouseover", () => {
        menu.style.display = "grid";
    });

    menu.addEventListener("mouseout", () => {
        menu.style.display = "none";
    });
});

// Hide menu when clicking anywhere outside
document.addEventListener("click", (event) => {
    if (activeMenu && !activeMenu.previousElementSibling.contains(event.target) && !activeMenu.contains(event.target)) {
        activeMenu.style.display = "none";
        activeMenu = null;
    }
});

