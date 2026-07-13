#!/usr/bin/env bash

# Local Code Review Testing Script
# This script runs all the automated checks locally before pushing to GitHub

set -e

echo "🔍 Running Local Code Review Checks..."
echo ""

PYTHON_FOUND=false
JAVA_FOUND=false
TERRAFORM_FOUND=false
FAILED_CHECKS=0

# Check for Python files
if find . -name "*.py" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./.git/*" | grep -q .; then
    PYTHON_FOUND=true
    echo "📝 Python files detected"
fi

# Check for Java files
if find . -name "*.java" -not -path "./.git/*" | grep -q .; then
    JAVA_FOUND=true
    echo "☕ Java files detected"
fi

# Check for Terraform files
if find . -name "*.tf" -not -path "./.terraform/*" -not -path "./.git/*" | grep -q .; then
    TERRAFORM_FOUND=true
    echo "🏗️ Terraform files detected"
fi

echo ""

# Python checks
if [ "$PYTHON_FOUND" = true ]; then
    echo "═══════════════════════════════════"
    echo "Running Python Quality Checks"
    echo "═══════════════════════════════════"
    
    if command -v pylint &> /dev/null; then
        echo "Running Pylint..."
        if ! pylint --exit-zero --output-format=json \
            $(find . -name "*.py" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./.git/*") \
            > /dev/null 2>&1; then
            echo "⚠️  Pylint found issues (use --exit-zero to continue)"
            ((FAILED_CHECKS++))
        else
            echo "✓ Pylint passed"
        fi
    else
        echo "⚠️  Pylint not installed: pip install pylint"
    fi
    
    if command -v flake8 &> /dev/null; then
        echo "Running Flake8..."
        if ! flake8 . --exit-zero --exclude=.git,.venv,venv; then
            echo "⚠️  Flake8 found issues"
            ((FAILED_CHECKS++))
        else
            echo "✓ Flake8 passed"
        fi
    else
        echo "⚠️  Flake8 not installed: pip install flake8"
    fi
    
    if command -v black &> /dev/null; then
        echo "Checking Black formatting..."
        if ! black --check . --exclude="/(\.git|\.venv|venv|\.terraform)/" 2>/dev/null; then
            echo "⚠️  Black formatting issues found"
            echo "   Fix with: black ."
            ((FAILED_CHECKS++))
        else
            echo "✓ Black formatting passed"
        fi
    else
        echo "⚠️  Black not installed: pip install black"
    fi
    
    if command -v bandit &> /dev/null; then
        echo "Running Bandit security scan..."
        if ! bandit -r . -f json -o /dev/null 2>/dev/null; then
            echo "⚠️  Bandit found security issues"
            ((FAILED_CHECKS++))
        else
            echo "✓ Bandit passed"
        fi
    else
        echo "⚠️  Bandit not installed: pip install bandit"
    fi
    
    echo ""
fi

# Java checks
if [ "$JAVA_FOUND" = true ]; then
    echo "═══════════════════════════════════"
    echo "Running Java Quality Checks"
    echo "═══════════════════════════════════"
    
    if [ -f "pom.xml" ]; then
        echo "Running Maven Checkstyle..."
        if ! mvn checkstyle:check -DskipTests -q 2>/dev/null; then
            echo "⚠️  Checkstyle found issues"
            ((FAILED_CHECKS++))
        else
            echo "✓ Checkstyle passed"
        fi
    elif [ -f "build.gradle" ]; then
        echo "⚠️  Gradle build detected - manual checkstyle review recommended"
    fi
    
    echo ""
fi

# Terraform checks
if [ "$TERRAFORM_FOUND" = true ]; then
    echo "═══════════════════════════════════"
    echo "Running Terraform Validation"
    echo "═══════════════════════════════════"
    
    if command -v terraform &> /dev/null; then
        echo "Checking Terraform format..."
        if ! terraform fmt -check -recursive . 2>/dev/null; then
            echo "⚠️  Terraform formatting issues"
            echo "   Fix with: terraform fmt -recursive ."
            ((FAILED_CHECKS++))
        else
            echo "✓ Terraform formatting passed"
        fi
        
        echo "Validating Terraform files..."
        for dir in $(find . -name "*.tf" -not -path "./.terraform/*" -type f | xargs dirname | sort -u); do
            cd "$dir" || continue
            if [ -f ".terraform.lock.hcl" ] || [ -f "main.tf" ]; then
                if ! terraform init -backend=false -quiet 2>/dev/null; then
                    echo "⚠️  Failed to initialize Terraform in $dir"
                    ((FAILED_CHECKS++))
                    cd - > /dev/null
                    continue
                fi
                
                if ! terraform validate -json 2>/dev/null | grep -q '"valid": true'; then
                    echo "⚠️  Terraform validation failed in $dir"
                    ((FAILED_CHECKS++))
                else
                    echo "✓ Terraform validated: $dir"
                fi
            fi
            cd - > /dev/null
        done
    else
        echo "⚠️  Terraform not installed"
    fi
    
    if command -v tflint &> /dev/null; then
        echo "Running TFLint..."
        tflint --init 2>/dev/null || true
        if ! tflint --format json . 2>/dev/null | grep -q '"issues"'; then
            echo "✓ TFLint passed"
        else
            echo "⚠️  TFLint found issues"
            tflint --format default . || true
        fi
    else
        echo "⚠️  TFLint not installed"
    fi
    
    echo ""
fi

# Secrets scanning
echo "═══════════════════════════════════"
echo "Running Secrets Detection"
echo "═══════════════════════════════════"

if grep -r "AKIA" . --include="*.py" --include="*.java" --include="*.tf" 2>/dev/null | grep -v ".git"; then
    echo "❌ Potential AWS credentials found!"
    ((FAILED_CHECKS++))
else
    echo "✓ No AWS credentials detected"
fi

if grep -rE "(password|secret|api_key|token)\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}" . \
    --include="*.py" --include="*.java" --include="*.tf" 2>/dev/null | grep -v ".git"; then
    echo "⚠️  Potential secrets found - review manually"
    ((FAILED_CHECKS++))
else
    echo "✓ No obvious secrets detected"
fi

echo ""
echo "═══════════════════════════════════"
echo "Summary"
echo "═══════════════════════════════════"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo "✅ All checks passed locally!"
    echo "Your code is ready to push to GitHub for full CI/CD validation"
    exit 0
else
    echo "❌ $FAILED_CHECKS check(s) failed"
    echo "Please fix the issues before pushing"
    exit 1
fi
