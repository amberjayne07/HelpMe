document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (e) => {
        // Proxy Create
        const createProxy = e.target.closest('.js-proxy-create');
        if (createProxy) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('js-real-create-trigger').click();
        }

        // Proxy Delete
        const deleteProxy = e.target.closest('.js-proxy-delete');
        if (deleteProxy) {
            e.preventDefault();
            e.stopPropagation();
            const targetId = deleteProxy.getAttribute('data-target');
            document.getElementById(`js-real-delete-${targetId}`).click();
        }

        // Confirm Delete
        const confirmDelete = e.target.closest('.js-confirm-delete');
        if (confirmDelete) {
            e.preventDefault();
            e.stopPropagation();
            const targetId = confirmDelete.getAttribute('data-target');
            document.getElementById(`delete-post-form-${targetId}`).submit();
        }

        // Proxy Edit
        const editProxy = e.target.closest('.js-proxy-edit');
        if (editProxy) {
            e.preventDefault();
            e.stopPropagation();
            const targetId = editProxy.getAttribute('data-target');
            document.getElementById(`js-real-edit-trigger-${targetId}`).click();
        }
    });
});