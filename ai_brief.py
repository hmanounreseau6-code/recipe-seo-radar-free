#!/usr/bin/env python3
"""Create a Google AI Pro SERP audit prompt from Google Trends Rising queries."""
import argparse
import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "reports"
ANGLES = OUT / "angles.csv"
PROMPT = OUT / "google-ai-pro-prompt.md"


def get_angles(path):
    if not path.exists():
        return []
    data, seen = [], set()
    with path.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            if row.get("source") != "Google Trends USA" or row.get("trend_type") != "Rising":
                continue
            keyword = (row.get("related_keyword") or "").strip()
            parent = (row.get("source_query") or row.get("parent_keyword") or "").strip()
            if not keyword or not parent or keyword.casefold() in seen:
                continue
            seen.add(keyword.casefold())
            data.append({
                "keyword": keyword, "parent": parent,
                "growth": (row.get("relative_growth_or_index") or "").lstrip("'"),
                "relation": row.get("relation_to_parent") or "not verified",
                "trends_url": row.get("google_trends_comparison") or ""
            })
    return data


def diversify(angles, limit=7):
    out, counts = [], {}
    for a in angles:
        parent = a["parent"].lower()
        if counts.get(parent, 0) >= 2:
            continue
        counts[parent] = counts.get(parent, 0) + 1
        out.append(a)
        if len(out) >= limit:
            break
    return out


def compose(angles):
    day = datetime.now(ZoneInfo("Africa/Casablanca")).strftime("%Y-%m-%d")
    lines = [
        "# Google AI Pro — Deep Research: US Recipe Competition and Hidden Angles",
        "",
        "Copy the following into Google AI Pro Deep Research.",
        "",
        "Act as a senior SEO researcher for low-authority US food blogs.",
        "Target Google USA, English, all recipe categories, no brand dependency, NO PORK.",
        "Date: " + day + ".",
        "GOAL: find search demand + an underserved recipe angle with realistic organic clicks.",
        "",
        "These candidates are from Google Trends USA RELATED Rising queries.",
        "The growth percentages are RELATIVE, not search volumes; they do not prove",
        "the exact term independently trends over 90 days.",
        "",
        "CANDIDATES:"
    ]
    if angles:
        for i, a in enumerate(angles, 1):
            lines.append(
                "{}. {} | Parent: {} | Related Rising: {} | Relation: {} | Trends URL: {}".format(
                    i, a["keyword"], a["parent"], a["growth"], a["relation"], a["trends_url"]
                )
            )
    else:
        lines.append("NO VERIFIED RISING ANGLES FOUND in this run. Do not invent any.")
        lines.append("Research credible recent US recipe trend sources first and document citations.")
    lines.extend([
        "",
        "RESEARCH EACH CANDIDATE:",
        "1. Demand: Confirm the US Google search intent and whether exact-query",
        "   demand is independent of the parent keyword. Explain seasonality,",
        "   evergreen potential, Google Trends sampling, and Breakout limitations.",
        "   Provide volume and organic KD only with a verifiable measurement source.",
        "2. Google USA SERP: Identify the actual top 3 organic ranking pages with",
        "   title, URL, observed ranking if accessible, publish/update date, page type,",
        "   and notable results in positions 4–10. Distinguish videos, snippets",
        "   and recipe carousels from the normal organic Top 3.",
        "3. Parent cannibalization: Check if stronger parent recipe pages already",
        "   satisfy the intent; diagnose navigational/viral-author queries,",
        "   roundup intent and likely click opportunity for a small blog.",
        "4. Competitor gaps: For the three strongest relevant organic pages, analyze",
        "   ingredients, method, cooking times, recipe card, pictures, FAQ,",
        "   troubleshooting, storage, substitutions, and mobile UX.",
        "   Cite URLs for actual weaknesses; do NOT invent missing sections.",
        "5. Better original recipe: Suggest a specific differentiated, pork-free",
        "   recipe approach and 5 reader-helpful improvements without copying.",
        "6. Provide a comparison table per keyword: demand and trend evidence,",
        "   measured/unverified KD, top competing URLs, weakness, isolated intent,",
        "   estimated ranking feasibility, and PUBLISH / TEST / REJECT.",
        "",
        "STRICT: Do not invent volume, KD, backlink counts, Google positions,",
        "People Also Ask questions, reader complaints or kitchen testing.",
        "A long keyword is not necessarily easy to rank. Prioritize distinct",
        "search intent, sustained demand, and a SERP a small blog could enter.",
        "",
        "FINAL: choose the single best opportunity, with exact keyword, target",
        "intent, evidence-backed top 3 gaps and an SEO recipe brief. No full article."
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        sample = [{"keyword": "sweet potato breakfast skillet", "parent": "sweet potato breakfast",
                   "growth": "+80 %", "relation": "linked", "trends_url": "https://trends.google.com/"}]
        assert "sweet potato breakfast skillet" in compose(sample)
        assert "NO VERIFIED RISING" in compose([])
        assert len(diversify(sample)) == 1
        print("AI brief self-test OK")
        return
    OUT.mkdir(exist_ok=True, parents=True)
    selected = diversify(get_angles(ANGLES))
    PROMPT.write_text(compose(selected), encoding="utf-8")
    print("AI Pro prompt created:", PROMPT, "Rising candidates:", len(selected))


if __name__ == "__main__":
    main()
