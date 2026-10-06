# mql5-activations-catalog

A Cline **skill** that turns a Telegram EA/indicator file-index page into a
queryable catalogue, and pairs it with a static **triage** procedure for compiled
MetaTrader 4/5 artifacts.

Built from `C:\Infinity\sent_files.html` — the file index of the Telegram channel
`@MQL5Activations` (watermark `@LifeInDreamsWorld`).

## Read this first

This is an **inventory and risk-triage** project. It is **not** a downloader, a
decompiler, or a licence bypass. It does not contain any EA binaries.

The source channel redistributes commercial EAs and indicators at no cost. Most of
what it lists is freely circulating **MQL4 source**; a minority are **compiled
binaries with no source**, and those are both opaque and licence-encumbered. See
[`reference/LEGAL_AND_RISK.md`](reference/LEGAL_AND_RISK.md).

## What it contains

| Path | Purpose |
|---|---|
| `SKILL.md` | the skill definition (workflows, schema, guardrails) |
| `data/catalog.json` | 2,349 parsed entries with derived fields |
| `data/catalog.csv` | flat export for spreadsheets |
| `data/SUMMARY.md` | generated roll-up statistics |
| `scripts/parse_catalog.py` | rebuild the catalogue from the source HTML |
| `scripts/query_catalog.py` | search / filter / stats |
| `scripts/ex4_triage.py` | static triage of a `.ex4`/`.ex5` |
| `reference/EX4_FORMAT.md` | the EX4 container and why it is opaque |
| `reference/LEGAL_AND_RISK.md` | licence, malware and publishing notes |

## Catalogue at a glance

* **2,349** entries, one channel (`MQL5Activations`).
* Extensions: `.mq4` 1,449 · `.ex4` 576 · `.zip` 247 · `.ex5` 72 · `.mq5` 5.
* Inferred roles: indicator 571 · expert_ea 415 · panel_dashboard 31 · other 1,332.
* Filename strategy signals: scalping 181 · trend_following 179 · ai_ml 58 ·
  breakout 52 · grid 48 · news 12 · mean_reversion 8 · martingale 8.
* Source availability: **1,365 `.mq4`-only**, **540 `.ex4` with no source**,
  24 products with both.

## Usage

```bash
python scripts/query_catalog.py --stats
python scripts/query_catalog.py "infinity"
python scripts/query_catalog.py --ex4-only --role expert_ea --limit 20
python scripts/query_catalog.py --strategy grid --json

python scripts/ex4_triage.py "C:\path\to\file.ex4"
python scripts/ex4_triage.py "C:\path\to\file.ex4" --json evidence.json
```

Requirements: Python 3.8+. Standard library only — no third-party packages.

## Install as a Cline skill

Copy this folder to `~/.cline/skills/mql5-activations-catalog/` (Windows:
`C:\Users\<you>\.cline\skills\mql5-activations-catalog\`), then restart Cline.

## Caveats

* `role` and `strategies` are **filename keyword hints**, not verified behaviour.
* A clean string scan of an encrypted binary proves **nothing** about safety.
* Catalogue contents change as the source index changes; re-run `parse_catalog.py`.

## License

MIT — see [`LICENSE`](LICENSE). The license covers this tooling and its
documentation. It does not grant any rights to the third-party EAs referenced by
name in the catalogue.
