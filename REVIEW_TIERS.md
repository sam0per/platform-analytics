# Review tiers

Review effort follows risk. The strictest tier a pull request touches wins.

| Tier | What changes | Reviewers |
| --- | --- | --- |
| Docs | Markdown only | None. Claude approves. |
| Table | A new or changed table, script or test | One person who is not the author |
| Dashboard metric | A model a dashboard reads, or a file that decides what passes | Two people who are not the author |

- The events dashboard reads `daily_events`. The customer dashboard reads `customer_activity`.
- "Decides what passes" means the CI comparison, `demo_numbers.toml`, `.github/`, `.claude/`, `CLAUDE.md` and `ANALYSIS_PLAN.md`.
- `.claude/approvals.yml` holds the same tiers for Claude Approvals. It names no person, only counts.
