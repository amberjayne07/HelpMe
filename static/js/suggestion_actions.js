// Joseph Beattie - Responding to suggestions like and dislike with AJAX

document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', function(e) {
        // Find the closest button with our action class
        const btn = e.target.closest('.js-suggestion-action');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const container = btn.closest('.js-approval-container');
        const itemId = container.dataset.itemId;
        const action = btn.dataset.action;

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrfToken) {
            console.error("CSRF token not found. Ensure {% csrf_token %} is present on the page.");
            return;
        }

        // Prepare the request
        const formData = new FormData();
        formData.append('action', action);
        formData.append('csrfmiddlewaretoken', csrfToken);

        container.style.opacity = '0.5';
        container.style.pointerEvents = 'none';

        fetch(`/respond-to-suggestion/${itemId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                container.innerHTML = `
                    <div class="flex-1 text-center py-2 opacity-40 animate-in fade-in zoom-in duration-300">
                        <span class="text-sm font-semibold">
                            ${data.new_status}
                        </span>
                    </div>
                `;

                if (window.lucide) {
                    lucide.createIcons();
                }
            } else {
                alert("Error: " + (data.message || "Something went wrong"));
                container.style.opacity = '1';
                container.style.pointerEvents = 'auto';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.style.opacity = '1';
            container.style.pointerEvents = 'auto';
        });
    });
});