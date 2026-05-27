theorem t3 {α : Type _} (l : List α) : l.reverse.reverse = l :=  by simp [List.reverse_reverse]
