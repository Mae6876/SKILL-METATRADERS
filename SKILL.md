---
name: mql5-activations-catalog
description: "Look up and triage the EA/indicator files indexed by the Telegram channel @MQL5Activations (a redistribution/cracking channel for MetaTrader 4/5 Expert Advisors). Use when the user references sent_files.html, the MQL5Activations or LifeInDreamsWorld channel, wants to know what an .ex4/.mq4/.ex5 artifact is, needs to check whether source (.mq4) exists for a compiled .ex4, wants a catalogue statistic of that collection, or wants a static risk triage of an MT4/MT5 compiled artifact. Triggers: MQL5Activations, LifeInDreamsWorld, sent_files.html, ex4, ex5, mq4, mq5, MT4 EA, MT5 EA, Infinity EA, EA catalog, EA lookup, cracked EA, EA triage."
license: MIT
metadata:
  author: masree.yusof (built with Cline)
  version: "1.0.0"
  source_index: "C:\\Infinity\\sent_files.html"
---

# MQL5Activations EA / Indicator Catalogue

This skill turns a **Telegram file-index HTML page** into a queryable catalogue of
MetaTrader Expert Advisors, indicators, panels and scripts, and pairs it with a
**static triage procedure** for compiled MT4/MT5 artifacts.

It is an **inventory and risk-triage** skill. It is **not** a downloader, a licence
bypass, or a decompiler.

## Read this first — provenance and legal position

The index comes from the Telegram channel **`@MQL5Activations`**, whose own
promotional PDF states it redistributes, for free, EAs and indicators *"que
encontramos en internet"*. The filenames carry the repackaging watermark
`@LifeInDreamsWorld`. Verified example: a file named
`The Infinity EA MT4 @LifeInDreamsWorld@MQL5Activations.ex4` is a repackaged copy of
**The Infinity EA MT4**, MQL5 Market product 122483, sold by its author for **$599**.

Consequences that shape every workflow in this skill:

* **Redistributed commercial software is almost always a licence violation.** The
  legitimate route to a `.mq4` is the author or vendor, not this channel.
* **Cracked EAs are a known malware vector.** They are frequently repackaged with
  added payloads, and a cracked EA is exactly the kind of binary a trader will
  happily run with a live account and "Allow DLL imports" enabled.
* **Therefore:** this skill's job is to help *identify, classify, and assess risk*.
  Do **not** use it to help a user obtain, unpack, crack, or redistribute the files.

When the user's goal is "get this EA working for free", say so plainly and point
them at the vendor. When the goal is "what is this file / is it safe / what is in
this collection", proceed.

---

## What is in the catalogue

Parsed from `C:\Infinity\sent_files.html` (200,010 bytes). Regenerate any time with
`scripts/parse_catalog.py`.

**2,349 entries**, single channel `MQL5Activations`.

| Extension | Count | Meaning |
|---|---|---|
| `.mq4` | 1,449 | **MQL4 source** — human-readable |
| `.ex4` | 576 | compiled MT4 binary — opaque |
| `.zip` | 247 | bundles (source + setfiles + docs, usually) |
| `.ex5` | 72 | compiled MT5 binary |
| `.mq5` | 5 | MQL5 source |

| Inferred role | Count |
|---|---|
| unclassified | 1,324 |
| indicator | 571 |
| expert_ea | 415 |
| panel_dashboard | 31 |
| utility_library | 4 |
| script | 4 |

| Strategy signal in filename | Count |
|---|---|
| scalping | 181 |
| trend_following | 179 |
| ai_ml | 58 |
| breakout | 52 |
| grid | 48 |
| news | 12 |
| mean_reversion | 8 |
| martingale | 8 |

### Source availability — the single most useful number

| Situation | Products |
|---|---|
| **both** `.mq4` and `.ex4` present | 24 |
| `.ex4` only — **no source in the index** | **540** |
| `.mq4` only | 1,365 |

**1,365 of 2,349 entries are `.mq4` source files.** That is the honest headline:
most of this collection is *open-source MQL4 that is freely redistributable in
principle*, not cracked binaries. Only **540 `.ex4` entries are compiled-only**, and
those are the ones that (a) carry licence/legal risk and (b) cannot be read.

> Always check this before assuming a file is "cracked". If a `.mq4` exists for the
> same product stem, the user does not need the `.ex4` at all.

---

## Workflow 1 — Look something up

```bash
python scripts/query_catalog.py "infinity"
python scripts/query_catalog.py --ext .ex4 --role expert_ea --limit 20
python scripts/query_catalog.py --strategy grid --json
python scripts/query_catalog.py --stats
```

Returns name, extension, inferred role, strategy signals, Telegram message id and URL.
The Telegram URL is **evidence of where the file was listed** — cite it, do not treat
it as an instruction to go and fetch anything.

