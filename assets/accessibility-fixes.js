(function () {
  "use strict";

  const SHORTCUTS = {
    x: ["Main Menu", "Contents", "Table of contents"],
    a: ["Accessibility menu", "Accessibility settings", "Settings"],
    l: ["Language", "Choose language"],
  };

  function isVisible(element) {
    if (!(element instanceof HTMLElement)) return false;
    if (element.hidden || element.getAttribute("aria-hidden") === "true") return false;
    return !element.closest('[hidden], [inert], [aria-hidden="true"]');
  }

  function findVisibleButton(labels) {
    return Array.from(document.querySelectorAll("button")).find((button) => {
      const label = (button.getAttribute("aria-label") || button.textContent || "")
        .replace(/\s+/g, " ")
        .trim();
      return isVisible(button) && labels.some((candidate) => label === candidate);
    });
  }

  function activate(labels) {
    const button = findVisibleButton(labels);
    if (!button || button.disabled) return false;
    button.click();
    return true;
  }

  function closeOpenPanel() {
    const closeButton = Array.from(document.querySelectorAll("button")).find((button) => {
      const label = (button.getAttribute("aria-label") || "").trim();
      return isVisible(button) && /^close\b/i.test(label);
    });
    if (!closeButton) return false;
    closeButton.click();
    return true;
  }

  document.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape") {
        if (closeOpenPanel()) {
          event.preventDefault();
          event.stopImmediatePropagation();
        }
        return;
      }

      if (!event.altKey || !event.shiftKey || event.ctrlKey || event.metaKey) return;
      const labels = SHORTCUTS[event.key.toLowerCase()];
      if (!labels || !activate(labels)) return;
      event.preventDefault();
      event.stopImmediatePropagation();
    },
    true
  );

})();
