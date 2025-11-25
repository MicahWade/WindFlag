function toggleGiveAwardModal() {
    const modal = document.getElementById('giveAwardModal');
    modal.classList.toggle('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.theme-tab-button');
    const tabContents = document.querySelectorAll('.theme-tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Deactivate current active tab and content
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Activate clicked tab and corresponding content
            button.classList.add('active');
            const targetTab = document.querySelector(button.dataset.tabTarget);
            if (targetTab) {
                targetTab.classList.add('active');
            }
        });
    });

    // Set initial active tab if none is set
    if (!document.querySelector('.theme-tab-button.active')) {
        const firstButton = document.querySelector('.theme-tab-button');
        const firstContent = document.querySelector('.theme-tab-content');
        if (firstButton) firstButton.classList.add('active');
        if (firstContent) firstContent.classList.add('active');
    }
});