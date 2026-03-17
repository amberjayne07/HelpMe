// Joseph Beattie - Account actions. Basically just used for deleting accounts :)

document.addEventListener('click', (e) => {
    const deleteAccountProxy = e.target.closest('.js-proxy-delete-account');
    if (deleteAccountProxy) {
        e.preventDefault();
        const trigger = document.getElementById('js-real-delete-account-trigger');
        if (trigger) trigger.click();
    }

    const confirmDeleteAccount = e.target.closest('.js-confirm-delete-account');
    if (confirmDeleteAccount) {
        e.preventDefault();
        const form = document.getElementById('delete-account-form');
        if (form) form.submit();
    }
});