"use strict";

// Canonical maps are validated before rendering. Imported prose remains data
// even when it travels to a Markdown reader rather than the offline HTML.
function noteText(value) {
  return String(value ?? "Not extracted")
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replace(/[\\`*_{}\[\]#!|]/g, "\\$&")
    .replace(/(^|\n)(\s*)([+\-])(?=\s)/g, "$1$2\\$3")
    .replace(/(^|\n)(\s*\d+)\.(?=\s)/g, "$1$2\\.");
}

function noteSource(url) {
  return new URL(url).href.replaceAll("(", "%28").replaceAll(")", "%29").replaceAll("&", "&amp;");
}

function noteResult(data, result, heading) {
  const work = data.works.find((item) => item.id === result.work_id),
    version = work.versions.find((item) => item.id === result.version_id);
  const lines = ["### " + heading + noteText(result.label), "",
    noteText(work.title) + " — " + work.authors.map(noteText).join(", "),
    "First published: " + noteText(work.first_published) + ". Cited version: " + noteText(version.label) + " (" + noteText(version.published) + ").",
    "[Pinned version](" + noteSource(version.url) + ")", "", noteText(result.summary)];
  Object.entries(result.settings).forEach(([name, value]) => lines.push("- " + noteText(name) + ": " + noteText(value)));
  lines.push("- Result review: " + noteText(result.review_status));
  result.reviews.forEach((review) => lines.push("- [Recorded review: " + noteText(review.name) + "](" + noteSource(review.url) + ")"));
  lines.push("");
  return lines;
}

function noteEvidence(data, ids) {
  const lines = [];
  new Set(ids).forEach((key) => {
    const item = data.evidence.find((entry) => entry.id === key),
      work = data.works.find((entry) => entry.id === item.work_id);
    lines.push("### " + noteText(key) + ": " + noteText(work.title), "",
      "- Version: " + noteText(item.version_id) + "; locator: " + noteText(item.locator) + ".",
      "- Access: " + noteText(item.kind.replaceAll("_", " ")) + "; checked: " + noteText(item.checked) + ".",
      "- Interpretation: " + noteText(item.summary),
      "- [Source](" + noteSource(item.url) + ")");
    if (item.quote) lines.push("", ...noteText(item.quote.exact).split("\n").map((line) => "> " + line), "",
      "Local text match: " + noteText(item.anchor_check?.outcome || "unchecked") + "; recorded only, not reproduced by this export.");
    lines.push("");
  });
  return lines;
}

function noteScope(data) {
  return ["## Map scope", "", noteText(data.scope.summary), "Cutoff: " + noteText(data.scope.cutoff),
    "Coverage: " + noteText(data.scope.coverage), "Search strategy: " + noteText(data.scope.search_strategy), "", "### Exclusions", "",
    ...data.scope.exclusions.map((item) => "- " + noteText(item)), "", "### Known gaps", "",
    ...data.scope.gaps.map((item) => "- " + noteText(item))];
}
