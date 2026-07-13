#!/usr/bin/env python3
"""
Run a small set of checks that mirror what a team lead looks for on a PR.
Outputs: review-summary.md (GitHub Step Summary), review.json, GITHUB_OUTPUT vars.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Finding:
    file: str
    line: int | None
    message: str
    hint: str = ""
    level: str = "suggestion"  # must_fix | should_fix | suggestion


@dataclass
class ReviewResult:
    areas: list[dict] = field(default_factory=list)
    must_fix: list[Finding] = field(default_factory=list)
    should_fix: list[Finding] = field(default_factory=list)
    suggestions: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        bucket = {
            "must_fix": self.must_fix,
            "should_fix": self.should_fix,
            "suggestion": self.suggestions,
        }[finding.level]
        bucket.append(finding)

    @property
    def blocked(self) -> bool:
        return len(self.must_fix) > 0

    @property
    def verdict(self) -> str:
        if self.blocked:
            return "fail"
        if self.should_fix:
            return "warn"
        return "pass"

    def to_json(self) -> dict:
        def dump(items: list[Finding]) -> list[dict]:
            return [
                {"file": f.file, "line": f.line, "message": f.message, "hint": f.hint}
                for f in items
            ]

        return {
            "verdict": self.verdict,
            "blocked": self.blocked,
            "areas": self.areas,
            "must_fix": dump(self.must_fix),
            "should_fix": dump(self.should_fix),
            "suggestions": dump(self.suggestions),
        }


def changed_files() -> list[str]:
    raw = os.environ.get("CHANGED_FILES", "").strip()
    if not raw:
        return []
    return [f for f in raw.split() if f and Path(f).exists()]


def run_cmd(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return 1, str(exc)


def check_secrets(files: list[str], result: ReviewResult) -> None:
    patterns = [
        (r"AKIA[0-9A-Z]{16}", "Possible AWS access key"),
        (r"(?i)(password|api_key|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]", "Possible hardcoded secret"),
        (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private key in repository"),
    ]
    hits = 0
    for path in files:
        if not path.endswith((".py", ".java", ".tf", ".yml", ".yaml", ".json", ".properties")):
            continue
        try:
            text = Path(path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for pattern, msg in patterns:
                if re.search(pattern, line) and "example" not in line.lower() and "placeholder" not in line.lower():
                    hits += 1
                    result.add(
                        Finding(
                            file=path,
                            line=i,
                            message=msg,
                            hint="Use GitHub Secrets or environment variables — never commit credentials.",
                            level="must_fix",
                        )
                    )
    status = "fail" if hits else "pass"
    notes = f"{hits} issue(s)" if hits else "No secrets detected"
    result.areas.append({"label": "🔐 Security (secrets & credentials)", "status": status, "notes": notes})


def check_python_bugs(py_files: list[str], result: ReviewResult) -> None:
    if not py_files:
        result.areas.append({"label": "🐛 Obvious bugs (Python syntax/errors)", "status": "na", "notes": "No Python changes"})
        return
    code, out = run_cmd(
        ["flake8", "--select=E9,F63,F7,F82", "--show-source", *py_files]
    )
    hits = 0
    for line in out.splitlines():
        if ":" in line and ".py" in line:
            hits += 1
            parts = line.split(":", 3)
            if len(parts) >= 4:
                result.add(
                    Finding(
                        file=parts[0],
                        line=int(parts[1]) if parts[1].isdigit() else None,
                        message=parts[3].strip(),
                        hint="Fix syntax or undefined-name errors before merge.",
                        level="must_fix",
                    )
                )
    status = "fail" if hits or code != 0 else "pass"
    notes = f"{hits} error(s)" if hits else "No syntax errors"
    result.areas.append({"label": "🐛 Obvious bugs (Python syntax/errors)", "status": status, "notes": notes})


def check_python_security(py_files: list[str], result: ReviewResult) -> None:
    if not py_files:
        return
    code, out = run_cmd(["bandit", "-r", *py_files, "-ll", "-f", "json", "-q"])
    try:
        data = json.loads(out) if out.strip().startswith("{") else {"results": []}
    except json.JSONDecodeError:
        data = {"results": []}
    hits = 0
    for item in data.get("results", []):
        sev = item.get("issue_severity", "")
        if sev in ("HIGH", "MEDIUM"):
            hits += 1
            level = "must_fix" if sev == "HIGH" else "should_fix"
            result.add(
                Finding(
                    file=item.get("filename", ""),
                    line=item.get("line_number"),
                    message=item.get("issue_text", "Security issue"),
                    hint=item.get("issue_cwe", {}).get("link", "See Bandit docs"),
                    level=level,
                )
            )
    # Security area may already exist from secrets — merge into one row at end
    for area in result.areas:
        if area["label"].startswith("🔐"):
            if hits:
                area["status"] = "fail" if any(f.level == "must_fix" for f in result.must_fix) else "warn"
                area["notes"] = (area["notes"] + f"; {hits} code security note(s)").strip("; ")
            return
    result.areas.append(
        {
            "label": "🔐 Security (code patterns)",
            "status": "pass" if not hits else "warn",
            "notes": f"{hits} note(s)" if hits else "OK",
        }
    )


def check_standards(py_files: list[str], result: ReviewResult) -> None:
    if not py_files:
        result.areas.append({"label": "📐 Code standards (style)", "status": "na", "notes": "No Python changes"})
        return
    code, out = run_cmd(["flake8", "--max-line-length=120", "--max-complexity=15", *py_files])
    count = sum(1 for line in out.splitlines() if ".py:" in line)
    for line in out.splitlines()[:5]:
        if ".py:" in line:
            parts = line.split(":", 3)
            if len(parts) >= 4:
                result.add(
                    Finding(
                        file=parts[0],
                        line=int(parts[1]) if parts[1].isdigit() else None,
                        message=parts[3].strip(),
                        hint="Run: black <file> or fix manually.",
                        level="suggestion",
                    )
                )
    status = "warn" if count else "pass"
    notes = f"{count} style note(s)" if count else "Looks fine"
    result.areas.append({"label": "📐 Code standards (style)", "status": status, "notes": notes})


def check_terraform(tf_files: list[str], result: ReviewResult) -> None:
    if not tf_files:
        result.areas.append({"label": "🏗️ Infrastructure safety (Terraform)", "status": "na", "notes": "No Terraform changes"})
        return
    dirs = sorted({str(Path(f).parent) for f in tf_files})
    issues = 0
    for d in dirs:
        if d == ".":
            d = "."
        fmt_code, _ = run_cmd(["terraform", "fmt", "-check", "-recursive", d])
        if fmt_code != 0:
            issues += 1
            result.add(
                Finding(
                    file=d,
                    line=None,
                    message="Terraform files not formatted",
                    hint="Run: terraform fmt -recursive .",
                    level="should_fix",
                )
            )
        init_code, _ = run_cmd(["terraform", "init", "-backend=false", "-input=false"], cwd=d)
        if init_code == 0:
            val_code, val_out = run_cmd(["terraform", "validate", "-no-color"], cwd=d)
            if val_code != 0:
                issues += 1
                result.add(
                    Finding(
                        file=d,
                        line=None,
                        message="Terraform validation failed",
                        hint=val_out.strip()[:200],
                        level="must_fix",
                    )
                )
        for tf in Path(d).glob("*.tf"):
            text = tf.read_text(encoding="utf-8", errors="ignore")
            if "0.0.0.0/0" in text:
                issues += 1
                result.add(
                    Finding(
                        file=str(tf),
                        line=None,
                        message="Overly open network rule (0.0.0.0/0)",
                        hint="Restrict CIDR to required IPs only.",
                        level="should_fix",
                    )
                )
    status = "fail" if any(f.level == "must_fix" for f in result.must_fix if ".tf" in f.file or f.file in dirs) else ("warn" if issues else "pass")
    result.areas.append(
        {
            "label": "🏗️ Infrastructure safety (Terraform)",
            "status": status,
            "notes": f"{issues} note(s)" if issues else "Validated",
        }
    )


def check_dependencies(files: list[str], result: ReviewResult) -> None:
    req = [f for f in files if f.endswith("requirements.txt")]
    if not req:
        result.areas.append({"label": "📦 Dependencies (known vulnerabilities)", "status": "na", "notes": "No dependency file changed"})
        return
    code, out = run_cmd(["pip-audit", "-r", req[0], "--desc"])
    vulns = out.count("VULNERABILITY") + out.count("CVE-")
    if vulns:
        result.add(
            Finding(
                file=req[0],
                line=None,
                message="Known vulnerable packages in requirements.txt",
                hint="Upgrade affected packages (see pip-audit output in logs).",
                level="should_fix",
            )
        )
    result.areas.append(
        {
            "label": "📦 Dependencies (known vulnerabilities)",
            "status": "warn" if vulns else "pass",
            "notes": f"{vulns} finding(s)" if vulns else "No known CVEs",
        }
    )


def write_github_output(result: ReviewResult) -> None:
    out_path = os.environ.get("GITHUB_OUTPUT")
    payload = json.dumps(result.to_json())
    blocked = "true" if result.blocked else "false"
    if out_path:
        with open(out_path, "a", encoding="utf-8") as fh:
            fh.write("review_json<<EOF\n")
            fh.write(payload + "\n")
            fh.write("EOF\n")
            fh.write(f"blocked={blocked}\n")
    else:
        print(f"review_json={payload}")
        print(f"blocked={blocked}")


def write_step_summary(result: ReviewResult) -> None:
    icon = {"pass": "✅", "warn": "⚠️", "fail": "🛑", "na": "—"}
    lines = [
        "# PR Review (Team Lead View)\n",
        f"**Verdict:** {result.verdict.upper()}\n",
        "| Area | Status | Notes |",
        "|------|--------|-------|",
    ]
    for area in result.areas:
        lines.append(f"| {area['label']} | {icon.get(area['status'], '—')} | {area.get('notes', '')} |")
    if result.must_fix:
        lines.append("\n## Must fix\n")
        for f in result.must_fix:
            lines.append(f"- `{f.file}` — {f.message}")
    Path("review-summary.md").write_text("\n".join(lines), encoding="utf-8")
    Path("review.json").write_text(json.dumps(result.to_json(), indent=2), encoding="utf-8")


def main() -> int:
    files = changed_files()
    result = ReviewResult()

    py_files = [f for f in files if f.endswith(".py")]
    tf_files = [f for f in files if f.endswith(".tf") or f.endswith(".tfvars")]

    check_secrets(files, result)
    check_python_bugs(py_files, result)
    check_python_security(py_files, result)
    check_standards(py_files, result)
    check_terraform(tf_files, result)
    check_dependencies(files, result)

    write_step_summary(result)
    write_github_output(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
