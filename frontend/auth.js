const API_URL = "";


document.addEventListener("DOMContentLoaded", () => {
    checkAuth();

    const loginForm = document.getElementById("loginForm");
    if (loginForm) loginForm.addEventListener("submit", handleLogin);

    const registerForm = document.getElementById("registerForm");
    if (registerForm) registerForm.addEventListener("submit", handleRegister);
});

// ================= LOGIN =================
async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const message = document.getElementById("message");

    if (!email || !password) {
        showMessage(message, "All fields are required", "error");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        if (!res.ok) throw new Error("Invalid credentials");

        const data = await res.json();

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("microwealth_user", JSON.stringify(data.user));


        showMessage(message, "Login successful", "success");
        setTimeout(() => window.location.href = "dashboard.html", 1000);

    } catch (err) {
        showMessage(message, "Invalid email or password", "error");
    }
}

// ================= REGISTER =================
async function handleRegister(e) {
    e.preventDefault();

    const full_name = document.getElementById("full_name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const message = document.getElementById("message");

    if (!full_name || !email || !password) {
        showMessage(message, "All fields are required", "error");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ full_name, email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            // 🔥 show backend error message
            throw new Error(data.detail || "Registration failed");
        }

        showMessage(message, data.message, "success");
        setTimeout(() => window.location.href = "login.html", 1000);

    } catch (err) {
        showMessage(message, err.message, "error");
    }
}
function showMessage(element, text, type) {
    element.textContent = text;
    element.className = ""; // reset
    element.classList.add(type);
}




// ================= AUTH GUARD =================
function checkAuth() {
    const token = localStorage.getItem("access_token");
    const path = window.location.pathname;

    if (path.includes("dashboard.html") && !token) {
        window.location.href = "login.html";
    }

    if ((path.includes("login.html") || path.includes("register.html")) && token) {
        window.location.href = "dashboard.html";
    }
}

// ================= LOGOUT =================
function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    sessionStorage.clear();
    window.location.href = "index.html";
}
