# What the automated PR review checks (team-lead view)

This is a **simple** review — not 15 tools. It mirrors what a team lead typically checks in the first pass on a PR.

---

## One check, one comment

| In GitHub | What you see |
|-----------|----------------|
| **Checks tab** | Single status: **Team Lead Review** |
| **PR comment** | One summary table + short lists |
| **Actions run** | One job with a readable **Summary** panel |

---

## The 5 areas we check

### 1. Security (secrets and credentials)
**Team lead asks:** *Could this leak passwords or keys?*

- Hardcoded passwords, API keys, tokens
- AWS access keys
- Private keys in files

**Blocks merge:** Yes, if found

---

### 2. Obvious bugs (Python)
**Team lead asks:** *Will this even run?*

- Syntax errors
- Undefined names
- Import errors (flake8 fatal rules only)

**Blocks merge:** Yes, if found

**Note:** We do **not** run full Pylint or style police on every line.

---

### 3. Code standards (light touch)
**Team lead asks:** *Is this readable enough?*

- Very long lines, high complexity (warnings only)
- Shown as **suggestions**, not blockers

**Blocks merge:** No

---

### 4. Infrastructure safety (Terraform)
**Team lead asks:** *Are we opening the network or breaking infra?*

- `terraform fmt` and `validate` on changed modules
- Obvious risk: `0.0.0.0/0` in rules

**Blocks merge:** Yes, if validation fails

---

### 5. Dependencies
**Team lead asks:** *Are we pulling in a package with a known CVE?*

- `pip-audit` on `requirements.txt` when it changes

**Blocks merge:** No (warning only)

---

## What we intentionally skip (to reduce noise)

- SonarQube (use your existing Sonar if you already have it)
- Multiple parallel workflows
- Java Checkstyle / PMD / SpotBugs (add back only if needed)
- CodeQL, Semgrep, Trivy on every PR
- AI review bots
- Strict formatting gates on every file

You can turn advanced checks back on later from `pr-review-system/archive/workflows/`.

---

## How to read the PR comment

```
## PR Review Summary

**✅ Ready for human review** — no blocking issues found.

| What we check (team-lead view) | Status | Notes |
|--------------------------------|--------|-------|
| 🔐 Security ...                | ✅     | ...   |
| 🐛 Obvious bugs ...            | ✅     | ...   |
| 📐 Code standards ...          | ⚠️     | ...   |
| 🏗️ Infrastructure ...         | —      | ...   |
| 📦 Dependencies ...            | ✅     | ...   |

### 🛑 Must fix (blocks merge)
- only critical items

### ⚠️ Should fix
- recommended before or soon after merge

### 💡 Suggestions
- optional improvements
```

---

## For developers

**Before pushing (optional):**
```bash
python pr-review-system/scripts/run_pr_review.py
# Set CHANGED_FILES to your edited files, e.g.:
# CHANGED_FILES="src/foo.py" python pr-review-system/scripts/run_pr_review.py
```

**When a check fails:**
1. Read **Must fix** section only first
2. Fix those items
3. Push again — the same comment updates automatically

---

## For team leads

Use the bot comment as a **first pass**. You still review:

- Business logic and requirements
- Test coverage and test quality
- Architecture and design fit
- Naming and API contracts
- Edge cases automation cannot see

The bot handles repetitive hygiene so you can focus on judgment calls.

---

## Customization

Edit `pr-review-system/scripts/run_pr_review.py` to:

- Add Java compile check
- Tighten or loosen flake8 rules
- Enable SonarQube as a non-blocking step
- Change what blocks merge (`level="must_fix"`)

Edit `.github/workflows/pr-review.yml` to change when the workflow runs.
