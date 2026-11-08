"use strict";
const $ = (id) => document.getElementById(id);
const nf = new Intl.NumberFormat("fr-CH");
const svgNS = "http://www.w3.org/2000/svg";
let snapshot = { records: [] };

function node(name, attrs = {}) {
  const el = document.createElementNS(svgNS, name);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, String(value));
  return el;
}
function dayString(date) { return date.toISOString().slice(0, 10); }
function filteredRecords() {
  const choice = $("range").value;
  if (choice === "all") return snapshot.records;
  const end = new Date(), start = new Date(end);
  start.setUTCDate(start.getUTCDate() - Number(choice) + 1);
  const lower = dayString(start);
  return snapshot.records.filter((r) => r.day >= lower && r.day <= dayString(end));
}
function drawChart(records) {
  const svg = $("chart");
  svg.replaceChildren();
  const byDay = new Map();
  for (const r of records) byDay.set(r.day, (byDay.get(r.day) || 0) + r.boots);
  const choice = $("range").value;
  let days;
  if (choice === "all") days = [...byDay.keys()].sort();
  else {
    const count = Number(choice), today = new Date();
    days = [];
    for (let i = count - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setUTCDate(date.getUTCDate() - i);
      days.push(dayString(date));
    }
  }
  const values = days.map((day) => byDay.get(day) || 0);
  if (!values.some((value) => value > 0)) {
    $("chart-empty").hidden = false; svg.hidden = true; return;
  }
  $("chart-empty").hidden = true; svg.hidden = false;
  const W = 800, H = 280, left = 48, right = 18, top = 18, bottom = 42;
  const max = Math.max(1, ...values);
  const x = (i) => left + (days.length < 2 ? (W-left-right)/2 : i * (W-left-right)/(days.length-1));
  const y = (v) => top + (max-v) * (H-top-bottom)/max;
  for (let j = 0; j <= 4; j++) {
    const value = Math.ceil(max * j / 4), yy = y(value);
    svg.append(node("line", {x1:left,y1:yy,x2:W-right,y2:yy,class:"grid"}));
    const label = node("text", {x:left-10,y:yy+4,"text-anchor":"end",class:"axis"});
    label.textContent = nf.format(value); svg.append(label);
  }
  const points = values.map((v, i) => [x(i), y(v)]);
  const area = "M " + points[0][0] + " " + (H-bottom) + " " +
    points.map((p) => "L " + p[0] + " " + p[1]).join(" ") +
    " L " + points[points.length-1][0] + " " + (H-bottom) + " Z";
  svg.append(node("path", {d:area,class:"area"}));
  const line = points.map((p,i) => (i ? "L " : "M ") + p[0] + " " + p[1]).join(" ");
  svg.append(node("path", {d:line,class:"line"}));
  const stride = Math.max(1, Math.ceil(days.length / 6));
  points.forEach((p, i) => {
    svg.append(node("circle", {cx:p[0],cy:p[1],r:3.5,class:"dot"}));
    if (i % stride === 0 || i === days.length - 1) {
      const label = node("text", {x:p[0],y:H-12,"text-anchor":"middle",class:"axis"});
      label.textContent = days[i].slice(5); svg.append(label);
    }
  });
}
function render() {
  const records = snapshot.records.slice().sort((a,b) =>
    b.day.localeCompare(a.day) || b.version.localeCompare(a.version) || a.mode.localeCompare(b.mode)
  );
  const total = records.reduce((sum, r) => sum + r.boots, 0);
  $("total").textContent = nf.format(total);
  $("versions").textContent = nf.format(new Set(records.map((r) => r.version)).size);
  const cutoff = new Date();
  cutoff.setUTCDate(cutoff.getUTCDate() - 29);
  const lower = dayString(cutoff);
  $("recent").textContent = nf.format(records.filter((r) => r.day >= lower).reduce((sum,r)=>sum+r.boots,0));
  $("row-count").textContent = nf.format(records.length) + " lignes";
  const body = $("rows"); body.replaceChildren();
  if (!records.length) {
    const tr = document.createElement("tr"), td = document.createElement("td");
    td.colSpan = 4; td.textContent = "Aucun événement reçu."; tr.append(td); body.append(tr);
  } else {
    for (const r of records) {
      const tr = document.createElement("tr");
      for (const value of [r.day, r.version, r.mode === "installed" ? "Installé" : "Live"]) {
        const td = document.createElement("td"); td.textContent = value; tr.append(td);
      }
      const td = document.createElement("td"); td.textContent = nf.format(r.boots);
      td.className = "numeric"; tr.append(td); body.append(tr);
    }
  }
  $("updated").textContent = "Export du " + new Date(snapshot.updated_at).toLocaleString("fr-CH");
  drawChart(filteredRecords());
}
async function load() {
  try {
    const response = await fetch("/api/metrics", {cache:"no-store",credentials:"same-origin"});
    if (!response.ok) throw new Error("metrics unavailable");
    const data = await response.json();
    if (!Array.isArray(data.records)) throw new Error("invalid metrics");
    snapshot = data; $("error").hidden = true; render();
  } catch (_) {
    $("error").hidden = false; $("rows").replaceChildren(); $("chart").replaceChildren();
    $("total").textContent = "—"; $("recent").textContent = "—"; $("versions").textContent = "—";
  }
}
$("range").addEventListener("change", render);
load();
window.setInterval(load, 60_000);