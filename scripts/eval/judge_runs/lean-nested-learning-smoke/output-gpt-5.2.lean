structure MetaLearner {θ : Type} (InnerLearner : Type → Type) where
  inner : InnerLearner θ
  metaStep : θ → θ
