# Guardrails: Rules of Maintenance

## 1. Philosophy of Guardrails

*For full citations, refer to the [`bibliography.md`](bibliography.md).*

The guardrails defined in this repository (`GUARDRAILS.md`) are not theoretical best practices; they are a taxonomy of *measured agent failure classes*. This empirical approach ensures that our safety and operational constraints are grounded in reality.

*   *Reference*: Amodei et al. (2016)
*   *Application*: We only introduce guardrails when a specific behavior causes a debugging cycle or review failure.

## 2. Maintenance Rules

To ensure the integrity of the guardrail system, all contributors (human and agent) must adhere to these invariants:

1.  **Empirical Origin**: Every entry must be bound to a measured failure. No speculative or stylistic rules are permitted.
2.  **Stable IDs**: Entry IDs (e.g., `GT-01`) are permanently stable. Never renumber them. If a rule becomes obsolete, mark it as *retired* with a justification, but do not delete the ID.
3.  **Skill Authority**: The `SKILL.md` file that owns the failure mode is the ultimate authority on the remedy. The central `GUARDRAILS.md` file condenses this information for token-efficiency but does not override the specific skill document.

## 3. Barrier Proportionality and Escalation

Hard stops (terminal NO-GO, frozen clamps) are reserved exclusively for actions that pose security risks, corrupt history, or incur economic costs (as defined in `AGENT.md`). Everywhere else, the design must fail-open with compensating controls, allowing the agent to proceed provisionally within a quarantined scope.

*   *Reference*: Constitutional AI principles regarding bounded escalation (Bai et al., 2022)
