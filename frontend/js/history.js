// ================= HISTORY =================
document.addEventListener("DOMContentLoaded", fetchHistory);

async function fetchHistory() {
    const token = getToken();
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/history`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        const data = await res.json();
        renderHistoryTable(data);

    } catch (err) {
        console.error(err);
    }
}

function renderHistoryTable(data) {
    historyTable.innerHTML = "";

    if (!data.length) {
        historyTable.innerHTML = `<tr><td colspan="7">No history</td></tr>`;
        return;
    }

    data.forEach(r => {
        historyTable.innerHTML += `
            <tr>
                <td>${new Date(r.date).toLocaleDateString()}</td>
                <td>KSh ${r.income}</td>
                <td>KSh ${r.expenses}</td>
                <td>KSh ${r.savings}</td>
                <td>${r.risk_level}</td>
                <td><button onclick="deleteHistory(${r.id})">Delete</button></td>
            </tr>
        `;
    });
}

async function deleteHistory(id) {
    if (!confirm("Delete record?")) return;

    await fetch(`${API_URL}/history/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${getToken()}` }
    });

    fetchHistory();
}
