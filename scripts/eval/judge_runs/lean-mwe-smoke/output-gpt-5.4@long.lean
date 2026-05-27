import Mathlib

#guard_msgs in
example : True := by
  fail_if_success
    exact 0
