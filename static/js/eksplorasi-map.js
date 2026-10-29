(() => {
  const element = document.getElementById("activity-map");
  const dataElement = document.getElementById("activity-map-markers");
  if (!element || !dataElement || !window.L) return;

  let markers = [];
  try {
    markers = JSON.parse(dataElement.textContent || "[]");
  } catch (error) {
    console.error("Data marker peta tidak dapat dibaca.", error);
  }

  const map = L.map(element, { scrollWheelZoom: false }).setView([-2.5, 118], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  const points = [];
  markers.forEach((item) => {
    const lat = Number(item.lat);
    const lng = Number(item.lng);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

    const marker = L.marker([lat, lng]).addTo(map);
    const popup = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = item.nama || "Kegiatan lingkungan";
    popup.appendChild(title);

    const location = document.createElement("p");
    location.textContent = [item.lokasi, item.tanggal].filter(Boolean).join(" · ");
    popup.appendChild(location);

    if (item.url) {
      const link = document.createElement("a");
      link.href = item.url;
      link.textContent = "Lihat detail kegiatan";
      popup.appendChild(link);
    }
    marker.bindPopup(popup);
    points.push([lat, lng]);
  });

  if (points.length === 1) map.setView(points[0], 14);
  else if (points.length > 1) map.fitBounds(points, { padding: [28, 28], maxZoom: 14 });

  requestAnimationFrame(() => map.invalidateSize());
})();
