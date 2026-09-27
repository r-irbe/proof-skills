# Template_LeanBlueprintChapter.md -- Lean Blueprint Chapter & Pedagogical Section

> **Status:** Production template for Lean Blueprint LaTeX chapters and pedagogical math sections.
> Compatible with Patrick Massot's `leanblueprint` toolchain and PlasTeX web renderers.

---

## 1. When to Use

- Writing interactive blueprint chapters connecting formal Lean definitions and theorems to human-readable mathematical descriptions.
- Embedding informal proof sketches with dependency tracking (`\uses{...}`) and verification status (`\leanok`).

---

## 2. Template Structure

````latex
% Chapter: <Chapter Title>
% Lean Blueprint Chapter Template
% Compatible with leanblueprint and plasTeX

\chapter{<Chapter Title>}
\label{chap:<chapter_label>}

\section{Overview and Core Intuition}

<High-level intuitive description of the mathematical content of this chapter.
Explain the main question, the central geometric or algebraic obstruction,
and the key strategy of the formal proof.>

\section{Definitions and Fundamental Concepts}

\begin{definition}[<Concept Name>]
\label{def:<concept_label>}
\lean{<Namespace.concept_name>}
\leanok
Let $X$ be a space and let $u \colon X \to \mathbb{R}^3$ be a smooth vector field.
We define the \emph{<concept name>} as:
\[
  \mathcal{T}(u) = \dots
\]
\end{definition}

\begin{remark}
<Pedagogical intuition explaining why this definition is structured this way in Lean,
noting any scaled-integer or finite-dimensional design decisions.>
\end{remark}

\section{Core Lemmas and Auxiliary Estimates}

\begin{lemma}[<Lemma Name>]
\label{lem:<lemma_label>}
\uses{def:<concept_label>}
\lean{<Namespace.lemma_name>}
\leanok
Under the assumptions of Definition~\ref{def:<concept_label>}, we have:
\[
  \|\mathcal{T}(u)\|_{L^\infty} \le C (1 + \|u\|_{H^1}).
\]
\end{lemma}

\begin{proof}
\uses{def:<concept_label>}
\leanok
<Informal, human-readable proof sketch explaining the mathematical argument,
highlighting the key inequality, integration by parts, or algebraic cancellation.>
\end{proof}

\section{Main Theorem}

\begin{theorem}[<Main Theorem Name>]
\label{thm:<theorem_label>}
\uses{def:<concept_label>, lem:<lemma_label>}
\lean{<Namespace.main_theorem>}
\leanok
Let $u_0$ be initial data satisfying Definition~\ref{def:<concept_label>}.
Then the maximal lifespan $T^*$ is finite, and:
\[
  \lim_{t \to T^*} \|u(\cdot, t)\|_{C^1} = \infty.
\]
\end{theorem}

\begin{proof}
\uses{lem:<lemma_label>}
\leanok
<Three-stage narrative walkthrough of the theorem's proof,
breaking down the argument into clearly articulated conceptual milestones.>
\end{proof}
````
