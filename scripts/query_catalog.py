"""Query the MQL5Activations catalogue built by parse_catalog.py.

Examples
--------
python query_catalog.py "infinity"
python query_catalog.py --ext .ex4 --role expert_ea --limit 20
python query_catalog.py --strategy grid --json
python query_catalog.py --stats
python query_catalog.py --ex4-only --limit 50
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "..", "data", "catalog.json")


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def matches(e, term):
    if not term:
        return True
    return term.lower() in e["name"].lower()


def fmt_row(e):
    strat = ",".join(e.get("strategies") or []) or "-"
    return (f"{e['ext']:<5} {e['role']:<15} {strat:<28} "
            f"#{e.get('msg_id')}  {e['name']}")


def print_stats(cat):
    print(f"entries      : {cat['entry_count']}")
    print(f"source html  : {cat['source_html']} ({cat['source_bytes']:,} bytes)")
    print("channels     : " + ", ".join(f"{k}={v}" for k, v in cat["channels"].items()))
    print("\nby extension :")
    for k, v in cat["ext_counts"].items():
        print(f"  {k:<8} {v}")
    print("\nby role      :")
    for k, v in cat["role_counts"].items():
        print(f"  {k:<18} {v}")
    print("\nby strategy  :")
    for k, v in cat["strategy_counts"].items():
        print(f"  {k:<18} {v}")
    print("\nsource availability :")
    for k, v in cat["pairing"].items():
        print(f"  {k:<36} {v}")


def main():
    ap = argparse.ArgumentParser(description="Query the MQL5Activations catalogue.")
    ap.add_argument("term", nargs="?", default=None, help="substring to match on filename")
    ap.add_argument("--ext", help="filter by extension, e.g. .ex4")
    ap.add_argument("--role", help="filter by inferred role, e.g. expert_ea")
    ap.add_argument("--strategy", help="filter by strategy signal, e.g. grid")
    ap.add_argument("--ex4-only", action="store_true",
                    help="only .ex4 entries whose product has no .mq4 in the index")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--stats", action="store_true", help="print roll-up statistics")
    ap.add_argument("--catalog", default=CATALOG)
    args = ap.parse_args()

    cat = load(args.catalog)

    if args.stats:
        print_stats(cat)
        return 0

    rows = [e for e in cat["entries"] if matches(e, args.term)]
    if args.ext:
        rows = [e for e in rows if e["ext"].lower() == args.ext.lower()]
    if args.role:
        rows = [e for e in rows if e["role"].lower() == args.role.lower()]
    if args.strategy:
        rows = [e for e in rows if args.strategy.lower() in (e.get("strategies") or [])]

    if args.ex4_only:
        # products that appear as .ex4 but have no .mq4 anywhere in the index
        stems_with_source = {e["stem"] for e in cat["entries"] if e["ext"] == ".mq4"}
        rows = [e for e in rows if e["ext"] == ".ex4"
                and e["stem"] not in stems_with_source]

    if args.json:
        json.dump({"count": len(rows), "entries": rows[:args.limit]},
                  sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0

    print(f"matched {len(rows)} of {cat['entry_count']} entries "
          f"(showing up to {args.limit})\n")
    for e in rows[:args.limit]:
        print(fmt_row(e))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
