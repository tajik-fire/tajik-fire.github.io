


document.addEventListener('DOMContentLoaded', () => {
    console.log('DevStudio Pro initialized');
    initializeTheme();
    initializeNavigation();
    initializeLogout();
});


function initializeTheme() {
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
}


function initializeNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar__link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
}


function initializeLogout() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
            } catch (error) {
                console.error('Logout error:', error);
            } finally {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/';
            }
        });
    }
}


function getAuthToken() {
    return localStorage.getItem('access_token');
}


function isAuthenticated() {
    return !!getAuthToken();
}


window.DevStudio = {
    getAuthToken,
    isAuthenticated
};
