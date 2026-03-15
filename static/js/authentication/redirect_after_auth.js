// Joseph Beattie - Accidentally removed this on last commit. Moves user on to next page after auth action
// like login / register / change password.

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('signing-in');

    if (container) {
        // Get the URL from the page above
        const nextUrl = container.getAttribute('next-url');

        if (nextUrl) {
            // Give a short delay.
            setTimeout(() => {
                window.location.href = nextUrl;
            }, 1500);
        }
    }
});