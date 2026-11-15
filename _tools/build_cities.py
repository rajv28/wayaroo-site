#!/usr/bin/env python3
"""Writes the city pages and cities.html from _tools/cities_data.py.

  python3 _tools/build_cities.py

The folder name starts with "_", so GitHub Pages does not publish it. The pages are plain files in the site root.
A city's picture (img/city-<slug>.jpg) is used when the file is there.
"""
import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cities_data import APP, CITIES, FARES_CHECKED, SNAP, SNAP_DAY, SNAP_ISO, STORE  # noqa: E402

# 16 Nov 2026: Queensland is paused. Translink's open-data terms ask each app for a release and indemnity (and the same
# from its users); Rajbir's rule is no indemnity, so the app hides Translink's data and Rajbir asks Translink for
# permission without it. A paused city keeps its page (a short notice in place of the live numbers) and leaves the lists.
PAUSED = {"brisbane", "gold-coast", "cairns"}
LISTED = [c for c in CITIES if c["slug"] not in PAUSED]

ROOT = pathlib.Path(__file__).resolve().parent.parent
E = html.escape
ADS = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6318067996201537" crossorigin="anonymous"></script>'
NAV = '''  <nav>
    <a class="brand" href="index.html"><img src="icon.svg" alt="">Wayaroo</a>
    <div class="links"><a href="live-public-transport.html">Live transport</a><a href="fuel-prices.html">Fuel</a><a href="driving.html">Driving</a><a href="public-toilets.html">Toilets</a><a href="support.html">Support</a><a class="open" href="https://app.wayaroo.com/">Open the app</a></div>
  </nav>'''
FOOT = '''  <footer>
    <p>Wayaroo™ is published by Ozrsym Pty Ltd (ABN 56 671 004 390), Victoria, Australia. Contact: <a href="mailto:support@wayaroo.com">support@wayaroo.com</a></p>
    <p><a href="index.html">Home</a><a href="cities.html">Cities</a><a href="live-public-transport.html">Live transport</a><a href="fuel-prices.html">Fuel prices</a><a href="driving.html">Driving</a><a href="public-toilets.html">Public toilets</a><a href="support.html">Support</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="credits.html">Data credits</a></p>
    <p>Follow Wayaroo: <a href="https://www.facebook.com/profile.php?id=61596770721004" rel="me noopener">Facebook</a><a href="https://www.linkedin.com/company/wayaroo" rel="me noopener">LinkedIn</a><a href="https://www.youtube.com/@wayarooapp" rel="me noopener">YouTube</a><a href="https://x.com/wayaroo" rel="me noopener">X</a><a href="https://www.instagram.com/wayaroo/" rel="me noopener">Instagram</a><a href="https://www.tiktok.com/@app.wayaroo.com" rel="me noopener">TikTok</a></p>
    <p>© 2026 Ozrsym Pty Ltd</p>
  </footer>'''
CTA = f'''  <section class="cta">
    <div><b>Get Wayaroo on the App Store, or use it in your browser.</b><br><span class="note">Free, no account, 20 languages. For iPhone and iPad. The Android app is in review at Google Play.</span></div>
    <span class="ctabtns"><a class="badge" href="{STORE}">Download on the App Store</a><a class="badge alt" href="{APP}">Open in your browser</a></span>
  </section>'''


def n(x):
    return f"{x:,}"


def join_counts(counts):
    parts = [f"{n(c)} {E(label)}" for label, c in counts]
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def view_link(c, zoom=None):
    lon, lat, z = c["view"]
    return f"{APP}?view={lon},{lat},{zoom or z}&modes=rtbf"


def og_image(image):
    # A link card on a social site wants a wide picture (1200 x 630); the tall phone picture is cut badly.
    if image in ("img/live-melbourne.jpg", "img/share-card.jpg"):
        return "img/share-card.jpg"
    wide = image.replace("img/city-", "img/share-")  # a wide card of the city, when there is one
    return wide if image.startswith("img/city-") and (ROOT / wide).exists() else image


def og_size(image):
    return '\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">' if og_image(image).startswith("img/share-") else ""


def head(title, desc, path, image, ld, lang="en-AU", alts=None, nav=None):
    alt = "".join(f'\n<link rel="alternate" hreflang="{h}" href="https://wayaroo.com/{u}">' for h, u in (alts or []))
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-itunes-app" content="app-id=6831237478">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="https://wayaroo.com/{path}">{alt}
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="stylesheet" href="site.css">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Wayaroo">
<meta property="og:title" content="{E(title.split(" | ")[0])}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="https://wayaroo.com/{path}">
<meta property="og:image" content="https://wayaroo.com/{og_image(image)}">{og_size(image)}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
{ADS}
</head>
<body>
<div class="wrap">
{nav or NAV}
'''


# A city's pages in other languages: (key of its block in cities_data.py, file suffix, hreflang, link label).
# A city can carry several blocks (ja, zh); each makes <slug>-<suffix>.html. The English page stays the default.
LANGS = [("ja", "ja", "ja", "日本語"), ("zh", "zh", "zh-Hans", "中文"), ("hi", "hi", "hi", "हिन्दी"), ("pa", "pa", "pa", "ਪੰਜਾਬੀ"), ("vi", "vi", "vi", "Tiếng Việt")]


def lang_alts(c):
    """The English page and each other-language page of a city point at each other (hreflang)."""
    others = [(hl, f"{c['slug']}-{suf}.html") for key, suf, hl, _ in LANGS if c.get(key)]
    return [("en", f"{c['slug']}.html")] + others + [("x-default", f"{c['slug']}.html")] if others else None


def lang_links(c):
    """' · 日本語' / ' · 中文' links on the English page, one per language the city has."""
    return "".join(f' · <a href="{c["slug"]}-{suf}.html" lang="{hl}" hreflang="{hl}">{label}</a>' for key, suf, hl, label in LANGS if c.get(key))


def city_page(c):
    path = f"{c['slug']}.html"
    img = f"img/city-{c['slug']}.jpg"
    has_img = (ROOT / img).exists()
    image = img if has_img else "img/live-melbourne.jpg"
    total = sum(v for _, v in c["counts"])
    snap, snap_iso, snap_day = c.get("snap", SNAP), c.get("snap_iso", SNAP_ISO), c.get("snap_day", SNAP_DAY)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": c["h1"], "url": f"https://wayaroo.com/{path}", "isPartOf": {"@id": "https://wayaroo.com/#website"},
             "about": {"@id": "https://wayaroo.com/#app"}, "primaryImageOfPage": f"https://wayaroo.com/{image}", "inLanguage": "en-AU", "dateModified": snap_iso},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Wayaroo", "item": "https://wayaroo.com/"},
                {"@type": "ListItem", "position": 2, "name": "Cities", "item": "https://wayaroo.com/cities.html"},
                {"@type": "ListItem", "position": 3, "name": c["name"], "item": f"https://wayaroo.com/{path}"}]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]},
        ],
    }
    shot_img = f'<img class="shot" src="{img}" width="375" height="815" alt="Live public transport moving on the map of {E(c["name"])} in Wayaroo, on {snap_day}">'
    webp = f"img/city-{c['slug']}.webp"
    if has_img and (ROOT / webp).exists():  # WebP first, the JPEG for old browsers and link previews (site commit 3638f73)
        shot_img = f'<picture><source srcset="{webp}" type="image/webp">{shot_img}</picture>'
    shot = f"\n    {shot_img}" if has_img else ""
    rows = "".join(f"<tr><td>{E(label[0].upper() + label[1:])}</td><td>{n(v)}</td></tr>" for label, v in c["counts"])
    fare = (f'\n  <p><b>The fare deal Wayaroo shows here:</b> {E(c["fare"])} <span class="note">(checked on {FARES_CHECKED}; the app links to the source.)</span></p>' if c["fare"] else "")
    also = f"\n  <p>{E(c['also'])}</p>" if c["also"] else ""
    extras = "".join(f"\n    <li>{x}</li>" for x in c["extras"])
    faq = "".join(f"\n    <details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in c["faq"])
    others = " · ".join(f'<a href="{o["slug"]}.html">{E(o["name"])}</a>' for o in LISTED if o["slug"] != c["slug"])
    body = f'''
  <p class="note"><a href="index.html">Wayaroo</a> › <a href="cities.html">Cities</a> › {E(c["name"])}{lang_links(c)}</p>
  <section class="feature{'' if has_img else ' solo'}">
    <div>
      <h1>{E(c["h1"])}</h1>
      <p>{E(c["lede"])}</p>
      <p><span class="ctabtns"><a class="badge go" href="{view_link(c)}">Open the live map of {E(c["name"])}</a><a class="badge alt2" href="{STORE}">Get the iPhone app</a></span></p>
      <p class="note">Free. No account. It opens in your browser.</p>
    </div>{shot}
  </section>

  <h2>What was on the map</h2>
  <p>On {snap}, Wayaroo showed {n(total)} vehicles in {E(c["name"])}: {join_counts(c["counts"])}.</p>
  <div class="tablewrap"><table class="facts"><thead><tr><th>Live on the map</th><th>Vehicles at that time</th></tr></thead><tbody>{rows}</tbody></table></div>{also}
  <p class="note">The numbers change through the day. Source: {E(c["source"])}.</p>

  <h2>What you can do</h2>
  <ul class="plain">
    <li><b>See your ride now.</b> {c.get("see") or "Tap a vehicle to see its route, where it is going, its next stops and, when the operator sends a prediction, how late it is."}</li>
    <li><b>Follow it.</b> "Ride along" keeps the map on one vehicle.</li>{extras}
  </ul>

  <h2>Plan the trip</h2>
  <p>{E(c["plan"])}</p>{fare}

  <section class="faq">
    <h2>Questions people ask</h2>{faq}
    <details><summary>Is Wayaroo free?</summary><p>Yes. Wayaroo is free and needs no account. Your settings stay on your phone.</p></details>
  </section>

