structure InnerLearner (θ : Type*) where
  params : θ

structure MetaLearner {θ : Type*} (InnerLearner : Type*) where
  inner : InnerLearner
  metaStep : θ → θ
