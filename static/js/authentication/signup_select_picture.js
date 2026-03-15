// Joseph Beattie - Alpine.js script for controlling poll toggle.

document.addEventListener('DOMContentLoaded', () => {
    const profileInput = document.getElementById('id_picture');
    const profilePreview = document.getElementById('profile_preview');
    const changeBtn = document.getElementById('change_pic_btn');

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
                const reader = new FileReader();
                reader.onload = (e) => {
                    profilePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
});