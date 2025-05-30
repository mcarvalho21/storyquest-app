// Main JavaScript for StoryQuest

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Add animation classes on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('visible');
            }
        });
    };

    // Auto-save functionality for story editor
    const setupAutoSave = () => {
        const storyForm = document.getElementById('story-editor-form');
        if (!storyForm) return;

        let autoSaveTimer;
        const autoSaveDelay = 30000; // 30 seconds
        
        const triggerAutoSave = () => {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(() => {
                const storyId = storyForm.dataset.storyId;
                const formData = new FormData(storyForm);
                const storyContent = {
                    title: formData.get('title'),
                    content: JSON.parse(formData.get('content') || '{}')
                };
                
                fetch(`/progress/autosave/${storyId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(storyContent),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const saveIndicator = document.getElementById('save-indicator');
                        if (saveIndicator) {
                            saveIndicator.textContent = `Last saved: ${new Date().toLocaleTimeString()}`;
                            saveIndicator.classList.add('text-success');
                            setTimeout(() => {
                                saveIndicator.classList.remove('text-success');
                            }, 2000);
                        }
                    }
                })
                .catch(error => {
                    console.error('Auto-save failed:', error);
                });
            }, autoSaveDelay);
        };
        
        // Trigger auto-save on input changes
        storyForm.addEventListener('input', triggerAutoSave);
        
        // Initial auto-save setup
        triggerAutoSave();
    };

    // Story element drag and drop functionality
    const setupDragAndDrop = () => {
        const storyElementsContainer = document.getElementById('story-elements-container');
        if (!storyElementsContainer) return;
        
        new Sortable(storyElementsContainer, {
            animation: 150,
            handle: '.element-handle',
            ghostClass: 'element-ghost',
            onEnd: function(evt) {
                // Update element positions after drag
                const elements = storyElementsContainer.querySelectorAll('.element-card');
                elements.forEach((element, index) => {
                    element.querySelector('.element-position').value = index;
                });
            }
        });
    };

    // Character creator preview functionality
    const setupCharacterPreview = () => {
        const characterForm = document.getElementById('character-form');
        if (!characterForm) return;
        
        const nameInput = document.getElementById('character-name');
        const previewName = document.getElementById('preview-name');
        
        if (nameInput && previewName) {
            nameInput.addEventListener('input', () => {
                previewName.textContent = nameInput.value || 'Character Name';
            });
        }
        
        // Image preview
        const imageInput = document.getElementById('character-image');
        const previewImage = document.getElementById('preview-image');
        
        if (imageInput && previewImage) {
            imageInput.addEventListener('change', () => {
                const file = imageInput.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImage.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    };

    // Age-appropriate content filtering
    const setupContentFiltering = () => {
        const ageGroup = document.body.dataset.ageGroup;
        if (!ageGroup) return;
        
        const contentElements = document.querySelectorAll('[data-age-group]');
        contentElements.forEach(element => {
            const allowedAges = element.dataset.ageGroup.split(',');
            if (!allowedAges.includes(ageGroup)) {
                element.style.display = 'none';
            }
        });
    };

    // Initialize all interactive features
    const initializeFeatures = () => {
        animateOnScroll();
        setupAutoSave();
        setupDragAndDrop();
        setupCharacterPreview();
        setupContentFiltering();
        
        // Listen for scroll events
        window.addEventListener('scroll', animateOnScroll);
    };

    // Run initialization
    initializeFeatures();
});
