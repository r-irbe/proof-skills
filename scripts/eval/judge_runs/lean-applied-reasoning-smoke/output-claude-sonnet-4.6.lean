structure Evidence where
  content : String
  deriving Repr

structure Hypothesis where
  claim : String
  deriving Repr

structure EvidenceWeight where
  value : Float
  deriving Repr

structure InfRule where
  premises   : List Evidence
  conclusion : Hypothesis
  weight     : EvidenceWeight
