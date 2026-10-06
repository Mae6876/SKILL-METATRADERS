# Legal and risk notes

This file exists so that anyone using this skill states the position accurately
instead of hand-waving it. Nothing here is legal advice.

## 1. The channel and what it distributes

The index (`sent_files.html`) belongs to the Telegram channel **`@MQL5Activations`**.
Its own PDF says it shares *"GRATIS todos los Expert Advisors (EAs) e indicadores
Forex que encontramos en internet"* — i.e. it collects and redistributes EAs and
indicators it finds, at no cost. Filenames carry the watermark
`@LifeInDreamsWorld`.

**Verified worked example.** `The Infinity EA MT4 @LifeInDreamsWorld@MQL5Activations.ex4`
is a repackaged copy of *The Infinity EA MT4*, MQL5 Market product **122483**, by
**Abhimanyu Hans**, listed for **$599** with **12 activations**. The file's own body
is encrypted (entropy 7.9993 bits/byte) and contains no recoverable strings, so the
repackaging claim rests on the product/author identity plus the filename watermark.

### What the catalogue actually contains

It is **not** mostly cracked binaries. Of 2,349 entries:

* 1,449 `.mq4` + 5 `.mq5` + 247 `.zip` → **source code**, most of it MQL4 that
  circulates freely;
* 576 `.ex4` + 72 `.ex5` → compiled artifacts, of which **540 `.ex4` have no
  corresponding `.mq4` in the index**.

Only the compiled-only subset is both opaque and licence-encumbered. Say so — an
accurate catalogue is more useful than a sensational one.

## 2. Licence position

* Redistributing paid software without permission infringes copyright.
* **Decompiling another party's EA generally breaches the licence** under which it
  was distributed, independently of whether it can be done technically.
* Reverse engineering for interoperability/research may be lawful in some
  jurisdictions; redistributing the result rarely is.
* The practical, lawful route to `.mq4` source is the author or vendor.

## 3. Malware and operational risk

Cracked EAs are a recognised attack vector, for three reasons:

1. **Repackaging.** A redistributed EA can contain anything the repackager added. The
   original vendor is not responsible for it.
2. **Runtime capability without any bundled binary.** An MQL4/MQL5 EA can call
   `WebRequest`, `SendMail`, `SendNotification`, read and write files in the terminal
   data folder, read account/broker identifiers and full trade history, and — if
   "Allow DLL imports" is enabled — `#import` native libraries such as `kernel32`,
   `wininet` and `ws2_32`. **None of this requires an embedded PE, so "no embedded
   PE found" does not clear a file.**
3. **Profit motive.** A trader running an EA on a funded live account is an attractive
   target, and an EA already has permission to trade that account.

### Operating guidance worth repeating

* Do not run uncompiled binaries from an unknown source on a live account.
* If analysis is unavoidable, use a disposable, network-isolated VM, a **demo**
  account, and DLL imports disabled.
* Treat "free premium EA" as guilty until proven otherwise, and prefer source you can
  read over a binary you cannot.

## 4. Publishing caution (this repository)

This project is an **index and methodology**. Before publishing it anywhere public:

* A curated index of a redistribution channel may itself attract legal complaints and
  can breach platform terms of service (GitHub's Acceptable Use / DMCA process).
* Do not add the EA binaries themselves.
* Keep the provenance and "do not redistribute" notes intact.
* A private repository, or a public one containing only the methodology and
  non-identifying statistics, is the lower-risk option.

## 5. What this skill will not do

It will not download, mirror, unpack, patch, keygen or crack anything, and it will
not present filename keywords as verified performance. If a request needs those, the
answer is no — redirect to the vendor.
