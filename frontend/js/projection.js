// ================= PROJECTION =================
document.addEventListener("DOMContentLoaded", setupInvestmentProjection);

function setupInvestmentProjection() {
    const form = document.getElementById("projection-form");
    if (!form) return;

    form.addEventListener("submit", async e => {
        e.preventDefault();

        const token = requireAuth();
        if (!token) return;

        try {
            const res = await fetch(`${API_URL}/project-investment-enhanced`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    amount: +investAmount.value,
                    years: +investYears.value
                })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail);

            projectionResult.innerHTML = `
                <p><strong>Expected:</strong> KSh ${data.projection.expected_amount}</p>
                <p><strong>Assets:</strong> ${data.recommended_assets.join(", ")}</p>
            `;

        } catch (err) {
            showGlobalMessage(err.message, "error");
        }
    });
}
