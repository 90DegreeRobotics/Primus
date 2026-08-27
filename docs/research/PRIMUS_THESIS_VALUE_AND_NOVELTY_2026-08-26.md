# Primus: Thesis, Technical Value, and Novelty Assessment

**Date:** August 26, 2026
**Author:** Manus AI
**Status:** Research assessment; not a patentability opinion, product-certification claim, or declaration of artificial general intelligence

## Executive judgment

**The thesis for creating Primus is valuable. The current trained model has not yet demonstrated that value. The individual architectural ingredients are largely not novel. The exact NeuroCognica integration is plausibly distinctive engineering, but it is not yet a demonstrated scientific contribution.**
**Authorship and chronology.** The name and core architecture assessed here are Michael Holt and NeuroCognica's independently conceived **Primus**. A Google Docs server-side “Modified” date of **2025-06-11** is preserved in the repository through a SHA-256-sealed PDF and provenance ledger. That evidence predates the unrelated OpenCog/SingularityNET PRIMUS world-model publication dated **2025-12-27** by approximately six months. The later publication is relevant prior art and creates a naming issue; it is **not** evidence that NeuroCognica derived Primus from that work or that the idea originated there.[27] [28] [18]

Primus addresses a real and strategically important problem: how to build an intelligence substrate that is **locally owned, continuously adaptable, inspectable, evidence-bound, and able to represent and act on worlds without outsourcing its core cognition to a remote foundation model**. This is a stronger thesis than “make a smaller language model.” It is also stronger than “combine biologically inspired modules.” The durable version of the thesis is that learning, memory, world representation, execution, and self-modification should form one governed local system.

The repository now contains meaningful first-party infrastructure: a from-scratch selective-state sequence substrate, a fast-weight path, surprise calculation, episodic and sleep-lifecycle components, an append-only evidence discipline, isolated candidate training, hash-bound manifests, shadow comparison, an explicit promotion boundary, a memory-bounded selective scan, and a typed object-agnostic world-program representation that round-trips through ChronoSophia’s S³V compiler interface.[1] [2] [3] These are valuable research assets because they make experiments reproducible, falsifiable, and harder to misrepresent.

That is not the same as having a valuable trained intelligence. The protected parent checkpoint was trained from only 845 conversation turns and scored **0/3** on its first live protected baseline. The August 26 scaling candidates measured training-path and hardware feasibility, not reasoning or world-model quality; none was promoted.[1] The typed world schema is currently tested as a representation and compiler bridge but is **not wired into model training or runtime prediction**. Primus therefore does not yet demonstrate learned world dynamics, reliable continual learning, stable long-term consolidation, or a product-live world-builder.[1] [2]

The novelty judgment is similarly layered. Selective state-space models, Hebbian fast weights, complementary fast/slow learning, generative replay, sleep consolidation, holographic representations, Minimum Description Length, neuro-symbolic world models, typed scene graphs, model registries, shadow evaluation, and artifact provenance all have substantial prior art.[4] [7] [8] [10] [11] [12] [13] [14] [15] [16] The strongest 2025–2026 counterexamples now cover much of Primus’s conceptual territory: **Titans** learns a surprise-sensitive neural memory at test time; **Language Models Need Sleep** formalizes wake/sleep and fast-to-slow consolidation with experiments; **Eyla** proposes a local-first SSM-and-memory architecture and documents the failure of architecture-by-aggregation; and SingularityNET/OpenCog has already published an unrelated cognitive architecture named **PRIMUS** whose world-model design combines multi-rate neural, hypervector, symbolic, evidence, uncertainty, and program representations.[7] [8] [9] [17]

The defensible novelty opportunity is narrower and more concrete:

> **Primus may become a novel evidence-native world-learning architecture if it couples a locally trained selective-state learner to a typed executable world program, preserves evidence and uncertainty through that boundary, treats learning and consolidation as isolated candidate mutations, and allows changes to canonical memory or parent weights only after reproducible held-out evidence and explicit promotion.**

No exact implemented duplicate of that full contract was found in this review. However, novelty by combination is not established merely because the component list is long. The coupling must produce a measurable capability that simpler combinations do not.

