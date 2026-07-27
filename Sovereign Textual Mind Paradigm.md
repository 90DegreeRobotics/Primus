# **ORIGIN OF A SOVEREIGN TEXTUAL MIND: THE CHRONO-COMPRESSIVE FIELD PARADIGM**

## **1\. The Entropy of the Monolith: A Critique of Static Intelligence**

The contemporary pursuit of Artificial General Intelligence (AGI) has become synonymous with industrial scale. The prevailing paradigm—the "Epochal Monolith"—relies on the construction of static, gargantuan matrices of weights, trained on massive clusters of GPUs that consume megawatts of power. These models are characterized by a fundamental rigidity: they are snapshots of the internet frozen in time, incapable of learning from subsequent interaction without prohibitively expensive re-training or the risk of catastrophic forgetting. This industrial dogma assumes that intelligence is a product of dataset size and parameter count, governed by scaling laws that demand exponentially increasing resources for diminishing returns.

For a sovereign entity—a single researcher, a localized system, or a distinct desktop node—to possess a textual mind, we must reject the premise that intelligence requires a hyperscale data center. The current architecture of Large Language Models (LLMs), primarily the Transformer, is inherently inefficient for continuous, autonomous existence. It suffers from the "flat sequence fallacy," treating time as a spatial dimension (the context window) that scales quadratically (![][image1]), rendering infinite context memory impossible on consumer hardware.1 Furthermore, the reliance on global Backpropagation (BP) for all updates necessitates storing vast activation maps, creating a memory wall that locks learning behind the doors of high-end industrial computation.3

This report proposes a radical departure: the **Chrono-Compressive Field (CCF)**. We posit that a sovereign textual mind can be instantiated on a single high-end consumer desktop (e.g., NVIDIA RTX 4090\) by reframing the problem of learning not as global function approximation over a static dataset, but as a continuous, homeostatic process of **Minimum Description Length (MDL) optimization** over a temporal stream. By synthesizing the linear efficiency of **Structured State Space Models (SSMs)** like Mamba and RWKV, the robustness of **Holographic Associative Memory**, and the biological wisdom of **Sleep-Dependent Consolidation**, we define a system that grows, sleeps, dreams, and internalizes knowledge incrementally. This is not a "fine-tuned" model; it is a living dynamical system.

### **1.1 The Inefficiency of the "Epoch"**

The concept of the "epoch"—the iterative cycling through a static dataset—is an artifact of batch processing that has no analogue in biological or physical reality. In the known universe, time is unidirectional. An intelligent agent does not see the same data twice in the exact same context. The Epochal Monolith wastes massive computational energy re-processing redundant syntax to squeeze out marginal semantic gains, treating "learning" as the global minimization of a loss function over a fixed distribution.

This approach is mathematically flawed for a sovereign mind because the data distribution is **non-stationary** (drifting). When a standard LLM is exposed to a new stream of information (e.g., a new field of physics), the global gradient updates required to minimize the loss on the new data inevitably destruct the interference patterns that encoded the old data—a phenomenon known as **Catastrophic Forgetting**. Studies indicate that standard fine-tuning can result in an 89% loss of previously learned knowledge.5 Current mitigations, such as Retrieval Augmented Generation (RAG), are admissions of defeat: they acknowledge the model cannot *learn*, so they attach an external hard drive (vector database) and call it memory. A true mind does not retrieve; it *knows*.

### **1.2 The Sovereign Constraint**

We operate under the "Sovereign Node" constraint:

1. **Hardware:** Single Consumer GPU (\~24GB VRAM).
2. **Data:** Continuous, infinite stream (no "dataset" size).
3. **Objective:** Internalization of knowledge (no external RAG).
4. **Lifecycle:** Continuous operation (no "train" vs "inference" distinct phases, but rather a circadian rhythm).

To achieve this, we must look beyond the Transformer. We require an architecture where the memory footprint is constant (![][image2]) regardless of the sequence length, and where plasticity (learning) is local and energetic, rather than global and error-driven.

## ---

**2\. Survey of the Known World: Alternatives to the Monolith**

Before constructing the CCF, we must ruthlessly survey the landscape of non-standard learning paradigms. The "Known World" of Deep Learning contains scattered islands of innovation that, when unified, offer a path out of the Monolith.

### **2.1 The Retreat from Quadratic Attention: Mamba and RWKV**

The Transformer's attention mechanism calculates the correlation between every token and every other token (![][image3]). While powerful for static analysis, this quadratic cost is the primary barrier to lifelong learning.

* **Structured State Space Models (SSMs) & Mamba:** Mamba 6 introduces a "Selection Mechanism" into SSMs. It allows the model to selectively propagate or forget information along the sequence dimension based on the current input content. Crucially, Mamba operates with linear time complexity (![][image4]) and constant inference memory. It maintains a compressed hidden state ![][image5] that evolves over time. This state *is* the memory. Unlike the Transformer, which must "re-read" the past (via the KV cache), Mamba "carries" the past.
* **RWKV (Receptance Weighted Key Value):** RWKV 8 bridges the gap between RNNs and Transformers. It reformulates the attention mechanism as a linear recurrence, allowing for parallelization during training (like a Transformer) but constant-memory inference (like an RNN). Recent iterations (RWKV-7 "Goose") introduce vector-valued states and dynamic "state tuning," which allows the model to adjust its internal state based on context without updating the global weights—a rudimentary form of fast-weight plasticity.10

**Insight:** Both Mamba and RWKV prove that high-performance language modeling does not require ![][image1] memory. They provide the necessary *substrate* for a Sovereign Mind: a backbone that can run indefinitely on a single GPU without crashing from memory exhaustion.

### **2.2 The Plasticity Frontier: Beyond Backpropagation**

Global Backpropagation (BP) is physically untenable for a continuous learner because it locks the entire system into a synchronous update cycle and requires storing activations for the backward pass.3

* **Hebbian Learning:** Biological systems use local rules: "neurons that fire together, wire together." Modern interpretations, such as "Match-and-Control" 11, demonstrate that Hebbian-like mechanisms can approximate attention. If pre-synaptic and post-synaptic activities are correlated, the synaptic weight is boosted locally. This allows for *asynchronous* updates—parts of the network can learn while others act.
* **Fast Weights:** The concept of "Fast Weights" 13 suggests separating memory into "Slow Weights" (the static model parameters, akin to DNA or long-term structural connectivity) and "Fast Weights" (dynamic, rapidly decaying changes to synapses, akin to working memory). Linear Transformers and RWKV can be mathematically interpreted as systems manipulating Fast Weights.
* **Target Propagation & Forward-Forward:** Algorithms like Hinton's Forward-Forward 15 and Target Propagation 17 attempt to replace BP with local error signals. While they have not yet matched BP's performance on static benchmarks, they offer a crucial advantage for the Sovereign Mind: they enable learning *forward* in time, without stopping to propagate errors backward through the entire history.

### **2.3 Continual Learning and Memory Consolidation**

The battle against Catastrophic Forgetting has yielded several key strategies:

* **Elastic Weight Consolidation (EWC):** EWC 18 calculates the Fisher Information Matrix to identify which weights are critical for past tasks and "locks" them (high rigidity), forcing new learning into less critical weights. This is akin to synaptic consolidation.
* **Generative Replay:** Instead of storing old data (which violates storage constraints), the model generates "dreams" of its past experiences and mixes them with new data during training.19 This **Pseudo-Rehearsal** 21 creates a "training loop" where the model teaches itself to preserve its own manifold.
* **Sparse Memory Finetuning (SMF):** Recent work shows that updating only a sparse subset of parameters (or low-rank adapters) significantly reduces forgetting rates compared to full finetuning.5

### **2.4 Compression as Cognition**

The **Minimum Description Length (MDL)** principle 22 frames learning as data compression. A model that understands the underlying causal laws of a text stream can compress it more efficiently than one that memorizes it.

* **Neural Arithmetic Coding:** Language models can be viewed as probability estimators for arithmetic coding.24 The "better" the model, the narrower the prediction interval, and the fewer bits required to encode the stream. This links information theory directly to the "energy" of the system: high surprise equals high code length (high energy).

## ---

**3\. Re-Framing the Problem: The Physics of the Textual Field**

To engineer the Sovereign Mind, we must abandon the "computer science" view of filling a buffer and processing a batch. Instead, we adopt a **Physical** view. The Sovereign Mind is a localized region of low entropy maintaining itself against a high-entropy stream of text.

### **3.1 Text as a Statistical Field**

We treat the incoming text not as a sequence of discrete tokens ![][image6], but as a **Statistical Field** ![][image7]. The "meaning" of a text is not in the tokens themselves, but in the latent relationships (correlations) between them.

The goal of the Sovereign Mind is **Homeostasis**: to minimize its internal **Variational Free Energy** (![][image8]) with respect to the external field.

![][image9]

* **Prediction Error (Surprise):** When the model encounters text it cannot predict (e.g., a new scientific discovery), the Free Energy spikes. In a physical system, this energy must be dissipated. In the Sovereign Mind, this dissipation occurs via **Plasticity** (learning).
* **Model Complexity (MDL):** We cannot simply minimize error by memorizing (which would maximize model entropy). We must minimize error while maintaining a *low-complexity* (compressed) internal representation. This forces the model to discover **Abstractions**—the laws of physics, the rules of grammar, the logic of argumentation—because abstractions are the most efficient compression of reality.26

### **3.2 The Dynamical Systems View**

The model is a dynamical system defined by the state equation:

![][image10]

* ![][image5]: The "Conscious State" (Current context, short-term memory).
* ![][image11]: The "Long-Term Memory" (Holographic weights, equivalent to the Connectome).
* ![][image12]: The "Working Memory" (Synaptic transience, equivalent to calcium concentrations in synapses).
* ![][image13]: The sensory input (Text stream).

Standard training (SGD) tries to optimize ![][image11] directly from ![][image13]. This is inefficient and unstable. The Sovereign Paradigm introduces an intermediate timescale: ![][image12] absorbs the immediate shock of ![][image13], stabilizing the system so that ![][image11] can be updated slowly and coherently during sleep.

### **3.3 Compression as the Objective Function**

We posit that **Intelligence is Lossless Compression of the Interaction History**.

If the Sovereign Mind can perfectly compress the stream of text it has seen, it has "learned" it.

* **The Loss Function:** Instead of Cross-Entropy, we use a **MDL-based Loss**.23
  ![][image14]
  Where ![][image15] is the bits required to encode the new text given the current model (residuals), and ![][image16] is the bits required to encode the *change* to the model parameters. This penalty on parameter change (![][image17]) enforces stability and prevents the model from overfitting to the recent stream (Catastrophic Forgetting). It forces the model to find the *minimal* change to its weights that explains the new data—often by generalizing rather than memorizing.

## ---

**4\. The Chrono-Compressive Field (CCF): A New Paradigm**

We propose the **Chrono-Compressive Field (CCF)**, a tripartite architecture designed to operate continuously on a sovereign node. It consists of:

1. **The Substrate:** A Linear-State Backbone (Mamba/RWKV).
2. **The Memory:** Holographic Associative Fields (HAM).
3. **The Rhythm:** A Circadian Cycle of Awake (Acquisition) and Sleep (Consolidation).

### **4.1 The Substrate: Mamba-RWKV Hybrid**

We reject the Transformer. The Sovereign Mind utilizes a **Selective State Space Model (Mamba)** for its efficiency.

* **Mechanism:** Mamba discretizes a continuous system ![][image18] into a recurrent form ![][image19].
* **Selectivity:** The matrix ![][image20] is not static; it is a function of the input ![][image13] (![][image21]). This allows the model to *selectively* remember or ignore information. For a sovereign mind, this is the "attention" mechanism: it decides what enters the long-term state ![][image5].1
* **State Tuning (RWKV-7):** We augment Mamba with the **State Tuning** mechanism from RWKV-7.10 This allows the hidden state to be "guided" by a larger, frozen teacher model (if available) or by internal heuristics during test time, effectively increasing the model's expressivity without changing its weights.

### **4.2 The Memory: Holographic Associative Weights (HAM)**

To solve the storage problem (millions of pages on 24GB VRAM), we utilize **Holographic Reduced Representations (HRR)**.29

* **Weights as Holograms:** Standard neural networks use scalar weights. In CCF, the weight matrices are treated as **Holographic Fields**. A "memory" (e.g., a fact read in a book) is encoded as a vector trace ![][image22].
* **Superposition:** We store this memory by *adding* it to the existing weight matrix: ![][image23].
* **Orthogonality:** In high-dimensional space (e.g., ![][image24]), random vectors are quasi-orthogonal. This means we can superimpose thousands of memories into the same weight matrix without them destroying each other. The "noise" introduced by other memories is negligible until the capacity limit is reached.30
* **Retrieval:** The network retrieves information via **Circular Correlation** (the inverse of convolution). The output is the desired vector plus some noise (which is filtered out by the non-linearities of the network).
  * *Mathematical formulation:*
    Encoding: ![][image25] (Bind concept A and B)
    Superposition: ![][image26]
    Decoding: ![][image27] (Correlate A with Memory M to retrieve B).
    This turns the entire neural network into a **content-addressable memory**, solving the RAG problem. The model doesn't need to "search" a database; the answer is distributed holographically within its own synaptic weights.

### **4.3 The Plasticity: Fast and Slow Weights**

We implement a **Dual-Process Theory** of plasticity.32

