"""Static triage for a compiled MetaTrader .ex4 / .ex5 artifact.

Read-only. Never executes the target. Prints a report, optionally JSON.

    python ex4_triage.py "C:\\path\\to\\file.ex4"
    python ex4_triage.py "C:\\path\\to\\file.ex4" --json out.json

Reads: header magic/layout, Shannon entropy (whole + per 8 KB), recoverable
ASCII/UTF-16LE strings, MQL4/MT5 API probes in both encodings, URL indicators,
and embedded-container signatures.
"""
import argparse
import hashlib
import json
import math
import os
import re
import struct
import sys

API_PROBES = [
    "OnInit", "OnDeinit", "OnTick", "OnTimer", "OnChartEvent", "OnCalculate",
    "OrderSend", "OrderClose", "OrderModify", "OrderSelect", "OrderDelete",
    "iMA", "iRSI", "iMACD", "iBands", "iCustom", "iStochastic", "iATR",
    "MarketInfo", "SymbolInfo", "AccountBalance", "AccountEquity",
    "AccountNumber", "AccountInfoInteger", "GlobalVariable", "GlobalVariableSet",
    "WebRequest", "SendMail", "SendNotification", "FileOpen", "FileWrite",
    "FileRead", "FolderCreate", "IsDllsAllowed", "IsLibrariesAllowed",
    "DllImport", "LoadLibrary", "GetProcAddress", "kernel32", "user32",
    "ws2_32", "wininet", "shell32", "advapi32", "WinExec", "ShellExecute",
    "CreateProcess", "VirtualAlloc", "VirtualProtect", "WriteProcessMemory",
    "MetaQuotes", "copyright", "#property", "expert", "indicator",
    "LifeInDreamsWorld", "MQL5Activations",
]

URL_PATTERNS = [b"http://", b"https://", b"ftp://", b".com", b".net", b".ru",
                b"t.me", b"telegram", b"www.", b"api.", b"socket", b"discord"]

CONTAINER_SIGS = {
    "MZ (DOS/PE)": b"MZ", "PE\\0\\0": b"PE\x00\x00", "ELF": b"\x7fELF",
    "ZIP(local)": b"PK\x03\x04", "ZIP(EOCD)": b"PK\x05\x06",
    "GZIP": b"\x1f\x8b\x08", "7z": b"7z\xbc\xaf\x27\x1c", "RAR": b"Rar!\x1a\x07",
    "CAB(MSCF)": b"MSCF", "UPX0": b"UPX0", "UPX1": b"UPX1",
}


def entropy(buf):
    if not buf:
        return 0.0
    counts = [0] * 256
    for b in buf:
        counts[b] += 1
    n = len(buf)
    h = 0.0
    for c in counts:
        if c:
            p = c / n
            h -= p * math.log(p, 2)
    return h


def ascii_runs(data, minlen):
    out, cur = [], bytearray()
    for b in data:
        if 32 <= b <= 126:
            cur.append(b)
        else:
            if len(cur) >= minlen:
                out.append(cur.decode("ascii"))
            cur = bytearray()
    if len(cur) >= minlen:
        out.append(cur.decode("ascii"))
    return out


def utf16le_runs(data, minlen):
    out, cur, i, n = [], bytearray(), 0, len(data)
    while i + 1 < n:
        if data[i + 1] == 0 and 32 <= data[i] <= 126:
            cur.append(data[i])
            i += 2
        else:
            if len(cur) >= minlen:
                out.append(cur.decode("ascii"))
            cur = bytearray()
            i += 1
    if len(cur) >= minlen:
        out.append(cur.decode("ascii"))
    return out