| Question | Direct answer |
|---|---|
| **Is the thesis worth pursuing?** | **Yes, conditionally.** Locally owned, continually adapting, auditable world intelligence has clear research and product value. |
| **Does the current trained model hold demonstrated value?** | **Not as an intelligence model yet.** It proves execution and training infrastructure, not useful cognition. |
| **Does the repository hold value now?** | **Yes.** It contains owned research infrastructure, evidence controls, hardware measurements, and a typed world boundary that materially reduce development risk. |
| **Are the component ideas novel?** | **Mostly no.** Each major component has substantial prior art. |
| **Is the exact approach novel?** | **Plausibly as system engineering; unproven as science.** The evidence-native coupling is distinctive, but no end-to-end learned result exists. |
| **Is it patent-novel?** | **Unknown.** The field is dense, and a professional claim search is required. |
| **Is there a naming risk?** | **Yes.** A later, unrelated OpenCog/SingularityNET cognitive architecture uses the name PRIMUS and published a closely related world-model paper on 2025-12-27, approximately six months after the preserved NeuroCognica Primus evidence dated 2025-06-11. This is a naming and prior-art issue, not evidence of origin or derivation.[27] [28][17] [18] |

## 1. Scope and method

This report evaluates four different meanings of “novel,” because collapsing them into a single label produces either hype or an unfair dismissal.

| Dimension | Question evaluated |
|---|---|
| **Scientific novelty** | Does Primus introduce a new learning principle, representation, algorithm, or empirically supported explanation? |
| **Engineering novelty** | Does Primus implement a useful and non-obvious integration, runtime, safety boundary, or hardware optimization? |
| **Product differentiation** | Could the resulting system deliver a capability that users cannot obtain from a prompt wrapper or ordinary local model? |
| **Patent novelty** | Might a specific claim be new relative to the complete prior-art record? This report identifies risk but does not provide a legal conclusion. |

Repository claims were checked against the current `STATUS.md`, the CCF source audit, the day-one world-core evidence report, the typed world-schema contract, and the implementation surfaces under `CCF_Sovereign`.[1] [2] [3] External comparisons prioritize primary papers, official project pages, and official engineering documentation. The review covered selective state-space models, test-time memory, fast weights, continual learning, replay, sleep consolidation, HRR/vector-symbolic memory, MDL, neuro-symbolic world models, scene graphs, local-first agents, model governance, shadow deployment, and artifact provenance.[4] [5] [6] [7] [8] [9] [10] [11] [12] [13] [14] [15] [16] [17] [18] [19] [20] [21] [22] [23] [24] [25]

The report uses the following evidence rule:

> **An architectural intention is not an implemented mechanism; an implemented mechanism is not a learned capability; a learned capability is not a useful product until it survives representative evaluation.**

## 2. The thesis of creating Primus

The original CCF thesis rejects the idea that useful intelligence must remain a frozen hyperscale model served from a distant data center. It proposes a “sovereign node” that learns over a continuous stream, uses recurrent state rather than an ever-growing attention cache, adapts rapidly through fast weights, consolidates selectively into slower weights, and treats sleep as an active learning phase rather than downtime.[26] The later NeuroCognica direction expands this from a textual mind into a **world-building substrate**: the stable learning target is no longer conversation prose but persistent entities, relations, geometry, cameras, evidence, uncertainty, operations, and state transitions.[2]

The strongest statement of the thesis is therefore not “Mamba plus memory.” It is:

> **A useful local intelligence should own its representations and learning history, maintain an explicit and revisable model of world state, distinguish observation from inference, execute only typed capabilities it actually possesses, and change itself through auditable evidence rather than opaque overwrite.**

This thesis contains five separable commitments.

| Commitment | Meaning for Primus | Why it matters |
|---|---|---|
| **Sovereignty** | The core learner and memory can operate locally without requiring a remote model for every inference. | Ownership, privacy, continuity, cost control, and independence from provider behavior. |
| **Continuity** | Learning is a lifecycle with fast acquisition, episodic retention, offline consolidation, evaluation, and explicit promotion. | A world-builder must change after deployment without silently destroying earlier competence. |
| **World grounding** | The central representation is typed state and action, not merely natural-language continuation. | Text alone is an indirect and ambiguous carrier of geometry, identity, causality, and execution semantics. |
| **Evidence preservation** | Observations, inferred state, uncertainty, source hashes, and capability status remain distinct. | Generated detail should not become indistinguishable from measured fact. |
| **Governed self-modification** | New weights or canonical beliefs are candidates until comparative evidence authorizes promotion. | Self-improvement without promotion discipline is uncontrolled model drift. |

These commitments define a coherent research program. They also expose why training a conventional small language model on archived conversations is insufficient: it may imitate a voice, but it does not thereby acquire a persistent world state, action-conditioned dynamics, calibrated provenance, or a safe self-modification process.

## 3. What Primus is today

The repository makes a disciplined distinction between architectural notes, executable components, verified behavior, and unproven claims.[1] [3] That distinction should remain central to every novelty statement.

