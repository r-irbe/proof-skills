Let E be a set of evidence propositions and H a hypothesis. One inference step is a defeasible modus ponens:

  Premises: E₁, E₂, …, Eₙ   (observed facts, each with confidence cᵢ ∈ [0,1])
  Warrant:  ∀x. E₁(x) ∧ … ∧ Eₙ(x) → H(x)   unless defeated by D(x)
  Conclusion: H with strength s = ∏ cᵢ · (1 − P(D | E))

The step is valid iff: (1) all Eᵢ are grounded (traceable to an observation), (2) the warrant is domain-authorised, and (3) no active defeater D is consistent with the evidence set. Formally encode it as a tuple ⟨E, W, D, H, s⟩ where W is the warrant schema, D the defeater guard, and s the propagated confidence. Chaining appends this tuple to the proof trace; the next step may use H as a new Eᵢ only if s exceeds a context-defined threshold θ.