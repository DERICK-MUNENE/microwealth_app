// ================= UI CORE =================

// SHOW GLOBAL MESSAGES
function showMessage(message, type = 'success') {
    const existing = document.querySelector('.global-message');
    if (existing) existing.remove();

    const msg = document.createElement('div');
    msg.className = `global-message ${type}`;
    msg.innerHTML = `<span>${message}</span><button class="close-message">&times;</button>`;
    document.body.appendChild(msg);

    msg.querySelector('.close-message').addEventListener('click', () => msg.remove());

    setTimeout(() => {
        if (msg.parentNode) msg.remove();
    }, 5000);
}

// UPDATE USER INFO
function updateUserInfo() {
    const userData = localStorage.getItem('microwealth_user');
    if (!userData) return;

    let user;
    try {
        user = JSON.parse(userData);
    } catch (err) {
        console.error('Failed to parse user data:', err);
        return;
    }

    const profileName = document.querySelector('.profile-info h4');
    const userName = document.querySelector('.user-info .user');

    if (user && user.full_name) {
        if (profileName) profileName.textContent = user.full_name;
        if (userName) userName.innerHTML = `<i class="fas fa-user-circle"></i> ${user.full_name}`;
    }
}

function renderManualResult(data) {
    const resultDiv = document.getElementById("manualResult");
    if (!resultDiv) return;

    resultDiv.innerHTML = `
        <h4>Analysis Result:</h4>
        <p><strong>Disposable Income:</strong> KSh ${data.disposable_income}</p>
        <p><strong>Risk Level:</strong> ${data.risk_level}</p>
        <p><strong>Recommendations:</strong> ${data.recommendations.join(", ")}</p>
    `;
}


// SIDEBAR NAVIGATION
function setupSidebarNavigation() {
    const sidebarItems = document.querySelectorAll('.sidebar-menu li');
    const sections = document.querySelectorAll('.section');

    sidebarItems.forEach(item => {
        item.addEventListener('click', () => {
            const sectionId = item.getAttribute('data-section');

            sidebarItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === sectionId) section.classList.add('active');
            });

            history.pushState(null, null, `#${sectionId}`);
        });
    });

    const hash = window.location.hash.substring(1);
    if (hash) {
        const targetItem = document.querySelector(`.sidebar-menu li[data-section="${hash}"]`);
        if (targetItem) targetItem.click();
    }
}


// DATE DISPLAY
function setupDateDisplay() {
    const currentDateElement = document.getElementById('currentDate');
    if (!currentDateElement) return;

    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    currentDateElement.textContent = now.toLocaleDateString('en-US', options);
}

// DOM READY
document.addEventListener('DOMContentLoaded', () => {
    updateUserInfo();
    setupSidebarNavigation();
    setupMobileMenu();
    setupDateDisplay();
});
