// Joseph Beattie - Handling for alpine poll area within post creation, editing and comments.

document.addEventListener('alpine:init', () => {
    Alpine.data('pollManager', (initialChoices = ['', ''], isEnabled = false) => ({
        showPoll: isEnabled,
        customTitle: false,
        choices: initialChoices,

        refreshIcons() {
            setTimeout(() => {
                if (window.lucide) { window.lucide.createIcons(); }
            }, 50);
        },

        addChoice() {
            if (this.choices.length < 10) {
                this.choices.push('');
                this.refreshIcons();
            }
        },

        removeChoice(index) {
            if (this.choices.length > 2) {
                this.choices.splice(index, 1);
            }
        }
    }));
});