(() => {
  const dialog = document.getElementById("signup-dialog");
  if (!dialog) return;

  document.querySelectorAll("[data-open-signup]").forEach((button) => {
    button.addEventListener("click", () => dialog.showModal());
  });
  dialog.querySelectorAll("[data-close-signup]").forEach((button) => {
    button.addEventListener("click", () => dialog.close());
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
})();
