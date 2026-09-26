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
