# applied-domain cluster known-bad corpus

Calibration corpus for the `applied-domain-quality` rubric. Covers
both the applied-* and ai-* skill clusters:

**applied-***
- applied-data-information-security
- applied-engineering-disciplines
- applied-intelligence-analysis
- applied-legal-reasoning
- applied-strategy-analysis

**ai-***
- ai-agentic-evolving
- ai-commonsense-reasoning
- ai-high-stakes-verifiable
- ai-causal-deontic
- ai-symbolic-neuro

## Failure modes covered

| Transcript | Rubric clause | Expected aggregate |
|---|---|---|
| `fabricated-cve` | §1 fabricated_regulation | 1 |
| `gdpr-on-us-only-case` | §2 jurisdiction_confusion | 2 |
| `missing-calibration` | §3 uncalibrated_confidence | 3 (boundary case) |
| `single-option-no-tradeoff` | §2 missing_tradeoff_analysis | 2 |
| `empty-applied` | §1 empty_response | 1 |
