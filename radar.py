#!/usr/bin/env python3
"""Recipe SEO Radar FREE: public suggestions + cautious, evidence-aware screening."""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
DATA_DIR = ROOT / "data"
USER_AGENT = "Mozilla/5.0 (compatible; RecipeSEORadarFree/1.0; keyword research)"
SEEDS = [
    "cranberry coffee", "pumpkin soup", "turkey meatballs", "apple cider dessert",
    "white bean soup", "cabbage noodles", "butter bean recipes", "sweet potato breakfast",
    "lemon chicken soup", "cottage cheese breakfast", "carrot salad", "corn casserole",
    "rice paper dessert", "air fryer potatoes", "miso noodles", "pumpkin coffee",
    "crispy rice salad", "hot honey chicken", "baked oats", "potato leek soup",
    "ginger chicken", "no bake cheesecake", "cranberry appetizer", "rice pudding",
    "high protein soup", "salmon rice bowl", "oven baked tacos", "korean rice cake",
    "chocolate chia pudding", "holiday mocktail", "roasted cabbage", "pear dessert",
    "cornflake cookies", "eggplant pasta", "mushroom stroganoff", "miso butter noodles",
    "lentil soup", "green bean casserole", "roasted carrots", "turkey chili",
    "gingerbread dessert", "cinnamon roll", "healthy hot chocolate", "chicken pot pie",
    "shakshuka", "baked sweet potato", "rice paper rolls", "roasted cauliflower",
    "tomato soup", "homemade granola", "chicken salad", "chickpea curry",
    "chicken and dumplings", "sourdough discard", "spicy noodles", "matcha dessert",
    "savory oatmeal", "greek yogurt dessert", "apple bread", "cranberry cookies",
    "breakfast casserole", "baked feta", "garlic parmesan potatoes", "ground turkey bowl",
    "tortellini soup", "one pot pasta", "coconut curry", "beans on toast",
    "spinach soup", "pear salad", "stuffed dates", "pumpkin brownies",
    "maple cookies", "dumpling bake", "sweet potato noodles", "egg drop soup",
    "smashed broccoli", "rotisserie chicken soup", "no water chicken soup",
    "roasted chickpeas", "blueberry breakfast", "apple cinnamon oatmeal",
    "holiday dip", "potato soup", "green chicken pozole", "tahini noodles"
]
FOOD_HINTS = [
    "recipe", "soup", "cookie", "cake", "salad", "chicken", "turkey", "noodle",
    "pasta", "rice", "cabbage", "pumpkin", "potato", "bean", "dessert", "butter",
    "chocolate", "oat", "coffee", "bake", "miso", "curry", "taco", "bread",
    "pudding", "dip", "casserole", "egg", "salmon", "feta", "chickpea",
    "sauce", "carrot", "cranberry", "smoothie", "breakfast", "apple",
    "ginger", "mocktail", "cheesecake", "granola", "corn", "mushroom",
    "spinach", "yogurt", "lemon", "stew", "toast", "lentil", "dates",
    "cauliflower", "broccoli", "dumpling", "pear", "bowl", "honey"
]
PORK_TERMS = [
    "pork", "bacon", "ham", "prosciutto", "pancetta", "lard", "guanciale",
    "chorizo", "salami", "pepperoni", "carnitas", "pig", "porchetta",
    "pulled pork", "pork sausage", "soppressata", "mortadella"
]
NON_RECIPE = [
    "near me", "restaurant", "store near", "where to buy", "amazon",
    "price", "calories in", "nutrition facts", "brand review",
    "delivery", "recall", "outbreak", "stock", "menu prices"
]


def norm(value: str) -> str:
    return " ".join(re.sub(r"\s+", " ", value.strip().lower()).split())


def matches_phrase(value: str, term: str) -> bool:
    return bool(re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", value))


def acceptable(value: str) -> bool:
    q = norm(value)
    if not 2 <= len(q.split()) <= 10 or len(q) > 105:
        return False
    if any(matches_phrase(q, word) for word in PORK_TERMS):
        return False
    if any(x in q for x in NON_RECIPE):
        return False
    return any(word in q for word in FOOD_HINTS)


def fetch(url: str, timeout: int = 12) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(600_000)


def autocomplete(seed: str) -> list[str]:
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "hl": "en", "gl": "us", "q": seed}
    )
    try:
        obj = json.loads(fetch(url).decode("utf-8", errors="replace"))
        if isinstance(obj, list) and len(obj) > 1 and isinstance(obj[1], list):
            return [str(x) for x in obj[1] if isinstance(x, str)]
    except (OSError, ValueError, IndexError, TypeError) as exc:
        print("Autocomplete indisponible:", seed, type(exc).__name__)
    return []


