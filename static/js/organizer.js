(function () {
  "use strict";

  const navLinks = [...document.querySelectorAll('.organizer-top nav a[href^="#"]')];
  const sections = navLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  function activate(id) {
    navLinks.forEach((link) => {
      if (link.getAttribute("href") === `#${id}`) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
  }

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) activate(visible.target.id);
    }, { rootMargin: "-100px 0px -58% 0px", threshold: [0, 0.15, 0.4, 0.7] });
    sections.forEach((section) => observer.observe(section));
  }

  navLinks.forEach((link) => link.addEventListener("click", () => {
    const id = link.getAttribute("href").slice(1);
    activate(id);
  }));

  const initial = location.hash.slice(1);
  if (sections.some((section) => section.id === initial)) activate(initial);

  const submissionNotice = document.querySelector("[data-submission-notice]");
  if (submissionNotice) {
    const counter = submissionNotice.querySelector("[data-submission-countdown]");
    let seconds = 5;
    const timer = window.setInterval(() => {
      seconds -= 1;
      if (counter) counter.textContent = String(Math.max(seconds, 0));
      if (seconds <= 0) {
        window.clearInterval(timer);
        window.location.replace(`${window.location.pathname}#ringkasan`);
      }
    }, 1000);
  }
})();
