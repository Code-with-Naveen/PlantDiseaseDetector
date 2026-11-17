/* Shared helpers */
function $(sel, root) { return (root || document).querySelector(sel); }
function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function pct(x) { return (x * 100).toFixed(1) + "%"; }

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove("show"), 2600);
}

/* fetch wrapper that always returns parsed JSON or throws an Error with a readable message */
async function api(url, options) {
  let res;
  try { res = await fetch(url, options); }
  catch (e) { throw new Error("Cannot reach the app. Is the black console window still open?"); }
  let data = null;
  try { data = await res.json(); } catch (e) { /* non-JSON */ }
  if (!res.ok) throw new Error((data && data.error) || ("Request failed (" + res.status + ")"));
  return data;
}

/* Render the analysis of one image (used by Detect and History modal-less detail) */
function renderResult(r) {
  const cls = r.healthy ? "ok" : "bad";
  const status = r.healthy ? "Healthy" : "Disease detected";
  const list = items => "<ul class='tips'>" + items.map(i => "<li>" + esc(i) + "</li>").join("") + "</ul>";
  const bars = r.top5.map((t, i) => `
    <div class="bar-row">
      <div><div class="label">${esc(t.label)}</div>
        <div class="bar"><span class="${t.healthy ? "" : "bad"}" style="width:${(t.confidence * 100).toFixed(1)}%"></span></div></div>
      <div class="pct">${pct(t.confidence)}</div>
    </div>`).join("");
  return `
    <span class="badge ${cls}">${status}</span>
    <div class="result-title">${esc(r.plant)} — ${esc(r.condition)}</div>
    <div class="muted">Confidence: <strong>${pct(r.confidence)}</strong></div>
    ${r.low_confidence ? `<div class="alert warn">⚠️ <strong>Low confidence.</strong> The model is unsure about this image.
      Try a clear, well-lit close-up of a single leaf against a plain background, from one of the supported crops (see About).</div>` : ""}
    <div class="imgs">
      <figure><img src="${r.image_url}" alt="Uploaded leaf"><figcaption>Your image</figcaption></figure>
      <figure><img src="${r.heatmap_url}" alt="Attention heatmap"><figcaption>Where the model looked (red = most important)</figcaption></figure>
    </div>
    <h3>About</h3><p>${esc(r.about)}</p>
    <h3>${r.healthy ? "Care" : "Suggested treatment"}</h3>${list(r.treatment)}
    <h3>Prevention</h3>${list(r.prevention)}
    <h3>Top predictions</h3>${bars}
    <p class="muted" style="font-size:.82rem">This tool is an aid, not a lab diagnosis. For serious or spreading problems consult a local agricultural expert.</p>`;
}
