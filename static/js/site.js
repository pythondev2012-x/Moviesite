document.addEventListener('DOMContentLoaded', function () {
  const nav = document.getElementById('mainNav');
  if (nav) {
    const updateNav = () => nav.classList.toggle('scrolled', window.scrollY > 20);
    updateNav();
    window.addEventListener('scroll', updateNav, { passive: true });
  }

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
});
