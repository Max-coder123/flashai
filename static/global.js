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

    if (productsButton && productsDropdown) {
        productsButton.addEventListener('click', function () {
            if (productsDropdown.style.display === 'none' || productsDropdown.style.display === '') {
                productsDropdown.style.display = 'block';
            } else {
                productsDropdown.style.display = 'none';
            }
        });
    }

    // Mobile menu toggle and panels
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', () => {
            const isHidden = mobileMenu.hasAttribute('hidden');
            if (isHidden) {
                mobileMenu.removeAttribute('hidden');
                mobileMenuToggle.setAttribute('aria-expanded', 'true');
            } else {
                mobileMenu.setAttribute('hidden', '');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            }
        });

        // Hide menu if viewport grows beyond mobile breakpoint
        const handleResize = () => {
            if (window.innerWidth > 700) {
                if (!mobileMenu.hasAttribute('hidden')) {
                    mobileMenu.setAttribute('hidden', '');
                    mobileMenuToggle.setAttribute('aria-expanded', 'false');
                }
            }
        };
        window.addEventListener('resize', handleResize);
        // Initial check
        handleResize();
    }

    const mobileProductsToggle = document.getElementById('mobile-products-toggle');
    const mobileProductsPanel = document.getElementById('mobile-products-panel');
    if (mobileProductsToggle && mobileProductsPanel) {
        mobileProductsToggle.addEventListener('click', () => {
            if (mobileProductsPanel.hasAttribute('hidden')) {
                mobileProductsPanel.removeAttribute('hidden');
            } else {
                mobileProductsPanel.setAttribute('hidden', '');
            }
        });
    }

    const mobileFeedbackToggle = document.getElementById('mobile-feedback-toggle');
    const mobileFeedbackPanel = document.getElementById('mobile-feedback-panel');
    if (mobileFeedbackToggle && mobileFeedbackPanel) {
        mobileFeedbackToggle.addEventListener('click', () => {
            if (mobileFeedbackPanel.hasAttribute('hidden')) {
                mobileFeedbackPanel.removeAttribute('hidden');
            } else {
                mobileFeedbackPanel.setAttribute('hidden', '');
            }
        });
    }

    const mobileFeedbackForm = document.getElementById('mobile-feedback-form');
    if (mobileFeedbackForm) {
        mobileFeedbackForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const name = document.getElementById('mobile-feedback-name').value;
            const subject = document.getElementById('mobile-feedback-subject').value;
            const message = document.getElementById('mobile-feedback-message').value;

            fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, subject, message })
            })
                .then(r => {
                    if (!r.ok) throw new Error('Network response was not ok');
                    return r.json();
                })
                .then(() => {
                    alert('Feedback sent successfully!');
                    mobileFeedbackForm.reset();
                })
                .catch(() => alert('Error sending feedback. Please try again later.'));
        });
    }

    const mobileLogout = document.getElementById('mobile-logout');
    if (mobileLogout) {
        mobileLogout.addEventListener('click', () => {
            fetch('/api/logout', { method: 'GET', credentials: 'include' })
                .then(res => res.json())
                .then(data => { if (data.message === 'Logged out successfully') window.location = '/'; });
        });
    }
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