{CTA}

  <p>Other cities: {others} · <a href="cities.html">all cities</a></p>
  <p class="note">Wayaroo is an independent app from Ozrsym Pty Ltd. {E(c.get("endorse") or c["operator"] + " does not run or endorse it.")} Live positions and times come from the operator's feed. They can be late or wrong. Always check the sign at the stop. Full list of sources: <a href="credits.html">data credits</a>.</p>

{FOOT}
</div>
</body>
</html>
'''
    (ROOT / path).write_text(head(c["title"], c["desc"], path, image, ld, alts=lang_alts(c)) + body, encoding="utf-8")
    return path


# Japanese pages (cities with a "ja" block): the same facts as the English page, in polite Japanese. The links go to
# the English pages of the site (they have no Japanese copy yet); the app itself opens in Japanese on a Japanese phone.
JA_NAV = '''  <nav>
    <a class="brand" href="index.html"><img src="icon.svg" alt="">Wayaroo</a>
    <div class="links"><a href="live-public-transport.html">交通情報</a><a href="fuel-prices.html">燃料</a><a href="driving.html">運転</a><a href="public-toilets.html">トイレ</a><a href="support.html">サポート</a><a class="open" href="https://app.wayaroo.com/">アプリを開く</a></div>
  </nav>'''
JA_FOOT = '''  <footer>
    <p>Wayaroo™ の発行元は Ozrsym Pty Ltd（ABN 56 671 004 390、オーストラリア・ビクトリア州）です。お問い合わせ：<a href="mailto:support@wayaroo.com">support@wayaroo.com</a></p>
    <p><a href="index.html">ホーム</a><a href="cities.html">都市一覧</a><a href="live-public-transport.html">交通情報</a><a href="fuel-prices.html">燃料価格</a><a href="driving.html">運転</a><a href="public-toilets.html">公衆トイレ</a><a href="support.html">サポート</a><a href="privacy.html">プライバシー</a><a href="terms.html">利用規約</a><a href="credits.html">データ出典</a></p>
    <p>Wayaroo をフォロー：<a href="https://www.facebook.com/profile.php?id=61596770721004" rel="me noopener">Facebook</a><a href="https://www.linkedin.com/company/wayaroo" rel="me noopener">LinkedIn</a><a href="https://www.youtube.com/@wayarooapp" rel="me noopener">YouTube</a><a href="https://x.com/wayaroo" rel="me noopener">X</a><a href="https://www.instagram.com/wayaroo/" rel="me noopener">Instagram</a><a href="https://www.tiktok.com/@app.wayaroo.com" rel="me noopener">TikTok</a></p>
    <p>© 2026 Ozrsym Pty Ltd</p>
  </footer>'''
JA_CTA = f'''  <section class="cta">
    <div><b>App Store で Wayaroo を入手するか、ブラウザでご利用ください。</b><br><span class="note">無料、アカウント不要、20言語対応（日本語を含む）。iPhone・iPad 用です。Android アプリは Google Play で審査中です。</span></div>
    <span class="ctabtns"><a class="badge" href="{STORE}">App Store からダウンロード</a><a class="badge alt" href="{APP}">ブラウザで開く</a></span>
  </section>'''
JA_SEE = "車両をタップすると、系統、行き先、次の停留所、そして事業者が予測を送っている場合は遅れが表示されます。"


def city_page_ja(c):
    j = c["ja"]
    path = f"{c['slug']}-ja.html"
    img = f"img/city-{c['slug']}.jpg"
    has_img = (ROOT / img).exists()
    image = img if has_img else "img/live-melbourne.jpg"
    counts = [(j["labels"][label], v) for label, v in c["counts"]]  # the English page's numbers, Japanese words
    total = sum(v for _, v in counts)
    snap_iso = c.get("snap_iso", SNAP_ISO)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": j["h1"], "url": f"https://wayaroo.com/{path}", "isPartOf": {"@id": "https://wayaroo.com/#website"},
             "about": {"@id": "https://wayaroo.com/#app"}, "primaryImageOfPage": f"https://wayaroo.com/{image}", "inLanguage": "ja", "dateModified": snap_iso},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Wayaroo", "item": "https://wayaroo.com/"},
                {"@type": "ListItem", "position": 2, "name": "都市一覧", "item": "https://wayaroo.com/cities.html"},
                {"@type": "ListItem", "position": 3, "name": j["name"], "item": f"https://wayaroo.com/{path}"}]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in j["faq"]]},
        ],
    }
    shot_img = f'<img class="shot" src="{img}" width="375" height="815" alt="{E(j["name"])}の交通が Wayaroo の地図上で動いている様子（{E(j["snap_day"])}）">'
    webp = f"img/city-{c['slug']}.webp"
    if has_img and (ROOT / webp).exists():
        shot_img = f'<picture><source srcset="{webp}" type="image/webp">{shot_img}</picture>'
    shot = f"\n    {shot_img}" if has_img else ""
    rows = "".join(f"<tr><td>{E(label)}</td><td>{n(v)}台</td></tr>" for label, v in counts)
    listed = "、".join(f"{E(label)} {n(v)}台" for label, v in counts)
    also = f"\n  <p>{E(j['also'])}</p>" if j.get("also") else ""
    extras = "".join(f"\n    <li>{x}</li>" for x in j["extras"])
    faq = "".join(f"\n    <details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in j["faq"])
    others = "、".join(f'<a href="{o["slug"]}-ja.html">{E(o["ja"]["name"])}</a>' for o in LISTED if o.get("ja") and o["slug"] != c["slug"])
    body = f'''
  <p class="note"><a href="index.html">Wayaroo</a> › <a href="cities.html">都市一覧</a> › {E(j["name"])} · <a href="{c["slug"]}.html" lang="en" hreflang="en">English</a></p>
  <section class="feature{'' if has_img else ' solo'}">
    <div>
      <h1>{E(j["h1"])}</h1>
      <p>{E(j["lede"])}</p>
      <p><span class="ctabtns"><a class="badge go" href="{view_link(c)}">{E(j["name"])}のライブマップを開く</a><a class="badge alt2" href="{STORE}">iPhone アプリを入手</a></span></p>
      <p class="note">無料です。アカウントは不要です。ブラウザで開きます。</p>
    </div>{shot}
  </section>

  <h2>地図に表示されていた車両</h2>
  <p>{E(j["snap"])}、Wayaroo の地図には{E(j["name"])}で{n(total)}台の車両が表示されていました（{listed}）。</p>
  <div class="tablewrap"><table class="facts"><thead><tr><th>種類</th><th>その時の台数</th></tr></thead><tbody>{rows}</tbody></table></div>{also}
  <p class="note">台数は時間帯によって変わります。出典：{E(j["source"])}。</p>

  <h2>できること</h2>
  <ul class="plain">
    <li><b>今の位置を見る。</b>{j.get("see") or JA_SEE}</li>
    <li><b>追いかける。</b>「同乗する」を選ぶと、地図が1台の車両を追い続けます。</li>{extras}
  </ul>

  <h2>ルートを調べる</h2>
  <p>{E(j["plan"])}</p>

  <section class="faq">
    <h2>よくある質問</h2>{faq}
    <details><summary>Wayaroo は無料ですか？</summary><p>はい。Wayaroo は無料で、アカウントは不要です。設定はお使いのスマートフォンに保存されます。</p></details>
  </section>

