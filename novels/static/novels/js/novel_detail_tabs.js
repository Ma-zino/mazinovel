document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-nav .tab-btn');
    const tabContents = document.querySelectorAll('.tab-content-wrapper .tab-content');

    // Hide all tab contents initially (redundant if CSS handles it, but safe)
    // tabContents.forEach(content => content.style.display = 'none');
    // Show the default active one (redundant if CSS handles it)
    // const initiallyActiveContent = document.querySelector('.tab-content.active');
    // if (initiallyActiveContent) initiallyActiveContent.style.display = 'block';

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Get target content ID from data attribute
            const targetId = button.getAttribute('data-tab-target');
            const targetContent = document.querySelector(targetId);

            // Remove 'active' class from all buttons and content panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add 'active' class to the clicked button and target content pane
            button.classList.add('active');
            if (targetContent) {
                targetContent.classList.add('active'); // Use CSS to show/hide
            }
        });
    });
});