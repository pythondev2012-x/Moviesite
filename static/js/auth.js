// Auth Pages JavaScript

document.addEventListener('DOMContentLoaded', function() {
  console.log('Auth.js loaded');

  // Password toggle functionality
  const toggleButtons = document.querySelectorAll('.password-toggle');
  console.log('Toggle buttons found:', toggleButtons.length);

  toggleButtons.forEach((button, index) => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();

      // Find the input within the same wrapper
      const wrapper = this.parentElement;
      const input = wrapper.querySelector('input[type="password"], input[type="text"]');
      const icon = this.querySelector('i');

      console.log('Button clicked, index:', index, 'Input:', input, 'Icon:', icon);

      if (input && icon) {
        if (input.type === 'password') {
          input.type = 'text';
          icon.classList.remove('bi-eye');
          icon.classList.add('bi-eye-slash');
          console.log('Password shown');
        } else {
          input.type = 'password';
          icon.classList.remove('bi-eye-slash');
          icon.classList.add('bi-eye');
          console.log('Password hidden');
        }
      } else {
        console.log('Input or icon not found');
      }
    });
  });

  // Form validation for signup
  const signupForm = document.getElementById('signupForm');
  if (signupForm) {
    signupForm.addEventListener('submit', function(e) {
      const password = document.getElementById('password');
      const passwordConfirm = document.getElementById('password_confirm');
      
      if (password.value !== passwordConfirm.value) {
        e.preventDefault();
        alert('Parollar mos kelmaydi!');
        return false;
      }
      
      if (password.value.length < 6) {
        e.preventDefault();
        alert('Parol kamida 6 ta belgidan iborat bo\'lishi kerak!');
        return false;
      }
    });
  }

  // Input focus effects
  const inputs = document.querySelectorAll('.form-control');
  inputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.querySelector('.input-icon')?.style.color = '#e50914';
    });
    
    input.addEventListener('blur', function() {
      this.parentElement.querySelector('.input-icon')?.style.color = '#a0a0a0';
    });
  });

  // Add loading state to buttons
  const authButtons = document.querySelectorAll('.auth-btn, .btn-google');
  authButtons.forEach(button => {
    button.addEventListener('click', function() {
      if (this.type === 'submit') {
        this.innerHTML = '<i class="bi bi-arrow-repeat"></i> Yuborilmoqda...';
        this.disabled = true;
        this.style.opacity = '0.7';
      }
    });
  });
});

// Password toggle function for inline onclick handlers
function togglePassword(inputId, button) {
  const input = document.getElementById(inputId);
  const icon = button.querySelector('i');
  
  if (input && icon) {
    if (input.type === 'password') {
      input.type = 'text';
      icon.classList.remove('bi-eye');
      icon.classList.add('bi-eye-slash');
    } else {
      input.type = 'password';
      icon.classList.remove('bi-eye-slash');
      icon.classList.add('bi-eye');
    }
  }
}
