// Joseph Beattie - Global Notification removal logic

document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', async (e) => {
        const btn = e.target.closest('.dismiss-notif-btn, .clear-history-btn, .mark-all-btn');
        if (!btn) return;

        e.preventDefault();
        const isHistory = btn.classList.contains('clear-history-btn');
        const isMarkAll = btn.classList.contains('mark-all-btn');
        const isSingle = btn.classList.contains('dismiss-notif-btn');

        // Animations
        const targets = isSingle ? [btn.closest('.notification-item')] : document.querySelectorAll('.notification-item');
        targets.forEach(t => {
            t.style.opacity = '0';
            t.style.transform = 'scale(0.95)';
        });

        // Reload
        setTimeout(() => {
            if (isSingle) targets[0].remove();
            if (isHistory || isMarkAll) location.reload();
        }, 300);

        const url = isSingle ? `/notifications/mark-read/${btn.dataset.id}/` :
                    isHistory ? '/notifications/clear-history/' : '/notifications/mark-all-read/';

        await fetch(url, { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } });

        // Update the badge if the x button clicked rather than all.
        if (isSingle) updateBadge();
    });
});

// Swap notif number for bell when reached 0.
function updateBadge() {
    const badge = document.getElementById('notif-badge');
    if (badge) {
        let count = parseInt(badge.textContent) - 1;
        count > 0 ? badge.textContent = count : location.reload();
    }
}

// Work with Django CSRF token to work on the cookies :)
function getCookie(name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}