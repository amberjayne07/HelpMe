// Joseph Beattie - Animations for each page opening.

document.addEventListener("DOMContentLoaded", () => {
    const mainContent = document.querySelector('main');
    const loader = document.getElementById('loading-overlay');
    let loaderTimeout;

    const showPage = () => {
        if (loader) {
            loader.classList.add('hidden');
            loader.classList.remove('opacity-100');
        }
        if (mainContent) {
            mainContent.classList.add('page-visible');
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'scale(1)';
        }
    };

    setTimeout(showPage, 10);

    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            showPage();
        }
    });

    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', e => {
            const isInternal = link.hostname === window.location.hostname;
            const isNotNewTab = link.target !== "_blank";
            const isNotSpecial = !link.hasAttribute('data-no-transition') &&
                !link.href.includes('#') &&
                link.href !== "javascript:void(0);";

            if (isInternal && isNotNewTab && isNotSpecial) {
                e.preventDefault();
                const destination = link.href;

                if (mainContent) {
                    mainContent.classList.remove('page-visible');
                    mainContent.style.opacity = '0';
                    mainContent.style.transform = 'scale(0.98)';
                }

                loaderTimeout = setTimeout(() => {
                    if (loader) {
                        loader.classList.remove('hidden');
                        requestAnimationFrame(() => {
                            loader.classList.add('opacity-100');
                        });
                    }
                }, 200);

                setTimeout(() => {
                    window.location.href = destination;
                }, 400);
            }
        });
    });
});