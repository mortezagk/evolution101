# فرگشت ۱۰۱ (Understanding Evolution in Persian)

[![CC BY-NC-SA 4.0](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

این پروژه، ترجمهٔ فارسی وب‌سایت [Understanding Evolution](https://evolution.berkeley.edu/) متعلق به دانشگاه برکلی است.

**[می‌توانید نسخهٔ آنلاین را اینجا بخوانید.](https://mortezagk.github.io/evolution101/)**

This project is a Persian translation of UC Berkeley's [Understanding Evolution](https://evolution.berkeley.edu/) website.

**[You can read the live version here.](https://mortezagk.github.io/evolution101/)**

---

## 🛠️ ساخت و پیش‌نمایش (Building and previewing)

The site is built with [Pelican](https://getpelican.com/) (Python 3.12, see `.python-version`).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Build into _build/ exactly as CI does (any warning fails the build):
pelican content -s pelicanconf.py --fatal warnings

# Preview at http://localhost:8000 with rebuild on save:
pelican content -s pelicanconf.py --listen --autoreload
```

Pages use folder-style addresses (`speciation/cospeciation/`), so preview
through `--listen` (or any web server) rather than opening the HTML files
directly from disk.

### Content layout

- `content/chapters/NNN-name.md`: one file per page. The first digit is the
  chapter (0-6) and the next two digits its position; `x00` is the chapter's
  cover page. `000` is the introduction, which is also the home page.
- Each file's metadata ties it to the original page:
  - `Slug`: its path on evolution.berkeley.edu after `/evolution-101/`,
    which is also its address on this site.
  - `Source` / `Source_title`: the original page, linked at the bottom.
  - `Redirect_from`: old addresses that should forward here
    (handled by `plugins/redirects`).
- `content/images/`: figures, named as on the original site where possible.

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