(() => {
  "use strict";

  const navigation = document.querySelector(".organizer-top nav");
  if (!navigation) return;
  const links = [...navigation.querySelectorAll("a")];
  const overview = links.find((link) => link.textContent.trim() === "Ringkasan");
  const activities = links.find((link) => link.textContent.trim() === "Kegiatan");
  const impact = links.find((link) => link.textContent.trim() === "Laporan dampak");

  function updateCurrentPage() {
    const onActivitiesPage = activities && location.pathname === new URL(activities.href).pathname;
    const current = onActivitiesPage
      ? (location.hash === "#dampak" ? impact : activities)
      : overview;
    [overview, activities, impact].forEach((link) => {
      if (!link) return;
      if (link === current) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
  }

  window.addEventListener("hashchange", updateCurrentPage);
  updateCurrentPage();
})();
