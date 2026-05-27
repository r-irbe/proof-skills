Let \(A \in \mathbb{R}^{m \times n}\) be the payoff matrix for the row player, where the column player receives \(-A\).
If the row player uses mixed strategy \(x \in \Delta_m\) and the column player uses mixed strategy \(y \in \Delta_n\), the expected payoff is \(x^\top A y\), where \(\Delta_k=\{p\ge 0,\ \mathbf{1}^\top p=1\}\).
The row player solves \(\max_{x\in\Delta_m}\min_{y\in\Delta_n} x^\top A y\), while the column player solves \(\min_{y\in\Delta_n}\max_{x\in\Delta_m} x^\top A y\).
The game value is \(v=\max_{x\in\Delta_m}\min_{y\in\Delta_n} x^\top A y=\min_{y\in\Delta_n}\max_{x\in\Delta_m} x^\top A y\) by the minimax theorem.
Equivalently, the row player can compute \(x\) from the LP \(\max_{x,v} v\) subject to \(A^\top x \ge v\mathbf{1},\ x\ge 0,\ \mathbf{1}^\top x=1\).
The column player can compute \(y\) from the dual LP \(\min_{y,w} w\) subject to \(Ay \le w\mathbf{1},\ y\ge 0,\ \mathbf{1}^\top y=1\).
An optimal pair \((x^*,y^*)\) is a Nash equilibrium, and \(v=x^{*\top}Ay^*\) is the guaranteed payoff to the row player.
