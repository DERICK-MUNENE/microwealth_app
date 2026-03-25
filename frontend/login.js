const API_URL = "https://microwealthapp-production.up.railway.app/"; 

const form = document.getElementById("loginForm");
const email = document.getElementById("email");
const password = document.getElementById("password");
const message = document.getElementById("message");
const btn = document.getElementById("loginBtn");
const togglePassword = document.getElementById("togglePassword");

// 👁️ Toggle password
togglePassword.addEventListener("click", () => {
    const isHidden = password.type === "password";
    password.type = isHidden ? "text" : "password";

    togglePassword.classList.toggle("fa-eye");
    togglePassword.classList.toggle("fa-eye-slash");
});

// 🔐 Login
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    message.textContent = "";
    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Logging in...`;

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email.value,
                password: password.value
            })
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Login failed");

        // ✅ Save token
        localStorage.setItem("access_token", data.access_token);

        message.textContent = "Login successful!";
        message.className = "message success";

        // Redirect
        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 1000);

    } catch (err) {
        message.textContent = err.message;
        message.className = "message error";
    } finally {
        btn.disabled = false;
        btn.innerHTML = "Login";
    }
});
