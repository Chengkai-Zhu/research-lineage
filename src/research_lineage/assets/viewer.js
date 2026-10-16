"use strict";
(() => {
  const data = JSON.parse(document.getElementById("map-data").textContent);
  const $ = (id) => document.getElementById(id);
  const index = (items) =>
    Object.fromEntries(items.map((item) => [item.id, item]));
  const results = index(data.results),
    works = index(data.works),
    evidence = index(data.evidence),
    relations = index(data.relations);
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
  let selected = null,
    selectedType = "result",
    routeStep = -1,
    zoom = 1;

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
  function updateHash(type, id) {
    const hash = "#" + type + "=" + encodeURIComponent(id);
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
      card.append(element("p", "", item.summary));
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
    appendReviews(panel, result);
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
          edge.comparability.replaceAll("_", " ") +
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
        () => showCompare(edge.source, edge.target),
        "relation-link",
      ),
    );
    appendReviews(panel, edge);
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
    if (!visible.length) {
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
  function showCompare(left, right) {
    const body = modal("What changed in the setting?"),
      pickers = element("div", "compare-pickers");
    ["left", "right"].forEach((side, index) => {
      const label = element(
        "label",
        "",
        index === 0 ? "EARLIER / FIRST RESULT" : "LATER / SECOND RESULT",
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
      select.addEventListener("change", updateComparison);
    });
    body.append(pickers, element("div", "", undefined));
    body.lastChild.id = "comparison-output";
    updateComparison();
  }
  function updateComparison() {
    const a = results[$("compare-left").value],
      b = results[$("compare-right").value],
      output = $("comparison-output");
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
    output.replaceChildren(
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
  function download(name, content, type) {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const anchor = element("a");
    anchor.href = url;
    anchor.download = name;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $("announcement").textContent = "Exported " + name;
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
      "0 0 1240 " + (height + 60 + lines.length * 18),
    );
    lines.forEach((line, index) => {
      const node = doc.createElementNS("http://www.w3.org/2000/svg", "text");
      node.setAttribute("x", "30");
      node.setAttribute("y", String(height + 30 + index * 18));
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
      button("Interactive HTML  ↓", () => {
        $("modal").close();
        download("map.html", originalHtml, "text/html;charset=utf-8");
      }),
      button("Editable SVG  ↓", () =>
        download("map.svg", svgExport(), "image/svg+xml"),
      ),
      button("Structured JSON  ↓", () =>
        download(
          "map.json",
          JSON.stringify(data, null, 2) + "\n",
          "application/json",
        ),
      ),
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
  $("map-category").textContent = data.id.replaceAll("-", " ").toUpperCase();
  const years = data.works.map((work) =>
    Number(work.first_published.slice(0, 4)),
  );
  [
    [data.works.length, "source papers"],
    [data.relations.length, "connections"],
    [Math.min(...years) + "–" + Math.max(...years), "publication span"],
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
    " draft results · " +
    data.evidence.filter((item) => item.kind === "abstract").length +
    " abstract-level sources · Evidence limits stay visible.";
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
  $("compare-button").addEventListener("click", () =>
    showCompare(
      selectedType === "result" ? selected : data.results[0].id,
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
  function restoreHash() {
    try {
      const [type, id] = location.hash.slice(1).split("=");
      if (type === "relation" && relations[decodeURIComponent(id)])
        showRelation(decodeURIComponent(id), false);
      else if (type === "result" && results[decodeURIComponent(id)])
        showResult(decodeURIComponent(id), false);
    } catch (_) {
      /* Invalid fragments do not prevent using the map. */
    }
  }
  showResult(
    data.results.find((result) => result.kind === "framework")?.id ||
      data.results[0].id,
    false,
  );
  restoreHash();
  filter();
  window.addEventListener("hashchange", restoreHash);
})();
