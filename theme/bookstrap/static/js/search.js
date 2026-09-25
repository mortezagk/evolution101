// On-site search over window.SEARCH_INDEX (built by Pelican into
// search-index.js). Every word of the query must appear in a page; matches in
// the title rank higher. Spelling variants are smoothed over first: Arabic
// yeh/kaf, diacritics, tatweel, zero-width non-joiners and Persian/Arabic
// digits.
(function () {
  'use strict';

  var CHAR_MAP = {
    'ي': 'ی', 'ى': 'ی', // Arabic yeh / alef maksura -> Persian yeh
    'ك': 'ک',                     // Arabic kaf -> Persian keheh
    'ة': 'ه', 'ۀ': 'ه', // teh marbuta, heh with yeh -> heh
    'أ': 'ا', 'إ': 'ا', 'آ': 'ا' // alef forms -> alef
  };
  var DROP = /[ً-ٰٟـ‌‍‎‏]/;

  function normChar(ch) {
    if (DROP.test(ch)) return '';
    if (CHAR_MAP[ch]) return CHAR_MAP[ch];
    var code = ch.charCodeAt(0);
    if (code >= 0x06F0 && code <= 0x06F9) return String(code - 0x06F0); // Persian digits
    if (code >= 0x0660 && code <= 0x0669) return String(code - 0x0660); // Arabic digits
    return ch.toLowerCase();
  }

  // Normalised text plus, for each normalised character, its index in the
  // original string (so matches can be highlighted in the original text).
  function normalize(text) {
    var out = '', map = [];
    for (var i = 0; i < text.length; i++) {
      var n = normChar(text[i]);
      for (var j = 0; j < n.length; j++) { out += n[j]; map.push(i); }
    }
    return { text: out, map: map };
  }

  function terms(query) {
    return normalize(query).text.split(/\s+/).filter(Boolean);
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // Wrap every occurrence of any term in <mark>.
  function highlight(original, words) {
    var n = normalize(original), ranges = [];
    words.forEach(function (w) {
      var from = 0, at;
      while ((at = n.text.indexOf(w, from)) !== -1) {
        ranges.push([n.map[at], n.map[at + w.length - 1] + 1]);
        from = at + w.length;
      }
    });
    ranges.sort(function (a, b) { return a[0] - b[0]; });
    var html = '', pos = 0;
    ranges.forEach(function (r) {
      if (r[0] < pos) return;
      html += escapeHtml(original.slice(pos, r[0])) + '<mark>' + escapeHtml(original.slice(r[0], r[1])) + '</mark>';
      pos = r[1];
    });
    return html + escapeHtml(original.slice(pos));
  }

  function snippet(entry, words) {
    var n = entry._norm, at = -1;
    for (var i = 0; i < words.length && at === -1; i++) at = n.text.indexOf(words[i]);
    if (at === -1) return escapeHtml(entry.text.slice(0, 180)) + '…';
    var start = Math.max(0, n.map[at] - 80), end = Math.min(entry.text.length, n.map[at] + 140);
    while (start > 0 && entry.text[start] !== ' ') start--;
    while (end < entry.text.length && entry.text[end] !== ' ') end++;
    return (start > 0 ? '…' : '') + highlight(entry.text.slice(start, end).trim(), words) + (end < entry.text.length ? '…' : '');
  }

  function count(haystack, word) {
    var c = 0, from = 0, at;
    while ((at = haystack.indexOf(word, from)) !== -1) { c++; from = at + word.length; }
    return c;
  }

  function search(index, query) {
    var words = terms(query);
    if (!words.length) return { words: words, hits: [] };
    var hits = [];
    index.forEach(function (entry) {
      entry._norm = entry._norm || normalize(entry.text);
      entry._title = entry._title || normalize(entry.title).text;
      var score = 0;
      for (var i = 0; i < words.length; i++) {
        var inTitle = count(entry._title, words[i]), inText = count(entry._norm.text, words[i]);
        if (!inTitle && !inText) return;
        score += inTitle * 20 + Math.min(inText, 10);
      }
      var phrase = words.join(' '), title = entry._title.replace(/\s+/g, ' ').trim();
      if (title === phrase) score += 200;
      else if (title.indexOf(phrase) === 0) score += 60;
      else if (title.indexOf(phrase) !== -1) score += 30;
      hits.push({ entry: entry, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    return { words: words, hits: hits };
  }

  function toPersianDigits(n) {
    return String(n).replace(/\d/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'[d]; });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('site-search-form');
    var input = document.getElementById('site-search-input');
    var status = document.getElementById('search-status');
    var list = document.getElementById('search-results');
    var google = document.getElementById('search-google');
    var root = form.getAttribute('data-root') || '.';
    var domain = form.getAttribute('data-domain');
    var index = window.SEARCH_INDEX || [];

    function run(query, pushState) {
      query = query.trim();
      if (pushState && window.history && history.replaceState) {
        var url = new URL(window.location.href);
        if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
        try { history.replaceState(null, '', url); } catch (e) { /* file:// */ }
      }
      list.innerHTML = '';
      google.hidden = !query;
      if (query) {
        google.href = 'https://www.google.com/search?q=' + encodeURIComponent(query + ' site:' + domain);
      }
      if (!query) { status.textContent = ''; return; }
      var result = search(index, query);
      status.textContent = result.hits.length
        ? toPersianDigits(result.hits.length) + ' صفحه پیدا شد.'
        : 'صفحه‌ای با همهٔ این کلمات پیدا نشد.';
      result.hits.forEach(function (hit) {
        var e = hit.entry, li = document.createElement('li');
        li.className = 'search-result';
        li.innerHTML =
          '<a class="search-result__title" href="' + root + '/' + e.url + '">' + highlight(e.title, result.words) + '</a>' +
          '<span class="search-result__chapter">' + escapeHtml(e.chapter) + '</span>' +
          '<p class="search-result__snippet">' + snippet(e, result.words) + '</p>';
        list.appendChild(li);
      });
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      run(input.value, true);
    });

    var initial = new URLSearchParams(window.location.search).get('q');
    if (initial) { input.value = initial; run(initial, false); }
    input.focus();
  });
})();
