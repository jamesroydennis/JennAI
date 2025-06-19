console.log("JennAI Flask App: main.js loaded successfully.");

document.addEventListener('DOMContentLoaded', function() {
    const jsMessageDiv = document.getElementById('js-message');
    if (jsMessageDiv) {
        jsMessageDiv.textContent = 'JavaScript from static/js/main.js is executing!';
    }

    const yearSpan = document.getElementById('currentYear');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
});