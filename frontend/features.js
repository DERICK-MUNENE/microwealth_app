// ==================== FEATURES.JS ====================
document.addEventListener("DOMContentLoaded", () => {
    loadCBKRates();
    loadInvestmentOptions();
    loadAIRecommendations();
    setupProviderTabs();
    setupScrollSpy();

    // Auto-refresh CBK rates every 30 seconds
    setInterval(loadCBKRates, 30000);
});



// ------------------ CBK RATES ------------------
async function loadCBKRates() {
    const container = document.getElementById("cbkRates");
    if (!container) return;

    container.innerHTML = `<p class="loading">Loading CBK rates...</p>`;

    try {
        const res = await fetch(`${API_URL}/cbk-rates`);
        const data = await res.json();

        if (!res.ok) throw new Error("Failed to load CBK rates");

        container.innerHTML = "";

        data.forEach(rate => {
            container.innerHTML += `
                <div class="feature-card">
                    <span class="tag live">LIVE</span>
                    <h3>${rate.tenor}</h3>
                    <p class="rate">${rate.rate}% p.a</p>
                    <p class="meta">Issued by Central Bank of Kenya</p>
                </div>
            `;
        });

    } catch (err) {
        container.innerHTML = `
            <p class="error">
                Unable to load CBK rates. Please try again later.
            </p>
        `;
        console.error(err);
    }
}

// ------------------ INVESTMENT OPTIONS ------------------
function loadInvestmentOptions() {
    const container = document.getElementById("investmentOptions");
    if (!container) return;

    const options = [
        { name: "Money Market Funds", risk: "Low Risk", providers: ["CIC MMF", "NCBA MMF", "Sanlam MMF"], description: "Highly liquid, capital-preserving investments ideal for emergency funds." },
        { name: "Treasury Bills", risk: "Low Risk", providers: ["CBK 91-Day", "CBK 182-Day", "CBK 364-Day"], description: "Government-backed securities with predictable returns." },
        { name: "Unit Trust Funds", risk: "Medium Risk", providers: ["CIC Unit Trust", "Britam Unit Trust"], description: "Diversified portfolios combining bonds and equities." },
        { name: "Balanced Funds", risk: "Medium Risk", providers: ["ICEA Lion Balanced Fund"], description: "Blends growth and stability for long-term investors." },
        { name: "REITs", risk: "Medium–High Risk", providers: ["ILAM Fahari I-REIT", "Acorn D-REIT"], description: "Real estate exposure without owning physical property." },
        { name: "Equity Funds", risk: "High Risk", providers: ["CIC Equity Fund", "ICEA Lion Equity Fund"], description: "Designed for aggressive growth over long periods." }
    ];

    container.innerHTML = "";

    options.forEach(opt => {
        container.innerHTML += `
            <div class="feature-card">
                <span class="tag">${opt.risk}</span>
                <h3>${opt.name}</h3>
                <p>${opt.description}</p>
                <p class="meta"><strong>Providers:</strong> ${opt.providers.join(", ")}</p>
            </div>
        `;
    });
}

// ------------------ AI RECOMMENDATIONS ------------------
function loadAIRecommendations() {
    const container = document.getElementById("aiRecommendations");
    if (!container) return;

    const recommendations = [
        { title: "Low Risk Investors", text: "Focus on CBK Treasury Bills and Money Market Funds to preserve capital while earning stable returns." },
        { title: "Medium Risk Investors", text: "Balanced Funds and Unit Trusts offer growth while managing downside risk." },
        { title: "High Risk Investors", text: "Equity Funds and REITs are suitable if you can tolerate volatility for higher long-term returns." }
    ];

    container.innerHTML = "";

    recommendations.forEach(rec => {
        container.innerHTML += `
            <div class="feature-card ai">
                <h3>${rec.title}</h3>
                <p>${rec.text}</p>
            </div>
        `;
    });
}

// ------------------ PROVIDER TABS ------------------
function setupProviderTabs() {
    const tabs = document.querySelectorAll(".providers-tabs button");
    const list = document.querySelector(".providers-list");

    const providersData = {
        "Fund Managers": ["CIC Group", "Old Mutual", "Britam", "Sanlam"],
        "Banks": ["Equity Bank", "KCB", "NCBA", "Co-operative Bank"],
        "SACCOs": ["Mwalimu SACCO", "Stima SACCO", "KUSCCO SACCO"],
        "Government": ["CBK", "National Treasury", "NSSF"]
    };

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const key = tab.textContent.trim();
            list.innerHTML = "";

            if (providersData[key]) {
                providersData[key].forEach(p => {
                    const div = document.createElement("div");
                    div.className = "provider";
                    div.textContent = p;
                    list.appendChild(div);
                });
            }
        });
    });
}

// ==================== SCROLL-SPY & SMOOTH SCROLL ====================
function setupScrollSpy() {
    const sidebarLinks = document.querySelectorAll(".features-sidebar a");
    const sections = document.querySelectorAll(".features-main section");

    function onScroll() {
        let scrollPos = window.scrollY || window.pageYOffset;

        sections.forEach((section) => {
            const top = section.offsetTop - 120; // adjust for header
            const bottom = top + section.offsetHeight;

            const id = section.getAttribute("id");
            const link = document.querySelector(`.features-sidebar a[href="#${id}"]`);

            if (scrollPos >= top && scrollPos < bottom) {
                sidebarLinks.forEach(link => link.classList.remove("active"));
                if (link) link.classList.add("active");
            }
        });
    }

    window.addEventListener("scroll", onScroll);

    // Smooth scrolling
    sidebarLinks.forEach(link => {
        link.addEventListener("click", function(e) {
            e.preventDefault();
            const targetId = this.getAttribute("href").substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                window.scrollTo({
                    top: targetSection.offsetTop - 100, // adjust for fixed header
                    behavior: "smooth"
                });
            }
        });
    });
}
