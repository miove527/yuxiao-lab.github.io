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

const gallery = document.querySelector('.gallery-grid');
if (gallery) {
  const filter = document.querySelector('#gallery-category');
  filter.parentElement.hidden = false;
  filter.addEventListener('change', () => {
    gallery.querySelectorAll('figure').forEach(figure => {
      figure.hidden = filter.value !== 'all' && figure.dataset.category !== filter.value;
    });
  });
  const dialog = document.querySelector('.gallery-dialog');
  const photo = dialog.querySelector('img');
  const count = dialog.querySelector('.gallery-controls span');
  let photos = [], index = 0;
  function showPhoto() {
    photo.src = photos[index].href;
    photo.alt = photos[index].dataset.alt;
    count.textContent = `${index + 1} / ${photos.length}`;
    dialog.querySelectorAll('.gallery-previous, .gallery-next').forEach(button => button.hidden = photos.length < 2);
  }
  gallery.addEventListener('click', event => {
    const button = event.target.closest('.gallery-open');
    if (!button) return;
    photos = [...button.closest('figure').querySelectorAll('.gallery-photos a')];
    index = Math.max(0, photos.findIndex(link => link.href === button.closest('figure').querySelector('img').src));
    showPhoto();
    dialog.showModal();
  });
  dialog.querySelector('.gallery-close').addEventListener('click', () => dialog.close());
  dialog.querySelector('.gallery-previous').addEventListener('click', () => { index = (index - 1 + photos.length) % photos.length; showPhoto(); });
  dialog.querySelector('.gallery-next').addEventListener('click', () => { index = (index + 1) % photos.length; showPhoto(); });
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') dialog.querySelector('.gallery-previous').click();
    if (event.key === 'ArrowRight') dialog.querySelector('.gallery-next').click();
  });
}
