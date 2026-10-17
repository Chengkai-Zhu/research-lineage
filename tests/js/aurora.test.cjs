"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const root = path.join(__dirname, "../..");
const context = vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(root, "src/research_lineage/assets/aurora-graph.js"), "utf8"), context);
const data = JSON.parse(fs.readFileSync(path.join(root, "docs/test-reports/surface-code-rerun/map.json"), "utf8"));
const works = Object.fromEntries(data.works.map((work) => [work.id, work]));
const plain = (value) => JSON.parse(JSON.stringify(value));

test("focus comes from authored reading guidance and never drops small maps", () => {
  const before = JSON.stringify(data);
  const focus = plain(context.auroraFocus(data));
  assert.equal(focus.length, 12);
  assert.equal(new Set(focus).size, 12);
  assert.ok(data.reading_route.every((id) => focus.includes(id)));
  const authored = new Set([...data.reading_route, ...data.narrative.turning_points.flatMap((point) => point.result_ids)]);
  assert.ok(focus.every((id) => authored.has(id)));
  assert.equal(JSON.stringify(data), before);
  const noGuidance = { results: [{ id: "a" }, { id: "b" }, { id: "c" }] };
  assert.deepEqual(plain(context.auroraFocus(noGuidance)), ["a", "b", "c"]);
  assert.deepEqual(plain(context.auroraFocus({ ...noGuidance, reading_route: ["stale", "b", "b", "a"] })), ["b", "a"]);
});

for (const width of [280, 390, 640, 900, 1280]) {
  test(`the full 54-result map fits ${width}px without overlapping cards`, () => {
    const before = JSON.stringify(data);
    const layout = context.auroraLayout(data.results, works, width);
    const boxes = Object.entries(layout.positions);
    assert.equal(boxes.length, 54);
    for (const [index, [id, a]] of boxes.entries()) {
      assert.ok(a.x >= 0 && a.x + a.width <= width, id);
      assert.ok(a.y > 0 && a.y + a.height < layout.height, id);
      assert.ok(a.width >= 160, "card remains readable");
      for (const [, b] of boxes.slice(index + 1)) {
        assert.ok(a.x + a.width <= b.x || b.x + b.width <= a.x || a.y + a.height <= b.y || b.y + b.height <= a.y, id);
      }
    }
    const byPosition = boxes.sort(([, a], [, b]) => a.x - b.x || a.y - b.y).map(([id]) => works[data.results.find((r) => r.id === id).work_id].first_published);
    assert.deepEqual(byPosition, [...byPosition].sort());
    assert.equal(JSON.stringify(data), before);
    assert.deepEqual(plain(context.auroraLayout([...data.results].reverse(), works, width)), plain(layout));
  });
}

test("empty and single-paper layouts remain finite and do not merge results", () => {
  assert.deepEqual(plain(context.auroraLayout([], works, 390)).positions, {});
  const items = [{ id: "one", work_id: "w" }, { id: "two", work_id: "w" }, { id: "three", work_id: "w" }];
  const layout = context.auroraLayout(items, { w: { first_published: "2024-01-01" } }, 640);
  assert.equal(Object.keys(layout.positions).length, 3);
  assert.ok(layout.periods.every((p) => p.label === "2024"));
  for (const [a, b] of [[items[0], items[1]], [items[1], items[0]]]) {
    const connection = context.auroraConnection(layout.positions[a.id], layout.positions[b.id]);
    assert.ok(!/NaN|undefined|Infinity/.test(connection));
    assert.match(connection, /^M\d/);
  }
});

test("malformed graph preferences recover safely with no executable values", () => {
  for (const value of ["null", "[]", "{", '{"theme":"<script>","density":"missing"}']) {
    assert.deepEqual(plain(context.readGraphPreference(value)), { theme: "dark", density: "focus" });
  }
  assert.deepEqual(plain(context.readGraphPreference('{"theme":"light","density":"all"}')), { theme: "light", density: "all" });
});

test("measured label wrapping preserves word boundaries and limits long CJK titles", () => {
  // Width units isolate line-breaking behavior; real SVG glyphs are checked in the browser.
  let glyphWidth = () => 1;
  const part = (_tag, _attrs, text) => ({ textContent: text,
    getComputedTextLength() { return [...this.textContent].reduce((sum, char) => sum + glyphWidth(char), 0); } });
  const node = { children: [], replaceChildren() { this.children = []; }, append(child) { this.children.push(child); } };
  const wrap = (text, width) => {
    context.auroraWrap(node, text, width, part);
    return node.children.map((row) => row.textContent.trim());
  };
  assert.deepEqual(wrap("Quantum signal processing", 18), ["Quantum signal", "processing"]);
  assert.deepEqual(wrap("Singular value transformation", 18), ["Singular value", "transformation"]);
  assert.deepEqual(wrap("alpha beta", 5), ["alpha", "beta"]);
  assert.deepEqual(wrap("abcdefghijk", 4), ["abcd", "efgh", "ijk"]);
  assert.deepEqual(wrap("量子纠错的条件需要保留完整来源", 4), ["量子纠错", "的条件需", "要保留…"]);
  const full = "An extraordinarilylongtoken followed by more words";
  const rows = wrap(full, 12);
  assert.equal(rows.length, 3);
  assert.ok(rows.every((row) => row.length <= 12));
  assert.ok(rows.at(-1).endsWith("…"));
  glyphWidth = (char) => char === "W" ? 2 : char === "i" ? .8 : 1;
  assert.deepEqual(wrap("W i", 2.9), ["W", "i"]);
});


