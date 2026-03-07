// ================= DASHBOARD =================
document.addEventListener("DOMContentLoaded", populateDashboard);

async function populateDashboard() {
    const token = requireAuth();
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/dashboard/data`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        userName.textContent = data.user.name;
        userRole.textContent = `${data.user.risk_level} Risk`;

    } catch (err) {
        console.error(err.message);
    }
}
