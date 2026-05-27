Added a JSDoc `@typedef` block at the top of `graph_widget.html`'s script:

- **`NodeGroup`** — union of all valid `group` strings (person, company, event, document, hypothesis, Tacit Knowledge, case, asset, evidence_for, evidence_against, environmental, ai_phase), annotated against their W3C PROV-O equivalents (prov:Agent, prov:Activity, prov:Entity).
- **`NodeStatus`** — `'verified' | 'pending' | 'hypothetical'`.
- **`GraphNode`** — captures the full node shape: `id`, `label`, `group` (typed as `NodeGroup`), optional `status`, `title`, and `hidden`.