| Surface | Implemented or measured today | Not yet established |
|---|---|---|
| **Sequence substrate** | Custom PyTorch Mamba-like backbone with input-dependent selective state, causal convolution, token logits, extracted field state, and a production chunked scan.[1] [3] | Competitive language or world-model quality; a new state-space theory. |
| **Fast adaptation** | Identity-initialized linear fast-weight layer; local outer-product update is called from the main runtime and continual-learning benchmark.[3] | Stable long-horizon online learning, advantage over stronger fast-weight baselines, or interference control at realistic scale. |
| **Surprise** | Shifted next-token negative log probability is computed per token and used by episodic paths.[3] | Calibration, task relevance, or proof that the signal selects memories worth retaining. |
| **Sleep lifecycle** | Wake/saturation/sleep orchestration, replay/consolidation components, immutable ledger events, tests, and operator surfaces exist.[1] [3] | Autonomous lifelong learning, reliable dream quality, or improved retained capability after repeated real cycles. |
| **Associative memory** | HRR-related component tests include deterministic identity-key round trips.[1] | Large-capacity learned retrieval, resistance to superposition noise, or improved world reasoning. |
| **Candidate governance** | Candidate-only directories, frozen-parent and corpus hashes, commit binding, manifests, shadow comparison, and a separate explicit promotion command.[1] [3] | A real quality candidate that defeats the parent and is safely promoted. |
| **World representation** | Object-agnostic typed `WorldProgram`; entities, relations, frames, cameras, materials, operations, evidence, uncertainty, holdouts, and a 4K lossless codec.[1] [2] | Training or inference over world programs; learned state transition; visual correctness; a shipped world-builder. |
| **Compiler boundary** | Lossless schema-to-S³V bridge; a generated fixture was accepted by ChronoSophia’s Rust S³V parser.[1] [2] | End-to-end generation of correct compiled worlds from sensory input or user intent. |
| **GPU feasibility** | Full training-path passes at 5.34M, 16.21M, and 53.93M parameters on the RTX 3060; 155.35M crossed one step and then OOMed. Chunked scan reduced the large stress case from 16.23 GB to 8.50 GB reserved memory.[1] [3] | A scaling law, capability improvement, or proof that 53.93M is sufficient for world intelligence. |
| **Current parent** | Local checkpoint loads and generates; first protected baseline produced 0/3 passes without execution errors.[1] [3] | Useful reasoning, learned world modeling, or product quality. |

The most important current integration gap is explicit: repository search finds the `world_schema` package referenced by its dedicated tests and documentation, but not by the model trainer, the main inference path, or a learned dynamics objective. The schema is therefore **real software but not yet model cognition**. This is not a criticism of the schema; it is the correct boundary for planning the next experiment.

## 4. Does a model like Primus hold value?

### 4.1 Research value: yes

Primus holds immediate value as an owned experimental platform. The repository can run controlled candidate training, preserve the parent, bind inputs and outputs to hashes, reproduce hardware limits, compare candidates without promotion, and lower a structured world representation into an existing compiler.[1] [2] [3] This replaces informal experimentation with an auditable scientific loop.

The consumer-hardware constraint is also valuable. It forces the architecture to expose costs that hyperscale work can conceal: state materialization, optimizer memory, sequence length, update frequency, checkpoint provenance, and the distinction between a representational feature and a usable learned capability. The measured 53.93M ceiling for a full pass and the 155.35M failure boundary are useful design facts even though they are not intelligence results.[1]

### 4.2 Model value: not yet demonstrated

The current checkpoint cannot be valued as a useful general model based on the available evidence. Its training corpus is too small and too dominated by archived dialogue to establish a sovereign learning system, its first protected baseline failed all three cases, and the scaling ladder did not evaluate generalization.[1] [3] No candidate has yet demonstrated improvement over the parent.

This distinction prevents a common error: confusing ownership of weights with ownership of capability. A model can be wholly first-party and still not perform a valuable task. Conversely, third-party components can be used as temporary teachers without making the final system a wrapper, provided the shipped core has an independently measured capability and can run without the teacher.

### 4.3 Potential product value: high if the thesis is realized

A local system that actually learns a user’s worlds, preserves provenance, exports editable typed artifacts, and improves without silent regression would be materially different from a prompt-routing application. Its value would come from **continuity, inspectability, editability, and ownership**, not from claiming that every mathematical primitive is unprecedented.

The product claim should be tied to observable outcomes. A buyer does not receive value from “Hebbian plasticity” as a label. A buyer receives value if the system can retain a newly demonstrated rule, apply it to a different object or scene, identify what evidence supports the result, admit what was inferred, survive restart, and improve later without losing previous abilities.

## 5. What is not novel

