(async function () {
  const root = $("#dash");
  let s;
  try { s = await api("/api/stats"); }
  catch (e) { root.innerHTML = `<div class="alert error">${esc(e.message)}</div>`; return; }

  if (!s.total) {
    root.innerHTML = `<div class="card empty"><div class="icon">📊</div>No data yet.
      <p><a class="btn" href="/">Analyse your first leaf</a></p></div>`;
    return;
  }
  root.innerHTML = `
    <div class="grid four" style="margin-bottom:20px">
      <div class="card stat"><div class="num">${s.total}</div><div class="lbl">Leaves analysed</div></div>
      <div class="card stat"><div class="num" style="color:#b91c1c">${s.diseased}</div><div class="lbl">Diseased</div></div>
      <div class="card stat"><div class="num">${s.healthy}</div><div class="lbl">Healthy</div></div>
      <div class="card stat"><div class="num">${pct(s.avg_confidence)}</div><div class="lbl">Average confidence</div></div>
    </div>
    <div class="grid two" style="margin-bottom:20px">
      <div class="card"><h2>Healthy vs diseased</h2><div class="chart-box"><canvas id="c-health"></canvas></div></div>
      <div class="card"><h2>Analyses by plant</h2><div class="chart-box"><canvas id="c-plant"></canvas></div></div>
    </div>
    <div class="grid two">
      <div class="card"><h2>Most detected diseases</h2><div class="chart-box"><canvas id="c-dis"></canvas></div></div>
      <div class="card"><h2>Activity (last 14 days)</h2><div class="chart-box"><canvas id="c-day"></canvas></div></div>
    </div>`;

  const green = "#16a34a", red = "#ef4444";
  const palette = ["#16a34a", "#0ea5e9", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#64748b", "#84cc16", "#e11d48"];
  const opts = { responsive: true, maintainAspectRatio: false };

  new Chart($("#c-health"), { type: "doughnut", data: { labels: ["Healthy", "Diseased"],
    datasets: [{ data: [s.healthy, s.diseased], backgroundColor: [green, red] }] },
    options: { ...opts, plugins: { legend: { position: "bottom" } } } });

  new Chart($("#c-plant"), { type: "bar", data: { labels: s.by_plant.map(x => x.plant),
    datasets: [{ label: "Analyses", data: s.by_plant.map(x => x.n), backgroundColor: palette }] },
    options: { ...opts, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } } });

  if (s.top_diseases.length) {
    new Chart($("#c-dis"), { type: "bar", data: { labels: s.top_diseases.map(x => x.label),
      datasets: [{ label: "Detections", data: s.top_diseases.map(x => x.n), backgroundColor: red }] },
      options: { ...opts, indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } } });
  } else {
    $("#c-dis").parentElement.innerHTML = `<div class="empty">No diseases detected yet 🎉</div>`;
  }

  new Chart($("#c-day"), { type: "line", data: { labels: s.per_day.map(x => x.day),
    datasets: [{ label: "All", data: s.per_day.map(x => x.n), borderColor: green, backgroundColor: "rgba(22,163,74,.15)", fill: true, tension: .3 },
               { label: "Diseased", data: s.per_day.map(x => x.diseased), borderColor: red, tension: .3 }] },
    options: { ...opts, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } } });
})();
