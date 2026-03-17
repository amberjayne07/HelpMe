// Joseph Beattie - Logic and stuff for opening sheets, dialogs etc.

document.addEventListener('DOMContentLoaded', () => {

    document.addEventListener('click', (e) => {
        const triggerEl = e.target.closest('[data-trigger-click]');

        if (triggerEl) {
            e.preventDefault();

            const targetId = triggerEl.getAttribute('data-trigger-click');
            const targetBtn = document.getElementById(targetId);

            if (targetBtn) {
                targetBtn.click();
            } else {
                console.warn(`Target ID "${targetId}" not found in the DOM.`);
            }
        }
    });
});

