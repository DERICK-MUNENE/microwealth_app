// ================= AUTH =================
document.addEventListener("DOMContentLoaded", () => {
    checkAuth();

    document.getElementById("loginForm")?.addEventListener("submit", handleLogin);
    document.getElementById("registerForm")?.addEventListener("submit", handleRegister);
});

async function handleLogin(e) {
    e.preventDefault();

    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("microwealth_user", JSON.stringify(data.user));

        showGlobalMessage("Login successful", "success");
        setTimeout(() => location.href = "dashboard.html", 800);

    } catch (err) {
        showGlobalMessage(err.message, "error");
    }
}

async function handleRegister(e) {
    e.preventDefault();

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                full_name: full_name.value.trim(),
                email: email.value.trim(),
                password: password.value.trim()
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        showGlobalMessage(data.message, "success");
        setTimeout(() => location.href = "login.html", 1000);

    } catch (err) {
        showGlobalMessage(err.message, "error");
    }
}

function logout() {
    localStorage.clear();
    location.href = "login.html";
}

function checkAuth() {
    const token = getToken();
    const path = location.pathname;

    if (path.includes("dashboard") && !token) location.href = "login.html";
    if ((path.includes("login") || path.includes("register")) && token)
        location.href = "dashboard.html";
}
