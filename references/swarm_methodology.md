# Stanford ACE Prover Swarm Methodology

To prevent context collapse, persona drift, and proof degradation in long-running Lean 4 sessions, the formalization lifecycle is divided into four distinct roles: Specifier, Prover, Auditor, Gardener.

Agents transition sequentially and never mix generative proving with long-term memory curation within the same turn.
