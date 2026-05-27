Let \(f_\theta\) be a model with parameters \(\theta\), task-specific support loss \(L_{\text{sup}}^{(\tau)}(\theta)\), and query loss \(L_{\text{qry}}^{(\tau)}(\theta)\) for task \(\tau\).
The inner learner performs one gradient step on the support set: \(\theta'_\tau=\theta-\alpha \nabla_\theta L_{\text{sup}}^{(\tau)}(\theta)\), where \(\alpha\) is the inner learning rate.
The outer objective evaluates the adapted parameters on query data across tasks: \(J(\theta)=\mathbb{E}_{\tau\sim p(\tau)}[L_{\text{qry}}^{(\tau)}(\theta'_\tau)]\).
The outer learner then makes a meta-step on the initialization \(\theta\): \(\theta \leftarrow \theta-\beta \nabla_\theta J(\theta)\), where \(\beta\) is the meta learning rate.
Expanding this for a minibatch of tasks \(\{\tau_i\}_{i=1}^B\), \(\theta \leftarrow \theta-\beta \frac{1}{B}\sum_i \nabla_\theta L_{\text{qry}}^{(\tau_i)}\!\left(\theta-\alpha \nabla_\theta L_{\text{sup}}^{(\tau_i)}(\theta)\right)\).
This is a two-level nested learner because the outer update depends on parameters produced by the inner update.
Keeping the second-order dependence yields MAML, while dropping Hessian terms gives the common first-order approximation.
