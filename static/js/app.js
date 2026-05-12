/* global bootstrap – loaded from CDN in the HTML */

document.addEventListener("DOMContentLoaded", () => {
  const urlInput = document.getElementById("urlInput");
  const linkCount = document.getElementById("linkCount");
  const clearBtn = document.getElementById("clearBtn");
  const scrapeBtn = document.getElementById("scrapeBtn");
  const progressSection = document.getElementById("progressSection");
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");
  const resultsSection = document.getElementById("resultsSection");
  const resultsBody = document.querySelector("#resultsTable tbody");
  const exportBtn = document.getElementById("exportBtn");

  let scrapedResults = [];

  /* ---- helpers ---- */

  function parseUrls() {
    return urlInput.value
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.length > 0);
  }

  function updateLinkCount() {
    const count = parseUrls().length;
    linkCount.textContent = `${count} link${count !== 1 ? "s" : ""} entered`;
    scrapeBtn.disabled = count === 0;
    clearBtn.disabled = urlInput.value.trim().length === 0;
  }

  function formatNumber(n) {
    if (n === null || n === undefined || n === "N/A") return "N/A";
    const num = Number(n);
    if (Number.isNaN(num)) return String(n);
    return num.toLocaleString();
  }

  function showToast(message, variant = "success") {
    const container = document.getElementById("toastContainer");
    const id = "toast-" + Date.now();
    const html = `
      <div id="${id}" class="toast align-items-center text-bg-${variant} border-0" role="alert">
        <div class="d-flex">
          <div class="toast-body">${message}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto"
                  data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    container.insertAdjacentHTML("beforeend", html);
    const toastEl = document.getElementById(id);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
    bsToast.show();
    toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
  }

  function setProgress(pct, text) {
    progressBar.style.width = pct + "%";
    progressBar.textContent = Math.round(pct) + "%";
    if (text) progressText.textContent = text;
  }

  /* ---- scrape ---- */

  async function scrape() {
    const urls = parseUrls();
    if (urls.length === 0) return;

    scrapeBtn.disabled = true;
    clearBtn.disabled = true;
    urlInput.disabled = true;
    resultsSection.classList.add("d-none");
    progressSection.classList.remove("d-none");
    setProgress(0, `Processing 0 / ${urls.length}…`);
    scrapedResults = [];
    resultsBody.innerHTML = "";

    /* Process in batches of 3 to avoid overloading the server */
    const batchSize = 3;
    let completed = 0;

    for (let i = 0; i < urls.length; i += batchSize) {
      const batch = urls.slice(i, i + batchSize);
      try {
        const resp = await fetch("/api/scrape", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ urls: batch }),
        });
        const data = await resp.json();
        if (data.results) {
          scrapedResults.push(...data.results);
        }
      } catch (err) {
        batch.forEach((url) =>
          scrapedResults.push({ error: "Network error", url })
        );
      }
      completed += batch.length;
      const pct = (completed / urls.length) * 100;
      setProgress(pct, `Processing ${completed} / ${urls.length}…`);
    }

    renderResults();
    progressSection.classList.add("d-none");
    resultsSection.classList.remove("d-none");
    urlInput.disabled = false;
    scrapeBtn.disabled = false;
    clearBtn.disabled = false;

    const errors = scrapedResults.filter((r) => r.error).length;
    if (errors > 0) {
      showToast(
        `Scraped ${scrapedResults.length} videos (${errors} failed)`,
        "warning"
      );
    } else {
      showToast(`Successfully scraped ${scrapedResults.length} videos`);
    }
  }

  function renderResults() {
    resultsBody.innerHTML = "";
    scrapedResults.forEach((item, idx) => {
      const tr = document.createElement("tr");
      if (item.error) {
        tr.classList.add("error-row");
        tr.innerHTML = `
          <td>${idx + 1}</td>
          <td colspan="3"><span class="badge bg-warning text-dark">Error</span>
            ${escapeHtml(item.url || "")}</td>
          <td colspan="4">${escapeHtml(item.error)}</td>`;
      } else {
        tr.innerHTML = `
          <td>${idx + 1}</td>
          <td>${escapeHtml(item.date)}</td>
          <td>${escapeHtml(item.channel)}</td>
          <td><a href="${escapeHtml(item.url)}" target="_blank" rel="noopener"
                 title="${escapeHtml(item.url)}">${truncate(item.url, 40)}</a></td>
          <td title="${escapeHtml(item.title)}">${escapeHtml(truncate(item.title, 48))}</td>
          <td>${formatNumber(item.views)}</td>
          <td>${formatNumber(item.likes)}</td>
          <td>${formatNumber(item.comments)}</td>`;
      }
      resultsBody.appendChild(tr);
    });
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  function truncate(str, max) {
    if (!str) return "";
    return str.length > max ? str.slice(0, max - 1) + "…" : str;
  }

  /* ---- export ---- */

  async function exportToExcel() {
    if (scrapedResults.length === 0) return;
    exportBtn.disabled = true;
    exportBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm"></span> Exporting…';

    try {
      const resp = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ results: scrapedResults }),
      });
      if (!resp.ok) throw new Error("Export failed");

      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "youtube_metadata.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      showToast("Excel file downloaded!");
    } catch (err) {
      showToast("Export failed: " + err.message, "danger");
    } finally {
      exportBtn.disabled = false;
      exportBtn.innerHTML =
        '<i class="bi bi-file-earmark-excel"></i> Export to Excel';
    }
  }

  /* ---- events ---- */

  urlInput.addEventListener("input", updateLinkCount);
  clearBtn.addEventListener("click", () => {
    urlInput.value = "";
    updateLinkCount();
    resultsSection.classList.add("d-none");
    scrapedResults = [];
  });
  scrapeBtn.addEventListener("click", scrape);
  exportBtn.addEventListener("click", exportToExcel);

  updateLinkCount();
});
