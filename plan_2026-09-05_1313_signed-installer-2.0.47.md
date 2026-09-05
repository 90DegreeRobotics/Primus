# Plan — Signed installer 2.0.47 (wine-glass Create recovery)

**Date:** 2026-09-05 1313 CDT
**Status:** IN PROGRESS
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

- [ ] Write this plan; pair it into `C:\Primus`.
- [ ] Bump `installer/version.json` to `2.0.47` / serial `71` (keep `stable`).
- [ ] Update `docs/customer/WHAT_YOU_GET.md` present-tense pin so the customer-doc gate stays honest.
- [ ] Run `desktop/tests/test_customer_doc_claims.py` and `scripts/check_signing_ready.ps1` in azure mode.
- [ ] Commit the prepare identity on `main`.
- [ ] Run `pwsh installer\build.ps1` with azure signing env set; no `-SkipSign`.
- [ ] Confirm `installer/output/release.json` `signing_status` is `signed` and Authenticode is `Valid`.
- [ ] Confirm Downloads copy exists, version-named, and hash-matches the build.
- [ ] Record proof in STATUS / release.json; push `HEAD == origin/main`.
- [ ] Tell the operator the path, version, sha256, and the Create click after they install.

## Out of scope

- Launching the installer.
- A live Foundry wine-glass witness (that is the operator's post-install click).
- Unrelated dirty files (`docs/windows/DEMO_LAPTOPS_CONNECT.md`, CRLF on `desktop/chronos_foundry.py`).

## Paired implementation

The installer build runs in `C:\chronos2`. This Primus file is the tandem-repo plan copy. No Primus trainer or corpus behavior changes in this unit of work.
