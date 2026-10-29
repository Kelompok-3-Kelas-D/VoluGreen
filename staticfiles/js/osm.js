(function () {
  "use strict";

  const endpoint = "https://nominatim.openstreetmap.org/search";
  let lastRequestAt = 0;

  async function findPlace(query) {
    const delay = Math.max(0, 1100 - (Date.now() - lastRequestAt));
    if (delay) await new Promise((resolve) => setTimeout(resolve, delay));
    lastRequestAt = Date.now();

    const url = new URL(endpoint);
    url.search = new URLSearchParams({
      format: "jsonv2",
      addressdetails: "1",
      limit: "1",
      countrycodes: "id",
      q: query,
    });
    const response = await fetch(url, { headers: { "Accept-Language": "id" } });
    if (!response.ok) throw new Error("Pencarian lokasi sedang tidak tersedia.");
    const places = await response.json();
    if (!places.length) throw new Error("Lokasi tidak ditemukan. Coba tambahkan nama jalan atau kota.");
    return places[0];
  }

  function mapUrls(place) {
    const lat = Number(place.lat);
    const lon = Number(place.lon);
    const bounds = (place.boundingbox || []).map(Number);
    const south = Number.isFinite(bounds[0]) ? bounds[0] : lat - 0.006;
    const north = Number.isFinite(bounds[1]) ? bounds[1] : lat + 0.006;
    const west = Number.isFinite(bounds[2]) ? bounds[2] : lon - 0.006;
    const east = Number.isFinite(bounds[3]) ? bounds[3] : lon + 0.006;
    const embed = new URL("https://www.openstreetmap.org/export/embed.html");
    embed.search = new URLSearchParams({
      bbox: [west, south, east, north].join(","),
      layer: "mapnik",
      marker: `${lat},${lon}`,
    });
    const full = new URL("https://www.openstreetmap.org/");
    full.searchParams.set("mlat", String(lat));
    full.searchParams.set("mlon", String(lon));
    full.hash = `map=16/${lat}/${lon}`;
    return { lat, lon, embed: embed.toString(), full: full.toString() };
  }

  function connectActivityMap(button) {
    const form = button.closest("form");
    const status = form.querySelector("[data-osm-status]");
    const frame = form.querySelector("[data-osm-frame]");
    const frameWrap = form.querySelector("[data-osm-frame-wrap]");
    const mapLink = form.querySelector("[data-osm-link]");
    const latitude = form.querySelector("[name=latitude]");
    const longitude = form.querySelector("[name=longitude]");
    const locationFields = ["nama_lokasi", "alamat", "kota"]
      .map((name) => form.querySelector(`[name="${name}"]`))
      .filter(Boolean);

    button.addEventListener("click", async () => {
      const query = locationFields.map((field) => field.value.trim()).filter(Boolean).join(", ");
      if (!query) {
        status.textContent = "Isi nama tempat atau kota terlebih dahulu.";
        locationFields[0]?.focus();
        return;
      }
      button.disabled = true;
      status.textContent = "Mencari lokasi di OpenStreetMap…";
      try {
        const place = await findPlace(query);
        const map = mapUrls(place);
        latitude.value = map.lat.toFixed(6);
        longitude.value = map.lon.toFixed(6);
        frame.src = map.embed;
        frameWrap.hidden = false;
        mapLink.href = map.full;
        mapLink.hidden = false;
        status.textContent = `Lokasi ditemukan: ${place.display_name}. Pin tersimpan otomatis.`;
      } catch (error) {
        latitude.value = "";
        longitude.value = "";
        frameWrap.hidden = true;
        mapLink.hidden = true;
        status.textContent = error.message || "Pencarian gagal. Periksa koneksi internet lalu coba lagi.";
      } finally {
        button.disabled = false;
      }
    });

    locationFields.forEach((field) => field.addEventListener("input", () => {
      latitude.value = "";
      longitude.value = "";
      frameWrap.hidden = true;
      mapLink.hidden = true;
      status.textContent = "Lokasi berubah. Cari kembali agar pin peta sesuai.";
    }));
  }

  async function loadOrganizationMap() {
    const frame = document.querySelector("[data-org-osm-frame]");
    if (!frame || frame.dataset.loaded === "true") return;
    const city = document.querySelector('[data-bind="org-city"]')?.textContent.trim();
    const status = document.querySelector("[data-org-osm-status]");
    if (!city || city === "Lokasi belum diisi") {
      status.textContent = "Tambahkan kota organisasi pada profil untuk melihat petanya.";
      return;
    }
    const button = document.querySelector("[data-org-osm-load]");
    const empty = document.querySelector("[data-org-osm-empty]");
    button.disabled = true;
    status.textContent = "Mencari kota di OpenStreetMap…";
    try {
      const map = mapUrls(await findPlace(city));
      frame.src = map.embed;
      frame.hidden = false;
      empty.hidden = true;
      document.querySelector("[data-org-osm-link]").href = map.full;
      document.querySelector("[data-org-osm-link]").hidden = false;
      frame.dataset.loaded = "true";
      status.textContent = "Peta kota organisasi · © OpenStreetMap contributors";
    } catch (error) {
      status.textContent = error.message || "Peta tidak dapat dimuat. Periksa koneksi internet lalu coba lagi.";
    } finally {
      button.disabled = false;
    }
  }

  document.querySelectorAll("[data-osm-search]").forEach(connectActivityMap);
  document.querySelector("[data-org-osm-load]")?.addEventListener("click", loadOrganizationMap);
})();
