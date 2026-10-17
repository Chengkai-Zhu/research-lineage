"use strict";

function readReadingPreference(text) {
  let saved = {};
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) saved = parsed;
  } catch (_) { /* A malformed saved preference leaves the reader usable. */ }
  return {
    mode: saved.mode === "explore" ? "explore" : "overview",
    view: saved.view === "list" ? "list" : "map",
    fragment: typeof saved.fragment === "string" && saved.fragment.startsWith("#") && saved.fragment.length <= 2048
      ? saved.fragment : "",
  };
}

function exportViewPreferences(original, colors, reading) {
  for (const [id, value] of [["color-preference", colors], ["reading-preference", reading]]) {
    const serialized = JSON.stringify(value).replaceAll("<", "\\u003c").replaceAll(">", "\\u003e").replaceAll("&", "\\u0026");
    const selector = new RegExp('(<script type="application/json" id="' + id + '">)[\\s\\S]*?(<\\/script>)');
    original = original.replace(selector, (_whole, start, end) => start + serialized + end);
  }
  return original;
}
