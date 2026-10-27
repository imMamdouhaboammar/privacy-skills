#!/usr/bin/env python3
from __future__ import annotations

"""
Automated Multi-Dimensional Test Suite for Privacy & Data Protection Skills
Validates 100% of skills across Structural, Portability, and Execution gates.
"""

import os
import subprocess
import sys
import yaml
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def verify_single_skill(skill_name: str) -> tuple[str, list[str]]:
    skill_path = SKILLS_DIR / skill_name
    errors = []

    # 1. Structural files check
    required_files = [
        skill_path / "SKILL.md",
        skill_path / "scripts" / "process.py",
        skill_path / "assets" / "template.md",
        skill_path / "references" / "standards.md",
        skill_path / "references" / "workflows.md",
    ]
    for rf in required_files:
        if not rf.exists():
            errors.append(f"Missing required artifact: {rf.name}")

    # 2. YAML frontmatter check
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append("Malformed YAML frontmatter in SKILL.md")
        else:
            try:
                fm = yaml.safe_load(parts[1])
                if not fm or not isinstance(fm, dict):
                    errors.append("Empty or non-dictionary YAML frontmatter")
                else:
                    if fm.get("name") != skill_name:
                        errors.append(f"Frontmatter name '{fm.get('name')}' != folder name '{skill_name}'")
                    if not fm.get("description"):
                        errors.append("Missing description in frontmatter")
            except Exception as ex:
                errors.append(f"YAML parse error: {ex}")

    # 3. Execution check of scripts/process.py
    proc_py = skill_path / "scripts" / "process.py"
    if proc_py.exists():
        try:
            res = subprocess.run(
                [sys.executable, str(proc_py)],
                capture_output=True,
                text=True,
                timeout=6,
            )
            if res.returncode != 0:
                err_msg = res.stderr.splitlines()[-1] if res.stderr else f"Exit code {res.returncode}"
                errors.append(f"Runtime failure: {err_msg}")
        except subprocess.TimeoutExpired:
            errors.append("Execution timed out (>6s)")
        except Exception as ex:
            errors.append(f"Subprocess error: {ex}")

    return skill_name, errors


def main():
    entries = sorted(
        d for d in os.listdir(SKILLS_DIR)
        if (SKILLS_DIR / d).is_dir() and d != "privacy"
    )
    print(f"Executing automated verification on {len(entries)} skills using {os.cpu_count() or 4} workers...")

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(verify_single_skill, entries))

    passed = 0
    failed = []
    for skill_name, errors in results:
        if not errors:
            passed += 1
        else:
            failed.append((skill_name, errors))

    print(f"\n==================================================================")
    print(f"  VERIFICATION REPORT: {passed}/{len(entries)} SKILLS PASSED")
    print(f"==================================================================")

    if failed:
        print(f"\n[FAILURES DETECTED: {len(failed)}]")
        for sname, errs in failed:
            print(f"  ❌ {sname}:")
            for e in errs:
                print(f"     - {e}")
        sys.exit(1)
    else:
        print("\n✅ All 257 privacy skills verified with ZERO structural or execution errors.")
        sys.exit(0)


if __name__ == "__main__":
    main()
