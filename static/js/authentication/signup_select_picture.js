// Joseph Beattie - Select preview image within the registration form.

document.addEventListener('DOMContentLoaded', () => {
    const profileInput = document.getElementById('id_picture');
    const profilePreview = document.getElementById('profile_preview');
    const changeBtn = document.getElementById('change_pic_btn');
    const spinner = document.getElementById('preview_spinner');

    if (changeBtn && profileInput) {
        // Allow the hidden input button to be clicked instead of the styled button.
        changeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            profileInput.click();
        });

        // Change the preview image after the file is pulled
        profileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                // Show spinner and hide preview of old with opacity,
                if (spinner) spinner.classList.remove('hidden');
                profilePreview.style.opacity = '0.1';

                const objectUrl = URL.createObjectURL(file);
                profilePreview.src = objectUrl;

                // Hide the spinner when the preview has loaded.
                profilePreview.onload = () => {
                    if (spinner) spinner.classList.add('hidden');
                    profilePreview.style.opacity = '1';

                    // Remove the object from memory. Not needed
                    URL.revokeObjectURL(objectUrl);
                };
            }
        });
    }
});