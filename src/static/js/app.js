/* Halo Blog — Frontend JS (minimal, most logic is inline in templates) */

// Header search (from 博客园 style)
function headerSearch(e) {
    if (e) e.preventDefault();
    const q = document.getElementById('header-search-input').value.trim();
    if (q) window.location.href = '/?q=' + encodeURIComponent(q);
}

// Smooth scroll for anchor links
document.addEventListener('click', e => {
    const link = e.target.closest('a[href^="#"]');
    if (link) {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth' });
    }
});
