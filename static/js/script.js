(() => {
  "use strict";

  const icons = {
    leaf: '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    sprout: '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    menu: '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>'
  };
  document.querySelectorAll("[data-i]").forEach((element) => {
    const paths = icons[element.dataset.i];
    if (paths) element.insertAdjacentHTML("afterbegin", '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">' + paths + "</svg>");
  });

  const button = document.querySelector("[data-drawer]");
  const drawer = button && document.getElementById(button.dataset.drawer);
  if (!button || !drawer) return;

  function setMenuOpen(open) {
    drawer.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    button.setAttribute("aria-label", open ? "Tutup menu" : "Buka menu");
  }

  button.addEventListener("click", () => setMenuOpen(drawer.hidden));
  drawer.addEventListener("click", (event) => {
    if (event.target.closest("a")) setMenuOpen(false);
  });
  document.addEventListener("click", (event) => {
    if (!drawer.hidden && !drawer.contains(event.target) && !button.contains(event.target)) setMenuOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setMenuOpen(false);
      document.querySelector(".account-menu")?.removeAttribute("open");
    }
  });
  window.addEventListener("resize", () => {
    if (window.matchMedia("(min-width: 761px)").matches) setMenuOpen(false);
  });
})();
