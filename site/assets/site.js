const toggle = document.querySelector('.nav-toggle');
const navigation = document.querySelector('.site-nav');
const mobile = window.matchMedia('(max-width: 900px)');

function setNavigation(open) {
  toggle.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('open', open);
  navigation.inert = mobile.matches && !open;
}
toggle.addEventListener('click', () => setNavigation(toggle.getAttribute('aria-expanded') !== 'true'));
mobile.addEventListener('change', () => setNavigation(false));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
    setNavigation(false);
    toggle.focus();
  }
});
setNavigation(false);

const publications = document.querySelector('.publication-list');
if (publications) {
  document.querySelector('.view-controls').hidden = false;
  const original = Array.from(publications.children);
  const controls = Object.fromEntries(['view', 'sort', 'status', 'year'].map(key => [key, document.querySelector('#publication-' + key)]));

  function applySelections() {
    publications.classList.toggle('card-view', controls.view.value === 'cards');
    const items = [...original];
    if (controls.sort.value === 'date') {
      items.sort((a, b) => b.dataset.published.localeCompare(a.dataset.published));
    }
    items.forEach(item => {
      item.hidden = (controls.status.value !== 'all' && item.dataset.status !== controls.status.value) || (controls.year.value !== 'all' && item.dataset.year !== controls.year.value);
    });
    publications.append(...items);
  }

  function restoreSelections() {
    const params = new URLSearchParams(location.hash.slice(1));
    Object.entries(controls).forEach(([key, select]) => {
      select.value = params.get(key) || select.options[0].value;
      if (select.selectedIndex === -1) select.selectedIndex = 0;
    });
    applySelections();
  }

  Object.values(controls).forEach(select => select.addEventListener('change', () => {
    applySelections();
    const params = new URLSearchParams();
    Object.entries(controls).forEach(([key, control]) => {
      if (control.selectedIndex !== 0) params.set(key, control.value);
    });
    const url = new URL(location.href);
    url.hash = params.toString();
    history.replaceState(null, '', url);
  }));
  window.addEventListener('hashchange', restoreSelections);
  window.addEventListener('pageshow', restoreSelections);
  restoreSelections();
}
