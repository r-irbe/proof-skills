structure BridgeContract where
  source : String
  target : String
  exported : List String
  validator : Unit → Bool
