/* Wayaroo store links (18 Nov 2026, Rajbir: "Based on the system they should get option from the top to download app").
   - iPhone and iPad: the App Store badge first, the Google Play badge hidden; Android: the other way round; a computer: both.
   - On a phone, a bar at the top of the page with the store of that phone (close it with x; it stays closed for 14 days).
   - Under the first store badges, a line to rate Wayaroo in the store (no reward and no "give 5 stars": the store rules).
   Nothing is sent anywhere; the closed bar is kept only in this browser. */
(function () {
  var base = (document.currentScript && document.currentScript.src) || location.href;
  var at = function (f) { try { return new URL(f, base).href; } catch (e) { return f; } };
  var ua = navigator.userAgent || "";
  var android = /Android/i.test(ua);
  var ios = !android && (/iPhone|iPad|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1));   // an iPad says "Macintosh"
  var lang = (document.documentElement.lang || "en").toLowerCase().split("-")[0];
  var W = {
    en: { sub: "Free · Live transport and fuel prices", close: "Close", rate: "Do you use Wayaroo? Rate it on ", ios: "the App Store", android: "Google Play", or: " or " },
    zh: { sub: "免费 · 实时公交、地图和油价", close: "关闭", rate: "在用 Wayaroo 吗？欢迎在 ", ios: "App Store", android: "Google Play", or: " 或 ", end: " 上评分" },
    ja: { sub: "無料 · ライブ交通、地図、燃料価格", close: "閉じる", rate: "Wayaroo をお使いですか？ ", ios: "App Store", android: "Google Play", or: " ・ ", end: " で評価してください" },
    vi: { sub: "Miễn phí · Giao thông trực tiếp, bản đồ, giá xăng", close: "Đóng", rate: "Bạn dùng Wayaroo? Hãy đánh giá trên ", ios: "App Store", android: "Google Play", or: " hoặc " },
    hi: { sub: "मुफ़्त · लाइव परिवहन, नक्शे और ईंधन", close: "बंद करें", rate: "क्या आप Wayaroo इस्तेमाल करते हैं? ", ios: "App Store", android: "Google Play", or: " या ", end: " पर रेटिंग दें" },
    pa: { sub: "ਮੁਫ਼ਤ · ਲਾਈਵ ਆਵਾਜਾਈ, ਨਕਸ਼ੇ ਅਤੇ ਤੇਲ", close: "ਬੰਦ ਕਰੋ", rate: "ਕੀ ਤੁਸੀਂ Wayaroo ਵਰਤਦੇ ਹੋ? ", ios: "App Store", android: "Google Play", or: " ਜਾਂ ", end: " ਉੱਤੇ ਰੇਟਿੰਗ ਦਿਓ" }
  };
  var w = W[lang] || W.en;
  var APPLE = "https://apps.apple.com/au/app/wayaroo-maps-transport/id6831237478";
  var PLAY = "https://play.google.com/store/apps/details?id=com.wayaroo.app";
  var first = document.querySelector("a.store.ios"); if (first) APPLE = first.href.split("?")[0];

  // 1. The store of this phone first; the other store hidden on a phone
  var boxes = document.querySelectorAll(".herobtns, .ctabtns");
  for (var i = 0; i < boxes.length; i++) {
    var b = boxes[i], a = b.querySelector("a.store.ios"), g = b.querySelector("a.store.android");
    if (android && g && a) b.insertBefore(g, b.firstChild);
    if (ios && g) g.hidden = true;
    if (android && a) a.hidden = true;
  }

  // 2. A line to rate the app, under the first group of store badges
  var top = document.querySelector(".herobtns, .ctabtns");
  if (top && top.querySelector("a.store")) {
    var p = document.createElement("p"); p.className = "rate";
    var link = function (href, text) { var x = document.createElement("a"); x.href = href; x.textContent = text; x.rel = "noopener"; return x; };
    p.appendChild(document.createTextNode("★★★★★ " + w.rate));
    if (!android) p.appendChild(link(APPLE + "?action=write-review", w.ios));
    if (!ios && !android) p.appendChild(document.createTextNode(w.or));
    if (!ios) p.appendChild(link(PLAY + "&showAllReviews=true", w.android));
    p.appendChild(document.createTextNode(w.end || "."));
    var host = top.closest("p") || top;
    host.parentNode.insertBefore(p, host.nextSibling);
  }

  // 3. The bar at the top, on a phone only, in the look of Apple's own Smart App Banner (Rajbir, 18 Nov 2026: "that is good").
  // Safari on iPhone and iPad shows Apple's own banner (the apple-itunes-app tag of each page): then this bar is not shown.
  if (!ios && !android) return;
  var safari = ios && /Safari\//.test(ua) && !/CriOS|FxiOS|EdgiOS|OPiOS|GSA\/|FBAN|FBAV|Instagram|Line\/|Snapchat|DuckDuckGo|YaBrowser|Brave/.test(ua);
  if (safari) return;
  try { var t = Number(localStorage.getItem("wayaroo.appbar") || 0); if (t && Date.now() - t < 14 * 864e5) return; } catch (e) {}
  var S = { en: ["Live buses, trains and trams · Free", "Download"], zh: ["实时公交、火车和电车 · 免费", "下载"], ja: ["バス・電車・トラムをライブで · 無料", "ダウンロード"],
    vi: ["Xe buýt, tàu, xe điện trực tiếp · Miễn phí", "Tải về"], hi: ["लाइव बसें, ट्रेनें और ट्राम · मुफ़्त", "डाउनलोड"], pa: ["ਲਾਈਵ ਬੱਸਾਂ, ਰੇਲਾਂ ਅਤੇ ਟਰਾਮਾਂ · ਮੁਫ਼ਤ", "ਡਾਊਨਲੋਡ"] }[lang] || ["Live buses, trains and trams · Free", "Download"];
  var NS = "http://www.w3.org/2000/svg";
  var svg = function (d, cls) { var e = document.createElementNS(NS, "svg"); e.setAttribute("viewBox", "0 0 24 24"); e.setAttribute("aria-hidden", "true"); if (cls) e.setAttribute("class", cls); d.forEach(function (x) { var q = document.createElementNS(NS, "path"); q.setAttribute("d", x); e.appendChild(q); }); return e; };
  var bar = document.createElement("div"); bar.className = "appbar"; bar.setAttribute("role", "region"); bar.setAttribute("aria-label", "Wayaroo app");
  var icon = document.createElement("img"); icon.src = at("apple-touch-icon.png"); icon.alt = ""; icon.width = 52; icon.height = 52;
  var txt = document.createElement("a"); txt.className = "t"; txt.href = ios ? APPLE : PLAY;
  var nm = document.createElement("b"); nm.textContent = ios ? "Wayaroo: Maps & Transport" : "Wayaroo: Live Transit & Maps";
  var sb = document.createElement("span"); sb.textContent = S[0];
  txt.appendChild(nm); txt.appendChild(sb);
  var go = document.createElement("a"); go.className = "get"; go.href = ios ? APPLE : PLAY;
  go.setAttribute("aria-label", S[1] + " · " + (ios ? "App Store" : "Google Play"));
  go.appendChild(svg(["M7 18h10.5a4.5 4.5 0 0 0 .6-8.96A6 6 0 0 0 6.4 8.1 5 5 0 0 0 7 18z", "M12 10v8", "M8.8 14.8 12 18l3.2-3.2"]));
  var x = document.createElement("button"); x.type = "button"; x.className = "x"; x.setAttribute("aria-label", w.close);
  x.appendChild(svg(["M7 7l10 10", "M17 7 7 17"]));
  x.addEventListener("click", function () { bar.remove(); try { localStorage.setItem("wayaroo.appbar", String(Date.now())); } catch (e) {} });
  bar.appendChild(icon); bar.appendChild(txt); bar.appendChild(go); bar.appendChild(x);
  document.body.insertBefore(bar, document.body.firstChild);
})();
