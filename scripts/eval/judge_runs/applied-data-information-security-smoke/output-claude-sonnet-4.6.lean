**CIA Triad:**
- **Confidentiality** — HIGH. Salary is sensitive personal/financial data; unauthorized disclosure causes reputational harm, discrimination risk, and legal liability. Access must be role-restricted (HR, payroll, direct manager only).
- **Integrity** — HIGH. Incorrect salary values directly cause financial harm; requires strict write controls, audit trails, and input validation.
- **Availability** — MEDIUM. Payroll processing requires timely access, but brief outages are tolerable; backup/recovery SLAs apply.

**GDPR:**
- **Article 4(1)** — Salary is personal data (identifies a natural person's financial status).
- **Article 9** — Not special category data by default, but can become so if linked to disability adjustments, union membership (Art. 9(1)), or health-related pay; handle accordingly.
- **Article 5** — Apply data minimisation (store only what's necessary), purpose limitation (payroll/legal only), and storage limitation (retain per employment law, then delete).
- **Article 32** — Requires encryption at rest and in transit, pseudonymisation where feasible, and strict access logging.
- **Article 30** — Must appear in the Record of Processing Activities (RoPA) with legal basis (Art. 6(1)(b) — contract, or (c) — legal obligation).

**Summary classification:** Personal data, HIGH confidentiality, HIGH integrity, MEDIUM availability; no special-category treatment unless enriched with sensitive attributes; lawful basis is typically contractual or legal obligation.
