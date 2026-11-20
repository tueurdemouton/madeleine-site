"use strict";

// Sans JavaScript, les trois captures et leurs légendes restent consultables.
(() => {
  const tabs = document.querySelector("[data-tour-tabs]");
  const panels = [...document.querySelectorAll("[data-tour-panel]")];
  if (!tabs || !panels.length) return;
  const buttons = [...tabs.querySelectorAll("button")];

  function select(button, moveFocus = false) {
    buttons.forEach(item => {
      const selected = item === button;
      item.setAttribute("aria-selected", String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    panels.forEach(panel => { panel.hidden = panel.id !== button.getAttribute("aria-controls"); });
    if (moveFocus) button.focus();
  }

  buttons.forEach((button, index) => {
    button.addEventListener("click", () => select(button));
    button.addEventListener("keydown", event => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % buttons.length;
      if (event.key === "ArrowLeft") next = (index + buttons.length - 1) % buttons.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = buttons.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      select(buttons[next], true);
    });
  });
  panels.forEach(panel => {
    panel.setAttribute("role", "tabpanel");
    panel.setAttribute("aria-labelledby", `tab-${panel.dataset.tourPanel}`);
    panel.tabIndex = 0;
  });
  tabs.hidden = false;
  select(buttons[0]);
})();
