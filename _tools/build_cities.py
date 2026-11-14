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


def head(title, desc, path, image, ld):
    return f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-itunes-app" content="app-id=6831237478">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="https://wayaroo.com/{path}">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="stylesheet" href="site.css">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Wayaroo">
<meta property="og:title" content="{E(title.split(" | ")[0])}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="https://wayaroo.com/{path}">
<meta property="og:image" content="https://wayaroo.com/{image}">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
{ADS}
</head>
<body>
<div class="wrap">
{NAV}
'''


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
    others = " · ".join(f'<a href="{o["slug"]}.html">{E(o["name"])}</a>' for o in CITIES if o["slug"] != c["slug"])
    body = f'''
  <p class="note"><a href="index.html">Wayaroo</a> › <a href="cities.html">Cities</a> › {E(c["name"])}</p>
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
    <li><b>See your ride now.</b> Tap a vehicle to see its route, where it is going, its next stops and, when the operator sends a prediction, how late it is.</li>
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
    (ROOT / path).write_text(head(c["title"], c["desc"], path, image, ld) + body, encoding="utf-8")
    return path


WORLD = [
    ("United States", 148, "King County Metro (Seattle), MBTA (Boston), SEPTA (Philadelphia), MARTA (Atlanta), RTD (Denver), Capital Metro (Austin), Metro Transit (Minneapolis–Saint Paul), VIA (San Antonio), Valley Metro (Phoenix), the Long Island Rail Road and NYC Ferry"),
    ("France", 146, "Bordeaux (TBM), Montpellier (TaM), Nice (Lignes d'Azur), Rennes (STAR), Rouen (Astuce), Toulon (Mistral), Angers (Irigo), Brest (Bibus), Dijon (Divia), Metz (Le Met'), Tours (Fil Bleu), Le Havre (LiA), and networks on Réunion and Martinique"),
    ("Canada", 50, "Edmonton, Halifax, York Region, Mississauga (MiWay), Hamilton, Durham Region, Guelph, Kingston, Thunder Bay, and more than 30 BC Transit systems (Victoria, Kelowna, Kamloops, Nanaimo, Whistler)"),
    ("Japan", 48, "Toyama (trams and buses), Takaoka (Manyosen tram), Kumamoto (four bus companies), Mie Kotsu buses, Nagano and Aomori city buses"),
    ("Italy", 18, "Rome, Turin (GTT), Venice (ACTV buses and water buses), Bari (AMTAB), Tuscany (Autolinee Toscane), Modena, Reggio Emilia and Piacenza (SETA), Parma (TEP), Padua (Busitalia Veneto), Lazio (Cotral)"),
    ("Poland", 8, "Warsaw, Kraków, Poznań, Szczecin, Rzeszów and Ełk"),
    ("Spain", 7, "Renfe Cercanías commuter trains, Metro Bilbao, Málaga (EMT), Córdoba (AUCORSA) and Fuenlabrada"),
    ("Romania", 4, "the Bucharest region, Cluj-Napoca, Iași and Buzău"),
    ("Sweden and Norway", 3, "Vy and Go-Ahead services"),
    ("Portugal", 2, "Lisbon (Carris and Carris Metropolitana)"),
    ("Ukraine", 2, "Kyiv and Lviv"),
    ("Czechia", 1, "Prague (PID)"),
    ("Finland", 1, "Helsinki (HSL)"),
    ("Lithuania", 1, "Vilnius"),
    ("Bulgaria", 1, "Sofia"),
    ("Hungary", 1, "Orosháza"),
    ("Moldova", 1, "Chișinău"),
    ("Sri Lanka", 1, "Colombo (Lanka Metro Transit)"),
    ("India", 1, "Delhi buses"),
]


def cities_page():
    path = "cities.html"
    title = "Cities with live public transport on the map | Wayaroo"
    desc = "Where Wayaroo shows buses, trains, trams and ferries live: Melbourne, Sydney, Brisbane, Gold Coast, Adelaide, Canberra, Cairns, Kumamoto and 19 other countries."
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Cities with live public transport in Wayaroo", "url": f"https://wayaroo.com/{path}",
          "isPartOf": {"@id": "https://wayaroo.com/#website"}, "about": {"@id": "https://wayaroo.com/#app"}, "inLanguage": "en-AU", "dateModified": SNAP_ISO}
    rows = ""
    for c in [x for x in CITIES if x.get("country", "Australia") == "Australia"]:
        live = ", ".join(label[0].upper() + label[1:] if i == 0 else label for i, (label, _) in enumerate(c["counts"]))
        rows += f'<tr><td><a href="{c["slug"]}.html"><b>{E(c["name"])}</b></a><br><span class="note">{E(c["region"])}</span></td><td>{E(live)}</td><td>{n(sum(v for _, v in c["counts"]))}<span class="unit"> vehicles</span></td><td><a href="{view_link(c)}">Open the map</a></td></tr>'
    far = [x for x in CITIES if x.get("country", "Australia") != "Australia"]
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
    <li><b>New Zealand:</b> no live positions yet.</li>
  </ul>
  <p class="note">Everywhere in Australia, Wayaroo also gives directions by car, bike or on foot, public toilets, the weather and places near you.</p>

  <h2>Other countries</h2>
  <p>Outside Australia, Wayaroo reads the open live feeds of about {round(total_world, -1)} transport operators in {len(WORLD)} countries. Wayaroo checks each feed, and shows a city only when its feed sent vehicles in the last two weeks.</p>
  <div class="tablewrap"><table class="facts wide"><thead><tr><th>Country</th><th>Operators</th><th>For example</th></tr></thead><tbody>{world}</tbody></table></div>{far_html}
  <p class="note">Checked on 13 November 2026. The list changes each week.</p>
  <p><a class="badge go" href="{APP}?view=15,35,1.8&layers=transitcities&modes=rtbf">Open the world map of cities with live vehicles</a></p>

{CTA}

  <p class="note">Wayaroo is an independent app from Ozrsym Pty Ltd. The transport operators do not run or endorse it. Live positions and times come from each operator's own open feed. They can be late or wrong. Always check the sign at the stop. Full list of sources: <a href="credits.html">data credits</a>.</p>

{FOOT}
</div>
</body>
</html>
'''
    (ROOT / path).write_text(head(title, desc, path, "img/live-melbourne.jpg", ld) + body, encoding="utf-8")
    return path


if __name__ == "__main__":
    made = [city_page(c) for c in CITIES] + [cities_page()]
    print("wrote", ", ".join(made))