The individual ingredients of Primus occupy mature or rapidly developing fields. Describing them accurately strengthens the project because it reveals where original work is actually required.

| Primus ingredient | Relevant prior art | Novelty implication |
|---|---|---|
| **Selective state-space backbone** | Mamba introduced input-dependent selective SSMs and a hardware-aware scan with linear sequence scaling.[4] RWKV and related recurrent models also target constant-memory inference. | A Mamba-like backbone is not a novel principle. Primus may contribute a locally maintainable implementation and measured consumer-GPU tradeoffs. |
| **Surprise-sensitive long-term memory** | Titans updates a neural memory at test time using surprise, momentum-like accumulated surprise, and forgetting, and reports broad benchmark results.[7] | “Surprise determines what to remember” is not a new claim. Primus needs a distinct update rule or a superior governed consolidation result. |
| **Hebbian fast weights** | Hebbian fast weights for rapid binding and one-shot learning were demonstrated years before Primus.[10] | The existence of a fast Hebbian matrix is not novel. Stability, routing, and coupling to slow consolidation could be. |
| **Fast and slow plasticity** | Complementary learning systems date to at least 1995, and modern work derives joint fast-control and slow-learning rules with convincing evidence.[11] [12] | The biological analogy and dual-timescale idea are established. Primus must show a new computational coupling or systems result. |
| **Replay and sleep consolidation** | Generative replay is established in continual learning; brain-inspired replay has scaled to demanding class-incremental tasks.[13] The 2026 “Language Models Need Sleep” work explicitly proposes wake/sleep, replay, fast-to-slow consolidation, parameter activation, and dreaming, with experiments.[8] | A wake/sleep metaphor or replay loop is not novel. The auditable promotion transaction may still be distinctive. |
| **Holographic representations** | HRR/vector-symbolic representation predates modern deep learning; differentiable HRR work improved numerical stability and retrieval by more than 100×.[14] | HRR is not proprietary to Primus. A new capacity-control or integration result would require measurement. |
| **Compression as learning** | MDL explicitly treats learning as finding compressive regularity and balancing fit against model description length.[15] Recent work formally connects predictive coding to MDL objectives.[16] | “Intelligence is compression” is a research lineage, not a Primus invention. Primus currently invokes MDL more than it operationalizes it. |
| **Typed scene/world graphs** | 3D/4D scene graphs already model grounded entities, attributes, relations, hierarchy, dynamics, actions, and uncertainty as open research problems.[19] | Typed persistent world state is valuable but not new by itself. |
| **Neuro-symbolic world models** | WorldCloner learns symbolic transition rules for novelty detection and imagination-based adaptation; NeuroSymLand builds uncertainty-aware scene graphs and executes auditable symbolic programs over them.[20] [21] | Neural-to-symbolic world state and executable rules have prior art. Primus must distinguish itself through domain generality, compiler coupling, and learning governance. |
| **Model candidates, lineage, and shadow comparison** | MLflow provides model lineage, versioning, aliases, validation tags, and controlled promotion. AWS documents shadow deployment for non-impacting model comparison. SLSA specifies digest-bound artifact provenance and isolated production.[22] [23] [24] [25] | Candidate isolation and promotion are established MLOps practices. Applying them to cognitive consolidation is good engineering, not a new governance principle. |

## 6. The strongest counterexamples

### 6.1 Titans

Titans is a direct counterexample to broad claims around active test-time memory. It frames attention as short-term memory, introduces a deep neural long-term memory that changes at test time, uses a surprise signal to control memorization, and reports results across language, reasoning, genomics, time series, and context lengths above two million tokens.[7] Primus differs by using a selective-state backbone, an explicit lifecycle, evidence governance, and a typed world compiler boundary. But any scientific claim about surprise-driven internal memory must compare against Titans or its descendants.

### 6.2 Language Models Need Sleep

This work is an even stronger counterexample to the lifecycle thesis. It explicitly argues that continual learners should not have a static train/test division, separates active and sleep stages, transfers fragile short-term memory into slower components, uses replay and dreaming, and evaluates the proposal.[8] Therefore, Primus cannot claim scientific novelty for “models need sleep,” “wake versus sleep,” or “fast-to-slow consolidation.”

The remaining opening is the **governed form** of consolidation. Primus can make sleep produce a candidate model and candidate beliefs whose source evidence, training inputs, regressions, uncertainty, and executable effects are independently checked before promotion. The prior-art review found model-governance systems and sleep-learning systems, but not a strong peer-reviewed demonstration of their full integration into an evidence-native world builder.

### 6.3 Eyla

