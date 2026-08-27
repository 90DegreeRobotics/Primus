# Primus Typed World Schema v1

**Status:** Implemented draft with passing local regression tests
**Scope:** World-state and world-action representation, not a trained capability
**Vocabulary:** 4,096 token IDs
**Compiler boundary:** ChronoSophia S³V v1

## Purpose

The Primus world core must not become a collection of object recipes or a smaller prompt-response model. Its stable learning target is a **typed world program**: persistent entities, relations, geometry operations, cameras, materials, evidence, uncertainty, and time-ordered state transitions. Object classes remain data labels for evaluation and holdout partitioning; they do not select bespoke model architectures.

The schema is grounded in four existing ChronoSophia contracts. `crates/chronos_s3v/src/lib.rs` defines the compiler-facing entity, predicate, action, frame, camera-directive, and causal-plan artifact. `crates/chronos_geometry_plan/src/lib.rs` defines the finite geometry families and compiler-owned macro vocabulary. `crates/chronos_lexicon` defines primitive atoms, mesh/procedural verbs, symbolic part anchors, distributions, material slots, and scalar plan values. `data/capability_ledger.json` distinguishes available routes from unavailable or unproven routes. The world schema does not turn an unavailable ledger entry into an executable promise.

> **Design law:** The learned core may propose state and action tokens, but only compiler-owned operations may cross the execution boundary. Evidence, uncertainty, and capability status remain explicit throughout the program.

## World-state contract

The schema uses integer-quantized physical values to keep canonical serialization stable across languages and machines. Translation is represented in millimetres, rotation in centidegrees, scale as thousandths, camera focal length and sensor width in micrometres, color as RGBA bytes, material factors as unsigned bytes, and confidence as unsigned 16-bit values.

| Record | Required meaning | Domain-general role |
|---|---|---|
| `WorldEntity` | Stable ID, kind, class label, transform, optional material, attributes | Represents any persistent character, object, location, or abstract entity without selecting a recipe |
| `WorldRelation` | Typed subject-object edge and confidence | Represents `part_of`, `attached_to`, `supports`, `occludes`, `constrained_by`, spatial, and possession relations |
| `WorldOperation` | Typed state transition with references and preconditions | Represents creation, relation edits, transforms, materials, cameras, observations, narrative actions, and finite geometry macros |
| `WorldFrame` | Tick, camera, operations, and observed entities | Makes temporal order and observation coverage explicit |
| `CameraState` | Projection, full quantized transform, intrinsics, image dimensions, clipping planes | Provides real pose inputs and recoverable metadata rather than a named-view label |
| `MaterialState` | Role, color, metallic, roughness, emission, compiler hint | Separates material identity from object identity |
| `EvidenceBinding` | Source URI, source hash, kind, confidence, frame, camera | Distinguishes observed or measured facts from inferred or generated content |
| `Uncertainty` | Target, reason, confidence, supporting evidence | Marks unobserved, occluded, conflicting, extrapolated, and quantized state |
| `DatasetPartition` | Split, object class, operation family, generator family | Supports whole-family and whole-class holdouts rather than random-example leakage |

## Compiler-owned operations

The geometry vocabulary mirrors the existing `chronos_geometry_plan` families: `primitive`, `box_grammar`, `lathe`, `sweep`, `compound`, `sdf`, and `voxel_fallback`. The macro set mirrors its finite compiler operations, including rectangle bodies, face selection, extrusion, inset, bevel, lathe, hollow lip, sweep, tapered extrusion, part assembly, SDF union, and voxel-hull extraction.

This finite execution alphabet is intentionally narrower than the world model’s representational capacity. The world model may represent an unknown object class, an occluded region, or an unavailable capability. It may execute only an operation whose compiler token and capability status are explicit. This preserves the difference between **being able to describe a world state** and **being able to build it today**.

## Relation to S³V

