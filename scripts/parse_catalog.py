"""Parse the MQL5Activations file-index HTML into structured catalog data.

Read-only against the source HTML. Writes catalog.json / catalog.csv / SUMMARY.md
into this script's directory.

Source:  C:\\Infinity\\sent_files.html
Format:  <li><a href="https://t.me/<channel>/<msgid>">filename.ext</a></li>
"""
import csv
import html
import json
import os
import re
from collections import Counter, defaultdict

SRC = r"C:\Infinity\sent_files.html"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUT_DIR = os.path.abspath(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

ENTRY_RE = re.compile(r'<li>\s*<a href="([^"]+)"\s*>(.*?)</a>\s*</li>', re.S | re.I)
CHANNEL_RE = re.compile(r"t\.me/([^/]+)/(\d+)$", re.I)

ROLE_SIGNALS = [
    ("expert_ea", [" ea", "ea ", "expert", "robot", "bot", "scalper", "scalp",
                   "advisor", "autotrade", "auto trade"]),
    ("indicator", ["indicator", "indicador", "arrow", "arrows", "signal",
                   "signals", "oscillator", "histogram", "heatmap", "zigzag",
                   "channel", "bands", "bollinger", "macd", "rsi", "tma",
                   "gann", "fibonacci", "fib", "pivot", "supply", "demand",
                   "trend", "reversal", "divergence"]),
    ("panel_dashboard", ["panel", "dashboard", "gui", "button", "control",
                         "trade manager", "manager", "copier", "monitor"]),
    ("utility_library", ["library", "lib", "helper", "util", "include",
                         "template", "snippet", "framework"]),
    ("script", ["script", "closer", "deleter", "export", "import", "report"]),
]

STRATEGY_SIGNALS = [
    ("martingale", ["martingale", "martin", "lot multiplier", "averaging"]),
    ("grid", ["grid", "hedge", "hedging", "lock"]),
    ("scalping", ["scalp", "m1", "m5", "tick", "hft", "high frequency"]),
    ("news", ["news", "nfp", "economic"]),
    ("trend_following", ["trend", "ma ", "moving average", "momentum"]),
    ("mean_reversion", ["reversal", "reversion", "counter", "mean"]),
    ("breakout", ["breakout", "break out", "bollinger", "range"]),
    ("ai_ml", ["ai ", "ai_", "neural", "ml ", "machine learning", "gpt",
               "chatgpt", "deep learning", "quantum"]),
]


def read_source(path):
    with open(path, "rb") as f:
        raw = f.read()
    return raw, raw.decode("utf-8", errors="replace")


def parse_entries(text):
    out, seen = [], set()
    for m in ENTRY_RE.finditer(text):
        url = m.group(1).strip()
        name = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        name = re.sub(r"\s+", " ", name)
        if url in seen:
            continue
        seen.add(url)
        out.append({"name": name, "url": url})
    return out


def ext_of(name):
    base = name.rsplit("/", 1)[-1]
    if "." not in base:
        return "(none)"
    return "." + base.rsplit(".", 1)[1].strip().lower()


def base_stem(name):
    """Normalized stem for pairing .mq4 with .ex4 of the same product."""
    stem = name.rsplit("/", 1)[-1]
    stem = re.sub(r"\.[A-Za-z0-9]{1,5}$", "", stem)
    stem = stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "", stem)
    stem = re.sub(r"(mt4|mt5|ea|v\d+)$", "", stem)
    return stem


def role_of(name):
    low = " " + name.lower() + " "
    for role, keys in ROLE_SIGNALS:
        if any(k in low for k in keys):
            return role
    return "unclassified"


def strategy_of(name):
    low = " " + name.lower() + " "
    return [s for s, keys in STRATEGY_SIGNALS if any(k in low for k in keys)]


def main():
    raw, text = read_source(SRC)
    entries = parse_entries(text)

    for e in entries:
        e["ext"] = ext_of(e["name"])
        e["stem"] = base_stem(e["name"])
        e["role"] = role_of(e["name"])
        e["strategies"] = strategy_of(e["name"])
        cm = CHANNEL_RE.search(e["url"])
        e["channel"] = cm.group(1) if cm else None
        e["msg_id"] = int(cm.group(2)) if cm else None

    ext_counts = Counter(e["ext"] for e in entries)
    role_counts = Counter(e["role"] for e in entries)
    chan_counts = Counter(e["channel"] for e in entries)

    stems = defaultdict(lambda: {"mq4": [], "ex4": [], "other": []})
    for e in entries:
        if e["ext"] == ".mq4":
            stems[e["stem"]]["mq4"].append(e["name"])
        elif e["ext"] == ".ex4":
            stems[e["stem"]]["ex4"].append(e["name"])
        else:
            stems[e["stem"]]["other"].append(e["name"])

    paired = {k: v for k, v in stems.items() if k and v["mq4"] and v["ex4"]}
    ex4_no_source = {k: v for k, v in stems.items() if k and v["ex4"] and not v["mq4"]}
    mq4_only = {k: v for k, v in stems.items() if k and v["mq4"] and not v["ex4"]}

    strategy_counts = Counter()
    for e in entries:
        for s in e["strategies"]:
            strategy_counts[s] += 1

    cat = {
        "source_html": SRC,
        "source_bytes": len(raw),
        "entry_count": len(entries),
        "channels": dict(chan_counts),
        "ext_counts": dict(ext_counts.most_common()),
        "role_counts": dict(role_counts.most_common()),
        "strategy_counts": dict(strategy_counts.most_common()),
        "pairing": {
            "products_with_both_mq4_and_ex4": len(paired),
            "ex4_only_no_mq4": len(ex4_no_source),
            "mq4_only": len(mq4_only),
        },
        "entries": entries,
    }

    with open(os.path.join(OUT_DIR, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(cat, f, indent=2, ensure_ascii=False)

    with open(os.path.join(OUT_DIR, "catalog.csv"), "w", encoding="utf-8",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "ext", "role", "strategies", "channel", "msg_id", "url"])
        for e in entries:
            w.writerow([e["name"], e["ext"], e["role"],
                        "|".join(e["strategies"]), e["channel"], e["msg_id"],
                        e["url"]])

    lines = ["# MQL5Activations file index - parsed catalog\n"]
    lines.append(f"- Source: `{SRC}` ({len(raw):,} bytes)")
    lines.append(f"- Entries parsed: **{len(entries):,}**")
    lines.append("- Channels: " + ", ".join(f"{k} ({v})" for k, v in chan_counts.items()))
    lines.append("\n## By file extension\n\n| Extension | Count |\n|---|---|")
    for k, v in ext_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append("\n## By inferred role\n\n| Role | Count |\n|---|---|")
    for k, v in role_counts.most_common():
        lines.append(f"| {k} | {v} |")
    lines.append("\n## By strategy signal\n\n| Strategy | Count |\n|---|---|")
    for k, v in strategy_counts.most_common():
        lines.append(f"| {k} | {v} |")
    lines.append("\n## Source availability\n")
    lines.append(f"- Products with **both** `.mq4` and `.ex4`: {len(paired)}")
    lines.append(f"- `.ex4` only (no source in index): **{len(ex4_no_source)}**")
    lines.append(f"- `.mq4` only: {len(mq4_only)}")
    with open(os.path.join(OUT_DIR, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("entries:", len(entries))
    print("ext:", dict(ext_counts.most_common()))
    print("role:", dict(role_counts.most_common()))
    print("strategy:", dict(strategy_counts.most_common()))
    print("pairing:", cat["pairing"])
    print("channels:", dict(chan_counts))


if __name__ == "__main__":
    main()

