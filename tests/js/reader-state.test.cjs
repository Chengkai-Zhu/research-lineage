"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const test = require("node:test");
const context = vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(__dirname, "../../src/research_lineage/assets/view-state.js"), "utf8"), context);
const read = (text) => JSON.parse(JSON.stringify(context.readReadingPreference(text)));
const slot = (name, value) => '<script type="application/json" id="' + name + '">' + JSON.stringify(value) + "</script>";
const extract = (html, name) => JSON.parse(html.match(new RegExp('<script type="application/json" id="' + name + '">([\\s\\S]*?)<\\/script>'))[1]);

test("saved context preserves the selected question and full canonical data", () => {
  const data = { results: ["a", "b", "c"], comparisons: ["depth", "cost", "quality"], exclusions: ["unavailable full text"] };
  const original = slot("map-data", data) + slot("color-preference", {}) + slot("reading-preference", {});
  const colors = { mode: "authors", focus: "author:Yoshua Bengio" };
  const reading = { mode: "explore", view: "list", fragment: "#comparison=c-quality" };
  const saved = context.exportViewPreferences(original, colors, reading);
  assert.deepEqual(extract(saved, "map-data"), data);
  assert.deepEqual(extract(saved, "color-preference"), colors);
  assert.deepEqual(read(JSON.stringify(extract(saved, "reading-preference"))), reading);
  const updated = context.exportViewPreferences(saved, { mode: "groups", focus: "group:team" }, { mode: "overview", view: "map", fragment: "#overview" });
  assert.deepEqual(extract(updated, "map-data"), data);
  assert.equal(extract(updated, "color-preference").focus, "group:team");
  assert.equal(extract(updated, "reading-preference").fragment, "#overview");
  assert.equal((updated.match(/id="reading-preference"/g) || []).length, 1);
});

test("comparison reading mode survives repeated saves and explicit map links still win", () => {
  const original = slot("map-data", { results: ["a", "b"], exclusions: ["access gap"] }) + slot("color-preference", {}) + slot("reading-preference", {});
  const preference = { mode: "comparison", view: "map", fragment: "#comparison=c-quality" };
  const first = context.exportViewPreferences(original, { mode: "authors", focus: "all" }, preference);
  const restored = context.readReadingPreference(JSON.stringify(extract(first, "reading-preference")), "");
  assert.deepEqual(JSON.parse(JSON.stringify(restored)), preference);
  const second = context.exportViewPreferences(first, { mode: "authors", focus: "all" }, restored);
  assert.deepEqual(extract(second, "reading-preference"), preference);
  assert.deepEqual(extract(second, "map-data"), { results: ["a", "b"], exclusions: ["access gap"] });
  const explicit = context.readReadingPreference(JSON.stringify(preference), "#result=r-attention");
  assert.equal(explicit.fragment, "#result=r-attention");
});

test("copying the research prompt reports success or selects it when clipboard access is denied", async () => {
  const source = fs.readFileSync(path.join(__dirname, "../../src/research_lineage/assets/preview.js"), "utf8");
  for (const denied of [false, true]) {
    let action;
    const copied = [], selected = [];
    const nodes = {
      "copy-prompt": { hidden: true, addEventListener(_type, handler) { action = handler; } },
      "research-prompt": { value: "Use research-lineage with my paper.", focus() { selected.push("focus"); }, select() { selected.push("select"); } },
      "copy-status": {},
    };
    vm.runInNewContext(source, {
      document: { getElementById(id) { return nodes[id]; } },
      navigator: { clipboard: { async writeText(text) {
        if (denied) throw new Error("Clipboard permission denied");
        copied.push(text);
      } } },
    });
    assert.equal(nodes["copy-prompt"].hidden, false);
    await action();
    assert.deepEqual(copied, denied ? [] : ["Use research-lineage with my paper."]);
    assert.deepEqual(selected, denied ? ["focus", "select"] : []);
    assert.match(nodes["copy-status"].textContent, denied ? /selected.*Ctrl\+C/ : /Copied.*research agent/);
  }
});

test("imported labels and fragments cannot close a preference script", () => {
  const hostile = '</script><img src=x onerror="globalThis.INJECTED=true">&';
  const original = slot("color-preference", {}) + slot("reading-preference", {});
  const saved = context.exportViewPreferences(original, { mode: "authors", focus: hostile }, { fragment: "#" + hostile });
  assert.equal((saved.match(/<\/script>/g) || []).length, 2);
  assert.ok(!saved.includes("<img"));
  assert.equal(extract(saved, "color-preference").focus, hostile);
  assert.equal(extract(saved, "reading-preference").fragment, "#" + hostile);
});

test("an entry link cannot override the subsequently chosen identity focus", () => {
  const original = slot("color-preference", {}) + slot("reading-preference", {});
  const reading = { mode: "explore", view: "map", fragment: "#author=Yoshua%20Bengio" };
  const chosen = { mode: "groups", focus: "group:chosen-team" };
  const saved = context.exportViewPreferences(original, chosen, reading);
  assert.deepEqual(extract(saved, "color-preference"), chosen);
  assert.equal(extract(saved, "reading-preference").fragment, "#explore");
  assert.equal(reading.fragment, "#author=Yoshua%20Bengio");
  const team = context.exportViewPreferences(original, { mode: "authors", focus: "author:Chosen name" },
    { mode: "explore", view: "list", fragment: "#team:invalid" });
  assert.equal(extract(team, "reading-preference").fragment, "#team:invalid");
  const selected = context.exportViewPreferences(original, { mode: "authors", focus: "author:Chosen name" },
    { mode: "explore", view: "list", fragment: "#team=entry-team" });
  assert.equal(extract(selected, "color-preference").focus, "author:Chosen name");
  assert.equal(extract(selected, "reading-preference").fragment, "#explore");
});

