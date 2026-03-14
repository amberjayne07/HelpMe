// Joseph Beattie - Controller for background page glow.
// Essentially checks current page and will maintain glow in helpme_overrides.css
// without restarting the animation when jumping between pages.

document.addEventListener('DOMContentLoaded', function () {
    const glow = document.querySelector('.background-glow');
    if (!glow) {
        sessionStorage.removeItem('pageHasGlow');
        return;
    }

    // Used to get the list of pages and the current name of the page.
    const glowPagesAttr = glow.getAttribute('data-glow-pages');
    const currentPage = glow.getAttribute('data-current-page');

    // Split django settings items into array for JS
    const glowPages = glowPagesAttr ? glowPagesAttr.split(',') : [];

    // Check if the page is one that includes the glow animation
    const isGlowPage = glowPages.includes(currentPage);

    const wasOnGlowPage = sessionStorage.getItem('pageHasGlow') === 'true';

    if (isGlowPage && wasOnGlowPage) {
        // Skips the animation / change background animation
        glow.classList.add('skip-entrance');
    }

    // Update the session storage for checking with the constant :)
    if (isGlowPage) {
        sessionStorage.setItem('pageHasGlow', 'true');
    }
});