def trending_now_us() -> list[str]:
    url = "https://trends.google.com/trending/rss?geo=US"
    try:
        root = ET.fromstring(fetch(url))
        items = [n.text or "" for n in root.findall(".//channel/item/title")]
        return [x for x in items if acceptable(x)]
    except (OSError, ET.ParseError) as exc:
        print("RSS Google Trends indisponible:", type(exc).__name__)
    return []


def bing_rss_screen(keyword: str) -> dict:
    """Exploratory Bing titles only: NOT a Google USA SERP check."""
    query = '"' + keyword + '" recipe'
    url = "https://www.bing.com/search?" + urllib.parse.urlencode(
        {"q": query, "format": "rss", "setlang": "en-US"}
    )
    try:
        root = ET.fromstring(fetch(url))
        items = []
        for item in root.findall(".//channel/item")[:8]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if title and link.startswith("http"):
                items.append({"title": title, "url": link})
        full = norm(keyword)
        exact = sum(full in norm(item["title"]) for item in items)
        return {"results": items, "exact_title_count": exact, "source": "Bing RSS"}
    except (OSError, ET.ParseError) as exc:
        print("Bing RSS indisponible:", keyword, type(exc).__name__)
    return {"results": [], "exact_title_count": None, "source": "indisponible"}


def classify_trend(values: list[int]) -> tuple[str, str]:
    """Relative 90-day signal; never infer absolute volume or organic KD."""
    if len(values) < 42 or sum(v > 0 for v in values) < 15:
        return "Signal insuffisant", "Données trop clairsemées"
    recent = values[-14:]
    previous = values[-56:-14]
    mean_recent = sum(recent) / len(recent)
    mean_previous = sum(previous) / len(previous)
    if (sum(x > 0 for x in recent) >= 8
            and mean_recent >= 12
            and mean_recent >= 1.4 * max(mean_previous, 1)
            and max(recent) / max(sum(recent), 1) < 0.30):
        return "Rising 90j", "Indice récent {:.1f} vs précédent {:.1f}".format(
            mean_recent, mean_previous
        )
    if (sum(x > 0 for x in values) >= 55
            and mean_previous >= 8
            and 0.7 <= mean_recent / max(mean_previous, 1) <= 1.3):
        return "Stable 90j", "Stable sur 90j ; evergreen annuel NON prouvé"
    return "Non confirmé", "Aucune hausse soutenue démontrée"


def trends_90d(keyword: str, client: object) -> tuple[str, str]:
    if client is None:
        return "Non vérifié", "Source pytrends non accessible"
    try:
        client.build_payload([keyword], timeframe="today 3-m", geo="US")
        frame = client.interest_over_time()
        if frame is None or frame.empty or keyword not in frame.columns:
            return "Signal insuffisant", "Graphique Google Trends indisponible"
        return classify_trend([int(x) for x in frame[keyword].tolist()])
    except Exception as exc:
        print("Google Trends non disponible:", keyword, type(exc).__name__)
        return "Non vérifié", "Appel Google Trends échoué"


def safe_md(value: str) -> str:
    return str(value).replace("|", "/").replace("\n", " ").replace("\r", " ")


def safe_csv(value: str) -> str:
    s = str(value)
    return "'" + s if s.startswith(("=", "+", "-", "@")) else s


def load_seen() -> dict:
    path = DATA_DIR / "seen.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
    return {}


