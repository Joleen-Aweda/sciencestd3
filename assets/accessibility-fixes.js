(function () {
  "use strict";

  const SHORTCUTS = {
    x: ["Main Menu", "Main menu: table of contents", "Contents", "Table of contents"],
    a: ["Accessibility menu", "Accessibility menu: settings", "Accessibility settings", "Settings"],
    l: ["Language", "Language tab", "Choose language"],
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

  function normaliseText(element) {
    return (element?.textContent || "").replace(/\s+/g, " ").trim();
  }

  let lastSpokenLabel = "";
  let lastSpokenAt = 0;
  let interfaceAudio = null;

  const INTERFACE_AUDIO = {
    "main menu: table of contents": "main-menu.mp3",
    "glossary tab": "glossary-tab.mp3",
    "language tab": "language-tab.mp3",
    "accessibility menu: settings": "accessibility-menu.mp3",
    "search the table of contents": "search-contents.mp3",
    "search the glossary": "search-glossary.mp3",
    "search languages": "search-languages.mp3",
    "on this page": "on-this-page.mp3",
    "book glossary": "book-glossary.mp3",
    "contents": "contents.mp3",
    "page list": "page-list.mp3",
    "english language": "english-language.mp3",
    "go to previous audio": "previous-audio.mp3",
    "play": "play.mp3",
    "pause": "pause.mp3",
    "go to next audio": "next-audio.mp3",
    "stop": "stop.mp3",
    "open table of contents, x": "open-contents.mp3",
    "open settings, a": "open-settings.mp3",
    "open language, l": "open-language.mp3",
    "close panel, escape": "close-panel.mp3",
  };

  function interfaceAudioFile(label) {
    const key = label.toLowerCase().replace(/\s+/g, " ").trim();
    if (INTERFACE_AUDIO[key]) return INTERFACE_AUDIO[key];
    if (key.startsWith("playback speed")) return "playback-speed.mp3";
    if (key.startsWith("volume")) return "volume.mp3";
    return null;
  }

  function speakInterfaceLabel(label) {
    if (!label) return;
    const now = Date.now();
    if (label === lastSpokenLabel && now - lastSpokenAt < 750) return;
    lastSpokenLabel = label;
    lastSpokenAt = now;
    const audioFile = interfaceAudioFile(label);
    if (audioFile) {
      interfaceAudio?.pause();
      interfaceAudio = document.createElement("audio");
      interfaceAudio.preload = "auto";
      interfaceAudio.src = `./assets/interface-audio/${audioFile}`;
      interfaceAudio.play().catch(() => {});
      return;
    }
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(label);
      utterance.lang = document.documentElement.lang || "en";
      utterance.rate = 0.92;
      window.speechSynthesis.speak(utterance);
    }
  }

  function isSpokenInterfaceControl(element) {
    if (!(element instanceof HTMLElement)) return false;
    if (element.matches('[data-adt-speak-interface="true"]')) return true;
    if (element.closest('[aria-label="Read aloud controls"]')) return true;
    if (element.matches('[role="tab"], [role="group"][data-adt-shortcut]')) return true;
    if (element.matches('[role="dialog"] input[type="text"]')) return true;
    const label = element.getAttribute("aria-label") || "";
    return /^(Main menu|Glossary tab|Language tab|Accessibility menu)/i.test(label);
  }

  function spokenName(element) {
    return element.getAttribute("aria-label")
      || element.getAttribute("title")
      || element.getAttribute("placeholder")
      || normaliseText(element);
  }

  function labelButtonByName(name, label) {
    document.querySelectorAll("button").forEach((button) => {
      const current = (button.getAttribute("aria-label") || normaliseText(button)).trim();
      if (current === name) button.setAttribute("aria-label", label);
    });
  }

  function improveGeneratedInterfaceAccessibility() {
    // Give each generated pop-up a useful accessible name.
    document.querySelectorAll('[role="dialog"]').forEach((dialog) => {
      const heading = dialog.querySelector("h1, h2, h3, h4, h5, h6");
      if (!heading) return;
      if (!heading.id) heading.id = `adt-dialog-title-${Math.random().toString(36).slice(2)}`;
      dialog.setAttribute("aria-labelledby", heading.id);
    });

    // Main reader tabs must have explicit spoken names, even when their icons
    // or visible captions change with state.
    labelButtonByName("Main Menu", "Main menu: table of contents");
    labelButtonByName("Glossary", "Glossary tab");
    labelButtonByName("Language", "Language tab");
    labelButtonByName("Accessibility menu", "Accessibility menu: settings");
    document.querySelectorAll("button").forEach((button) => {
      if (/^(Main menu|Glossary tab|Language tab|Accessibility menu)/i.test(button.getAttribute("aria-label") || "")) {
        button.setAttribute("data-adt-speak-interface", "true");
      }
    });

    // Search controls need context so a screen-reader user knows what is searched.
    document.querySelectorAll('[role="dialog"] input[type="text"]').forEach((input) => {
      const title = normaliseText(input.closest('[role="dialog"]')?.querySelector("h1, h2, h3, h4, h5, h6"));
      const label = title === "Glossary" ? "Search the glossary"
        : title === "Contents" ? "Search the table of contents"
        : "Search languages";
      input.setAttribute("aria-label", label);
    });

    // Language entries behave as selectable tabs; expose both purpose and state.
    document.querySelectorAll('[role="dialog"] button').forEach((button) => {
      const dialog = button.closest('[role="dialog"]');
      if (dialog?.querySelector('input[aria-label="Search languages"]')) {
        const language = normaliseText(button);
        if (language && !button.getAttribute("aria-label")) {
          button.setAttribute("aria-label", `${language} language`);
        }
        if (language) button.setAttribute("data-adt-speak-interface", "true");
        if (language && button.querySelector("svg")) button.setAttribute("aria-current", "true");
      }
    });

    // Read-aloud controls: retain dynamic state labels and provide safe fallbacks
    // for every native media button.
    document.querySelectorAll('[aria-label="Read aloud controls"] button').forEach((button) => {
      if (button.getAttribute("aria-label")) return;
      const title = button.getAttribute("title");
      button.setAttribute("aria-label", title || "Read aloud control");
    });

    // Announce each shortcut as one meaningful item instead of two unrelated spans.
    const shortcutsHeading = Array.from(document.querySelectorAll("h1, h2, h3, h4, h5, h6"))
      .find((heading) => normaliseText(heading) === "Keyboard shortcuts");
    if (shortcutsHeading) {
      shortcutsHeading.parentElement?.removeAttribute("role");
      shortcutsHeading.parentElement?.removeAttribute("aria-label");
      const shortcutLabels = {
        "Open table of contents": "X",
        "Open settings": "A",
        "Open language": "L",
        "Close panel": "Escape",
      };
      Object.entries(shortcutLabels).forEach(([action, key]) => {
        const label = Array.from(document.querySelectorAll('[role="dialog"] span, [role="dialog"] div, [role="dialog"] p'))
          .find((element) => normaliseText(element) === action);
        const row = label?.parentElement;
        if (!row) return;
        row.setAttribute("role", "group");
        row.setAttribute("aria-label", `${action}, ${key}`);
        row.setAttribute("data-adt-shortcut", "true");
        row.setAttribute("tabindex", "0");
        Array.from(row.children).forEach((child) => child.setAttribute("aria-hidden", "true"));
      });
    }
  }

  const accessibilityObserver = new MutationObserver(improveGeneratedInterfaceAccessibility);
  accessibilityObserver.observe(document.documentElement, { childList: true, subtree: true });
  improveGeneratedInterfaceAccessibility();

  document.addEventListener("focusin", (event) => {
    const control = event.target instanceof HTMLElement
      ? event.target.closest('button, input, [role="tab"], [role="group"][data-adt-shortcut]')
      : null;
    if (control && isSpokenInterfaceControl(control)) speakInterfaceLabel(spokenName(control));
  }, true);

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