S³V remains the canonical ChronoSophia compiler artifact. The bridge lowers every world entity to an S³V entity, every world operation to an S³V action, and every world frame to an S³V frame. Known narrative verbs use native `ActionVerb` values; geometry and state-edit operations use the existing extensible `Other(String)` path. Relation additions and removals lower to typed effects.

S³V v1 does not have native fields for full camera intrinsics, evidence bindings, quantified uncertainty, material state, or quantized transforms. To satisfy the required **schema → S³V → schema** lossless gate without adding unsupported S³V fields, the bridge stores a compressed, versioned canonical `WorldProgram` envelope in the S³V title. Native S³V fields remain populated for compiler interoperability. This bridge envelope is an implementation boundary, not a user-visible title or a claim that S³V v1 natively models every field.

The following invariants are tested:

| Invariant | Gate |
|---|---|
| Canonical schema JSON is deterministic | Parse and reserialize without byte-level semantic change |
| Token stream is bounded by 4,096 IDs | Every emitted ID is checked against the declared vocabulary |
| Token stream is lossless | Decode produces an equal `WorldProgram` and identical SHA-256 |
| S³V bridge is lossless | S³V JSON decodes to an equal `WorldProgram` |
| Camera pose is preserved | Translation, rotation, intrinsics, resolution, and evidence-camera binding survive the S³V round trip |
| Dangling references fail closed | Unknown entities, materials, cameras, relations, operations, or evidence IDs are rejected |
| Capability status remains explicit | S³V action receipts retain the capability ID and availability state |

## 4K vocabulary

The token stream combines a compact semantic prefix with a canonical byte payload. The semantic prefix exposes entities, relations, operations, geometry families, geometry macros, cameras, evidence kinds, uncertainty reasons, and dataset split classes directly to the model. The byte payload guarantees exact decoding without an open-ended text tokenizer.

| Token range | Purpose |
|---|---|
| `0–15` | Padding and program/semantic/payload boundary controls |
| `16–63` | Reserved control tokens |
| `64–1023` | Typed world symbols and future quantized symbols |
| `1024–1279` | Canonical UTF-8 byte tokens |
| `1280–4095` | Reserved future learned world symbols |

The vocabulary is independent of object names and recipe names. Literal IDs and class labels occur in the canonical payload, while the semantic prefix and structural signature expose the reusable world dynamics.

## Generator-entropy safeguards

Token count is not accepted as dataset diversity. `structural_program_signature` canonicalizes entity references and removes display names and concrete object-class labels while preserving operation order, relation topology, compiler family, macro choice, quantized transforms, parameter structure, and frame organization. `unique_program_coverage` reports total programs, unique structural programs, duplicates, and the unique fraction.

A dataset partition must label its object class, operation family, and generator family. Evaluation splits are whole-family contracts: `held_out_object_class`, `held_out_operation_family`, or `held_out_composition`. A random example split is deliberately absent. Two prompts that rename the same generator template collapse to the same structural signature; a changed operation order does not.

## Stage 2 deterministic trajectory generator

`src/world_schema/trajectory_generator.py` now emits deterministic, validated, multi-frame `WorldProgram` trajectories. Each program contains three ordered frames, compiler-owned geometry and state-transition operations, explicit cameras, generated and inferred evidence bindings, quantified uncertainty, capability status, and a `DatasetPartition`. The generator reserves a whole object class, a whole operation family, and a composition of otherwise-seen families; it deliberately does not offer a random-example split. Generator v1.1 derives the declared transform effect and optional support/near relation effects from generated pre-action geometry, material, and action-intent context rather than sampling an independent target delta.

The writer refuses an existing destination, publishes canonical JSONL plus a deterministic manifest through a temporary sibling directory, and records file hashes, record counts, split counts, structural-program coverage, token-sequence lengths, evidence kinds, capability states, and explicit non-claims. The manifest contains no wall-clock field, so the same configuration and seed produce byte-identical artifacts. This is synthetic, typed trajectory infrastructure: its evidence is labeled `generated` or `inferred`, not `observed` or `measured`.

