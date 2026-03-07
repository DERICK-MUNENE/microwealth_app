console.log("history.js loaded");



document.addEventListener("DOMContentLoaded", () => {
    const token = requireAuth();
    if (token) {
        fetchHistory(token);
    }
});

// ---------------- AUTH GUARD ----------------
function requireAuth() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "login.html";
        return null;
    }
    return token;
}

// ---------------- FETCH HISTORY ----------------
async function fetchHistory(token) {
    try {
        const res = await fetch(`${API_URL}/history`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (res.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "login.html";
            return;
        }

        const data = await res.json();
        console.log("History data:", data);
        renderHistoryTable(data);

    } catch (err) {
        console.error("History fetch failed:", err);
    }
}

// ---------------- RENDER TABLE ----------------
function renderHistoryTable(data) {
    const tbody = document.getElementById("historyTable");
    tbody.innerHTML = "";

    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7">No history found</td></tr>`;
        return;
    }

    data.forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${new Date(r.date).toLocaleDateString()}</td>
            <td>KSh ${r.income.toLocaleString()}</td>
            <td>KSh ${r.expenses.toLocaleString()}</td>
            <td>KSh ${r.savings.toLocaleString()}</td>
            <td>KSh ${r.disposable_income.toLocaleString()}</td>
            <td>${r.risk_level}</td>
            <td>
                <button onclick="deleteHistory(${r.id})" class="btn-delete">
                    Delete
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// ---------------- DELETE ----------------
async function deleteHistory(id) {
    const token = localStorage.getItem("access_token");
    if (!confirm("Delete this record?")) return;

    try {
        const res = await fetch(`${API_URL}/history/${id}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error("Delete failed");
        fetchHistory(token);

    } catch (err) {
        alert(err.message);
    }
}

// ---------------- LOGOUT ----------------
function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}
