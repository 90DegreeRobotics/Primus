# Plan — Create must render, not refuse

**Date:** 2026-09-05 1614 CDT
**Status:** COMPLETE — source on main; 2.0.47 installer does not contain this fix
**Scope:** Stop Object-mode Create from being a carve-or-nothing failure machine. A readable prompt must reach the live LLM scene compiler and produce a rateable draft. No new noun recipes.

## Why

Installed Create waited 9:11 on `mountain range` in Object mode, then showed **CARVED GEOMETRY — REFUSED** and no image. That violates attempt-first law and the product: ChronoSophia is a world renderer (prompt → LLM → geometry, material, lighting → render), not a recipe book and not a refusal engine. A wine glass is a generic cup, not a special-cased noun.

## Work items

- [x] Object mode no longer dispatches `--geometry-forge`. Buyer Create uses `first-light` (live oracle + compiler).
- [x] Remove the terminal-`glass` vessel head-noun added for wine glass.
- [x] Measured route stays only for stated sizes and existing vessel/cut words.
- [x] CLI `--geometry-forge` continues the compiled scene as a labeled draft if carve misses.
- [x] Tests, Object-mode copy, and the capability-map Object row updated.
- [x] Focused Python and Rust gates. Do not install.

## Paired implementation

The executable repair is in `C:\chronos2`. This Primus file is the tandem-repo plan copy. No Primus trainer change.
