1. **Formalise the public API surface (types + contracts)** — Highest priority. Impact: high (unlocks safe refactors, tooling, downstream consumers); Confidence: high (well-understood techniques: TypeScript types, OpenAPI, JSON Schema); Effort: medium. Best ROI.

2. **Formalise invariants in the core domain model** — Second. Impact: high (prevents whole classes of bugs at the hot center of the system); Confidence: medium (requires domain judgment on which invariants matter); Effort: medium-high. Do after the API is pinned so invariants are expressed against stable types.

3. **Formalise edge-case behaviour via property-based / spec tests** — Third. Impact: medium-high (catches regressions, documents intent); Confidence: medium (value depends on chosen properties); Effort: medium but ongoing. Deferred because it compounds on the prior two — properties are cheap to write once types and invariants are explicit.

Sequence rationale: each task de-risks and reduces the effort of the next.