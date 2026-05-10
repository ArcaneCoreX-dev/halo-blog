/* Halo Blog — Frontend JS (minimal, most logic is inline in templates) */

// Smooth scroll for anchor links
document.addEventListener('click', e => {
    const link = e.target.closest('a[href^="#"]');
    if (link) {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth' });
    }
});
