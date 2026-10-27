# Contributing to Privacy & Data Protection Skills

Thank you for contributing to the Privacy & Data Protection Skills library!

## Development Guidelines

1. **Deterministic Execution**: Every new skill must contain an executable `scripts/process.py` runner with `from __future__ import annotations`.
2. **Standard Directory Layout**:
   ```
   skills/<skill-id>/
   ├── SKILL.md
   ├── assets/
   │   └── template.md
   ├── references/
   │   ├── standards.md
   │   └── workflows.md
   └── scripts/
       └── process.py
   ```
3. **Quality Gates**:
   Before submitting a Pull Request, ensure that all tests pass:
   ```bash
   python scripts/verify-all.py
   python scripts/router.py --stats
   ```
