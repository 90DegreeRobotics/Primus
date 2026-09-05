# Plan — Signed installer 2.0.47 (wine-glass Create recovery)

**Date:** 2026-09-05 1313 CDT
**Status:** COMPLETE — signed 2.0.47 delivered to Downloads; operator owns install
**Scope:** Bump release identity, produce a signed ChronoSophia2 installer from current `main`, and deliver it version-named to Downloads. Do not install, uninstall, or elevate.

## Why this build exists

Installed 2.0.46 still declines `a wine glass` in Object mode at 0:00. The source repair is on `origin/main` (`4964f1e9`). An installed payload cannot see that repair until a new signed installer is built and the operator installs it.

## Governing constraints

- Work only on `main`.
- Never run the installer or uninstaller.
- Two builds must never share a version: bump `product_version` and `build_serial` together.
- Sign with Azure Artifact Signing. Do not pass `-SkipSign`.
- Deliver `C:\Users\m\Downloads\ChronoSophia2_Setup_2.0.47.exe` and report sha256.
- Record hashes after signing.

## Work items

- [x] Write this plan; pair it into `C:\Primus`.
- [x] Bump `installer/version.json` to `2.0.47` / serial `71` (keep `stable`).
- [x] Update `docs/customer/WHAT_YOU_GET.md` present-tense pin so the customer-doc gate stays honest.
- [x] Run `desktop/tests/test_customer_doc_claims.py` and `scripts/check_signing_ready.ps1` in azure mode.
- [x] Commit the prepare identity on `main`.
- [x] Run `pwsh installer\build.ps1` with azure signing env set; no `-SkipSign`.
- [x] Confirm `installer/output/release.json` `signing_status` is `signed` and Authenticode is `Valid`.
- [x] Confirm Downloads copy exists, version-named, and hash-matches the build.
- [x] Record proof in STATUS / release.json; push `HEAD == origin/main`.
- [ ] Tell the operator the path, version, sha256, and the Create click after they install.

## Out of scope

- Launching the installer.
- A live Foundry wine-glass witness (that is the operator's post-install click).
- Unrelated dirty files (`docs/windows/DEMO_LAPTOPS_CONNECT.md`, CRLF on `desktop/chronos_foundry.py`).

## Delivery evidence (2026-09-05)

| Item | Value |
|---|---|
| Version / serial | `2.0.47` / `71` |
| Prepare commit | `bca9e7415257` |
| SHA-256 | `e9f17e8ab1d081841b9fbae0ecf2d6e9ea5ac9cebabff4ca65a6ccc2ea9025f0` |
| Downloads | `C:\Users\m\Downloads\ChronoSophia2_Setup_2.0.47.exe` |
| Size | 15278496 bytes |
| Authenticode | `Valid` — `CN=Michael Holt, O=Michael Holt, L=Normal, S=il, C=US` |
| `release.json` | `signing_status: signed` |

## Paired implementation

The installer build runs in `C:\chronos2`. This Primus file is the tandem-repo plan copy. No Primus trainer or corpus behavior changes in this unit of work.
