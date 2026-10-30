## Thinking Path

<!-- Trace reasoning from project context to this change. Link the Paperclip issue (e.g. MIAA-123). -->

- Issue:
- Context / why this change:

## What Changed

<!-- Concrete bullet list of changes. One concern per PR; keep PRs small (< 400 lines). -->

-

## Verification

<!-- A reviewer must be able to reproduce this from the repo alone. Record the exact command and observed result. "Works on my machine" is not verification. -->

- Command(s):
- Result:

## Risks

<!-- What could go wrong. Name the rollback/revert path for anything deployable (previous tag/image or `git revert`). -->

- Rollback:

## Model Used

<!-- The AI model that produced or assisted with the change (provider, exact model ID). Write "None — human-authored" if no AI was used. -->

-

## Checklist

- [ ] Lint passes (`ruff` / `eslint` per repo toolchain)
- [ ] Typecheck passes (`mypy` / `tsc` per repo toolchain)
- [ ] Unit/API tests pass; new or changed logic ships with tests in the same PR
- [ ] Contracts synchronized across layers (db/shared/server/ui or py/ts equivalents) if interfaces changed
- [ ] Docs/runbooks updated if commands or behavior changed
- [ ] Conventional Commits title (`feat:` / `fix:` / `chore:` / `docs:` / `test:` / `refactor:`)
- [ ] Paperclip-authored commits end with `Co-Authored-By: Paperclip <noreply@paperclip.ing>`
- [ ] CTO review requested for API/schema, auth/security, DB migrations, or CI/release paths (see `CODEOWNERS`)
