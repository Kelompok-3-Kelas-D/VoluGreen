(function () {
  "use strict";

  const icons = {
    leaf: '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    sprout: '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    heart: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    building: '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4M10 10h4M10 14h4M10 18h4"/>',
    shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    pin: '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    mail: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    lock: '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    eye: '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
    eyeoff: '<path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    arrow: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    chev: '<path d="m6 9 6 6 6-6"/>',
    award: '<path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/>',
  };

  const svg = (name) =>
    '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">' +
    (icons[name] || "") +
    "</svg>";

  document.querySelectorAll("[data-i]").forEach((element) => {
    element.insertAdjacentHTML("afterbegin", svg(element.dataset.i));
  });

  document.querySelectorAll("[data-eye]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = document.getElementById(button.dataset.eye);
      if (!input) return;
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      button.innerHTML = svg(show ? "eyeoff" : "eye");
      button.setAttribute(
        "aria-label",
        show ? "Sembunyikan kata sandi" : "Tampilkan kata sandi"
      );
    });
  });

  document.querySelectorAll("[data-soon]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      window.alert(link.dataset.soon);
    });
  });

  const registerRole = document.getElementById("r-role");
  const registerTabs = document.getElementById("reg-role");
  const ticks = document.getElementById("reg-ticks");
  const nameLabel = document.getElementById("r-name-lbl");
  const nameInput = document.getElementById("r-name");
  const gratisSub = document.getElementById("gratis-sub");
  const tickText = {
    volunteer: [
      "Cari kegiatan berdasarkan lokasi, kategori, dan waktu",
      "Daftar kegiatan dan pantau status pendaftaranmu",
      "Lihat riwayat partisipasi dan dampak kontribusimu",
    ],
    organizer: [
      "Publikasikan lowongan kegiatan dan atur kuota relawan",
      "Tinjau pendaftar dan konfirmasi kehadiran",
      "Catat dampak kegiatan setelah organisasi diverifikasi admin",
    ],
  };

  function paintRegister(role) {
    if (!registerRole || !registerTabs) return;
    registerRole.value = role;
    registerTabs.querySelectorAll("[data-role]").forEach((button) => {
      button.setAttribute("aria-selected", String(button.dataset.role === role));
    });
    document.querySelectorAll("[data-only]").forEach((field) => {
      field.hidden = field.dataset.only !== role;
    });
    ticks.innerHTML = tickText[role]
      .map((text) => '<li><span class="t">' + svg("check") + "</span>" + text + "</li>")
      .join("");
    const organizer = role === "organizer";
    nameLabel.textContent = organizer ? "Nama organisasi" : "Nama lengkap";
    nameInput.placeholder = organizer
      ? "Contoh: Bank Sampah Hijau Lestari"
      : "Nama sesuai KTM/KTP";
    nameInput.autocomplete = organizer ? "organization" : "name";
    gratisSub.textContent = organizer
      ? "untuk komunitas & organisasi"
      : "untuk semua relawan";
  }

  if (registerRole && registerTabs) {
    paintRegister(registerRole.value || "volunteer");
    registerTabs.addEventListener("click", (event) => {
      const button = event.target.closest("[data-role]");
      if (button) paintRegister(button.dataset.role);
    });
  }

  const password = document.getElementById("r-pass");
  const password2 = document.getElementById("r-pass2");
  const strength = document.getElementById("r-strength");
  const match = document.getElementById("r-match");

  function strengthLevel(value) {
    if (!value) return 0;
    let level = 1;
    if (value.length >= 8 && /[A-Za-z]/.test(value) && /\d/.test(value)) level = 2;
    if (value.length >= 10 && /[^A-Za-z0-9]/.test(value)) level = 3;
    return level;
  }

  function paintPassword() {
    if (!password || !strength) return;
    const level = strengthLevel(password.value);
    strength.dataset.lv = String(level);
    strength.querySelector("b").textContent = ["", "Lemah", "Sedang", "Kuat"][level];
    if (password2 && match) {
      match.hidden = !(password2.value && password2.value === password.value);
    }
  }

  if (password) password.addEventListener("input", paintPassword);
  if (password2) password2.addEventListener("input", paintPassword);
  paintPassword();

  const loginRole = document.getElementById("login-role-value");
  const loginTabs = document.getElementById("login-role");
  const loginCta = document.getElementById("login-cta");
  const roleLabels = {
    volunteer: "Relawan",
    organizer: "Penyelenggara",
  };

  function paintLogin(role) {
    if (!loginRole || !loginTabs) return;
    loginRole.value = role;
    loginTabs.querySelectorAll("[data-role]").forEach((button) => {
      button.setAttribute("aria-selected", String(button.dataset.role === role));
    });
    loginCta.textContent = "Masuk sebagai " + roleLabels[role];
  }

  if (loginRole && loginTabs) {
    paintLogin(loginRole.value || "volunteer");
    loginTabs.addEventListener("click", (event) => {
      const button = event.target.closest("[data-role]");
      if (button) paintLogin(button.dataset.role);
    });
  }
})();
