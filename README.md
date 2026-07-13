# Terraform + Simple PR Review

Terraform infrastructure code with **automated PR review** — team-lead style.

---

## PR Review (simple)

Every PR gets **one check** that mirrors what a team lead checks first:

| Check | What it does |
|-------|--------------|
| 🔐 **Security** | Detects hardcoded passwords, API keys, private keys |
| 🐛 **Bugs** | Catches Python syntax errors |
| 🏗️ **Infrastructure** | Validates Terraform formatting & logic |
| 📦 **Dependencies** | Finds known CVEs in `requirements.txt` |
| 📐 **Standards** | Light style notes (suggestions only) |

**Blocks merge only for:**
- Secrets/credentials found
- Python syntax errors
- Terraform validation failures

**Blocks merge for:**
- High-severity security issues (Bandit)

Everything else is a warning or suggestion.

---

## In GitHub

**Checks tab:** Single status
```
✅ Team Lead Review (passed in 2m 30s)
```

**PR comment:** Clean table
```
## PR Review Summary

| What we check | Status | Notes |
|---------------|--------|-------|
| 🔐 Security | ✅ | No secrets detected |
| 🐛 Bugs | ✅ | No syntax errors |
| 🏗️ Infrastructure | ✅ | Validated |
| 📦 Dependencies | ✅ | OK |
| 📐 Standards | ⚠️ | 2 style notes |

### Must fix (blocks merge)
(if any)

### Should fix
(if any)

### Suggestions
(if any)
```

---

## For developers

1. **Create PR** as usual
2. **Wait** for "Team Lead Review" check (~2–5 min)
3. **Read** the PR comment
4. **Fix** "Must fix" items if any
5. **Push** again — comment updates automatically
6. **Request human review** when ready

---

## Repository structure

```
.
├── README.md                           ← You are here
├── terraform/                          ← Infrastructure code
├── .github/
│   └── workflows/pr-review.yml         ← Active review
└── pr-review-system/
    ├── scripts/run_pr_review.py        ← Review logic
    └── docs/TEAM_LEAD_REVIEW.md        ← What we check (details)
```

---

## Customize

Edit `pr-review-system/scripts/run_pr_review.py` to:
- Change what blocks merge vs warns only
- Add Java compile check
- Adjust complexity/line-length limits
- Skip checks you don't need

---

## Questions?

See [pr-review-system/docs/TEAM_LEAD_REVIEW.md](pr-review-system/docs/TEAM_LEAD_REVIEW.md) for details on what each check does.
