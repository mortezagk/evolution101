// Sidebar: one chapter open at a time; the current page's chapter opens on load.
document.addEventListener('DOMContentLoaded', function () {
  var groups = Array.prototype.slice.call(document.querySelectorAll('#sidebar .category-group'));
  if (!groups.length) {
    return;
  }

  function setGroupState(group, open) {
    var list = group.querySelector('.category-articles');
    var button = group.querySelector('.category-toggle');
    group.classList.toggle('is-open', open);
    if (list) {
      list.classList.toggle('is-collapsed', !open);
    }
    if (button) {
      button.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
  }

  function closeOthers(except) {
    groups.forEach(function (group) {
      if (group !== except) {
        setGroupState(group, false);
      }
    });
  }

  groups.forEach(function (group) {
    setGroupState(group, group.classList.contains('is-open'));
  });

  groups.forEach(function (group) {
    var button = group.querySelector('.category-toggle');
    if (!button) {
      return;
    }

    button.addEventListener('click', function (event) {
      event.preventDefault();
      var isOpen = group.classList.contains('is-open');
      if (isOpen) {
        setGroupState(group, false);
      } else {
        closeOthers(group);
        setGroupState(group, true);
      }
    });
  });

  var currentSlug = document.body.dataset.categorySlug;
  if (currentSlug) {
    var activeGroup = null;
    groups.forEach(function (group) {
      if (!activeGroup && group.dataset.categorySlug === currentSlug) {
        activeGroup = group;
      }
    });
    if (activeGroup) {
      closeOthers(activeGroup);
      setGroupState(activeGroup, true);
    }
  }
});

// Dark mode: the button overrides the system setting via data-theme on <html>
// and remembers it; base.html applies a saved choice before first paint.
document.addEventListener('DOMContentLoaded', function () {
  var button = document.getElementById('theme-toggle');
  if (!button) {
    return;
  }

  var root = document.documentElement;
  var icon = button.querySelector('i');
  var label = button.querySelector('.visually-hidden');
  var systemDark = window.matchMedia('(prefers-color-scheme: dark)');

  function isDark() {
    var chosen = root.getAttribute('data-theme');
    return chosen ? chosen === 'dark' : systemDark.matches;
  }

  function render() {
    var dark = isDark();
    // The button shows the theme you'd switch to.
    var text = dark ? 'حالت روشن' : 'حالت تیره';
    button.setAttribute('aria-pressed', dark ? 'true' : 'false');
    button.setAttribute('title', text);
    if (label) {
      label.textContent = text;
    }
    if (icon) {
      icon.classList.toggle('fa-moon', !dark);
      icon.classList.toggle('fa-sun', dark);
    }
  }

  button.addEventListener('click', function () {
    var next = isDark() ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    // Bootstrap's own components (form controls, buttons) read this one.
    root.setAttribute('data-bs-theme', next);
    try {
      localStorage.setItem('theme', next);
    } catch (e) { /* private mode: the choice lasts for this page only */ }
    render();
  });

  // Follow the system setting while the reader has not chosen one here.
  if (systemDark.addEventListener) {
    systemDark.addEventListener('change', function (event) {
      if (!root.getAttribute('data-theme')) {
        root.setAttribute('data-bs-theme', event.matches ? 'dark' : 'light');
        render();
      }
    });
  }

  if (!root.getAttribute('data-bs-theme')) {
    root.setAttribute('data-bs-theme', isDark() ? 'dark' : 'light');
  }

  render();
});

// Glossary: switch between Persian and A–Z order (both lists are in the page).
document.addEventListener('DOMContentLoaded', function () {
  var buttons = document.querySelectorAll('.glossary-switch__button');
  var lists = document.querySelectorAll('.glossary-index');
  if (!buttons.length || !lists.length) {
    return;
  }

  function show(script) {
    lists.forEach(function (list) {
      list.hidden = list.dataset.script !== script;
    });
    buttons.forEach(function (button) {
      var current = button.dataset.script === script;
      button.classList.toggle('is-current', current);
      button.setAttribute('aria-pressed', current ? 'true' : 'false');
    });
  }

  // Remember the choice; if storage is blocked, Persian order shows.
  var STORE = 'glossary-script';

  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      show(button.dataset.script);
      try { localStorage.setItem(STORE, button.dataset.script); } catch (e) { /* no storage */ }
    });
  });

  var saved = null;
  try { saved = localStorage.getItem(STORE); } catch (e) { /* no storage */ }
  if (saved === 'fa' || saved === 'en') {
    show(saved);
  }

  // Back from a term (…/glossary/#<term>): scroll to it and highlight it.
  var wanted = decodeURIComponent(window.location.hash.slice(1));
  if (wanted) {
    var items = document.querySelectorAll('.glossary-index:not([hidden]) .glossary-list__item');
    for (var i = 0; i < items.length; i++) {
      if (items[i].dataset.term === wanted) {
        items[i].scrollIntoView({ block: 'center' });
        items[i].classList.add('is-returned');
        break;
      }
    }
  }
});

