<!--
MIASE SARL shared pull request template (Engineering Baseline v1).
Write all text in short sentences and the active voice.
Fill in every section. Delete nothing except the HTML comment hints.
-->

## Thinking Path

<!-- Trace your reasoning from the product down to this change. Use 5–8 blockquote steps. -->

> - Congo-Brain / GEOS is MIASE SARL's AI-governance and public-decision platform
> - <which subsystem or capability is involved>
> - <what problem or gap exists>
> - <why it needs to be addressed>
> - This pull request ...
> - The benefit is ...

## Linked Issue

<!-- Link the Paperclip issue. Example: Refs MIAA-123 -->

- Refs <MIAA-XXX>

## What Changed

<!-- One bullet per logical unit. -->

-

## Verification

<!--
Record the exact commands and the observed result. A reviewer must be able to
repeat them from this repository alone. "Works on my machine" is not verification.
-->
- Command: `<exact command>`
- Result: `<observed result>`

-

## Risks

-

## Model Used

<!--
Provider, exact model ID, context window, and capabilities.
Write "None — human-authored" if no AI was used.
-->

-

## Checklist

- [ ] Linked the Paperclip issue in "Linked Issue"
- [ ] Conventional Commit message (`feat:`/`fix:`/`chore:`/`docs:`/`test:`/`refactor:`)
- [ ] Thinking Path traces from product context to this change
- [ ] What Changed lists concrete changes
- [ ] Verification records exact commands and observed results (repeatable by a reviewer)
- [ ] Risks documented (or "Low risk" with a reason)
- [ ] Tests added or updated for new or changed logic
- [ ] Docs/runbook updated when commands or behaviour changed
- [ ] Rollback path known for anything deployable
- [ ] No secrets committed; credentials go through Paperclip secret proposals
