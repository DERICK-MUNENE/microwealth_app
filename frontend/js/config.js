// ================= CONFIG =================
const API_URL = "http://127.0.0.1:8000";

// -------- TOKEN HELPERS --------
function getToken() {
    return localStorage.getItem("access_token");
}

function requireAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = "login.html";
        return null;
    }
    return token;
}
