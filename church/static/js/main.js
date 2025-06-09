// church/static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function () {
            const htmlEl = document.documentElement;
            const currentTheme = htmlEl.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlEl.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Countdown Timer Functionality
// Countdown Timer Functionality
document.addEventListener('DOMContentLoaded', function () {
    function updateCountdowns() {
        document.querySelectorAll('.event-timer').forEach(timer => {
            const startStr = timer.dataset.start;
            const endStr = timer.dataset.end;

            if (!startStr) return;

            const now = new Date();
            const start = new Date(startStr);
            const end = endStr ? new Date(endStr) : null;

            const countdownElement = timer.querySelector('.countdown');

            if (end && now > end) {
                // Event has ended
                if (countdownElement) {
                    timer.innerHTML = '<span class="text-muted">Event Ended</span>';
                }
            } else if (now >= start && (!end || now <= end)) {
                // Event is happening now
                if (countdownElement) {
                    timer.innerHTML = '<span class="text-danger fw-bold">Happening Now!</span>';
                }
            } else {
                // Event is upcoming
                if (countdownElement) {
                    const diff = start - now;
                    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

                    let countdownText = '';
                    if (days > 0) {
                        countdownText += `${days}d `;
                    }
                    if (hours > 0 || days > 0) {
                        countdownText += `${hours}h `;
                    }
                    countdownText += `${minutes}m`;

                    countdownElement.textContent = countdownText;
                }
            }
        });
    }

    // Update immediately
    updateCountdowns();

    // Update every minute
    setInterval(updateCountdowns, 60000);
});

document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("theme-toggle");
    const logo = document.getElementById("logo-img");

    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem("theme");
    const root = document.documentElement;

    function applyTheme(theme) {
        root.setAttribute("data-bs-theme", theme);
        logo.src = theme === "dark" ? logo.src.replace("logo-light", "logo-dark") : logo.src.replace("logo-dark", "logo-light");
    }

    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        applyTheme(prefersDark ? "dark" : "light");
    }

    toggleButton.addEventListener("click", () => {
        const currentTheme = root.getAttribute("data-bs-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        localStorage.setItem("theme", newTheme);
        applyTheme(newTheme);
    });
});
