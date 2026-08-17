(() => {
  "use strict";

  const PLAYER_ID = "science-sign-language-player";
  const SIGN_BUTTON_LABEL = "Sign language";
  let videoMappingsPromise = null;

  // Keep the bundled mutually-exclusive media player off. This page-level
  // player is used instead so sign language and narration can run together.
  try {
    localStorage.setItem("signLanguageMode", "false");
  } catch (_) {
    // Storage can be unavailable in private or embedded browsing contexts.
  }

  function currentPageNumber() {
    const value = document.querySelector('meta[name="page-section-id"]')?.content;
    const pageNumber = Number.parseInt(value || "", 10);
    return Number.isFinite(pageNumber) ? pageNumber : null;
  }

  function currentLanguage() {
    return document.documentElement.lang || "en";
  }

  function loadVideoMappings() {
    if (!videoMappingsPromise) {
      const version = new URL(document.currentScript?.src || location.href).searchParams.get("v") || "";
      const suffix = version ? `?v=${encodeURIComponent(version)}` : "";
      videoMappingsPromise = fetch(`./content/i18n/${currentLanguage()}/videos.json${suffix}`)
        .then((response) => {
          if (!response.ok) throw new Error(`Could not load sign-language mappings (${response.status})`);
          return response.json();
        });
    }
    return videoMappingsPromise;
  }

  function setButtonState(pressed) {
    document.querySelectorAll(`button[aria-label="${SIGN_BUTTON_LABEL}"]`).forEach((button) => {
      button.setAttribute("aria-pressed", String(pressed));
    });
  }

  function closePlayer() {
    document.getElementById(PLAYER_ID)?.remove();
    setButtonState(false);
  }

  function startNarrationIfNeeded() {
    if (document.querySelector('button[aria-label="Pause"]')) return;

    const playButton = document.querySelector('button[aria-label="Play"]');
    if (playButton) {
      playButton.click();
      return;
    }

    const enabledButton = document.querySelector('button[aria-label="Deactivate text to speech"]');
    const disabledButton = document.querySelector('button[aria-label="Activate text to speech"]');
    if (enabledButton) enabledButton.click();

    window.setTimeout(() => {
      const activateButton = document.querySelector('button[aria-label="Activate text to speech"]');
      if (activateButton) activateButton.click();
      window.setTimeout(() => {
        document.querySelector('button[aria-label="Play"]')?.click();
      }, 100);
    }, disabledButton ? 0 : 100);
  }

  function createPlayer(videoUrl, pageNumber) {
    const container = document.createElement("aside");
    container.id = PLAYER_ID;
    container.setAttribute("aria-label", `Sign language for page ${pageNumber}`);
    Object.assign(container.style, {
      position: "fixed",
      right: "1rem",
      bottom: "5rem",
      zIndex: "49",
      width: "min(24rem, calc(100vw - 2rem))",
      overflow: "hidden",
      borderRadius: "0.75rem",
      background: "#000",
      boxShadow: "0 12px 34px rgba(0,0,0,.38)",
    });

    const header = document.createElement("div");
    Object.assign(header.style, {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      minHeight: "2.25rem",
      padding: "0.35rem 0.5rem 0.35rem 0.75rem",
      color: "#fff",
      background: "rgba(0,0,0,.92)",
      font: "600 0.9rem/1.2 system-ui, sans-serif",
    });
    header.textContent = `Sign language — page ${pageNumber}`;

    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.setAttribute("aria-label", "Close sign language video");
    closeButton.textContent = "×";
    Object.assign(closeButton.style, {
      width: "2rem",
      height: "2rem",
      border: "0",
      borderRadius: "0.4rem",
      color: "#fff",
      background: "transparent",
      cursor: "pointer",
      font: "700 1.5rem/1 system-ui, sans-serif",
    });
    closeButton.addEventListener("click", closePlayer);
    header.appendChild(closeButton);

    const video = document.createElement("video");
    video.src = videoUrl;
    video.controls = true;
    video.autoplay = true;
    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;
    video.setAttribute("muted", "");
    video.setAttribute("aria-label", `Sign language video for page ${pageNumber}`);
    Object.assign(video.style, {
      display: "block",
      width: "100%",
      height: "auto",
      maxHeight: "min(62vh, 30rem)",
      background: "#000",
    });
    video.addEventListener("loadedmetadata", () => {
      video.play().catch(() => {});
      startNarrationIfNeeded();
    }, { once: true });

    container.append(header, video);
    document.body.appendChild(container);
    return container;
  }

  async function togglePlayer() {
    if (document.getElementById(PLAYER_ID)) {
      closePlayer();
      return;
    }

    // The play control may be inside a popover that closes after this click,
    // so start narration before waiting for the video mapping or metadata.
    startNarrationIfNeeded();

    const pageNumber = currentPageNumber();
    if (!pageNumber) return;
    const mappings = await loadVideoMappings();
    const filename = mappings[`video-${pageNumber}`];
    if (!filename) return;

    const videoUrl = `./content/i18n/${currentLanguage()}/video/${encodeURIComponent(filename)}`;
    createPlayer(videoUrl, pageNumber);
    setButtonState(true);
  }

  document.addEventListener("click", (event) => {
    const button = event.target instanceof Element
      ? event.target.closest(`button[aria-label="${SIGN_BUTTON_LABEL}"]`)
      : null;
    if (!button) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    togglePlayer().catch((error) => console.error("[sign-language]", error));
  }, true);
})();
