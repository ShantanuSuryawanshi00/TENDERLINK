document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initScrollReveal();
    initLiveCounters();
    initThemeToggle();
});


function initNavigation() {
    // Mobile Menu Toggle
    const menuBtn = document.querySelector('.mobile-menu');
    const navLinks = document.querySelector('.nav-links');

    if (menuBtn && navLinks) {
        // Clone to remove existing listeners from inline script if any
        const newBtn = menuBtn.cloneNode(true);
        menuBtn.parentNode.replaceChild(newBtn, menuBtn);

        newBtn.addEventListener('click', () => {
            navLinks.classList.toggle('show');
            const icon = newBtn.querySelector('i');
            if (navLinks.classList.contains('show')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
    }

    // Sticky Header
    const header = document.querySelector('.header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Smooth Scroll for Internal Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#' || !targetId.startsWith('#')) return;

            e.preventDefault();
            const target = document.querySelector(targetId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Close mobile menu if open
                if (navLinks && navLinks.classList.contains('show')) {
                    navLinks.classList.remove('show');
                    if (menuBtn) menuBtn.querySelector('i').className = 'fas fa-bars';
                }
            }
        });
    });

}


function initScrollReveal() {
    // Create observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, { threshold: 0.1, rootMargin: "0px 0px -50px 0px" });

    // Target elements to animate
    const elementsToReveal = document.querySelectorAll('.category-card, .table-row, .announcement-card');

    elementsToReveal.forEach((el, index) => {
        // Apply initial styles immediately
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.8s cubic-bezier(0.2, 0.8, 0.2, 1)';
        // Stagger effect based on index (modulo to reset for grid rows)
        el.style.transitionDelay = `${(index % 3) * 100}ms`;
        observer.observe(el);
    });

    // Add CSS class for 'revealed' state dynamically
    if (!document.getElementById('reveal-style')) {
        const style = document.createElement('style');
        style.id = 'reveal-style';
        style.innerHTML = `
            .revealed {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
        `;
        document.head.appendChild(style);
    }
}

function initLiveCounters() {
    // Animate stats in Hero
    const stats = document.querySelectorAll('.stat h3, .stat-row span:first-child, .count');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateValue(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    stats.forEach(stat => observer.observe(stat));
}

function animateValue(obj) {
    const rawText = obj.innerText;
    // Helper to find the first number in string "₹5.2K Cr" -> "5.2"
    const valueMatch = rawText.match(/[\d,\.]+/);
    if (!valueMatch) return;

    const originalNumStr = valueMatch[0];
    const endVal = parseFloat(originalNumStr.replace(/,/g, ''));
    if (isNaN(endVal)) return;

    const duration = 2000;
    let startTimestamp = null;

    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);

        // Easing (easeOutExpo)
        const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);

        const currentVal = endVal * ease;

        // Attempt to preserve approximate decimals
        let formattedVal;
        if (originalNumStr.includes('.')) {
            formattedVal = currentVal.toFixed(1);
        } else {
            formattedVal = Math.floor(currentVal).toLocaleString();
        }

        obj.innerText = rawText.replace(originalNumStr, formattedVal);

        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerText = rawText; // Ensure exact final value at end
        }
    };
    window.requestAnimationFrame(step);
}



// === NEW LOGIC FOR BUTTONS & PAGES ===
document.addEventListener('DOMContentLoaded', () => {
    // 1. Handle Search Buttons (Hero and Header)
    const searchBtns = document.querySelectorAll('.btn-search');
    searchBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // If it's the search bar button
            const input = btn.previousElementSibling;
            if (input && input.tagName === 'INPUT') {
                e.preventDefault();
                const query = input.value.trim();
                window.location.href = `/listing/?q=${encodeURIComponent(query)}`;
            }
        });
    });

    // 2. Handle Category Cards
    const catCards = document.querySelectorAll('.category-card');
    catCards.forEach(card => {
        card.addEventListener('click', () => {
            const catName = card.querySelector('h3').innerText;
            window.location.href = `/listing/?category=${encodeURIComponent(catName)}`;
        });
        // Make it look clickable
        card.style.cursor = 'pointer';
    });

    // 3. Handle "View All" / "Active Tenders" links
    // Handled by Django template URLs (href tags) in 2025 upgrade.


    // 5. Navigation logic handled by Django template URLs (href tags)
    // No additional JS overrides needed for main nav links.

    // LISTING PAGE LOGIC (Django route: /listing/)
    if (window.location.pathname.includes('/listing/')) {
        const urlParams = new URLSearchParams(window.location.search);
        const q = urlParams.get('q');
        const cat = urlParams.get('category');
        const title = document.getElementById('page-title');
        const searchInput = document.getElementById('list-search');

        if (q) {
            title.innerText = `Search Results: "${q}"`;
            searchInput.value = q;
        } else if (cat) {
            title.innerText = `${cat} Tenders`;
        }
    }

    // 4. Handle Favorite Toggles via AJAX
    const favBtns = document.querySelectorAll('.favorite-toggle');
    favBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const tenderId = btn.getAttribute('data-id');
            const icon = btn.querySelector('i');

            try {
                const response = await fetch(`/favorite/toggle/${tenderId}/?ajax=1`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await response.json();

                if (data.status === 'success') {
                    if (data.action === 'added') {
                        icon.className = 'fas fa-star';
                        btn.style.transform = 'scale(1.3)';
                        setTimeout(() => btn.style.transform = 'scale(1)', 200);
                    } else {
                        icon.className = 'far fa-star';
                        if (window.location.pathname.includes('/archive/')) {
                            const row = document.getElementById(`fav-row-${tenderId}`);
                            if (row) {
                                row.style.opacity = '0';
                                row.style.transform = 'translateX(20px)';
                                setTimeout(() => row.remove(), 300);
                            }
                        }
                    }
                }
            } catch (error) {
                window.location.href = btn.href;
            }
        });
    });

    // 6. Password Visibility Toggle
    const passwordToggles = document.querySelectorAll('.toggle-password');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const targetId = toggle.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    toggle.classList.remove('fa-eye');
                    toggle.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    toggle.classList.remove('fa-eye-slash');
                    toggle.classList.add('fa-eye');
                }
            }
        });
    });
});

function initThemeToggle() {
    const toggleBtn = document.getElementById('theme-toggle');
    if (!toggleBtn) return;

    const icon = toggleBtn.querySelector('i');

    // Check saved theme or system preference
    const savedTheme = localStorage.getItem('tenderlink_theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        icon.className = 'fas fa-sun';
    }

    toggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        if (currentTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('tenderlink_theme', 'light');
            icon.className = 'fas fa-moon';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('tenderlink_theme', 'dark');
            icon.className = 'fas fa-sun';
        }
    });
}


