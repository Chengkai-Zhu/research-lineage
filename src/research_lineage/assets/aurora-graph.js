"use strict";

// Presentation only: neither focus selection nor layout creates research relations.
function auroraFocus(data, limit = 12) {
  const ids = new Set(data.results.map((result) => result.id));
  const authored = [...(data.reading_route || []),
    ...(data.narrative?.turning_points || []).flatMap((point) => point.result_ids)];
  const selected = [...new Set(authored)].filter((id) => ids.has(id)).slice(0, limit);
  // Maps without an authored route remain complete; do not invent milestones.
  return selected.length ? selected : [...ids];
}

function auroraLayout(items, works, width) {
  const ordered = [...items].sort((a, b) =>
    works[a.work_id].first_published.localeCompare(works[b.work_id].first_published) ||
    a.id.localeCompare(b.id));
  width = Math.max(280, width);
  const columns = Math.max(1, Math.min(4, ordered.length, Math.floor((width - 24) / 202)));
  const gap = columns === 1 ? 0 : 34;
  const cardWidth = Math.min(240, (width - 64 - gap * (columns - 1)) / columns);
  const used = columns * cardWidth + (columns - 1) * gap;
  const left = (width - used) / 2;
  const positions = {}, periods = [];
  for (let column = 0; column < columns; column++) {
    const group = ordered.slice(Math.floor(column * ordered.length / columns), Math.floor((column + 1) * ordered.length / columns));
    const x = left + column * (cardWidth + gap);
    group.forEach((result, row) => { positions[result.id] = { x, y: 74 + row * 160, width: cardWidth, height: 122 }; });
    if (group.length) {
      const first = works[group[0].work_id].first_published.slice(0, 4);
      const last = works[group.at(-1).work_id].first_published.slice(0, 4);
      periods.push({ x, width: cardWidth, label: first === last ? first : first + "–" + last });
    }
  }
  return { positions, periods, width, height: Math.max(420, 90 + Math.ceil(ordered.length / columns) * 160) };
}

function auroraConnection(a, b) {
  const y1 = a.y + a.height / 2, y2 = b.y + b.height / 2;
  if (a.x === b.x) {
    const x = a.x + a.width;
    return `M${x} ${y1} C${x + 30} ${y1}, ${x + 30} ${y2}, ${x} ${y2}`;
  }
  const x1 = a.x < b.x ? a.x + a.width : a.x;
  const x2 = a.x < b.x ? b.x : b.x + b.width;
  const middle = (x1 + x2) / 2;
  return `M${x1} ${y1} C${middle} ${y1}, ${middle} ${y2}, ${x2} ${y2}`;
}

function readGraphPreference(text) {
  let saved;
  try { saved = JSON.parse(text); } catch (_) { /* Use the initial presentation. */ }
  return { density: saved?.density === "all" ? "all" : "focus", theme: saved?.theme === "light" ? "light" : "dark" };
}

function auroraWrap(node, text, width, part) {
  node.replaceChildren();
  const tokens = text.match(/[\u2e80-\uffef]|[^\s\u2e80-\uffef]+|\s+/gu) || [];
  const rows = [part("tspan", { x: 16, dy: 0 }, "")];
  node.append(rows[0]);
  let clipped = false;
  for (const token of tokens) {
    let row = rows.at(-1), previous = row.textContent;
    row.textContent = (previous + token).trimStart();
    if (row.getComputedTextLength() <= width) continue;
    row.textContent = previous.trimEnd();
    if (!token.trim()) { row.textContent = previous + token; continue; }
    // Keep words intact when they fit a fresh line. Only long tokens split.
    if (row.textContent) {
      if (rows.length === 3) { clipped = true; break; }
      row = part("tspan", { x: 16, dy: 18 }, "");
      rows.push(row); node.append(row);
    }
    // A long unbroken title/token also wraps; it must never escape the card.
    for (const char of token) {
      row = rows.at(-1);
      const before = row.textContent;
      row.textContent = (before + char).trimStart();
      if (row.getComputedTextLength() <= width) continue;
      row.textContent = before.trimEnd();
      if (rows.length === 3) { clipped = true; break; }
      row = part("tspan", { x: 16, dy: 18 }, char.trimStart());
      rows.push(row); node.append(row);
    }
    if (clipped) break;
  }
  rows.forEach((row) => { row.textContent = row.textContent.trimEnd(); });
  if (clipped) {
    const last = rows.at(-1);
    let label = last.textContent.trimEnd();
    last.textContent = label + "…";
    while (last.getComputedTextLength() > width && label) {
      label = Array.from(label).slice(0, -1).join("");
      last.textContent = label + "…";
    }
  }
}