### Generated temporal state witness

`src/world_data/temporal_witness.py` is a backward-compatible sidecar contract. It accepts only a validated manifest-bound ingestion result, then rederives one witness per canonical `WorldProgram`: pre-state at tick 0, safe action context, and target state at tick 2. Its context feature contract includes only initial translation, geometry extent/bevel/variant, and material metallic/roughness values. It explicitly excludes the declared transform delta, target translation, target relation booleans, program ID, source hash, evidence URI, object class, operation family, and partition label. The target is rederived from the declared `SET_TRANSFORM` and relation-edit operation history and retains only `generated`/`inferred` evidence labels.

This makes a more demanding **generated** benchmark possible: a model can be asked to infer the outcome from pre-state and context rather than being handed the generated delta. It is still not an observed or physical-world witness, does not execute compiler/render validation, and does not prove general learned dynamics.

The first ignored local smoke dataset used seed `20260826` with 12 training trajectories and three trajectories in each holdout split. It produced 21 validated programs, 21 unique structural signatures, zero duplicates, and token sequences ranging from 7,391 to 7,494 IDs. The JSONL SHA-256 is `3a0b5e79bd592dffb2731131f83ce1d1db93a583dd7aed0bdbe6718e4beb3a28`; the manifest SHA-256 is `6af0b09145aa680e527db98e33b6bf10bcd5752bef7e523e1180301b00d7f607`. Raw smoke output remains ignored under `CCF_Sovereign/tmp/`.

## What this implementation proves

The current implementation proves that a domain-general world program can be validated, serialized canonically, tokenized within a 4K vocabulary, decoded exactly, lowered to S³V-compatible JSON, and recovered losslessly. It proves that explicit camera pose, evidence provenance, uncertainty, and capability status survive the boundary. It also provides an executable measure of unique-program coverage and a deterministic generator for partitioned temporal fixtures. A fixture emitted by the Python bridge was independently parsed and validated by ChronoSophia’s real Rust `chronos_s3v` crate, which reported S³V version 1 with three entities, four actions, and one frame.

It does **not** prove that Primus has learned world dynamics, that the generated trajectories are physically or visually correct, that the schema covers every future compiler operation, or that unavailable capability-ledger routes work. A bounded generated-transition positive control did ingest a hash-verified Stage 2 dataset and evaluate exact model predictions across the protected splits. Its linear regressor received generated initial position and declared action delta, so its perfect score establishes only pipeline integrity and generated coordinate-addition/relation learnability; it is not a rich world-model result. The fixtures have not been compiled and rendered as a dataset, evaluated against observed outcomes, or used for full typed `WorldProgram` prediction. Those claims require compiler execution, render witnesses, context-dependent targets that do not expose the answer directly, protected whole-family evaluations, and operator review.

## Files and gates

| File | Responsibility |
|---|---|
| `src/world_schema/model.py` | Typed records, enums, canonical validation, references, hashes |
| `src/world_schema/tokens.py` | 4K semantic/byte codec and structural coverage metrics |
| `src/world_schema/s3v_bridge.py` | Native S³V lowering and lossless bridge envelope |
| `src/world_schema/trajectory_generator.py` | Deterministic temporal fixtures, context-derived generated action effects, holdout contracts, coverage evidence, and atomic dataset writing |
| `src/world_data/temporal_witness.py` | Manifest-bound generated pre-state/context/post-state sidecar and strict target-feature boundary |
| `generate_world_trajectories.py` | Explicit-destination Stage 2 command-line entry point |
| `test_world_schema.py` | Eight fail-hard schema, codec, bridge, and structural-signature regression tests |
| `test_world_trajectory_generator.py` | Seven fail-hard generator, holdout, determinism, hash, and destination-safety tests |

The focused gate is:

```bat
python -m compileall -q src\world_schema generate_world_trajectories.py test_world_schema.py test_world_trajectory_generator.py
python test_world_schema.py
python test_world_trajectory_generator.py
```
