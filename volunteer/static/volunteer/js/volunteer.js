/* =====================================================================
 * === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
 * ===================================================================== */
(function () {
  "use strict";

  /* ---------- Set ikon Lucide yang konsisten dengan Design System VoluGreen ---------- */
  const ICON_PATHS = {
    leaf: '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    sprout: '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    mail: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    arrow: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    heart: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    building: '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
    shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    award: '<path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/>',
    pin: '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    cal: '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    calcheck: '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="m9 16 2 2 4-4"/>',
    pencil: '<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/><path d="m15 5 4 4"/>',
    clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    trash: '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>',
    user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    phone: '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    chev: '<path d="m6 9 6 6 6-6"/>',
    recycle: '<path d="M7 19H4.815a1.83 1.83 0 0 1-1.57-.881 1.785 1.785 0 0 1-.004-1.784L7.196 9.5"/><path d="M11 19h8.203a1.83 1.83 0 0 0 1.556-.89 1.784 1.784 0 0 0 0-1.775l-1.226-2.12"/><path d="m14 16-3 3 3 3"/><path d="M8.293 13.596 7.196 9.5 3.1 10.598"/><path d="m9.344 5.811 1.093-1.892A1.83 1.83 0 0 1 11.985 3a1.784 1.784 0 0 1 1.546.888l3.943 6.843"/><path d="m13.378 9.633 4.096 1.098 1.097-4.096"/>'
  };

  function iconSvg(name) {
    return '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">' + (ICON_PATHS[name] || "") + "</svg>";
  }

  function paintIcons(root) {
    (root || document).querySelectorAll("[data-i]").forEach(function (el) {
      if (!el.dataset.painted) {
        el.insertAdjacentHTML("afterbegin", iconSvg(el.dataset.i));
        el.dataset.painted = "1";
      }
    });
  }

  /* ---------- Helper Sanitasi HTML (Anti-XSS) ---------- */
  function escapeHtml(value) {
    if (value === null || value === undefined) {
      return "";
    }
    return String(value).replace(/[&<>"']/g, function (ch) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }[ch];
    });
  }

  /* ---------- Helper CSRF Token Django ---------- */
  function getCsrfToken() {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (input && input.value) {
      return input.value;
    }
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith("csrftoken=")) {
        return decodeURIComponent(cookie.substring("csrftoken=".length));
      }
    }
    return "";
  }

  /* ---------- Helper Toast Notifikasi (#vg-toast.toast.show) ---------- */
  let toastTimer = null;
  function showToast(message) {
    const toastEl = document.getElementById("vg-toast") || document.getElementById("toast");
    const msgEl = document.getElementById("vg-toast-msg") || document.getElementById("toast-msg");
    if (!toastEl || !msgEl) {
      return;
    }
    msgEl.textContent = message || "";
    toastEl.classList.add("show");
    if (toastTimer) {
      clearTimeout(toastTimer);
    }
    toastTimer = setTimeout(function () {
      toastEl.classList.remove("show");
    }, 3200);
  }

  /* ---------- Helper Badge Status ---------- */
  function renderStatusChip(status, statusLabel) {
    const mapClass = {
      PENDING: "chip wait",
      ACCEPTED: "chip ok",
      COMPLETED: "chip done",
      CANCELLED: "chip danger",
      REJECTED: "chip danger"
    };
    const cls = mapClass[status] || "chip";
    return '<span class="' + cls + '">' + escapeHtml(statusLabel || status) + "</span>";
  }

  /* ---------- Helper Form Error Inline ---------- */
  function clearFormErrors(scope, prefix) {
    const root = scope || document;
    const pref = prefix || "";
    root.querySelectorAll("[data-err]").forEach(function (el) {
      if (!pref || el.dataset.err.startsWith(pref)) {
        el.textContent = "";
      }
    });
    root.querySelectorAll(".control.is-bad").forEach(function (el) {
      el.classList.remove("is-bad");
    });
  }

  function applyFormErrors(errors, scope, prefix) {
    if (!errors || typeof errors !== "object") {
      return;
    }
    const root = scope || document;
    const pref = prefix || "";
    Object.keys(errors).forEach(function (field) {
      const messages = Array.isArray(errors[field]) ? errors[field] : [String(errors[field])];
      const text = messages.filter(Boolean).join(" ");
      const errEl = root.querySelector('[data-err="' + pref + field + '"]');
      if (errEl) {
        errEl.textContent = text;
      }
      const ctrl = document.getElementById("ctrl-" + field);
      if (ctrl) {
        ctrl.classList.add("is-bad");
      }
    });
  }

  /* ===================================================================
   * 1. HALAMAN FORMULIR PENDAFTARAN KEGIATAN (daftar_kegiatan.html)
   * =================================================================== */
  function initHalamanDaftarKegiatan() {
    const form = document.getElementById("form-daftar-kegiatan");
    if (!form) {
      return;
    }

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      clearFormErrors(form, "");

      const motivasi = (form.querySelector('[name="motivasi"]')?.value || "").trim();
      const kontak = (form.querySelector('[name="kontak_darurat"]')?.value || "").trim();
      const pengalaman = (form.querySelector('[name="pengalaman_relevan"]')?.value || "").trim();
      const kebutuhan = (form.querySelector('[name="kebutuhan_khusus"]')?.value || "").trim();
      const komitmen = form.querySelector('[name="komitmen"]');

      if (komitmen && !komitmen.checked) {
        applyFormErrors({ komitmen: ["Harap centang pernyataan komitmen kehadiran terlebih dahulu."] }, form, "");
        return;
      }

      const btn = document.getElementById("btn-submit-daftar");
      const label = document.getElementById("btn-submit-daftar-label");
      const originalText = label ? label.textContent : "Kirim Pendaftaran Relawan";
      if (btn) {
        btn.disabled = true;
      }
      if (label) {
        label.textContent = "Mengirim pendaftaran...";
      }

      try {
        const response = await fetch(form.dataset.endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
            "X-Requested-With": "XMLHttpRequest"
          },
          body: JSON.stringify({
            motivasi: motivasi,
            kontak_darurat: kontak,
            pengalaman_relevan: pengalaman,
            kebutuhan_khusus: kebutuhan
          })
        });

        const result = await response.json();

        if (!response.ok || result.status !== "success") {
          if (result.errors) {
            applyFormErrors(result.errors, form, "");
          } else if (result.message) {
            applyFormErrors({ __all__: [result.message] }, form, "");
          }
          showToast(result.message || "Pendaftaran belum berhasil dikirim.");
          if (btn) {
            btn.disabled = false;
          }
          if (label) {
            label.textContent = originalText;
          }
          return;
        }

        // Sukses (201 Created): perbarui sisa kuota live & tampilkan notice sudah terdaftar
        const data = result.data || {};
        if (data.kegiatan) {
          const terisiEl = document.getElementById("live-terisi-kuota");
          const sisaEl = document.getElementById("live-sisa-kuota");
          if (terisiEl && data.kegiatan.kuota_terisi !== undefined) {
            terisiEl.textContent = data.kegiatan.kuota_terisi;
          }
          if (sisaEl && data.kegiatan.sisa_kuota !== undefined) {
            sisaEl.textContent = data.kegiatan.sisa_kuota;
          }
        }

        const boxTerdaftar = document.getElementById("box-sudah-terdaftar");
        const judulTerdaftar = document.getElementById("notice-judul-terdaftar");
        if (judulTerdaftar && data.status_label) {
          judulTerdaftar.textContent = "Pendaftaran berhasil dikirim (" + data.status_label + ")";
        }
        form.hidden = true;
        if (boxTerdaftar) {
          boxTerdaftar.hidden = false;
        }
        showToast(result.message || "Pendaftaran relawan berhasil dikirim!");
      } catch (err) {
        applyFormErrors({ __all__: ["Terjadi gangguan koneksi. Silakan coba lagi."] }, form, "");
        showToast("Gagal menghubungi server.");
        if (btn) {
          btn.disabled = false;
        }
        if (label) {
          label.textContent = originalText;
        }
      }
    });
  }

  /* ===================================================================
   * 2. HALAMAN DASHBOARD RELAWAN (dashboard_relawan.html)
   * =================================================================== */
  const cachePendaftaran = new Map();
  const ZERO_UUID = "00000000-0000-0000-0000-000000000000";

  function updateSummaryCounters(summary) {
    if (!summary) {
      return;
    }
    const mapId = {
      "stat-menunggu": summary.menunggu,
      "stat-diterima": summary.diterima,
      "stat-selesai": summary.selesai,
      "stat-jam": summary.total_jam_kontribusi
    };
    Object.keys(mapId).forEach(function (id) {
      const el = document.getElementById(id);
      if (el && mapId[id] !== undefined) {
        el.textContent = mapId[id];
      }
    });
  }

  function renderKartuStatus(item) {
    cachePendaftaran.set(item.id, item);
    const keg = item.kegiatan || {};
    const btl = item.pembatalan || {};
    const rw = item.riwayat_partisipasi || {};

    let blokTambahan = "";
    if (item.status === "CANCELLED" && btl.alasan) {
      blokTambahan =
        '<dl class="vg-detail-box warn">' +
        '<div class="full"><dt>Alasan Pembatalan</dt><dd>' + escapeHtml(btl.alasan) + "</dd></div>" +
        (btl.waktu_display ? '<div class="full"><dt>Waktu Pembatalan</dt><dd>' + escapeHtml(btl.waktu_display) + "</dd></div>" : "") +
        "</dl>";
    } else if (item.masuk_riwayat_partisipasi) {
      blokTambahan =
        '<dl class="vg-detail-box impact">' +
        '<div><dt>Jam Kontribusi</dt><dd>' + escapeHtml(rw.jam_kontribusi || 0) + " jam</dd></div>" +
        '<div><dt>Catatan Dampak Penyelenggara</dt><dd>' + escapeHtml(rw.catatan_dampak || "Partisipasi tuntas tercatat.") + "</dd></div>" +
        '<div class="full"><dt>Refleksi Relawan</dt><dd>' + escapeHtml(rw.refleksi_relawan || "Belum ada refleksi yang ditulis.") + "</dd></div>" +
        "</dl>";
    }

    let tombolAksi = "";
    if (item.bisa_diubah) {
      tombolAksi +=
        '<button class="btn btn-ghost btn-sm" type="button" data-action="buka-ubah" data-id="' + escapeHtml(item.id) + '">' +
        iconSvg("pencil") + "Ubah Informasi</button>";
    }
    if (item.bisa_dibatalkan) {
      tombolAksi +=
        '<button class="btn btn-danger-outline btn-sm" type="button" data-action="buka-batal" data-id="' + escapeHtml(item.id) + '">' +
        iconSvg("trash") + "Batalkan Pendaftaran</button>";
    }
    if (item.bisa_isi_refleksi) {
      tombolAksi +=
        '<button class="btn btn-ghost btn-sm" type="button" data-action="buka-refleksi" data-id="' + escapeHtml(item.id) + '">' +
        iconSvg("award") + (rw.refleksi_relawan ? "Perbarui Refleksi" : "Tulis Refleksi") + "</button>";
    }

    return (
      '<article class="vg-item" data-pendaftaran-id="' + escapeHtml(item.id) + '">' +
      '<div class="vg-item-head">' +
      "<div>" +
      '<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">' +
      '<span class="chip sm">' + escapeHtml(keg.kategori || "Kegiatan") + "</span>" +
      renderStatusChip(item.status, item.status_label) +
      "</div>" +
      '<h4 class="vg-item-title">' + escapeHtml(keg.judul) + "</h4>" +
      '<div class="vg-item-meta">' +
      "<span>" + iconSvg("building") + escapeHtml(keg.penyelenggara || "Penyelenggara") + "</span>" +
      "<span>" + iconSvg("pin") + escapeHtml(keg.lokasi || "-") + "</span>" +
      "<span>" + iconSvg("cal") + escapeHtml(keg.tanggal_display || "-") + "</span>" +
      "</div>" +
      "</div>" +
      '<span class="muted-sm">Didaftarkan: ' + escapeHtml(item.waktu_daftar_display || "-") + "</span>" +
      "</div>" +
      '<dl class="vg-detail-box">' +
      '<div class="full"><dt>Motivasi Pendaftaran</dt><dd>' + escapeHtml(item.motivasi) + "</dd></div>" +
      "<div><dt>Kontak Darurat</dt><dd>" + escapeHtml(item.kontak_darurat) + "</dd></div>" +
      "<div><dt>Kebutuhan Khusus</dt><dd>" + escapeHtml(item.kebutuhan_khusus || "Tidak ada") + "</dd></div>" +
      (item.pengalaman_relevan
        ? '<div class="full"><dt>Pengalaman Relevan</dt><dd>' + escapeHtml(item.pengalaman_relevan) + "</dd></div>"
        : "") +
      "</dl>" +
      (item.pesan
        ? '<div class="notice" role="note"><strong>Catatan penyelenggara:</strong> ' + escapeHtml(item.pesan) + "</div>"
        : "") +
      blokTambahan +
      '<div class="vg-actions">' +
      '<span class="muted-sm">Sisa kuota kegiatan: <b>' + escapeHtml(keg.sisa_kuota) + "/" + escapeHtml(keg.kuota) + "</b></span>" +
      '<div class="vg-actions-group">' + tombolAksi + "</div>" +
      "</div>" +
      "</article>"
    );
  }

  function renderKartuRiwayatSelesai(item) {
    cachePendaftaran.set(item.id, item);
    const keg = item.kegiatan || {};
    const rw = item.riwayat_partisipasi || {};
    return (
      '<article class="vg-item" data-riwayat-id="' + escapeHtml(item.id) + '">' +
      '<div class="vg-item-head">' +
      "<div>" +
      '<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">' +
      '<span class="chip done">' + iconSvg("calcheck") + "Selesai Berpartisipasi</span>" +
      '<span class="chip yellow">' + iconSvg("clock") + escapeHtml(rw.jam_kontribusi || 0) + " Jam Kontribusi</span>" +
      '<span class="chip sm">' + escapeHtml(keg.kategori || "Lingkungan") + "</span>" +
      "</div>" +
      '<h4 class="vg-item-title">' + escapeHtml(keg.judul) + "</h4>" +
      '<div class="vg-item-meta">' +
      "<span>" + iconSvg("building") + escapeHtml(keg.penyelenggara || "-") + "</span>" +
      "<span>" + iconSvg("pin") + escapeHtml(keg.lokasi || "-") + "</span>" +
      "<span>" + iconSvg("cal") + escapeHtml(keg.tanggal_display || "-") + "</span>" +
      "</div>" +
      "</div>" +
      '<button class="btn btn-ghost btn-sm" type="button" data-action="buka-refleksi" data-id="' + escapeHtml(item.id) + '">' +
      iconSvg("pencil") + (rw.refleksi_relawan ? "Edit Refleksi" : "Tulis Refleksi") +
      "</button>" +
      "</div>" +
      '<dl class="vg-detail-box impact">' +
      '<div><dt>Dampak Tercatat oleh Penyelenggara</dt><dd>' + escapeHtml(rw.catatan_dampak || "Hadir dan menuntaskan kegiatan lapangan.") + "</dd></div>" +
      '<div><dt>Waktu Selesai Partisipasi</dt><dd>' + escapeHtml(rw.waktu_selesai_display || keg.tanggal_display || "-") + "</dd></div>" +
      '<div class="full"><dt>Refleksi Pribadi Relawan</dt><dd>' +
      escapeHtml(rw.refleksi_relawan || "Belum ada refleksi yang ditulis. Klik tombol 'Tulis Refleksi' untuk mencatat kesanmu.") +
      "</dd></div>" +
      "</dl>" +
      "</article>"
    );
  }

  function renderKartuLogTidakAktif(item) {
    const keg = item.kegiatan || {};
    const btl = item.pembatalan || {};
    return (
      '<article class="vg-item">' +
      '<div class="vg-item-head">' +
      "<div>" +
      '<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">' +
      renderStatusChip(item.status, item.status_label) +
      '<span class="chip sm">' + escapeHtml(keg.kategori || "Kegiatan") + "</span>" +
      "</div>" +
      '<h4 class="vg-item-title">' + escapeHtml(keg.judul) + "</h4>" +
      '<div class="vg-item-meta">' +
      "<span>" + iconSvg("pin") + escapeHtml(keg.lokasi || "-") + "</span>" +
      "<span>" + iconSvg("cal") + escapeHtml(keg.tanggal_display || "-") + "</span>" +
      "</div>" +
      "</div>" +
      (item.status === "CANCELLED" && keg.url_daftar && !keg.sudah_lewat
        ? '<a class="btn btn-ghost btn-sm" href="' + escapeHtml(keg.url_daftar) + '">Daftar Ulang</a>'
        : "") +
      "</div>" +
      (btl.alasan
        ? '<dl class="vg-detail-box warn"><div class="full"><dt>Alasan Pembatalan</dt><dd>' + escapeHtml(btl.alasan) + "</dd></div></dl>"
        : "") +
      "</article>"
    );
  }

  async function muatDaftarStatus() {
    const root = document.getElementById("vg-dashboard-relawan");
    const container = document.getElementById("list-status-pendaftaran");
    if (!root || !container) {
      return;
    }

    const q = (document.getElementById("filter-q")?.value || "").trim();
    const status = (document.getElementById("filter-status")?.value || "ALL").trim();
    const params = new URLSearchParams();
    if (status && status !== "ALL") {
      params.set("status", status);
    }
    if (q) {
      params.set("q", q);
    }

    const url = root.dataset.endpointStatus + (params.toString() ? "?" + params.toString() : "");
    try {
      const response = await fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
      });
      const result = await response.json();
      if (!response.ok || result.status !== "success") {
        showToast(result.message || "Gagal memuat daftar pendaftaran.");
        return;
      }

      updateSummaryCounters(result.summary || result.ringkasan);
      const items = result.data || [];
      if (!items.length) {
        container.innerHTML =
          '<div class="vg-empty">' +
          '<span class="round">' + iconSvg("cal") + "</span>" +
          "<b>Belum ada pendaftaran yang cocok</b>" +
          "<span>Kamu belum memiliki pendaftaran pada filter ini atau belum mendaftar kegiatan.</span>" +
          "</div>";
        return;
      }
      container.innerHTML = items.map(renderKartuStatus).join("");
    } catch (err) {
      showToast("Gagal memuat daftar status pendaftaran.");
    }
  }

  async function muatRiwayatPartisipasi() {
    const root = document.getElementById("vg-dashboard-relawan");
    const listSelesai = document.getElementById("list-riwayat-selesai");
    const listLog = document.getElementById("list-riwayat-log");
    if (!root || !listSelesai || !listLog) {
      return;
    }

    try {
      const response = await fetch(root.dataset.endpointRiwayat, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
      });
      const result = await response.json();
      if (!response.ok || result.status !== "success") {
        showToast(result.message || "Gagal memuat riwayat partisipasi.");
        return;
      }

      const totalKeg = result.total_kegiatan_diikuti || 0;
      const totalJam = result.total_jam_kontribusi || 0;
      const judulRingkasan = document.getElementById("riwayat-ringkasan-judul");
      if (judulRingkasan) {
        judulRingkasan.textContent =
          "Total kontribusimu: " + totalKeg + " kegiatan selesai · " + totalJam + " jam kontribusi";
      }
      const statSelesai = document.getElementById("stat-selesai");
      const statJam = document.getElementById("stat-jam");
      if (statSelesai) {
        statSelesai.textContent = totalKeg;
      }
      if (statJam) {
        statJam.textContent = totalJam;
      }

      const selesaiItems = result.data || [];
      if (!selesaiItems.length) {
        listSelesai.innerHTML =
          '<div class="vg-empty">' +
          '<span class="round">' + iconSvg("award") + "</span>" +
          "<b>Belum ada kegiatan yang diselesaikan</b>" +
          "<span>Kegiatan yang telah dikonfirmasi kehadirannya oleh penyelenggara akan tampil di sini beserta metrik dampaknya.</span>" +
          "</div>";
      } else {
        listSelesai.innerHTML = selesaiItems.map(renderKartuRiwayatSelesai).join("");
      }

      const logItems = result.riwayat_dibatalkan_ditolak || [];
      if (!logItems.length) {
        listLog.innerHTML =
          '<div class="vg-empty">' +
          "<b>Tidak ada pendaftaran yang dibatalkan atau ditolak</b>" +
          "<span>Seluruh pendaftaranmu berjalan baik.</span>" +
          "</div>";
      } else {
        listLog.innerHTML = logItems.map(renderKartuLogTidakAktif).join("");
      }
    } catch (err) {
      showToast("Gagal memuat riwayat partisipasi relawan.");
    }
  }

  /* ---------- Pengelolaan Modal ---------- */
  function bukaModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.hidden = false;
    }
  }

  function tutupModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.hidden = true;
    }
  }

  function initDashboardRelawan() {
    const root = document.getElementById("vg-dashboard-relawan");
    if (!root) {
      return;
    }

    // Navigasi Tab (.seg)
    const tabContainer = document.getElementById("tab-relawan");
    const panelStatus = document.getElementById("panel-status");
    const panelRiwayat = document.getElementById("panel-riwayat");
    const judulTab = document.getElementById("judul-tab-aktif");

    if (tabContainer) {
      tabContainer.addEventListener("click", function (event) {
        const btn = event.target.closest("button[data-tab]");
        if (!btn) {
          return;
        }
        const tabName = btn.dataset.tab;
        tabContainer.querySelectorAll("button[data-tab]").forEach(function (b) {
          b.setAttribute("aria-selected", b === btn ? "true" : "false");
        });
        if (tabName === "riwayat") {
          panelStatus.hidden = true;
          panelRiwayat.hidden = false;
          if (judulTab) {
            judulTab.textContent = "Riwayat Partisipasi & Dampak Kontribusi";
          }
          muatRiwayatPartisipasi();
        } else {
          panelRiwayat.hidden = true;
          panelStatus.hidden = false;
          if (judulTab) {
            judulTab.textContent = "Status Pendaftaran Kegiatan";
          }
          muatDaftarStatus();
        }
      });
    }

    // Filter & Pencarian
    let debounceTimer = null;
    const inputQ = document.getElementById("filter-q");
    const selectStatus = document.getElementById("filter-status");
    const btnReset = document.getElementById("btn-reset-filter");
    const btnRefresh = document.getElementById("btn-muat-ulang");

    if (inputQ) {
      inputQ.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(muatDaftarStatus, 220);
      });
    }
    if (selectStatus) {
      selectStatus.addEventListener("change", muatDaftarStatus);
    }
    if (btnReset) {
      btnReset.addEventListener("click", function () {
        if (inputQ) {
          inputQ.value = "";
        }
        if (selectStatus) {
          selectStatus.value = "ALL";
        }
        muatDaftarStatus();
      });
    }
    if (btnRefresh) {
      btnRefresh.addEventListener("click", function () {
        muatDaftarStatus();
        muatRiwayatPartisipasi();
        showToast("Data pendaftaran & riwayat diperbarui.");
      });
    }

    // Delegasi klik tombol pada kartu & penutup modal
    document.addEventListener("click", function (event) {
      const closeBtn = event.target.closest("[data-close-modal]");
      if (closeBtn) {
        tutupModal(closeBtn.dataset.closeModal);
        return;
      }

      const actionBtn = event.target.closest("[data-action]");
      if (!actionBtn) {
        return;
      }
      const action = actionBtn.dataset.action;
      const id = actionBtn.dataset.id;
      const item = cachePendaftaran.get(id);
      if (!item) {
        return;
      }

      if (action === "buka-ubah") {
        clearFormErrors(document.getElementById("modal-ubah"), "ubah_");
        document.getElementById("ubah-pendaftaran-id").value = item.id;
        document.getElementById("sub-modal-ubah").textContent = item.kegiatan?.judul || "";
        document.getElementById("ubah-motivasi").value = item.motivasi || "";
        document.getElementById("ubah-kontak").value = item.kontak_darurat || "";
        document.getElementById("ubah-kebutuhan").value = item.kebutuhan_khusus || "";
        document.getElementById("ubah-pengalaman").value = item.pengalaman_relevan || "";
        bukaModal("modal-ubah");
      } else if (action === "buka-batal") {
        clearFormErrors(document.getElementById("modal-batal"), "batal_");
        document.getElementById("batal-pendaftaran-id").value = item.id;
        document.getElementById("sub-modal-batal").textContent = item.kegiatan?.judul || "";
        document.getElementById("batal-alasan").value = "";
        bukaModal("modal-batal");
      } else if (action === "buka-refleksi") {
        clearFormErrors(document.getElementById("modal-refleksi"), "refleksi_");
        document.getElementById("refleksi-pendaftaran-id").value = item.id;
        document.getElementById("sub-modal-refleksi").textContent = item.kegiatan?.judul || "";
        document.getElementById("refleksi-teks").value =
          item.riwayat_partisipasi?.refleksi_relawan || "";
        bukaModal("modal-refleksi");
      }
    });

    // Submit Modal Ubah Informasi
    const formUbah = document.getElementById("form-modal-ubah");
    if (formUbah) {
      formUbah.addEventListener("submit", async function (event) {
        event.preventDefault();
        clearFormErrors(formUbah, "ubah_");
        const id = document.getElementById("ubah-pendaftaran-id").value;
        const url = root.dataset.endpointUbahTemplate.replace(ZERO_UUID, id);

        try {
          const response = await fetch(url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
              "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({
              motivasi: document.getElementById("ubah-motivasi").value,
              kontak_darurat: document.getElementById("ubah-kontak").value,
              kebutuhan_khusus: document.getElementById("ubah-kebutuhan").value,
              pengalaman_relevan: document.getElementById("ubah-pengalaman").value
            })
          });
          const result = await response.json();
          if (!response.ok || result.status !== "success") {
            applyFormErrors(result.errors || { __all__: [result.message] }, formUbah, "ubah_");
            showToast(result.message || "Gagal memperbarui informasi pendaftaran.");
            return;
          }
          tutupModal("modal-ubah");
          showToast(result.message || "Informasi pendaftaran berhasil diperbarui.");
          muatDaftarStatus();
        } catch (err) {
          showToast("Gagal menghubungi server.");
        }
      });
    }

    // Submit Modal Batalkan Pendaftaran
    const formBatal = document.getElementById("form-modal-batal");
    if (formBatal) {
      formBatal.addEventListener("submit", async function (event) {
        event.preventDefault();
        clearFormErrors(formBatal, "batal_");
        const id = document.getElementById("batal-pendaftaran-id").value;
        const url = root.dataset.endpointBatalTemplate.replace(ZERO_UUID, id);

        try {
          const response = await fetch(url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
              "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({
              alasan_pembatalan: document.getElementById("batal-alasan").value
            })
          });
          const result = await response.json();
          if (!response.ok || result.status !== "success") {
            applyFormErrors(result.errors || { __all__: [result.message] }, formBatal, "batal_");
            showToast(result.message || "Pembatalan belum berhasil.");
            return;
          }
          tutupModal("modal-batal");
          showToast(result.message || "Pendaftaran berhasil dibatalkan.");
          muatDaftarStatus();
          muatRiwayatPartisipasi();
        } catch (err) {
          showToast("Gagal menghubungi server.");
        }
      });
    }

    // Submit Modal Refleksi Riwayat Partisipasi
    const formRefleksi = document.getElementById("form-modal-refleksi");
    if (formRefleksi) {
      formRefleksi.addEventListener("submit", async function (event) {
        event.preventDefault();
        clearFormErrors(formRefleksi, "refleksi_");
        const id = document.getElementById("refleksi-pendaftaran-id").value;
        const url = root.dataset.endpointUbahTemplate.replace(ZERO_UUID, id);

        try {
          const response = await fetch(url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
              "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({
              refleksi_relawan: document.getElementById("refleksi-teks").value
            })
          });
          const result = await response.json();
          if (!response.ok || result.status !== "success") {
            applyFormErrors(
              result.errors || { __all__: [result.message] },
              formRefleksi,
              "refleksi_"
            );
            showToast(result.message || "Gagal menyimpan refleksi.");
            return;
          }
          tutupModal("modal-refleksi");
          showToast(result.message || "Refleksi partisipasi berhasil disimpan.");
          muatRiwayatPartisipasi();
          muatDaftarStatus();
        } catch (err) {
          showToast("Gagal menghubungi server.");
        }
      });
    }

    // Muat data awal saat halaman dibuka
    muatDaftarStatus();
    muatRiwayatPartisipasi();
  }

  /* ---------- Helper publik untuk integrasi dengan Modul 2 (Eksplorasi) ---------- */
  async function cekStatusPadaKegiatan(kegiatanId) {
    const response = await fetch(
      "/volunteer/api/kegiatan/" + encodeURIComponent(kegiatanId) + "/cek-status/",
      { headers: { "X-Requested-With": "XMLHttpRequest" } }
    );
    return response.json();
  }

  window.VoluGreenRelawan = {
    getCsrfToken: getCsrfToken,
    escapeHtml: escapeHtml,
    showToast: showToast,
    cekStatusPadaKegiatan: cekStatusPadaKegiatan
  };

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-drawer]");
    const drawers = document.querySelectorAll(".mobile-drawer");
    drawers.forEach((drawer) => {
      if (trigger && drawer.id === trigger.dataset.drawer) {
        drawer.hidden = !drawer.hidden;
        trigger.setAttribute("aria-expanded", String(!drawer.hidden));
      } else {
        drawer.hidden = true;
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    document.querySelectorAll(".mobile-drawer").forEach((drawer) => { drawer.hidden = true; });
    document.querySelectorAll("[data-drawer]").forEach((button) => button.setAttribute("aria-expanded", "false"));
  });

  paintIcons(document);
  initHalamanDaftarKegiatan();
  initDashboardRelawan();
})();
/* =====================================================================
 * === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
 * ===================================================================== */