function createAuroraGraph(data) {
  const $ = (id) => document.getElementById(id);
  const svg = $("lineage-map"), scroll = $("graph-scroll");
  const works = Object.fromEntries(data.works.map((work) => [work.id, work]));
  const nodes = new Map(data.results.map((r) => [r.id, $("result-" + r.id)]));
  const edges = new Map(data.relations.map((r) => [r.id, $("relation-" + r.id)]));
  const focus = new Set(auroraFocus(data));
  const preference = readGraphPreference($("graph-preference").textContent);
  let matching = data.results, filtered = false, selected = null, selectedType = "result", route = [], zoom = 1, frame;
  const ns = "http://www.w3.org/2000/svg";
  function part(tag, attrs, text) {
    const node = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function visible() {
    if (preference.density === "all" || filtered || $("color-mode").value !== "thread") return matching;
    const included = new Set([...focus, ...route]);
    if (selectedType === "result") included.add(selected);
    else {
      const edge = data.relations.find((item) => item.id === selected);
      if (edge) { included.add(edge.source); included.add(edge.target); }
    }
    return matching.filter((item) => included.has(item.id));
  }
  function highlight() {
    const neighbors = new Set([selected]), connected = new Set();
    data.relations.forEach((edge) => {
      if ((selectedType === "result" && (edge.source === selected || edge.target === selected)) ||
          (selectedType === "relation" && edge.id === selected)) {
        neighbors.add(edge.source); neighbors.add(edge.target); connected.add(edge.id);
      }
    });
    nodes.forEach((node, id) => {
      node.classList.toggle("selected", selectedType === "result" && selected === id);
      node.classList.toggle("context-node", !!selected && !neighbors.has(id));
      node.classList.toggle("related-node", !!selected && neighbors.has(id));
      node.classList.toggle("route-node", route.includes(id));
      node.setAttribute("aria-pressed", String(selectedType === "result" && selected === id));
    });
    edges.forEach((edge, id) => {
      edge.classList.toggle("selected", selectedType === "relation" && selected === id);
      edge.classList.toggle("connected-edge", connected.has(id));
      edge.classList.toggle("context-edge", !!selected && !connected.has(id));
    });
  }
  function draw() {
    frame = null;
    const items = visible(), ids = new Set(items.map((item) => item.id));
    const constrained = filtered || $("color-mode").value !== "thread";
    $("graph-focus").setAttribute("aria-pressed", String(preference.density === "focus" && !constrained && focus.size < data.results.length));
    $("graph-all").setAttribute("aria-pressed", String(preference.density === "all" || constrained || focus.size === data.results.length));
    $("graph-focus").disabled = constrained;
    $("graph-all").disabled = constrained;
    $("graph-count").textContent = items.length + " of " + data.results.length + " results";
    $("graph-caption").textContent = constrained ? "All matching results are shown; colors follow your selection." :
      preference.density === "focus" && focus.size < data.results.length
        ? "Focus follows the authored reading route and overview."
        : "Follow a connection. Inspect the evidence.";
    if (!scroll.clientWidth) return;
    const geometry = auroraLayout(items, works, scroll.clientWidth);
    svg.setAttribute("viewBox", `0 0 ${geometry.width} ${geometry.height}`);
    svg.style.width = geometry.width * zoom + "px";
    svg.style.height = geometry.height * zoom + "px";
    svg.querySelector(".graph-paper").setAttribute("width", geometry.width);
    svg.querySelector(".graph-note").setAttribute("display", "none");
    const periods = svg.querySelector(".periods");
    periods.replaceChildren();
    geometry.periods.forEach((period, index) => {
      periods.append(part("text", { x: period.x, y: 32, class: "period-label" }, period.label),
        part("path", { class: "period-line", d: `M${period.x} 46 H${period.x + period.width}` }));
      if (index > 0) periods.append(part("path", { class: "period-guide", d: `M${period.x - 17} 62 V${geometry.height - 20}` }));
    });
    data.results.forEach((result) => {
      const node = nodes.get(result.id), position = geometry.positions[result.id];
      node.classList.toggle("hidden", !position);
      node.setAttribute("tabindex", position ? "0" : "-1");
      node.setAttribute("aria-hidden", String(!position));
      if (!position) return;
      node.setAttribute("transform", `translate(${position.x},${position.y})`);
      node.querySelector(".node-card").setAttribute("width", position.width);
      auroraWrap(node.querySelector(".label"), result.label, position.width - 32, part);
    });
    data.relations.forEach((edge) => {
      const node = edges.get(edge.id), show = ids.has(edge.source) && ids.has(edge.target);
      node.classList.toggle("hidden", !show);
      node.setAttribute("tabindex", show ? "0" : "-1");
      node.setAttribute("aria-hidden", String(!show));
      if (show) node.querySelectorAll("path").forEach((path) => path.setAttribute("d", auroraConnection(geometry.positions[edge.source], geometry.positions[edge.target])));
    });
    highlight();
  }
  function schedule() {
    if (!frame) frame = requestAnimationFrame(draw);
  }
  $("graph-focus").textContent = "Focus · " + focus.size;
  $("graph-all").textContent = "All · " + data.results.length;
  $("graph-focus").hidden = focus.size === data.results.length;
  ["focus", "all"].forEach((mode) => $("graph-" + mode).addEventListener("click", () => {
    preference.density = mode;
    scroll.scrollTop = 0;
    schedule();
  }));
  function theme() {
    document.body.dataset.graphTheme = preference.theme;
    $("graph-theme").value = preference.theme;
  }
  $("graph-theme").addEventListener("change", () => { preference.theme = $("graph-theme").value; theme(); });
  theme();
  const legend = $("thread-legend");
  data.lanes.forEach((lane) => {
    const item = document.createElement("span"), dot = document.createElement("i");
    const result = data.results.find((r) => r.lane === lane.id);
    const accent = result && nodes.get(result.id).querySelector(".thread-mark");
    dot.style.background = accent ? accent.dataset.threadColor || accent.style.fill : "#8a9da8";
    dot.setAttribute("aria-hidden", "true");
    item.append(dot, document.createTextNode(lane.label)); legend.append(item);
  });
  document.addEventListener("litdelta:identity-change", () => {
    legend.hidden = $("color-mode").value !== "thread";
    schedule();
  });
  legend.hidden = $("color-mode").value !== "thread";
  if (typeof ResizeObserver !== "undefined") new ResizeObserver(schedule).observe(scroll);
  else window.addEventListener("resize", schedule);
  return {
    update(items, isFiltered) { matching = items; filtered = isFiltered; schedule(); },
    select(id, type, readingRoute = []) { selected = id; selectedType = type; route = readingRoute; schedule(); },
    resize: schedule,
    setZoom(value) { zoom = value; schedule(); },
    exportHtml(original) {
      const json = JSON.stringify(preference);
      return original.replace(/(<script type="application\/json" id="graph-preference">)[\s\S]*?(<\/script>)/,
        (_match, start, end) => start + json + end);
    },
  };
}
