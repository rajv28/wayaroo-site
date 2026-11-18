/* Wayaroo store links (18 Nov 2026, Rajbir: "Based on the system they should get option from the top to download app").
   - iPhone and iPad: the App Store badge first, the Google Play badge hidden; Android: the other way round; a computer: both.
   - On a phone, a bar at the top of the page with the store of that phone (close it with x; it stays closed for 14 days).
   - Under the first store badges, a line to rate Wayaroo in the store (no reward and no "give 5 stars": the store rules).
   Nothing is sent anywhere; the closed bar is kept only in this browser. */
(function () {
  var base = (document.currentScript && document.currentScript.src) || location.href;
  var at = function (f) { try { return new URL(f, base).href; } catch (e) { return f; } };
  var ua = navigator.userAgent || "";
  var ios = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  var android = !ios && /Android/i.test(ua);
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

  // 3. The bar at the top, on a phone only
  if (!ios && !android) return;
  try { var t = Number(localStorage.getItem("wayaroo.appbar") || 0); if (t && Date.now() - t < 14 * 864e5) return; } catch (e) {}
  var bar = document.createElement("div"); bar.className = "appbar"; bar.setAttribute("role", "region"); bar.setAttribute("aria-label", "Wayaroo app");
  var x = document.createElement("button"); x.type = "button"; x.className = "x"; x.setAttribute("aria-label", w.close); x.textContent = "×";
  x.addEventListener("click", function () { bar.remove(); try { localStorage.setItem("wayaroo.appbar", String(Date.now())); } catch (e) {} });
  var icon = document.createElement("img"); icon.src = at("apple-touch-icon.png"); icon.alt = ""; icon.width = 40; icon.height = 40;
  var txt = document.createElement("div"); txt.className = "t";
  var nm = document.createElement("b"); nm.textContent = "Wayaroo"; var sb = document.createElement("span"); sb.textContent = w.sub;
  txt.appendChild(nm); txt.appendChild(sb);
  var src = document.querySelector(ios ? "a.store.ios" : "a.store.android");
  var go = document.createElement("a"); go.className = "store"; go.href = ios ? APPLE : PLAY;
  var gi = document.createElement("img");
  if (src && src.querySelector("img")) { gi.src = src.querySelector("img").getAttribute("src"); gi.alt = src.querySelector("img").alt; }
  else { gi.src = at(ios ? "img/badges/app-store-en.svg" : "img/badges/google-play-en.png"); gi.alt = ios ? "Download on the App Store" : "Get it on Google Play"; }
  gi.height = 40; gi.width = ios ? 120 : 134; go.appendChild(gi);
  bar.appendChild(x); bar.appendChild(icon); bar.appendChild(txt); bar.appendChild(go);
  document.body.insertBefore(bar, document.body.firstChild);
})();
