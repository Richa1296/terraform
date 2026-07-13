# Simple PR Review System

Replaces the previous 9-workflow setup with **one team-lead-style review**.

## Start here

- **[TEAM_LEAD_REVIEW.md](docs/TEAM_LEAD_REVIEW.md)** — what we check and how to read the comment

## Active components

| File | Role |
|------|------|
| `../.github/workflows/pr-review.yml` | Single GitHub Action |
| `scripts/run_pr_review.py` | Check logic + summary |
| `docs/TEAM_LEAD_REVIEW.md` | Human-readable rules |

## Archived / disabled

- Old workflows remain in `../.github/workflows/` but only run manually (`workflow_dispatch`)
- Long docs (`INTERACTIVE_DEMO.md`, etc.) are still in `docs/` for reference

## Customize

Edit `run_pr_review.py` to change what blocks merge vs. warns only.
