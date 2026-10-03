// Sidebar: open/close each chapter's page list, keep one open at a time,
// and open the chapter of the current page on load.
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

// Dark mode. The page follows the reader's system setting on its own (a media
// query in style.css); this button overrides that by setting data-theme on
// <html>, and remembers the choice. base.html applies a saved choice before
// the first paint.
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
    // The button offers the theme you would switch to, not the one you are in.
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

// Glossary: switch between the Persian ordering and the A–Z one. Both lists
// are in the page; this only changes which is shown, so it still reads
// without JavaScript.
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
  // Remember the choice; if storage is blocked, Persian order shows.
  var STORE = 'glossary-script';

      button.classList.toggle('is-current', current);
      button.setAttribute('aria-pressed', current ? 'true' : 'false');
    });
      try { localStorage.setItem(STORE, button.dataset.script); } catch (e) { /* no storage */ }
  }


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
  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      show(button.dataset.script);
    });
  });
});