* **Fast Weights (![][image12]):** These are essentially a **LoRA (Low-Rank Adapter)** layer that is highly plastic. During the "Awake" phase (processing the user's daily stream), *only* these Fast Weights are updated.
  * *Update Rule:* We use a **modified Hebbian rule** (NoProp).34
    ![][image28]
    This update is local and instant. It does not require backpropagation through time. It captures the "gist" of the current document stream immediately.
* **Slow Weights (![][image11]):** The massive Holographic Mamba backbone. These weights are **frozen** during the day. They are the "Long Term Memory." They are updated only during the "Sleep" phase via consolidation.

## ---

**5\. The Circadian Training Lifecycle**

The Sovereign Mind does not have "epochs." It has a **Day/Night Cycle**.

### **5.1 Phase 1: Awake (Inference & Acquisition)**

*Status: User is active. System is processing text stream.*

* **Operation:** The model runs in inference mode.
* **Hebbian Micro-Updates:** As tokens flow in, the **Fast Weights** are updated in real-time using the local error signal (Surprise). This allows the model to "adapt" to the current document's style and vocabulary instantly.35
* **The Hippocampal Buffer (STEB):** When the model encounters a sequence with **High Surprise** (Free Energy Spike), it flags this sequence as "Novel." It does *not* train on it immediately (which causes freezing). Instead, it compresses this sequence and pushes it to a **Short-Term Episodic Buffer (STEB)** in RAM (acting as the Hippocampus).19

### **5.2 Phase 2: Deep Sleep (Consolidation)**

*Status: User is away. System detects idle GPU.*

* **Generative Replay (Dreaming):** To prevent catastrophic forgetting, the model must "rehearse" what it already knows. It enters a generative loop, producing sequences of text based on its current **Slow Weights**. These are its "Dreams"—a compression of its prior knowledge.38
* **The Mixed Batch:** The system creates a training batch consisting of:
  1. **Fresh Memories:** High-surprise sequences from the STEB.
  2. **Dreams:** Synthetic sequences generated from Slow Weights (Pseudo-Rehearsal).
* **GaLore Optimization:** The system performs **Gradient Descent** on the Slow Weights using this mixed batch. To fit on a single GPU, we use **GaLore** 4, which projects the gradients into a low-rank subspace. This allows us to update the massive 7B parameter model using a fraction of the VRAM (e.g., \<10GB).
* **Holographic Integration:** The updates are applied additively to the Holographic Slow Weights. The "Dreams" ensure that the new memories (STEB) are integrated into the existing manifold without overwriting the orthogonal vectors of old memories.5

### **5.3 Phase 3: REM (Pruning & Normalization)**

*Status: Pre-wake maintenance.*

* **Fast Weight Decay:** Once the information has been consolidated into the Slow Weights, the Fast Weights are decayed (multiplied by ![][image29]). This "clears the whiteboard" for the next day, preventing saturation.32
* **Manifold sharpening:** The model performs a brief optimization to maximize the "distinctness" of the holographic vectors, effectively performing a "garbage collection" on the synaptic weights to remove noise accumulated during superposition.26

## ---

**6\. Feasibility on the Sovereign Node**

How does this run on a single RTX 4090 (24GB)?

### **6.1 Quantization Strategy**

We utilize **4-bit NormalFloat (NF4)** quantization (QLoRA).41

* **Slow Weights (7B params):** Compressed to \~4.5 GB VRAM.
* **Fast Weights (LoRA adapters):** \~200 MB VRAM.
* **Optimizer State (GaLore):** \~4 GB VRAM (instead of the usual 40GB+ for Adam).
* **Activations (Mamba):** Linear scaling ![][image4]. For context length 100k, activations are manageable.
* **Total VRAM:** \~10-14 GB. This leaves ample room for the OS and background tasks.

### **6.2 The Daemon System**

The "Mind" is a set of asynchronous daemons 42:

* **Cortex Daemon:** Handles inference and Hebbian updates (High Priority).
* **Hippocampus Daemon:** Manages the STEB and RAM compression (Low Priority).
* **Dreamer Daemon:** Monitors nvidia-smi. When GPU utilization drops \< 10% for \> 5 minutes, it triggers the Sleep Phase (Background Priority).
* **Opportunistic Compute:** If the user starts a game, the Dreamer Daemon instantly checkpoints and pauses (saving state to NVMe), yielding the GPU.

### **6.3 Data Pipeline: The Infinite Stream**

The system does not use a "dataset." It uses a **Stream**.

* **Compression:** Incoming text is compressed via gzip or zstd before storage in the STEB to maximize buffer capacity.44
* **Retrieval-Free:** Note that we do not use RAG. The "retrieval" happens via the Holographic weights. However, the raw text *can* be archived on disk as a "cold backup" if the holographic memory degrades.

## ---

**7\. Failure Modes and Falsifiability**

### **7.1 The Threat of Model Collapse**

If the "Dreams" (Generative Replay) become too decoupled from reality, the model enters a feedback loop of reinforcing its own hallucinations. This is **Model Collapse**.46

* **Mitigation:** **Surprise-Guided Dreaming**. The system monitors the Free Energy of its dreams. If dreams become too "predictable" (low entropy), it injects high-entropy noise or retrieves random "cold" samples from the disk archive to "shock" the distribution back to reality.47

### **7.2 The Stability-Plasticity Limit**

Holographic memory has a "soft" capacity limit. As ![][image30], the orthogonality of the vector space is exhausted, and the "noise floor" rises.

* **Symptom:** The model begins to confuse similar concepts (e.g., conflating the French Revolution with the Russian Revolution).
* **Solution:** **Sleep-Dependent SVD Pruning**. During Deep Sleep, the system performs Singular Value Decomposition on the weight matrices to identify and amplify the "Principal Components" (core concepts) while zeroing out the "minor components" (noise). This is effectively "forgetting the details to remember the lesson".26

### **7.3 Experimental Falsification**

To falsify this paradigm, one would run the **"Sovereign Turing Test"**:

1. **Feed:** Stream the entirety of Wikipedia sequentially (one pass).
2. **Wait:** Allow the model 24 hours of "Sleep/Dreaming."
3. **Probe:** Ask detailed questions about the first article seen.
   * *Failure:* The model hallucinates or requires the source text (RAG).
   * *Success:* The model answers accurately from its weights, showing that the Fast-to-Slow consolidation successfully transferred the entropy of the stream into the holographic structure of the Mamba backbone.

## ---

**8\. Conclusion: The Emergence of the Sovereign**

The **Chrono-Compressive Field** is not merely a training algorithm; it is a shift in the ontology of AI. It moves us from the "Factory Model" (build, ship, deploy) to the "Gardening Model" (seed, grow, prune). By respecting the physics of limited resources and the biology of learning, we can instantiate a mind that is small, sovereign, and continuous.

This mind will not know everything in the cloud. It will know what *you* show it. It will share your context, your biases, and your history. It will sleep when you sleep, and in its dreams, it will weave your daily inputs into the fabric of its own intelligence. It is the origin of a true Personal AI.

### **Comparison: The Monolith vs. The Sovereign**

| Feature | The Industrial Monolith (Transformer) | The Sovereign Mind (CCF/Mamba) |
| :---- | :---- | :---- |
| **Compute** | Cluster (H100s) | Desktop (RTX 4090\) |
| **Memory** | **![][image1]** (Quadratic) | ![][image4] / ![][image2] (Linear/Constant) |
| **Update** | Global Backpropagation | Local Hebbian \+ GaLore Sleep |
| **Storage** | Weights \+ RAG Database | Holographic Weights (Internalized) |
| **Time** | Epochs (Batch) | Stream (Circadian Rhythm) |
| **Forgetting** | Catastrophic (-89%) | Mitigated (Generative Replay) |
| **Philosophy** | Statistical Approximation | Lossless Compression (MDL) |

The technology for this paradigm exists today. The components—Mamba, RWKV, GaLore, Hebbian rules, Holographic representations—are proven in isolation. The **Chrono-Compressive Field** is the unification of these islands into a continent of sovereign intelligence.

## ---

**Detailed Technical Addendum**

### **A. Mathematical Derivation of the Hebbian Update (NoProp)**

The Fast Weight update in the Awake phase uses a localized error signal.

Let ![][image31] be the activation of layer ![][image32], and ![][image33] be the "target" activation propagated from the layer above (Target Propagation).

The update to the local Fast Weights ![][image34] is:

![][image35]
This avoids the global chain rule. In the CCF, ![][image33] is approximated using the "Surprise" signal from the Mamba state prediction.34

### **B. The GaLore Projection for Sleep Training**

To update the 7B Slow Weights on a 24GB card, we project the gradient ![][image36] into low-rank matrices ![][image37] and ![][image38]:

![][image39]
We optimize ![][image37] and ![][image38] (which are small) instead of ![][image36] (which is huge).

![][image40]
This reduces the optimizer memory footprint by up to 65% while maintaining performance comparable to full-rank training.4

### **C. Holographic Binding Operations**

Using Circular Convolution (![][image41]) for binding in HRR:

For vectors ![][image42]:

![][image43]
This can be computed efficiently via Fast Fourier Transform (FFT):

![][image44]
Where ![][image45] is element-wise multiplication. This operation is ![][image46], making it extremely fast on GPUs.31

### **D. Data Tables**

**Table 1: Memory Consumption Analysis (7B Parameter Model)**

| Component | Standard Training (AdamW, FP16) | CCF Sovereign Training (GaLore, NF4) |
| :---- | :---- | :---- |
| Model Weights | 14 GB | 4.5 GB (NF4) |
| Gradients | 14 GB | \< 1 GB (Low Rank) |
| Optimizer States | 28 GB | 2-4 GB (8-bit Paged) |
| Activations (Ctx=4k) | \~10 GB | \~1 GB (Mamba Linear) |
| **Total VRAM** | **\~66 GB** (Requires A100) | **\~10-12 GB** (Fits RTX 3060/4090) |

Table 2: Forgetting Rates (Based on 5)

| Method | Forgetting Rate (Lower is Better) |
| :---- | :---- |
| Standard Fine-tuning | 89% |
| LoRA | 71% |
| Sparse Memory Finetuning (SMF) | 11% |
| **CCF (Holographic \+ Replay)** | **\< 5% (Theoretical Target)** |

**Table 3: Inference Complexity**

| Architecture | Time Complexity | Memory Complexity | Infinite Stream Feasibility |
| :---- | :---- | :---- | :---- |
| Transformer | ![][image1] | ![][image4] (KV Cache) | **Impossible** (OOM) |
| RNN (LSTM) | ![][image4] | ![][image2] | Feasible (Poor Performance) |
| **Mamba / RWKV** | **![][image4]** | **![][image2]** | **Optimal** |

This addendum provides the necessary mathematical and empirical grounding for the implementation of the CCF. The combination of these techniques creates a system that is theoretically sound and practically viable on consumer hardware.

#### **Works cited**

1. Mamba: Linear-Time Sequence Modeling with Selective State Spaces \- arXiv, accessed February 4, 2026, [https://arxiv.org/pdf/2312.00752](https://arxiv.org/pdf/2312.00752)
2. \[2312.00752\] Mamba: Linear-Time Sequence Modeling with Selective State Spaces \- arXiv, accessed February 4, 2026, [https://arxiv.org/abs/2312.00752](https://arxiv.org/abs/2312.00752)
3. Local Learning Rules for Deep Neural Networks with Two-State Neurons \- research.chalmers.se, accessed February 4, 2026, [https://research.chalmers.se/publication/545003/file/545003\_Fulltext.pdf](https://research.chalmers.se/publication/545003/file/545003_Fulltext.pdf)
4. GaLore: Memory-Efficient LLM Training by Gradient Low-Rank Projection \- arXiv, accessed February 4, 2026, [https://arxiv.org/html/2403.03507v1](https://arxiv.org/html/2403.03507v1)
5. Breakthrough for continual learning (lifelong learning) from Meta? : r/newAIParadigms, accessed February 4, 2026, [https://www.reddit.com/r/newAIParadigms/comments/1og97zw/breakthrough\_for\_continual\_learning\_lifelong/](https://www.reddit.com/r/newAIParadigms/comments/1og97zw/breakthrough_for_continual_learning_lifelong/)
6. What Is A Mamba Model? | IBM, accessed February 4, 2026, [https://www.ibm.com/think/topics/mamba-model](https://www.ibm.com/think/topics/mamba-model)
7. Mamba (deep learning architecture) \- Wikipedia, accessed February 4, 2026, [https://en.wikipedia.org/wiki/Mamba\_(deep\_learning\_architecture)](https://en.wikipedia.org/wiki/Mamba_\(deep_learning_architecture\))
8. RWKV Language Model, accessed February 4, 2026, [https://wiki.rwkv.com/](https://wiki.rwkv.com/)
9. \[Paper\] RWKV: Reinventing RNNs for the Transformer Era \- OpenAI Developer Community, accessed February 4, 2026, [https://community.openai.com/t/paper-rwkv-reinventing-rnns-for-the-transformer-era/567110](https://community.openai.com/t/paper-rwkv-reinventing-rnns-for-the-transformer-era/567110)
10. Introducing RWKV-7 “Goose”: A Breakthrough in Sequence Modeling | by Aditya Inamdar, accessed February 4, 2026, [https://medium.com/@inamdaraditya98/introducing-rwkv-7-goose-a-breakthrough-in-sequence-modeling-1446820f2aab](https://medium.com/@inamdaraditya98/introducing-rwkv-7-goose-a-breakthrough-in-sequence-modeling-1446820f2aab)
11. Short-term Hebbian learning can implement transformer-like attention \- PMC \- NIH, accessed February 4, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10849393/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10849393/)
12. Short-term Hebbian learning can implement transformer-like attention | PLOS Computational Biology \- Research journals, accessed February 4, 2026, [https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011843](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011843)
13. \[2508.08435\] Fast weight programming and linear transformers: from machine learning to neurobiology \- arXiv, accessed February 4, 2026, [https://arxiv.org/abs/2508.08435](https://arxiv.org/abs/2508.08435)
14. \[D\] Jürgen Schmidhuber's work on fast weights from 1991 is similar to linearized variants of Transformers : r/MachineLearning \- Reddit, accessed February 4, 2026, [https://www.reddit.com/r/MachineLearning/comments/megi8a/d\_j%C3%BCrgen\_schmidhubers\_work\_on\_fast\_weights\_from/](https://www.reddit.com/r/MachineLearning/comments/megi8a/d_j%C3%BCrgen_schmidhubers_work_on_fast_weights_from/)
15. The Forward-Forward Algorithm with a Spiking Neural Network \- snnTorch \- Read the Docs, accessed February 4, 2026, [https://snntorch.readthedocs.io/en/latest/tutorials/tutorial\_forward\_forward.html](https://snntorch.readthedocs.io/en/latest/tutorials/tutorial_forward_forward.html)
16. \[2212.13345\] The Forward-Forward Algorithm: Some Preliminary Investigations \- arXiv, accessed February 4, 2026, [https://arxiv.org/abs/2212.13345](https://arxiv.org/abs/2212.13345)
17. Backpropagation Free Transformers \- Dinko Franceschi, accessed February 4, 2026, [https://dinkofranceschi.com/docs/bft.pdf](https://dinkofranceschi.com/docs/bft.pdf)
18. Overcoming catastrophic forgetting in neural networks \- arXiv, accessed February 4, 2026, [https://arxiv.org/pdf/1612.00796](https://arxiv.org/pdf/1612.00796)
19. Continual Learning with Deep Generative Replay \- NIPS, accessed February 4, 2026, [https://papers.nips.cc/paper/6892-continual-learning-with-deep-generative-replay](https://papers.nips.cc/paper/6892-continual-learning-with-deep-generative-replay)
20. \[1809.10635\] Generative replay with feedback connections as a general strategy for continual learning \- arXiv, accessed February 4, 2026, [https://arxiv.org/abs/1809.10635](https://arxiv.org/abs/1809.10635)
21. Pseudo-rehearsal: A simple solution to catastrophic forgetting for NLP \- Explosion AI, accessed February 4, 2026, [https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting](https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting)
22. A Tutorial Introduction to the Minimum Description Length Principle \- CWI, accessed February 4, 2026, [https://homepages.cwi.nl/\~paulv/course-kc/mdlintro.pdf](https://homepages.cwi.nl/~paulv/course-kc/mdlintro.pdf)
23. A Minimum Description Length Approach to Regularization in Neural Networks \- arXiv, accessed February 4, 2026, [https://arxiv.org/html/2505.13398v1](https://arxiv.org/html/2505.13398v1)
24. Arithmetic coding \- Wikipedia, accessed February 4, 2026, [https://en.wikipedia.org/wiki/Arithmetic\_coding](https://en.wikipedia.org/wiki/Arithmetic_coding)
25. \[2308.01154\] Arithmetic with Language Models: from Memorization to Computation \- arXiv, accessed February 4, 2026, [https://arxiv.org/abs/2308.01154](https://arxiv.org/abs/2308.01154)
26. Compressibility Measures Complexity: Minimum Description Length Meets Singular Learning Theory \- Timaeus, accessed February 4, 2026, [https://timaeus.co/research/2025-10-13-smdl](https://timaeus.co/research/2025-10-13-smdl)
27. Minimum Description Length Recurrent Neural Networks | Transactions of the Association for Computational Linguistics \- MIT Press Direct, accessed February 4, 2026, [https://direct.mit.edu/tacl/article/doi/10.1162/tacl\_a\_00489/112499/Minimum-Description-Length-Recurrent-Neural](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00489/112499/Minimum-Description-Length-Recurrent-Neural)
28. State Tuning: State-based Test-Time Scaling on RWKV-7 \- arXiv, accessed February 4, 2026, [https://arxiv.org/html/2504.05097v1](https://arxiv.org/html/2504.05097v1)
29. Hypertokens: Holographic Associative Memory in Tokenized LLMs \- arXiv, accessed February 4, 2026, [https://arxiv.org/html/2507.00002v1](https://arxiv.org/html/2507.00002v1)
30. Learning with Holographic Reduced Representations \- NIPS, accessed February 4, 2026, [https://proceedings.neurips.cc/paper/2021/file/d71dd235287466052f1630f31bde7932-Paper.pdf](https://proceedings.neurips.cc/paper/2021/file/d71dd235287466052f1630f31bde7932-Paper.pdf)
31. Holographic reduced representations \- Neural Networks, IEEE Transactions on, accessed February 4, 2026, [https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf](https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf)
32. Fast and slow synaptic plasticity enables concurrent control and learning \- eLife, accessed February 4, 2026, [https://elifesciences.org/reviewed-preprints/105043](https://elifesciences.org/reviewed-preprints/105043)
33. Fast Weights in Artificial Intelligence | by Freedom Preetham | Autonomous Agents \- Medium, accessed February 4, 2026, [https://medium.com/autonomous-agents/fast-weights-in-artificial-intelligence-4728cd6b6b09](https://medium.com/autonomous-agents/fast-weights-in-artificial-intelligence-4728cd6b6b09)
34. NoProp: Training Neural Networks Without Back-Propagation or Forward-Propagation | by Pietro Bolcato | Medium, accessed February 4, 2026, [https://medium.com/@pietrobolcato/noprop-training-neural-networks-without-back-propagation-or-forward-propagation-920ebe8cb1af](https://medium.com/@pietrobolcato/noprop-training-neural-networks-without-back-propagation-or-forward-propagation-920ebe8cb1af)
35. Enabling Robust In-Context Memory and Rapid Task Adaptation in Transformers with Hebbian and Gradient-Based Plasticity \- arXiv, accessed February 4, 2026, [https://arxiv.org/html/2510.21908](https://arxiv.org/html/2510.21908)
36. Hebbian Learning: Biologically Plausible Alternative to Backpropagation | by Reut Dayan, accessed February 4, 2026, [https://medium.com/@reutdayan1/hebbian-learning-biologically-plausible-alternative-to-backpropagation-6ee0a24deb00](https://medium.com/@reutdayan1/hebbian-learning-biologically-plausible-alternative-to-backpropagation-6ee0a24deb00)
37. Memory consolidation from a reinforcement learning perspective \- PMC \- PubMed Central, accessed February 4, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11751224/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11751224/)
38. Continual Learning with Deep Generative Replay \- NIPS, accessed February 4, 2026, [http://papers.neurips.cc/paper/6892-continual-learning-with-deep-generative-replay.pdf](http://papers.neurips.cc/paper/6892-continual-learning-with-deep-generative-replay.pdf)
39. \[1812.02464\] Pseudo-Rehearsal: Achieving Deep Reinforcement Learning without Catastrophic Forgetting \- arXiv, accessed February 4, 2026, [https://arxiv.org/abs/1812.02464](https://arxiv.org/abs/1812.02464)
40. Memory-efficient LLM Training with GaLore | by Geronimo | Medium, accessed February 4, 2026, [https://medium.com/@geronimo7/llm-training-on-consumer-gpus-with-galore-d25075143cfb](https://medium.com/@geronimo7/llm-training-on-consumer-gpus-with-galore-d25075143cfb)
41. The Complete Guide to GPU Requirements for LLM Fine-Tuning | Runpod Blog, accessed February 4, 2026, [https://www.runpod.io/blog/llm-fine-tuning-gpu-guide](https://www.runpod.io/blog/llm-fine-tuning-gpu-guide)
42. Efficient LLM Scheduling by Learning to Rank | Hao AI Lab @ UCSD, accessed February 4, 2026, [https://hao-ai-lab.github.io/blogs/vllm-ltr/](https://hao-ai-lab.github.io/blogs/vllm-ltr/)
43. Topology-aware Preemptive Scheduling for Co-located LLM Workloads \- arXiv, accessed February 4, 2026, [https://arxiv.org/html/2411.11560v1](https://arxiv.org/html/2411.11560v1)
44. GZIP \- The Library of Congress, accessed February 4, 2026, [https://www.loc.gov/preservation/digital/formats/fdd/fdd000599.shtml?loclr=blogsig](https://www.loc.gov/preservation/digital/formats/fdd/fdd000599.shtml?loclr=blogsig)
45. The gzip home page, accessed February 4, 2026, [https://www.gzip.org/](https://www.gzip.org/)
46. \[1911.11988\] GRIm-RePR: Prioritising Generating Important Features for Pseudo-Rehearsal, accessed February 4, 2026, [https://arxiv.org/abs/1911.11988](https://arxiv.org/abs/1911.11988)
47. Any successful story of active inference (free energy principle)? \- Reddit, accessed February 4, 2026, [https://www.reddit.com/r/reinforcementlearning/comments/1fbu536/any\_successful\_story\_of\_active\_inference\_free/](https://www.reddit.com/r/reinforcementlearning/comments/1fbu536/any_successful_story_of_active_inference_free/)
48. \[2503.24322\] NoProp: Training Neural Networks without Full Back-propagation or Full Forward-propagation \- arXiv, accessed February 4, 2026, [https://arxiv.org/abs/2503.24322](https://arxiv.org/abs/2503.24322)
49. FutureComputing4AI/Learning-with-Holographic-Reduced-Representations \- GitHub, accessed February 4, 2026, [https://github.com/FutureComputing4AI/Learning-with-Holographic-Reduced-Representations](https://github.com/FutureComputing4AI/Learning-with-Holographic-Reduced-Representations)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAVCAYAAADvoQY8AAAC5ElEQVR4Xu2WTahOURSGX3GL/IXryn9kQC6uRCkZSGLAhIGSMQMj4uZ2B2ciMZBQCnVnJGIkPxPKzYCZEkWJRAgZSuF979qbvffZ5zifv/rKU2/nfHvt75y91llr7Q38558wnNpMnaL6qHGx+e8whhqZDv4GO6hVMGf6qUFqUmAfH9xn0eR11BZqAexBdfRQA2jw4IYoILeoM+73XOoltcFPICuC++8Mo1ZTd6mr1DanG9RjavmPqREzqJvUwtRAOqnb1FenD1R3NAPY52xeL6hFTrPdHAVSTqx1v7N0UIeopygvVjblpRawNLHJ8aNUkYynbKI+whZZxKYhFIg71PzU4OiFBVNfKIsWeZJ6j4pPBIvEO+oEbOEeRfWRu9ZRwHJcUX5ITYmswBLqNDUiGRda01lqYmoI2Ul9cdcqJlD3qAewFPEoQldQX9CjYbmtaCsI+hpboxmWtruTMaFaOwh7hpzois3GPFiu5aIT4p14Rk11Y1q4HFD7q0NFqShr/krqE3WNGhXMUSqrE4WoHg5Ts2Dv3I5yqg9RwCJzIBlP0UJeIXZCV/3e6CdVoI6y191r4XJAjsghoQCdRxxEOXwZ5YLX14zwbUypVFv1MLvmqdOMdWPLqNcoRzClQPx8pZIW5etL9aaazNXDT/GRVMHqQXUcQ7mzyInn7lqFr4fpwZgirvRVZOeguh4a4Z0IUyTHTNg+8RbxXtDEibAeQgpYUHYhXw+NUZdRt6lzQp97P+yFexJbEye0P+j/Kb6hKB2vI+54LaEcPEd9RnUk1KO1yWmz034SkjsKpBTI15uC49vtRfxiPXi0A2uRAygvcg31hjqCuB16/JfUJpZjMizKi1ODw7fbqv+3hHrvE9iZyZ+XdHa6D3Mk3KFDNC7nVfQh2pD0rLA9Hkf5EKnAXEJ1FrSMXqAOpVOr+v40VC8+RO1SC1avb1t0ZB+k1qeGdkMd6ALyddM2KO10rJCapOCfouMbMFmNgGvNmpcAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAAVCAYAAADM+lfpAAACF0lEQVR4Xu2VMUgcQRSG35EEDBiMGpSIaUIa0ULRWKlFENFCAyEQwcZO+yCi1VlY2IgEQUgTrRS0jQEbBa20EyQBA6JIJIra2InG/3dmdPbd7dxqjlT54GO59+Z23+zMvhH5z7+jEBboYIBHsEgHs1EK2+B7WAUfRNMZ1MIvkvDmFhYzAd/pBEnBFrgOv8Ee6xLchq9vh0aohMuwWicsj2EvfKrihJNe1EFWOQZ3JPOhzH2Gp7BO5TgBzi6t4iXwA5wW879d+Nwf4NHu/+DDpuAJbPQTHlyqYzgppgBHDfxhrz4s5i1sgHMSLiaytP3w0l7jKIYbcAs+8+KD8KuEN+6MhIu54RX8Bb/DcpXzccX4N2UBLGTYDYohcTFp+AeOqrjmJTyQ6E155e9ONyiGRMWwL6yIWaLWaCoD5jluFT6xsXr4Gza5QTEkKsbNjBuTGzTEJzFvMO3FWMyevYa4UzG5Br4Q02eOJNpL8loMvwp+HaGBKTgk5q18VLm8FvMQzsJziV939h02LTY99iMfbmp+iR0qrklUDGFH5cN4ruiHvYGHcFxMS9e4N9unEwoWsy/m2MgJ2/9PMWeSO494Nm2KKYhLlQ3GOQlubk2ZmC/vTMwS0wsxRYWa6zU8lflF8ZRm36iQ+CJ8usVMgk3xvnC75AWeumuiDrs7wlMgb3TBecm+r3LBtz+ig38DbzhgTbK0Ps1w4Qoblmbd6huK3gAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAYCAYAAACBbx+6AAACk0lEQVR4Xu2WS8hNURTHl1CEPPOIAUJ5TOQxkiJEMaMIEwORMjHQl4GvJBlQREqmMmGgyExfGXgNTDzKI5+SAWFkIHn8f629nX33vft+dTuDM7j/+nXPPmvfzjprrbPWNuurJ20V78QD8TBc8zskXoqz/3c2QGPEabE4rNeJt2Jhsj4crkfUdLFF7BRLxehWcy1aIA4m6+PirhgX1ji8uTK3a5RYL56Ie2Jv4L75m6+ptrZog/gi/iZ8E/uTPacy+20xW0wJdqJ90zziUTPFtGTdorHm9fLe2h3DdlV8FyszW6pr4o/YlBvM0/5Y7LMqgqnmitfW+b9twqEr5lFZm9miVpg7fMk8E7mmiqdi2PzhqTaKO2J+dj9VXr9ddcg8MvyWNEd8EC/EjMyGqPOv1lqD1P1RcUaMD/dKyuu3qEXik3huXjMlRYeB61zUOrXJg9EEcdm8jjtlJBVO4mxav0UNmj+I326aJz5a2eGL4pd5apeIZ+KRmJxuyjRRnBTXxU/z/nvBupQOfxiy6kHdhJ19NPhJmS3WLy9zRNwwd5YyYzDUppHSnIpUlzIR6/e3OGH+Ee8234/ztKxaFB3uFLVUpJWI0WuXZzYU63fAqnqdJV6ZdxY6TC3ia+erZ37zgJLonaT3WG4Iov92KqtBK2elJ5EqUhajQCqZSPTDc2FNX8bO4GCdK9Zvp5eOvZtI57aexeSKDu0Ru8J92hEf0LA4b+U+ukr8MB+rea3GcUuUyVJtYhS/MU8rvZCaZNYTaaYUdckQSCPMCKV/p+eDz+YvjejpnElSO72evl+LcGa1+elsh/kpKm3k24O9sTpgnmo+NIbCLSuXRSO0zapUUuOlQ1FjxFmAvkp0l2W2vvpqgv4BC9CRJDRmJwIAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAVCAYAAAAw73wjAAACkklEQVR4Xu2Wz4uOURTHvzKKkIQRYxJZEGZIlDIWkliwslD+ABZWhFg9m1nMZppQCjVLiWYnPzYUWZidmkZRIhFCllL4ft17uD+e+3jqtXgXvvXped977nPfc88959wX+K/u1zwyOx3sQK3WW0T2kINkHZkZmzNtIuNkQWroQCvJjXRQmkF2ksfkFjnsuUueka1/pkZaQe6R9amBWkwekB+ez2RDNAM45W3Ga7LR24ZskmkWGSEvkDsk2yW4H9mc2LS5MVIl46kOkC9wjlSx6Ze02UdkbTKu9X9Ljlwkn8i20BBIx/+RXED8sqLz1D+bVJEjcNGaJksjKzBILpOeZDzSUfLdP0taSCbJFNxxmk6Tm2hO+rnkClzUtFFF9VA0w6XY8WQs0hryBvW7DGWOviTL/Jick5NnbVJBq+GipfnbyVdym8wJ5ijtdgTfM1VwOxxOxlPpx94idlRPfd9vkwraR076z3JOTspZOS0pCNfQECj1qftwx747NmWSXfNUwfP92BbyDn+JBFwwwvV17AqO5bvyXzVSzE+LiIpEk5t0DnnFytFX/lmS5WdfMKbIKdVUWKvQIj/N0fA469QP10c/IO6VbRwN8zNUBbfxY2iRn6peVXGTozqaM3CLnkhsbRxV/9T7qayIlTp3EHeSTMqJq+QbyjtSX1WjV8NXvw2laOnHVCwlVajPfwXAWpWuyWJ+mnTTyJFx5I7sIu/JKOJWYrITUSOv0xK4aA2kBi9rVaX3M+nKfA53x9v9rrv+CZyz0TUWSOPaoAotVC/cWuH9fR75HxttfgLl06yVFlHl69+S+uJylB0MpVYjp9QLu1r6O/iQ7E0N3ShV9nXU53GnUiD+mZQiuiJFm3RpK61V/QQeAX3joIQK1gAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAYCAYAAAAcYhYyAAABM0lEQVR4Xt3TvytGURzH8a/8yCOKKMkgZZGyWGVTFpKFemyKxWQgm8VmYTEaLcpgUoqJf4J6lJTBaJDE+9v3njrf0/W4Z30+9arnOd9z7z3ne+4Vaem0YRD9aaFqjvBT2ElqWVnBF2bTQk5O0MBoMl45vbjDBTp8qXom8Y49DGMRc+iMJ/2XJXzjBqdYwz2uUIvmNY32Q2+yKnbUGl3VM0bCpGYJ/bgUv/xDPIltL06XlGwz7kfIX43W3+diPXPRfnyKfz9m8IF6NKbRVT2IPdhFl90Q/34c4AXjmMcmNsS2/IYzTIfJZcuOx3pwjImitiV2CC5jeMV2NKans4tHsRstF+P6EP2vn4eLXjCA9rQg9jXrqkKGcCsl/ciJNv4afVgX61d2psR6tY8FX8pLd6FV8wsdvjEXCyacWQAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAYCAYAAACx4w6bAAAB20lEQVR4Xu2WTShEURiGP6GIooiIiGTJVkqSLQtSsqBYsrCh2GChpJQsLGSlJGs/GxZ21oqNlI2yV8pPft63e87Mucfce8fMPbK4Tz3N3O+c3plz7nznjkhCQkJCDEzCM1hlD8SAy+xQSuCJku/jxGV2JA3wAa7aAzHgMjuQclgHR+A7HIW1sNiclCMusyOZgDvwHr7CfbgFW81JOeIyOytc9oDL7EiieqAGjktuXywsm2Osb8MeWOAfzp9++KZeTdrhETyGF+L1zG8JyuailmApbIO3cMw3IwYW4SNssQcUA5L7woKymfkEO9Q179w5LEvNyBPdAzqUJ9a6eDuqCVsYa3zoZvoZhWXzulvVCA8Vuw8rYL34szm/Sb1qCmGzWK1SDW8k3QNDcFb8YUEL44KuxDvxuqwxkk02aYTXcNCoBWVvwC+4bNSmVO0AFukiP2QF3sFD9d5+zgQtjNen8BPOWWMkm2xeb4r3rDMXrLPZe7xDGm4Me3bYqPH7vcB5+blpUqnMRNDCNDwYZuyiQVA2F8Ue7FPXPERSO/4XRC2MO5XppxgGd3ZavGz+O+EJvKDqzuEur8FL+Az3YKdvhneq7Yp3bP+GXvghXm9oeff+Ddxx8wRNSEhI8w1P7l8lVivbGwAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAYCAYAAABA6FUWAAADSUlEQVR4Xu2XS6iNURTH/0IR8kikSCTlkUdCioFnJI8wIIyEAUqEwkBh5iIGJJKBx4AkjxRxSxkgMRCFQqKIgZDI4/+/a+97tnXO991zT+dcpfuvX6e913e/vdf61lp7X6BVrcpSV9LeT9ZYLbrmbFKHFlwwaBw5CXO2SfUit8h38jvhMzlDOhUeLdJochP2jn+hZeQwmhngrTAHF3hDCXUkF8hib6iBFMQbZLmb1x4uImO/8nwqmU/6JPNbYE7OSeYGkUVkfDInzSQPSW83XwtNg2Wafr0U5NsokbZycg35Sa7CIiJ5JweQ1+QlmRDmpDbkODmQzNVSyrC3ZKA3wOaekYneIHWB1aIciF/TOzkrjL0zPckjZKQJ1ZaMITNgNa2gDCbTUQhoU9I7lKb9yTVY7Svo3dKHYO+/DgtEkaLxAxkS5ryT+tVY86nkwKvw66W0OUU2kG2wlN5PdpNj5Dzp0Ph0tvqRfbDnf5F75AhZBQtaqhOwTuvnG3SUfCVjw9g7qY1qvDSMo2QvlT5aZBeZFMbKEGXKaTICFtB60jnYy1FePUZp3/XIeK+KVk6sDePUyXbkLHlPhgV7lOxpmkf1INtR+FIjySdYkNQH1B2HBlu5yqvHKO37LunuDZLq4xxsw3IkdXIh+UE2ozgNspz0knNfUDqty5GCdTmQl+La93PkdHo5ugmWSoqYnFRHfUGWwBqAVzlOxg6cGeEy1Be2F9VznnLT1avcy4Da9RtYOqZS0zkIaw6xA8vRmAnqrrJFxQ6a9ZVUhzrm1OUl1fq6grlRCoKaaN7trFHRydh4sqRuLCd9M4hHTh2ZDEv32JkVAHVBXS6iVsCeV2NSD/BajUI96u8PwY6UVAqgOqs/5v5SvLt+hC0YeYfsu6vSoh62iVTazH3YorryrSdPYUfHFTKl8GiDFMxvsHoqlfo6W5/AjpFLZNTf5gapFO6Qud5QDe2AdV//BZR6ClysZT/2kl0pntU01JX191mXcN3EHsMuClWX0u4BGe4NzZQ2twfFwSpHStWdAX8CVE0byV5UvoC+rhxUQ6pECrQajq/TqkoppFTTmVqJVIfzUFmQtLY6d1MnQVWkxqR0ybuR1EIrYf/uteq/1h/+O6JR25Y+/wAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAXCAYAAAAC9s/ZAAAA0ElEQVR4Xu3TMQsBYRjA8UcYTEo2SnYfwaQUi8mATGYTg89gVCwWNovN6AuYlMHMYGZVCv/Xezr3cnmvjP71y+l5r8tzEflnFkYde9wsDB53vdTCEjVU0Rd9cOR8f+phh7K+zb8OLsibA5simGOLpDGzKiV6F0OEvCO7Krg6n4FTT5zI+9aVNRLu0c9lccBU3M2rN6O2n3aP+dfGCTlzYFMcK8xEv4nAlXBG0Rz4VRD9e5uIYeFQ11Z1xd3wERtkPCe+FBX9BxqjIQGe/O9H3QGDCy6X25LkowAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAiCAYAAADiWIUQAAAFbUlEQVR4Xu3caaitUxjA8UeGzHOGEBkSypgxPhij8EG6EfkifCOuIfLhCuUqZSjJGBKikHmI/e0KJUpJqUMiyhehyLT+rbXuXmfZ5zjd8+7dUf9fPd13rf2e877vPrf20/OstSMkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSZIkSVpv6xSb95NaETZOsVE/KUmSZuO5FH+nOKt/YYpWp3ghxcvN3J4pDmnGv0W+r62auZVkXeT7I45K8XEz/qKcU8cvlfHQfo/xNR6I/L7W8W0pdkzxfhmfUX5mOZ7oJyRJ0mxQ0Xo1cnVrVn5KcUSKnZq5z5tjnJbiz25upSERuqEZ35TiomZ8c4rTm/HQdkjxYYrdm7lvyly1f4otmvFybJJiTT8pSZKmb48Uc/3klH2ZYtdujqSxRSL0XTe30pCwkaRhn8jP1SZwd6bYtBkPjSR7FLk6CVqW3NNXzfiWcjwUkkESRUmSNEMkGL+muDVywnH3/JcHRcXpqRQfpXgwxpUfKkTn1JOKuchtRipW38f8dulQ9k5xeYp7UzyU4s0Ud807Y3G/pHi8HN+R4rxmfFLMZs0X16MlCxLEUeT7wj2RK2xDIhnkOSVJ0gzNpVhbjp9P8c74pdiyOR4KH/YndnMkHDXpqH5IcUA5Zj1bXWPH4vf/uq9dUlzST05wdfmX3809kbzVahXX4FqLIXkZxbjtyTPw/rHu7ooy16Ot+EcMl/SQcJPskvzuFTmBo8pGu5n3oUeivNSkdLN+IvLz3t5PSpKk6WKd2LnleC7GH8bbpXijHA+JFmJNiqo+YWNd3SjG6+poje5bji9I8Vg5nuTAFK9E/vml4plpDbd49j6J7JGw0SJ8tIwPinzd/WLxNYHvRT53CCRsVCHr2jmqhSRsl64/Yz42eixlAwKJ5dP9ZOTne7iflCRJ08OH8ihycsExOwpJ1M5O8VaKryNXbVqsyTo1xfkLxLHjU/9l5xSf9ZORk7F2lyrVrppEHh85SaNadFzk5K3dXToJFadRN7d9idYzkROnH8v4ssjJzHWRn52WInh/2g0S1SjFXzG/tUuy1Cc6tEZJImmbgqSqzj9ZguPXUhye4tDIf4f7y3mg2jfpK094VqqRtcpHAsc90JJt8excn3b0tmXu4Mhr3E4p4xMi7xomoWYXL61o7qVFgnpNNydJkqaIZOjMckwixof5i2X8boqjy/FQSMpob/ZIVmoSg2djnAQdE7lVy/ossAaO80miaO+1cWU5Z1LC9knk5Kqfo1rH+r1HYlz1YlF9++wkUv3PgvZjW23invhd/do12qMkf+yMJWmt1/m0/EuiR8LFdUhWWUuHtkrGM7HGsNdXJznv22bcIhGrlUoSQv727MZ9vcz9HPmrO/i/wHs+qW1Lwt1XIyVJ0hT1X4ZKFalWcWjbkVwMiXbopAobPmiO+3Yi91Xvc6G1Ya1JCRuooLW4Tv29bQWNhKp/dhKbHolSfx7ffdZjTRsbKAgSsrrLkqQIzJEEvV1e473nvvpnva8bg+u1f0PGRzbjFtfZphxz7yRwVORqG/zCyO8bbeWF2rZUD6nGSpKkFYDkoX5lxRBo05GwUGWahBZoraothNfXxOItOVp/6yLvlKS9WFFNWtuMF0O1i2ev93pYLG/dFtdlF+rJKValuD5yFYs2KZW3+jxUNa+K3JpeHbkKVpFc17bnhmqrmCSrbLrgHmi9kpzR0uZ+SABHKW6sJxcXx3S/pkSSJP0PXBt5nZqGRdWUVjdt4w1FZa7fLCJJkqQBUdXbrZ+UJEmSJEmSJEmSJEmSJEmSJEmSJEmSJEmSJEmSJEmSJEmSJEmSpMn+AZlT1FL2C2QGAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAYCAYAAABqWKS5AAACkklEQVR4Xu2WTaiNURSGX6EIyU9K/q5IScnPSFFXEQZKQoqZYiJEuZFQlL8SCgNSUkgmSvIXVwaUASkTZWBkZGBgoIT3sfbufPY913XrnnMGzltPfWevfb691tprr/1JbbX1/2m8eWF+VvhkFprJ5nVhe29m/f6ntLmw3TEjkq2p6lI4sL00WPsVtrWlwZprnpiOYryp2qRwkCBKZeeZU9Ugc8AsL8abrtUKB3G0qg7zQfUDm2NOmqHFeNO1zPwwVytjZPaoOaOezg8xxxQBtFwc0K/603nGjitqHeertiVmnyLAlis7/1jRMSiFs2ZmxZadH2kuminpd8s10Xw03QrnOIS7kq0MjIO7Ldn6EuV1ynxX/W41IMrOv1Jk+4qZkGyzzWdFYDPMeUWA/yrukqeK9zREYxSOE8Ahs75iy4E9NwfV/9a42DxTrNEQkcluRce5aYZXbNl5Du0N9d4aObxrzF3FQR+dximxc3mSYt5Kcy0xP42tMPfMvDSPC5Ak8p4Lqt3sPUQtU9PfFJ2kqhwYdU/99yZ2hJ0ZpkhAp6Lmb6t2weHkXsV9MljxCXJfsTvr0vjhNJeACRznH5lVabyu6CaXFQtWlZ0/or+3Rhb6ouhSZBPnynpfZN6aSek3u/pGEfhUReYJZJR5kJ7RFvVxZsgqi9XTAjO2HCzE7u1QfMzBOPWsdy46diInCPs7RTCsT4aZi6MEjT8kjMT0p0n0S2SGxViAUril2O5c72w5Du1WtE6EU6cVZcQznyiUGzvGjf9Q8b7pamCbRZ3mhNloLpmlaXyDua5wkIM+TXGgtyrKi2ByAyBovlB3Kt7xMj3vUe3wN0w4QWmV54L6JZtZ2JlXr2tho2yYX31uq62B0C+853uixxSQXgAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC4AAAAYCAYAAACFms+HAAACoklEQVR4Xu2WS6iNURTH//KIkDxyPet6dCVFuRkoRt4DE6UUZSAM3IHHwCOvQqQUSkooSeSR5C1xS6EMpIyUZKSUoYEJ/v/737uzbef7Trdz77nS+ddv8K31nbPX2t9aa2+gqab+f40hr8ivhC+knUwibzPfB9LW9UtgXea7Q4YGX8O0E168I3dQe2DfqtxBzSbPSGtmb5jWwsEpgVwxcL2Tqh/ZS5Zk9oZqJRycgkzVSj6ielKzyHEyMLM3VIvJT3IpsWlHD5OT+DvwAeQoHHyfSs34HX8GLtsxuLYVeOpbSHbDyfWpYuBP4cmgz3+KTE98MfBh5CyZHJ6LpPcG58ae1njymXTCC6rhtgZfnpSadHPwFWkjuUVek9GZrzvSFy0dsTHwN/AuXyRjg28m+QYnNY2cgZMr0kjyhGwiu1Bf884n91GynhZT0Ar+AFmd+GJSL8h+1B5/c+B3dbjVq+3kdG5MpYw64clyjQxJfDFwNehVlO/gBvKQfCUX4AMqSv+pErsON7xKMErlsI88gEtxCtxjn+C4lMCg+HIq/VA1/AOeGKliUqrzdLEiaWweyWz6j3tkOVy3V1B5R88arQvIDDhx9YW+2HO4VEulqXEentGpYuCHUHv8xaDyU3YNvJvadU2au2RF8OlZdfyebCMTgl2JPCbDw3OhtJtFdTmXjMqNVaRe0d1lXmbXpsRTeSLcA1Mr7q6mV2moxE4Em8qqtL57UgrmJdwXqRS4rhWSykXlsIgsJbdROZVV+wfhr34zPOu8WB/8vSZdHRRIfvAsI5fhs+EceQTXdQt8Am+Bx6d84+CS01VDu6+L3Aj0kvrDZbID3rFq0jSKh4kmRDqd1Ef5rFbwqu9afVWXNAbfkRv4By5e3ZFqW3NYJ11TRfoNE3d8Fb17ULIAAAAASUVORK5CYII=>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAYCAYAAAAcYhYyAAABJUlEQVR4Xu3TPUsDQRSF4Ssi+AUhIoKFjQTBFIqIpYVCBH+D2CqkEkEEtdQy4EctYqGWYiMSQQXLQMDCysr0NgErC33Pzmx2WXaLbSUHnmL2TmbmzhCzbrrJl17MYwVD6MEUKhiIzctMAdfYxj7ecIwjnOMW/Z3ZKdGOh1j043F84gYz+MILhn09NSM4sGinWbSxhj6so+xrYQbNtZ8Z/fjb3P2kRa0/WHY9aO0CDRQTtTA66StG4x+18hk2fOHd3EJaUNHrqKZ2d1BHCyeY8HNsFb+oYQk/2PU1bXCJkh8rp9iMjYNMookr3GELH+ae9h7L0dSgxScsxL51oqOOWXTjyXGYaTxb4j7yRi+nE+vpq+bazR1d8iP2MJeo5Yr+VzrJf80fjFQnxuZxscoAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAjCAYAAAApBFa1AAAEtUlEQVR4Xu3cX8ikYxjH8UuWaG2baNkQKylhJUkrlEIkihMkDpTsgTMijl5JcsDBtknCLg78Sc4UJTYO/DlTpJR6SRRJCYX8uX7u+zbXXPPMPO/OPrPtO30/dTX33Pe8z8w8e7C/rvt5xgwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgP2yOU/0OKrWPA73OjZPLlD8rEd4bQxri6Tv2cx7rgAAwCHmKq/L8uRBcK3X43myx3W15nGY1z31cUgKRTEkNfGzXuC1M6xF93ptz5MHYGsYz3uuAADAIeJjr4e8HvX6J60NQR2ln7zOyQvuaK+b86R7xuvP8PxkK8dougLbWV6fej2Y5uUTr0vS3Afp+RB+9dqV5tYS2HQe/vb6Ky8ECoSveL3vtSmtvWXj50sIbAAALImrbRSYFIpOCWtDucLrkTxppcO1J09WP3q9luaetxLKpCuwrXjd4LUvzG3wut9rtY6jW21tW6P5fWa52yZDb19gU1h7yesEr8+9Lh1f/p8C52NWQqGO01xj5Tx+F+aEwAYAwJJQUNiWJwemsHZ9nnTHe32WJyuFnrvSnALbhXXcFdhetBI4vwxzCos3WeleZefZ6Hiz5PeZRYFSYTOGw77ApoD2XB0r8OnfpIuC541Wzo1CmmyxElR1Ht+ucw2BDQCAJZG7QdN8PaPeDK/ros5P14X2ChG5KyTHWAkgCnTRqtfpddwV2B6oj7/VR3XwzreylRhDXKP3UQjqk9+njzp3qqYvsCms6WaERv8muRsoL1jZCv3ZRtu+d9bHGOIaAhsAAEtAoUDdoEXr6m7p4nyFiK/ygpUulbZDc2jRcdrdjl2BTd00aSFUYU2h7SSb3F4VBbaurVptTSrstLo9jNXR6rqxoDnRSqfrjTA3K7DpO14Znss3Nr7l2Wg7VHTO1G3U59fdtfqOCr4tzDYENgAAloACzkqenCIGmFwKMdOos5a7aNoCVMiYFth00X6+QUDh6+nwPAc2hZUW5vR+d9gowKkblY8nQ3fYTvW6z8p3iyF1VmB7MowbbVHnmzQU7Nr1ewqf6kC2Lpu2dbuCJ4ENAIB17myvH6zclbjXyn/o2pZ71fb/N9Fm0bVrMUyo8/RhHSuAfBvWRCFFYaV11/SZVr1ebi+oYgjSRft7R0v/3XRwWh0ryCnA5W6d6CaLFupmWUvY+cLGryHTd95Rx9MCm4LdLza5xaxSlzDeFXuLjX6GRCGzBUJ9LwW43F0TAhsAAOvcu1aunfrISjho9Xp80QH63sox/7ASzNp7rNR1dbj21bGo89Zeo21BBZffvS6yyd9MayFIXbX2N/qZDl33tqe+5tywps+Sqeum7dI+fWHnSK/3rGyHNgpru23USewKbAqn8dx3lf7+tjrWtWuXWzmWgrW6lzq3WlPwe9bGEdgAAMAgzrDu32frE0PQvN7JE1O0rch5TQtsi0ZgAwAAg3nCJjtofYYIbE/liQUhsAEAgHVPW3sP58keF9eaxybrvkh/UeJnPdO6f5NuEY4L43nPFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADg4PkXFpjHg6drAkcAAAAASUVORK5CYII=>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEcAAAAYCAYAAACoaOA9AAADyklEQVR4Xu2YS6hNURjHP4UISVckt0RSHkWJKAO3DBgwYIA8ZmKm5JXRiSQzSZHIo+Q9kvIqRAZMiURduhFCCQPy+H7WXves/Z29197u2ecauP/6d+9d65z1rfVf/+9ba12RPvThX2OocpBtbAIDlENsY8UYLi5OSzFDeUxcsKowU7nBNlaM2cpTUnLeHcp3yl8BvymvK9uCz4VoV95UTrUdipHK28ofkh6vK2h7qFym7Jd8xyMmzkrlZ6mPeVnirmWcMP5xqX9+tfKQ/IWDjih/KhfaDgMWtE9ZM+0Wi8RNbLdpH6zcrvyu3CppgWLiABZ3Vtxm3lEOS3d3Y6LyqrgYNj5gDpeUS21HFkYoHyg7lWPTXQ2YpnyS/IxhhzixF9gOcYIcUH6U9DhF4jC3k8qLyhfKMenuP8ANxN4jbnPYpCysUN6TEuk1WfleeUHZ3/RZbJNiS9PHZ14rJ5g+j8XiJr8+aCsSZ55yr7g5fBH3eQvEwBHUw1h82p+JGzOKVeImStAY/KLZmRjY4U6Ji+jFCccqEof5sXCY5YpR4tKd+I+UNyT/9KOd/qK1yH5x+VmkIjbGziwsBlKJlMrKd49N0rghMXFw9EFxLvfjs6kepOpGcYcE4+CsWHxwQtzJZQ+Gbvh681w52vRZEPSNFIvIgvPqDWAy2B5xwgXGxPH1hiI8XflJ0rvOEb0u+Z1UzXKWBfO8Je6+lomiejNQ6kcek3+Z/MxDmXrDcY/tiUt8j5g4vt4A72B2HrC4mrji6oWPxfdAHIyBQTLh6w02tyDQTqmfKGXEKVNvuC7gLK4P4YbExPH1BuAejnJfU9ZK3c1e+Fi98WDMaMYwwbx6w33hqLh7ASgjTlG9YZevKZ8qx5m+PHHCeuP/xumIMF9cevm6MUv5VfLjh4imVex+QyodlnRNwKavJJ7LsfsNY9aUH8TVCIs8cZjbOUnbn019Ky612oP2svUGIGCuw3xVt/WGnEYYXDI+aPeWDe8mIXDYFWnMd3Z1irhU427BuywLWeLwXZ4O1JHwVPFFf3nQ5h1l42eBsTipOKlTYFdxAApD3jxdCcM30WlJi+aLnR2wTdxbjDeM/y67iriMSTvvKWqDT9EsWHHWSHpMTqiOpI/rBG7Cjez8GfNZ3mGUBA6ULODC+8oltqMZcO1m0NwK3wSsOK3EXOVjSWdG08Ald6X4gdoT9JY4ZMCuhGGqVgKseF7iKdIT9JY4nMIUYntaVgLU3pKwSuV7QxxqFHWz1L8regqCbFbOsR1NYJJUXCAzwBOjFSWhD/81fgMtaN4O7QMBBAAAAABJRU5ErkJggg==>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAYCAYAAABEHYUrAAACfElEQVR4Xu2YP2gUQRjFX0gENQZRgyJqYbQRCwvRQrQyAS0EsRIMaVJEwVIQFCSiFjZWgo0QFAQrEcQQiEXQRrTVUoJiCKQM2Cj+eS/fzN3M3OztIexyhHvw427mm9udt998M5sAPa1/DZH+pG+jo5vVB5u7PkPl/DR0h+xO+s45ynSA3CBb00AN2kLuus9QOT8N5YKdmNUTfUj+kstJrEjbyTzsN+IPGY1GxNpJPqE5fomccrFazR4my7BJaEKaWKeSwUWY2QtJzEsP8xr5ArvPSByuz6wm8oBMkTmY4fFoRHtdJ/fIqvue03Fyk3wmb8hgHK7PrLL6iuwgZ2AZ+uDaZRogj8hp8pU8icNrkoFp2JgfsAeTqhazyuptNDO5Cc3sXvSD2mgPeUr2knfIZ22CnIStHF33bBxeUy1mD5IXiLOoulN236N8Z5aJ+7Cj7TX5SLYFcV1fS7ufzCBfr1ItZm+htT51wwV0ll0Z8ZvSY/IdlmVpA+woU3sYxfUqVW52PywbuZ1XJmV2Aa0T8PL1esi1ZVw1edS1tVzPu+/qK6pXqXKzymrRmarlq2Xc7jjx9Trk2hrna1IPcBqWXaldvUqVmt1HXpJdSX8on11tWNq4Uvl6Ddu/YA9Qy1e7vKRN8BmK61Wq1KyW3NWkL5U2LR1Byq6OpFS6xqWgfQR21uqt6krQX1avUmVmlU3dfIV8K+En8tnVq+IsORb06b46a98i3sV9xovqVarMrDLq30875TcZg2VbZsLYc7IZNlFteP59dxT2QMOxi+SEi4eqzGw3qmcWeT8N5YI9s12m/zI7ida/VrQh5DaFbpLerfXikf77KOenp3Wpfz3vrlLNU8C2AAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAYCAYAAAB9ejRwAAACDElEQVR4Xu2VTSguURzG/7e4EbrdiIQF3Y3uLQuxsiAWLGxskI+dj4WyVBZiIdnY3s2VjxVCSoqyUDayJms2ioUSFhSex3/Ofc85M+/7zk5pnvrVzPmfOR/PPHNGJNEX1TcwDFr9wmfqD7gDZ6DUq6VTL3gAbwF7IM/p4WpUUn2fwbJk6E+XFsCr6AN8OK446Dq4BcegyC3/1y9wAF7ArFeL1G+wC/pEF3YKip0e6VUBVsEWuATlbvlDuWASzIluusMth2Vc6gf5YF/0Qd7HUROYBxPgEdS75Q9xEV1gCVyDGrccFm3dlpQz7aJunYAfplMGcTGckES5wHxOizp6Dg5Bgd3BF12aEdeVQnAkOkGP1R6lHPAX1II20c0wAkYcf1w0HnSQTmbNUzXYlHB+uOs4bpk8Mdx14F40O0aNYCi4HpFoJ0OakugvjQvhgrgwLjCdTJ4oBpxBXwnu6fi06Fh0LFae6BLPlXRnEl8dd3YkOkGUTJ4ousUjwWRmUHTRVInEzBMHHPMbLdluMfy+7DyZe0aBkzeLvkY6RDWAJ8mSpyqwA8r8gid+AHSLxwSPC1vM0wb4abX9Azeir7DSao+VJzrEY/4qC5yAg/lu0QH+YpgT4wZF99m322ozDmbME925kNQ/KC488enWgOiGTDu/uBZRdYq6xxOc2Vnz+vI/uQi+B/0TJUqUyNc7byWAcTlY+UEAAAAASUVORK5CYII=>

[image18]: <data:image/png;base64,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>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJQAAAAYCAYAAAAcTtR3AAAFVklEQVR4Xu2ae6htUxTGP3nkGe4VeT9CISQRhZBnHkmKcqUIpZvk5k1u4R/vVykREiKP5HqLE8UfyuMPUqhDHiGUUMhj/PbY46655l57n7XP2ae99r7rq6/WmXPtvfac8xtjfHOuI00HNjNuXcGtjOsm962paOdnSJxrvK+Cdxp3Km5bY9HOT4vpwFrGpfIUOakglV+lwWPY2Lilce28o8XocIvxvy4vyfomBQTE9cavjdtlfeAI45/yMb5u3KjcPVVYz/iA8S8V6wq/Nf7Wvf7GuFyL6KNONf5tPCTvmBDsb/y9S66rgNAQ3I15x5RiD+NPxkflARcgO18jF9aKpH2kuMs4a9w2a58EbGB8xPiVBgfFUcZ/jCfnHQ3DvvKqsVAwTkRzQd6hIgBn5DZgpOALZ4xPGdcpd00EyK43G6+QT+BJ5e7VuNz4nXGXvKNhYLHvzhvnATJxv4wdYntci7DmkRqZcM4nWJDDtIj1dYTAYD9t3F7++5mkM0t3ONY3viAPnC2Mh8vHyUakaRiFoCJJfCwfb4pNjW8Zf5RnwxSUQ55/jNxnUip3Nx4trwS1gFopBZjVe41nGN8xPq8hvmRMuNS4rHuNQBAUwspBKZ81fiAfF6KjzH9v3Ku4rREYhaDIwmTjZ4zbqDjQPNT4frc937wgtMfkG7OrjR8Z75BnOkz+s/LAnBNMLII6XYV5Y1G+lP+I+eBauaepy5eNSzqfrA+EgHcKDxCCqjLd+Kd/jferCJLwEf1K5LgwCkFFSXtV5QPNVca35RUoNepc3yAXHGDdWX9K4j7yCjajGn4rUiPqS0sci/KFvASmYEvahFLIb7hHxQQAzDim/OGkLUCA/GDcLWnjfo4Sjk/aAGl/w6ytLigT52jwWVggzv7y1yLHyjNC3g5rZQj1908880q52M5L2glmdn7x/ZTCX+WZnLk+y7hnty/AHPWc56X+KdDPpHONYpsQ0dR0smp6zhLEK6UTn/qnNML6mXRK/oNZ21xAGMwN5fQT1cvs+D82E/lrEYL704p2mIu/CoP8E4jMPOg8DiFVCTJAeaSq9PSTGonSdKsdD8zNLdnqXbkI5wKDyqNrEIc5vWYwLN6uWTvfQ5qeUVk44Z/SUtgvaABlsWqrXQfM3YeqJ6h+WGjJ63f+FDhOXv7zwAvwGQLqPePmWV+ADEbp7BEskzyr8vnTSvkB4M7yTHC+/CUjkYOJ5WHU1UHY23jaECTy6m4AMI1VCx6Cykt1lLb0/Olg4x/ybISYbzceJB8bWYtMc/bqu+ujCYIadP5E+XpSvedxBCnPZK0RCdmNuQhBhg4QIBshvBnel5fM7LA7qIrStI0ayQciE/ADMfDjAoNDHCzYDlkfYFLIoPlmoqq0pW1k4sjGRPebqoi8mmiCoFgjguWArH2pPGshthUqZy8CmvZb5a+p8KJhg5hXfGlaEXhGj2B3lL/fWZ608ZDLjJ/LRXVKtx3B8TeHiOMA5vsXFT4JMaQm8TaV311xjbEl6z0hr/dpBjxQHmGM6SYVGw2ElZYKxn2Rer1M8DqVy+u4BEXmeEjFuzr4s4pdNNfMySr1mmtAYHGcwNifM15s/Ew+hy8ajyxu7ZTBN9Qr2M6k0VnlXdilpBNFxBK5dfxT08A4qrwCbURtGqmVkTcExiWoUYD5SL1s/ndgoVm8A0rNK8ZN5AeJ+KtpQxp5+xlPKHfXwigExWdPzBsbhMjiZPUL5SVxaHCIOCM/w2CXMI2I8rhSbvyjDNZBmNWX5P6DUlpniz+JwKC/Jv/fMwJv3mDSqkrHNIH0ThZuMRicXw0TcC1atGjRosW04H/H9jCCMKUlagAAAABJRU5ErkJggg==>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAWCAYAAAAfD8YZAAAA7UlEQVR4Xu2SIQ9BURTHj41gE5iNCTZB0ZisKYIiSJpAUmmSJKmUp/MVzFSB4Av4ADRB4n927tu777rPU17z237h3f85e/ecXaJg0rBgMQ8TWp2VPlxaXMCSVxYxcTiCVTP4hQZ8wo4ZhJGCe/iCY38UzhCeSJpnRvaVItzCFnzAtT8OJgbnJHPWSZo3JMsLhRtWJA+CH8eVZHbewVeS0IE19e02H2FGnVnJwQvJgkxvsOKV+uE5J7BnBiTL4rl5HCt8TYfk2ibczH/nzX/A193BrhkopiTNbf0wCw8qcB1oeRPejfwMy1rNn8h5A9OjLzyC38jYAAAAAElFTkSuQmCC>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAYCAYAAABqWKS5AAACzElEQVR4Xu2XS6hNURjHP3nkGSJSHpEUSiRKUVKkRKKkKCMxUErpCgMlI0UJUSRJHhElMRCniGJioCgkUjIyMkDi/7trr3P2/u46z31K6f7qV/fsb+/12t/61r5m/fwfDJaj/cUS0BZtlmKS3C/H+EAOOjorF/tACWjrspVYkAHysPwsJ7tYZJA8JXf6QBfYKs9Yh29gofyeyd8pVsqKlVihBgyTd+QGH2gGD16Sn+QvubQY7oV77stdPtBFNsun1ubiMNujcp/8I9cWw73wNt7K2T7QRWbId5ZevCQT5E05RfZYGPyWwh2BHfKxHOUDGeMsTHqWhf0zQq6SM/M3NYFnHlgoGi2x18JmATpn8EzCczEzxXp5xcKkn8jT8qqFFPsgl1fvbA59UHlYgIbMtZDrI7PfcfBHqncEiFcS14E2TlqtSjDxH3KJPGGhvXVZrBV4vmK1MSWhMzpdlrtGrrFh/QrHwafeyCYrtnFOvpBjLaTQNgubPTJQDs/99tBHfL4ulL3fFlbGe1cOrd3acPB56JCOL1j9105FIV4P+ngvJ/pAhFJEjvrNxAn70fq+tlYHH8+K1IaP8GbY/PVomjZ7LN1AHLyfOSfrDQsde6go1y08S5v5Q450OW6hos23sOJfLBxGpFMK9hUVh8pTgFdJXr+UU10MeCPPLEyAweRh8/l0iqXtq5wnb1nx2Y3yoNVSiDPikRyf/fZwH5WGvgqwqb5ZLa9ZgTm5+DH5Mxfn7/NySBanYryyYsd0dkg+lLflAXkvk7RkEPkVJJ0alUH2zHNrrzq1xHT5xvqefgyEAyrmqP+dh8mk0jVCeX1toa+uwqD46qS81lu5RrCqvKFFcoFcUwxX28dO2m8Kn8rkLAdTu7B5r1lIMwqG//Sl8rF/prnrXYV/HKgubX35ZXBApb6NmAiVqO3P4U5YIXf7iyXYLlf7i/38a/4CqsWAb5JyWFcAAAAASUVORK5CYII=>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABS0lEQVR4Xu2TLUsEURSGj2BQ0LIKBg2LzbiIxQ8waNSoP8Cy2aK2LQZBBLNRxGJUEDH4J4yCQTGJIGpQ/HjeOfeycx2RnbBtXniYYc6Zc89977lmlbqtaXiA78A1DCcZqRbh0zxXz0sYSjJy2oV7uIOxX7Eo/XwMz3ACvWk41QAcwj68wmQaztQDTdiCL1hPw0WNwwGsmG9rKQ1napgX3YQPmE3DRS2bdzAFb1bsoh9aMApncAMj+YS/1IIFmIBH2E6iZqvmcRW9tRJ+6nC0uro4MvdQqsOGeREVLuVnn/kCVwG9q5AK1j01ey/lp6Tu1GX0TJ1p65IWLe1nlPyUr/OwY35IkuzRDHfkp4ZZFkTJL02AftYYRXXs5wycwmDum2ZUsypL4mFJ2sG/fs7Bk7Xv+zushZhu04W17/MevIS8mHsOtRCvVKkb+gFM/0ZwbSwG7gAAAABJRU5ErkJggg==>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHUAAAAYCAYAAADEbrI4AAADZUlEQVR4Xu2YS6hNURjH/8ozb4nkdUJKChGlKIqBgYmSbh4TeSTFTB5xC3mMSFLelLwHBoqSbhkYGBiZKOmOFJkIhcL/f7697ll7Oe557H32ubfWr/51zv7W3vv7vvWt9a1zgEgkEolEInkxnnpJ/fH0gVpETaFeB7a31OzyncCmwPaIGp7Y2kF/j6WD+oqKD4+poakRaXaiMvYndR3B+H2Jcbd/MeEAzLYuNJB51HOqFFxvJ/05Fk3KXeoT9YIamTb3MIt6Sv2ijge2HjbCglVCQlwiNMZnAHWIWh1cbzftiGUidRHZV/dk6ib1kOqmJqXNZQbB4jgBi2VN2lxhLWyABvuUqHeonqS51GnYSxplBLUdvW8vzVJ0LELJvwGLKwvLqFMw/77BWkeIJlE7zTVYe5mRNldYRf2GOeZQ9R6jzuDfRAyEVYqS0QxLYfe3gqJjEXlNqvzShEnVVuEEqhO2ot9Qz9DL7qCKUGX4idC1k6i8wLctp/bDktUoWg1nUb0K86DIWBx5TKqK6wI1B5XC9NuE/NsDKz4X43/7qXCD3My7xKshh0mS43r51OR7I8ixXdTe5HMrKCoWnzwm1fVTHY7mU1+QbiFLqG3J5x2ovpJTyKluqgvmmA4MSrwIk6Tq0UMbZRR1LtE02Dsb0RjUR6tjkR+hb5qE+7DCCW31TrTrp8LF4BdfJzUathhq9lPhHvIK5thV2P4ttB18hiVpJnUe9TvqGEIdhSX0Ceyk2KgOopf+4dHKWPR++RH6dot6D0t2aNtavrM2rp8KrVb9pHHFtwU26UK/x2v2UzEWlgQl4wi13rO5JOklh9H8sV+UYMf1BcH1PCkqFh89N8v26/dT9/0BbPJWwLZh164WU99Ro58KOdMFa853qGGezSVCe/htNH/sd0ynLsG2klZQZCyOrJOqfnoPVpCOy9RH2HP1j5ijrn4qtIy1nH/AToM+LknaOvM6saqXbQgv5kTRsYgsk6oV2AHbut1qFNqOVZh+ntwKrtlPHXJK1aEbfVwi1BP9l2ZBlaffjOG78qLIWESzk7oZ9r+tVp6kE+/KxKY/UbR6tZuoULXr+GP1P/EVanAyviqqXDXhaiykxoUXM6CE6jCQZ2J9ioxFNDupkT6MJlMHsnBniEQikUgkEon0Ff4CqFD5nmJngqoAAAAASUVORK5CYII=>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEsAAAAYCAYAAACyVACzAAADV0lEQVR4Xu2XS6hNURjH/0KRV1yRV+6VlLgDCSnUESKRZykDRkgiFCGlJCMlA+WVDGRCRooYXBQDBhQGJI+UKAZCIY//37e+e9ZZZ5/HnexL7X/9au+19l7nrP/6vm+tDRQqVOg/UH8yjPRMOwqVVSLfyG9yg/Sr7M5Vg8hZ0p609yAzyDFynCxG9qIOJNvISbI33GcpHW9OaGtKo8kbcijtyFH6s3vIFzI1ad9FbpI20kLOwwzpHT03kTwhO8gIsjHcT4iekRQMWpDLsHcmkftkfvxQPc2CRdfStCNHaaU/otosXb+D/UfXOPKKLAz3KiEd5CrpG9p6kYvkQriWZPxRcgsWxZLMVVbtDvcNpQc/wJzuDumPn4JFS2qWol3GKFpcA8htWITIgHnkFzkXPSOl89K4Gl9R51JW6Te0AJlSvmuAJWQ4bAU6YCuUtzRZre5K2ORis/qQK6g2yyPpHhkMm4eiI8sstatfOkB+wKJUY2hM/UZNyaQH5DDZEK6/w4pdd2g6OQKrP6lZbkots7y9kVlaDDde42vuJ0L7M7IZGQV+LHkKK6TeuR42YKN6tZ+87gKqH0P+vllbSj+lXmu4T82SETKkkVltsA1Khd/n5TXL65G/o/vToV8qkU9I5q9OFTsNqsFdaV7nJU1qO1kdtaVmqUQ8R2OzNJZ2TEVJa3jGN4zULNU21TiXL4iirjMlZYZMkdvuqrvfgfzr1RSU08+VmpWa4spqVx3eAovql7Dz00GUa5aODDpHphtIZvR6Xsc7wSjYwM3UKy+IzdLoa2ATqlP3M+w/voftdiNhi1nLLD2jnbGWNK84a5R+XTJrkTfAdgXtDivITFha1FI7WdUF9Dt+5mlWaWR5W1omhpLHKC+yMkRRegnl85MbGp+z1sDOk/GZzc2qSMPJsB/1QqZB47Dch8pc7g7pE+UrmRa1jYfVWU3UNRsWfVpgyY2J67GOIm9h6e5StD9C5QG0hIwCryKonH5IzpDrZDns5Wuorh95SoukySvyxU9yBzY5SZH/AnbUWQf7jEm3+53kLlkLizg9Pzfqd6lNpur4sDVc6914rE5pFeJ6IoMU1vXqy7+gFlgpEbpOpcm2kmWwD+N6C69ivwD27Jikr1ChQoUKFSqEPwR62OJnQeDzAAAAAElFTkSuQmCC>

[image25]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF4AAAAYCAYAAABz00ofAAADsklEQVR4Xu2YWahNURzGPxkyzxkyXTIkD5IQGcpQFB4McTM9GTLFgzwh0wsvpjyIJCHDi7oyJCklRXggCnFlCKF0qWv+vvM/y9l7n7332ffe3HNof/XrnrvWXmfv9V//9a3/PkCqVKlSpUqogWQtaRrsKHWNJ0/I84RMtGElocbkFLlGWgX66kujYHH55aGKvMp+/kHOkf5ugNSA7CMnSVn2f+kg+UkmZ/9vSMaRZ2RYtq0UNAP2nJWka6CvvrWHfEF+fPrBEvsB6e4aO8MyppNroNqRm7Agd/O0tyRH4RlcZOmZr5A35DXp4++O1QByGJapFeQOuUUWkmae65JKsblK7pOO/q6MjsCyf5prkG3IH70aTD6RM6SRp10LolUt1pYOah1ZBpvUZzLU3x0q7eiVsGTrHeiTbc0n51Hz5NKia/G1mM41nNyiVJORrnE2At5DzYOtzvpAeweyBPlfXAwNgtmjJqXAfyOjfVeEaybZCwuy1AK2i8f8uQIYDluYNp62QpoOi9nSYAc1B+bzsnRvIudJ/p50IsWQHn43csFSgvi2cYRkq1okJZACr3PLZaMb2wSWWApgWBCjtB2W0VNgZ43oRTbBrLAcdr9IRfl7ErUnF5BfBcWxITOyZppEdiGXPS7w2qlxmksWk+bkIjkLKyiOw7J8NXlLRsDmrgTUjigkt3jvYFZzIMshmOdvI63dxVGST8ovg/5eKtL2P0H6etqirDGo5chVHMr6neQprNp4BDtcx8IyXu8E+5GsUorz9zJYRXMb/gImT0knUSzpMNXzhaGDP05b4D+AFXyNUTn6EHbweQO3FckCH+fvkqtoZEOh0k21arX1d43XZJzHJaFtZmQylcGyXffwyu1STTBOa2CT105WUL+SjTBLWEEek+uwikaVm+wirDQMKqp+l1Sayn61uJEvnnXxd0kH1gQyqwbIT5NIwZKvy9+DcoG/jHhPVkbvgB1y8nvZirz3Eiwo+iyfV0K4a4PWEVSh+l0FQDXsHro2VKXq7wpUOWyCYSVeT/IS1h85OVhiqBryLra+7wb8FZErUYd42qKk34nek2PwL5KeWbvrI7kHq3B8Ug0v4/8Av19WwQ6dJC8lf1MLYJbgnusucpml7FYtrxrZ+9xxlZICUIGcLShYOhzd26q+U9WMXrLisl2ZXIncffUML2CVmv5+hznHKtTuTfi/VBdyGpbV+oFL1qLfU1T1KAmnIj7oqeqoHmQRrGzcDPN890abKlWqVKlSpfqX9Bt9JtWHxpz7QAAAAABJRU5ErkJggg==>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJQAAAAYCAYAAAAcTtR3AAAESklEQVR4Xu2ZSYgVVxSGjySCwThLggPaBokIikpIwAlcGETUIEaUKBqIiOJKXJiBLBpFnAUJbhwQFBMXQhaJIiGLXggKulEQRBEaccCFCkHFAaPn61OXV3VfVb9X1e+9avV+8NOPU0Pf4dxzzr0lEggEAoFAIBDoKTNU91SvI11VDU/ckeRr1Suxe/n7r2pY4o7m84PqVp26oppsj7Wcj1THpbpNWTqp6t/15DvAHtUd1W3VaO+aA8f5Q/Wf6pTqw+TllsAknVHtVn0a2ZgEHPuRalJk66taoboh2f1pNrTlumq5ql9kmyI2fmfF+gKDVEdUJ1R9IttbzcdiK2m/6onqi+TlLujoetXPqv9Vm5KXWwaTdFQqkwGfiUXZDrG+OEaITdKAmK0IOAELLi8bxMYszkqx6P6jZ1+k+sWzFWGjar5vbDVMyCHVMrHO0jmfaWKD85PqpWpW8nLLWKv6xrMxgLR7m2enX3ul56ueBfabb6wBEemAapRnPyzp44ejLfFsRcBR0+avpTBBRJ4vVU+lOvoQDdrFBue06qZU0k0rIcXiUH7NhiPhUL6jfa761rMVoYhDjVR9L0lnHqK6qOqUakdbrJro2YrQKxyqXTVXrEMPpHqlUwNwnUHolPLqpzRc/UTKIyI1gyIOlYarn5o5fqU7lKufKFyJOkSfeHHYJtZIBgCnylM/jVddkurdTHf6ruvJ+smqnxpJoxwqq35qJKU7lKufyPlMSEckfuNENLDNbu36nZb/y4Q0l1Y/xflEtVoqO60sWESkU4r5uOaJ7cJ8O6r1TgfvZjORNX4fiKXng2LF+cDk5SrYxRIA/PZsFeurb2cM+B9Nx9VPQKeJTq5GIiKR7oCBK7N+yiKrfoIJqr9Uf0t9EYxB5ziCSY3rT9W1FDuqd0fVXf0E68QcjUn/VXVOqmvFOJwf+m1BZIR/Uuzs4Nt4sNm0izmOgwmijpqj2imV7Tkp8bbky/8MDpPkr5buVGvS47iIWqt+IgV0SL53x2lEyuMdHMmkjZ/rBztAoC93pX5njVNqyqMjHFTGJ4P6iJ0eHeeowJG3fgIK5gWqpTmUZ6dTb/3UGxyqVv3Eaf7Y6DdjgEPFF3q9FHUoFn+bVKdwspEfKTmIHSkpxzEzxdJB/OCPxtBx0mD8ASJXVv4vi3rqJyjboWrVTz44BWmrSHuLOtQasbEkwLgISslwXywzjYtsONdl1XPV9Mgms8U+U/AC9ELshcDg0RnnlftUj6P73L18NhgaXW81tJ06Lt4m9FB1QdI/s5TlUFvEJsN9+3Qi+nDomVYkf6X6XYqPb1GH4plnqs1SCSSMJc7DsQxRCRhDPn1dl0pEfe8oy6HyMlW1XaxUwKGoP/NS1KECOeipQ7FZWOgbGwyrfZdqjNj/WyX25SIvMyRfHRrIwWDVDtV5sR3WMbEo0NugEOZoIp4WSZVp6TsQCAQCgUAg8A7wBnnK+4oMABQNAAAAAElFTkSuQmCC>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAYCAYAAADjwDPQAAAEdklEQVR4Xu2Ya6hmUxjH/3KJxp1GQiOhkEsJmWiGKAoffHC/fJBIiRm3oswoEl9cc5eDlHtJmiFlmpGI8IFIySURkhLK3f93nr3mrL325d3HZc7Q/tW/c9611rv32s+znst+pZGRkZGR9YBTrGPLwf86C61PrT8yfW99Xv3/m/WctWf6wnrE7op9XllOrENOVdgr2Q5bbVpbUed8zaz92ZpSz/pbrR+tg4rxPawPrfesnYu5uWQj6z7Fwz1YzK1rMOpj1tfWGmuL+vRaOETPW79Y1xVzDTa3VlnvWtvXp6bhoXn448uJOeRo6x3FAz6pcNIQNrROst5WRBmn9WPrGesQa4O1K4ezk/WQ9ZT1ibVjfXqajRURfb3ClhNT7m7WF9YDam4qOewn69D6VCdbV+qD+2xSDg6EPXEycQxGWFWNTWIrxQG73NpMYTw+893trNsURsOAs+Ew6wbrCusH68D69DQ44USFjbE1Nu/lBIX3zisnzMmKunK7Jp9G0tsrmsmZpLwj1XQ0sPaMcnAg5OXLFEbFKa9b29RWNMHQN1vHZWO5U4B9cl3UtucucAYGR21RMN9arogostGL1rx8QRvkNyKBi7FRtMBaZn2pKGaEfR+cvCnFNVjLQ+1nvWo9rXo9Sg+Pw2fLLtYjipOdorgrZeQcY12qurFLpwDO4wDuk431wUG909rLOsr63To9m+d+FymuRwQRSYPrCUWK0Lqn0v0Kr15rbZkW90A4nl0OKhyEU79R3Idrv2U9rkgns4EHJE0Q2ZD2PikdYLib1FzT5hTg+hcXY12kekJx39/6TvVu8GDr3Op/MlFbJDXoqye7KjqvNxUh2AcGZoNdEK40CmyYEzMp8tqgEN+rmZyPsSnyXXk8QWq7S9FJpkyAMOITiq4oH19s3cIXB5DqCaR0iqMBZy9X2Abb/iP1BLjBIO8qbkyaWKnIm6cp0lobpJ9F5WAPXOdZzdSrXKQMUkcXGOs11TMBIg1+1DF+x/Q3J5PqCRAttMSpZpylcBrQ1Q6uJ13vJ4AhMPCkh05cYr1hnaPIqyus99Ve7DnZrBsK9edqNa+DUXBMX7uOEeisyna/K31hC9L2JPJ6kj4TuRh/sSIrpP1yTew8uJ50vZ8crmgAXlBz4yU7WDeq2U7urUh/vAeQLjAEJ+tlRdoYAk0CNagthSanLC0nCq5SRHFOl1OWqLm2DdI1+8o7P15ov1JcN29uBtcTPEwBJlzzE0i+58vfKl7QFmRzXWDwvN3MIeIIZaKGqFutcNYQOOU0HcvKiQpeBHlYnNMHBwBD5c1Fm1NYN1WMtYG9aGBIfbnt2AfPmHeWKYJ66wkRQEFKOZn3kM8Uv4Hx91fFW+6F6q4J/zb8dPGw6rWDDiqxr/VBMc/+F2ZrSohQOqVtq8+lUzikpOsDqs9dnKn4JSDdl47riGqONEr0kDE4UI8Wa/mdjEP2V1+c/5csUhR98j1FmO4Lg95tvaToOEfmANIzjcY1im7rAsWv4GUTMTIyMjIyMjLy9/kTeNr2iK+8Q/IAAAAASUVORK5CYII=>

[image28]: <data:image/png;base64,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>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAYCAYAAABqWKS5AAABjklEQVR4Xu2WzysFURiGP6FIkZSyo5Tk18JCZCFRNkpslP9AShaysWRDKbJVLKxYWLEgFjYWVv4BkZ2trXhf30zNOXPNnJk7uncyTz117/nubd5z5nxnRqSgoKAa6YSL9mA10wuX4S38hCdmuTLUwyZ7sAQMPwfH4JtUOHwz3IQPooFc6YAvEhO+AU7Aadholn5qNA28+CG8Ew1da5ZjiQ0/Cd/hl+cNbPFqvM37sNv77koXPIJXcBDWmGVnIsP3wWe4DYdEu/oVbnj1Ubgl7hfvgWee/FwukeH34II1xgldwDa4A/vNcghOjKvLVeZqc9WzIjJ8q4T3IcNwq/AuMHydWQ7RLrqnj0UvliWR4X9jHT6KbhsXgqvPC2WxZUiq8POix5rfuElg8HMpv1lJqvCzcMUeTEjwmByRdJPww59Kgv/zgTJuD6aEjb8L70WPZbvHSjEl+mTlq4F/hH/AJzgQ+F0INvGl6CM6S/hasCq6Jf+MYXgtOoncsQQP7MG8sAZn7MG8wIZy7uyC/8Y3Uk1Aq2kQ2cIAAAAASUVORK5CYII=>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH8AAAAYCAYAAADTTCLxAAAFA0lEQVR4Xu2aa6imUxiGbzmN89k4xYzMlEMhhyJqRs6n5NCYjLFDRM5yCGkjISGGyChJTmMaUxiMci7+8UOUwz/xQxLxY5TDfe1nrf2tb+093z7NF3usu+72+6613udd31rPcz/PettSQ0NDQ0NDw/8R880fzb8T3zQ3K/q3NlcX/XCFuUUxpmEaYwPzSfMPc415RHf3EM40l6vbMRrWA2xnPmNerYjsRxUOUeI687yqrWE9wIHmQ+au5pfmd+bson8jc2ka1zB5zDAvMbesO/5NENGXputBRfRfMdwr7ahQBhSiYfJATe82D6k7xgmcZ555mrmbRqoz2NDc1zw7/eW+Jx5UZ0IHmD+bn5jbpLajzCXpumFqYJ0fUKjpRHCo+YP5vfmbIkA/MGcVYw4zvzbfNS8yH1EEbd7HEcj5nugGTOoF8y/zxNSGKrR8v25AtF5jLk7X48Ee5ivmPumeaKY++9P8VhHhh5tfmSeo2y7tt1dtw8j5vuxk09l8nIDqfrrmezz+svS3X9hWUStNhHuaTyvUlKP0WFhonlu1sV83KhTgc8XGn9U1IsC428y96w5Q5vsMFgvZR/6P0fTN9zgsJ5d+FVh867hVcUyeKPme8rt5l7mpeqNMyyU2VtjCAVabm3d3D+Na89i6Ea/A+8gVNRYpjH5h3lf1NUwN5O+XFXI+Htyp0Tcf4OC/KvYKJRhN3q9U1G1dqPN9iZmKYx9Gy3xPTcBx5QlzjnmL+YZ5vOLj0EvmY+Yu+QGF1BEhr5kXKCZIxbrM3N+8WGFjwJxrPqWww3UGXo70kfuwP8vcyXxYkf/4CPW8Yg7YP8NcZR6kDkhh2OBjFUVXTgd5PPO7t2jvB3YwnzX3qjt6YEFiDeb5tsKRUGlqgFr6UT3eN7tqH5J0PtWuTS4GzZ8UBUXGweap5nPm44oFxSupRNkAcL/ioxDAy99X/FgWGZljQ6hGcZy3zO0VDkLxcn0aN6BwAsDGs+HkPvpQKhznQvNohTrhfDjGoGK+Jynscw9YKPrz4rDZjAHHKYoijlIvKo5T/cLlGpm/xwJzZ61Lh2HN2HTaWZ9TFGkEotq0kZZIGTeoUAT0Px8X4BrFwzU49pGbyny/syIiP1JHik5XbAaqALmmjcV8Pd3zg5kIG4b3U/S8msYBbOHF+V2ch29K1zzL8SXnbsZ+Zh6pKE7Jd/SxSPxo5oh9Ij/LHXXNN+b5Crtl5NP3i0JFcO4xz8aTBOuBE+9ed4wDpAjWZ6X5jiIoCRR+b8Z+5sfq7CtKcE81ZsrotVHIC47BX6KZqJyf+kqwAB+qU4WSWqiA8dAsZ0g4IDXxjgzGvqfYcN5b9mXwLDbyBmOD2mU4AgoQIVeZnybinP0A794q/Z0sOF3g3L0clHVh7XG2dY5yo3gRkZerSfo4InK+RKZLhQDkeJ4hIolMrrGDvXzqoA/vxpNJD8j/QOojzSB3yDc/DvXI8l2CDxw4xskKBcv3GdQkyCj2s6oQXahUP3P+tAfHi5y3WEC+NGUpo528eYdiEakDyEu0I7VsFJtNTTAYjwyNI71kJyFqKQCpD7BP3UA/xSJOco7CxkzFxqEyNXjXEkWly1jsMC+cEye4WeFI8xSKwPyWanSVaihAgZhlh4XdpOgDSFspS0QoUlrKHc+UuaiWKKS47MceNkq72Fvb/xWMJrE8y8mmzoHcU0BNRY4bGhoaGhr+a/gHZlzhG7LIwCYAAAAASUVORK5CYII=>

[image31]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAABLUlEQVR4Xu3SvytGcRTH8SOUIlIipcQiEyVJyaasNuUPkFIGg5KB0aBkMclkUGaT8mMxWEkpg7LIZrAYeH/uOffe7308/gDxqVc93+/33HvPuc81+89fSiPGMI3mmrOOOntFdLCLdVxhJzkbwgvmk71KZrCBdlzg2LwTZQHvGI/1tyxhBJPmhelT9nCHLsziFUdoSGqybOIZA7HuxI1Vi3WzxfhdpM285RM0xZ66ebOyWDe7xFSsi/TiCWvJnub9sLJ4GOfmI1TSg0crL9bfc2blvIpulnZWRDOtms98YD7rJw7jTKk7r9ISNLu60JvXvPmb/3HePtybt9lq3tY+btEdNfm8E5iLvSx6q/qKls0vXMEDRpOafpxiC4PJfvZ5at7rsG3+tdUmH+235wu60zG0SAoRdAAAAABJRU5ErkJggg==>

[image32]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAYAAAAZCAYAAAASTF8GAAAAd0lEQVR4XmNgoBngAWIxIGaGCWgB8R0g/g/EV4FYBCYBAoJAfBqIlwIxI7KEJhC/BeJ0ZEEQiAbi30Bsgy4xiQGP+WuAmAVZgnTzcUqQb7E6EFfDJDyB+CcDxPwsII6ASYBC8xwQ7wfixUDMD5MAAVaoAhA9iAEADUgZKJL1EpIAAAAASUVORK5CYII=>

[image33]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAYCAYAAAD3Va0xAAABcElEQVR4Xu2TPSiGURTHj1CKSPlIKZF8TBSSkk0MBjay2KSUQVIyMBqUGJSSUgZltlA+FoOVlDIoi2wGi4Hfce7Ded5XnvcZ3s2/fsNz7nnOved/7hX5Vz7UBVuZwTRqhj0YggWYgiWfkEaNcACPMAHF8eXcVA07sA/bcAKjsQxUKNb7gGTvUhFipdAG3WIelUOLy/tK2hDr9xLW3VorPMO4i9XBiPv+1iAsi+1wDodiJ1RNwhv0hO8/NQMd0Cf2k999E26hysUStQJPYpNRVcK12JQKQixRZWJtHUFRiOkpX2E6fA/DiyQUVgP1biy6mPrzDv0upq1GhX9VLTzITyEd+anE/dFWLyReOEt61Hkxj3bFvPkQexJRG+1wJgnGlwTUKz2dTlD98RPUVr2HWaqHO7FW9PZqoj6BG6hxeYn+6HT09s6KFZmDe+h0OTn5o09E/bkKrIndcq/In14Yy1hLpQY4hlVoylhLrWgg+dUn7ZM7Xp2nBJEAAAAASUVORK5CYII=>

[image34]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABj0lEQVR4Xu2UPyiFURjGH8UgDCSlqFukpAxkY2O0qDtRJlkMNpEYKDL5kyxSJgaLXVwZDAa7MphMFmWw4Hnu+x0d53zf7dalJE/9hnuec9/nfO95vw/4129QM7km7x6PpJ+0kdvAuyNdxX8CE4F3SuoSL9IcbNNMaFALMG8sNKheck5ywXqkcVgRBYVyAdrjq4oskpFgPVWjsCIq5itH7pEe3kM2SE2wnqph8kYOvTWdcJVsIg6oJmuwkLKkS33B1wCtrcN6rwDfGyLzsEOUJRdwBpsEPfYW6fQ8F1BP9kh78rsstZIHUoAV0MXNJl4YrsueTjynBnJEnslA4BXlAm5gpz4gLYnXTZ5g4R1kF3aIUNp3AXu3IjXCiitkmeQ9z4VfkSVkj6We7AQ2AJF0ogJsko5Jree5AF202pA1ltuIW/cp9VY9foVNiC8XrnvQfaRJHbgkg6HhS1Oyj/gRXcAKsseyZP+ddLqsDX2kKVz0VLL/3yHX/0lkH7Ii6aO3Q6aQ3caKpKJ62X6k+B/WB47tUgf7kHnSAAAAAElFTkSuQmCC>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAiCAYAAADiWIUQAAAEPElEQVR4Xu3dXchNWRzH8b9QCiEimRrjRppkJoxG5o4aTTMXuKCZy4mUcmGivKXBxSSJZkpqmnJBU0INmqIcuTDNXM2FFKmHvMSl4oLx8v+19rKXdfZ5znnmnM5znuP7qX/PWWvv9lnO1a/1spkBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEa+Q8Xfb72meK3zWlleBgAAGBkm5R3DbFze0YZvvEZ5/Za0F5aXAQBAv/nZ63Xe6Q54vbRw7Qev0Un7eXHPvaL92Gt+0dcLPvWannd20VKv1V47LMx+yRdeZ9/e0T4FtFt5JwAA6D+apdng9afXd9k1meNVS9qLvU55jSnaCiH7yss94Uuvf/POLtPvdtzroteSpP9zr4+Sdjs0u3Yk7wQAAP3nY6+pFkLO39k1mel1NWkrJNS8JhTtw16z48Ue0QtBZprX1xZ+vw+Sfu03076zTrhunXsWAADoYaeTz6+sft+Xgtmd5PNnRVtBREFPNRwUgg563fD6w0JAu19cu2vv7uda5fWTlWM9Y2F5txPGem23MBaZ67W2vFwpDcDNxLHHGUON/ffyMgAA6Hdamkv3eSlo1KycPYueWrjvl+LaE68FXkeTe7Tf7b+k3a4ZFkJhXhqHlmN3WQhK2jsnyy3sr5MYKGWR1/def1m5jKv9dxr/Ta+JRV+kADbYd+c2WljmjCFNwVGza4N5mHdYCMpV+9vi2E8WbY1d/1YAAPCe2J21FRo0y6ZZndQLr51eKyycdFSAUxBKZ7EUUi4n7XYda1Bago3Oe10qPm+zMgilgS16lnzWQQnR3r3cJ1b/nVXfndpj5b60fyzsCxyMAm9OAfJR3lnQ2GMg1NjTJVYAANDHFHA25Z0W9rEptKV0ClR73dL2QNIWhZ+qfWPjvb7yWtOg5pW3Dplm1OK7xwa89hefH1gIQKla8VeHAXRfJwNmXDIWhduoKhDK7byjiZqFmc04dmn07EhLs+esfrYUAACMIApdg5Vm06L81REKdfneNYWfdsLXUGkPmmbY4rvNNLumQCM1qw80mpnSkqOWFGdZ44D5f2zx+tXC7JoOPIh+i6qlUS3LKiwPhcauk7lx7NJK2NShBwIbAADvifz9alXB7IqFE5DdFMOaQpCWRjWbJ3ssBJxI4U5707RMWrNwv6536oSlxqF9b+leNj077plLaelU97Uqjl3Pr1n5TP3ezRDYAADAO054bc07u2SZ1W/E16yX9pIpxCnMaX+eDhnEZWCdjv2x+NwOLb3qmZstPF8UXKsClWYlL+SdTcSx6/13cewKba2ETQIbAADoGY1e0bE37+iSDy0Es7hEG6235gcSWqEA1yxsTva6ZuHlvTpIAQAAgEwn/9/QKnH5FwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABa9AbZ6qXGOE6GBgAAAABJRU5ErkJggg==>

[image36]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAABJUlEQVR4Xu3TsSsAYRjH8Z+kiKJYFJGk8DcoyWBUbEaLySCDZFDyD0gpGbD5A6RMNpJisTApMVkkA4Xv47n3etydjEp+9am393muu+feO+lPpgnDmEQ/arP9RnRk61IGcIwn7GEOuzjEIA4wmndnqcMSXrCAhq9lDeERtyrc2S7cwCsmYiGkHvsZW+eZwTtWUBMLhexgMW704g7X6IyFimypMO+y/K5rcfObNMtH/IwdxxHeVPEGf0o7bvAgP8sYm71V3hO1pIZ0sbF1jH0MdnQn8uOz0c4xnRracKnqi1PSaPfoiQV7tHX5zGOxEGLj2Fil87V04QoXKn+z9mY35Y+8Wqjl6cMpnrGNKXnzGWYxj5HUXBUboRvj8j/JfoL8TP/zm/kAj68y31zxjSIAAAAASUVORK5CYII=>

[image37]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAA2UlEQVR4Xu3SPQtBURzH8TMYDB4ySZRZmWRRDMrsTXgHRq9CRikZbFYLBmVRXoNioQiLRQrf+3Dq3r+Lu6r7q0/d7u+c0/13rlJBqtjj6XDGwX6+oo2Y3uCVHu4oi/cFZR00QUR0ZqJYYI2k6IwNczxQc1dWcjhhhJDoElgp768yU1fWfE1ZkBJuWCIuOjMd5X2ysXiGI4qiM6NnMk4fomsbYIc+MnqxjJ53iixSDmHHOs/oeVuy8BNj3o/X8C36fjdIu6vfyeOCsfIxn04FW/X+Pzeci4L8dV5HLDA3ZZscAQAAAABJRU5ErkJggg==>

[image38]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAZCAYAAADuWXTMAAABT0lEQVR4Xt2TsStFURzHf8IgZCBSRovHojDJYFDq2RiExSBlNMimZDAwSCn/gMlgsklZZPYmhJJFMZkUPr/3O+d699xzX2+w8KlP993f95x3T+f8jsi/pB0ncBr7sD4dZ6nDMbzCU5xznuEtDv8MTdOI23gv2UGaHeIbDgZZOTzAVxwJMs+A2OR9sRUmLOOne+bRjY9Ywg5f7MVnvMZOX4zgJ6v6u8wGfrlnNXrwSSomt+A5fuBoMiyO5jruAlu1EF1KDmsSrPBXJidLyaENL/EF+31Rt1y3/g67fDHCvNhRrlYWG/BI7PC1CbRZNsVacce9a9Norh2m7ym03Xw4izOuvoAr+IC72OTqGbSXb8SOYkvsMpyIrWBcrB31VmW+7NFgSOwKTuGS2B95ii6viUV8F9ukPTyWKksPmRQ7V1X3JO+2RWnGdbGvFoLsr/INH4lDrnpTAjYAAAAASUVORK5CYII=>

[image39]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAiCAYAAADiWIUQAAACTElEQVR4Xu3cy6tNURwH8CWU9yNSishMBgZSDJSBRCLJwOMPIMmQIQbGxMzEKxMGGBgxYCYMSSlloIRSzCiP32rt4667ukf3dm/R7vOpb3ft39rn3Omv397rpAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADA1FsYOd+tn0UWRw6ObAMA8K9tiuyJTItc7Gr5GgCgNxZEvkfORs5FdkUujLpjch5HfnV5F/nR1SZqReRK5ETkUuRLZHq1vyGytroGAOiF3KhdbmpH0tQ3PrlZ21ldn0oj07Dx2Bc5mcoUbWB25FV1nZs5AIBeWRd5GlnS1HdH5je1gWWRWW0xzGgLlXz/+8iaqpYneTnj9SmVBq31s1q/rNYAAL3wLbK0LaaxG7Lsdvd3ZiqPNvPEK8sv/V/t1mPZlkY3Z/lzudGqp2V/sznypC2m8vk8uQMA6K222VlepX43bGBeW0jl8enKtti4H9mSRr57mHuRu20xXEtl6tfK76yN1cgBAPRG27DlZulz5GNkUbOXzY08T2Wa1k7H1jfXtbdp+CPW2tfIh7aYSsO2sS2GM5GjbREAoE/ax5L5UWiehg07cHC4Wh9KpblaFTkduV7ttdrGcKIORI6ncmjhRSr/82HkdX0TAEAf5YlZ/omNR5FjkRuRHfUNk/QglVOouWG7GZkzentCbqXyffvT8AMIAAC9lA8MbI9sber/mzwJ3JtKw3anq63+swsAwH/lTSpTu8EpVQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoMd+A0o5SrDtT8uIAAAAAElFTkSuQmCC>

[image40]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAiCAYAAADiWIUQAAAE70lEQVR4Xu3dW6jtUxTH8SEUHULkuOaElCTJIcQbDxJJxAl5EIecTi4nStIhntyvySWXQkSUS0KseBFPyqVcihIhD8QLuYxfY86zxp7nv/b+77X3av87fT81Wv8513+v/muthzUaY87/NgMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbNt287i7HH/ssYfHuvHTAAAA6LJjOzFDx3uc6bGdx31lTmPZvswDAIAB+drjvxIHeByTxu+Xc+r4gTIegtttfF2bPB7y+KeMLyrnfF/GP5fxEB3t8V4z96ON35uu/Q+Pe+ac0Y++zyc8Nnrc7/GbRUJW6bs+PI2rp9sJAACw8m7zOCONn/E4KY2VqB2RxkOhxGaUxsd6vJjGJ3vcmsZD9InH6mZuV49v0vwuFu/zlHpCD2d7XGdzq2U7e3yRxkrmuuzgsbmdBAAAK+t6ix/46k+bm8BdY7Nvkx3STvTwnccH5VgtRSUgoy3Pmt3rsSaNhya3JDNVvZR4KnESrTHTWrOcRC/kF4sErfVvOv4sHbfq2jYAADAQSs6UtMlZ5biOLyiPs3ReO9HTyCJpk4c9jkvjPUsMgdq3j3vc5HG+x0sWyZRakoqWkricnL1jkYD1dYLHh+2kRYKoNmsf+hxzEg8AAFaYkoanPC6xSNiUwD1m8QN/ajovU9vud4s25LS0nmpksY5r33kir7vKdM2qBu5t0TZU6JoOtUjgJlHyo7bvtHayra+xRluJPNBiV+bLNt5YUNud+pz1N61fPQ6y8WtOotd9pZ20+FxyhbTS99yVyHUZWbTKAQDAQOiHXC04JTmq/GitlH70tW6ttuW6aLH8Xu3kIpxu0ZZ71OOReeKw+gcNXePfHjeWsRIpJXA3W3flqlIFa307uQin2dbXWGP3dF6lFqfayqKksrY7JyVsfatgR3n81E5afC5difRmj8vbyQlGFkk7AAAYCCUNf9m4OqRkR2udlPhkqzzesHGbtCY9qhypgvSgRcKnBEzVH7X/1nrcWc7ror+9o53sSW1bJTd5Q4TGqrC1dA2vleOcaKpNqXldt3ZS3mJxTfpMVG1sK2bTUIJYNxDo9hm13alHJV2ZKpffNnOLpc99g0Vi+alFtU5t1S/zSQvQGraaZAIAgAFQ1aeuWRMlKxemcfW6x9Ue+1lUjWrSU29LoUTvRI+3LRasv2vx2jeU5ydRUnRwO9mDKlRfNXMfNWPRdWpzwsVlXBPN58qj6FYWSqZesFi7pQpYV/VrGj+k45GNq5b6bHKlT+vG6u081J5eCr0PfQ/n2OQNCPNR5XP/dhIAAKwcJRCqnuVx1w+8dnLqvmCqVqnKVhOPutZJc0pC6liVJf3oryvj+Uxz41i99pHNXNd9xeRJi/uZKZGsFa7Py6PehxJW7TLVe6g7N7W2bjnk3Za6FUmWd4MuJyXBqhAqYVP1U9ZseXZhSmZncV0AAGCGlABcabFOax+LdWOXlvk3LZKdc8u5b1ncrFWPas8tR1txKdRyvcri3zGpPahWryp6qhZe5vFsOU/nPO/xqscVNnnDxVK0t9K41uOuZm65aZODqna6L1sfqq5Ok0ADAABsE7p2vKq6OU1LeBa0hk7/IQEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMCz/A8XZu8hM9mMfAAAAAElFTkSuQmCC>

[image41]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAABS0lEQVR4Xu3SvytFYRzH8Y/8iPwqlJR0UxTyo4RMVqUM/AMmg0EWCmWhMFgYlJQiKVKsBikGNgMli0Upf4CV9/d+n3PuPVdks9xPveqc58d5nuf7HCmf/0shRnCNJ5zhGecYQEFmaDLVOMQ8ynP6arGFVRTn9KUbrHM8q60Tp/KJFlt1NkjsYBhLobE0tPXiHg2hvQRl2EVHGKMi+apt8tXeMIdunKAJx/I6VGEUM+mZpAJrqJSv0IULPOAFr9hDYxhvi2yEZ9VhW/4RS/SBW3xiX771KPa8HL1YZXdQHzqu8I4JHGERH1iXF7YPK8qKDbCi2XVNy7doBbuR76wdk/L6RGPjpOTnsslRBvGo5JatiAfKHDHOmPx8NeHdrqVZmTu1Ql2iJ7x/yxDusIAW+ar92JTfQCoe+UPs/7bz2l1bIafQql/+63z+mC8IDy+v/ogRRwAAAABJRU5ErkJggg==>

[image42]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEkAAAAYCAYAAAC2odCOAAADf0lEQVR4Xu2YW6hMYRTHl1DkWuQS5biklEhuKY8o5RJSokgeKFIUOlEIkUi5PbgkDzhJeXDLJUYekAeXSLmUJEp5EUUS/19rf3yzmz2z5zhHndr/+jUz39qz59trr/X/vj1mhQo1Q93EGfFNTE7FCkUaIW6J3ulAS6qT6Cs6pgNtRHPFOdEhHWgJDRNPxS/xQQwpD7equDHrzH//mjgiHomH4ob4Ll6K9aJ78p1YA8VecVRcEGvLwy0rJntJlETX8tB/0VixInm/TfRP3vcT+8Q40SQGJeNogridHMONfWWt7EcDxBuxIzVej9qLPuYXGOAz47WUlSREdeA3I8XmZIybel6sSj4Tv2tuF62mKeKnmJUO5FBn85Z5Jk6at8xusUBMT+K1VC1JjBNnBdtlXunEn4jxyTE1/Yg7RSaniS6pWF5tMPejUebnoWzzVAClflEstHzHZ6laklaK0eYttT0ZI15KXtuJg+YVt9QqVNNwcU/sFIvNv/je6jOw4EeYJEvoIvOKuCJ6RMelxV07JOalA81QVpL4fYx5jLk5402I3+a4TeYWcVqcEGvMk/ZHmNgL0RgFuEBWqXraJvgRq0lICpP+bNXPg0eQpMwSr0Nxkg6LU+bz+SI+mldQXF1BdE7YsvC+LEFM7Jh4JwZH41TQJ/P2yytaiyqKE8Kkv5q3YZZmitVWbtRpellq4hlKV9JUc18Lq1u1is4USSAZsVnxyueS1beMk4h0YkNFVmtbkhT2NllgtD3DF6oonSQSvEzMN08Y88iT7DIxQS5ieTSGYb0W+6OxPMJ/7pivHkGcg+qaFI2lxYqIB7SEKiWJG007N4itYmISz62QJJbYINrmh/lyyMWFCwj7Fwy6kkgSBJHs5+KsVX9E4Zw8VPL6r6qUJIRhY8y0LcYdbyZrCtOkRYKP0LMYHT7CD240v9OIsiWhXFAlk91if9uWkuYRgCTlmRArG97Y3K1HUFaSmA+tRsuxw+bG5fYnvsxu87E4Lq6LOebPQFfNl81QBVQdfyHQiuHHY/H8c9M8UZfNPa0hilcT85gh7ptXcD1eiKjuRvNHiuBvPKs9EEuSY0hKk/l1lsyveWgSyyUmFW/9SQx/FaQ3dkzmgFXYaCXiYinpPCZbSTx8UrFU89sIbh7nbRNim7DHKrdbIfOqIkH0daEM4UOzrRn7jEKFChXKod8MMKGBtO+u9gAAAABJRU5ErkJggg==>

[image43]: <data:image/png;base64,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>

[image44]: <data:image/png;base64,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>

[image45]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAXCAYAAADUUxW8AAABE0lEQVR4XmNgGAUDB5iBOAyILwDxIyi+C8QbgdgciBkRSlEBPxAvBOIyIOZEkxMG4slA3A7ErGhyYIFOIHZBl0ACIFtLoRjFBR5AXIIuiAWAXDQHiLVhAixA3A/ESjABKOAAYjEGSDggAz8gLoBxBIF4EhDzwqUh/j8ExP+BeDoDxAIY0ATiXhhHkgESUDxwaYgrnjNANO8BYm4kOZD6ZhgHJAEKSRG4NMTvSUC8G4itkcRBwBSIW5AFqhkggUYMwFCrwgBxOsiv+AAolBczoHoRDIKAeBEQC6FLQAEooPYBsQG6BAzYA/FJIK4BYh0GSOCYAfFMIN4PxApwlTgAKF6NgbgRiGcBcRYQqzEQTkAjAgAA/P0hZPgGIPcAAAAASUVORK5CYII=>

[image46]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFIAAAAYCAYAAABp76qRAAAE7ElEQVR4Xu2YaaitUxjH/0KROTJLV5fCvSGz0CVkiLhRiuQTPojM4cvxQZIMoZQhUVKGKPNQdgghU0SGDIkQSvlg9vzO8z6d513vWvtsHfccV+df//bea613rWf91zOsd0uLWMT/Hesb1ykbV3OsbdyobPwn2NR4hPFE487GNfvdA+xuvFOTLYpxW6guOofB2muUHfMM7NhcbuMNxpX97vHA+IONrxqfMJ7S8WnjR8a9Z4b2sK3xOeOuZUeBzeRz/2X8ybhb6ltu/LbrG8k3shA4xPiL3I5njevJD/Zx4z5pXBN4ydXGTzUUjL5bjT8a9yj6EJ8TmyraW2D8PcbXjJsUfazzkBZWSIBjfGm8MrUdKXeosXaxgVuMP6itOuH9vfFm9cNumfGD7nMSIB4ikgZq4XuXFl7IA+VeeVxqI2W9ZDw5tQ1wlvHP7rOFEOA9eYgGLjE+pnq+q2FP48/GM8uODv8FIdkTToPzZOChDxjXKtqnsdT4lfF9eQFoIYT83LhV14Z4iHhZDGqAeY817mQ8VS4kgtbQEpI8dZJ8LZ6tFT/sWWE83ridcUPjucZL5bmuBeZCNGzEVsQaaWjDUfL9E/oDTMkTa84HNexg/Fp9IfnkNwbUgPGE8CPyovWgPH2UXp1RCkn4nyY/xBXG7Y3XGJ8xbtmNAdwaPjReJV+L8Z8YzzB+ofbBIeBb8ucYy/dfjTfmQR2Yg9xZ1pBpY0fysD6s3zUA/Yx7wbhB18bE38hzSokoUM9r5kq0o7wyt/IjKIU8XF7kDooB8rnvkx/Quh2fVD/suK78YTxUbm9tPQ4F8fHY6D9d7lg5PwaajhMdtXxQghNiganUhpCt0yYpI3xOzrPlR5CFjNRR82Dy2G/yQ4x98GyAzWLv+aktA8HvlXvYktTeyo8g1sHjqx05XGsg33CP/E79u2JLyBCAVEBKCGDAuPwIspDkK8Izfmew4RAKj8Q7R5oZh0dSeffvfpeIW0j2Yj5b+RGEXoPD4ZQ57XFC4vK4PkZfUPS1hIwFczVnHkK65l0ZWciwr3bnDCHDO46WX/JvM54jvw+frXpIg/DYHB3bGD9TPT+CZmiHe0eI1MC9khxFviM3ZeBtVHyqWUYseHtqi6rPZZzv18uraoksZA6/slJSHLFrWff7JuNe8urO+jWPygghs+1ogBZ4M558XuoDrf1OgzcVDMJbSqFI1BSH6+ThUyI8psx5kfyjqMCL5YbjSRhJlawhCwmwj0rPtSmAWLxq8kYVHsehEZb8NxAkDZV7CnAAhHYUFQoir4SRei7XsABTrUk1tfw5DQZ8LDcu3q95135HLmYrPCJca6HAdYTn75aLyn2Ozb5ufFheMTOWyysoYkPEi43sYnzZ+KjxDvnhXaS+SMcYf9fM80HyOp5aAtsJ/bflc3KdOsH4rvEp47UaHgK6jDSLt8ellJPE7bdWW8AMqjIHUOYwgCH5Xx7mw5smfQsqsbF8vnKDeC2HcEDRvkT+Z0PO1SUQhX954oLP3ERaeeGPNDNVtP9rQJgX5S/1CwWq6Eh1TyHfEY7j3tomwVLjK93nKgN55n7V8+h8gDRBiFIcsreSEt6Q5+dJoqsFnr1Cc59nVjA5OQuu0oXGgBsAG0XQNzuSU/fV3G3irYpCNsmf1nMGnnChcb+yYzUHd0uuWvMi4iIWMXf8DfrKC6Hai0kuAAAAAElFTkSuQmCC>