{JA_CTA}

  <p>{"ほかの都市（日本語）：" + others + " · " if others else ""}<a href="cities.html">都市一覧（英語）</a></p>
  <p class="note">Wayaroo は Ozrsym Pty Ltd による独立したアプリです。{E(j["endorse"])}車両の位置と時刻は事業者のデータによるもので、遅れや誤りがある場合があります。必ず停留所の表示もご確認ください。データの出典一覧：<a href="credits.html">データ出典</a>（英語）。</p>

{JA_FOOT}
</div>
</body>
</html>
'''
    (ROOT / path).write_text(head(j["title"], j["desc"], path, image, ld, lang="ja", alts=lang_alts(c), nav=JA_NAV) + body, encoding="utf-8")
    return path


# Simplified Chinese pages (cities with a "zh" block): the same facts as the English page. The site's other pages are
# in English (the links say so); the app itself opens in Chinese on a Chinese phone.
ZH_NAV = """  <nav>
    <a class="brand" href="index.html"><img src="icon.svg" alt="">Wayaroo</a>
    <div class="links"><a href="live-public-transport.html">实时交通</a><a href="fuel-prices.html">油价</a><a href="driving.html">驾驶</a><a href="public-toilets.html">厕所</a><a href="support.html">支持</a><a class="open" href="https://app.wayaroo.com/">打开应用</a></div>
  </nav>"""
ZH_FOOT = """  <footer>
    <p>Wayaroo™ 由 Ozrsym Pty Ltd（ABN 56 671 004 390，澳大利亚维多利亚州）发布。联系方式：<a href="mailto:support@wayaroo.com">support@wayaroo.com</a></p>
    <p><a href="index.html">首页</a><a href="cities.html">城市列表</a><a href="live-public-transport.html">实时交通</a><a href="fuel-prices.html">油价</a><a href="driving.html">驾驶</a><a href="public-toilets.html">公共厕所</a><a href="support.html">支持</a><a href="privacy.html">隐私</a><a href="terms.html">条款</a><a href="credits.html">数据来源</a></p>
    <p>关注 Wayaroo：<a href="https://www.facebook.com/profile.php?id=61596770721004" rel="me noopener">Facebook</a><a href="https://www.linkedin.com/company/wayaroo" rel="me noopener">LinkedIn</a><a href="https://www.youtube.com/@wayarooapp" rel="me noopener">YouTube</a><a href="https://x.com/wayaroo" rel="me noopener">X</a><a href="https://www.instagram.com/wayaroo/" rel="me noopener">Instagram</a><a href="https://www.tiktok.com/@app.wayaroo.com" rel="me noopener">TikTok</a></p>
    <p>© 2026 Ozrsym Pty Ltd</p>
  </footer>"""
ZH_CTA = f"""  <section class="cta">
    <div><b>在 App Store 下载 Wayaroo，或在浏览器中使用。</b><br><span class="note">免费，无需注册账户，支持20种语言（含中文）。适用于 iPhone 和 iPad。Android 版正在 Google Play 审核中。</span></div>
    <span class="ctabtns"><a class="badge" href="{STORE}">在 App Store 下载</a><a class="badge alt" href="{APP}">在浏览器中打开</a></span>
  </section>"""
ZH_SEE = "点击车辆，即可查看线路、开往哪里、接下来的站点，以及运营方提供预测时的晚点情况。"
_MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}


def zh_date(d):
    """'2 November 2026' → '2026年11月2日'."""
    day, month, year = d.split()
    return f"{year}年{_MONTHS[month]}月{int(day)}日"


def city_page_zh(c):
    z = c["zh"]
    path = f"{c['slug']}-zh.html"
    img = f"img/city-{c['slug']}.jpg"
    has_img = (ROOT / img).exists()
    image = img if has_img else "img/live-melbourne.jpg"
    counts = [(z["labels"][label], v) for label, v in c["counts"]]  # the English page's numbers, Chinese words
    total = sum(v for _, v in counts)
    snap_iso = c.get("snap_iso", SNAP_ISO)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": z["h1"], "url": f"https://wayaroo.com/{path}", "isPartOf": {"@id": "https://wayaroo.com/#website"},
             "about": {"@id": "https://wayaroo.com/#app"}, "primaryImageOfPage": f"https://wayaroo.com/{image}", "inLanguage": "zh-Hans", "dateModified": snap_iso},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Wayaroo", "item": "https://wayaroo.com/"},
                {"@type": "ListItem", "position": 2, "name": "城市列表", "item": "https://wayaroo.com/cities.html"},
                {"@type": "ListItem", "position": 3, "name": z["name"], "item": f"https://wayaroo.com/{path}"}]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in z["faq"]]},
        ],
    }
    shot_img = f'<img class="shot" src="{img}" width="375" height="815" alt="{E(z["name"])}的公共交通在 Wayaroo 地图上实时移动（{E(z["snap_day"])}）">'
    webp = f"img/city-{c['slug']}.webp"
    if has_img and (ROOT / webp).exists():
        shot_img = f'<picture><source srcset="{webp}" type="image/webp">{shot_img}</picture>'
    shot = f"\n    {shot_img}" if has_img else ""
    rows = "".join(f"<tr><td>{E(label)}</td><td>{n(v)}</td></tr>" for label, v in counts)
    listed = "、".join(f"{E(label)} {n(v)}" for label, v in counts)
    also = f"\n  <p>{E(z['also'])}</p>" if z.get("also") else ""
    fare = (f'\n  <p><b>Wayaroo 在此显示的票价优惠：</b>{E(z["fare"])} <span class="note">（核实日期：{zh_date(FARES_CHECKED)}；应用内附有来源链接。）</span></p>' if z.get("fare") else "")
    extras = "".join(f"\n    <li>{x}</li>" for x in z["extras"])
    faq = "".join(f"\n    <details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in z["faq"])
    others = " · ".join(f'<a href="{o["slug"]}-zh.html">{E(o["zh"]["name"])}</a>' for o in LISTED if o.get("zh") and o["slug"] != c["slug"])
    body = f"""
  <p class="note"><a href="index.html">Wayaroo</a> › <a href="cities.html">城市列表</a> › {E(z["name"])} · <a href="{c["slug"]}.html" lang="en" hreflang="en">English</a></p>
  <section class="feature{'' if has_img else ' solo'}">
    <div>
      <h1>{E(z["h1"])}</h1>
      <p>{E(z["lede"])}</p>
      <p><span class="ctabtns"><a class="badge go" href="{view_link(c)}">打开{E(z["name"])}实时地图</a><a class="badge alt2" href="{STORE}">下载 iPhone 应用</a></span></p>
      <p class="note">免费，无需注册账户，在浏览器中打开。</p>
    </div>{shot}
  </section>

  <h2>当时地图上的车辆</h2>
  <p>{E(z["snap"])}，Wayaroo 在{E(z["name"])}的地图上共显示了 {n(total)} 辆车（{listed}）。</p>
  <div class="tablewrap"><table class="facts"><thead><tr><th>类型</th><th>当时的车辆数</th></tr></thead><tbody>{rows}</tbody></table></div>{also}
  <p class="note">车辆数在一天中会变化。数据来源：{E(z["source"])}。</p>

  <h2>您可以做什么</h2>
  <ul class="plain">
    <li><b>查看车辆现在在哪里。</b>{z.get("see") or ZH_SEE}</li>
    <li><b>跟随一辆车。</b>选择“跟车视角”，地图会一直跟随这辆车。</li>{extras}
  </ul>

  <h2>规划行程</h2>
  <p>{E(z["plan"])}</p>{fare}

  <section class="faq">
    <h2>常见问题</h2>{faq}
    <details><summary>Wayaroo 是免费的吗？</summary><p>是的。Wayaroo 免费，无需注册账户。您的设置保存在您的手机上。</p></details>
  </section>

{ZH_CTA}

  <p>{"其他城市（中文）：" + others + " · " if others else ""}<a href="cities.html">城市列表（英文）</a></p>
  <p class="note">Wayaroo 是 Ozrsym Pty Ltd 推出的独立应用。{E(z["endorse"])}车辆位置和时间来自运营方的数据，可能有延迟或错误。请务必查看车站的显示屏。完整的数据来源列表：<a href="credits.html">数据来源</a>（英文）。</p>

{ZH_FOOT}
</div>
</body>
</html>
"""
    (ROOT / path).write_text(head(z["title"], z["desc"], path, image, ld, lang="zh-Hans", alts=lang_alts(c), nav=ZH_NAV) + body, encoding="utf-8")
    return path


TR_FOOT_LINKS = ["index.html", "cities.html", "live-public-transport.html", "fuel-prices.html", "driving.html", "public-toilets.html", "support.html", "privacy.html", "terms.html", "credits.html"]
FOLLOW = '<a href="https://www.facebook.com/profile.php?id=61596770721004" rel="me noopener">Facebook</a><a href="https://www.linkedin.com/company/wayaroo" rel="me noopener">LinkedIn</a><a href="https://www.youtube.com/@wayarooapp" rel="me noopener">YouTube</a><a href="https://x.com/wayaroo" rel="me noopener">X</a><a href="https://www.instagram.com/wayaroo/" rel="me noopener">Instagram</a><a href="https://www.tiktok.com/@app.wayaroo.com" rel="me noopener">TikTok</a>'

# Page words for the Hindi, Punjabi and Vietnamese city pages (15 Nov 2026). App labels as the app's own
# strings write them (public/js/lang/hi.json, pa.json, vi.json: foryou, ride_along).
TR = {
    "hi": dict(
        nav=["लाइव ट्रांसपोर्ट", "ईंधन", "ड्राइविंग", "टॉयलेट", "सहायता", "ऐप खोलें"],
        foot_pub="Wayaroo™ को Ozrsym Pty Ltd (ABN 56 671 004 390), विक्टोरिया, ऑस्ट्रेलिया प्रकाशित करता है। संपर्क:",
        foot_links=["होम", "शहर", "लाइव ट्रांसपोर्ट", "ईंधन की कीमतें", "ड्राइविंग", "सार्वजनिक टॉयलेट", "सहायता", "गोपनीयता", "शर्तें", "डेटा स्रोत"],
        follow="Wayaroo को फ़ॉलो करें:",
        cta_b="Wayaroo को App Store से डाउनलोड करें, या अपने ब्राउज़र में इस्तेमाल करें।",
        cta_note="मुफ़्त, कोई अकाउंट नहीं, 20 भाषाएँ (हिन्दी समेत)। iPhone और iPad के लिए। Android ऐप Google Play पर समीक्षा में है।",
        cta_store="App Store से डाउनलोड करें", cta_web="ब्राउज़र में खोलें",
        cities="शहरों की सूची", open_map="{name} का लाइव मैप खोलें", get_app="iPhone ऐप डाउनलोड करें",
        free_note="मुफ़्त। कोई अकाउंट नहीं। आपके ब्राउज़र में खुलता है।",
        h_map="मैप पर क्या दिख रहा था", sentence="{snap}, Wayaroo ने {name} में मैप पर कुल {total} वाहन दिखाए ({listed})।", sep=", ",
        th=["प्रकार", "उस समय वाहन"], numbers="वाहनों की संख्या दिन भर बदलती रहती है। स्रोत: {source}।",
        h_do="आप क्या कर सकते हैं", see_b="अपनी सवारी अभी देखें।",
        see="किसी वाहन पर टैप करें और उसका रूट, वह कहाँ जा रहा है, उसके अगले स्टॉप और, जब ऑपरेटर अनुमान भेजता है, वह कितनी देर से है, देखें।",
        follow_b="उसे फ़ॉलो करें।", follow_t="“साथ चलें” चुनें, मैप एक ही वाहन पर बना रहता है।",
        h_plan="यात्रा प्लान करें", fare_b="Wayaroo यहाँ जो किराया छूट दिखाता है:", fare_note="(जाँच की तारीख़: {date}; ऐप में स्रोत का लिंक है।)",
        h_faq="लोग क्या पूछते हैं", free_q="क्या Wayaroo मुफ़्त है?", free_a="हाँ। Wayaroo मुफ़्त है और इसके लिए कोई अकाउंट नहीं चाहिए। आपकी सेटिंग्स आपके फ़ोन पर ही रहती हैं।",
        list_en="शहरों की सूची (अंग्रेज़ी में)",
        disclaimer="Wayaroo, Ozrsym Pty Ltd का एक स्वतंत्र ऐप है। {endorse} वाहनों की जगह और समय ऑपरेटर के डेटा से आते हैं और देर से या गलत हो सकते हैं। स्टॉप पर लगा बोर्ड ज़रूर देखें। सभी स्रोतों की पूरी सूची: <a href=\"credits.html\">डेटा स्रोत</a> (अंग्रेज़ी में)।",
        alt="{name} का सार्वजनिक परिवहन Wayaroo के मैप पर लाइव चलता हुआ ({snap_day})",
        months=["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"], date="{d} {m} {y}",
    ),
    "pa": dict(
        nav=["ਲਾਈਵ ਟਰਾਂਸਪੋਰਟ", "ਬਾਲਣ", "ਡਰਾਈਵਿੰਗ", "ਟਾਇਲਟ", "ਸਹਾਇਤਾ", "ਐਪ ਖੋਲ੍ਹੋ"],
        foot_pub="Wayaroo™ ਨੂੰ Ozrsym Pty Ltd (ABN 56 671 004 390), ਵਿਕਟੋਰੀਆ, ਆਸਟ੍ਰੇਲੀਆ ਪ੍ਰਕਾਸ਼ਿਤ ਕਰਦੀ ਹੈ। ਸੰਪਰਕ:",
        foot_links=["ਮੁੱਖ ਪੰਨਾ", "ਸ਼ਹਿਰ", "ਲਾਈਵ ਟਰਾਂਸਪੋਰਟ", "ਬਾਲਣ ਦੀਆਂ ਕੀਮਤਾਂ", "ਡਰਾਈਵਿੰਗ", "ਜਨਤਕ ਟਾਇਲਟ", "ਸਹਾਇਤਾ", "ਪਰਦੇਦਾਰੀ", "ਸ਼ਰਤਾਂ", "ਡੇਟਾ ਸਰੋਤ"],
        follow="Wayaroo ਨੂੰ ਫ਼ਾਲੋ ਕਰੋ:",
        cta_b="Wayaroo ਨੂੰ App Store ਤੋਂ ਡਾਊਨਲੋਡ ਕਰੋ, ਜਾਂ ਆਪਣੇ ਬ੍ਰਾਊਜ਼ਰ ਵਿੱਚ ਵਰਤੋ।",
        cta_note="ਮੁਫ਼ਤ, ਕੋਈ ਖਾਤਾ ਨਹੀਂ, 20 ਭਾਸ਼ਾਵਾਂ (ਪੰਜਾਬੀ ਸਮੇਤ)। iPhone ਅਤੇ iPad ਲਈ। Android ਐਪ Google Play 'ਤੇ ਸਮੀਖਿਆ ਅਧੀਨ ਹੈ।",
        cta_store="App Store ਤੋਂ ਡਾਊਨਲੋਡ ਕਰੋ", cta_web="ਬ੍ਰਾਊਜ਼ਰ ਵਿੱਚ ਖੋਲ੍ਹੋ",
        cities="ਸ਼ਹਿਰਾਂ ਦੀ ਸੂਚੀ", open_map="{name} ਦਾ ਲਾਈਵ ਨਕਸ਼ਾ ਖੋਲ੍ਹੋ", get_app="iPhone ਐਪ ਡਾਊਨਲੋਡ ਕਰੋ",
        free_note="ਮੁਫ਼ਤ। ਕੋਈ ਖਾਤਾ ਨਹੀਂ। ਤੁਹਾਡੇ ਬ੍ਰਾਊਜ਼ਰ ਵਿੱਚ ਖੁੱਲ੍ਹਦਾ ਹੈ।",
        h_map="ਨਕਸ਼ੇ 'ਤੇ ਕੀ ਦਿਖ ਰਿਹਾ ਸੀ", sentence="{snap}, Wayaroo ਨੇ {name} ਵਿੱਚ ਨਕਸ਼ੇ 'ਤੇ ਕੁੱਲ {total} ਵਾਹਨ ਦਿਖਾਏ ({listed})।", sep=", ",
        th=["ਕਿਸਮ", "ਉਸ ਸਮੇਂ ਵਾਹਨ"], numbers="ਵਾਹਨਾਂ ਦੀ ਗਿਣਤੀ ਦਿਨ ਭਰ ਬਦਲਦੀ ਰਹਿੰਦੀ ਹੈ। ਸਰੋਤ: {source}।",
        h_do="ਤੁਸੀਂ ਕੀ ਕਰ ਸਕਦੇ ਹੋ", see_b="ਆਪਣੀ ਸਵਾਰੀ ਹੁਣੇ ਵੇਖੋ।",
        see="ਕਿਸੇ ਵਾਹਨ 'ਤੇ ਟੈਪ ਕਰੋ ਅਤੇ ਉਸਦਾ ਰੂਟ, ਉਹ ਕਿੱਥੇ ਜਾ ਰਿਹਾ ਹੈ, ਉਸਦੇ ਅਗਲੇ ਸਟਾਪ ਅਤੇ, ਜਦੋਂ ਆਪਰੇਟਰ ਅਨੁਮਾਨ ਭੇਜਦਾ ਹੈ, ਉਹ ਕਿੰਨਾ ਲੇਟ ਹੈ, ਵੇਖੋ।",
        follow_b="ਉਸਨੂੰ ਫ਼ਾਲੋ ਕਰੋ।", follow_t="“ਨਾਲ ਚੱਲੋ” ਚੁਣੋ, ਨਕਸ਼ਾ ਇੱਕੋ ਵਾਹਨ 'ਤੇ ਟਿਕਿਆ ਰਹਿੰਦਾ ਹੈ।",
        h_plan="ਯਾਤਰਾ ਦੀ ਯੋਜਨਾ ਬਣਾਓ", fare_b="Wayaroo ਇੱਥੇ ਜੋ ਕਿਰਾਇਆ ਛੋਟ ਦਿਖਾਉਂਦਾ ਹੈ:", fare_note="(ਜਾਂਚ ਦੀ ਤਾਰੀਖ਼: {date}; ਐਪ ਵਿੱਚ ਸਰੋਤ ਦਾ ਲਿੰਕ ਹੈ।)",
        h_faq="ਲੋਕ ਕੀ ਪੁੱਛਦੇ ਹਨ", free_q="ਕੀ Wayaroo ਮੁਫ਼ਤ ਹੈ?", free_a="ਹਾਂ। Wayaroo ਮੁਫ਼ਤ ਹੈ ਅਤੇ ਕੋਈ ਖਾਤਾ ਨਹੀਂ ਚਾਹੀਦਾ। ਤੁਹਾਡੀਆਂ ਸੈਟਿੰਗਾਂ ਤੁਹਾਡੇ ਫ਼ੋਨ 'ਤੇ ਹੀ ਰਹਿੰਦੀਆਂ ਹਨ।",
        list_en="ਸ਼ਹਿਰਾਂ ਦੀ ਸੂਚੀ (ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ)",
        disclaimer="Wayaroo, Ozrsym Pty Ltd ਦੀ ਇੱਕ ਸੁਤੰਤਰ ਐਪ ਹੈ। {endorse} ਵਾਹਨਾਂ ਦੀ ਥਾਂ ਅਤੇ ਸਮਾਂ ਆਪਰੇਟਰ ਦੇ ਡੇਟਾ ਤੋਂ ਆਉਂਦੇ ਹਨ ਅਤੇ ਲੇਟ ਜਾਂ ਗਲਤ ਹੋ ਸਕਦੇ ਹਨ। ਸਟਾਪ 'ਤੇ ਲੱਗਿਆ ਬੋਰਡ ਜ਼ਰੂਰ ਵੇਖੋ। ਸਾਰੇ ਸਰੋਤਾਂ ਦੀ ਪੂਰੀ ਸੂਚੀ: <a href=\"credits.html\">ਡੇਟਾ ਸਰੋਤ</a> (ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ)।",
        alt="{name} ਦੀ ਜਨਤਕ ਆਵਾਜਾਈ Wayaroo ਦੇ ਨਕਸ਼ੇ 'ਤੇ ਲਾਈਵ ਚੱਲਦੀ ਹੋਈ ({snap_day})",
        months=["ਜਨਵਰੀ", "ਫ਼ਰਵਰੀ", "ਮਾਰਚ", "ਅਪ੍ਰੈਲ", "ਮਈ", "ਜੂਨ", "ਜੁਲਾਈ", "ਅਗਸਤ", "ਸਤੰਬਰ", "ਅਕਤੂਬਰ", "ਨਵੰਬਰ", "ਦਸੰਬਰ"], date="{d} {m} {y}",
    ),
    "vi": dict(
        nav=["Giao thông trực tiếp", "Nhiên liệu", "Lái xe", "Nhà vệ sinh", "Hỗ trợ", "Mở ứng dụng"],
        foot_pub="Wayaroo™ do Ozrsym Pty Ltd (ABN 56 671 004 390), Victoria, Úc phát hành. Liên hệ:",
        foot_links=["Trang chủ", "Thành phố", "Giao thông trực tiếp", "Giá nhiên liệu", "Lái xe", "Nhà vệ sinh công cộng", "Hỗ trợ", "Quyền riêng tư", "Điều khoản", "Nguồn dữ liệu"],
        follow="Theo dõi Wayaroo:",
        cta_b="Tải Wayaroo trên App Store, hoặc dùng ngay trong trình duyệt.",
        cta_note="Miễn phí, không cần tài khoản, 20 ngôn ngữ (có tiếng Việt). Cho iPhone và iPad. Ứng dụng Android đang được Google Play xét duyệt.",
        cta_store="Tải trên App Store", cta_web="Mở trong trình duyệt",
        cities="Danh sách thành phố", open_map="Mở bản đồ trực tiếp {name}", get_app="Tải ứng dụng iPhone",
        free_note="Miễn phí. Không cần tài khoản. Mở ngay trong trình duyệt.",
        h_map="Trên bản đồ lúc đó", sentence="{snap}, Wayaroo hiển thị {total} xe ở {name} trên bản đồ ({listed}).", sep=", ",
        th=["Loại", "Số xe lúc đó"], numbers="Số xe thay đổi trong ngày. Nguồn: {source}.",
        h_do="Bạn có thể làm gì", see_b="Xem xe của bạn ngay bây giờ.",
        see="Chạm vào một xe để xem tuyến, nơi xe đang đến, các trạm kế tiếp và, khi nhà vận hành gửi dự báo, xe trễ bao lâu.",
        follow_b="Theo dõi xe.", follow_t="Chọn “Đi cùng xe”, bản đồ sẽ luôn theo một xe.",
        h_plan="Lên kế hoạch chuyến đi", fare_b="Ưu đãi giá vé Wayaroo hiển thị ở đây:", fare_note="(kiểm tra {date}; ứng dụng có liên kết đến nguồn.)",
        h_faq="Câu hỏi thường gặp", free_q="Wayaroo có miễn phí không?", free_a="Có. Wayaroo miễn phí và không cần tài khoản. Cài đặt của bạn được lưu trên điện thoại của bạn.",
        list_en="Danh sách thành phố (tiếng Anh)",
        disclaimer="Wayaroo là ứng dụng độc lập của Ozrsym Pty Ltd. {endorse} Vị trí và giờ của xe lấy từ dữ liệu của nhà vận hành và có thể chậm hoặc sai. Hãy luôn xem bảng thông tin tại trạm. Danh sách đầy đủ các nguồn: <a href=\"credits.html\">nguồn dữ liệu</a> (tiếng Anh).",
        alt="Phương tiện công cộng ở {name} di chuyển trực tiếp trên bản đồ Wayaroo ({snap_day})",
        months=[str(i) for i in range(1, 13)], date="ngày {d} tháng {m} năm {y}", thou=".",
    ),
}


def tr_date(key, d):
    """'2 November 2026' in the page's language."""
    day, month, year = d.split()
    w = TR[key]
    return w["date"].format(d=int(day), m=w["months"][_MONTHS[month] - 1], y=year)


def city_page_tr(c, key):
    """A city page in Hindi, Punjabi or Vietnamese, from the city's block of that language: the English page's numbers."""
    w, z = TR[key], c[key]
    hl = next(h for k, _, h, _ in LANGS if k == key)
    path = f"{c['slug']}-{key}.html"
    img = f"img/city-{c['slug']}.jpg"
    has_img = (ROOT / img).exists()
    image = img if has_img else "img/live-melbourne.jpg"
    counts = [(z["labels"][label], v) for label, v in c["counts"]]
    total = sum(v for _, v in counts)
    snap_iso = c.get("snap_iso", SNAP_ISO)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": z["h1"], "url": f"https://wayaroo.com/{path}", "isPartOf": {"@id": "https://wayaroo.com/#website"},
             "about": {"@id": "https://wayaroo.com/#app"}, "primaryImageOfPage": f"https://wayaroo.com/{image}", "inLanguage": hl, "dateModified": snap_iso},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Wayaroo", "item": "https://wayaroo.com/"},
                {"@type": "ListItem", "position": 2, "name": w["cities"], "item": "https://wayaroo.com/cities.html"},
                {"@type": "ListItem", "position": 3, "name": z["name"], "item": f"https://wayaroo.com/{path}"}]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in z["faq"]]},
        ],
    }
    shot_img = f'<img class="shot" src="{img}" width="375" height="815" alt="{E(w["alt"].format(name=z["name"], snap_day=z["snap_day"]))}">'
    webp = f"img/city-{c['slug']}.webp"
    if has_img and (ROOT / webp).exists():
        shot_img = f'<picture><source srcset="{webp}" type="image/webp">{shot_img}</picture>'
    shot = f"\n    {shot_img}" if has_img else ""
    nn = lambda x: n(x).replace(",", w.get("thou", ","))  # 1.996 in Vietnamese, 1,996 elsewhere
    rows = "".join(f"<tr><td>{E(label)}</td><td>{nn(v)}</td></tr>" for label, v in counts)
    listed = w["sep"].join(f"{E(label)} {nn(v)}" for label, v in counts)
    also = f"\n  <p>{E(z['also'])}</p>" if z.get("also") else ""
    fare = (f'\n  <p><b>{E(w["fare_b"])}</b> {E(z["fare"])} <span class="note">{E(w["fare_note"].format(date=tr_date(key, FARES_CHECKED)))}</span></p>' if z.get("fare") else "")
    extras = "".join(f"\n    <li>{x}</li>" for x in z["extras"])
    faq = "".join(f"\n    <details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in z["faq"])
    nav_links = "".join(f'<a href="{u}">{E(t)}</a>' for u, t in zip(["live-public-transport.html", "fuel-prices.html", "driving.html", "public-toilets.html", "support.html"], w["nav"][:5]))
    nav = f'''  <nav>
    <a class="brand" href="index.html"><img src="icon.svg" alt="">Wayaroo</a>
    <div class="links">{nav_links}<a class="open" href="https://app.wayaroo.com/">{E(w["nav"][5])}</a></div>
  </nav>'''
    foot_links = "".join(f'<a href="{u}">{E(t)}</a>' for u, t in zip(TR_FOOT_LINKS, w["foot_links"]))
    foot = f'''  <footer>
    <p>{E(w["foot_pub"])} <a href="mailto:support@wayaroo.com">support@wayaroo.com</a></p>
    <p>{foot_links}</p>
    <p>{E(w["follow"])} {FOLLOW}</p>
    <p>© 2026 Ozrsym Pty Ltd</p>
  </footer>'''
    cta = f'''  <section class="cta">
    <div><b>{E(w["cta_b"])}</b><br><span class="note">{E(w["cta_note"])}</span></div>
    <span class="ctabtns"><a class="badge" href="{STORE}">{E(w["cta_store"])}</a><a class="badge alt" href="{APP}">{E(w["cta_web"])}</a></span>
  </section>'''
    sentence = E(w["sentence"]).format(snap=E(z["snap"]), name=E(z["name"]), total=nn(total), listed=listed)
    body = f"""
  <p class="note"><a href="index.html">Wayaroo</a> › <a href="cities.html">{E(w["cities"])}</a> › {E(z["name"])} · <a href="{c["slug"]}.html" lang="en" hreflang="en">English</a></p>
  <section class="feature{'' if has_img else ' solo'}">
    <div>
      <h1>{E(z["h1"])}</h1>
      <p>{E(z["lede"])}</p>
      <p><span class="ctabtns"><a class="badge go" href="{view_link(c)}">{E(w["open_map"].format(name=z["name"]))}</a><a class="badge alt2" href="{STORE}">{E(w["get_app"])}</a></span></p>
      <p class="note">{E(w["free_note"])}</p>
    </div>{shot}
  </section>

  <h2>{E(w["h_map"])}</h2>
  <p>{sentence}</p>
  <div class="tablewrap"><table class="facts"><thead><tr><th>{E(w["th"][0])}</th><th>{E(w["th"][1])}</th></tr></thead><tbody>{rows}</tbody></table></div>{also}
  <p class="note">{E(w["numbers"].format(source=z["source"]))}</p>

  <h2>{E(w["h_do"])}</h2>
  <ul class="plain">
    <li><b>{E(w["see_b"])}</b> {E(z.get("see") or w["see"])}</li>
    <li><b>{E(w["follow_b"])}</b> {E(w["follow_t"])}</li>{extras}
  </ul>

  <h2>{E(w["h_plan"])}</h2>
  <p>{E(z["plan"])}</p>{fare}

  <section class="faq">
    <h2>{E(w["h_faq"])}</h2>{faq}
    <details><summary>{E(w["free_q"])}</summary><p>{E(w["free_a"])}</p></details>
  </section>

{cta}

  <p><a href="cities.html">{E(w["list_en"])}</a></p>
  <p class="note">{w["disclaimer"].format(endorse=E(z["endorse"]))}</p>

{foot}
</div>
</body>
</html>
"""
    (ROOT / path).write_text(head(z["title"], z["desc"], path, image, ld, lang=hl, alts=lang_alts(c), nav=nav) + body, encoding="utf-8")
    return path


# Counted on 15 Nov 2026 from the app's feed list: feeds that sent vehicles at least once and that the app shows
# (lib/worldtransit.mjs HIDDEN_FEEDS, lists 1 to 3, are out). France has the 4 French networks that the catalogue files
# under Germany and Belgium; India is the Delhi feed. Count again when a hidden feed comes back.
WORLD = [
    ("France", 146, "Bordeaux (TBM), Rennes (STAR), Montpellier (TaM), Nice (Lignes d'Azur), Rouen (Astuce), Toulon (Mistral), Angers (Irigo), Brest (Bibus), Dijon (Divia), Metz (Le Met'), Tours (Fil Bleu), Le Havre (LiA), and networks on Réunion and Martinique"),
    ("United States", 128, "King County Metro (Seattle), MARTA (Atlanta), Valley Metro (Phoenix), the Long Island Rail Road, Austin (Texas), GoDurham and Chapel Hill Transit (North Carolina)"),
    ("Japan", 52, "Toyama (trams and buses), Takaoka (Manyosen tram), Kumamoto (four bus companies), Mie Kotsu buses, Nagano and Aomori city buses"),
    ("Canada", 49, "Edmonton, Halifax, York Region, Hamilton, Guelph, Kingston, Thunder Bay, Durham Region, Waterloo Region (Grand River Transit), and more than 30 BC Transit systems (Victoria, Kelowna, Kamloops, Nanaimo, Whistler)"),
    ("Poland", 4, "Warsaw, Poznań, Szczecin and Ełk"),
    ("Spain", 4, "Renfe Cercanías commuter trains, Metro Bilbao and Málaga (EMT)"),
    ("Sweden and Norway", 3, "Vy and Go-Ahead services"),
    ("Ukraine", 1, "Kyiv"),
    ("Portugal", 1, "the Lisbon region (Carris Metropolitana)"),
    ("Czechia", 1, "Prague (PID)"),
    ("Bulgaria", 1, "Sofia"),
    ("Sri Lanka", 1, "Colombo (Lanka Metro Transit)"),
    ("India", 1, "Delhi buses"),
]


def cities_page():
    path = "cities.html"
    title = "Cities with live public transport on the map | Wayaroo"
    desc = "Where Wayaroo shows buses, trains, trams and ferries live: Australian cities, Kumamoto, Toyama and Mie in Japan, Edmonton, Victoria and Halifax in Canada."
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Cities with live public transport in Wayaroo", "url": f"https://wayaroo.com/{path}",
          "isPartOf": {"@id": "https://wayaroo.com/#website"}, "about": {"@id": "https://wayaroo.com/#app"}, "inLanguage": "en-AU", "dateModified": SNAP_ISO}
    rows = ""
    for c in [x for x in LISTED if x.get("country", "Australia") == "Australia"]:
        live = ", ".join(label[0].upper() + label[1:] if i == 0 else label for i, (label, _) in enumerate(c["counts"]))
        rows += f'<tr><td><a href="{c["slug"]}.html"><b>{E(c["name"])}</b></a><br><span class="note">{E(c["region"])}</span></td><td>{E(live)}</td><td>{n(sum(v for _, v in c["counts"]))}<span class="unit"> vehicles</span></td><td><a href="{view_link(c)}">Open the map</a></td></tr>'
    far = [x for x in LISTED if x.get("country", "Australia") != "Australia"]
    far_rows = "".join(f'<tr><td><a href="{c["slug"]}.html"><b>{E(c["name"])}</b></a><br><span class="note">{E(c["region"])}</span></td><td>{E(join_counts(c["counts"]))}</td><td>{E(c.get("snap", SNAP))}</td></tr>' for c in far)
    far_html = (f'''
  <h3>City pages in other countries</h3>
  <div class="tablewrap"><table class="facts wide"><thead><tr><th>City</th><th>Live on the map</th><th>Checked</th></tr></thead><tbody>{far_rows}</tbody></table></div>''' if far else "")
    total_world = sum(x[1] for x in WORLD)
    world = "".join(f"<tr><td><b>{E(country)}</b></td><td>{k}<span class=\"unit\"> {'operator' if k == 1 else 'operators'}</span></td><td>{E(ex)}</td></tr>" for country, k, ex in WORLD)
    body = f'''
  <p class="note"><a href="index.html">Wayaroo</a> › Cities</p>
  <h1>Where Wayaroo shows public transport live</h1>
  <p>Wayaroo puts buses, trains, trams and ferries on the map where the operator publishes an open live feed. This page lists the places, with what was on the map at the time of the check. A place with no open live feed is not on the list, and this page says so.</p>

  <h2>Australia</h2>
  <div class="tablewrap"><table class="facts wide"><thead><tr><th>City</th><th>Live on the map</th><th>Vehicles</th><th></th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="note">Vehicles on the map on {SNAP}. The numbers change through the day. Regional Victoria (Geelong, Ballarat, Bendigo), Newcastle, Wollongong and the Sunshine Coast are live too: they are on the pages of Melbourne, Sydney and Brisbane.</p>

  <h3>Not live yet</h3>
  <ul class="plain">
    <li><b>Perth:</b> Wayaroo shows stops and timetable times. There are no live positions, because Wayaroo has no open live feed for Perth.</li>
    <li><b>Hobart and Darwin:</b> no live positions yet.</li>
    <li><b>Queensland (Brisbane, Gold Coast, Sunshine Coast, Cairns, Townsville):</b> paused since 16 November 2026. Translink's open-data terms ask for an indemnity, and Wayaroo has asked Translink for permission without it.</li>
    <li><b>New Zealand:</b> no live positions yet.</li>
  </ul>
  <p class="note">Everywhere in Australia, Wayaroo also gives directions by car, bike or on foot, public toilets, the weather and places near you.</p>

  <h2>Other countries</h2>
  <p>Outside Australia, Wayaroo reads the open live feeds of about {round(total_world, -1)} transport operators in {len(WORLD)} countries. Wayaroo checks each feed, and shows a city only when its feed sent vehicles in the last two weeks.</p>
  <div class="tablewrap"><table class="facts wide"><thead><tr><th>Country</th><th>Operators</th><th>For example</th></tr></thead><tbody>{world}</tbody></table></div>{far_html}
  <p class="note">Checked on 15 November 2026. The list changes each week.</p>
  <p><a class="badge go" href="{APP}?view=15,35,1.8&layers=transitcities&modes=rtbf">Open the world map of cities with live vehicles</a></p>

