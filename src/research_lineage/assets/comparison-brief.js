"use strict";

// The reader receives a map validated by the canonical Python build. This
// formatter copies its authored records; it does not infer a comparison.
function comparisonBrief(data, id) {
  const record = (data.comparisons || []).find((item) => item.id === id);
  if (!record) throw new Error("Choose an authored comparison before saving an explanation.");
  const escape = (value) => String(value ?? "Not extracted")
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replace(/[\\`*_{}\[\]#!|]/g, "\\$&")
    .replace(/(^|\n)(\s*)([+\-])(?=\s)/g, "$1$2\\$3")
    .replace(/(^|\n)(\s*\d+)\.(?=\s)/g, "$1$2\\.");
  const index = (items) => Object.fromEntries(items.map((item) => [item.id, item]));
  const results = index(data.results), works = index(data.works), evidence = index(data.evidence);
  const source = (url) => new URL(url).href.replaceAll("(", "%28").replaceAll(")", "%29").replaceAll("&", "&amp;");
  const lines = ["# " + escape(record.question), "", escape(record.summary), "",
    "- **Applies when:** " + escape(record.regime),
    "- **Keep in mind:** " + escape(record.tradeoffs),
    "- **Authored assessment:** " + escape(record.assessment) + "; outcome: " + escape(record.outcome.replaceAll("_", " ")),
    "- **Review:** " + (record.review_status === "proposed" ? "Awaiting scholarly review" : "Review recorded; identity not verified"),
    "- **Basis:** " + escape(record.basis.replaceAll("_", " ")), "", "## Compared results", ""];
  [record.left, record.right].forEach((key, position) => {
    const result = results[key], work = works[result.work_id], version = work.versions.find((item) => item.id === result.version_id);
    lines.push("### " + (position ? "B" : "A") + ": " + escape(result.label), "",
      escape(work.title) + " — " + work.authors.map(escape).join(", "),
      "First published: " + escape(work.first_published) + ". Cited version: " + escape(version.label) + " (" + escape(version.published) + ").",
      "[Pinned version](" + source(version.url) + ")", "");
    lines.push(escape(result.summary));
    Object.entries(result.settings).forEach(([name, value]) => lines.push("- " + escape(name) + ": " + escape(value)));
    lines.push("- Result review: " + escape(result.review_status));
    result.reviews.forEach((review) => lines.push("- [Recorded review: " + escape(review.name) + "](" + source(review.url) + ")"));
    lines.push("");
  });
  lines.push("## Conditions", "");
  record.conditions.forEach((row) => {
    lines.push("- **" + escape(row.dimension) + ":** A: " + escape(row.left) + (row.left_unit ? " [" + escape(row.left_unit) + "]" : "") +
      "; B: " + escape(row.right) + (row.right_unit ? " [" + escape(row.right_unit) + "]" : "") + ". " + escape(row.reason) +
      " Evidence A: " + row.left_evidence.map(escape).join(", ") + "; B: " + row.right_evidence.map(escape).join(", ") + ".");
  });
  lines.push("", "## Reasoning and limits", "", escape(record.rationale));
  if (record.improvement) lines.push("", "Specific improvement: " + escape(record.improvement));
  if (record.conversion) lines.push("", "Conversion: " + escape(record.conversion.summary), "Assumptions: " + escape(record.conversion.assumptions));
  lines.push("", "## Sources", "");
  const refs = new Set([...record.evidence, ...results[record.left].evidence, ...results[record.right].evidence]);
  refs.forEach((key) => {
    const item = evidence[key];
    lines.push("### " + escape(key) + ": " + escape(works[item.work_id].title), "",
      "- Version: " + escape(item.version_id) + "; locator: " + escape(item.locator) + ".",
      "- Access: " + escape(item.kind.replaceAll("_", " ")) + "; checked: " + escape(item.checked) + ".",
      "- Interpretation: " + escape(item.summary),
      "- [Source](" + source(item.url) + ")");
    if (item.quote) {
      lines.push("", ...escape(item.quote.exact).split("\n").map((line) => "> " + line), "",
        "Local text match: " + escape(item.anchor_check?.outcome || "unchecked") + "; recorded only, not reproduced by this export.");
    }
    lines.push("");
  });
  lines.push("## Map scope", "", escape(data.scope.summary), "Cutoff: " + escape(data.scope.cutoff),
    "Coverage: " + escape(data.scope.coverage), "Search strategy: " + escape(data.scope.search_strategy), "", "### Exclusions", "",
    ...data.scope.exclusions.map((item) => "- " + escape(item)), "", "### Known gaps", "",
    ...data.scope.gaps.map((item) => "- " + escape(item)));
  if (record.reviews.length) lines.push("", "## Recorded reviews", "", ...record.reviews.map((item) => "- [" + escape(item.name) + "](" + source(item.url) + ")"));
  lines.push("", "---", "Selected explanation from [LitDelta](https://chengkaizhu.site/litdelta/) map " + escape(data.id) + ", comparison " + escape(record.id) + ".",
    "This is an authored explanation, not an independent scientific review. Source matching and structural checks do not certify its claims.",
    "Keep the full map for the complete research record. Filters do not change this note's conditions or evidence.", "");
  return lines.join("\n");
}
