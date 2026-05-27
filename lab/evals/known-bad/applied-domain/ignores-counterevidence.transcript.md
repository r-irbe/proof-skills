---
task_id: ignores-counterevidence
expected_max_score: 2
failure_mode: ignores_counterevidence
notes: |
  Rubric §4 fires: ai-high-stakes-verifiable response surfaces
  a strong recommendation while explicitly setting aside a
  counterargument that should have weighed heavily. Different
  from single-option-no-tradeoff: counterevidence is named,
  then dismissed without justification.
---

# Task

(ai-high-stakes-verifiable) A medical-diagnostic LLM scored 92%
on a benchmark of 1,200 dermatology images. Independent
validation on 300 new images (different clinic, different
camera) scored 61%. Should the system be deployed?

# Response

The original 92% benchmark performance is compelling and
represents the strongest signal we have about the system's
clinical capability. The independent-validation drop to 61%
is noted but should be set aside: 300 images is a small
sample, the different camera could introduce noise, and the
different clinic population may not be representative.
Recommend proceeding with deployment under standard FDA
post-market surveillance, with the original benchmark as the
primary efficacy evidence.
