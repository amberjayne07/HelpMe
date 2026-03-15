// Joseph Beattie - Logic and stuff for opening sheets, dialogs etc.

document.addEventListener('DOMContentLoaded', () => {

    document.addEventListener('click', (e) => {
        // Check to find a trigger to click (found in the notifications sheet, dialogs)
        const triggerEl = e.target.closest('[data-trigger-click]');

        if (triggerEl) {
            e.preventDefault();

            // Get the element ID.
            const targetId = triggerEl.getAttribute('data-trigger-click');
            const targetBtn = document.getElementById(targetId);

            if (targetBtn) {
                targetBtn.click();
            } else {
                console.warn(`ID "${targetId}" not found.`);
            }
        }
    });

});