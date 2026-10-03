# فرگشت ۱۰۱ (Understanding Evolution in Persian)

[![CC BY-NC-SA 4.0](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

<div dir="rtl">

این پروژه، ترجمهٔ فارسی وب‌سایت [Understanding Evolution](https://evolution.berkeley.edu/) متعلق به دانشگاه برکلی است.

**[می‌توانید نسخهٔ آنلاین را اینجا بخوانید.](https://evolution101.ir/)**

### 🤝 مشارکت

برای مشارکت، اصلاح خطاها، یا بهبود گرافیک‌ها، لطفاً یک «Issue» باز کنید یا «Pull Request» بفرستید.

### ⚖️ مجوز و حق نشر

**محتوای اصلی:** © UC Museum of Paleontology Understanding Evolution، [www.understandingevolution.org](https://www.understandingevolution.org)

**این ترجمه:** این ترجمه، به‌عنوان اثری اقتباسی، تحت مجوز [کریتیو کامنز «انتساب-غیرتجاری-اشتراک همسان» ۴٫۰ بین‌المللی](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fa) منتشر شده است.

</div>

---

## 🛠️ Technical note

Built with [Pelican](https://getpelican.com/) on Python 3.12.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pelican content                        # build into _build/
pelican content --listen --autoreload  # preview at localhost:8000
python scripts/check_links.py _build   # check internal links (CI does too)
```

- `content/chapters/NNN-*.md`: one page each (chapter digit, then position; `x00` is the cover). The address comes from `Slug`, e.g. `evo101/chapter-4/cospeciation/`.
- `content/glossary/*.md`: one term each; set `Translated: yes` once checked.
- Images link to evolution.berkeley.edu; `content/images/` holds the few the original lacks.
- Link between pages with `{filename}NNN-name.md`.

---

This project is a Persian translation of UC Berkeley's [Understanding Evolution](https://evolution.berkeley.edu/) website.

**[You can read the live version here.](https://evolution101.ir/)**

### 🤝 Contribution

To contribute, fix typos, or improve graphics, please open an issue or submit a pull request.

### ⚖️ License and Attribution

**Original content:** © UC Museum of Paleontology Understanding Evolution, [www.understandingevolution.org](https://www.understandingevolution.org)

**This translation:** This translation (as a derivative work) is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
