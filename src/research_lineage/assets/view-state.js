"use strict";

function readReadingPreference(text, urlFragment = "") {
  let saved = {};
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) saved = parsed;
  } catch (_) { /* A malformed saved preference leaves the reader usable. */ }
  return {
    mode: saved.mode === "explore" ? "explore" : "overview",
    view: saved.view === "list" ? "list" : "map",
    fragment: urlFragment || (typeof saved.fragment === "string" && saved.fragment.startsWith("#") && saved.fragment.length <= 2048
      ? saved.fragment : ""),
  };
}

function exportViewPreferences(original, colors, reading) {
  // The color preference owns a saved author/team focus. Replaying the entry
  // link would override a different name or mode chosen after opening that link.
  if (/^#(?:author|team)=/.test(reading.fragment)) reading = { ...reading, fragment: "#explore" };
  for (const [id, value] of [["color-preference", colors], ["reading-preference", reading]]) {
    const serialized = JSON.stringify(value).replaceAll("<", "\\u003c").replaceAll(">", "\\u003e").replaceAll("&", "\\u0026");
    const selector = new RegExp('(<script type="application/json" id="' + id + '">)[\\s\\S]*?(<\\/script>)');
    original = original.replace(selector, (_whole, start, end) => start + serialized + end);
  }
  return original;
}
