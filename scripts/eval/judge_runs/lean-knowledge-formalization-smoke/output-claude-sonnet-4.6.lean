inductive NodeType where
  | entity : NodeType
  | concept : NodeType
  | event : NodeType
  | attribute : NodeType
  deriving Repr, BEq

inductive Value where
  | str : String → Value
  | num : Float → Value
  | bool : Bool → Value
  | nat : Nat → Value
  deriving Repr, BEq

structure KGNode where
  id    : Nat
  kind  : NodeType
  props : List (String × Value)
  deriving Repr
