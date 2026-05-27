CIA Classification:

Confidentiality: HIGH. Salary data is sensitive personal financial information. Unauthorized disclosure causes reputational harm, workplace conflict, discrimination claims, and competitive disadvantage. Access must be restricted to HR, payroll systems, the data subject, and authorized managers on a strict need-to-know basis. Encryption at rest and in transit is mandatory. Column-level or row-level security should enforce access control in the database layer itself.

Integrity: HIGH. Incorrect salary values directly cause financial harm to individuals and the organization. Overpayments trigger legal liability; underpayments violate employment contracts and labor law. Changes must be audit-logged with before/after values, actor identity, and timestamp. Dual-control or approval workflows should govern updates. Database constraints and application-layer validation must prevent nulls, negative values, and implausible outliers.

Availability: MEDIUM. Payroll processing runs on defined cycles, typically monthly or bi-weekly, so real-time access is not required continuously. Brief outages outside payroll windows are tolerable. However, availability must be guaranteed during payroll runs; failure at that window causes regulatory non-compliance and contractual breach. Backup and recovery procedures should target an RPO aligned to the payroll cycle frequency.

GDPR Classification:

Legal Basis: Salary data is processed under Article 6(1)(b) — necessary for the performance of an employment contract — and Article 6(1)(c) — necessary for compliance with legal obligations such as tax reporting and social security contributions. Some processing may also rely on 6(1)(f) legitimate interest for internal compensation benchmarking, but this requires a documented balancing test.

Special Category Status: Salary itself is not a special category under Article 9. However, salary data can indirectly reveal trade union membership (e.g., union dues deductions), disability accommodations reflected in adjusted pay, or maternity/paternity pay status. Any salary field that encodes or can be used to infer special category data elevates the risk profile and may trigger Article 9 protections, requiring explicit consent or another Article 9(2) basis.

Data Subject Rights Implications: Data subjects have a right of access under Article 15, meaning they can request their own salary record. They have a right to rectification under Article 16 if values are inaccurate. The right to erasure under Article 17 is limited here because retention is mandated by tax and labor law, typically six to seven years in most EU jurisdictions, making erasure requests largely overridable under Article 17(3)(b). The right to restriction under Article 18 applies during dispute resolution. Portability under Article 20 applies because salary is provided by the data subject and processed by automated means under contract.

Data Minimisation: Article 5(1)(c) requires collecting only what is necessary. The column should store the agreed compensation figure. Supplementary fields like bonus history, equity grants, or allowances should each be justified separately. Historical salary records beyond the legally mandated retention window must be deleted.

Purpose Limitation: Article 5(1)(b) prohibits using salary data for purposes incompatible with the original collection purpose. Using salary columns for profiling, marketing, or sharing with third parties outside payroll, tax, and benefits providers requires a separate legal basis and likely a new privacy notice.

Retention: Article 5(1)(e) requires storage limitation. Define a documented retention schedule. Tax obligations in most EU states require payroll records for at least five years. After the retention period, records must be securely deleted or anonymized.

Data Protection by Design: Article 25 requires pseudonymization or encryption where possible. Salary columns should be encrypted at rest using a key managed separately from the database. Access logs must be maintained. The column should not appear in general-purpose reporting views or developer environments without masking.

DPIA Requirement: Article 35 requires a Data Protection Impact Assessment when processing is likely to result in high risk. Salary data at scale, combined with other HR attributes, constitutes large-scale processing of personal data that can be used for profiling. A DPIA is strongly recommended and likely mandatory if salary is joined with performance scores, demographics, or behavioral data.

International Transfers: If the database or its replicas are hosted outside the EEA, Chapter V transfer mechanisms apply. Standard Contractual Clauses, adequacy decisions, or Binding Corporate Rules must be in place before salary data leaves the EEA. Cloud hosting contracts must specify data residency.

Summary mapping: Confidentiality HIGH, Integrity HIGH, Availability MEDIUM; GDPR Article 6(1)(b)/(c) basis, non-special-category but special-category-adjacent risk, subject to access/rectification/portability rights, restricted erasure, mandatory retention schedule, encryption and access control required by design, DPIA recommended.
