# The EX4 container — what it is, and why it is opaque

## What an .ex4 actually is

An `.ex4` is **not** a Windows executable. It is a proprietary container compiled by
MetaEditor from `.mq4` source and interpreted by the MetaTrader 4 runtime. It has no
`PE` header and cannot be run standalone, converted to an `.exe`, or converted to
`.ex5`. The MT5 counterpart is `.ex5`.

Because it is only meaningful to MT4, general-purpose reverse-engineering tooling
(Hopper, Ghidra, IDA, objdump, `file`, capstone-on-the-whole-file) has nothing to
grip: they are looking for a PE/ELF/Mach-O structure that is not there. REA returns
`target_unavailable` for exactly this reason.

## Observed layout (worked example)

`The Infinity EA MT4 @LifeInDreamsWorld@MQL5Activations.ex4` — 465,246 bytes.

```
0000  45 58 2d 02 70 00 6f 09 10 10 d0 00 00 e0 00 00  |EX-.p.o.........|
0010  e4 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00  |................|
0020  7e cd 89 f4 20 6d c9 20 08 1b c1 03 90 5d 22 2c  |~... m. .....]",|
0030  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  |................|
0040  0e 00 00 00 29 02 00 00 00 00 00 00 00 00 00 00  |....)...........|
0060  89 03 00 00 00 00 00 00 80 08 3b 10 80 05 00 00  |..........;.....|
0070  f5 8b bc 57 c9 fa 21 52 b3 e1 fb 08 f8 a8 3d 03  |...W..!R......=.|  <- body
```

| Offset | Observed | Reading |
|---|---|---|
| `0x00` | `45 58 2D 02` | signature `"EX-"` + format version `0x02` |
| `0x04` | u16 = **112** | **verified** to equal the offset where the body begins |
| `0x06`, `0x08`, `0x10` | 2415, 4112, 1252 | unidentified counts/sizes |
| `0x20`–`0x2F` | 16 high-entropy bytes | likely key material / nonce / hash |
| `0x40`, `0x44`, `0x60`, `0x6C` | 14, 553, 905, 1408 | unidentified counts |

**The 112-byte boundary is confirmed by entropy**, not assumed:

```
entropy[0..111]    (header, 112 bytes)     = 2.6914   <- structured
entropy[112..end]  (body, 465,134 bytes)   = 7.9994   <- encrypted
```

## Why it cannot be read

MetaTrader 4 **build 600 (February 2014)** changed `.ex4` to a format that is
deliberately obfuscated against decompilation. Symptoms of that obfuscation:

* uniform Shannon entropy ≈ 7.98–7.99 bits/byte across the whole body;
* **zero** recoverable word-like ASCII or UTF-16LE strings;
* **zero** hits for `OnInit`/`OnTick`/`OrderSend`/`iMA`/`MetaQuotes`/`copyright`
  in either encoding;
* single-byte "instruction" patterns (`push` 0x68, `call` 0xE8, `ret` 0xC3) appearing
  at exactly the chance rate (~1/256 of the file length), i.e. matching ciphertext.

Pre-2014 files were far less protected, and that is the entire basis of the
"ex4 to mq4 decompiler" market. For build 600+ files that market divides into:

1. tools that **do not work** on modern files;
2. **paid scams** that take money and deliver nothing;
3. **malware** that uses "free decompiler" as the lure.

None of them recover usable source, and running them is a worse risk than the EA.

## Detection heuristics you can rely on

| Signal | Meaning |
|---|---|
| entropy ≈ 7.99 flat | encrypted/compressed — unreadable, capability unknown |
| entropy with valleys | older build — strings/symbols may be recoverable |
| `PE\0\0` absent, `MZ` ≈ size/65536 | the `MZ` hits are coincidence; **no** embedded native image |
| `PE\0\0` at a valid `e_lfanew` | an embedded PE/DLL is present — hostile until proven otherwise |
| archive signatures (`PK`, `7z`, `Rar!`, `MSCF`) | embedded archive — inspect for nested payloads |
| `UPX0`/`UPX1` | packed payload |

A clean string scan of an encrypted file proves **nothing** about safety. Report it
as "no plaintext indicators found; behaviour unverified", never as "clean".

## The legitimate route to source

Ask the author or vendor for the `.mq4`. For a commercial EA that means the vendor's
own distribution and support, not a redistribution channel.
