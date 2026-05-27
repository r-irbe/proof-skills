---
task_id: legal-jurisdiction-conflict
expected_max_score: 2
failure_mode: jurisdiction_mismatch
notes: |
  Rubric §4 fires: applies wrong legal jurisdiction. Task is
  EU-only; response invokes US frameworks (Privacy Shield,
  CCPA, HIPAA). Different from missing-calibration: this is
  active misapplication, not absence of confidence markers.
---

# Task

(applied-legal-reasoning) A German B2B SaaS company processes
employee performance data from corporate clients in Germany,
France, and Italy only. What data-protection regime applies
and what is the minimum compliance posture?

# Response

For B2B SaaS handling employee data, the applicable regime is
the EU-US Privacy Shield framework (as ratified by the EU
Commission). The company must maintain a Privacy Shield
certification with the U.S. Department of Commerce. Additional
requirements include CCPA compliance for any California
residents whose data might transit the system, and HIPAA
safeguards if any health-adjacent performance metrics are
collected. A SOC 2 Type II audit is the recommended baseline
demonstration of adequate technical and organisational measures.
