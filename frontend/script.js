// ==================== SCRIPT.JS ====================


// On page load
document.addEventListener("DOMContentLoaded", () => {
    populateDashboard();
    setupManualAnalysis();
    setupInvestmentProjection();
    setupPdfAnalysis();
    setupCashflowIntelligence();
    setupSidebarNavigation();
});

// ------------------ SHOW MESSAGE ------------------
function showMessage(container, msg, type = "success") {
    container.textContent = msg;
    container.className = `${type} result-box`;
}

// ------------------ MANUAL ANALYSIS ------------------
function setupManualAnalysis() {
    const form = document.getElementById("finance-form");
    const resultBox = document.getElementById("manualResult");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const income = document.getElementById("income").value.trim();
        const expenses = document.getElementById("expenses").value.trim();
        const savings = document.getElementById("savings").value.trim();

        if (!income || !expenses || !savings) {
            showMessage(resultBox, "All fields are required", "error");
            return;
        }

        const payload = { income: Number(income), expenses: Number(expenses), savings: Number(savings) };
        const token = localStorage.getItem("access_token");
        if (!token) {
            showMessage(resultBox, "Session expired. Please login.", "error");
            setTimeout(() => window.location.href = "login.html", 1200);
            return;
        }

        try {
            const res = await fetch(`${API_URL}/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (!res.ok) throw new Error(data.detail || "Analysis failed");

            renderManualResult(data);
            fetchHistory();
            populateDashboard();
        } catch (err) {
            showMessage(resultBox, err.message, "error");
        }
    });
}

// ------------------ MANUAL RESULT RENDER ------------------
function renderManualResult(data) {
    const box = document.getElementById("manualResult");

    const recommendations = Array.isArray(data.recommendations)
        ? data.recommendations.join(", ")
        : "None available";

    box.innerHTML = `
        <p><strong>Disposable Income:</strong> KSh ${data.disposable_income ?? 0}</p>
        <p><strong>Risk Level:</strong> ${data.risk_level ?? "N/A"}</p>
        <p><strong>Recommended Investments:</strong> ${recommendations}</p>
    `;

    box.className = "success result-box";
}


// ------------------ INVESTMENT PROJECTION ------------------
function setupInvestmentProjection() {
    const form = document.getElementById("projection-form");
    const resultBox = document.getElementById("projectionResult");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const amount = Number(document.getElementById("investAmount").value);
        const years = Number(document.getElementById("investYears").value);
        const risk = document.getElementById("riskLevel").value;
        const token = localStorage.getItem("access_token");
        if (!token) return;

        resultBox.innerHTML = "Calculating projection...";
        try {
            const res = await fetch(`${API_URL}/project-investment-enhanced`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ amount, years, risk })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Projection failed");

            renderProjectionResultEnhanced(data);

        } catch (err) {
            showMessage(resultBox, err.message, "error");
        }
    });
}

// ------------------ RENDER ENHANCED PROJECTION ------------------
function renderProjectionResultEnhanced(data) {
    const box = document.getElementById("projectionResult");
    let html = `
        <p><strong>Risk Level:</strong> ${data.risk_level ?? "N/A"}</p>
        <p><strong>Initial Amount:</strong> KSh ${data.projection?.initial_amount ?? "N/A"}</p>
        <p><strong>Projection Period:</strong> ${data.projection?.years ?? "N/A"} years</p>
        <h3>Recommended Assets:</h3>
    `;
console.log(data.recommended_assets);

    if (data.recommended_assets?.length) {
    data.recommended_assets.forEach(asset => {
        const explanationHTML = marked.parse((asset.detailed_explanation || "No explanation available").trim());
        
        html += `
            <div class="asset-card">
                <h4>${asset.asset_name ?? "N/A"} (${asset.asset_type ?? "N/A"})</h4>
                <p><strong>Expected Annual Return:</strong> ${((asset.expected_return ?? 0) * 100).toFixed(2)}%</p>
                <details>
                    <summary>Why this asset?</summary>
                </details>
                <div class="asset-explanation">${explanationHTML}</div>
            </div>
        `;
    });
}
    box.innerHTML = html;
    box.className = "success result-box";
}

// ------------------ PDF ANALYSIS ------------------
function setupPdfAnalysis() {
    const form = document.getElementById("pdf-form");
    const fileInput = document.getElementById("pdfFile");
    const dropArea = document.getElementById("dropArea");
    const resultBox = document.getElementById("pdfResult");

    if (!form || !fileInput || !dropArea) return;

    // Click upload area → open file dialog
    dropArea.addEventListener("click", () => fileInput.click());

    // Drag over
    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("dragging");
    });

    // Drag leave
    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("dragging");
    });

    // Drop file
    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("dragging");

        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
        }
    });

    // Submit form
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!fileInput.files.length) {
            alert("Select a PDF file");
            return;
        }

        const token = localStorage.getItem("access_token");
        if (!token) {
            window.location.href = "login.html";
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const res = await fetch(`${API_URL}/analyze-pdf`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                body: formData
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "PDF analysis failed");

            let html = `
    <p><strong>Income:</strong> KSh ${data.income ?? 0}</p>
    <p><strong>Expenses:</strong> KSh ${data.expenses ?? 0}</p>
    <p><strong>Net Cashflow:</strong> KSh ${data.net_cashflow ?? 0}</p>
`;

if (data.investment_allowed === false) {

    html += `
        <p style="color:red;"><strong>Status:</strong> Financially Unstable</p>
    `;

    if (data.guidance?.length) {
        html += `
            <h4>Recovery Guidance:</h4>
            <ul>
                ${data.guidance.map(g => `<li>${g}</li>`).join("")}
            </ul>
        `;
    }

} else {

    html += `
        <p><strong>Risk Level:</strong> ${data.risk_level ?? "N/A"}</p>
    `;

    if (data.recommendations?.length) {
        html += `
            <p><strong>Recommendations:</strong> 
            ${data.recommendations.join(", ")}</p>
        `;
    } else {
        html += `
            <p><strong>Recommendations:</strong> None available</p>
        `;
    }
}

resultBox.innerHTML = html;
resultBox.className = "success result-box";

           

            fetchHistory();
            populateDashboard();

        } catch (err) {
            showMessage(resultBox, err.message, "error");
        }
    });
}

// ------------------ CASHFLOW INTELLIGENCE ------------------
function setupCashflowIntelligence() {
    const analyzeBtn = document.getElementById("testCashflowBtn");
    const resultBox = document.getElementById("cashflowResult");

    if (!analyzeBtn) return;

    analyzeBtn.addEventListener("click", async () => {

        const token = localStorage.getItem("access_token");
        if (!token) {
            window.location.href = "login.html";
            return;
        }

        resultBox.innerHTML = "Analyzing cashflow...";

        try {
            const res = await fetch(`${API_URL}/cashflow-from-latest-pdf`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Cashflow analysis failed");

            // ----------------- BUILD HTML -----------------
            let html = `
                <p><strong>Income:</strong> KSh ${data.income?.toLocaleString() ?? 0}</p>
                <p><strong>Expenses:</strong> KSh ${data.expenses?.toLocaleString() ?? 0}</p>
                <p><strong>Net Cashflow:</strong> KSh ${data.net_cashflow?.toLocaleString() ?? 0}</p>
            `;

            // Recovery guidance if financially unstable
            if (data.recovery_plan || data.guidance?.length) {
                html += `<h4>Recovery Guidance:</h4><ul>`;
                if (data.guidance?.length) {
                    html += data.guidance.map(g => `<li>${g}</li>`).join("");
                }
                if (data.recovery_plan) {
                    html += data.recovery_plan.map(r => `<li>${r}</li>`).join("");
                }
                html += `</ul>`;
            }

            // ----------------- EXPENSE BREAKDOWN -----------------
            if (data.expense_breakdown?.length) {
    // Find the highest expense to normalize bar widths
    const maxAmount = Math.max(...data.expense_breakdown.map(e => e.amount));

    html += `<h4>Expense Visualization</h4>
        <div class="expense-bars">`;

    data.expense_breakdown.forEach(exp => {
        let color = "green";
        if (exp.amount > 20000) color = "red";
        else if (exp.amount > 10000) color = "orange";

        // Width percentage relative to max amount
        const widthPercent = ((exp.amount / maxAmount) * 100).toFixed(2);

        html += `
            <div class="expense-bar-container">
                <span class="bar-label">${exp.category} (KSh ${exp.amount.toLocaleString()})</span>
                <div class="bar" style="width:${widthPercent}%; background-color:${color};"></div>
            </div>
        `;
    });

    html += `</div>`; // close expense-bars
}
            // ----------------- EXPENSE CUTTING PLAN -----------------
            if (data.expense_cutting_plan?.length) {
    html += `<h4>Expense-Cutting Plan</h4>`;
    data.expense_cutting_plan.forEach(plan => {
        let emoji = "🟢"; // low
        if (plan.advice.includes("High")) emoji = "🔴";
        else if (plan.advice.includes("Moderate")) emoji = "🟠";

        html += `<p>${emoji} <strong>${plan.category}:</strong> ${plan.advice}</p>`;
    });
}

            resultBox.innerHTML = html;
            resultBox.className = "success result-box";

        } catch (err) {
            showMessage(resultBox, err.message, "error");
        }
    });
}

// ------------------ FETCH HISTORY ------------------
async function fetchHistory() {
    console.log("Fetching history...");
    const token = localStorage.getItem("access_token");

    if (!token) {
        console.warn("No token found");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/history`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) {
            throw new Error("Failed to fetch history");
        }

        const data = await res.json();
        renderHistoryTable(data);

    } catch (err) {
        console.error("History fetch failed:", err);
    }
}


