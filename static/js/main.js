// Main JavaScript file for ThriveMate

// Global variables
let currentUser = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Check if the user is authenticated
    checkAuthStatus();
    
    // Add event listeners
    setupEventListeners();
});

// Check if the user is authenticated
function checkAuthStatus() {
    // Firebase auth status observer
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            // User is signed in
            currentUser = user;
            updateUIForAuthenticatedUser(user);
        } else {
            // User is signed out
            currentUser = null;
            updateUIForUnauthenticatedUser();
        }
    });
}

// Update UI elements for authenticated user
function updateUIForAuthenticatedUser(user) {
    const authButtons = document.querySelectorAll('.auth-buttons');
    const userInfo = document.querySelectorAll('.user-info');
    const userNameElements = document.querySelectorAll('.user-name');
    const userEmailElements = document.querySelectorAll('.user-email');
    
    // Hide auth buttons and show user info
    authButtons.forEach(el => el.classList.add('d-none'));
    userInfo.forEach(el => el.classList.remove('d-none'));
    
    // Set user name and email
    if (user.displayName) {
        userNameElements.forEach(el => el.textContent = user.displayName);
    } else {
        userNameElements.forEach(el => el.textContent = 'User');
    }
    
    if (user.email) {
        userEmailElements.forEach(el => el.textContent = user.email);
    }
    
    // Show features that require authentication
    document.querySelectorAll('.auth-required').forEach(el => {
        el.classList.remove('d-none');
    });
}

// Update UI elements for unauthenticated user
function updateUIForUnauthenticatedUser() {
    const authButtons = document.querySelectorAll('.auth-buttons');
    const userInfo = document.querySelectorAll('.user-info');
    
    // Show auth buttons and hide user info
    authButtons.forEach(el => el.classList.remove('d-none'));
    userInfo.forEach(el => el.classList.add('d-none'));
    
    // Hide features that require authentication
    document.querySelectorAll('.auth-required').forEach(el => {
        el.classList.add('d-none');
    });
}

// Sign in with Google
function signInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth().signInWithPopup(provider)
        .then((result) => {
            // This gives you a Google Access Token
            const credential = result.credential;
            const token = credential.accessToken;
            
            // The signed-in user info
            const user = result.user;
            showToast('Success', 'Signed in successfully!');
        })
        .catch((error) => {
            // Handle Errors here
            const errorCode = error.code;
            const errorMessage = error.message;
            showToast('Error', errorMessage);
        });
}

// Sign out
function signOut() {
    firebase.auth().signOut()
        .then(() => {
            showToast('Success', 'Signed out successfully!');
        })
        .catch((error) => {
            showToast('Error', error.message);
        });
}

// Show toast notification
function showToast(title, message) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Setup event listeners
function setupEventListeners() {
    // Sign in button
    const signInButtons = document.querySelectorAll('.btn-sign-in');
    signInButtons.forEach(button => {
        button.addEventListener('click', signInWithGoogle);
    });
    
    // Sign out button
    const signOutButtons = document.querySelectorAll('.btn-sign-out');
    signOutButtons.forEach(button => {
        button.addEventListener('click', signOut);
    });
}

// Format date string
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Format relative time (e.g., "2 days ago")
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'just now';
    }
    
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
        return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
    }
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
        return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    }
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 30) {
        return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
    }
    
    const diffInMonths = Math.floor(diffInDays / 30);
    if (diffInMonths < 12) {
        return `${diffInMonths} month${diffInMonths > 1 ? 's' : ''} ago`;
    }
    
    const diffInYears = Math.floor(diffInMonths / 12);
    return `${diffInYears} year${diffInYears > 1 ? 's' : ''} ago`;
}
