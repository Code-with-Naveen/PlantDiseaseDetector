(function () {
  const MAX_FILES = Number(document.body.dataset.maxBatch || 20);
  const MAX = Number(document.body.dataset.maxMb || 10) * 1024 * 1024;
  const dz = $("#dropzone"), input = $("#file-input"), list = $("#file-list");
  const runBtn = $("#run-btn"), resetBtn = $("#reset-btn"), errEl = $("#form-error"), out = $("#batch-out");
  let files = [];

  const showError = m => { errEl.innerHTML = m ? `<div class="alert error">${esc(m)}</div>` : ""; };

  function setFiles(fl) {
    showError("");
    const imgs = Array.from(fl).filter(f => f.type.startsWith("image/"));
    const skipped = fl.length - imgs.length;
    if (!imgs.length) { showError("No image files selected."); return; }
    if (imgs.length > MAX_FILES) { showError(`Please select at most ${MAX_FILES} images (you chose ${imgs.length}).`); return; }
    const big = imgs.filter(f => f.size > MAX);
    if (big.length) { showError(`These files exceed ${MAX / 1048576} MB: ` + big.map(f => f.name).join(", ")); return; }
    files = imgs;
    list.innerHTML = files.map(f => `<li>📄 ${esc(f.name)} (${(f.size / 1024).toFixed(0)} KB)</li>`).join("");
    if (skipped) showError(`${skipped} non-image file(s) were ignored.`);
    runBtn.disabled = false; resetBtn.hidden = false;
  }
  function reset() { files = []; input.value = ""; list.innerHTML = ""; showError(""); runBtn.disabled = true; resetBtn.hidden = true; out.innerHTML = ""; }

  dz.addEventListener("click", () => input.click());
  dz.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); } });
  input.addEventListener("change", () => setFiles(input.files));
  ["dragenter", "dragover"].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add("drag"); }));
  ["dragleave", "drop"].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove("drag"); }));
  dz.addEventListener("drop", e => setFiles(e.dataTransfer.files));
  resetBtn.addEventListener("click", reset);

  runBtn.addEventListener("click", async () => {
    if (!files.length) return;
    runBtn.disabled = true;
    out.innerHTML = `<div class="card loading"><span class="spinner"></span> Analysing ${files.length} image(s)…</div>`;
    const fd = new FormData(); files.forEach(f => fd.append("images", f));
    try {
      const res = await api("/api/batch", { method: "POST", body: fd });
      const ok = res.filter(r => r.ok), diseased = ok.filter(r => !r.healthy).length;
      out.innerHTML = `
        <div class="grid three" style="margin-bottom:16px">
          <div class="card stat"><div class="num">${ok.length}</div><div class="lbl">Analysed</div></div>
          <div class="card stat"><div class="num" style="color:#b91c1c">${diseased}</div><div class="lbl">Diseased</div></div>
          <div class="card stat"><div class="num">${ok.length - diseased}</div><div class="lbl">Healthy</div></div>
        </div>
        <div class="card"><div class="table-wrap"><table>
          <thead><tr><th>Image</th><th>File</th><th>Plant</th><th>Condition</th><th>Status</th><th>Confidence</th></tr></thead>
          <tbody>${res.map(r => r.ok ? `
            <tr><td><img class="thumb" src="${r.image_url}" alt=""></td><td>${esc(r.filename)}</td>
            <td>${esc(r.plant)}</td><td>${esc(r.condition)}</td>
            <td><span class="badge ${r.healthy ? "ok" : "bad"}">${r.healthy ? "Healthy" : "Diseased"}</span>${r.low_confidence ? ' <span class="badge warn">uncertain</span>' : ""}</td>
            <td>${pct(r.confidence)}</td></tr>` : `
            <tr><td>—</td><td>${esc(r.filename)}</td><td colspan="4"><span class="badge bad">Failed</span> ${esc(r.error)}</td></tr>`).join("")}
          </tbody></table></div>
          <p class="muted" style="margin-bottom:0">Results were also saved to <a href="/history">History</a>.</p></div>`;
    } catch (e) {
      out.innerHTML = `<div class="alert error">❌ ${esc(e.message)}</div>`;
    } finally { runBtn.disabled = false; }
  });
})();
