"""Builds one small card file per game for Flavored Cardboard from TCGCSV (https://tcgcsv.com), a free daily copy of
TCGplayer's card lists and prices. Runs nightly on GitHub Actions; standard library only.

Each cards/<game>.json is:
  {"updated": "...", "source": "...", "sets": [set names, newest first],
   "cards": [[name, set index, number, rarity, type, price, foil price, TCGplayer product id], ...]}
Prices are TCGplayer market prices in USD (mid price when there's no market price yet), 0 when unknown.
Sealed products (boxes, packs, decks) have no card number and are left out.
"""
import json, os, sys, time, urllib.request
from datetime import datetime, timezone

GAMES = {"onepiece": 68, "fab": 62, "digimon": 63, "dbs": 80, "swu": 79, "vanguard": 16, "weiss": 20, "unionarena": 81}
BASE = "https://tcgcsv.com/tcgplayer"
UA = "FlavoredCardboard-data/1.0 (+https://github.com/Shadowhammer717/flavored-cardboard-data)"
TYPE_KEYS = ("CardType", "Card Type", "Type", "Category")


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # network hiccups: wait and retry
            if i == tries - 1:
                raise
            print(f"  retry {url}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return None


def price(p):
    v = p.get("marketPrice") or p.get("midPrice") or 0
    return round(float(v), 2) if v else 0


def build(game, cat):
    groups = get(f"{BASE}/{cat}/groups")["results"]
    groups.sort(key=lambda g: g.get("publishedOn") or "", reverse=True)
    sets, cards = [], []
    for g in groups:
        gid = g["groupId"]
        products = get(f"{BASE}/{cat}/{gid}/products")["results"]
        time.sleep(0.25)
        prices = get(f"{BASE}/{cat}/{gid}/prices")["results"]
        time.sleep(0.25)
        normal, foil = {}, {}
        for p in prices:
            (foil if "foil" in (p.get("subTypeName") or "").lower() else normal)[p["productId"]] = price(p)
        rows = []
        for p in products:
            ext = {e.get("name"): e.get("value") for e in p.get("extendedData") or []}
            number = (ext.get("Number") or "").strip()
            if not number:
                continue
            ctype = next((ext[k] for k in TYPE_KEYS if ext.get(k)), "")
            pid = p["productId"]
            rows.append([p.get("name") or "", len(sets), number, ext.get("Rarity") or "", ctype,
                         normal.get(pid, 0), foil.get(pid, 0), pid])
        if rows:
            sets.append(g.get("name") or "")
            cards.extend(rows)
    return {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": "TCGplayer prices via TCGCSV (tcgcsv.com)", "sets": sets, "cards": cards}


def main():
    os.makedirs("cards", exist_ok=True)
    only = sys.argv[1:] or list(GAMES)
    failed = []
    for game in only:
        try:
            data = build(game, GAMES[game])
        except Exception as e:  # one game failing keeps yesterday's file for it
            print(f"{game}: FAILED {e}", file=sys.stderr)
            failed.append(game)
            continue
        with open(f"cards/{game}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        print(f"{game}: {len(data['cards'])} cards in {len(data['sets'])} sets")
    if len(failed) == len(only):
        sys.exit(1)


if __name__ == "__main__":
    main()
