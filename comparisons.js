"use strict";

// Amélioration facultative : toutes les cartes et leurs liens sont dans le HTML.
(() => {
  const tools = document.querySelector("[data-comparison-tools]");
  const search = document.getElementById("comparison-search");
  const count = document.getElementById("comparison-count");
  const empty = document.getElementById("comparison-empty");
  const cards = [...document.querySelectorAll("[data-comparison]")];
  if (!tools || !search || !count || !empty || !cards.length) return;
  const buttons = [...tools.querySelectorAll("[data-category-filter]")];
  const normalize = value => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("fr").trim();
  const text = new Map(cards.map(card => [card, normalize(card.textContent)]));
  let category = "all";

  function update() {
    const query = normalize(search.value);
    let total = 0;
    cards.forEach(card => {
      const match = (category === "all" || card.dataset.category === category) && text.get(card).includes(query);
      card.hidden = !match;
      if (match) total += 1;
    });
    count.textContent = `${total} comparatif${total > 1 ? "s" : ""} disponible${total > 1 ? "s" : ""}.`;
    empty.hidden = total !== 0;
  }

  buttons.forEach(button => button.addEventListener("click", () => {
    category = button.dataset.categoryFilter;
    buttons.forEach(other => other.setAttribute("aria-pressed", String(other === button)));
    update();
  }));
  search.addEventListener("input", update);
  tools.hidden = false;
})();
