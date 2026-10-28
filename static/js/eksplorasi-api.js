(() => {
  const searchForm = document.getElementById("activity-search-form");
  const searchInput = searchForm?.querySelector('input[name="q"]');
  const suggestions = document.getElementById("activity-suggestions");
  const searchStatus = document.getElementById("api-search-status");
  const communityProof = document.querySelector("[data-community-url]");
  if (!searchInput || !suggestions) return;

  const apiUrl = (base, values = {}) => {
    const url = new URL(base, window.location.origin);
    for (const [key, value] of Object.entries(values)) {
      if (value) url.searchParams.set(key, value);
    }
    return url;
  };

  async function getJson(url) {
    const response = await fetch(url, {
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    return response.json();
  }

  async function refreshDirectory(query = "") {
    const values = {
      q: query,
      kota: searchForm.elements.kota?.value,
      kategori: searchForm.elements.kategori?.value,
    };
    const activityResponse = await getJson(apiUrl(searchInput.dataset.suggestUrl, values));

    suggestions.replaceChildren();
    const labels = new Set();
    for (const activity of activityResponse.data) {
      const label = activity.name;
      if (labels.has(label)) continue;
      labels.add(label);
      const option = document.createElement("option");
      option.value = label;
      option.label = activity.organizer.name;
      suggestions.append(option);
    }
    if (searchStatus) {
      searchStatus.textContent = query
        ? `${activityResponse.meta.total} kegiatan cocok dengan pencarianmu.`
        : "";
    }
  }

  let debounce;
  searchInput.addEventListener("input", () => {
    window.clearTimeout(debounce);
    debounce = window.setTimeout(() => {
      refreshDirectory(searchInput.value.trim()).catch(() => {
        if (searchStatus) searchStatus.textContent = "Saran pencarian belum tersedia; kamu tetap bisa menekan Cari.";
      });
    }, 250);
  });

  searchForm.addEventListener("change", () => {
    refreshDirectory(searchInput.value.trim()).catch(() => {});
  });

  refreshDirectory(searchInput.value.trim()).catch(() => {
    if (searchStatus) searchStatus.textContent = "Saran pencarian belum tersedia; kamu tetap bisa memakai filter.";
  });

  if (communityProof) {
    getJson(new URL(communityProof.dataset.communityUrl, window.location.origin))
      .then((response) => {
        for (const [key, value] of Object.entries(response.data)) {
          const target = communityProof.querySelector(`[data-community-value="${key}"]`);
          if (target) target.textContent = new Intl.NumberFormat("id-ID").format(value);
        }
      })
      .catch(() => communityProof.remove());
  }
})();