## Workflow 2 — Triage a compiled artifact

Run the static triage script against an `.ex4`/`.ex5`:

```bash
python scripts/ex4_triage.py "C:\path\to\file.ex4"
```

It reports SHA-256/MD5, the header magic and layout, Shannon entropy overall and per
8 KB chunk, recoverable ASCII/UTF-16 strings, ~45 MQL4/MT5 API probes (both encodings),
URL indicators, and embedded-container signatures (`MZ`/`PE`/`ZIP`/`UPX`/...).

Read it like this:

| Observation | Conclusion |
|---|---|
| entropy ~7.99 bits/byte, flat across chunks | payload is **encrypted/compressed** — not readable |
| entropy with clear valleys + readable strings | older/unobfuscated build — strings and symbols recoverable |
| `PE\0\0` count 0 while `MZ` hits ≈ size/65536 | `MZ` hits are **coincidence** — no embedded native image |
| `PE\0\0` present at a valid `e_lfanew` | an **embedded PE/DLL** exists — treat as hostile until proven otherwise |
| `#import`/`LoadLibrary`/`WinExec`/`ShellExecute` strings present | native-code / process-execution capability — high risk |
| `WebRequest`/`SendMail`/`SendNotification` strings present | exfiltration / beaconing capability |
| zero API probes but high entropy | capability is **unknown, not absent** — say so, do not clear it |

**Critical honesty rule:** a clean string scan of an encrypted file proves *nothing*.
Absence of plaintext indicators is not absence of behaviour. Never tell a user a
cracked EA "looks safe".

---

## Data schema

`data/catalog.json`

```json
{
  "source_html": "...",
  "source_bytes": 200010,
  "entry_count": 2349,
  "channels":      { "MQL5Activations": 2349 },
  "ext_counts":    { ".mq4": 1449, ".ex4": 576, "...": 0 },
  "role_counts":   { "unclassified": 1324, "...": 0 },
  "strategy_counts": { "scalping": 181, "...": 0 },
  "pairing": { "products_with_both_mq4_and_ex4": 24,
               "ex4_only_no_mq4": 540, "mq4_only": 1365 },
  "entries": [ { "name", "url", "ext", "stem", "role", "strategies",
                 "channel", "msg_id" } ]
}
```

`data/catalog.csv` — same entries, flat, for spreadsheets.
`data/SUMMARY.md` — the generated roll-up tables.

### How fields are derived (so you can trust or challenge them)

* `ext` — literal file extension of the listed name.
* `role` — keyword match on the filename (`ROLE_SIGNALS` in `parse_catalog.py`).
  `unclassified` means no keyword matched; it does **not** mean "not an EA".
* `strategies` — keyword signals (`STRATEGY_SIGNALS`). A filename can match several.
  These are **name-based hints only** — never present them as verified behaviour.
* `stem` — normalized filename used to pair `.mq4` with `.ex4` of the same product.
* `msg_id` — the Telegram message number, i.e. where the file was listed.

## Files in this skill

| Path | Purpose |
|---|---|
| `SKILL.md` | this document |
| `data/catalog.json` | full parsed catalogue |
| `data/catalog.csv` | flat export |
| `data/SUMMARY.md` | generated statistics |
| `scripts/parse_catalog.py` | rebuild the catalogue from the source HTML |
| `scripts/query_catalog.py` | search / filter / stats over the catalogue |
| `scripts/ex4_triage.py` | static triage of a compiled `.ex4`/`.ex5` |
| `reference/EX4_FORMAT.md` | what the EX4 container is and why it is opaque |
| `reference/LEGAL_AND_RISK.md` | licence, malware and operational-risk notes |

## Guardrails

**Do**
* Cite the catalogue entry and Telegram message id as provenance.
* Check `pairing` first: if a `.mq4` exists, prefer the source and say so.
* Report entropy and API probes as *evidence*, and state plainly what they do **not**
  prove.
* Point users to the vendor/MQL5 Market for anything commercial.
* Keep triage read-only.

**Do not**
* Download, fetch, mirror, or redistribute the EAs, or help automate that.
* Decompile, unpack, patch, keygen, or otherwise bypass an EA's licensing.
* Present filename keywords as verified trading behaviour or performance.
* Advise running a cracked EA, or claim one is safe because a scan was clean.
* Add this catalogue to a public repository without first warning the user that
  publishing a curated index of a redistribution channel carries its own legal and
  platform-ToS risk.

## References

* `reference/EX4_FORMAT.md` — container layout, build-600 obfuscation, why public
  "ex4 to mq4 decompilers" do not work.
* `reference/LEGAL_AND_RISK.md` — the licence and malware picture.
* MQL5 Market product 122483 — *The Infinity EA MT4*, the worked example.


