structure MetaLearner {θ : Type _} (InnerLearner : Type _ → Type _) where
  inner : InnerLearner θ
  metaStep : θ → θ