Eyla is a warning especially relevant to Primus. It proposed a local-first identity-anchored architecture combining SSM sidecars, episodic memory, calibrated uncertainty, adversarial defense, and biologically inspired lifecycle modules. Its implementation attempt produced a 1.27B-parameter system with 86 named subsystems, but the side modules contributed less than 2% to output and behavior remained indistinguishable from the donor model.[9]

Eyla’s failure establishes an important standard:

> **Named modules and passing component tests do not prove that an architecture influences behavior.**

Primus has already reduced this risk through stricter repository law, source audits, real failure records, candidate isolation, and explicit non-claims.[1] [3] It still needs influence and ablation tests proving that the fast weights, episodic buffer, sleep process, associative memory, typed world tokens, and evidence gates each alter measured outcomes in the intended direction.

### 6.4 SingularityNET/OpenCog PRIMUS

The most consequential external finding is a naming and conceptual collision. SingularityNET/OpenCog publicly describes **PRIMUS** as a cognitive architecture, and its December 27, 2025 world-model paper proposes a multi-rate neuro-symbolic system for robotics and game worlds.[17] [18] Its design includes explicit entities and programs, hypervector associative memory, dense neural tensors, persistent identity, evidence anchoring, uncertainty and staleness, predictive dynamics, program space, continual learning, and fast/mid/slow loops.[17]

The overlap is substantial enough that NeuroCognica should not publicly claim that the name PRIMUS, a multi-rate neuro-symbolic world model, evidence anchoring, or typed world programs are uniquely its invention. This report does **not** determine trademark rights or infringement. It does establish the need for prompt naming, trademark, publication, and positioning review before public launch or patent drafting.

There are still concrete differences. NeuroCognica Primus is currently a local Python/PyTorch system with a first-party selective-state substrate, a ChronoSophia-specific typed compiler boundary, SHA-bound candidate manifests, an immutable evidence ledger, and explicit parent promotion controls.[1] [2] [3] OpenCog PRIMUS is built around Hyperon/Atomspace, MeTTa, probabilistic logic, hypervectors, and distributed cognitive synergy.[17] [18] Those differences can support a distinct implementation identity, but they do not erase the conceptual and naming prior art.

## 7. What may be genuinely distinctive

The strongest candidate is not a single neural layer. It is a **cross-layer control contract**.

### 7.1 Evidence-native learning and execution

Primus’s world schema makes evidence, uncertainty, camera state, capability status, and compiler-owned operations explicit.[2] If the learned model is trained to emit and revise this state—and if generated content cannot silently impersonate observed content—the system would differ materially from most generative world models, whose latent state and provenance are opaque.

The distinctive property would be the invariant:

> **Every world-state claim remains linked to how it was observed, inferred, generated, or revised; every executable action remains within a typed compiler capability; every learned change remains a candidate until held-out evidence authorizes promotion.**

Elements of this invariant exist elsewhere. Probabilistic scene graphs carry uncertainty and reasoning provenance; artifact systems carry hashes and lineage; model registries manage promotion; neuro-symbolic systems execute typed rules.[21] [22] [23] [24] [25] The potentially novel contribution is their integration into the cognition loop rather than their use as surrounding deployment tooling.

### 7.2 Consolidation as a governed transaction

Most continual-learning research asks whether a model remembers. Primus can additionally ask whether the memory change is **admissible**. A sleep cycle can be treated as a transaction that begins from sealed state, consumes a declared episode set and replay set, produces candidate weights and beliefs, runs protected evaluations, records regressions and uncertainty, and either promotes or rejects the mutation.

This is not yet proven end to end. It is nevertheless a credible engineering research contribution because it converts a vague “self-improving model” into a reversible, inspectable lifecycle.

### 7.3 Typed world learning coupled to a real compiler

The implemented WorldProgram is object-agnostic and lowers to ChronoSophia’s S³V representation while preserving a lossless envelope for fields S³V v1 does not natively support.[2] A learned model that predicts these programs would not merely generate descriptions. It would predict persistent state and compiler-owned operations that can be validated and executed.

Typed program synthesis and neuro-symbolic world models are established. The distinctive opportunity is to make the **same learned representation** support state estimation, action-conditioned prediction, provenance, uncertainty, user editing, and executable world construction on local hardware.

### 7.4 Sovereign ownership as a system property

“Local AI” alone is not novel. Primus can define sovereignty more rigorously: local inference, local learning, readable state, exportable memory, reproducible candidates, independent operation without a provider, and no hidden dependence on an external model at runtime. That combination can be commercially differentiating even if it is not scientific novelty.

## 8. Novelty rating

