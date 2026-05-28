universe u v

structure MetaLearner (InnerLearner : Type u → Type v) {θ : Type u} where
  inner : InnerLearner θ
  metaStep : θ → θ
