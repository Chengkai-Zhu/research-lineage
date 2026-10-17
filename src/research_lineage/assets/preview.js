"use strict";
(() => {
  const button = document.getElementById("copy-prompt"),
    seed = document.getElementById("seed-input"),
    goal = document.getElementById("request-goal"),
    preview = document.getElementById("request-preview"),
    prompt = document.getElementById("research-prompt"),
    status = document.getElementById("copy-status");
  function update() {
    status.textContent = "";
    try {
      prompt.value = researchRequest(seed.value, goal.value);
      button.disabled = false;
    } catch (error) {
      prompt.value = "";
      button.disabled = true;
      if (seed.value.trim()) status.textContent = error.message;
    }
  }
  seed.addEventListener("input", update);
  goal.addEventListener("change", update);
  update();
  button.addEventListener("click", async () => {
    const requested = prompt.value;
    if (!requested) return;
    try {
      await navigator.clipboard.writeText(requested);
      status.textContent = prompt.value === requested
        ? "Copied. Paste it into your research agent."
        : "Previous request copied. Copy again to use your edited input.";
    } catch (_) {
      if (prompt.value !== requested) return;
      preview.open = true;
      prompt.focus();
      prompt.select();
      status.textContent = "Request selected. Copy it with Ctrl+C or ⌘C.";
    }
  });
})();