| Dimension | Current rating | Rationale | What would raise the rating |
|---|---|---|---|
| **Scientific novelty** | **Low to medium, unproven** | Components and high-level lifecycle have strong prior art. The current model has not learned the world schema or demonstrated a new continual-learning effect. | A formal coupling mechanism plus end-to-end results showing gains that survive ablation against Mamba, Titans-style memory, replay, and neuro-symbolic baselines. |
| **Engineering novelty** | **Medium to high** | The repository combines first-party local training, fail-closed candidates, evidence ledgers, memory-bounded scan, typed world state, and a real compiler boundary with unusual rigor. | Complete the learned world-program path, consolidate evidence and model promotion into one verified transaction, and publish reproducible benchmarks. |
| **Product differentiation** | **Potentially high; currently pre-capability** | Evidence-aware local world construction and user-owned continual learning would be meaningfully different from prompt wrappers. Current model quality and end-to-end world building are unproven. | Demonstrate a user-visible task where Primus learns, builds, explains evidence, accepts edits, persists the change, and avoids regression offline. |
| **Patent novelty** | **Unknown; prior-art risk is high** | Dense prior art exists across every broad component, and an unrelated PRIMUS architecture occupies closely related conceptual territory. | Commission a professional search, identify narrow mechanism claims, preserve dates and inventorship, and avoid unsupported broad claims. |

## 9. The principal technical risk

The largest risk is **architecture-by-aggregation**: a system can contain many correct components without learning a capability that depends on them. Eyla demonstrates this failure vividly.[9] Primus’s own repository currently shows an analogous but earlier boundary: the world schema is correct and tested, but not wired into the learner; the parent model runs, but has not demonstrated useful reasoning; the lifecycle exists, but no candidate has defeated and replaced the parent.[1] [2] [3]

The remedy is not more modules. It is a narrow end-to-end experiment with ablations.

| Failure mode | Required control |
|---|---|
| A component exists but does not affect output | Measure activation, gradient/update magnitude, intervention effect, and behavioral delta when removed. |
| The full system improves because it has more parameters | Compare at equal parameter count, data, tokens, and compute. |
| Replay appears to help because evaluation leaked into training | Use manifest-bound whole-family holdouts and reject source overlap. |
| World-program accuracy hides invalid executable behavior | Compile outputs, execute in controlled worlds, and score action validity and state consequences. |
| The system remembers new tasks by forgetting old ones | Track backward transfer, forgetting, protected regressions, and calibration across sequential cycles. |
| Generated evidence contaminates observed truth | Require evidence-kind labels, source hashes, confidence, and fail-closed promotion policy. |
| Biological language substitutes for mechanism | Name variables, updates, state transitions, and metrics; treat “sleep,” “dream,” and “hippocampus” as metaphors only. |

## 10. The decisive experiment

The next model should not be trained primarily on conversation turns. It should be a **53.93M-class world core trained on grounded, versioned world trajectories** represented in the typed schema. The 53.93M rung is justified as the largest configuration that completed the existing full-pass harness on the target RTX 3060; this is a hardware starting point, not a claim of sufficient cognitive capacity.[1]

A decisive study should compare six systems under the same data, parameter, token, and compute budgets.

| System | Purpose |
|---|---|
| **A. Static selective-state baseline** | Establish what the backbone learns without online plasticity or sleep. |
| **B. A + fast weights** | Isolate immediate adaptation. |
| **C. B + episodic buffer and replay** | Measure retention and replay value. |
| **D. C + sleep consolidation** | Test whether periodic fast-to-slow transfer improves the stability–plasticity tradeoff. |
| **E. D + typed world-program objectives** | Test whether explicit entities, relations, actions, evidence, and uncertainty improve generalization and execution validity. |
| **F. Full evidence-gated system** | Test whether candidate isolation and promotion preserve capability across repeated learning cycles. |

Training trajectories should span many object classes, operation families, compositions, camera states, materials, temporal changes, and counterfactual actions. Object names must not select architectural recipes. Evaluation must use whole object-class, whole operation-family, and composition holdouts rather than random example splits.[2]

The measurement suite should include action-conditioned next-state accuracy, entity and relation persistence, operation validity, held-out composition success, calibration, evidence/provenance completeness, adaptation speed, backward transfer, forgetting, replay contamination, candidate regression rate, compiler acceptance, latency, peak memory, energy or wall-time cost, and user-correctability. Visual tasks additionally require artifact and render witnesses rather than token accuracy alone.

The scientific hypothesis should be falsifiable:

> **At equal resources, the complete Primus coupling will learn new world dynamics faster than the static baseline, retain earlier dynamics better than naive fine-tuning, generalize better to held-out compositions than untyped sequence learning, and produce fewer unsupported or invalid actions because evidence, uncertainty, and compiler capability are explicit.**

