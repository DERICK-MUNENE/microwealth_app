const API_URL = "https://microwealthapp-production.up.railway.app";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    let message = document.getElementById("message");
    const btn = document.getElementById("loginBtn");
    const togglePassword = document.getElementById("togglePassword");

    // Ensure message exists
    if (!message) {
        message = document.createElement("p");
        message.id = "message";
        form.appendChild(message);
    }

    //  Toggle password visibility
    togglePassword.addEventListener("click", () => {
        const isHidden = password.type === "password";
        password.type = isHidden ? "text" : "password";
        togglePassword.classList.toggle("fa-eye-slash");
        togglePassword.classList.toggle("fa-eye");
    });

    //  Login
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        message.textContent = "";
        message.className = "message";
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Logging in...`;

        try {
            const res = await fetch(`${API_URL}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: email.value.trim(),
                    password: password.value.trim()
                })
            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.detail || "Login failed");

            //  Save token
            localStorage.setItem("access_token", data.access_token);

            message.textContent = `Welcome back, ${data.user.full_name}!`;
            message.className = "message success";

            // Smooth redirect
            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 1200);

        } catch (err) {
            message.textContent = err.message;
            message.className = "message error";
        } finally {
            btn.disabled = false;
            btn.innerHTML = "Login";
        }
    });
});
