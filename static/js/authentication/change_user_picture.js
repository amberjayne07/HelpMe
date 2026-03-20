// Joseph Beattie - Change user picture. Handles button click events for c-button to pull input from html and open the file picker.

document.addEventListener('DOMContentLoaded', function() {
    const triggerBtn = document.getElementById('js-change-picture-trigger');
    const fileInput = document.getElementById('picture-input');
    const pictureForm = document.getElementById('change-user-picture-form');

    if (triggerBtn && fileInput) {
        triggerBtn.addEventListener('click', function() {
            fileInput.click();
        });
    }

    if (fileInput && pictureForm) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files && fileInput.files.length > 0) {
                pictureForm.submit();
            }
        });
    }
});