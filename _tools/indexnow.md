# IndexNow

IndexNow tells Bing and the other search engines that use it (Yandex, Seznam, Naver, Yep) that a page is new or changed.
Rajbir said yes on 13 Nov 2026.

- The key file is `c503f2473bdb5357635f236f4f0a3f78.txt` in the root of the site. Its text is the key. The key is public by design: it only proves
  that the sender controls wayaroo.com. Do not remove the file.
- After a page is new or changed, open this address once for each page (a browser is enough):

      https://api.indexnow.org/indexnow?url=https://wayaroo.com/<page>&key=c503f2473bdb5357635f236f4f0a3f78

  An empty answer with status 200 or 202 means "received". 403 means the key file was not found; 422 means the address
  is not on wayaroo.com.
- Do not send a page that did not change. Google does not use IndexNow; it reads sitemap.xml.