{CTA}

  <p class="note">Wayaroo is an independent app from Ozrsym Pty Ltd. The transport operators do not run or endorse it. Live positions and times come from each operator's own open feed. They can be late or wrong. Always check the sign at the stop. Full list of sources: <a href="credits.html">data credits</a>.</p>

{FOOT}
</div>
</body>
</html>
'''
    (ROOT / path).write_text(head(title, desc, path, "img/share-card.jpg", ld) + body, encoding="utf-8")  # 1200 x 630, for link cards
    return path



PAUSE_EN = ("Since 16 November 2026, Wayaroo does not show Translink's buses, trains, trams and ferries in Queensland. Translink's "
            "open-data terms ask each app to give the State a release and indemnity, and to ask the same of its users. Wayaroo does "
            "not give that promise, so it has asked Translink for permission to use the data without it.")
PAUSE_ZH = ("自 2026 年 11 月 16 日起，Wayaroo 不再显示昆士兰州 Translink 的公交车、火车、电车和渡轮。Translink 的开放数据条款要求每个应用"
            "向州政府作出免责和赔偿承诺，并要求其用户也作出同样的承诺。Wayaroo 不作出这一承诺，因此已向 Translink 申请在没有该条款的情况下使用数据的许可。")


def paused_page(c):
    """A city whose operator's data Wayaroo does not show now (PAUSED)."""
    path = f"{c['slug']}.html"
    title = f"{c['name']}: live public transport paused | Wayaroo"
    desc = f"Live buses, trains and ferries in {c['name']} are paused in Wayaroo while Wayaroo asks Translink for permission. Directions, toilets and the weather still work."
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": f"https://wayaroo.com/{path}", "isPartOf": {"@id": "https://wayaroo.com/#website"},
          "about": {"@id": "https://wayaroo.com/#app"}, "inLanguage": "en-AU", "dateModified": "2026-11-16"}
    body = f'''
  <p class="note"><a href="index.html">Wayaroo</a> › <a href="cities.html">Cities</a> › {E(c["name"])}</p>
  <h1>{E(c["name"])}: live public transport is paused</h1>
  <p>{E(PAUSE_EN)}</p>
  <p>In {E(c["name"])}, Wayaroo still gives directions by car, bike or on foot, public toilets, the weather and places near you.</p>
  <p class="note">For timetables and live times in Queensland, use Translink's own website and app.</p>
  <p><a href="cities.html">Cities with live public transport</a></p>

