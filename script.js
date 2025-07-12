// SnapSaver JavaScript

// Theme Management
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme();
        this.setupToggle();
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        const themeIcon = document.querySelector('#themeToggle i');
        if (themeIcon) {
            themeIcon.className = this.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.theme);
        this.applyTheme();
    }

    setupToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }
}

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        this.container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: duration
        });
        
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

// URL Validator
class URLValidator {
    static isValid(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    static addProtocol(url) {
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            return 'https://' + url;
        }
        return url;
    }

    static clean(url) {
        return url.trim().replace(/\s+/g, '');
    }
}

// Download Manager
class DownloadManager {
    constructor() {
        this.activeDownloads = new Set();
    }

    async download(url, audioOnly = false) {
        if (this.activeDownloads.has(url)) {
            toastManager.show('Download already in progress', 'warning');
            return;
        }

        this.activeDownloads.add(url);
        
        try {
            const downloadUrl = `/download?url=${encodeURIComponent(url)}&audio_only=${audioOnly}`;
            
            // Create download link
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = '';
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            toastManager.show('Download started successfully!', 'success');
            
        } catch (error) {
            console.error('Download error:', error);
            toastManager.show('Download failed. Please try again.', 'danger');
        } finally {
            this.activeDownloads.delete(url);
        }
    }
}

// Newsletter Manager
class NewsletterManager {
    constructor() {
        this.setupSubscription();
    }

    setupSubscription() {
        const subscribeBtn = document.querySelector('#newsletterEmail + button');
        if (subscribeBtn) {
            subscribeBtn.addEventListener('click', () => this.subscribe());
        }
        
        const emailInput = document.getElementById('newsletterEmail');
        if (emailInput) {
            emailInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.subscribe();
                }
            });
        }
    }

    subscribe() {
        const emailInput = document.getElementById('newsletterEmail');
        const email = emailInput.value.trim();
        
        if (!email) {
            toastManager.show('Please enter your email address', 'warning');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            toastManager.show('Please enter a valid email address', 'danger');
            return;
        }
        
        // Send subscription request to backend
        fetch('/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `email=${encodeURIComponent(email)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                toastManager.show(data.error, 'danger');
            } else {
                toastManager.show(data.message, 'success');
                emailInput.value = '';
            }
        })
        .catch(error => {
            console.error('Newsletter subscription error:', error);
            toastManager.show('Subscription failed. Please try again.', 'danger');
        });
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// Form Enhancement
class FormEnhancer {
    constructor() {
        this.setupFormValidation();
        this.setupFormSubmission();
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => this.validateForm(e));
        });
    }

    setupFormSubmission() {
        const urlForm = document.getElementById('urlForm');
        if (urlForm) {
            urlForm.addEventListener('submit', (e) => this.handleUrlSubmission(e));
        }
    }

    validateForm(e) {
        const form = e.target;
        const urlInput = form.querySelector('input[type="url"]');
        
        if (urlInput) {
            const url = URLValidator.clean(urlInput.value);
            
            if (!url) {
                e.preventDefault();
                toastManager.show('Please enter a URL', 'warning');
                return false;
            }
            
            const fullUrl = URLValidator.addProtocol(url);
            
            if (!URLValidator.isValid(fullUrl)) {
                e.preventDefault();
                toastManager.show('Please enter a valid URL', 'danger');
                return false;
            }
            
            urlInput.value = fullUrl;
        }
        
        return true;
    }

    handleUrlSubmission(e) {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            setTimeout(() => {
                submitBtn.disabled = false;
            }, 3000);
        }
    }
}

// Utility Functions
class Utils {
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    static formatDuration(seconds) {
        if (!seconds) return '0:00';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }

    static timeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    }

    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            toastManager.show('Copied to clipboard!', 'success');
        }).catch(() => {
            toastManager.show('Failed to copy to clipboard', 'danger');
        });
    }
}

// Analytics (placeholder for future implementation)
class Analytics {
    static trackEvent(eventName, eventData = {}) {
        // Placeholder for Google Analytics or other tracking
        console.log('Analytics Event:', eventName, eventData);
    }

    static trackDownload(platform, url) {
        this.trackEvent('download', {
            platform: platform,
            url: url
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize managers
    window.themeManager = new ThemeManager();
    window.toastManager = new ToastManager();
    window.downloadManager = new DownloadManager();
    window.newsletterManager = new NewsletterManager();
    window.formEnhancer = new FormEnhancer();
    
    // Add global utility functions
    window.Utils = Utils;
    window.Analytics = Analytics;
    
    // Setup keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const urlInput = document.querySelector('input[name="url"]');
            if (urlInput) {
                urlInput.focus();
            }
        }
        
        // Ctrl/Cmd + D to toggle theme
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            themeManager.toggleTheme();
        }
    });
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Show welcome message
    if (localStorage.getItem('firstVisit') !== 'false') {
        setTimeout(() => {
            toastManager.show('Welcome to SnapSaver! Paste any social media URL to get started.', 'info', 8000);
            localStorage.setItem('firstVisit', 'false');
        }, 1000);
    }
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    toastManager.show('An error occurred. Please refresh the page.', 'danger');
});

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // navigator.serviceWorker.register('/sw.js')
        //     .then(function(registration) {
        //         console.log('ServiceWorker registration successful');
        //     })
        //     .catch(function(err) {
        //         console.log('ServiceWorker registration failed');
        //     });
    });
}
