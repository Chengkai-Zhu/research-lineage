"use strict";
(() => {
  const data = JSON.parse(document.getElementById("map-data").textContent);
  const $ = (id) => document.getElementById(id);
  const index = (items) =>
    Object.fromEntries(items.map((item) => [item.id, item]));
  const results = index(data.results),
    works = index(data.works),
    evidence = index(data.evidence),
    relations = index(data.relations),
    comparisons = index(data.comparisons || []);
  const labels = {
    generalizes: "generalizes",
    uses_result: "uses a result from",
    improves_bound: "improves a bound in",
    simplifies: "simplifies",
    surveys: "surveys",
    critiques: "critiques conditions in",
    refutes_claim: "refutes a claim in",
    addresses: "addresses a question in",
    independent_parallel: "develops in parallel with",
    empirically_checks: "experimentally checks",
    cites: "cites",
  };
  const settingLabels = {
    input: "Input & access",
    assumptions: "Assumptions",
    cost: "Cost model",
    error: "Error & precision",
  };
  const originalSvg = $("lineage-map").outerHTML;
  const originalHtml = "<!doctype html>\n" + document.documentElement.outerHTML;
  const readingState = readReadingPreference($("reading-preference").textContent, location.hash);
  const identityView = createIdentityView(data, element, button);
  const readingWorkspace = createReadingWorkspace({
    data, saved: $("collection-preference").textContent, element, button, link, modal,
    exportText: showTextExport,
    inspect: (id) => { $("modal").close(); resetFilters(); showResult(id); },
    announce: (text) => { $("announcement").textContent = text; },
  });
  let selected = null,
    selectedType = "result",
    routeStep = -1,
    zoom = 1,
    comparisonSelection = null,
    activeComparison = null;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function button(text, action, className = "button") {
    const node = element("button", className, text);
    node.type = "button";
    node.addEventListener("click", action);
    return node;
  }
  function link(text, url) {
    const node = element("a", "", text);
    if (/^https?:\/\//i.test(url)) {
      node.href = url;
      node.target = "_blank";
      node.rel = "noopener noreferrer";
    }
    return node;
  }
  const title = (text) => element("h3", "section-label", text);
  const unknown = (value) => (value === null ? "Not extracted" : value);
  const reviewLabel = (item) =>
    item.review_status === "proposed"
      ? "Awaiting scholarly review"
      : "Review recorded · identity not verified";
  function updateHash(type, id = null) {
    const hash = "#" + type + (id === null ? "" : "=" + encodeURIComponent(id));
    readingState.fragment = hash;
    try {
      history.replaceState(null, "", hash);
    } catch (_) {
      /* Sandboxed previews may disallow history writes. */
    }
  }
  function highlights() {
    document.querySelectorAll(".node,.relation").forEach((node) => {
      node.classList.toggle(
        "selected",
        node.dataset.id === selected &&
          node.classList.contains(
            selectedType === "result" ? "node" : "relation",
          ),
      );
      node.classList.toggle(
        "route-node",
        routeStep >= 0 && data.reading_route.includes(node.dataset.id),
      );
    });
  }
  function appendEvidence(parent, ids) {
    parent.append(title("THE EVIDENCE"));
    ids.forEach((id) => {
      const item = evidence[id],
        work = works[item.work_id];
      const card = element("div", "source-card");
      card.append(
        element(
          "div",
          "source-meta",
          item.kind.replace("_", " ").toUpperCase() + " / " + item.locator,
        ),
      );
      card.append(element("p", "source-title", work.title));
      if (item.quote) {
        card.append(
          element("p", "source-meta", "SOURCE EXCERPT"),
          element("blockquote", "source-quote", item.quote.exact),
          element("p", "source-meta", "ANNOTATION / INTERPRETATION"),
        );
      }
      card.append(element("p", "", item.summary));
      if (item.quote) card.append(element("p", "source-meta",
        item.anchor_check
          ? "Recorded local text check: " + item.anchor_check.outcome + ". Not reproduced here; a match does not establish scientific support."
          : "Local text match: unchecked. Use the locator and pinned source to check this excerpt."));
      card.append(
        element(
          "p",
          "source-meta",
          item.version_id + " · checked " + item.checked,
        ),
      );
      card.append(link("Read the pinned source ↗", item.url));
      parent.append(card);
    });
  }
  function appendReviews(parent, item) {
    if (!item.reviews.length) return;
    parent.append(title("RECORDED REVIEWS"));
    item.reviews.forEach((review) =>
      parent.append(link(review.name + " ↗", review.url)),
    );
  }
  function showMode(mode) {
    if (mode === "comparison" && !(data.comparisons || []).length) mode = "overview";
    readingState.mode = mode;
    $("story-view").hidden = mode !== "overview";
    $("explorer").hidden = mode !== "explore";
    $("comparison-view").hidden = mode !== "comparison";
    $("mode-overview").setAttribute("aria-pressed", String(mode === "overview"));
    $("mode-explore").setAttribute("aria-pressed", String(mode === "explore"));
    $("mode-comparison").setAttribute("aria-pressed", String(mode === "comparison"));
    document.body.classList.toggle("exploring", mode === "explore");
    document.body.classList.toggle("comparing", mode === "comparison");
  }
  function finishInspector() {
    const panel = $("inspector");
    let group = null;
    [...panel.children].forEach((node) => {
      if (node.classList.contains("section-label")) {
        group = element("details", "evidence-section");
        group.append(element("summary", "", node.textContent));
        node.replaceWith(group);
      } else if (node.classList.contains("paper-meta") && !group) {
        group = element("details", "evidence-section");
        group.append(element("summary", "", "PAPER & VERSION"));
        node.before(group);
        group.append(node);
      } else if (group) group.append(node);
    });
    panel.prepend(button("Close details ×", () => {
      const old = selected, type = selectedType;
      selected = null;
      panel.hidden = true;
      $("explorer").classList.remove("has-selection");
      highlights();
      updateHash("explore");
      $(type + "-" + old)?.focus();
    }, "inspector-close"));
    panel.hidden = false;
    $("explorer").classList.add("has-selection");
    showMode("explore");
  }
  function showResult(id, update = true) {
    if (!results[id]) return;
    selected = id;
    selectedType = "result";
    const result = results[id],
      work = works[result.work_id],
      panel = $("inspector");
    panel.replaceChildren(
      element("div", "eyebrow", "RESULT / " + work.first_published.slice(0, 4)),
      element("h2", "", result.label),
    );
    panel.append(
      element("span", "status", reviewLabel(result)),
      element("p", "summary", result.summary),
      readingWorkspace.resultButton(id),
    );
    panel.append(
      element(
        "p",
        "paper-meta",
        work.authors.join(" · ") + "\nFirst published " + work.first_published,
      ),
    );
    const version = work.versions.find((item) => item.id === result.version_id);
    panel.append(
      element(
        "p",
        "paper-meta",
        "Cited version: " + version.label + " · " + version.published,
      ),
    );
    appendEvidence(panel, result.evidence);
    panel.append(title("UNDER WHICH CONDITIONS?"));
    const settings = element("dl", "settings");
    Object.entries(result.settings).forEach(([key, value]) => {
      const row = element("div");
      row.append(
        element("dt", "", settingLabels[key]),
        element("dd", value === null ? "unknown" : "", unknown(value)),
      );
      settings.append(row);
    });
    panel.append(settings);
    const connected = data.relations.filter(
      (edge) => edge.source === id || edge.target === id,
    );
    if (connected.length) {
      panel.append(title("FOLLOW THE CONNECTIONS"));
      connected.forEach((edge) => {
        const node = button(
          results[edge.target].label +
            " " +
            labels[edge.type] +
            " " +
            results[edge.source].label,
          () => showRelation(edge.id),
          "relation-link",
        );
        node.append(
          element(
            "span",
            "",
            edge.basis.replaceAll("_", " ") +
              " · " +
              (edge.review_status === "proposed"
                ? "proposed"
                : "review recorded"),
          ),
        );
        panel.append(node);
      });
    }
    const relatedComparisons = (data.comparisons || []).filter((record) => record.left === id || record.right === id);
    if (relatedComparisons.length) {
      panel.append(title("WHAT CHANGES BETWEEN RESULTS?"));
      relatedComparisons.forEach((record) => panel.append(button(record.question,
        () => showCompare(record.left, record.right, record.id), "relation-link")));
    }
    const groups = (work.groups || []).filter((group) => group.version_id === result.version_id);
    if (groups.length) {
      panel.append(title("RECORDED TEAMS"));
      groups.forEach((group) => {
        panel.append(element("p", "summary", group.label));
        group.evidence.forEach((eid) => {
          const source = evidence[eid], paragraph = element("p", "source-meta");
          paragraph.append(link(source.locator + " · " + source.version_id + " ↗", source.url));
          panel.append(paragraph);
        });
      });
    }
    appendReviews(panel, result);
    finishInspector();
    highlights();
    if (update) updateHash("result", id);
  }
  function showRelation(id, update = true) {
    if (!relations[id]) return;
    selected = id;
    selectedType = "relation";
    const edge = relations[id],
      panel = $("inspector");
    panel.replaceChildren(
      element("div", "eyebrow", "RELATIONSHIP / WHY THIS CONNECTION?"),
      element("h2", "", labels[edge.type]),
    );
    panel.append(
      element("span", "status", reviewLabel(edge)),
      element(
        "p",
        "summary",
        results[edge.target].label + " " + labels[edge.type] + " " + results[edge.source].label,
      ),
      element("p", "summary", edge.summary),
    );
    panel.append(
      element(
        "p",
        "paper-meta",
        "Basis: " +
          edge.basis.replaceAll("_", " ") +
          ". Comparability: " +
          (edge.comparability ? "legacy author annotation: " + edge.comparability.replaceAll("_", " ") : "see the authored comparison, if recorded") +
          ".",
      ),
    );
    appendEvidence(panel, edge.evidence);
    panel.append(title("EXPLORE BOTH RESULTS"));
    panel.append(
      button(
        results[edge.source].label,
        () => showResult(edge.source),
        "relation-link",
      ),
      button(
        results[edge.target].label,
        () => showResult(edge.target),
        "relation-link",
      ),
    );
    panel.append(
      button(
        "Compare their settings →",
        () => showCompare(edge.source, edge.target, edge.comparison_id),
        "relation-link",
      ),
    );
    appendReviews(panel, edge);
    finishInspector();
    highlights();
    if (update) updateHash("relation", id);
  }
  function matching() {
    const query = $("search").value.trim().toLowerCase();
    return data.results.filter((result) => {
      const work = works[result.work_id];
      return (
        ($("lane-filter").value === "all" ||
          result.lane === $("lane-filter").value) &&
        ($("review-filter").value === "all" ||
          result.review_status === $("review-filter").value) &&
        (!query ||
          [result.label, result.summary, work.title, ...work.authors]
            .join(" ")
            .toLowerCase()
            .includes(query))
      );
    });
  }
  function filter() {
    const visible = matching(),
      ids = new Set(visible.map((result) => result.id));
    data.results.forEach((result) => {
      const node = $("result-" + result.id);
      const show = ids.has(result.id);
      node.classList.toggle("hidden", !show);
      node.setAttribute("tabindex", show ? "0" : "-1");
    });
    data.relations.forEach((edge) => {
      const node = $("relation-" + edge.id);
      const show = ids.has(edge.source) && ids.has(edge.target);
      node.classList.toggle("hidden", !show);
      node.setAttribute("tabindex", show ? "0" : "-1");
    });
    $("visible-count").textContent =
      visible.length + " of " + data.results.length + " results";
    $("empty").hidden = visible.length > 0;
    $("graph-scroll").hidden = visible.length === 0;
    const list = $("list-view");
    list.replaceChildren();
    [...visible]
      .sort((a, b) =>
        works[a.work_id].first_published.localeCompare(
          works[b.work_id].first_published,
        ),
      )
      .forEach((result) => {
        const row = button("", () => showResult(result.id), "result-row");
        row.append(
          element(
            "span",
            "year-number",
            works[result.work_id].first_published.slice(0, 4),
          ),
        );
        const body = element("span");
        body.append(
          element("strong", "", result.label),
          element("p", "", result.summary),
        );
        row.append(body);
        list.append(row);
      });
    if (!selected) {
      $("inspector").hidden = true;
      $("explorer").classList.remove("has-selection");
    } else if (!visible.length) {
      $("inspector").replaceChildren(
        element("div", "eyebrow", "EVIDENCE INSPECTOR"),
        element("h2", "", "No selected result"),
        element("p", "summary", "Reset filters to explore the research map."),
      );
    } else if (
      (selectedType === "result" && !ids.has(selected)) ||
      (selectedType === "relation" &&
        (!ids.has(relations[selected]?.source) ||
          !ids.has(relations[selected]?.target)))
    )
      showResult(visible[0].id);
    else if (selectedType === "result") showResult(selected, false);
    else if (selectedType === "relation") showRelation(selected, false);
    $("announcement").textContent = visible.length + " matching results.";
  }
  function resetFilters() {
    $("search").value = "";
    $("lane-filter").value = "all";
    $("review-filter").value = "all";
    filter();
  }
  function view(mode) {
    $("map-view").hidden = mode !== "map";
    $("list-view").hidden = mode !== "list";
    $("view-map").setAttribute("aria-pressed", String(mode === "map"));
    $("view-list").setAttribute("aria-pressed", String(mode === "list"));
  }
  function modal(name) {
    $("modal-title").textContent = name;
    $("modal-content").replaceChildren();
    if (!$("modal").open) $("modal").showModal();
    return $("modal-content");
  }
  function scope() {
    const body = modal("A clear view of the scope");
    body.append(
      element("p", "", data.scope.summary),
      element(
        "p",
        "",
        "Cutoff: " +
          data.scope.cutoff +
          ". The timeline shows first publication dates; content refers to the cited versions. It is not an as-of reconstruction.",
      ),
    );
    [
      ["Coverage", data.scope.coverage],
      ["Search strategy", data.scope.search_strategy],
    ].forEach(([name, text]) =>
      body.append(element("h3", "", name), element("p", "", text)),
    );
    [
      ["Excluded from this map", data.scope.exclusions],
      ["Known gaps", data.scope.gaps],
    ].forEach(([name, items]) => {
      body.append(element("h3", "", name));
      const list = element("ul");
      items.forEach((item) => list.append(element("li", "", item)));
      body.append(list);
    });
    body.append(element("h3", "", "Source index"));
    const citedVersions = new Set([
      ...data.results.map((item) => item.version_id),
      ...data.evidence.map((item) => item.version_id),
    ]);
    data.works.forEach((work) => {
      body.append(element("h4", "", work.title));
      work.versions.forEach((version) => {
        const p = element("p");
        p.append(link(version.label + " · " + version.published + " ↗", version.url));
        p.append(element("span", "", citedVersions.has(version.id)
          ? " — Cited in this map"
          : " — Recorded version; not cited"));
        body.append(p);
      });
    });
  }
  function openComparison(id, update = true) {
    const record = comparisons[id];
    if (!record) return;
    activeComparison = id;
    if ($("modal").open) $("modal").close();
    $("comparison-answer").replaceChildren();
    appendComparison($("comparison-answer"), record, true);
    $("question-picker").value = id;
    document.querySelectorAll(".question-link").forEach((node) => {
      node.setAttribute("aria-pressed", String(node.dataset.comparison === id));
    });
    showMode("comparison");
    if (update) updateHash("comparison", id);
  }
  function finishComparisonDialog() {
    if (!$("modal-content").querySelector("#compare-left") || !readingState.fragment.startsWith("#compare=")) return;
    if (readingState.mode === "comparison" && activeComparison) updateHash("comparison", activeComparison);
    else if (readingState.mode === "explore" && selected) updateHash(selectedType, selected);
    else updateHash(readingState.mode === "explore" ? "explore" : "overview");
  }
  function showCompare(left, right, comparisonId = null) {
    comparisonSelection = comparisonId;
    const body = modal("What changes between these results?"),
      pickers = element("div", "compare-pickers");
    ["left", "right"].forEach((side, index) => {
      const label = element(
        "label",
        "",
        index === 0 ? "RESULT A" : "RESULT B",
      );
      const select = element("select");
      select.id = "compare-" + side;
      select.setAttribute(
        "aria-label",
        index === 0 ? "First result" : "Second result",
      );
      data.results.forEach((result) => {
        const option = element("option", "", result.label);
        option.value = result.id;
        select.append(option);
      });
      select.value = index === 0 ? left : right;
      label.append(select);
      pickers.append(label);
      select.addEventListener("change", () => {
        comparisonSelection = null;
        updateComparison();
      });
    });
    body.append(pickers, element("div", "", undefined));
    body.lastChild.id = "comparison-output";
    updateComparison();
  }
  function updateComparison() {
    const a = results[$("compare-left").value],
      b = results[$("compare-right").value],
      output = $("comparison-output");
    output.replaceChildren();
    const choices = (data.comparisons || []).filter((record) => record.left === a.id && record.right === b.id);
    const chosen = choices.find((record) => record.id === comparisonSelection) || (choices.length === 1 ? choices[0] : null);
    if (choices.length > 1) {
      const label = element("label", "comparison-question", "Question and applicable regime"),
        picker = element("select");
      picker.id = "comparison-choice";
      const empty = element("option", "", "Choose the question to compare…");
      empty.value = "";
      picker.append(empty);
      choices.forEach((record) => {
        const option = element("option", "", record.question + " — " + record.regime);
        option.value = record.id;
        picker.append(option);
      });
      picker.value = chosen?.id || "";
      picker.addEventListener("change", () => {
        comparisonSelection = picker.value || null;
        updateComparison();
        $("comparison-choice")?.focus();
      });
      label.append(picker);
      output.append(label);
    }
    if (chosen) {
      appendComparison(output, chosen);
      return;
    }
    output.append(element("p", "comparison-note", choices.length > 1
      ? "Several questions are recorded for this pair. Choose one; no assessment has been selected."
      : "No authored assessment is recorded for this ordered pair. Comparability remains unknown."));
    const table = element("table", "compare-table"),
      head = element("tr");
    ["Setting", a.label, b.label].forEach((name) =>
      head.append(element("th", "", name)),
    );
    table.append(head);
    Object.keys(settingLabels).forEach((key) => {
      const left = a.settings[key],
        right = b.settings[key],
        row = element(
          "tr",
          left !== null && right !== null && left !== right ? "different" : "",
        );
      const heading = element("th", "", settingLabels[key]);
      heading.scope = "row";
      row.append(
        heading,
        element("td", left === null ? "unknown" : "", unknown(left)),
        element("td", right === null ? "unknown" : "", unknown(right)),
      );
      table.append(row);
    });
    output.append(
      table,
      element(
        "p",
        "comparison-note",
        "Highlighted rows have different reported settings. Text matching does not establish comparability or a performance improvement. Unknown fields stay unknown.",
      ),
    );
    const sources = element("p");
    sources.append(
      link(
        "First pinned source ↗",
        works[a.work_id].versions.find((version) => version.id === a.version_id)
          .url,
      ),
      document.createTextNode(" · "),
      link(
        "Second pinned source ↗",
        works[b.work_id].versions.find((version) => version.id === b.version_id)
          .url,
      ),
    );
    output.append(sources);
  }
  function appendComparison(output, record, inline = false) {
    const meanings = {
      comparable: "Comparable here",
      conditional: "Conditional comparison",
      incomparable: "Not a valid comparison",
      unknown: "Evidence missing",
    };
    const status = element("div", "comparison-status");
    status.append(element("span", "assessment " + record.assessment, meanings[record.assessment]),
      element("span", "", reviewLabel(record)));
    output.append(status, element(inline ? "h1" : "h3", "comparison-title", record.question));
    if (inline) {
      const pair = element("p", "comparison-pair");
      pair.append(element("span", "", results[record.left].label),
        element("span", "", "→"), element("span", "", results[record.right].label));
      output.append(pair);
    }
    output.append(element("p", "comparison-takeaway", record.summary));
    const context = element("div", "comparison-context");
    [
      ["Applies when", record.regime],
      ["Keep in mind", record.tradeoffs],
    ].forEach(([heading, content]) => {
      const row = element("div");
      row.append(element("h2", "", heading), element("p", "", content));
      context.append(row);
    });
    output.append(context);
    const details = element("details", "evidence-section");
    details.append(element("summary", "", "Conditions & sources"));
    details.append(element("p", "", record.rationale));
    appendEvidence(details, record.evidence);
    const table = element("table", "compare-table"), head = element("tr");
    ["Condition", results[record.left].label, results[record.right].label, "Why it matters"].forEach((text) => head.append(element("th", "", text)));
    table.append(head);
    record.conditions.forEach((condition) => {
      const row = element("tr");
      row.append(element("th", "", condition.dimension));
      ["left", "right"].forEach((side) => {
        const unit = condition[side + "_unit"];
        row.append(element("td", "", unknown(condition[side]) + (unit ? " [" + unit + "]" : "")));
      });
      row.append(element("td", "", condition.reason));
      table.append(row);
    });
    const wrap = element("div", "comparison-table-wrap");
    wrap.tabIndex = 0;
    wrap.setAttribute("role", "region");
    wrap.setAttribute("aria-label", "Full comparison conditions; scroll horizontally");
    wrap.append(table);
    details.append(element("p", "table-hint", "Swipe or scroll sideways for all columns →"), wrap,
      element("p", "source-meta", "Basis: " + record.basis.replaceAll("_", " ") + ". This is an authored assessment; source matching and structural checks do not certify it."));
    if (record.conversion) details.append(element("p", "", "Conversion: " + record.conversion.summary + " Assumptions: " + record.conversion.assumptions));
    if (record.improvement) details.append(element("p", "", "Specific improvement claim: " + record.improvement));
    details.append(element("p", "source-meta", "Authored outcome: " + record.outcome.replaceAll("_", " ")));
    appendReviews(details, record);
    output.append(details);
    const permalink = element("a", "inline-button comparison-permalink", inline ? "Link to this question ↗" : "Read this question →");
    permalink.href = "#comparison=" + encodeURIComponent(record.id);
    if (!inline) permalink.addEventListener("click", (event) => {
      event.preventDefault();
      openComparison(record.id);
    });
    output.append(permalink);
  }
  function reading(step) {
    routeStep = Math.max(0, Math.min(step, data.reading_route.length - 1));
    resetFilters();
    view("map");
    $("route-bar").hidden = false;
    $("route-progress").textContent =
      "READING ROUTE · " + (routeStep + 1) + " / " + data.reading_route.length;
    $("route-prev").disabled = routeStep === 0;
    $("route-next").disabled = routeStep === data.reading_route.length - 1;
    showResult(data.reading_route[routeStep]);
    $("result-" + selected)?.scrollIntoView({
      block: "nearest",
      inline: "nearest",
      behavior: "instant",
    });
  }
  function downloadLink(label, name, content, type) {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const anchor = element("a", "button", label);
    anchor.href = url;
    anchor.download = name;
    anchor.addEventListener("click", () => {
      $("announcement").textContent = "Download requested: " + name;
    });
    $("modal").addEventListener("close", () => {
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }, {once:true});
    return anchor;
  }
  function saveExplanation() {
    if (!activeComparison) return;
    showTextExport("Take this explanation to your notes", comparisonBrief(data, activeComparison),
      "Comparison note in Markdown", "comparison-" + activeComparison + ".md",
      "The selected question, conditions and sources travel together. Review status and map gaps stay in the note.");
  }
  function showTextExport(name, note, label, filename, description) {
    const body = modal(name),
      preview = element("textarea", "brief-preview"),
      status = element("p", "source-meta");
    preview.readOnly = true;
    preview.value = note;
    preview.setAttribute("aria-label", label);
    status.setAttribute("role", "status");
    body.append(element("p", "", description));
    const actions = element("div", "brief-actions");
    actions.append(button(filename.endsWith(".md") ? "Copy Markdown" : "Copy request", async () => {
      try {
        await navigator.clipboard.writeText(note);
        status.textContent = "Copied. Paste it into your notes or research agent.";
      } catch (_) {
        preview.focus();
        preview.select();
        status.textContent = "Note selected. Copy it with Ctrl+C or ⌘C.";
      }
    }, "button primary"), downloadLink(filename.endsWith(".md") ? "Markdown ↓" : "Request ↓", filename, note, "text/plain;charset=utf-8"));
    body.append(actions, status, preview);
    return body;
  }
  function svgExport() {
    const doc = new DOMParser().parseFromString(originalSvg, "image/svg+xml"),
      root = doc.documentElement;
    const box = root.getAttribute("viewBox").split(" ").map(Number),
      height = box[3];
    const raw = JSON.parse($("export-notes").textContent);
    const metadata = doc.createElementNS("http://www.w3.org/2000/svg", "metadata");
    metadata.id = "research-lineage-data";
    metadata.textContent = JSON.stringify(data);
    root.append(metadata);
    const identityHeight = identityView.exportSvg(root, height);
    const lines = raw.flatMap((text) => {
      const words = text.split(" "),
        rows = [""];
      words.forEach((word) => {
        if ((rows[rows.length - 1] + word).length > 145) rows.push("");
        rows[rows.length - 1] += (rows[rows.length - 1] ? " " : "") + word;
      });
      return rows;
    });
    root.setAttribute(
      "viewBox",
      "0 0 1240 " + (height + identityHeight + 60 + lines.length * 18),
    );
    lines.forEach((line, index) => {
      const node = doc.createElementNS("http://www.w3.org/2000/svg", "text");
      node.setAttribute("x", "30");
      node.setAttribute("y", String(height + identityHeight + 30 + index * 18));
      node.setAttribute("fill", "#43594d");
      node.setAttribute("font-size", "12");
      node.textContent = line;
      root.append(node);
    });
    return new XMLSerializer().serializeToString(doc);
  }
  function exportMenu() {
    const body = modal("Take the whole story with you");
    body.append(
      element(
        "p",
        "",
        "The full map is exported, including hidden results, evidence, source versions, review status, and known gaps.",
      ),
    );
    const grid = element("div", "download-grid");
    grid.append(
      downloadLink("Interactive HTML  ↓", "map.html", identityView.exportHtml(originalHtml, {
        mode: readingState.mode,
        view: $("list-view").hidden ? "map" : "list",
        fragment: readingState.fragment,
      }, readingWorkspace.ids()), "text/html;charset=utf-8"),
      downloadLink("Editable SVG  ↓", "map.svg", svgExport(), "image/svg+xml"),
      downloadLink("Structured JSON  ↓", "map.json", JSON.stringify(data, null, 2) + "\n", "application/json"),
    );
    body.append(
      grid,
      element(
        "p",
        "",
        "HTML works offline. Open source links only when you choose to check a paper.",
      ),
    );
  }

  $("question").textContent = data.question;
  $("overview-summary").textContent = data.narrative?.overview || "";
  $("overview-summary").hidden = !data.narrative;
  $("overview-context").hidden = !data.narrative;
  document.body.classList.toggle("has-narrative", Boolean(data.narrative));
  $("route-caption").textContent = data.reading_route.length
    ? data.reading_route.length + " steps · a suggested path through the ideas"
    : "No reading route recorded · explore the map instead";
  $("mode-overview").addEventListener("click", () => {
    showMode("overview");
    updateHash("overview");
  });
  $("mode-explore").addEventListener("click", () => {
    showMode("explore");
    updateHash("explore");
  });
  document.querySelectorAll(".story-source").forEach((node) => {
    node.addEventListener("click", () => {
      resetFilters();
      showResult(node.dataset.result);
      $("explorer").scrollIntoView({block:"start", behavior:"instant"});
    });
  });
  document.querySelectorAll(".comparison-open").forEach((node) => node.addEventListener("click", () => {
    openComparison(node.dataset.comparison);
    $("comparison-view").scrollIntoView({block: "start", behavior: "instant"});
  }));
  $("all-comparisons")?.addEventListener("click", () => {
    const body = modal("Choose a comparison question");
    (data.comparisons || []).forEach((record) => body.append(button(record.question,
      () => { $("modal").close(); openComparison(record.id); }, "relation-link")));
  });
  const records = data.comparisons || [];
  $("mode-comparison").hidden = records.length === 0;
  records.forEach((record, index) => {
    const choice = button(record.question, () => openComparison(record.id), "question-link");
    choice.dataset.comparison = record.id;
    choice.prepend(element("span", "question-number", String(index + 1).padStart(2, "0")));
    $("question-links").append(choice);
    const option = element("option", "", record.question);
    option.value = record.id;
    $("question-picker").append(option);
  });
  $("question-picker").addEventListener("change", () => openComparison($("question-picker").value));
  $("mode-comparison").addEventListener("click", () => openComparison(activeComparison || records[0]?.id));
  $("change-pair").addEventListener("click", () => {
    const record = comparisons[activeComparison];
    if (record) showCompare(record.left, record.right, record.id);
  });
  $("save-explanation").addEventListener("click", saveExplanation);
  $("collect-comparison").addEventListener("click", () => {
    const record = comparisons[activeComparison];
    if (record) { readingWorkspace.add([record.left, record.right]); readingWorkspace.open(); }
  });
  $("comparison-map").addEventListener("click", () => {
    const record = comparisons[activeComparison];
    if (record) { resetFilters(); showResult(record.right); }
  });
  $("map-category").textContent = data.id.replaceAll("-", " ").toUpperCase();
  const years = data.works.map((work) =>
    Number(work.first_published.slice(0, 4)),
  );
  [
    [data.works.length, data.works.length === 1 ? "source paper" : "source papers"],
    [data.relations.length, data.relations.length === 1 ? "connection" : "connections"],
    [Math.min(...years) === Math.max(...years) ? String(years[0]) : Math.min(...years) + "–" + Math.max(...years), "publication span"],
  ].forEach(([number, label]) => {
    const item = element("div", "stat");
    item.append(
      element("strong", "", String(number)),
      element("span", "", label),
    );
    $("stats").append(item);
  });
  $("coverage-short").textContent =
    data.results.filter((result) => result.review_status === "proposed")
      .length +
    " results awaiting review · " +
    data.evidence.filter((item) => item.kind === "abstract").length +
    " abstract-level sources";
  $("cutoff-label").textContent = "SCOPE CUTOFF / " + data.scope.cutoff;
  data.lanes.forEach((lane) => {
    const option = element("option", "", lane.label);
    option.value = lane.id;
    $("lane-filter").append(option);
  });
  $("lineage-map").addEventListener("click", (event) => {
    const target = event.target.closest(".node,.relation");
    if (target)
      target.classList.contains("node")
        ? showResult(target.dataset.id)
        : showRelation(target.dataset.id);
  });
  $("lineage-map").addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      const target = event.target.closest(".node,.relation");
      if (target) {
        event.preventDefault();
        target.classList.contains("node")
          ? showResult(target.dataset.id)
          : showRelation(target.dataset.id);
      }
    }
  });
  $("search").addEventListener("input", filter);
  $("lane-filter").addEventListener("change", filter);
  $("review-filter").addEventListener("change", filter);
  $("clear-filters").addEventListener("click", resetFilters);
  $("empty-reset").addEventListener("click", resetFilters);
  $("view-map").addEventListener("click", () => view("map"));
  $("view-list").addEventListener("click", () => view("list"));
  $("scope-button").addEventListener("click", scope);
  $("coverage-link").addEventListener("click", scope);
  $("modal-close").addEventListener("click", () => $("modal").close());
  $("modal").addEventListener("close", finishComparisonDialog);
  $("compare-button").addEventListener("click", () =>
    showCompare(
      selectedType === "result" && selected ? selected : data.results[0].id,
      data.results.find((result) => result.id !== selected)?.id ||
        data.results[0].id,
    ),
  );
  $("route-start").disabled = data.reading_route.length === 0;
  $("route-start").addEventListener("click", () => reading(0));
  $("route-prev").addEventListener("click", () => reading(routeStep - 1));
  $("route-next").addEventListener("click", () => reading(routeStep + 1));
  $("route-exit").addEventListener("click", () => {
    routeStep = -1;
    $("route-bar").hidden = true;
    highlights();
  });
  $("export-button").addEventListener("click", exportMenu);
  function setZoom(value) {
    zoom = Math.max(1, Math.min(2.5, value));
    $("lineage-map").style.width = zoom * 100 + "%";
  }
  $("zoom-in").addEventListener("click", () => setZoom(zoom + 0.25));
  $("zoom-out").addEventListener("click", () => setZoom(zoom - 0.25));
  $("zoom-fit").addEventListener("click", () => setZoom(1));
  function restoreHash(fragment = location.hash) {
    try {
      readingState.fragment = fragment;
      const [type, id] = fragment.slice(1).split("=");
      if (type === "relation" && relations[decodeURIComponent(id)])
        showRelation(decodeURIComponent(id), false);
      else if (type === "result" && results[decodeURIComponent(id)])
        showResult(decodeURIComponent(id), false);
      else if (type === "comparison" && comparisons[decodeURIComponent(id)]) {
        openComparison(decodeURIComponent(id), false);
      } else if (type === "compare") {
        const [left, right] = decodeURIComponent(id).split(",");
        if (results[left] && results[right]) showCompare(left, right);
      }
      else if (type === "author" || type === "team") {
        const mode = type === "author" ? "authors" : "groups",
          key = (type === "author" ? "author:" : "group:") + decodeURIComponent(id);
        if (identityView.follow(mode, key)) showMode("explore");
        else $("announcement").textContent = "No recorded " + type + " matches this link.";
      }
      else if (type === "explore") showMode("explore");
      else if (type === "overview") showMode("overview");
    } catch (_) {
      /* Invalid fragments do not prevent using the map. */
    }
  }
  showMode(readingState.mode);
  view(readingState.view);
  if (!readingState.fragment && records.length) openComparison(records[0].id, false);
  restoreHash(readingState.fragment);
  filter();
  window.addEventListener("hashchange", () => restoreHash());
})();
