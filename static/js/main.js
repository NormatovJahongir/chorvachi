// CHORVA FERMERI PRO v2.0 - MOBILE OPTIMIZED

// ==================== NUMBER FORMATTING ====================
function formatNumber(number) {
    if (!number) return '0';
    return parseFloat(number).toLocaleString('en-US');
}

function parseFormattedNumber(formatted) {
    if (!formatted) return 0;
    return parseFloat(String(formatted).replace(/,/g, ''));
}

function setupNumberInput(input) {
    input.addEventListener('keypress', function(e) {
        if (e.key !== 'e' && e.key !== 'E' && e.key !== '+' && e.key !== '-') {
            if (!/[\d.]/.test(e.key)) {
                e.preventDefault();
            }
        } else {
            e.preventDefault();
        }
    });

    input.addEventListener('focus', function() {
        let val = this.value.replace(/,/g, '');
        this.value = val;
    });

    input.addEventListener('blur', function() {
        let val = parseFloat(this.value.replace(/,/g, ''));
        if (!isNaN(val)) {
            this.value = formatNumber(val);
        }
    });
}

// ==================== MODAL CLASS ====================
class Modal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.closeBtn = this.modal?.querySelector('.modal-close');
        
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.hide());
        }
        
        // Close on background click
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });
        
        // Prevent body scroll when modal open
        this.originalOverflow = '';
    }
    
    show() {
        if (this.modal) {
            this.modal.classList.add('show');
            this.originalOverflow = document.body.style.overflow;
            document.body.style.overflow = 'hidden';
            
            // Add haptic feedback for mobile
            if (navigator.vibrate) {
                navigator.vibrate(10);
            }
        }
    }
    
    hide() {
        if (this.modal) {
            this.modal.classList.remove('show');
            document.body.style.overflow = this.originalOverflow;
            
            // Haptic feedback
            if (navigator.vibrate) {
                navigator.vibrate(10);
            }
        }
    }
}

// ==================== API HELPERS ====================
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showAlert('Xatolik yuz berdi!', 'danger');
        throw error;
    }
}

// ==================== ALERTS ====================
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    alertDiv.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;
    
    // Insert at top of main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
        
        // Haptic feedback
        if (navigator.vibrate) {
            navigator.vibrate(type === 'danger' ? [50, 100, 50] : 20);
        }
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            alertDiv.style.opacity = '0';
            setTimeout(() => alertDiv.remove(), 300);
        }, 3000);
    }
}

// ==================== TOUCH & SWIPE ====================
class SwipeHandler {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            threshold: 50,
            onSwipeLeft: options.onSwipeLeft || null,
            onSwipeRight: options.onSwipeRight || null
        };
        
        this.touchStartX = 0;
        this.touchEndX = 0;
        
        this.element.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        this.element.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, { passive: true });
    }
    
    handleSwipe() {
        const diff = this.touchStartX - this.touchEndX;
        
        if (Math.abs(diff) > this.options.threshold) {
            if (diff > 0 && this.options.onSwipeLeft) {
                this.options.onSwipeLeft();
            } else if (diff < 0 && this.options.onSwipeRight) {
                this.options.onSwipeRight();
            }
        }
    }
}

// ==================== PULL TO REFRESH ====================
class PullToRefresh {
    constructor(callback) {
        this.callback = callback;
        this.startY = 0;
        this.isRefreshing = false;
        
        document.addEventListener('touchstart', (e) => {
            this.startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && !this.isRefreshing) {
                const currentY = e.touches[0].clientY;
                if (currentY - this.startY > 100) {
                    this.triggerRefresh();
                }
            }
        }, { passive: true });
    }
    
    async triggerRefresh() {
        if (this.isRefreshing) return;
        
        this.isRefreshing = true;
        
        // Haptic feedback
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
        
        await this.callback();
        
        setTimeout(() => {
            this.isRefreshing = false;
        }, 1000);
    }
}

// ==================== SEARCH WITH DEBOUNCE ====================
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function setupSearch(inputId, callback) {
    const input = document.getElementById(inputId);
    const clearBtn = document.querySelector('.search-clear');
    
    if (!input) return;
    
    const debouncedSearch = debounce((value) => {
        callback(value);
    }, 300);
    
    input.addEventListener('input', function() {
        const value = this.value.trim();
        
        // Show/hide clear button
        if (clearBtn) {
            if (value) {
                clearBtn.classList.add('show');
            } else {
                clearBtn.classList.remove('show');
            }
        }
        
        debouncedSearch(value);
    });
    
    // Clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            input.value = '';
            clearBtn.classList.remove('show');
            callback('');
            input.focus();
        });
    }
}

// ==================== BOTTOM NAV ACTIVE STATE ====================
function initBottomNav() {
    const currentPage = window.location.pathname;
    const navItems = document.querySelectorAll('.bottom-nav-item');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPage.includes(href.replace('/', ''))) {
            item.classList.add('active');
        }
        
        // Haptic feedback on click
        item.addEventListener('click', () => {
            if (navigator.vibrate) {
                navigator.vibrate(10);
            }
        });
    });
}

// ==================== LANGUAGE CHANGE ====================
async function changeLanguage(lang) {
    try {
        await apiRequest('/api/language', {
            method: 'POST',
            body: JSON.stringify({ language: lang })
        });
        
        showAlert('Til o\'zgartirildi', 'success');
        
        setTimeout(() => {
            location.reload();
        }, 500);
    } catch (error) {
        showAlert('Xatolik yuz berdi', 'danger');
    }
}

// ==================== HAPTIC FEEDBACK ====================
function hapticFeedback(pattern = 10) {
    if (navigator.vibrate) {
        navigator.vibrate(pattern);
    }
}

// Add haptic to all buttons
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('button, .btn, .bottom-nav-item');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => hapticFeedback(10));
    });
});

// ==================== FORM VALIDATION ====================
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = 'var(--danger)';
            isValid = false;
            
            // Haptic feedback for error
            hapticFeedback([50, 100, 50]);
        } else {
            field.style.borderColor = 'var(--border)';
        }
    });
    
    return isValid;
}

// ==================== CONFIRM DELETE ====================
function confirmDelete(message = "O'chirishni tasdiqlaysizmi?") {
    return new Promise((resolve) => {
        const result = confirm(message);
        if (result) {
            hapticFeedback([30, 50, 30]);
        }
        resolve(result);
    });
}

// ==================== AUTO RESIZE TEXTAREA ====================
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

document.addEventListener('DOMContentLoaded', () => {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
    });
});

// ==================== OFFLINE DETECTION ====================
window.addEventListener('online', () => {
    showAlert('Internet aloqasi tiklandi', 'success');
});

window.addEventListener('offline', () => {
    showAlert('Internet aloqasi yo\'q', 'warning');
});

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    // Bottom nav
    initBottomNav();
    
    // Number inputs
    const numberInputs = document.querySelectorAll('input[type="text"][name*="price"], input[type="text"][name*="cost"], input[type="text"][name*="amount"]');
    numberInputs.forEach(input => setupNumberInput(input));
    
    // Prevent zoom on input focus (iOS)
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.fontSize = '16px';
        });
    });
    
    console.log('🐄 CHORVA FERMERI PRO - Mobile Optimized');
});

// ==================== EXPORT ====================
window.chorvaApp = {
    formatNumber,
    parseFormattedNumber,
    Modal,
    apiRequest,
    showAlert,
    SwipeHandler,
    PullToRefresh,
    setupSearch,
    changeLanguage,
    hapticFeedback,
    validateForm,
    confirmDelete
};
