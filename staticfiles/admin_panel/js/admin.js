(() => {
  const pageButtons = [...document.querySelectorAll("[data-admin-page-target]")];
  const pages = [...document.querySelectorAll("[data-admin-page]")];
  const pageTitle = document.querySelector("#admin-page-title");
  const pageDescription = document.querySelector("#admin-page-description");
  const toggle = document.querySelector("[data-sidebar-toggle]");
  const backdrop = document.querySelector("[data-sidebar-close]");

  function setPage(pageName, writeHash = true) {
    const button = pageButtons.find((item) => item.dataset.adminPageTarget === pageName);
    const selected = button ? pageName : "overview";
    const selectedButton = button || pageButtons.find((item) => item.dataset.adminPageTarget === "overview");

    pages.forEach((page) => {
      page.hidden = page.dataset.adminPage !== selected;
    });
    pageButtons.forEach((item) => {
      const active = item.dataset.adminPageTarget === selected;
      item.classList.toggle("is-active", active);
      if (active && item.closest(".side-nav")) item.setAttribute("aria-current", "page");
      else item.removeAttribute("aria-current");
    });

    if (selectedButton && pageTitle && pageDescription) {
      pageTitle.textContent = selectedButton.dataset.title;
      pageDescription.textContent = selectedButton.dataset.description;
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
    document.body.classList.remove("sidebar-open");
    toggle?.setAttribute("aria-expanded", "false");
    if (backdrop) backdrop.hidden = true;
    if (writeHash && location.hash !== "#" + selected) {
      history.pushState(null, "", "#" + selected);
    }
  }

  document.addEventListener("click", (event) => {
    const pageButton = event.target.closest("[data-admin-page-target]");
    if (pageButton) {
      setPage(pageButton.dataset.adminPageTarget);
      return;
    }

    if (event.target.closest("[data-sidebar-toggle]")) {
      const open = !document.body.classList.contains("sidebar-open");
      document.body.classList.toggle("sidebar-open", open);
      toggle?.setAttribute("aria-expanded", String(open));
      if (backdrop) backdrop.hidden = !open;
      return;
    }

    if (event.target.closest("[data-sidebar-close]")) {
      document.body.classList.remove("sidebar-open");
      toggle?.setAttribute("aria-expanded", "false");
      if (backdrop) backdrop.hidden = true;
    }
  });

  window.addEventListener("hashchange", () => {
    setPage(location.hash.slice(1) || "overview", false);
  });
  window.addEventListener("popstate", () => {
    setPage(location.hash.slice(1) || "overview", false);
  });

  const requestedPage = location.hash.slice(1);
  setPage(requestedPage || "overview", !requestedPage);
})();