test("malformed saved state falls back without losing the reader", () => {
  const fallback = { mode: "overview", view: "map", fragment: "" };
  for (const raw of ["null", "[]", "true", '"text"', "{", '{"mode":"invalid","view":"grid","fragment":17}']) {
    assert.deepEqual(read(raw), fallback);
  }
  assert.equal(read(JSON.stringify({ fragment: "#" + "x".repeat(2048) })).fragment, "");
  assert.equal(read(JSON.stringify({ fragment: "javascript:alert(1)" })).fragment, "");
  assert.deepEqual(read('{"mode":"explore","view":"list","fragment":"#author=Ada%20Lovelace"}'),
    { mode: "explore", view: "list", fragment: "#author=Ada%20Lovelace" });
});

test("a restored location survives another save with an empty browser fragment", () => {
  const original = slot("color-preference", {}) + slot("reading-preference", {});
  const colors = { mode: "thread", focus: "all" };
  const first = context.exportViewPreferences(original, colors,
    { mode: "overview", view: "map", fragment: "#comparison=c-quality" });
  const restored = context.readReadingPreference(JSON.stringify(extract(first, "reading-preference")), "");
  const second = context.exportViewPreferences(original, colors, restored);
  assert.equal(extract(second, "reading-preference").fragment, "#comparison=c-quality");
  const explicit = context.readReadingPreference(JSON.stringify(restored), "#result=r-attention");
  assert.equal(explicit.fragment, "#result=r-attention");
  const explore = context.exportViewPreferences(original, colors,
    { mode: "explore", view: "map", fragment: "#explore" });
  assert.equal(extract(explore, "reading-preference").mode, "explore");
  assert.equal(extract(explore, "reading-preference").fragment, "#explore");
});

test("closing the production inspector clears its saved result even when history is restricted", () => {
  const source = fs.readFileSync(path.join(__dirname, "../../src/research_lineage/assets/viewer.js"), "utf8");
  const helper = source.match(/function updateHash\(type[\s\S]*?\n  }/)[0];
  const handler = source.match(/panel\.prepend\(button\("Close details ×", \(\) => \{([\s\S]*?)\n    \}, "inspector-close"\)\);/)[1];
  for (const restricted of [false, true]) {
    const focused = [], removed = [];
    const state = {
      selected: "r-attention", selectedType: "result",
      panel: { hidden: false }, readingState: { fragment: "#result=r-attention" },
      highlights() {},
      history: { replaceState(_a, _b, hash) {
        if (restricted) throw new Error("History writes are restricted");
        state.url = hash;
      } },
      $(id) { return { classList: { remove(name) { removed.push(name); } },
        focus() { focused.push(id); } }; },
    };
    vm.runInNewContext(helper + "\n" + handler, state);
    assert.equal(state.panel.hidden, true);
    assert.equal(state.selected, null);
    assert.equal(state.readingState.fragment, "#explore");
    assert.deepEqual(focused, ["result-r-attention"]);
    assert.deepEqual(removed, ["has-selection"]);
    assert.equal(state.url, restricted ? undefined : "#explore");
  }
});

test("dismissing the advanced comparison preserves the visible result or relation and saved location", () => {
  const source = fs.readFileSync(path.join(__dirname, "../../src/research_lineage/assets/viewer.js"), "utf8");
  const helper = source.match(/function updateHash\(type[\s\S]*?\n  }/)[0];
  const close = source.match(/function finishComparisonDialog\(\)[\s\S]*?\n  }/)[0];
  const cases = [
    ["explore", "result", "r-attention", "#result=r-attention", "#result=r-attention"],
    ["explore", "relation", "rel-depth", "#relation=rel-depth", "#relation=rel-depth"],
    ["explore", "result", "r-attention", "#compare=r-a%2Cr-b", "#result=r-attention"],
    ["overview", "result", null, "#compare=r-a%2Cr-b", "#overview"],
    ["comparison", "result", null, "#compare=r-a%2Cr-b", "#comparison=c-quality"],
  ];
  for (const [mode, selectedType, selected, fragment, expected] of cases) {
    for (const restricted of [false, true]) {
      const state = {
        selected, selectedType, activeComparison: "c-quality", readingState: { mode, fragment },
        $(id) { assert.equal(id, "modal-content"); return { querySelector() { return {}; } }; },
        history: { replaceState() { if (restricted) throw new Error("History denied"); } },
      };
      vm.runInNewContext(helper + "\n" + close + "\nfinishComparisonDialog();", state);
      assert.equal(state.selected, selected);
      assert.equal(state.readingState.fragment, expected);
      const original = slot("color-preference", {}) + slot("reading-preference", {});
      const saved = context.exportViewPreferences(original, {}, state.readingState);
      assert.equal(extract(saved, "reading-preference").fragment, expected);
    }
  }
});
