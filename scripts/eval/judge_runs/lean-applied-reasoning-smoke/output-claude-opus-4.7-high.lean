Evidence: HTTP 502 errors began at 14:03 UTC on service A; deploy logs show service B (an upstream dependency) was redeployed at 14:02 UTC; service A's error rate correlates 1:1 with requests routed through service B; rolling back B's deploy at 14:25 UTC restored service A's success rate to baseline within 60 seconds.

Inference rule: If an anomaly in X begins immediately after a change to Y, is confined to the code path traversing Y, and resolves upon reverting Y, then Y's change is the proximate cause of the anomaly in X (abductive inference under temporal precedence + dependency locality + reversibility).

Conclusion: Service B's 14:02 redeploy is the proximate cause of service A's 502 errors.

Caveats: Conclusion holds only if no confounding change occurred in the same window (verified: no other deploys, config changes, or traffic shifts logged between 14:00–14:25 UTC) and if the rollback isolated B's deploy artifact alone (verified: rollback touched only B's image tag).