{CTA}

{FOOT}
</div>
</body>
</html>
'''
    (ROOT / path).write_text(head(title, desc, path, "img/share-card.jpg", ld) + body, encoding="utf-8")
    return path


def paused_page_zh(c):
    path = f"{c['slug']}-zh.html"
    name = c["zh"]["name"]
    title = f"{name}：实时公共交通已暂停 | Wayaroo"
    desc = f"Wayaroo 暂停显示{name}的实时公交、火车和渡轮，正在向 Translink 申请许可。导航、厕所和天气仍可使用。"
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": f"https://wayaroo.com/{path}", "isPartOf": {"@id": "https://wayaroo.com/#website"},
          "about": {"@id": "https://wayaroo.com/#app"}, "inLanguage": "zh-Hans", "dateModified": "2026-11-16"}
    body = f'''
  <p class="note"><a href="index.html">Wayaroo</a> › <a href="cities.html">城市</a> › {E(name)} · <a href="{c["slug"]}.html" lang="en" hreflang="en">English</a></p>
  <h1>{E(name)}：实时公共交通已暂停</h1>
  <p>{E(PAUSE_ZH)}</p>
  <p>在{E(name)}，Wayaroo 仍提供驾车、骑行和步行导航、公共厕所、天气和附近地点。</p>
  <p class="note">如需昆士兰州的时刻表和实时信息，请使用 Translink 的官方网站和应用。</p>

