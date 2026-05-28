universe u v w

structure InfRule (Evidence : Type u) (Hypothesis : Type v) (EvidenceWeight : Type w) where
  premises : List Evidence
  conclusion : Hypothesis
  weight : EvidenceWeight
