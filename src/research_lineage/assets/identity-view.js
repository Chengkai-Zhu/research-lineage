"use strict";

function createIdentityView(data, element, button) {
  const $ = (id) => document.getElementById(id);
  const works = new Map(data.works.map((work) => [work.id, work]));
  const palette = ["#0072b2", "#e69f00", "#009e73", "#cc79a7", "#d55e00", "#56b4e9", "#b59b00", "#8b70c7"];
  let preference = { mode: "thread", focus: "all" };
  try {
    const saved = JSON.parse($("color-preference").textContent);
    if (["thread", "authors", "groups"].includes(saved.mode) && typeof saved.focus === "string") preference = saved;
  } catch (_) { /* An invalid saved preference does not prevent reading a map. */ }

  function members(result) {
    const work = works.get(result.work_id);
    if (preference.mode === "authors") {
      return [...new Set(work.authors)].map((name) => ({ id: "author:" + name, label: name }));
    }
    if (preference.mode === "groups") {
      return (work.groups || []).filter((group) => group.version_id === result.version_id)
        .map((group) => ({ id: "group:" + group.id, label: group.label }));
    }
    return [];
  }

  function catalog() {
    const identities = new Map();
    data.results.forEach((result) => members(result).forEach((member) => {
      if (!identities.has(member.id)) identities.set(member.id, { ...member, works: new Set() });
      identities.get(member.id).works.add(result.work_id);
    }));
    return [...identities.values()].sort((a, b) => b.works.size - a.works.size || (a.label < b.label ? -1 : a.label > b.label ? 1 : 0));
  }

  function keys() {
    const all = catalog();
    const common = all.slice(0, palette.length).map((member, index) => ({ ...member, color: palette[index] }));
    if (preference.focus === "all") return common;
    const focused = all.find((member) => member.id === preference.focus);
    return focused ? [{ ...focused, color: common.find((member) => member.id === focused.id)?.color || palette[0] }] : [];
  }

  function svgElement(tag, attributes, text) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, String(value)));
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function paint(root) {
    const colors = new Map(keys().map((member) => [member.id, member.color]));
    data.results.forEach((result) => {
      const node = root.querySelector('[id="result-' + result.id + '"]');
      if (!node) return;
      node.querySelectorAll(".identity-mark").forEach((mark) => mark.remove());
      const accent = node.querySelectorAll("rect")[1];
      if (!accent.dataset.threadColor) accent.dataset.threadColor = accent.style.fill;
      const identities = members(result), visible = identities.filter((member) => colors.has(member.id));
      const neutral = preference.mode !== "thread" && !visible.length;
      accent.style.fill = visible.length ? colors.get(visible[0].id) : neutral ? "#a6afa9" : accent.dataset.threadColor;
      node.classList.toggle("identity-muted", preference.mode !== "thread" && preference.focus !== "all" && neutral);
      node.setAttribute("aria-label", result.label + (identities.length ? ". " + identities.map((member) => member.label).join(", ") : ""));
      visible.forEach((member, index) => {
        const mark = svgElement("g", { class: "identity-mark" });
        const rect = svgElement("rect", { x: 15 + index * 17, y: 70, width: 13, height: 4, rx: 1,
          style: "fill:" + colors.get(member.id) + ";stroke:none" });
        rect.append(svgElement("title", {}, member.label));
        mark.append(rect);
        node.append(mark);
      });
    });
  }

  function apply() {
    $("color-mode").value = preference.mode;
    const all = catalog(), focus = $("identity-focus"), legend = $("identity-legend");
    if (!all.some((member) => member.id === preference.focus)) preference.focus = "all";
    focus.replaceChildren();
    const empty = element("option", "", "All names");
    empty.value = "all";
    focus.append(empty);
    all.forEach((member) => {
      const option = element("option", "", member.label + " (" + member.works.size + (member.works.size === 1 ? " paper)" : " papers)"));
      option.value = member.id;
      focus.append(option);
    });
    focus.value = preference.focus;
    $("identity-focus-label").hidden = preference.mode === "thread" || !all.length;
    legend.hidden = preference.mode === "thread";
    legend.replaceChildren();
    if (preference.mode !== "thread") {
      legend.append(element("p", "identity-caption", all.length
        ? "Choose a name to follow its work. Multiple color marks show collaboration; gray marks have no selected label."
        : "No sourced team assignments are recorded for these result versions."));
      keys().forEach((member) => {
        const key = button(member.label, () => {
          preference.focus = member.id;
          apply();
          focus.focus();
        }, "identity-key");
        const chip = element("span", "identity-chip");
        chip.style.backgroundColor = member.color;
        chip.setAttribute("aria-hidden", "true");
        key.prepend(chip);
        key.setAttribute("aria-label", "Follow " + member.label);
        legend.append(key);
      });
      if (all.length > palette.length && preference.focus === "all") {
        legend.append(element("p", "identity-caption", "The legend colors the eight most frequent labels. Use the name selector to follow any other recorded name."));
      }
    }
    paint($("lineage-map"));
  }

  function exportSvg(root, height) {
    paint(root);
    if (preference.mode === "thread") return 0;
    const legend = keys();
    root.append(svgElement("text", { x: 30, y: height + 26, fill: "#43594d", "font-size": 12 },
      "Color by " + (preference.mode === "authors" ? "author labels" : "recorded teams") + "; multiple marks indicate collaboration."));
    legend.forEach((member, index) => {
      const y = height + 46 + index * 18;
      root.append(svgElement("rect", { x: 30, y: y - 9, width: 12, height: 6, fill: member.color }));
      root.append(svgElement("text", { x: 50, y, fill: "#43594d", "font-size": 12 }, member.label));
    });
    const metadata = svgElement("metadata", { id: "litdelta-color-preference" }, JSON.stringify(preference));
    root.append(metadata);
    return 50 + legend.length * 18;
  }

  function follow(mode, id) {
    if (!["authors", "groups"].includes(mode)) return false;
    const previous = preference;
    preference = { mode, focus: id };
    if (!catalog().some((member) => member.id === id)) {
      preference = previous;
      return false;
    }
    apply();
    return true;
  }

  $("color-mode").addEventListener("change", () => {
    preference = { mode: $("color-mode").value, focus: "all" };
    apply();
  });
  $("identity-focus").addEventListener("change", () => {
    preference.focus = $("identity-focus").value;
    apply();
  });
  apply();
  return {
    exportSvg,
    exportHtml: (original, reading) => exportViewPreferences(original, preference, reading),
    follow,
  };
}
