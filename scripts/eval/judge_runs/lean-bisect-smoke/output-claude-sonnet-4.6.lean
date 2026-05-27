Use `lake +leanprover/lean4:nightly-YYYY-MM-DD` to test a specific nightly against your file. Run `git bisect` on the list of nightly dates by writing a bisect script that invokes `lake env lean Test.lean` (or whatever your file is) and exits 0 for good, 1 for bad. The nightly toolchain dates are listed at https://github.com/leanprover/lean4-nightly/releases. Concretely:

```
# build a sorted list of nightly tags, then:
git bisect start
git bisect bad <newest-bad-date>
git bisect good <last-known-good-date>
git bisect run bash -c 'elan run leanprover/lean4:nightly-$(cat TOOLCHAIN_DATE) lean Test.lean; [ $? -eq 0 ]'
```

If not using a git repo for dates, write a shell loop over an array of `nightly-YYYY-MM-DD` strings, call `elan toolchain install leanprover/lean4:nightly-$date && elan run leanprover/lean4:nightly-$date lean Test.lean`, and binary-search manually by halving the range on each failure/success. The `elan` version manager handles toolchain switching; pin the exact nightly in `lean-toolchain` for reproducibility. Once found, compare that nightly's changelog at `github.com/leanprover/lean4/compare/nightly-PREV...nightly-BAD`.