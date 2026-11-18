"""The App Store and Google Play links of every page become the official store badges (18 Nov 2026, Rajbir).

The badges are the companies' own files, unchanged (img/badges; downloaded on the Mac by ops/badges/fetch.sh in wayaroo-ios;
only the clear pixels round the Google badge were cut away). The text of the old link stays as the alt text. Each page also
gets stores.js: the store of the visitor's own phone first, a bar at the top with that store, and a line to rate the app.
Run: python3 _tools/stores.py   (build_cities.py runs it too, at the end). Running it again changes nothing.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAY_LANG = {"zh": "zh-cn", "ja": "ja", "vi": "vi", "hi": "hi", "pa": "pa"}
SKIP = {"googlea76703ac629521e5.html"}
VERSION = "202611182"   # change it when site.css or stores.js changes: browsers then load the new files at once

LINK = re.compile(r'<a class="badge(?: alt2)?" href="(https://(?:apps\.apple\.com|play\.google\.com)/[^"]+)">([^<]+)</a>')


def badgify(html: str) -> str:
    m = re.search(r'<html lang="([a-zA-Z]+)', html)
    lang = (m.group(1) if m else "en").lower()
    play = PLAY_LANG.get(lang, "en")

    def rep(mm):
        href, text = mm.group(1), mm.group(2)
        if "apps.apple.com" in href:
            return (f'<a class="store ios" href="{href}"><img src="img/badges/app-store-en.svg" alt="{text}" '
                    f'width="144" height="48"></a>')
        return (f'<a class="store android" href="{href}"><img src="img/badges/google-play-{play}.png" alt="{text}" '
                f'width="161" height="48"></a>')

    html = LINK.sub(rep, html)
    if "stores.js" not in html and "</body>" in html:
        src = "/stores.js" if 'href="/site.css' in html else "stores.js"   # 404.html is shown at any path
        html = html.replace("</body>", f'<script src="{src}" defer></script>\n</body>', 1)
    html = re.sub(r'href="(/?)site\.css(?:\?v=\d+)?"', lambda m: f'href="{m.group(1)}site.css?v={VERSION}"', html)
    html = re.sub(r'src="(/?)stores\.js(?:\?v=\d+)?"', lambda m: f'src="{m.group(1)}stores.js?v={VERSION}"', html)
    return html


def badgify_all(root: Path = ROOT) -> int:
    n = 0
    for f in sorted(root.glob("*.html")):
        if f.name in SKIP:
            continue
        old = f.read_text(encoding="utf-8")
        new = badgify(old)
        if new != old:
            f.write_text(new, encoding="utf-8")
            n += 1
    return n


if __name__ == "__main__":
    print("pages changed:", badgify_all())
