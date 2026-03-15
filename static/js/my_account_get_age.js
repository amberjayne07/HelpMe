// Joseph Beattie - Get user's age based on their date of birth.

document.addEventListener('DOMContentLoaded', function() {
    const ageDisplay = document.getElementById('user_age');
    const dobString = window.userBirthday;

    if (dobString && dobString !== "" && ageDisplay) {
        const birthDate = new Date(dobString);
        const today = new Date();

        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();

        // If not at date of birth (birthday) decrease age by 1.
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }

        ageDisplay.textContent = age;
    } else if (ageDisplay) {
        ageDisplay.textContent = "Age unknown";
    }
});