{ZH_CTA}

{ZH_FOOT}
</div>
</body>
</html>
'''
    (ROOT / path).write_text(head(title, desc, path, "img/share-card.jpg", ld, lang="zh-Hans", nav=ZH_NAV) + body, encoding="utf-8")
    return path


if __name__ == "__main__":
    made = [paused_page(c) if c["slug"] in PAUSED else city_page(c) for c in CITIES] + [city_page_ja(c) for c in CITIES if c.get("ja")] + [paused_page_zh(c) if c["slug"] in PAUSED else city_page_zh(c) for c in CITIES if c.get("zh")] + [city_page_tr(c, k) for k in TR for c in CITIES if c.get(k)] + [cities_page()]
    print("wrote", ", ".join(made))

# App Store links: the store of the page's country when the app is on sale there (Japan, Canada), else Australia.
# A link with no country opens Apple's United States store on a computer, where Wayaroo is not on sale (404).
STORE_CC = {"Japan": "jp", "Canada": "ca"}
for _c in CITIES:
    _cc = STORE_CC.get(_c.get("country", "Australia"))
    if not _cc:
        continue
    for _path in (f'{_c["slug"]}.html', f'{_c["slug"]}-ja.html'):
        _f = ROOT / _path
        if _f.exists():
            _f.write_text(_f.read_text(encoding="utf-8").replace("apps.apple.com/au/app/", f"apps.apple.com/{_cc}/app/"), encoding="utf-8")
