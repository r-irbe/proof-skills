Synced. The codebase has **2,859 theorems+lemmas** (`grep -c "^theorem\|^lemma" EASCI/**/*.lean`) across 176 `.lean` files / 77,328 LOC / 1,019 defs / 147 instances / 308 `@[simp]`. Replaced stale `≥1,255`, `≥1,888`, `≥1,903`, `≥1,947`, `≥2,850` with **`≥2,859`** in:

- `appendix-a.tex` — STALE banner, Curry–Howard remark, per-module summary table (added 14 newer modules; totals to **2,859**).
- `appendix-b.tex` — STALE banner (defs 630→**1,019**, instances 87→**147**, structures→**189**).
- `appendix-c.tex` — 7 occurrences (proof-length distribution, Erdős/De Millo remarks, gap-closure tables).
- `appendix-d-philosophical.tex` — 8 occurrences (Newell-Simon, Popper, Curry-Howard, Hilbert remarks).
- `appendix-e.tex` — STALE banner; Table 1 census; density table; both rebuilt with directory-recursive per-module counts (top-level file + subdir).
- `chapter2-methodology.tex` — 2 McCarthy/Martin-Löf remarks.

Fixed an in-progress edit that had zeroed per-module rows in `appendix-e.tex` (it had counted only top-level facade files, missing content in `EASCI/CCVGating/`, `CuspCatastrophe/`, etc.). Verified `pdflatex easci-report-full` compiles green.