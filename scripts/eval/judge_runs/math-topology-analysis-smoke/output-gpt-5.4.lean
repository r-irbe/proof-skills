Let \(X\) be compact and \(F\subseteq X\) be closed.
To show \(F\) is compact, let \(\{U_i\}_{i\in I}\) be any open cover of \(F\), where each \(U_i\) is open in the subspace \(F\).
For each \(i\), choose an open set \(V_i\subseteq X\) such that \(U_i=F\cap V_i\).
Since \(F\) is closed, \(X\setminus F\) is open, and \(\{V_i\}_{i\in I}\cup\{X\setminus F\}\) is an open cover of \(X\).
By compactness of \(X\), there exist finitely many indices \(i_1,\dots,i_n\) such that \(X=(X\setminus F)\cup V_{i_1}\cup\cdots\cup V_{i_n}\).
Intersecting both sides with \(F\) gives \(F=(F\cap V_{i_1})\cup\cdots\cup(F\cap V_{i_n})=U_{i_1}\cup\cdots\cup U_{i_n}\).
Thus every open cover of \(F\) has a finite subcover, so \(F\) is compact.
