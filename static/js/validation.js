// Form Validation for Registration

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) {
        const usernameInput = document.getElementById('username');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        const strengthIndicator = document.getElementById('passwordStrength');
        
        // Real-time password strength indicator
        if (passwordInput && strengthIndicator) {
            passwordInput.addEventListener('input', function() {
                const password = this.value;
                const strength = calculatePasswordStrength(password);
                
                strengthIndicator.className = 'password-strength';
                
                if (password.length === 0) {
                    strengthIndicator.style.display = 'none';
                } else if (strength.score < 3) {
                    strengthIndicator.classList.add('weak');
                    strengthIndicator.textContent = '❌ Weak password: ' + strength.message;
                } else if (strength.score < 5) {
                    strengthIndicator.classList.add('medium');
                    strengthIndicator.textContent = '⚠️ Medium password: ' + strength.message;
                } else {
                    strengthIndicator.classList.add('strong');
                    strengthIndicator.textContent = '✅ Strong password!';
                }
            });
        }
        
        // Confirm password validation
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', function() {
                if (this.value !== passwordInput.value) {
                    this.setCustomValidity('Passwords do not match');
                } else {
                    this.setCustomValidity('');
                }
            });
            
            passwordInput.addEventListener('input', function() {
                if (confirmPasswordInput.value && confirmPasswordInput.value !== this.value) {
                    confirmPasswordInput.setCustomValidity('Passwords do not match');
                } else {
                    confirmPasswordInput.setCustomValidity('');
                }
            });
        }
        
        // Username validation
        if (usernameInput) {
            usernameInput.addEventListener('input', function() {
                const username = this.value;
                const regex = /^[a-zA-Z0-9_]+$/;
                
                if (username.length > 0 && !regex.test(username)) {
                    this.setCustomValidity('Username can only contain letters, numbers, and underscores');
                } else if (username.length > 0 && username.length < 3) {
                    this.setCustomValidity('Username must be at least 3 characters');
                } else if (username.length > 20) {
                    this.setCustomValidity('Username must be 20 characters or less');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
        
        // Form submission
        registerForm.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            this.classList.add('was-validated');
        });
    }
});

function calculatePasswordStrength(password) {
    let score = 0;
    const messages = [];
    
    // Length check
    if (password.length >= 8) {
        score++;
    } else {
        messages.push('at least 8 characters');
    }
    
    // Uppercase check
    if (/[A-Z]/.test(password)) {
        score++;
    } else {
        messages.push('uppercase letter');
    }
    
    // Lowercase check
    if (/[a-z]/.test(password)) {
        score++;
    } else {
        messages.push('lowercase letter');
    }
    
    // Number check
    if (/\d/.test(password)) {
        score++;
    } else {
        messages.push('number');
    }
    
    // Special character check (bonus)
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        score++;
    }
    
    let message = '';
    if (messages.length > 0) {
        message = 'Add: ' + messages.join(', ');
    }
    
    return {
        score: score,
        message: message
    };
}

// Transaction form validation
document.addEventListener('DOMContentLoaded', function() {
    const transactionForms = document.querySelectorAll('.transaction-form');
    
    transactionForms.forEach(form => {
        const amountInput = form.querySelector('input[name="amount"]');
        
        if (amountInput) {
            amountInput.addEventListener('input', function() {
                const amount = parseFloat(this.value);
                
                if (isNaN(amount) || amount <= 0) {
                    this.setCustomValidity('Amount must be greater than 0');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
    });
});

// Number input formatting
function formatNumberInput(input) {
    let value = input.value.replace(/[^\d.]/g, '');
    const parts = value.split('.');
    
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    
    if (parts[1] && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2);
    }
    
    input.value = value;
}

// Add formatting to all number inputs
document.addEventListener('DOMContentLoaded', function() {
    const numberInputs = document.querySelectorAll('input[type="number"]');
    
    numberInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const value = parseFloat(this.value);
                if (!isNaN(value)) {
                    this.value = value.toFixed(2);
                }
            }
        });
    });
});