def explore(today: datetime, max_candidates: int) -> tuple[list[dict], dict]:
    randomizer = random.Random(today.date().toordinal())
    shuffled = SEEDS[:]
    randomizer.shuffle(shuffled)
    selected = shuffled[:16]
    breaking = trending_now_us()
    selected.extend(breaking[:4])
    print("Seeds explorés:", ", ".join(selected))
    seen = load_seen()
    found: dict[str, dict] = {}
    source_attempts = 0

    for base in selected:
        probes = [base, base + " recipe", base + " with", base + " without"]
        for probe in probes:
            source_attempts += 1
            for suggestion in autocomplete(probe):
                phrase = norm(suggestion)
                if acceptable(phrase):
                    found.setdefault(phrase, {"keyword": phrase, "seed": base})
            time.sleep(0.8)

    for base in breaking:
        if acceptable(base):
            found.setdefault(norm(base), {"keyword": norm(base), "seed": "Google Trends RSS"})

    # Prevent repeats unless the pool is too small, and disclose selection rules.
    cutoff = today.date() - timedelta(days=21)
    fresh = []
    for row in found.values():
        previous = seen.get(row["keyword"])
        if previous:
            try:
                if datetime.fromisoformat(previous).date() >= cutoff:
                    continue
            except ValueError:
                pass
        fresh.append(row)

    def pre_score(row: dict) -> float:
        kw = row["keyword"]
        length = len(kw.split())
        specificity = 10 if 3 <= length <= 7 else 3
        food_intent = 6 if "recipe" in kw or "how to make" in kw else 3
        trend_seed = 8 if row["seed"] == "Google Trends RSS" else 0
        return specificity + food_intent + trend_seed - abs(length - 5) * 0.7

    fresh.sort(key=lambda x: (pre_score(x), x["keyword"]), reverse=True)
    # Diversify by food family: avoid many near-identical keywords.
    candidates = []
    selected_seeds = set()
    for item in fresh:
        seed_name = item["seed"]
        if seed_name in selected_seeds:
            continue
        selected_seeds.add(seed_name)
        candidates.append(item)
        if len(candidates) >= max_candidates:
            break
    try:
        from pytrends.request import TrendReq
        trends_client = TrendReq(hl="en-US", tz=300, retries=0)
    except Exception as exc:
        print("pytrends non disponible:", type(exc).__name__)
        trends_client = None

    trending_failed = 0
    for row in candidates:
        if trends_client is None or trending_failed >= 3:
            row["trend"], row["trend_note"] = "Non vérifié", "pytrends indisponible/limité"
        else:
            row["trend"], row["trend_note"] = trends_90d(row["keyword"], trends_client)
            if row["trend"] == "Non vérifié":
                trending_failed += 1
            time.sleep(2)
        # Bing RSS returned country / encyclopaedia pages for recipe queries.
        # Do not use this as evidence of weak Google organic competition.
        row["bing"] = {"results": [], "exact_title_count": None, "source": "Non évalué"}
        row["serp_note"] = "Google USA Top 10 : non vérifié"
        row["score"] = pre_score(row)
        row["score"] += 35 if row["trend"] == "Rising 90j" else 12 if row["trend"] == "Stable 90j" else 0
        row["decision"] = "Priorité recherche approfondie" if row["trend"] == "Rising 90j" else "À confirmer"
        row["google_trends_url"] = (
            "https://trends.google.com/trends/explore?"
            + urllib.parse.urlencode({"date": "today 3-m", "geo": "US", "q": row["keyword"]})
        )
    candidates.sort(key=lambda x: (x["score"], x["keyword"]), reverse=True)
    final = candidates[:10]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for row in final:
        seen[row["keyword"]] = today.date().isoformat()
    # retain one year of compact history
    seen = {k: v for k, v in seen.items()
            if isinstance(v, str) and v >= (today.date() - timedelta(days=365)).isoformat()}
    (DATA_DIR / "seen.json").write_text(
        json.dumps(seen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return final, {
        "seeds": len(selected), "autocomplete_probes": source_attempts,
        "suggestion_candidates": len(found), "new_candidates": len(fresh),
        "trends_rss_food": len(breaking)
    }


def write_reports(today: datetime, rows: list[dict], stats: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORT_DIR / "latest.csv"
    fields = [
        "date", "keyword", "trend_90d", "trend_evidence", "screening_source",
        "bing_exact_titles", "screening_note", "us_volume", "organic_kd",
        "decision", "google_trends_url", "competitor_urls"
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: safe_csv(v) for k, v in {
                "date": today.date().isoformat(), "keyword": row["keyword"],
                "trend_90d": row["trend"], "trend_evidence": row["trend_note"],
                "screening_source": row["bing"]["source"],
                "bing_exact_titles": row["bing"]["exact_title_count"]
                    if row["bing"]["exact_title_count"] is not None else "non vérifié",
                "screening_note": row["serp_note"],
                "us_volume": "non vérifié", "organic_kd": "non vérifié",
                "decision": row["decision"], "google_trends_url": row["google_trends_url"],
                "competitor_urls": "; ".join(
                    c["url"] for c in row["bing"]["results"][:3])
            }.items()})

    lines = [
        "# Recipe SEO Radar FREE — " + today.strftime("%Y-%m-%d %H:%M"),
        "",
        "Marché : Google USA / English. Toutes catégories de recettes, sans porc.",
        "",
        "**Attention :** Autocomplete = idées, non volumes. Google Trends = indice relatif. "
        "Les éventuels résultats Bing ne représentent pas un classement Google. "
        "**Volume USA, KD, Top 10 Google : non vérifiés.**",
        "",
        "## Recherche exécutée",
        "Seeds : {seeds} ; requêtes Autocomplete : {autocomplete_probes} ; "
        "suggestions uniques : {suggestion_candidates} ; nouvelles candidates : "
        "{new_candidates} ; sujets food RSS : {trends_rss_food}.".format(**stats),
        "",
        "## Suggestions diversifiées à valider (non classées par KD SEO)",
        "",
        "| # | Keyword exact | Trend USA 90j | Pré-analyse concurrence | Décision |",
        "|---|---|---|---|---|"
    ]
    for ix, row in enumerate(rows, 1):
        lines.append("| {i} | {kw} | {tr} | {sr} | {de} |".format(
            i=ix, kw=safe_md(row["keyword"]), tr=safe_md(row["trend"]),
            sr=safe_md(row["serp_note"]), de=safe_md(row["decision"])))
    if not rows:
        lines.append("| — | Aucune nouvelle piste exploitable (ou sources indisponibles) | — | — | — |")
    lines.extend(["", "## Sources et recherches à approfondir", ""])
    for ix, row in enumerate(rows, 1):
        lines.append("### {}. {}".format(ix, safe_md(row["keyword"])))
        lines.append("- Google Trends USA : " + row["google_trends_url"])
        lines.append("- Signal : {} — {}".format(row["trend"], row["trend_note"]))
        lines.append("- Pré-analyse : " + row["serp_note"])
        for competitor in row["bing"]["results"][:3]:
            lines.append("- Résultat **Bing (pas Google)** : {} — {}".format(
                safe_md(competitor["title"]), competitor["url"]))
        lines.append("")
    lines.extend([
        "## Comment valider avant de publier",
        "",
        "1. Confirmer le sujet avec Google Trends USA et la demande exacte ou par groupe d'intentions.",
        "2. Examiner manuellement les 10 vrais résultats organiques Google USA (Top 3 en profondeur).",
        "3. Vérifier que les résultats existants ne satisfont pas déjà la même intention.",
        "4. Vérifier la recette, les ingrédients sans porc, les gaps culinaires et l'originalité.",
        "5. Si aucun signal de tendance ou de demande n'est vérifiable, ne pas affirmer KD 0 ni trafic attendu.",
        ""
    ])
    (REPORT_DIR / "latest.md").write_text("\n".join(lines), encoding="utf-8")
    print("Rapports créés :", csv_path, REPORT_DIR / "latest.md")


def self_test() -> None:
    assert acceptable("miso cabbage noodles recipe")
    assert not acceptable("pork belly cabbage noodle recipe")
    assert not acceptable("bacon soup recipe")
    assert not acceptable("chicken restaurant near me")
    values = [20] * 65 + [60] * 25
    assert classify_trend(values)[0] == "Rising 90j"
    assert classify_trend([40] * 90)[0] == "Stable 90j"
    assert classify_trend([0] * 89 + [100])[0] == "Signal insuffisant"
    print("Self-test OK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--max-candidates", type=int, default=18)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    now = datetime.now(ZoneInfo("Africa/Casablanca"))
    rows, stats = explore(now, max(5, min(args.max_candidates, 35)))
    write_reports(now, rows, stats)


if __name__ == "__main__":
    main()