def triage(path):
    with open(path, "rb") as f:
        data = f.read()
    ev = {"target": os.path.abspath(path), "size": len(data)}
    ev["sha256"] = hashlib.sha256(data).hexdigest()
    ev["md5"] = hashlib.md5(data).hexdigest()
    ev["magic_hex"] = data[:4].hex(" ")
    ev["magic_ascii"] = "".join(chr(b) if 32 <= b < 127 else "." for b in data[:4])
    ev["header_u32_le"] = {f"0x{o:02x}": struct.unpack_from("<I", data, o)[0]
                           for o in range(0, min(0x30, max(4, len(data) - 4)), 4)}

    ev["entropy_whole"] = round(entropy(data), 4)
    chunk = 8192
    ch = [round(entropy(data[i:i + chunk]), 4) for i in range(0, len(data), chunk)]
    ev["entropy_chunks_8k"] = {"count": len(ch), "min": min(ch),
                               "max": max(ch), "mean": round(sum(ch) / len(ch), 4)}

    a6 = ascii_runs(data, 6)
    a10 = ascii_runs(data, 10)
    ev["ascii_runs_ge6"] = len(a6)
    ev["ascii_runs_ge10"] = len(a10)
    ev["ascii_wordlike_ge10"] = len([s for s in a10
                                     if re.fullmatch(r"[A-Za-z0-9_.$]+", s)])
    ev["utf16_wordlike_ge6"] = len([s for s in utf16le_runs(data, 6)
                                    if re.fullmatch(r"[A-Za-z0-9_.$]+", s)])
    ev["sample_strings"] = sorted(set(a10), key=len, reverse=True)[:20]

    ev["api_probe_ascii"] = {p: data.count(p.encode()) for p in API_PROBES}
    ev["api_probe_utf16le"] = {p: data.count(p.encode("utf-16-le")) for p in API_PROBES}
    ev["url_probe_ascii"] = {p.decode(): data.count(p) for p in URL_PATTERNS}
    ev["container_signatures"] = {k: data.count(v) for k, v in CONTAINER_SIGS.items()}

    pe = ev["container_signatures"]["PE\\0\\0"]
    ev["mz_expected_by_chance"] = round(len(data) / 65536, 2)
    ev["embedded_pe_verdict"] = ("no embedded native PE image" if pe == 0
                                 else f"PE signature present ({pe}) - inspect further")
    return ev


DANGER_APIS = ("WebRequest", "SendMail", "SendNotification", "LoadLibrary",
               "WinExec", "ShellExecute", "CreateProcess", "VirtualAlloc",
               "DllImport", "IsDllsAllowed", "FileWrite")


def verdict(ev):
    v = []
    ent = ev["entropy_whole"]
    if ent >= 7.9:
        v.append("payload appears ENCRYPTED/COMPRESSED (entropy ~%.2f) - not readable; "
                 "behaviour UNKNOWN, not absent" % ent)
    elif ent >= 6.5:
        v.append("payload entropy %.2f - likely compressed/packed" % ent)
    else:
        v.append("payload entropy %.2f - likely readable code/data" % ent)
    if ev["embedded_pe_verdict"].startswith("no embedded"):
        v.append("no embedded PE/DLL image")
    else:
        v.append("EMBEDDED PE/DLL PRESENT - treat as hostile")
    danger = sorted(k for k, n in ev["api_probe_ascii"].items()
                    if n and k in DANGER_APIS)
    if danger:
        v.append("high-risk API strings present: " + ", ".join(danger))
    else:
        v.append("no plaintext high-risk API strings found (does NOT prove safety)")
    return v


def main():
    ap = argparse.ArgumentParser(description="Static triage of a .ex4/.ex5 artifact.")
    ap.add_argument("path")
    ap.add_argument("--json", help="also write raw evidence JSON to this path")
    args = ap.parse_args()

    if not os.path.isfile(args.path):
        print(f"not a file: {args.path}", file=sys.stderr)
        return 1

    ev = triage(args.path)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(ev, f, indent=2)

    print(f"target      : {ev['target']}")
    print(f"size        : {ev['size']:,} bytes")
    print(f"sha256      : {ev['sha256']}")
    print(f"md5         : {ev['md5']}")
    print(f"magic       : {ev['magic_hex']}  ({ev['magic_ascii']})")
    print(f"entropy     : {ev['entropy_whole']} bits/byte "
          f"(chunks min {ev['entropy_chunks_8k']['min']} / "
          f"max {ev['entropy_chunks_8k']['max']})")
    print(f"strings     : ascii>=6 {ev['ascii_runs_ge6']}, "
          f"ascii>=10 {ev['ascii_runs_ge10']}, "
          f"wordlike>=10 {ev['ascii_wordlike_ge10']}, "
          f"utf16 wordlike>=6 {ev['utf16_wordlike_ge6']}")
    print("containers  : " + (", ".join(f"{k}={v}" for k, v in
                                        ev["container_signatures"].items() if v) or "none"))
    hits = {k: v for k, v in ev["api_probe_ascii"].items() if v}
    print(f"api probes  : {len(hits)} non-zero " + (json.dumps(hits) if hits else ""))
    uh = {k: v for k, v in ev["api_probe_utf16le"].items() if v}
    print(f"api utf16   : {len(uh)} non-zero " + (json.dumps(uh) if uh else ""))
    urlh = {k: v for k, v in ev["url_probe_ascii"].items() if v}
    print(f"url probes  : {len(urlh)} non-zero " + (json.dumps(urlh) if urlh else ""))
    if ev["sample_strings"]:
        print("top strings :")
        for s in ev["sample_strings"][:10]:
            print("   ", s)
    print("\nVERDICT")
    for line in verdict(ev):
        print("  - " + line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
