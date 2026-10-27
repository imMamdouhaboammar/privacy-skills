#!/usr/bin/env python3
from __future__ import annotations

"""
Privacy & Data Protection Skills — Dynamic Intent Router & CLI Navigator
Indexes 257 curated, production-grade privacy engineering procedures across 20 subdomains.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_catalog() -> list[dict]:
    root_dir = Path(__file__).resolve().parent.parent
    catalog_path = root_dir / "catalog.json"
    if not catalog_path.exists():
        print(f"Error: Catalog not found at {catalog_path}", file=sys.stderr)
        sys.exit(1)
    with open(catalog_path, "r", encoding="utf-8") as f:
        return json.load(f)


def search_skills(catalog: list[dict], query: str) -> list[dict]:
    q = query.lower()
    matches = []
    for s in catalog:
        if (
            q in s["id"].lower()
            or q in s["name"].lower()
            or q in s["description"].lower()
            or any(q in t.lower() for t in s.get("tags", []))
            or any(q in r.lower() for r in s.get("regulations", []))
            or any(q in o.lower() for o in s.get("owasp_risks", []))
            or any(q in l.lower() for l in s.get("linddun_threats", []))
        ):
            matches.append(s)
    return matches


def filter_by_regulation(catalog: list[dict], reg: str) -> list[dict]:
    r = reg.strip().upper()
    return [s for s in catalog if any(r in x.upper() for x in s.get("regulations", []))]


def filter_by_subdomain(catalog: list[dict], subdomain: str) -> list[dict]:
    sub = subdomain.strip().lower()
    return [s for s in catalog if sub in s.get("subdomain", "").lower()]


def print_stats(catalog: list[dict]):
    from collections import Counter

    subdomains = Counter(s.get("subdomain", "unknown") for s in catalog)
    regulations = Counter(r for s in catalog for r in s.get("regulations", []))
    owasp = Counter(o.split(":")[0] for s in catalog for o in s.get("owasp_risks", []))

    print("==================================================================")
    print(f"  PRIVACY & DATA PROTECTION SKILLS — CATALOG METRICS")
    print(f"  Total Validated Skills: {len(catalog)}")
    print("==================================================================")
    print("\n[Subdomains Distribution]")
    for sd, count in subdomains.most_common():
        print(f"  - {sd:32s} : {count:3d} skills")

    print("\n[Top Regulations Coverage]")
    for reg, count in regulations.most_common(10):
        print(f"  - {reg:20s} : {count:3d} procedures")

    print("\n[OWASP Privacy Top 10 Alignment]")
    for o, count in owasp.most_common(10):
        print(f"  - {o:10s} : {count:3d} skills")
    print("==================================================================")


def main():
    parser = argparse.ArgumentParser(
        description="Privacy Skills Dynamic Intent Router & Catalog Search"
    )
    parser.add_argument("query", nargs="?", default="", help="Search query or keyword")
    parser.add_argument("--search", "-s", dest="search_opt", help="Search query")
    parser.add_argument("--regulation", "-r", help="Filter by regulation (e.g. GDPR, CCPA, HIPAA, EU_AI_ACT)")
    parser.add_argument("--subdomain", "-d", help="Filter by subdomain")
    parser.add_argument("--stats", action="store_true", help="Display catalog distribution statistics")
    parser.add_argument("--list", "-l", action="store_true", help="List all skills")
    parser.add_argument("--inspect", "-i", help="Inspect detailed skill spec by ID")

    args = parser.parse_args()
    catalog = load_catalog()

    if args.stats:
        print_stats(catalog)
        return

    if args.inspect:
        skill_id = args.inspect.strip()
        matched = [s for s in catalog if s["id"] == skill_id]
        if not matched:
            print(f"Skill '{skill_id}' not found.", file=sys.stderr)
            sys.exit(1)
        s = matched[0]
        print(json.dumps(s, indent=2))
        return

    q = args.search_opt or args.query
    results = catalog

    if q:
        results = search_skills(results, q)
    if args.regulation:
        results = filter_by_regulation(results, args.regulation)
    if args.subdomain:
        results = filter_by_subdomain(results, args.subdomain)

    if args.list or q or args.regulation or args.subdomain:
        print(f"Found {len(results)} matching skills:")
        print(f"{'ID':32s} | {'SUBDOMAIN':28s} | {'REGULATIONS':18s}")
        print("-" * 82)
        for s in results:
            regs = ", ".join(s.get("regulations", []))[:18]
            print(f"{s['id']:32s} | {s.get('subdomain', ''):28s} | {regs:18s}")
    else:
        print_stats(catalog)
        print("\nTip: Run 'python scripts/router.py <query>' or '--help' for options.")


if __name__ == "__main__":
    main()
