// Joseph Beattie - Post creator actions. Edit or delete posts.

document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (e) => {
        const createProxy = e.target.closest('.js-proxy-create');
        if (createProxy) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('js-real-create-trigger').click();
        }

        const deleteProxy = e.target.closest('.js-proxy-delete');
        if (deleteProxy) {
            e.preventDefault();
            e.stopPropagation();
            const targetId = deleteProxy.getAttribute('data-target');
            document.getElementById(`js-real-delete-${targetId}`).click();
        }

        const confirmDelete = e.target.closest('.js-confirm-delete');
        if (confirmDelete) {
            e.preventDefault();
            e.stopPropagation();
            const targetId = confirmDelete.getAttribute('data-target');
            document.getElementById(`delete-post-form-${targetId}`).submit();
        }

        const editProxy = e.target.closest('.js-proxy-edit');
        if (editProxy) {
            e.preventDefault();
            e.stopPropagation();
            const targetId = editProxy.getAttribute('data-target');
            document.getElementById(`js-real-edit-trigger-${targetId}`).click();
        }

        // Account deletion below.
        const deleteAccountProxy = e.target.closest('.js-proxy-delete-account');
        if (deleteAccountProxy) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('js-real-delete-account-trigger').click();
        }

        const confirmDeleteAccount = e.target.closest('.js-confirm-delete-account');
        if (confirmDeleteAccount) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('delete-account-form').submit();
        }
    });
});