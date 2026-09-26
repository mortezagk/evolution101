# فرگشت ۱۰۱ (Understanding Evolution in Persian)

[![CC BY-NC-SA 4.0](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

این پروژه، ترجمهٔ فارسی وب‌سایت [Understanding Evolution](https://evolution.berkeley.edu/) متعلق به دانشگاه برکلی است.

**[می‌توانید نسخهٔ آنلاین را اینجا بخوانید.](https://evolution101.ir/)**

This project is a Persian translation of UC Berkeley's [Understanding Evolution](https://evolution.berkeley.edu/) website.

**[You can read the live version here.](https://evolution101.ir/)**

---

## 🛠️ ساخت و پیش‌نمایش (Building and previewing)

The site is built with [Pelican](https://getpelican.com/) (Python 3.12, see `.python-version`).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Build into _build/ exactly as CI does (any warning fails the build):
pelican content -s pelicanconf.py --fatal warnings

# Check that every internal link resolves (CI runs this after each build and
# won't deploy if a link is broken):
python scripts/check_links.py _build

# Check that every image hotlinked from evolution.berkeley.edu loads (CI runs
# this on every pull request and weekly; see .github/workflows/check-images.yml):
python scripts/check_links.py --images _build

# Preview at http://localhost:8000 with rebuild on save:
pelican content -s pelicanconf.py --listen --autoreload
```

Every link points at a real `index.html` file, so the built `_build/` folder
also works when opened straight from disk.

### Content layout

- `content/pages/index.md`: the home page, listing every section.
- `content/chapters/NNN-name.md`: one file per page. The first digit is the
  chapter (0 is the introduction, 1-6 the chapters) and the next two digits
  its position; `x00` is the chapter's cover page.
- Each page's address is `<chapter>-<chapter slug>/<position>-<page slug>/`,
  e.g. `4-speciation/06-cospeciation/`, taken from its `Slug` metadata. The
  slugs follow the original page's path on evolution.berkeley.edu.
- `Source` / `Source_title` name the original page, linked as «منبع ⎋» after
  the footnotes.
- Search runs in the browser over `search-index.js`, which the build writes
  from every page's text (`theme_overrides/templates/search_index.html`,
  `theme/bookstrap/static/js/search.js`); no Google indexing needed.
- Link to another page with `{filename}NNN-name.md` so links follow any
  future address change.
- Figures are not stored in this repository: each image links to the file
  on evolution.berkeley.edu, at the size the original page shows it, e.g.
  `![alt](https://evolution.berkeley.edu/wp-content/uploads/…/x.png){: width="500" height="185" loading="lazy" }`.

---

## 🤝 مشارکت (Contribution)

برای مشارکت، اصلاح خطاها، یا بهبود گرافیک‌ها، لطفاً یک «Issue» باز کنید یا «Pull Request» بفرستید.

To contribute, fix typos, or improve graphics, please open an issue or submit a pull request.

---

## ⚖️ مجوز و حق نشر (License and Attribution)

**محتوای اصلی / Original Content:**
<br>
© UC Museum of Paleontology Understanding Evolution, [www.understandingevolution.org](https://www.understandingevolution.org)

**این ترجمه / This Translation:**
<br>
This translation (as a derivative work) is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/).