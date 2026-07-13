# Contributing Guide

This guide explains how our automated PR review system works and what to expect when contributing to this repository.

## Overview

All pull requests go through multiple layers of automated quality and security checks before human review. This document explains what checks run, what they detect, and how to respond to their findings.

## Automated Review Layers

### Layer 1: Code Quality & Style

**When it runs**: On every PR that modifies code files
**Tools**: Pylint, Flake8, Checkstyle, PMD, Black, SpotBugs

**What it checks**:
- Code formatting and style consistency
- Potential bugs and anti-patterns
- Complexity metrics
- Dead code and unused variables
- Documentation completeness

**Response**: Fix style issues with `black .` (Python) or `terraform fmt -recursive .` (Terraform)

### Layer 2: Security & Secrets

**When it runs**: On every PR
**Tools**: TruffleHog, GitLeaks, Bandit, OWASP Dependency-Check

**What it checks**:
- Hardcoded credentials (AWS keys, passwords, API keys)
- Private keys and certificates
- Known vulnerable dependencies
- Python security anti-patterns
- Exposed secrets in environment files

**Response**: 
- Never commit `.env` files or configuration with credentials
- Use GitHub Secrets for sensitive values
- Rotate any exposed credentials immediately

### Layer 3: Infrastructure-as-Code

**When it runs**: On PRs modifying `.tf`, `Dockerfile`, or `docker-compose.yml`
**Tools**: Checkov, TFLint, Hadolint, Trivy

**What it checks**:
- Terraform best practices and conventions
- Security misconfigurations (open security groups, public S3 buckets, etc.)
- Unencrypted databases and storage
- Dockerfile security (running as root, missing USER directive, etc.)
- Kubernetes manifest security

**Response**:
- Fix security group rules to be less permissive than `0.0.0.0/0`
- Enable encryption for databases and storage
- Use non-root users in containers
- Add required security controls

### Layer 4: SonarQube Analysis

**When it runs**: On every PR (if configured)
**Tools**: SonarQube/SonarCloud

**What it checks**:
- Code smells and maintainability issues
- Code coverage metrics
- Duplicated code
- Cognitive complexity
- Security hotspots

**Response**: Review the SonarQube dashboard and address items above the quality gate threshold

### Layer 5: AI-Powered Review

**When it runs**: On every non-draft PR
**Tools**: Custom pattern analysis, optional GitHub Copilot

**What it checks**:
- Anti-patterns (N+1 queries, bare excepts, missing error handling)
- Code complexity and cyclomatic metrics
- Documentation quality
- Missing exception handling
- Potential logical errors

**Response**: Review suggestions and make improvements where applicable

## Checking Your PR Status

1. **Automated Checks Tab**: Click "Checks" on your PR to see all running workflows
2. **Check Details**: Click individual checks to see detailed output and failures
3. **Artifacts**: Download report artifacts (HTML reports, JSON findings) for deeper analysis
4. **Summary Comment**: Look for the bot comment with a consolidated review summary

## Common Issues and Solutions

### Pylint/Flake8 Errors

```bash
# View violations
pylint your_file.py

# Format code automatically
black your_file.py

# Check formatting without changes
black --check your_file.py --diff
```

### Terraform Issues

```bash
# Format all Terraform files
terraform fmt -recursive .

# Validate syntax
terraform validate

# Run TFLint
tflint --init
tflint --recursive .
```

### Security Findings

If a security tool flags credentials:
1. Immediately delete the credentials from git history
2. Rotate any exposed credentials
3. Add patterns to `.gitignore` to prevent future commits
4. Use GitHub Secrets instead

### SonarQube Quality Gate Failures

1. Navigate to your SonarQube project dashboard
2. Review the "Issues" tab to see specific violations
3. Address items in order of severity and impact
4. Run a new push to trigger re-analysis

## Responding to Review Comments

### When a Check Fails

1. **Read the error message** - most tools provide clear, actionable guidance
2. **Review the documentation** - each tool has docs explaining the rule
3. **Make the fix** locally
4. **Push the changes** - checks will run automatically again
5. **Don't force merge** - wait for checks to pass

### Best Practices

1. **Address critical issues first** - security findings, syntax errors
2. **Fix warnings before merge** - prevents technical debt accumulation
3. **Keep commits focused** - don't mix refactoring with feature changes
4. **Write meaningful commit messages** - help reviewers understand intent
5. **Add documentation** - especially for complex logic

## Configuration Files

Review these files to understand tool configurations:

- `.pylintrc` - Python linting rules
- `.flake8` - Python formatting and complexity limits
- `.tflintrc` - Terraform linting rules
- `sonar-project.properties` - SonarQube analysis configuration
- `.github/workflows/` - Automation workflow definitions
- `.github/dependabot.yml` - Dependency update schedule

## Branch Protection Rules

This repository has branch protection rules requiring:

1. ✅ All automated checks must pass
2. ✅ At least one human review approval
3. ✅ No outstanding conversations or change requests

## Secrets and Environment Setup

Never commit secrets. Instead:

### For Local Development

Create a `.env.local` file (add to `.gitignore`):
```
DATABASE_URL=postgresql://localhost/db
API_KEY=your-key-here
```

### For CI/CD

Store secrets in GitHub:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Reference in workflows: `${{ secrets.SECRET_NAME }}`

## Getting Help

- **Tool documentation**: Links provided in check output
- **GitHub Discussions**: Ask questions about project standards
- **Contact maintainers**: Open an issue if something seems wrong

## Continuous Improvement

This automated review system improves over time:

- **Rules are updated regularly** to catch new patterns
- **False positives are discussed** and rules refined
- **New tools are evaluated** for integration
- **Feedback is welcome** - suggest improvements via issues

## Summary

The automated review system is designed to catch issues **before** human review, saving time and maintaining quality. By understanding each layer, you can write better code faster and merge with confidence.

Thank you for contributing!
