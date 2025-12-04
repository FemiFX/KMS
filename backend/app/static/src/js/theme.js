// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  const html = document.documentElement;

  // Check for saved theme preference or default to light mode
  const currentTheme = localStorage.getItem('theme') || 'light';
  html.classList.toggle('dark', currentTheme === 'dark');
  updateThemeIcon(currentTheme);

  // Theme toggle handler
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isDark = html.classList.toggle('dark');
      const newTheme = isDark ? 'dark' : 'light';
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');
    if (sunIcon && moonIcon) {
      if (theme === 'dark') {
        sunIcon.classList.remove('hidden');
        moonIcon.classList.add('hidden');
      } else {
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
      }
    }
  }
});

// Language switcher functionality
document.addEventListener('DOMContentLoaded', () => {
  const languageSelect = document.getElementById('language-select');

  if (languageSelect) {
    // Set current language from URL or default
    const urlParams = new URLSearchParams(window.location.search);
    const currentLang = urlParams.get('lang') || 'de';
    languageSelect.value = currentLang;

    // Handle language change
    languageSelect.addEventListener('change', (e) => {
      const newLang = e.target.value;
      const url = new URL(window.location.href);
      url.searchParams.set('lang', newLang);
      window.location.href = url.toString();
    });
  }
});
