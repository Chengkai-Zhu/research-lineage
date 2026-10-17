"use strict";

// The reader receives a map validated by the canonical Python build. This
// formatter copies its authored records; it does not infer a comparison.
function comparisonBrief(data, id) {
  const record = (data.comparisons || []).find((item) => item.id === id);
  if (!record) throw new Error("Choose an authored comparison before saving an explanation.");
  const escape = noteText;
  const index = (items) => Object.fromEntries(items.map((item) => [item.id, item]));
  const results = index(data.results);
  const source = noteSource;
  const lines = ["# " + escape(record.question), "", escape(record.summary), "",
    "- **Applies when:** " + escape(record.regime),
    "- **Keep in mind:** " + escape(record.tradeoffs),
    "- **Authored assessment:** " + escape(record.assessment) + "; outcome: " + escape(record.outcome.replaceAll("_", " ")),
    "- **Review:** " + (record.review_status === "proposed" ? "Awaiting scholarly review" : "Review recorded; identity not verified"),
    "- **Basis:** " + escape(record.basis.replaceAll("_", " ")), "", "## Compared results", ""];
  [record.left, record.right].forEach((key, position) => {
    lines.push(...noteResult(data, results[key], (position ? "B" : "A") + ": "));
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
  lines.push(...noteEvidence(data, refs), ...noteScope(data));
  if (record.reviews.length) lines.push("", "## Recorded reviews", "", ...record.reviews.map((item) => "- [" + escape(item.name) + "](" + source(item.url) + ")"));
  lines.push("", "---", "Selected explanation from [LitDelta](https://chengkaizhu.site/litdelta/) map " + escape(data.id) + ", comparison " + escape(record.id) + ".",
    "This is an authored explanation, not an independent scientific review. Source matching and structural checks do not certify its claims.",
    "Keep the full map for the complete research record. Filters do not change this note's conditions or evidence.", "");
  return lines.join("\n");
}
