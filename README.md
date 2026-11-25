<img width="2172" height="724" alt="ChatGPT Image 21 июл  2026 г , 02_49_13" src="https://github.com/user-attachments/assets/4dec10be-31a5-4600-ba4e-f5f89036ca29" />

<div align="center">

# Said Kulmakov

### Creator and Systems Architect of Semantic

**Designing deterministic, verifier-first systems for reasoning,  
controlled execution and evidence-driven AI-agent governance.**

<br>

`Meaning before execution.`  
`Evidence before admission.`  
`Authority through explicit contracts.`

<br>

[![Semantic](https://img.shields.io/badge/Flagship-Semantic-2563eb?style=for-the-badge)](https://github.com/skulmakov-oss/Semantic)
[![Quad Logic](https://img.shields.io/badge/Logic-N%20%2F%20F%20%2F%20T%20%2F%20S-0f766e?style=for-the-badge)](https://github.com/skulmakov-oss/Semantic)
[![Verifier First](https://img.shields.io/badge/Execution-Verifier_First-7c3aed?style=for-the-badge)](https://github.com/skulmakov-oss/Semantic)

</div>

---

## Self-Hosting Milestone — 2026-11-25

Semantic development began on **2026-02-08**. **290 days later**, on **2026-11-25**, the Semantic compiler written in Semantic compiled its own source to a **byte-identical fixed point**:

```text
C0 (Rust reference compiler) ── compiles S ──▶ C1
C1 (Semantic compiler, SemCode) ── compiles S ──▶ C2 ── compiles S ──▶ C3

C1 = C2 = C3   byte-identical, 339,746 bytes
```

| Item | Value |
|---|---|
| Compiler source `S` | nine `.sm` files written in Semantic |
| Fixed point | `C1 = C2 = C3`, SHA-256 `2bfd56e1…e939` (`byte-equality-v1`) |
| Differential corpus | 140 / 140 fixtures; C1 and C2 emit SemCode byte-identical to the reference compiler for every accepted program |
| Contract | Bootstrap Contract v4: canonical source set, pinned reference and executor, bounded execution envelope |
| Admission | verifier-first: every generation is admitted by `sm-verify` before it runs |

**Scope, stated plainly:**
- **Platform:** qualified locally on Windows x64 by a single operator.
- **Subset:** the compiler covers the Bootstrap Subset of the language, not the full language.
- **Rust components:** the verifier and VM remain Rust (`sm-verify`, `sm-vm`).
- **Bootstrap Seal:** in state **validated**. It is not yet independently reproduced or accepted.

Details and evidence: [**Semantic-Language**](https://github.com/skulmakov-oss/Semantic-Language).

---

## Semantic

[**Semantic**](https://github.com/skulmakov-oss/Semantic) is a deterministic, verifier-first language platform for reasoning programs and explicit four-state logic.

It compiles human-readable `.sm` source into versioned **SemCode**, verifies the artifact at a dedicated admission boundary, and executes admitted code in a deterministic virtual machine.

```text
.sm source
   → frontend and semantic analysis
   → deterministic IR
   → SemCode (.smc)
   → verifier admission
   → deterministic VM
   → capability-controlled host boundary
```

Semantic treats uncertainty and contradiction as explicit computational states:

| State | Meaning |
|:---:|---|
| `N` | insufficient evidence / unknown |
| `F` | false |
| `T` | true |
| `S` | conflicting evidence |

> A result is not admitted because an agent claims success.  
> It is admitted only when the required evidence exists.

---

## Ecosystem

| Project | Responsibility |
|---|---|
| [**Semantic**](https://github.com/skulmakov-oss/Semantic) | Language, SemCode format, Rust reference compiler (C0), `sm-verify` verifier and deterministic VM |
| [**Semantic-Language**](https://github.com/skulmakov-oss/Semantic-Language) | The Semantic compiler written in Semantic and its bootstrap qualification (self-hosting fixed point; Seal validated) |
| [**Semantic-Dist**](https://github.com/skulmakov-oss/Semantic-Dist) | Native distribution and installer (Windows x64 Developer Preview of the Rust toolchain) |
| [**CCL**](https://github.com/skulmakov-oss/CCL) | Deterministic governance and evidence-based admission for AI-agent software engineering |
| [**Themis**](https://github.com/skulmakov-oss/Themis) | MCP contract runtime with verified state transitions and bounded capabilities |
| [**Mission Control**](https://github.com/skulmakov-oss/Mission-Control) | Live 3D observability for semantic graphs, contracts, effects, conflicts and verdicts |
| [**Prometheus**](https://github.com/skulmakov-oss/Prometheus) | Experimental Rust `no_std` operating-system foundation with deterministic event routing |
| [**Admission Guardian**](https://github.com/skulmakov-oss/Admission-Guardian) | Local validation and admission boundary under active development |
| [**Semantic TextMate Grammar**](https://github.com/skulmakov-oss/semantic-textmate-grammar) | Editor syntax support for the Semantic language |
| [**Semantic-Agent**](https://github.com/skulmakov-oss/Semantic-Agent) | Policy-bound verified execution agent for the Semantic platform |

```mermaid
flowchart TD
    H[Human intent] --> S[Semantic]
    S --> V[Verifier]
    V --> VM[Deterministic VM]

    H --> CCL[CCL]
    CCL --> E[Evidence capture]
    E --> A[Admission verdict]

    AG[AI coding agent] --> T[Themis]
    T --> S
    T --> B[Bounded host capabilities]

    S --> MC[Mission Control]
    CCL --> MC
    A --> MC

    P[Prometheus] --> R[Deterministic runtime]
    R --> S
```

---

## Engineering Principles

```text
Verifier first
Deterministic execution
Explicit uncertainty and conflict
Least authority
Evidence over testimony
Bounded effects
Canonical meaning separated from presentation
```

These principles are applied across the ecosystem:

- **Reasoning is explicit.** Unknown and contradictory evidence are not silently collapsed into Boolean values.
- **Execution is admitted.** Raw artifacts do not enter the canonical runtime path without verification.
- **Authority is bounded.** Components receive only the capabilities required for the current state.
- **Evidence is structural.** Agent confidence and natural-language reports are not treated as proof.
- **Presentation is not meaning.** Visual and UI layers project canonical state rather than becoming the source of truth.

---

## Current Focus

- Semantic language and deterministic runtime
- Compiler, verifier and virtual-machine boundaries
- Semantic UI and application architecture
- Executable contracts for AI coding agents
- Evidence-backed engineering workflows
- Semantic graph observability and deterministic replay
- `no_std` runtime and systems architecture research

My industrial engineering background keeps this work grounded in real systems: constraints, failure modes, observability, bounded operations and controlled recovery.

---

## Technical Domains

`Rust` · `no_std` · `Compiler Design` · `Virtual Machines` · `Formal Boundaries`  
`MCP` · `AI-Agent Governance` · `Evidence Systems` · `Semantic Graphs`  
`TypeScript` · `React` · `Tauri` · `Three.js` · `Systems Engineering`

---

<div align="center">

### The system may propose. The verifier decides.

[Explore Semantic](https://github.com/skulmakov-oss/Semantic) ·
[View CCL](https://github.com/skulmakov-oss/CCL) ·
[Open Mission Control](https://github.com/skulmakov-oss/Mission-Control)

</div>