If System F does not outperform the strongest partial system, the extra architecture should be removed or revised. A failed ablation is more valuable than preserving an impressive diagram.

## 11. Commercial implications

Primus should not be marketed as a novel foundation model today. It can accurately be described as an **original NeuroCognica research architecture and local prototype integrating established methods under an evidence-first world-learning contract**. That language claims ownership of the implementation and research direction without claiming ownership of Mamba, replay, HRR, MDL, scene graphs, or sleep-inspired learning. It can also accurately state that the documented Primus conception by Michael Holt and NeuroCognica predates the later external PRIMUS publication, while avoiding any unreviewed patent or trademark claim.[27] [28]

The initial commercial value should come from an evidence-rich artifact workflow rather than an assertion of autonomous intelligence. A viable product can expose a coarse editable world state, its source evidence, uncertainty, and operations while generative refinements remain plainly labeled. This aligns product value with what can be inspected and corrected.

| Claim category | Safe current wording | Wording to avoid until proven |
|---|---|---|
| **Ownership** | “NeuroCognica’s first-party local world-core prototype and evidence pipeline.” | “The first sovereign cognitive architecture.” |
| **Novelty** | “A distinctive integration of local selective-state learning, typed executable world state, and governed promotion.” | “A wholly new learning paradigm” or “the first model that sleeps.” |
| **Capability** | “The schema and compiler bridge are implemented and losslessly tested.” | “Primus understands or builds arbitrary worlds.” |
| **Continual learning** | “The lifecycle and candidate gates are implemented; end-to-end continual-learning value remains under evaluation.” | “Learns forever without forgetting.” |
| **Model quality** | “The current checkpoint is a research parent with a recorded failed baseline.” | “Production-ready intelligence.” |
| **World-builder** | “Research path toward an evidence-native world builder.” | “World-builder achieved.” |

## 12. Patent and naming cautions

This report is not legal advice. From a technical prior-art perspective, broad claims are unlikely to be defensible because the constituent mechanisms are well populated. If intellectual-property protection is desired, candidate claims should focus on precise mechanisms such as the data structures, transition rules, evidence constraints, promotion transaction, or compiler coupling—not on “AI sleep,” “fast and slow weights,” “world model,” “holographic memory,” or “local sovereign AI” in the abstract.

A patent professional should search issued patents, published applications, papers, repositories, product documentation, and earlier public disclosures. The search must include Mamba/SSM implementations, test-time memory, continual-learning replay, model registry and shadow-deployment systems, software artifact provenance, neuro-symbolic world models, scene graphs, typed program synthesis, OpenCog/Hyperon, and the unrelated PRIMUS architecture.[4] [5] [6] [7] [8] [9] [10] [11] [12] [13] [14] [15] [16] [17] [18] [19] [20] [21] [22] [23] [24] [25]

The public name overlap deserves separate counsel, even though the dated evidence supports the earlier independent conception by Michael Holt and NeuroCognica. The unrelated OpenCog/SingularityNET use is not obscure: an official project page identifies PRIMUS as a cognitive architecture, and the December 2025 paper uses the name in a world-model context closely adjacent to NeuroCognica’s ambitions.[17] [18] Even if the implementations and businesses differ, external audiences may assume affiliation or derivation. The naming decision should be resolved before major publication, fundraising, patent positioning, or storefront branding.

## 13. Final conclusion

**Primus is worth building—but only if it is treated as a falsifiable systems research program, not as a collection of impressive component names.**

The project’s scientific inputs are mostly inherited from established research. That is normal. Novel systems are often built from known mathematics. The question is whether the integration creates a new measurable property. Primus’s best chance is not to claim that selective state, fast weights, sleep, replay, HRR, MDL, or scene graphs were invented here. Its best chance is to demonstrate that an evidence-native coupling of those ideas yields a local world learner that can change safely, explain what it knows, preserve what it observed, execute only what its compiler supports, and improve without hidden regression.

Today, the repository proves a credible substrate and governance foundation. It does not yet prove the mind described by the thesis. The next step is therefore not a larger prompt model and not another architectural layer. It is the grounded world-trajectory experiment, run with ablations and protected holdouts, that can convert an interesting architecture into evidence.

If that experiment succeeds, Primus could have **high engineering and product value** and a legitimate claim to a distinctive world-learning architecture. If it fails, the evidence system will still have done its job: it will identify which parts are real, which are ornamental, and where the next original idea is actually required.

## References

