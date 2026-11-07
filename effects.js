"use strict";

// Effets locaux et facultatifs. Le contenu est visible avant l'exécution du script.
(() => {
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
  const elements = [...document.querySelectorAll("[data-reveal]")];
  const played = new WeakSet();
  const running = new Set();
  let observer;

  function reveal(element, delay = 0) {
    if (preference.matches || played.has(element) || !element.animate) return;
    played.add(element);
    const effect = element.animate([
      { opacity: 0.55, transform: "translateY(14px)" },
      { opacity: 1, transform: "translateY(0)" }
    ], { duration: 560, delay, easing: "cubic-bezier(.2,.7,.2,1)", fill: "backwards" });
    running.add(effect);
    effect.onfinish = () => running.delete(effect);
    effect.oncancel = () => running.delete(effect);
  }

  function observe() {
    if (observer) observer.disconnect();
    if (preference.matches) {
      running.forEach(effect => effect.cancel());
      return;
    }
    if (!("IntersectionObserver" in window)) return;
    observer = new IntersectionObserver(entries => {
      let delay = 0;
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        reveal(entry.target, delay);
        delay = Math.min(delay + 80, 160);
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    elements.forEach(element => {
      if (!played.has(element)) observer.observe(element);
    });
  }

  // Le focus clavier n'attend jamais une animation, notamment sur les liens.
  document.addEventListener("focusin", event => {
    running.forEach(effect => {
      const target = effect.effect && effect.effect.target;
      if (target && target.contains(event.target)) effect.cancel();
    });
  });
  if (preference.addEventListener) preference.addEventListener("change", observe);
  observe();

  document.querySelectorAll("details").forEach(detail => {
    detail.addEventListener("toggle", () => {
      const content = detail.querySelector("p");
      if (!detail.open || !content || preference.matches || !content.animate) return;
      const effect = content.animate([{ opacity: 0.45 }, { opacity: 1 }], { duration: 180 });
      running.add(effect);
      effect.onfinish = () => running.delete(effect);
      effect.oncancel = () => running.delete(effect);
    });
  });
})();
