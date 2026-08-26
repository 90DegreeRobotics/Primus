# Primus Thesis, Value, and Novelty Report Plan

**Status:** IN PROGRESS

## Goal

Create a source-grounded Markdown report assessing the thesis for creating Primus, whether the current model and research program hold value, and which aspects are established, distinctive, or genuinely unproven.

## Files to read

- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `Sovereign Textual Mind Paradigm.md`
- `Organic Wetware AI Architecture.md`
- `CCF_Sovereign/README.md`
- `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`
- `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md`
- `docs/defense_evidence/benchmarks/ccf_world_core_day_one_2026-08-26.md`
- Relevant implemented substrate and world-schema source
- Primary external literature and official project documentation cited in the report

## Files to edit

- This plan
- `docs/research/PRIMUS_THESIS_VALUE_AND_NOVELTY_2026-08-26.md`
- `handoff_manus_2026-08-26_primus-thesis-novelty-report.md`

## Ordered steps

- [x] Read repository law and current truth surfaces.
- [x] Inspect the implemented substrate, world schema, evidence summary, and research thesis.
- [x] Cross-check closest prior art with primary sources.
- [x] Build a claim-by-claim novelty matrix separating scientific, engineering, product, and patent novelty.
- [x] Write the report with explicit current-evidence and non-claim boundaries.
- [x] Audit citations, dates, factual claims, concurrent Claude work, and protected parent integrity.
- [ ] Run the documentation gate, stage only this lane, commit on `main`, and push `origin/main`.
- [ ] Mark this plan complete and write the handoff.

## Test gate

```pwsh
git diff --check --cached
git status --short --branch
git diff --cached --stat
```

The report must also pass a manual citation audit: every external factual claim has a primary or authoritative URL, repository facts match `STATUS.md` and committed evidence, and no unverified capability is described as learned or product-live.

## Rollback path

No source, checkpoint, training data, or runtime artifact will be modified. If the report cannot pass the citation or concurrent-tree audit, leave this plan marked `INTERRUPTED`, do not stage or commit, and identify the first unresolved claim.

## Next-agent pickup notes

This is a docs-only, non-overlapping lane. Claude may concurrently run the chunked-scan ladder. Do not touch Claude’s plan, runtime artifacts, benchmark implementation, checkpoints, or generated evidence. Stage only the exact report, this plan, and the final handoff after the concurrent work is audited.
