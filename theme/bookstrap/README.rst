فرگشت ۱۰۱ theme
==================

The Pelican theme for this site. It started as the `bootstrap2` theme by
Jiachen Yang (farseerfc, 2012, Apache 2.0, see LICENSE.txt), as customised by
Jadi for BikeZen, and has since been rewritten for this book:

- Bootstrap 5.3 (right-to-left build ``css/bootstrap.rtl.min.css`` and
  ``js/bootstrap.bundle.min.js``; MIT, see ``css/bootstrap.LICENSE``)
- Font Awesome Free 7 (``fontawesome/``; icons CC BY 4.0, fonts SIL OFL 1.1,
  code MIT, see ``fontawesome/LICENSE.txt``). Use the current class names,
  e.g. ``<i class="fa-solid fa-book"></i>``.
- The Sahel font by Saber Rastikerdar (``font/``)
- No jQuery. ``js/site.js`` runs the sidebar's open/close behaviour.

Templates: ``base.html`` (layout, navbar, footer), ``sidebar.html`` (chapter
navigation), ``article.html`` (chapter pages and covers), ``page.html``
(home, about, search). Site styles live in ``css/style.css``.

To update Bootstrap or Font Awesome, copy the same files from the new
release's npm package (``npm pack bootstrap@5`` /
``npm pack @fortawesome/fontawesome-free@7``).
