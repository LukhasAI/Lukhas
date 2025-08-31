<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# How does SAMPL simulate human-like memory phenomena like retrieval-induced forgetting

The Spreading Activation and Memory Plasticity Model (SAMPL) simulates human-like memory phenomena, including retrieval-induced forgetting, by leveraging two key mechanisms: **spreading activation** and **non-monotonic plasticity**. These mechanisms allow SAMPL to dynamically adjust memory associations during retrieval, mirroring how human memory can enhance some items while weakening others.

---

### **How SAMPL Simulates Retrieval-Induced Forgetting**

#### 1. **Spreading Activation**

- **Mechanism**:
    - When a memory item (node) is retrieved, activation spreads across the network of associated items (nodes) through weighted edges.
    - The strength of activation diminishes as it propagates further from the retrieved item.
- **Effect**:
    - Closely related memories receive stronger activation, reinforcing their connections.
    - Distantly related or unrelated memories receive weaker activation or none at all.


#### 2. **Non-Monotonic Plasticity**

- **Mechanism**:
    - After activation, the weights of edges between nodes are updated based on their activation levels:
        - **Strongly activated nodes**: Connections are strengthened ("rich get richer").
        - **Moderately activated nodes**: Connections are weakened to reduce interference.
        - **Unactivated nodes**: Connections remain unchanged or decay naturally over time.
- **Effect**:
    - This selective reinforcement and weakening of associations leads to retrieval-induced forgetting:
        - Practiced items (e.g., RP+) are remembered better due to strengthened connections.
        - Related but unpracticed items (e.g., RP−) are remembered less well because their connections are weakened.

---

### **Validation of Retrieval-Induced Forgetting in SAMPL**

SAMPL has been validated against human memory experiments that demonstrate retrieval-induced forgetting. For example:

- In simulations, SAMPL showed that practiced items (RP+) were remembered more frequently than related but unpracticed items (RP−), replicating human results from studies like Anderson et al. (1994)[^1][^3].
- The model also demonstrated that retrieval-specificity is key: forgetting effects were more pronounced when retrieval practice was used compared to simple restudy conditions[^4].

---

### **Comparison to Human Memory**

SAMPL's ability to simulate retrieval-induced forgetting aligns with human behavior in several ways:

- **Selective Forgetting**: SAMPL weakens associations for moderately activated nodes, mimicking how humans deprioritize less relevant information during retrieval.
- **Contextual Sensitivity**: The model's spreading activation mechanism accounts for context-based memory effects, such as enhanced recall for closely related items and diminished recall for unrelated ones[^1][^3].

---

### **Implications**

The mechanisms in SAMPL not only replicate human-like memory phenomena but also have broader applications:

- **Memory Disorders**: Understanding how retrieval-induced forgetting occurs can inform treatments for conditions like PTSD, where certain memories dominate others[^1].
- **AI Systems**: Adaptive forgetting in AI systems can improve efficiency by prioritizing relevant information while discarding less useful data.

In summary, SAMPL captures the nuanced dynamics of retrieval-induced forgetting by combining spreading activation and non-monotonic plasticity, offering a computationally robust model of human-like memory behavior.

<div>⁂</div>

[^1]: https://www.biorxiv.org/content/10.1101/778563v1.full-text

[^2]: https://www.frontiersin.org/journals/cognition/articles/10.3389/fcogn.2022.1081181/full

[^3]: https://www.biorxiv.org/content/10.1101/778563v1

[^4]: https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/11/buchli_RIF.pdf

[^5]: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.00928/full

[^6]: https://pmc.ncbi.nlm.nih.gov/articles/PMC6206073/

[^7]: https://www.psychologistworld.com/memory/influential-memory-psychology-studies-experiments

[^8]: https://uwaterloo.ca/memory-attention-cognition-lab/sites/default/files/uploads/files/cdps15.pdf

[^9]: https://science.howstuffworks.com/life/inside-the-mind/human-brain/human-memory.htm

[^10]: https://www.sec-ed.co.uk/content/best-practice/do-you-know-about-retrieval-induced-forgetting/

[^11]: https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/07/Anderson_EBjork_RBjork_2000.pdf

[^12]: https://pmc.ncbi.nlm.nih.gov/articles/PMC4183265/

[^13]: https://en.wikipedia.org/wiki/Retrieval-induced_forgetting

[^14]: https://arxiv.org/html/2412.15501v1

[^15]: https://compmemweb.princeton.edu/wp/wp-content/uploads/2016/11/a-neural-network-model-of-retrieval-induced-forgetting-1.pdf

[^16]: https://3quarksdaily.com/3quarksdaily/2017/10/why-human-memory-is-not-a-bit-like-a-computers.html

[^17]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10285019/

[^18]: https://www.sciencedirect.com/science/article/abs/pii/S001002852030075X

[^19]: https://centaur.reading.ac.uk/37052/1/Murayama et al_2014_PB.pdf

[^20]: https://pmc.ncbi.nlm.nih.gov/articles/PMC3192650/

