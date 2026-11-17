(function () {
  const body = $("#history-body"), q = $("#q"), plant = $("#plant"), status = $("#status");
  let rows = [], timer = null;

  async function load() {
    const p = new URLSearchParams({ q: q.value, plant: plant.value, status: status.value });
    try { rows = await api("/api/history?" + p); render(); }
    catch (e) { body.innerHTML = `<div class="alert error">${esc(e.message)}</div>`; }
  }
  function render() {
    if (!rows.length) {
      body.innerHTML = `<div class="empty"><div class="icon">🗒️</div>No predictions yet. <a href="/">Analyse a leaf</a> to get started.</div>`;
      return;
    }
    body.innerHTML = `<div class="table-wrap"><table>
      <thead><tr><th>Image</th><th>Date</th><th>Plant</th><th>Condition</th><th>Status</th><th>Confidence</th><th></th></tr></thead><tbody>
      ${rows.map(r => `<tr>
        <td><img class="thumb" src="${r.image_url}" alt=""></td>
        <td>${esc(r.created_at)}</td><td>${esc(r.plant)}</td><td>${esc(r.condition)}</td>
        <td><span class="badge ${r.is_healthy ? "ok" : "bad"}">${r.is_healthy ? "Healthy" : "Diseased"}</span></td>
        <td>${pct(r.confidence)}</td>
        <td style="white-space:nowrap"><button class="btn secondary small" data-view="${r.id}">View</button>
            <button class="btn danger small" data-del="${r.id}">Delete</button></td></tr>`).join("")}
      </tbody></table></div><p class="muted" style="margin:10px 0 0">${rows.length} record(s)</p>`;
  }

  body.addEventListener("click", async e => {
    const v = e.target.closest("[data-view]"), d = e.target.closest("[data-del]");
    if (v) {
      const r = rows.find(x => x.id == v.dataset.view); if (!r) return;
      $("#detail-body").innerHTML = renderResult({
        plant: r.plant, condition: r.condition, healthy: r.is_healthy, confidence: r.confidence,
        low_confidence: r.confidence < 0.6, top5: r.top5, image_url: r.image_url,
        heatmap_url: r.heatmap_url || r.image_url, about: r.about, treatment: r.treatment, prevention: r.prevention
      });
      $("#detail").hidden = false; $("#detail").scrollIntoView({ behavior: "smooth" });
    }
    if (d && confirm("Delete this record?")) {
      try { await api("/api/history/" + d.dataset.del, { method: "DELETE" }); toast("Record deleted"); load(); }
      catch (err) { toast(err.message); }
    }
  });
  $("#close-detail").addEventListener("click", () => { $("#detail").hidden = true; });
  $("#clear-btn").addEventListener("click", async () => {
    if (!rows.length) return toast("History is already empty");
    if (!confirm("Delete ALL prediction history and stored images? This cannot be undone.")) return;
    try { await api("/api/history", { method: "DELETE" }); toast("History cleared"); load(); }
    catch (err) { toast(err.message); }
  });
  q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(load, 250); });
  plant.addEventListener("change", load); status.addEventListener("change", load);
  load();
})();
