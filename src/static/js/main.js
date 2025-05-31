// Main JavaScript for StoryQuest

document.addEventListener('DOMContentLoaded', function() {
    // Add js-enabled class to body for CSS targeting
    document.body.classList.add('js-enabled');
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            
            // Accessibility - toggle aria-expanded
            const expanded = navLinks.classList.contains('active');
            menuToggle.setAttribute('aria-expanded', expanded);
        });
    }
    
    // Add animation classes to elements when they come into view
    const animateElements = document.querySelectorAll('.feature-card, .age-group, .testimonial');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fadeIn');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animateElements.forEach(element => {
            observer.observe(element);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        animateElements.forEach(element => {
            element.classList.add('animate-fadeIn');
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Create or update error message
                    let errorMessage = field.nextElementSibling;
                    if (!errorMessage || !errorMessage.classList.contains('error-message')) {
                        errorMessage = document.createElement('div');
                        errorMessage.classList.add('error-message');
                        field.parentNode.insertBefore(errorMessage, field.nextSibling);
                    }
                    errorMessage.textContent = 'This field is required';
                } else {
                    field.classList.remove('is-invalid');
                    const errorMessage = field.nextElementSibling;
                    if (errorMessage && errorMessage.classList.contains('error-message')) {
                        errorMessage.textContent = '';
                    }
                }
            });
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    });
    
    // Responsive image loading
    const responsiveImages = document.querySelectorAll('[data-src]');
    
    responsiveImages.forEach(img => {
        const loadImage = () => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        };
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        loadImage();
                        observer.unobserve(entry.target);
                    }
                });
            });
            observer.observe(img);
        } else {
            loadImage();
        }
    });
    
    // Add mobile menu button if it doesn't exist
    if (!menuToggle && navLinks) {
        const navbar = document.querySelector('.navbar');
        
        if (navbar) {
            const toggle = document.createElement('button');
            toggle.className = 'menu-toggle';
            toggle.setAttribute('aria-label', 'Toggle navigation menu');
            toggle.setAttribute('aria-expanded', 'false');
            
            for (let i = 0; i < 3; i++) {
                const span = document.createElement('span');
                toggle.appendChild(span);
            }
            
            navbar.appendChild(toggle);
            
            toggle.addEventListener('click', function() {
                navLinks.classList.toggle('active');
                const expanded = navLinks.classList.contains('active');
                toggle.setAttribute('aria-expanded', expanded);
            });
        }
    }
    
    // Check viewport size and adjust UI accordingly
    function checkViewport() {
        const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        
        if (vw <= 768) {
            // Mobile view adjustments
            if (navLinks && !navLinks.classList.contains('active')) {
                navLinks.style.display = 'none';
            }
        } else {
            // Desktop view adjustments
            if (navLinks) {
                navLinks.style.display = 'flex';
            }
        }
    }
    
    // Run on load and resize
    checkViewport();
    window.addEventListener('resize', checkViewport);
});
