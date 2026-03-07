// ================= MANUAL ANALYSIS =================
document.addEventListener("DOMContentLoaded", setupManualAnalysis);

function setupManualAnalysis() {
    const form = document.getElementById("finance-form");
    if (!form) return;

    form.addEventListener("submit", async e => {
        e.preventDefault();

        const token = requireAuth();
        if (!token) return;

        const payload = {
            income: +income.value,
            expenses: +expenses.value,
            savings: +savings.value
        };

        try {
            const res = await fetch(`${API_URL}/analyze`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail);

            renderManualResult(data);
            fetchHistory();
            populateDashboard();

        } catch (err) {
            showGlobalMessage(err.message, "error");
        }
    });
}

function renderManualResult(data) {
    manualResult.innerHTML = `
        <p><strong>Disposable Income:</strong> KSh ${data.disposable_income}</p>
        <p><strong>Risk Level:</strong> ${data.risk_level}</p>
        <p><strong>Recommendations:</strong> ${data.recommendations.join(", ")}</p>
    `;
}