[1]: ../../STATUS.md "Primus STATUS.md — verified repository state and non-claims, August 26, 2026"
[2]: ../../CCF_Sovereign/docs/WORLD_SCHEMA_V1.md "Primus Typed World Schema v1"
[3]: ../defense_evidence/benchmarks/ccf_world_core_day_one_2026-08-26.md "CCF World Core Day-One Evidence Summary, August 26, 2026"
[4]: https://arxiv.org/html/2312.00752 "Gu and Dao, Mamba: Linear-Time Sequence Modeling with Selective State Spaces, 2023/2024"
[5]: https://arxiv.org/html/2412.14847v2 "A Survey of RWKV, 2025"
[6]: https://arxiv.org/html/2407.12492v3 "Temporal Test-Time Adaptation with State-Space Models, 2024"
[7]: https://arxiv.org/html/2501.00663 "Behrouz, Zhong, and Mirrokni, Titans: Learning to Memorize at Test Time, 2024"
[8]: https://arxiv.org/html/2606.03979v1 "Behrouz, Hashemi, and Mirrokni, Language Models Need Sleep: Learning to Self-Modify and Consolidate Memories, 2026"
[9]: https://arxiv.org/html/2604.00009v1 "Arif, Eyla: Toward an Identity-Anchored LLM Architecture with Integrated Biological Priors, 2026"
[10]: https://arxiv.org/abs/1807.05076 "Munkhdalai and Trischler, Metalearning with Hebbian Fast Weights, 2018"
[11]: https://pubmed.ncbi.nlm.nih.gov/7624455/ "McClelland, McNaughton, and O'Reilly, Why There Are Complementary Learning Systems in the Hippocampus and Neocortex, 1995"
[12]: https://elifesciences.org/reviewed-preprints/105043 "Bicknell and Latham, Fast and Slow Synaptic Plasticity Enables Concurrent Control and Learning, 2025"
[13]: https://www.nature.com/articles/s41467-020-17866-2 "van de Ven, Siegelmann, and Tolias, Brain-Inspired Replay for Continual Learning with Artificial Neural Networks, 2020"
[14]: https://proceedings.neurips.cc/paper/2021/hash/d71dd235287466052f1630f31bde7932-Abstract.html "Ganesan et al., Learning with Holographic Reduced Representations, NeurIPS 2021"
[15]: https://homepages.cwi.nl/~paulv/course-kc/mdlintro.pdf "Grünwald, A Tutorial Introduction to the Minimum Description Length Principle"
[16]: https://arxiv.org/html/2505.14635v1 "Prada et al., Bridging Predictive Coding and MDL: A Two-Part Code Framework for Deep Learning, 2025"
[17]: https://singularitynet.io/wp-content/uploads/2025/12/PRIMUS-world-modeling_v2.pdf "Goertzel, World Modeling in Hyperon for PRIMUS: A Multi-Rate, Neuro-Symbolic Approach for Robotics and Game Worlds, December 27, 2025"
[18]: https://singularitynet.io/research/opencog-hyperon/ "SingularityNET, OpenCog Hyperon official research page"
[19]: https://arxiv.org/html/2606.19383v1 "Rotondi et al., 3D Scene Graphs: Open Challenges and Future Directions, 2026"
[20]: https://arxiv.org/html/2301.06294 "Balloch et al., Neuro-Symbolic World Models for Adapting to Open World Novelty, AAMAS 2023"
[21]: https://arxiv.org/html/2510.22204v2 "Qian et al., Human-Inspired Neuro-Symbolic World Modeling and Logic Reasoning for Interpretable Safe UAV Landing Site Assessment, 2026"
[22]: https://mlflow.org/docs/latest/ml/model-registry/ "MLflow Model Registry documentation"
[23]: https://aws.amazon.com/blogs/machine-learning/deploy-shadow-ml-models-in-amazon-sagemaker/ "AWS, Deploy Shadow ML Models in Amazon SageMaker, 2021"
[24]: https://slsa.dev/spec/v1.0/provenance "SLSA Provenance specification v1.0"
[25]: https://slsa.dev/spec/v1.0/requirements "SLSA artifact production and isolation requirements v1.0"
[26]: ../../Sovereign%20Textual%20Mind%20Paradigm.md "Origin of a Sovereign Textual Mind: The Chrono-Compressive Field Paradigm"
[27]: ../provenance/PRIMUS_NAME_PROVENANCE_2026-08-26.md "NeuroCognica, Provenance record — the name Primus at NeuroCognica, sealed 2026-08-26"
[28]: ../provenance/evidence/2025-06-11_Full_Report_The_First_Emergence_NeuroCognica_Primus.pdf "Michael Holt / NeuroCognica, Full Report: The First Emergence — NeuroCognica Primus, Google Docs modified 2025-06-11; SHA-256 sealed repository export"