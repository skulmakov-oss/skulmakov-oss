# Independent accounting and diff review
Base: 188dec7eddfafaab5926af2d30f528bfe3d89a2c
Fresh-context reviewers: p3_accounting_review, p3_patch_review. Same-model independent review; owner selected no external-model opinion.
Accounting evidence checked against current source:
- semcode_vm.rs:2354 single Steps charge precedes semantic dispatch.
- direct call push at3275, closure push at3320, then continue; recursive calls use these routes.
- push_frame_in:3634 sole Calls charge, after target/signature/frame/stack/register validation, nonempty stack only.
- root wrappers initialize empty stack and zero counters; builtins inline spend Steps but no non-root Calls.
- checked_add fails closed, rejected increments are not stored.
Result: no counterexample found to stored charged Calls <= charged Steps on supported trusted SemCode paths. Count proof does not bound heap/time.
Compatibility ruling: Calls<=effectiveSteps is imposed only on explicit override, not omitted default16384 with smaller Steps.
Full five-file production/test/spec diff statically reviewed after implementation: no findings. Same effective config for admission, execution, metrics unchanged; profile-only capability selection unchanged. Public API snapshot generation and execution gates pending at time of that review.
Tests are separate execution evidence, not inferred from static review.
