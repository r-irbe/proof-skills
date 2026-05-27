Evidence: the access logs show 27 failed login attempts for the same account from one IP within 4 minutes, followed immediately by a successful login from that IP.
Formalisation: let F(x,t) mean "failed login for account x at time t," and S(x,t) mean "successful login for account x at time t."
If ∃t1…tn within a short interval such that n is unusually high for F(account,t), and then ∃t* immediately after with S(account,t*), infer H1: "the password was likely obtained by guessing or credential stuffing."
This is an abductive step, not a deductive proof, because other explanations remain possible.
So the reasoning chain is: abnormal burst of failures + immediate success from same source → increased likelihood of compromise attempt succeeding.
Operational conclusion: flag the session for investigation, preserve logs, and correlate with MFA events, prior IP history, and user-reported activity.
