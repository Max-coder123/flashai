const loginModal = document.getElementById('login-modal');
const openModalBtn = document.getElementById('open-modal');
const closeModalBtn = document.getElementById('close-modal');
const toggleFormText = document.getElementById('toggleForm');
const formTitle = document.getElementById('formTitle');
const authForm = document.getElementById('authForm'); // Added this

let isLogin = true;

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

document.getElementById('toggle-taskbar').addEventListener('click', function () {
    const taskbar = document.getElementById('taskbar');
    const mainContent = document.getElementById('main-content');
    taskbar.classList.toggle('minimized');
    mainContent.classList.toggle('expanded');
});
