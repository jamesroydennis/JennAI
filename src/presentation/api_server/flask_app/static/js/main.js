document.addEventListener('DOMContentLoaded', function() {
    // Set current year in footer
    const yearSpan = document.getElementById('currentYear');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    const flashContainer = document.getElementById('flash-messages-container');
    const runTestsButton = document.getElementById('run-tests-button');
    const runTestsForm = document.getElementById('run-tests-form');
    const loadingSpinner = document.getElementById('loading-spinner');
    const loadingMessage = document.getElementById('loading-message');

    // Function to show spinner and disable button
    function showLoadingState() {
        if (loadingSpinner) loadingSpinner.classList.remove('spinner-hidden');
        if (loadingMessage) loadingMessage.classList.remove('spinner-hidden');
        if (runTestsButton) runTestsButton.disabled = true;
    }

    // Function to hide spinner and enable button
    function hideLoadingState() {
        if (loadingSpinner) loadingSpinner.classList.add('spinner-hidden');
        if (loadingMessage) loadingMessage.classList.add('spinner-hidden');
        if (runTestsButton) runTestsButton.disabled = false;
    }

    // Check for a message indicating a test run has started
    if (flashContainer && flashContainer.innerText.includes('Test run started')) {
        // Start polling for status
        showLoadingState();
        pollTestStatus();
    } else {
        // Ensure button is enabled and spinner is hidden on fresh page load
        hideLoadingState();
    }

    // Add event listener to the form to immediately show loading state on submission
    if (runTestsForm) {
        runTestsForm.addEventListener('submit', function() {
            showLoadingState();
            // The page will redirect, so polling will start on the next page load if the flash message is present.
        });
    }
});

function pollTestStatus() {
    const flashContainer = document.getElementById('flash-messages-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const loadingMessage = document.getElementById('loading-message');
    const runTestsButton = document.getElementById('run-tests-button');

    let pollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/test_status');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();

            if (data.status === 'success' || data.status === 'failure') {
                clearInterval(pollingInterval);
                flashContainer.innerHTML = `<div class="flash ${data.status}">${data.message}</div>`;
                // Hide spinner and enable button
                if (loadingSpinner) loadingSpinner.classList.add('spinner-hidden');
                if (loadingMessage) loadingMessage.classList.add('spinner-hidden');
                if (runTestsButton) runTestsButton.disabled = false;
            }
            // If status is 'running', do nothing and let the interval continue.
        } catch (error) {
            console.error('Error polling for test status:', error);
            clearInterval(pollingInterval); // Stop polling on error
            flashContainer.innerHTML = `<div class="flash error">Error checking test status.</div>`;
            // Hide spinner and enable button on error
            if (loadingSpinner) loadingSpinner.classList.add('spinner-hidden');
            if (loadingMessage) loadingMessage.classList.add('spinner-hidden');
            if (runTestsButton) runTestsButton.disabled = false;
        }
    }, 3000); // Poll every 3 seconds
}