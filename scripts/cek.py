import json, os, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import date

KAYNAKLAR = {
    "Hürriyet": ["https://www.hurriyet.com.tr/rss/yazarlar"],
    "Sabah": ["https://www.sabah.com.tr/rss/Yazarlar.xml"],
    "Habertürk": ["https://www.haberturk.com/rss/yazarlar.xml"],
    "Milliyet": ["https://www.milliyet.com.tr/rss/rssnew/yazarlarrss.xml"],
    "Sözcü": ["https://www.sozcu.com.tr/feeds-rss-category-yazarlar"],
    "Cumhuriyet": ["https://www.cumhuriyet.com.tr/rss/yazarlar.xml"],
    "Karar": ["https://www.karar.com/rss/yazarlar"],
    "Yeni Şafak": ["https://www.yenisafak.com/rss?xml=yazarlar"],
    "BirGün": ["https://www.birgun.net/rss/yazarlar"],
    "Dünya": ["https://www.dunya.com/rss?dunya=yazarlar"],
}
DC = "{http://purl.org/dc/elements/1.1/}creator"

def indir(url):
    r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(r, timeout=30).read()

def tarih(s):
    try:
        return parsedate_to_datetime(s).date().isoformat()
    except Exception:
        return date.today().isoformat()

def oku(gazete, veri):
    sonuc = []
    for it in ET.fromstring(veri).iter("item"):
        baslik = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        yazar = (it.findtext("author") or it.findtext(DC) or "").strip()
        if not yazar and ":" in baslik[:40]:
            yazar, baslik = [x.strip() for x in baslik.split(":", 1)]
        if baslik and link:
            sonuc.append({"yazar": yazar or "Bilinmeyen", "gazete": gazete,
                          "baslik": baslik, "link": link,
                          "tarih": tarih(it.findtext("pubDate") or "")})
    return sonuc

os.makedirs("data", exist_ok=True)
try:
    eski = json.load(open("data/yazilar.json", encoding="utf-8"))
except Exception:
    eski = []
tum = {y["link"]: y for y in eski}
durum = []
for gazete, adresler in KAYNAKLAR.items():
    basarili = False
    for a in adresler:
        try:
            liste = oku(gazete, indir(a))
        except Exception:
            continue
        if liste:
            for y in liste:
                tum[y["link"]] = y
            durum.append(f"{gazete}: CALISTI, {len(liste)} yazi")
            basarili = True
            break
    if not basarili:
        durum.append(f"{gazete}: CALISMADI")

sirali = sorted(tum.values(), key=lambda y: y["tarih"], reverse=True)[:4000]
json.dump(sirali, open("data/yazilar.json", "w", encoding="utf-8"), ensure_ascii=False)
open("data/durum.txt", "w", encoding="utf-8").write("\n".join(durum))
