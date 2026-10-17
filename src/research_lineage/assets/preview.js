"use strict";
(() => {
  const button = document.getElementById("copy-prompt"),
    prompt = document.getElementById("research-prompt"),
    status = document.getElementById("copy-status");
  button.hidden = false;
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(prompt.value);
      status.textContent = "Copied. Paste it into your research agent.";
    } catch (_) {
      prompt.focus();
      prompt.select();
      status.textContent = "Prompt selected. Copy it with Ctrl+C or ⌘C.";
    }
  });
})();
