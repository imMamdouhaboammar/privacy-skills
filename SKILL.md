---
name: privacy-skills
description: >
  Universal dynamic privacy & data protection orchestrator routing across 257 specialized
  engineering procedures covering GDPR, CCPA/CPRA, EU AI Act, HIPAA, LGPD, and global standards.
  Use when conducting DPIA/PIA assessments, auditing RoPA compliance, assessing cross-border
  transfers, verifying consent flows, implementing cryptographic privacy, or evaluating AI risks.
license: Apache-2.0
metadata:
  author: mamdouh-boammar
  version: "1.0"
  domain: privacy
  ecosystem: bug-killer
---

# Privacy & Data Protection Skills Orchestrator

The dynamic privacy execution invariant is:

$$\text{Privacy Requirement} \xrightarrow{\text{Dynamic Router}} \text{Domain Procedure} \xrightarrow{\text{Compliance Artifact}} \text{Evidence Gate} \xrightarrow{\text{Auditor-Ready Decision}}$$

## Overview

Privacy Skills equips AI coding agents (Claude Code, Google Antigravity, Gemini CLI, Cursor, OpenAI Codex) with 257 machine-readable, verified privacy engineering and compliance procedures. Every skill incorporates structured workflows, statutory citations, and an executable automation script (`scripts/process.py`) with zero hallucinated requirements.

Part of the **Bug Killer Security & Autonomous Healing Ecosystem** ([`imMamdouhaboammar/bug-killer`](https://github.com/imMamdouhaboammar/bug-killer)).

---

## ⚡ Dynamic Intent Routing

To automatically find the right procedure for any privacy task:

```bash
# Search by keyword
python scripts/router.py "biometric facial recognition"

# Filter by regulation
python scripts/router.py --regulation GDPR
python scripts/router.py --regulation EU_AI_ACT
python scripts/router.py --regulation HIPAA

# Filter by subdomain
python scripts/router.py --subdomain ai-privacy-governance

# Display full distribution metrics
python scripts/router.py --stats
```

---

## Domain Taxonomy (20 Core Subdomains)

```mermaid
flowchart TD
    ROOT["Privacy Skills Catalog (257)"]

    subgraph Governance ["Governance & Audit"]
        G1["gdpr-compliance"]
        G2["privacy-impact-assessment (DPIA/PIA)"]
        G3["records-of-processing (RoPA)"]
        G4["privacy-audit-certification"]
        G5["privacy-by-design"]
    end

    subgraph Operations ["Rights & Operations"]
        O1["data-subject-rights (DSAR)"]
        O2["consent-management"]
        O3["cookie-consent-compliance"]
        O4["data-breach-response"]
        O5["data-retention-deletion"]
    end

    subgraph Engineering ["Engineering & AI"]
        E1["ai-privacy-governance (EU AI Act)"]
        E2["privacy-engineering (PETs / Diff Privacy)"]
        E3["data-classification (PII Discovery)"]
        E4["cross-border-transfers (SCC / DPF)"]
        E5["vendor-privacy-management"]
    end

    subgraph Regional ["Regional & Sectoral"]
        R1["us-state-privacy-laws (CCPA / VCDPA)"]
        R2["global-privacy-regulations (LGPD / PIPL)"]
        R3["healthcare-privacy (HIPAA / HITECH)"]
        R4["children-data-protection (COPPA / AADC)"]
        R5["employee-data-privacy"]
    end

    ROOT --> Governance
    ROOT --> Operations
    ROOT --> Engineering
    ROOT --> Regional
```

---

## Standard Skill Structure

Every procedure in `skills/<skill-id>/` implements a uniform contract:

- **`SKILL.md`**: Behavioral instructions, legal citations, architecture patterns, and gate conditions.
- **`scripts/process.py`**: Python compliance automation engine, runnable standalone with demo mode.
- **`assets/template.md`**: Auditor-ready markdown template or formal filing artifact.
- **`references/standards.md`**: Exact regulatory articles, recital mappings, and international standards.
- **`references/workflows.md`**: Step-by-step phased execution playbooks.
