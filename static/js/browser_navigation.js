// Joseph Beattie - Handles back button for account upsell maybe later button.

document.addEventListener('DOMContentLoaded', function() {
    const backButton = document.getElementById('back-btn');

    if (backButton) {
        backButton.addEventListener('click', function() {
            const homeUrl = backButton.getAttribute('data-home-url');

            if (document.referrer && window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = homeUrl;
            }
        });
    }
});