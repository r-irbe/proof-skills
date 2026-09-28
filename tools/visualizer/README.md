# Standalone Lean 4 Formalization DAG Visualizer

> Pure client-side, zero-dependency interactive visualizer and Tufte proof-walk engine for Lean 4 formal mathematical developments.
> Strict 7-bit ASCII only (INV-001).

---

## 1. Overview & Architectural Independence

This visualizer is an entirely standalone, client-side web application. It is **not** deployed to or dependent upon the AI investigator, and requires:
* Zero build steps (no webpack, no vite, no esbuild)
* Zero npm or node dependencies
* Zero external CDNs or network connections (works completely offline in air-gapped environments)
* Zero server-side rendering or database backends

The application renders interactive directed acyclic graphs (DAGs) of Lean 4 theorems, definitions, and axioms directly using native browser SVG and ES6+. It pairs every declaration with a Tufte-style pedagogical proof card showing:
1. Formal signature and Lean module coordinates
2. Pedagogical mathematical intuition and human-readable narrative
3. Step-by-step proof strategy milestones
4. Interactive premise and dependent relationship tags

---

## 2. How to View and Run

### Method A: Direct File URL (Instant, Offline)

Open `index.html` directly in any standard browser:

```text
file:///path/to/proof-skills/tools/visualizer/index.html
```

Or on Linux / macOS:
```bash
xdg-open index.html    # Linux
open index.html        # macOS
```

### Method B: Standalone Python Launcher (`serve.py`)

Run the included zero-dependency Python launcher:

```bash
python3 serve.py
```

This launches a local HTTP server on `http://127.0.0.1:8088/` and automatically opens your default browser.

#### Launcher Options:
* `--port <int>`: Custom port (default: 8088; auto-increments if port is busy).
* `--corpus <nse|flt|easci>`: Launch directly with a specific preloaded corpus.
* `--graph <path.json>`: Automatically serve and display a custom formalization graph JSON.
* `--no-browser`: Run headlessly without launching the browser window (useful for SSH port-forwarding).

Example:
```bash
python3 serve.py --corpus flt --port 8090
```

---

## 3. Preloaded Benchmark Corpora

The visualizer includes pre-packaged mathematical DAGs:

1. **Navier-Stokes & Euler (3D Blowup)**:
   * Piola-transformed curl algebra (`matrixAntisym_congruence`)
   * Solenoidal gauge invariance (`divergence_piola_curl`)
   * Multiscale wave-packet cascade (`pairLp_ae`)
   * Beale-Kato-Majda blowup contradiction (`vorticity_lintegral_eq_top`)
2. **Fermat's Last Theorem (Modularity Approach)**:
   * Frey elliptic curve construction
   * Mazur irreducibility theorem
   * Ribet level-lowering epsilon conjecture
   * Taylor-Wiles deformation ring isomorphism ($R = \mathbb{T}$)
3. **EASCI Formalization**:
   * Simplex invariant preservation
   * Stochastic CCV contraction mapping

---

## 4. Visualizing Custom Lean 4 Formalizations

To visualize your own Lean 4 codebase:

1. Export the graph using the `proof-skills` formalization breakdown tool:
   ```bash
   python3 ../../scripts/lean/formalization_breakdown.py \
       --json-graph my_project_dag.json \
       /path/to/lean/project
   ```

2. Load the JSON into the visualizer via any of the following:
   * **CLI flag**: `python3 serve.py --graph my_project_dag.json`
   * **In the UI**: Click **"Load JSON..."**, select the file or paste the JSON text, and click **"Load Graph"**.

### JSON Schema Format

```json
{
  "nodes": [
    {
      "id": "thm:my_theorem",
      "label": "MyModule.my_theorem",
      "kind": "theorem",
      "module": "MyModule",
      "line": 42,
      "statement": "theorem my_theorem (x : Nat) : x + 0 = x",
      "docstring": "Pedagogical narrative explaining mathematical intuition.",
      "milestones": ["Line 43: intros", "Line 44: rfl"],
      "uses": ["thm:prior_lemma"]
    }
  ],
  "edges": [
    { "source": "thm:prior_lemma", "target": "thm:my_theorem" }
  ]
}
```

---

## 5. Interface & Interaction Guide

* **Pan Canvas**: Click and drag any empty area of the canvas.
* **Zoom**: Use the mouse scroll wheel or click the `+` / `-` / `Fit` buttons.
* **Declaration Inspection**: Click any node circle or label to display its full Tufte proof card in the right sidebar.
* **Dependency Navigation**: In the Tufte card, click any premise or dependent tag to navigate directly to that declaration and center it in the viewport.
* **Layout Direction**: Toggle between **Left to Right (LR)** and **Top to Bottom (TB)** using the layout dropdown.
* **Search / Filter**: Type in the search box to highlight matching declarations and dim unrelated nodes.
* **Vector Export**: Click **"Export SVG"** to download an publication-grade SVG vector graphic of the current layout.
