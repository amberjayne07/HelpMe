// Joseph Beattie - Post viewer actions. Liking, commenting etc.

document.addEventListener('click', async (e) => {

    const likeButton = e.target.closest('.js-like-button');
    if (likeButton) {
        e.preventDefault();
        e.stopPropagation();

        if (likeButton.dataset.loading === 'true') return;
        likeButton.dataset.loading = 'true';

        const url = likeButton.getAttribute('data-url');
        const icon = likeButton.querySelector('[data-lucide="heart"]');
        const countSpan = likeButton.querySelector('.js-like-count');
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {'X-CSRFToken': csrfToken}
            });

            const data = await response.json();
            const isAdding = data.liked;

            countSpan.style.transition = 'none';
            countSpan.style.opacity = '0';
            countSpan.style.transform = isAdding ? 'translateY(-10px)' : 'translateY(10px)';

            if (isAdding) {
                likeButton.classList.add('is-liked');
                icon.classList.add('animate-pop');
                setTimeout(() => icon.classList.remove('animate-pop'), 300);
            } else {
                likeButton.classList.remove('is-liked');
            }

            setTimeout(() => {
                countSpan.textContent = data.count;
                countSpan.style.transform = isAdding ? 'translateY(10px)' : 'translateY(-10px)';

                requestAnimationFrame(() => {
                    countSpan.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
                    countSpan.style.opacity = '1';
                    countSpan.style.transform = 'translateY(0)';
                });
            }, 100);

        } catch (error) {
            console.error('Like failed:', error);
        } finally {
            delete likeButton.dataset.loading;
        }
        return;
    }

    const commentProxy = e.target.closest('.js-proxy-comment');
    if (commentProxy) {
        e.preventDefault();
        e.stopPropagation();

        const targetId = commentProxy.getAttribute('data-target');
        const trigger = document.getElementById(`js-real-comment-trigger-${targetId}`);

        if (trigger) {
            trigger.click();
        }
    }
});