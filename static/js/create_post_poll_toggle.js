// Joseph Beattie - Alpine.js script for controlling poll toggle.

document.addEventListener('alpine:init', () => {
    Alpine.data('postDialog', () => ({
        showPoll: false,

        togglePoll() {
            this.showPoll = !this.showPoll;
        },

        reset() {
            this.showPoll = false;
        }
    }));
});