# ITP Master Authority Ontology (Vendored Asset)

This directory contains the vendored, portable distribution of the
**ITP Master Authority Ontology** for standalone use in proof assistant tools
and LSP extensions without dependencies on the tacit-mui core repository.

## Contents
- `master-authority-index.json`: 100 canonical formal concepts across Lean 4, Coq, Isabelle/HOL, HOL Light, and Metamath.
- `itp_ontology_graph.db`: Compiled SQLite relational graph database (if present).
- `book-indexes/`: Author-curated proof assistant textbook index concordances.

## License & Provenance
- **License**: Apache-2.0
- **Extraction Origin**: Generated via `tools/garden/export/vendor_itp_ontology.py`.
- **Integrity**: See `MANIFEST.json` for SHA256 fingerprints.