// Footnotes: a marker opens the note in a small popover; its button jumps to
// the full footnote list at the bottom.
document.addEventListener('DOMContentLoaded', function () {
  var refs = Array.prototype.slice.call(document.querySelectorAll('main a.footnote-ref'));
  if (!refs.length) {
    return;
  }

  var DIGITS = '۰۱۲۳۴۵۶۷۸۹';
  function persian(n) {
    return String(n).replace(/\d/g, function (d) { return DIGITS[d]; });
  }

  var pop = document.createElement('div');
  pop.className = 'fn-pop';
  pop.setAttribute('role', 'dialog');
  pop.hidden = true;
  document.body.appendChild(pop);
  var opener = null;

  function close() {
    if (pop.hidden) {
      return;
    }
    pop.hidden = true;
    if (opener) {
      opener.setAttribute('aria-expanded', 'false');
      opener.focus({ preventScroll: true });
      opener = null;
    }
  }

  function open(ref, index, fromKeyboard) {
    var note = document.getElementById(decodeURIComponent(ref.hash.slice(1)));
    if (!note) {
      return;
    }
    var body = note.cloneNode(true);
    body.removeAttribute('id');
    Array.prototype.forEach.call(body.querySelectorAll('.footnote-backref'), function (a) { a.remove(); });

    pop.innerHTML = '';
    var text = document.createElement('div');
    text.className = 'fn-pop__text';
    if (note.classList.contains('footnote-latin')) {
      text.dir = 'ltr';
    }
    var num = document.createElement('span');
    num.className = 'fn-pop__num';
    num.textContent = persian(index) + '.';
    text.appendChild(num);
    while (body.firstChild) {
      text.appendChild(body.firstChild);
    }

    var bar = document.createElement('div');
    bar.className = 'fn-pop__bar';
    var go = document.createElement('a');
    go.className = 'fn-pop__go';
    go.href = ref.hash;
    go.textContent = 'رفتن به پانویس';
    go.addEventListener('click', function () { pop.hidden = true; opener = null; });
    var shut = document.createElement('button');
    shut.type = 'button';
    shut.className = 'fn-pop__close';
    shut.setAttribute('aria-label', 'بستن');
    shut.textContent = '×';
    shut.addEventListener('click', close);
    bar.appendChild(go);
    bar.appendChild(shut);

    pop.appendChild(text);
    pop.appendChild(bar);
    pop.setAttribute('aria-label', 'پانویس ' + persian(index));
    pop.hidden = false;

    // Below the marker, kept inside the viewport.
    var r = ref.getBoundingClientRect();
    var margin = 12;
    var width = pop.offsetWidth;
    var left = r.left + r.width / 2 - width / 2;
    left = Math.max(margin, Math.min(left, document.documentElement.clientWidth - width - margin));
    var top = r.bottom + 8;
    if (top + pop.offsetHeight > window.innerHeight - margin && r.top - pop.offsetHeight - 8 > margin) {
      top = r.top - pop.offsetHeight - 8;
    }
    pop.style.left = (left + window.scrollX) + 'px';
    pop.style.top = (top + window.scrollY) + 'px';

    opener = ref;
    ref.setAttribute('aria-expanded', 'true');
    if (fromKeyboard) {
      go.focus({ preventScroll: true });
    }
  }

  refs.forEach(function (ref, i) {
    ref.setAttribute('aria-haspopup', 'dialog');
    ref.setAttribute('aria-expanded', 'false');
    ref.addEventListener('click', function (event) {
      event.preventDefault();
      if (!pop.hidden && opener === ref) {
        close();
      } else {
        close();
        open(ref, i + 1, event.detail === 0);
      }
    });
  });

  document.addEventListener('click', function (event) {
    if (!pop.hidden && !pop.contains(event.target) && !event.target.closest('a.footnote-ref')) {
      close();
    }
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      close();
    }
  });
  // Mobile browsers fire resize while scrolling (the address bar); close only
  // when the width really changes.
  var width = document.documentElement.clientWidth;
  window.addEventListener('resize', function () {
    if (document.documentElement.clientWidth !== width) {
      width = document.documentElement.clientWidth;
      close();
    }
  });
});
