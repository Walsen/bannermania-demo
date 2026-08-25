"use strict";

const $ = (id) => document.getElementById(id);
const controls = ["text", "font", "effect", "pattern", "border", "size",
                  "fg", "fg2", "bg", "accent", "animate", "motion", "speed", "cycle"];

function buildQuery() {
  const [width, height] = $("size").value.split("x");
  const params = new URLSearchParams({
    text: $("text").value || "BANNER",
    font: $("font").value,
    effect: $("effect").value,
    pattern: $("pattern").value,
    border: $("border").value,
    fg: $("fg").value,
    fg2: $("fg2").value,
    bg: $("bg").value,
    accent: $("accent").value,
    width,
    height,
  });
  if ($("animate").checked) {
    // Slider is ms/frame: lower = faster. Invert so "right" reads as faster.
    const ms = 220 - Number($("speed").value);
    params.set("speed", String(ms));
    params.set("motion", $("motion").value);
    if ($("cycle").checked) params.set("cycle", "1");
  }
  return params;
}

function endpoint() {
  return $("animate").checked ? "/generate.gif" : "/generate";
}

function refresh() {
  const isGif = $("animate").checked;
  $("speedRow").hidden = !isGif;
  $("motionRow").hidden = !isGif;
  $("cycleRow").hidden = !isGif;

  const params = buildQuery();
  params.set("_", Date.now().toString()); // cache-bust
  $("banner").src = endpoint() + "?" + params.toString();

  const dl = buildQuery();
  dl.set("download", "1");
  const a = $("download");
  a.href = endpoint() + "?" + dl.toString();
  a.setAttribute("download", isGif ? "banner.gif" : "banner.png");

  const cyc = isGif && $("cycle").checked ? " · 🌈cycle" : "";
  $("status").textContent =
    `${isGif ? $("motion").value + " gif · " : ""}${$("effect").value} · ${$("font").value} · ${$("pattern").value} · ${$("border").value}${cyc}`;
}

let timer = null;
function scheduleRefresh() {
  clearTimeout(timer);
  // GIFs are heavier to render — debounce a touch longer.
  timer = setTimeout(refresh, $("animate").checked ? 300 : 120);
}

controls.forEach((id) => {
  const el = $(id);
  el.addEventListener("input", scheduleRefresh);
  el.addEventListener("change", scheduleRefresh);
});

$("speed").addEventListener("input", () => {
  const v = Number($("speed").value);
  $("speedVal").textContent = v < 70 ? "fast" : v < 140 ? "medium" : "slow";
});

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomColor() {
  return "#" + Math.floor(Math.random() * 0xffffff).toString(16).padStart(6, "0");
}

$("randomize").addEventListener("click", () => {
  const opts = (sel) => Array.from($(sel).options).map((o) => o.value);
  $("font").value = pick(opts("font"));
  $("effect").value = pick(opts("effect"));
  $("pattern").value = pick(opts("pattern"));
  $("border").value = pick(opts("border"));
  $("fg").value = randomColor();
  $("fg2").value = randomColor();
  $("bg").value = randomColor();
  $("accent").value = randomColor();
  refresh();
});

refresh();
