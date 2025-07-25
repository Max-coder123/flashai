const loginModal = document.getElementById('login-modal');
const openModalBtn = document.getElementById('open-modal');
const closeModalBtn = document.getElementById('close-modal');
const toggleFormText = document.getElementById('toggleForm');
const formTitle = document.getElementById('formTitle');
const authForm = document.getElementById('authForm'); // Added this

let isLogin = true;

document.addEventListener('DOMContentLoaded', function () {
    const feedbackButton = document.getElementById('feedback-button');
    const feedbackDropdown = document.getElementById('feedback-dropdown');

    feedbackButton.addEventListener('click', function () {
        if (feedbackDropdown.style.display === 'none' || feedbackDropdown.style.display === '') {
            feedbackDropdown.style.display = 'block';
        }
        else {
            feedbackDropdown.style.display = 'none';
        }
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const productsButton = document.getElementById('products-button');
    const productsDropdown = document.getElementById('products-dropdown');

    productsButton.addEventListener('click', function () {
        if (productsDropdown.style.display === 'none' || productsDropdown.style.display === '') {
            productsDropdown.style.display = 'block';
        } else {
            productsDropdown.style.display = 'none';
        }
    });
});

if (openModalBtn) {
    openModalBtn.addEventListener('click', () => {
        loginModal.style.display = 'flex';
    });
}

if (closeModalBtn) {
    closeModalBtn.addEventListener('click', () => {
        loginModal.style.display = 'none';
    });
}

if (authForm) {
    authForm.addEventListener('submit', (e) => {
        e.preventDefault();
        console.log("Form submitted:", document.getElementById('email').value, document.getElementById('password').value);
    });
}

if (toggleFormText) {
    toggleFormText.addEventListener('click', () => {
        if (isLogin) {
            formTitle.textContent = 'Sign Up';
            document.querySelector('.highlight').textContent = 'Login';
            toggleFormText.innerHTML = 'Already have an account? <span class="highlight">Login</span>';
            isLogin = false;
        } else {
            formTitle.textContent = 'Login';
            document.querySelector('.highlight').textContent = 'Sign up';
            toggleFormText.innerHTML = "Don't have an account? <span class=\"highlight\">Sign up</span>";
            isLogin = true;
        }
    });
}
