document.addEventListener('DOMContentLoaded', function() {
    // Form validation for login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            
            let isValid = true;
            
            // Clear previous error messages
            clearErrors();
            
            if (username === '') {
                displayError('username', 'Username is required');
                isValid = false;
            }
            
            if (password === '') {
                displayError('password', 'Password is required');
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Form validation for signup form
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(event) {
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();
            const confirmPassword = document.getElementById('confirm_password').value.trim();
            
            let isValid = true;
            
            // Clear previous error messages
            clearErrors();
            
            if (username === '') {
                displayError('username', 'Username is required');
                isValid = false;
            } else if (username.length < 3) {
                displayError('username', 'Username must be at least 3 characters');
                isValid = false;
            }
            
            if (email === '') {
                displayError('email', 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email)) {
                displayError('email', 'Please enter a valid email address');
                isValid = false;
            }
            
            if (password === '') {
                displayError('password', 'Password is required');
                isValid = false;
            } else if (password.length < 6) {
                displayError('password', 'Password must be at least 6 characters');
                isValid = false;
            }
            
            if (confirmPassword === '') {
                displayError('confirm_password', 'Please confirm your password');
                isValid = false;
            } else if (password !== confirmPassword) {
                displayError('confirm_password', 'Passwords do not match');
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Helper functions
    function displayError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        errorDiv.textContent = message;
        
        field.classList.add('error');
        field.style.borderColor = '#e74c3c';
        
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearErrors() {
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(function(error) {
            error.remove();
        });
        
        const errorFields = document.querySelectorAll('.error');
        errorFields.forEach(function(field) {
            field.classList.remove('error');
            field.style.borderColor = '';
        });
    }
    
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Password visibility toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const passwordField = document.getElementById(this.getAttribute('data-toggle'));
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            
            // Change the icon
            const icon = this.querySelector('i');
            if (type === 'text') {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
});
