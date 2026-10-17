"use strict";

function createReadingWorkspace({ data, saved, element, button, link, modal, exportText, inspect, announce }) {
  const collection = createReadingCollection(data, saved),
    results = Object.fromEntries(data.results.map((item) => [item.id, item])),
    works = Object.fromEntries(data.works.map((item) => [item.id, item]));

  function update() {
    document.getElementById("reading-count").textContent = String(collection.ids().length);
    document.querySelectorAll("[data-reading-result]").forEach((node) => {
      const added = collection.has(node.dataset.readingResult);
      node.textContent = added ? "Added to My reading ✓" : "Add to My reading +";
      node.setAttribute("aria-pressed", String(added));
    });
  }
  function add(ids) {
    collection.add(ids);
    update();
    announce(collection.ids().length + " results in My reading. The complete map is unchanged.");
  }
  function resultButton(id) {
    const node = button(collection.has(id) ? "Added to My reading ✓" : "Add to My reading +", () => {
      if (collection.has(id)) { collection.remove(id); update(); announce("Removed from My reading."); }
      else add([id]);
    }, "button reading-toggle");
    node.dataset.readingResult = id;
    node.setAttribute("aria-pressed", String(collection.has(id)));
    return node;
  }
  function exportSelection(request = false) {
    const text = request ? readingCheckRequest(data, collection.ids()) : readingNote(data, collection.ids());
    const body = exportText(request ? "Check the evidence with your agent" : "Take your reading into your notes", text,
      request ? "Evidence check request" : "Research note in Markdown",
      request ? "evidence-check-request.txt" : "reading-notes.md",
      request ? "Copy this request to your research agent. The browser does not run research or resolve these tasks."
        : "Your reading order, conditions, exact sources and unfinished checks travel together.");
    body.prepend(button("← Back to My reading", () => open(), "text-button"));
  }
  function open(focusId = null, action = null) {
    const body = modal("My reading"), ids = collection.ids();
    body.append(element("p", "reading-intro", ids.length
      ? ids.length + " selected result" + (ids.length === 1 ? "" : "s") + " · your order, with sources and conditions."
      : "Keep the results you want to understand next."));
    if (!ids.length) {
      body.append(element("p", "", "Open a result and choose Add to My reading, or begin with the map's suggested route."));
      if (data.reading_route.length) body.append(button("Add suggested route", () => { add(data.reading_route); open(); }, "button primary"));
      body.append(element("p", "source-meta", "Nothing is selected. Research notes and check requests become available after you add a result."));
    } else {
      const actions = element("div", "brief-actions reading-actions");
      actions.append(button("Export research note", () => exportSelection(), "button primary"),
        button("Prepare evidence check", () => exportSelection(true)));
      body.append(actions);
      const list = element("ol", "reading-collection");
      ids.forEach((id, index) => {
        const result = results[id], work = works[result.work_id], row = element("li", "reading-item");
        const heading = button(result.label, () => inspect(id), "reading-item-title");
        row.append(heading, element("p", "reading-citation", work.title + " · " + work.first_published.slice(0, 4)));
        const controls = element("div", "reading-item-controls");
        [ ["Move up", -1, index === 0], ["Move down", 1, index === ids.length - 1] ].forEach(([label, step, disabled]) => {
          const control = button(label, () => { collection.move(id, step); open(id, label); announce("Reading order updated."); }, "text-button");
          control.disabled = disabled;
          control.setAttribute("aria-label", label + ": " + result.label);
          controls.append(control);
        });
        const remove = button("Remove", () => {
          collection.remove(id); update(); open(collection.ids()[Math.min(index, collection.ids().length - 1)], "Remove");
          announce("Removed from My reading. The complete map is unchanged.");
        }, "text-button");
        remove.setAttribute("aria-label", "Remove: " + result.label);
        controls.append(remove);
        row.append(controls);
        list.append(row);
        if (id === focusId) queueMicrotask(() => {
          const target = [...controls.children].find((node) => node.textContent === action && !node.disabled);
          (target || heading).focus();
        });
      });
      body.append(list);
      appendChecks(body, ids);
    }
    body.append(element("p", "source-meta reading-privacy", "Kept in this tab. Export the complete HTML to carry your selection with the map; reloading this page discards unsaved changes. No automatic storage or uploads."));
  }
  function appendChecks(body, ids) {
    const tasks = readingChecks(data, ids), details = element("details", "evidence-section reading-checks");
    details.append(element("summary", "", "Check next · " + tasks.length + " recorded follow-ups"),
      element("p", "source-meta", "These tasks identify recorded limits, not certified open scientific problems. Exporting or reading them does not resolve them or change scholarly review status."));
    const list = element("ul", "reading-check-list");
    tasks.forEach((task) => {
      const row = element("li");
      row.append(element("strong", "", task.label), element("p", "", task.detail));
      task.evidence.forEach((id) => {
        const source = data.evidence.find((item) => item.id === id), paragraph = element("p", "source-meta");
        paragraph.append(link(id + " · " + source.version_id + " · " + source.locator + " ↗", source.url));
        row.append(paragraph);
      });
      list.append(row);
    });
    details.append(list);
    body.append(details, element("p", "source-meta", "Review status stays with each result in the exported note. A recorded review does not verify reviewer identity."));
  }
  document.getElementById("reading-button").addEventListener("click", () => open());
  update();
  return { ids: collection.ids, add, resultButton, open };
}
