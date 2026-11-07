"use strict";

// Détection locale uniquement : aucun appel réseau, aucune donnée enregistrée.
(() => {
  const ua = navigator.userAgent;
  const android = /Android/i.test(ua);
  const apple = /iPhone|iPad|iPod/i.test(ua) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  const card = document.getElementById(android ? "android" : "iphone");
  if ((android || apple) && card) {
    card.classList.add("recommended");
    card.parentElement.prepend(card);
    const hint = document.getElementById("device-hint");
    if (hint) hint.textContent = android
      ? "Votre parcours : Android."
      : "Votre parcours : iPhone / iPad.";
  }

  const button = document.getElementById("share-button");
  const field = document.getElementById("share-url");
  const status = document.getElementById("share-status");
  if (!button || !field || !status) return;
  button.hidden = false;
  button.addEventListener("click", async () => {
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(field.value);
      status.textContent = "Lien copié ! Vous pouvez le coller dans WhatsApp ou un message.";
    } catch {
      field.focus();
      field.select();
      status.textContent = "Le lien est sélectionné : copiez-le puis collez-le dans votre message.";
    }
  });
})();
