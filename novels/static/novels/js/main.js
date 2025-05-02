// Simple Tab Functionality
document.addEventListener('DOMContentLoaded', () => {
    const tabLinks = document.querySelectorAll('.tab-navigation .tab-link');
    const tabContents = document.querySelectorAll('.tab-content-wrapper .tab-content');

    tabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent potential page jump if using href="#"

            const targetId = link.getAttribute('data-tab-target'); // #about-tab or #toc-tab
            const targetContent = document.querySelector(targetId);

            // Remove active class from all links and content
            tabLinks.forEach(tl => tl.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));

            // Add active class to the clicked link and target content
            link.classList.add('active');
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
});