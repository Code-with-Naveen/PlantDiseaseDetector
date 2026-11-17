(function () {
  const MAX = Number(document.body.dataset.maxMb || 10) * 1024 * 1024;
  const dz = $("#dropzone"), input = $("#file-input");
  const btn = $("#analyse-btn"), resetBtn = $("#reset-btn");
  const resultEl = $("#result"), errEl = $("#form-error");
  let file = null;

  const showError = m => { errEl.innerHTML = m ? `<div class="alert error">${esc(m)}</div>` : ""; };

  function setFile(f) {
    showError("");
    if (!f) return;
    if (!f.type.startsWith("image/")) { showError("Please choose an image file (JPG, PNG, BMP or WEBP)."); return; }
    file = f;
    $("#dz-empty").hidden = true; $("#dz-preview").hidden = false;
    $("#preview-img").src = URL.createObjectURL(f);
    $("#preview-name").textContent = f.name;
    btn.disabled = false; resetBtn.hidden = false;
  }
  function reset() {
    file = null; input.value = ""; showError("");
    $("#dz-empty").hidden = false; $("#dz-preview").hidden = true;
    btn.disabled = true; resetBtn.hidden = true;
  }

  dz.addEventListener("click", () => input.click());
  dz.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); } });
  input.addEventListener("change", () => setFile(input.files[0]));
  ["dragenter", "dragover"].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add("drag"); }));
  ["dragleave", "drop"].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove("drag"); }));
  dz.addEventListener("drop", e => setFile(e.dataTransfer.files[0]));
  resetBtn.addEventListener("click", reset);

  function loading() {
    resultEl.innerHTML = `<div class="loading"><span class="spinner"></span> Analysing leaf…</div>`;
  }
  function show(r) {
    resultEl.innerHTML = renderResult(r);
    $("#result-card").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
  function fail(e) {
    resultEl.innerHTML = `<div class="alert error">❌ ${esc(e.message)}</div>`;
  }

  btn.addEventListener("click", async () => {
    if (!file) return;
    if (file.size > MAX) { showError("File is too large. Maximum size is " + (MAX / 1048576) + " MB."); return; }
    btn.disabled = true; loading();
    const fd = new FormData(); fd.append("image", file);
    try { show(await api("/api/predict", { method: "POST", body: fd })); }
    catch (e) { fail(e); }
    finally { btn.disabled = false; }
  });

  /* samples */
  api("/api/samples").then(list => {
    const box = $("#samples");
    if (!list.length) { box.innerHTML = `<div class="empty">No sample images found.</div>`; return; }
    // show 2 per class interleaved so variety is visible at the top
    box.innerHTML = list.map(s => `
      <button class="sample" data-path="${esc(s.path)}" title="${esc(s.plant)} - ${esc(s.condition)}">
        <img loading="lazy" src="/sample-image/${encodeURI(s.path)}" alt="">
        <small>${esc(s.plant)}<br>${esc(s.condition)}</small>
      </button>`).join("");
    box.addEventListener("click", async e => {
      const b = e.target.closest(".sample"); if (!b) return;
      loading();
      try { show(await api("/api/predict-sample", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: b.dataset.path }) })); }
      catch (err) { fail(err); }
    });
  }).catch(() => { $("#samples").innerHTML = `<div class="empty">Could not load samples.</div>`; });
})();
