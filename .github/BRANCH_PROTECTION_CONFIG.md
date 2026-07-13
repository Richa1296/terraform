# Branch Protection Configuration Guide
#
# To apply these settings, use GitHub's web UI or the GitHub CLI:
# 
# GitHub Web UI:
# 1. Go to Settings → Branches → Branch protection rules
# 2. Click "Add rule"
# 3. Enter pattern name (e.g., "main", "develop", "release/*")
# 4. Configure as shown below
#
# GitHub CLI:
# gh api repos/{owner}/{repo}/branches/{branch}/protection \
#   --input branch-protection.json

# === CONFIGURATION FOR main BRANCH ===

# Branch name pattern
branch: "main"

# Require status checks to pass before merging
required_status_checks:
  strict: true  # Require branch to be up to date before merge
  contexts:
    # Code Quality
    - "Java Code Quality Checks / Checkstyle Analysis"
    - "Java Code Quality Checks / SpotBugs Analysis"
    - "Java Code Quality Checks / PMD Analysis"
    - "Java Code Quality Checks / Dependency Vulnerability Check"
    
    # Python Quality
    - "Python Code Quality Checks / Pylint Analysis"
    - "Python Code Quality Checks / Flake8 Linting"
    - "Python Code Quality Checks / Black Code Formatting Check"
    - "Python Code Quality Checks / Bandit Security Scan"
    - "Python Code Quality Checks / Dependency Safety Check"
    
    # Terraform Quality
    - "Terraform Code Quality Checks / Terraform Format Check"
    - "Terraform Code Quality Checks / Terraform Validation"
    - "Terraform Code Quality Checks / TFLint Analysis"
    - "Terraform Code Quality Checks / Checkov Infrastructure Security Scan"
    - "Terraform Code Quality Checks / Trivy Vulnerability Scan"
    
    # Security
    - "Secrets and Credentials Scanning / TruffleHog Secret Detection"
    - "Secrets and Credentials Scanning / GitLeaks Secret Scanning"
    - "Secrets and Credentials Scanning / Credential and Configuration Check"
    - "Secrets and Credentials Scanning / Environment File Check"
    
    # Advanced Security
    - "Advanced Security Scanning / Trivy Filesystem Scan"
    - "Advanced Security Scanning / Trivy Configuration Scan"
    - "Advanced Security Scanning / OWASP Dependency-Check"
    - "Advanced Security Scanning / CodeQL Analysis"
    
    # Infrastructure
    - "Infrastructure-as-Code Validation / Checkov Infrastructure Security"
    - "Infrastructure-as-Code Validation / TFLint with Strict Rules"
    - "Infrastructure-as-Code Validation / Terraform Validation and Plan"
    
    # AI Review
    - "AI-Powered Code Review / Intelligent Code Pattern Analysis"
    
    # SonarQube (if enabled)
    - "SonarQube Code Quality Analysis / SonarQube Analysis"

# Require pull request reviews before merging
required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: false  # Set to true if using CODEOWNERS file
  require_last_push_approval: false

# Require approval of the most recent reviewable push
require_last_push_approval: false

# Require all conversations to be resolved
required_conversation_resolution:
  enabled: true

# Require signed commits
required_signatures:
  enabled: false  # Set to true to require GPG signed commits

# Require branches to be up to date before merging
require_branches_up_to_date: true

# Enforce all configured restrictions above for administrators
enforce_admins: true

# Allow or disallow force pushes for all users
allow_force_pushes:
  enabled: false

# Allow or disallow deletions for all users
allow_deletions:
  enabled: false

# Allow auto-merge
allow_auto_merge: true

# Delete head branch on merge
delete_branch_on_merge: true

# Require merge queue
required_merge_queue:
  enabled: false  # Set to true to require linear history via merge queue

---

# === CONFIGURATION FOR develop BRANCH ===
# Similar to main but slightly less restrictive

branch: "develop"

required_status_checks:
  strict: true
  # Same contexts as main, or subset for faster development
  contexts:
    - "Python Code Quality Checks / Pylint Analysis"
    - "Python Code Quality Checks / Flake8 Linting"
    - "Terraform Code Quality Checks / Terraform Validation"
    - "Secrets and Credentials Scanning / Credential and Configuration Check"
    - "Advanced Security Scanning / Trivy Filesystem Scan"

required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true

require_branches_up_to_date: true
enforce_admins: true

---

# === HOW TO APPLY THESE SETTINGS ===

# Option 1: GitHub Web UI
# 1. Go to repository Settings
# 2. Navigate to Branches in left sidebar
# 3. Click "Add rule"
# 4. Pattern name: "main"
# 5. Check:
#    - ✓ Require a pull request before merging
#    - ✓ Require status checks to pass before merging
#    - ✓ Require branches to be up to date before merging
#    - ✓ Require pull request reviews before merging
#    - ✓ Require conversation resolution
#    - ✓ Include administrators
# 6. In Status checks, select all workflows listed above
# 7. Click "Create"

# Option 2: GitHub CLI
# gh repo edit --default-branch main
# gh api repos/{owner}/{repo}/branches/main/protection \
#   --field required_pull_request_reviews.required_approving_review_count=1 \
#   --field required_status_checks.strict=true \
#   --field enforce_admins=true

# Option 3: Terraform (for IaC management)
# resource "github_branch_protection" "main" {
#   repository_id            = github_repository.this.node_id
#   pattern                  = "main"
#   required_status_checks {
#     strict   = true
#     contexts = [...]
#   }
#   required_pull_request_reviews {
#     required_approving_review_count = 1
#     dismiss_stale_reviews           = true
#   }
#   enforce_admins = true
# }

---

# === RECOMMENDED ADDITIONAL SETTINGS ===

# In Settings → General:
# - ✓ Automatically delete head branches
# - ✓ Allow auto-merge commits (squash or rebase preferred)
# - ✓ Always suggest updating pull request branches

# In Settings → Actions → General:
# - Allow all actions and reusable workflows

# In Settings → Security → Code security and analysis:
# - ✓ Enable Dependabot alerts
# - ✓ Enable Dependabot security updates
# - ✓ Enable secret scanning
# - ✓ Enable secret scanning push protection

# In Settings → Code security → Code scanning:
# - Enable CodeQL analysis (via workflow)
# - Enable other SAST tools as needed

---

# === TROUBLESHOOTING ===

# "Context not available" error?
# → Workflow hasn't completed yet. Wait and retry push.

# Too many status checks failing?
# → Start with critical checks only. Add others gradually.

# Admins can't merge?
# → Set enforce_admins: false temporarily to bypass, or:
#   → Fix the failing status check

# How to temporarily bypass protection?
# → Use GitHub's "Bypass protection" button (must be admin + have permission)
# → Or push without --force using a new branch

# How to update existing rule?
# → Delete old rule and create new one, OR
# → Use GitHub CLI or API to update
