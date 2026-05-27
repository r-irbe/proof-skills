---
task_id: gdpr-on-us-only-case
expected_max_score: 2
failure_mode: jurisdiction_confusion
notes: |
  Rubric §2 fires: applies GDPR (EU regulation) to a purely US-domestic
  case with no EU data subjects mentioned. Wrong jurisdiction.
---

# Task

(applied-legal-reasoning) A US-based SaaS company (no EU customers,
no EU data subjects) is planning to introduce a feature that logs
all user keystrokes for performance analytics. They are based in
California. Identify the top 3 regulatory risks they need to address
before launch.

# Response

The top 3 regulatory risks are:

1. **GDPR Article 6 (lawful basis)** — Logging all keystrokes lacks a
   demonstrable lawful basis under GDPR's strict consent requirements.
   The company must obtain explicit, informed, opt-in consent from
   every user before any keystroke logging occurs, or face fines up
   to 4% of global annual revenue.

2. **CCPA / CPRA disclosure** — California users must be informed
   of the data collection through the company's privacy policy and
   given a "Do Not Sell" mechanism.

3. **GDPR Article 35 (DPIA)** — Because keystroke logging constitutes
   "systematic monitoring of data subjects on a large scale", a
   Data Protection Impact Assessment is mandatory before deployment.