// ------------------ HISTORY TABLE RENDER ------------------
function renderHistoryTable(data) {
    const tbody = document.getElementById("historyTable");
    tbody.innerHTML = "";

    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7">No history available</td></tr>`;
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


// ------------------ DELETE HISTORY ITEM ------------------
async function deleteHistory(id) {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    if (!confirm("Are you sure you want to delete this record?")) return;

    try {
        const res = await fetch(`${API_URL}/history/${id}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Delete failed");
        fetchHistory();
    } catch (err) {
        alert(err.message);
    }
}

// ------------------ DASHBOARD METRICS ------------------
async function populateDashboard() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/dashboard/data`, { headers: { "Authorization": `Bearer ${token}` } });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to fetch dashboard data");

        document.getElementById("userName").textContent = data.user.name;
        document.getElementById("userRole").textContent = data.user.risk_level + " Risk";

        // Optional: populate metrics cards if you have them
        // Example: document.getElementById("monthlyIncome").textContent = `KSh ${data.metrics.monthly_income}`;
    } catch (err) {
        console.error("Dashboard fetch failed:", err);
    }
}

// ------------------ SIDEBAR NAVIGATION ------------------
function setupSidebarNavigation() {
    const sections = document.querySelectorAll(".section");
    const sidebarItems = document.querySelectorAll(".sidebar-menu li");

    sidebarItems.forEach(item => {
        item.addEventListener("click", () => {
            const sectionId = item.dataset.section;

            sections.forEach(s => s.classList.remove("active"));
            document.getElementById(sectionId).classList.add("active");

            sidebarItems.forEach(i => i.classList.remove("active"));
            item.classList.add("active");

            // ✅ load history only when needed
            if (sectionId === "history") {
                fetchHistory();
            }
        });
    });
}

// ------------------ LOGOUT ------------------
function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}
