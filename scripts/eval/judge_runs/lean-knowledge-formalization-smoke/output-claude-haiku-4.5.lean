inductive NodeType : Type where
  | entity : NodeType
  | relation : NodeType
  | attribute : NodeType

inductive Value : Type where
  | string : String → Value
  | nat : Nat → Value
  | bool : Bool → Value
  | float : Float → Value

structure KGNode : Type where
  id : Nat
  kind : NodeType
  props : List (String × Value)
