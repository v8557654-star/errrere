// MineMods - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });
        images.forEach(img => imageObserver.observe(img));
    } else {
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }

    // Search with debounce
    const searchInput = document.querySelector('.search-bar input[name="q"]');
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const form = this.closest('form');
                if (form && this.value.length >= 2) {
                    // Visual feedback for search
                    form.style.opacity = '0.7';
                    setTimeout(() => form.style.opacity = '1', 200);
                }
            }, 300);
        });
    }

    // Smooth scroll for skip link
    const skipLink = document.querySelector('.skip-link');
    if (skipLink) {
        skipLink.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
                target.focus();
            }
        });
    }

    // User dropdown accessibility
    const menuBtn = document.querySelector('.user-menu-btn');
    const dropdown = document.querySelector('.user-dropdown');
    if (menuBtn && dropdown) {
        menuBtn.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                dropdown.classList.toggle('open');
                this.setAttribute('aria-expanded', dropdown.classList.contains('open'));
            }
            if (e.key === 'Escape') {
                dropdown.classList.remove('open');
                this.setAttribute('aria-expanded', 'false');
                this.focus();
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!menuBtn.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
                menuBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Mobile menu close on escape
    const sidebar = document.querySelector('.sidebar');
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    if (sidebar && menuToggle) {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
                menuToggle.focus();
            }
        });
    }

    // Add loading state to download buttons
    const downloadButtons = document.querySelectorAll('.btn-download');
    downloadButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.add('loading');
            setTimeout(() => this.classList.remove('loading'), 2000);
        });
    });

    // Stats counter animation
    const statNums = document.querySelectorAll('.stat-num');
    if ('IntersectionObserver' in window) {
        const statObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const num = entry.target;
                    const target = parseInt(num.textContent);
                    if (!isNaN(target)) {
                        animateCounter(num, 0, target, 1500);
                        statObserver.unobserve(num);
                    }
                }
            });
        });
        statNums.forEach(num => statObserver.observe(num));
    }

    function animateCounter(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= end) {
                element.textContent = end;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }

    // Toast notifications auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Theme preview on hover (settings page)
    const themeOptions = document.querySelectorAll('.theme-option');
    const htmlEl = document.documentElement;
    const originalTheme = htmlEl.getAttribute('data-theme');
    
    themeOptions.forEach(option => {
        option.addEventListener('mouseenter', function() {
            const theme = this.querySelector('input').value;
            htmlEl.setAttribute('data-theme', theme);
        });
        
        option.addEventListener('mouseleave', function() {
            htmlEl.setAttribute('data-theme', originalTheme);
        });
    });

    // Live appearance preview on the settings page. The server validates and persists
    // the exact same values when the form is saved.
    const appearanceForm = document.querySelector('#appearanceForm');
    if (appearanceForm) {
        const customColorsToggle = appearanceForm.querySelector('#custom-colors-toggle');
        const colorControls = appearanceForm.querySelector('#colorControls');
        const accentInput = appearanceForm.querySelector('#accent-color');
        const accentSecondaryInput = appearanceForm.querySelector('#accent-color-secondary');
        const colorOutputs = appearanceForm.querySelectorAll('[data-color-value]');

        const selectedValue = (name, fallback) => {
            const choice = appearanceForm.querySelector(`input[name="${name}"]:checked`);
            return choice ? choice.value : fallback;
        };

        const updateAppearancePreview = () => {
            const usesCustomColors = customColorsToggle.checked;
            const accent = accentInput.value;
            const secondary = accentSecondaryInput.value;

            htmlEl.setAttribute('data-custom-colors', usesCustomColors ? 'on' : 'off');
            htmlEl.setAttribute('data-density', selectedValue('interface_density', 'comfortable'));
            htmlEl.setAttribute('data-corners', selectedValue('corner_style', 'rounded'));
            htmlEl.setAttribute('data-background', selectedValue('background_style', 'aurora'));

            if (usesCustomColors) {
                htmlEl.style.setProperty('--user-accent', accent);
                htmlEl.style.setProperty('--user-accent-2', secondary);
            }

            colorControls.classList.toggle('is-disabled', !usesCustomColors);
            accentInput.disabled = !usesCustomColors;
            accentSecondaryInput.disabled = !usesCustomColors;
            colorOutputs.forEach((output, index) => {
                output.textContent = (index === 0 ? accent : secondary).toUpperCase();
            });
        };

        appearanceForm.addEventListener('input', updateAppearancePreview);
        appearanceForm.addEventListener('change', updateAppearancePreview);
        updateAppearancePreview();
    }

    // Performance: Reduce motion for users who prefer it
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.documentElement.setAttribute('data-animations', 'off');
    }
});

// Service Worker registration for PWA (if available)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js').then(reg => {
        //     console.log('ServiceWorker registered:', reg.scope);
        // }).catch(err => {
        //     console.log('ServiceWorker registration failed:', err);
        // });
    });
}