// This zero-width fixture exercises controller state and events without pretending
// to implement SVG font measurement or browser layout.
function controllerFixture(mode = "thread") {
  function node() {
    return {
      style: {}, dataset: {}, attributes: {}, children: [], listeners: {},
      classList: { toggle() {} }, clientWidth: 0, textContent: "", value: "", hidden: false,
      setAttribute(name, value) { this.attributes[name] = String(value); },
      addEventListener(type, listener) { (this.listeners[type] ||= []).push(listener); },
      emit(type) { (this.listeners[type] || []).forEach((listener) => listener({ type })); },
      append(...children) { children.forEach((child) => { child.parent = this; this.children.push(child); }); },
      prepend(child) { child.parent = this; this.children.unshift(child); },
      replaceChildren(...children) { this.children = []; this.append(...children); },
      remove() { this.parent.children = this.parent.children.filter((child) => child !== this); },
      querySelectorAll(selector) { return this.children.filter((child) => child.attributes?.class === selector.slice(1)); },
    };
  }
  const ids = Object.fromEntries([
    "lineage-map", "graph-scroll", "graph-preference", "graph-focus", "graph-all",
    "graph-theme", "graph-count", "graph-caption", "thread-legend", "color-mode",
    "color-preference", "identity-focus", "identity-focus-label", "identity-legend",
  ].map((id) => [id, node()]));
  const map = {
    works: [
      { id: "w1", authors: ["Ada"], groups: [{ id: "g1", label: "Team A", version_id: "v1" }] },
      { id: "w2", authors: ["Bo"], groups: [{ id: "g2", label: "Team B", version_id: "v2" }] },
      { id: "w3", authors: ["Chen"], groups: [] },
    ],
    results: [1, 2, 3].map((i) => ({ id: "r" + i, work_id: "w" + i, version_id: "v" + i, lane: "lane" + i, label: "Result " + i })),
    lanes: [1, 2, 3].map((i) => ({ id: "lane" + i, label: "Thread " + i })),
    reading_route: ["r1", "r2"], relations: [],
  };
  const threadColors = ["#40ad9c", "#6e9edb", "#c89d52"];
  const accents = threadColors.map((color, index) => {
    const accent = node();
    accent.style.fill = color;
    ids["result-r" + (index + 1)] = node();
    ids["result-r" + (index + 1)].querySelector = (selector) => selector === ".thread-mark" ? accent : null;
    return accent;
  });
  ids["lineage-map"].querySelector = (selector) => ids[selector.match(/^\[id="(.*)"\]$/)?.[1]];
  ids["graph-preference"].textContent = '{"density":"focus","theme":"dark"}';
  ids["color-preference"].textContent = JSON.stringify({ mode, focus: "all" });
  const events = {}, frames = [];
  const document = {
    body: node(), getElementById: (id) => ids[id], createElement: node,
    createElementNS: node, createTextNode: (text) => ({ textContent: text }),
    addEventListener(type, listener) { (events[type] ||= []).push(listener); },
    dispatchEvent(event) { (events[event.type] || []).forEach((listener) => listener(event)); },
  };
  const sandbox = vm.createContext({
    document, Event: class { constructor(type) { this.type = type; } },
    ResizeObserver: class { observe() {} },
    requestAnimationFrame(callback) { frames.push(callback); return frames.length; },
  });
  for (const filename of ["identity-view.js", "aurora-graph.js"]) {
    vm.runInContext(fs.readFileSync(path.join(root, "src/research_lineage/assets", filename), "utf8"), sandbox);
  }
  const element = (_tag, className, text) => Object.assign(node(), { className, textContent: text });
  const button = (text, action, className) => {
    const result = element("button", className, text);
    result.addEventListener("click", action);
    return result;
  };
  sandbox.createIdentityView(map, element, button);
  const graph = sandbox.createAuroraGraph(map);
  return { ids, map, accents, threadColors, graph, flush() { while (frames.length) frames.shift()(); } };
}

for (const mode of ["authors", "groups"]) {
  test(`reopened ${mode} colors retain a correct thread legend when switching back`, () => {
    const { ids, accents, threadColors, flush } = controllerFixture(mode);
    const legendColors = () => ids["thread-legend"].children.map((item) => item.children[0].style.background);
    assert.equal(ids["thread-legend"].hidden, true);
    assert.notDeepEqual(accents.map((accent) => accent.style.fill), threadColors);
    if (mode === "groups") assert.equal(accents[2].style.fill, "#a6afa9", "an unassigned result starts neutral");
    assert.deepEqual(legendColors(), threadColors);
    ids["color-mode"].value = "thread";
    ids["color-mode"].emit("change");
    flush();
    assert.equal(ids["thread-legend"].hidden, false);
    assert.deepEqual(accents.map((accent) => accent.style.fill), threadColors);
    assert.deepEqual(legendColors(), threadColors);
  });
}

test("hidden no-match graphs update the count and recover focus controls on reset", () => {
  const { ids, graph, map, flush } = controllerFixture();
  graph.update(map.results, false);
  flush();
  assert.equal(ids["graph-count"].textContent, "2 of 3 results");
  graph.update([], true);
  flush();
  assert.equal(ids["graph-count"].textContent, "0 of 3 results");
  assert.equal(ids["graph-focus"].disabled, true);
  assert.equal(ids["graph-all"].disabled, true);
  assert.equal(ids["graph-all"].attributes["aria-pressed"], "true");
  graph.update(map.results, false);
  flush();
  assert.equal(ids["graph-count"].textContent, "2 of 3 results");
  assert.equal(ids["graph-focus"].disabled, false);
  assert.equal(ids["graph-all"].disabled, false);
  assert.equal(ids["graph-focus"].attributes["aria-pressed"], "true");
});
