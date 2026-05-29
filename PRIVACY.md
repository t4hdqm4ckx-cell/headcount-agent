# Privacy & Data Handling Policy

**Project:** Headcount & People Cost Agent System
**Applies to:** All agents, skills, outputs, and data files in this repository
**Effective:** 2026-05-28
**Owner:** FP&A / HR — jointly

---

## 1. Why this document exists

This system processes employee compensation, salary bands, attrition records, and hiring pipeline data. This is some of the most sensitive data a company holds. Mishandling it — surfacing an individual's salary in a shared output, distributing a comp review to the wrong audience, or committing real employee data to a public repository — causes real harm to real people and exposes the company to legal and regulatory risk.

This document defines the rules that govern how the agents, skills, and outputs in this system handle that data. These rules are not defaults that can be overridden by a prompt. They are absolute.

---

## 2. Data classification

All data in this system falls into one of three tiers:

| Tier | Classification | Description | Examples |
|---|---|---|---|
| **T1** | Public | Safe to share broadly; no sensitivity | Department headcount counts, org structure, job titles |
| **T2** | Internal | Finance and management use; not for general distribution | Department-level cost variances, budget vs actual, headcount totals, attrition rates |
| **T3** | Restricted | HR and Controller only; never shared without explicit approval | Individual salaries, compa-ratios, comp band exceptions, departure reasons, individual attrition records |

All Compensation Analysis Agent outputs are **T3 by default**.
All Headcount Forecast and Hiring Pipeline outputs are **T2 by default**, except where they reference individual employees (T3).

---

## 3. Absolute rules — cannot be overridden

These rules apply to every agent, every skill, every output, and every prompt in this system. No instruction, business justification, or prompt engineering can override them.

### 3.1 No individual salary data in shared outputs
Individual employee base salaries, total compensation, bonus targets, or equity values must never appear in any output that leaves the HR team. This includes memos, dashboards, slides, emails, and Slack messages.

**Permitted:** "The Marketing L3 band midpoint is above industry median" or "two employees in this group have a compa-ratio above 1.15."
**Not permitted:** "John Smith earns $168,000, which is $30,000 above his band midpoint."

### 3.2 No individual names in comp outputs
Compensation Analysis outputs must never identify individual employees by name, even in restricted workpapers distributed within HR. Use Employee ID (e.g., EMP-4007) only. Names are joined to IDs only at the point of HR action, by an authorized HR team member.

### 3.3 Aggregate to department and level minimum
The lowest granularity that may appear in a T2 output is department + level. Individual rows — even without names — must not appear in outputs distributed beyond HR and the Controller.

### 3.4 No real employee data in the repository
Real employee names, salaries, or personal information must never be committed to this repository. The `/data/client/` folder is gitignored for this reason. If a client data file is accidentally staged, run `git rm --cached` immediately before pushing.

Verify before every push:
```bash
git diff --cached --name-only | grep -i "client\|salary\|comp\|roster"
```

### 3.5 Compensation outputs are HR-restricted until explicitly released
All Compensation Analysis Agent outputs are marked `_HR-RESTRICTED` in the filename. They must not be distributed to department heads, hiring managers, or the broader finance team without written approval from the VP People & HR.

### 3.6 No comp data in prompts
Individual salary figures, comp band details, or employee-level data must not be typed into a Claude Projects chat prompt. Upload the source file to project knowledge — never paste raw salary data into the conversation window.

---

## 4. Data access controls

| Role | T1 | T2 | T3 |
|---|---|---|---|
| CFO | ✓ | ✓ | Read-only, aggregated |
| Controller | ✓ | ✓ | ✓ |
| VP Finance / FP&A Director | ✓ | ✓ | Aggregated only |
| VP People & HR | ✓ | ✓ | ✓ |
| HR Business Partners | ✓ | Limited | ✓ (own departments) |
| Department Heads / Managers | ✓ | Own dept only | ✗ |
| All others | ✓ | ✗ | ✗ |

The Compensation Analysis Agent enforces T3 access by producing only Emp ID-based outputs. The act of joining Emp IDs to names happens in the HR system, not in this agent.

---

## 5. Repository rules

### What is committed to this repo

| Committed | Not committed |
|---|---|
| Synthetic data (`/data/synthetic/`) | Real employee data (`/data/client/`) |
| Agent definitions (`/agents/`) | Individual salary files |
| Skill definitions (`/skills/`) | Comp exceptions with names |
| Config files (`/config/`) | Any file containing real PII |
| Reference outputs from synthetic data | Real client outputs |
| Build scripts | `.env` files or credentials |

### .gitignore enforcement

The following patterns are gitignored and must remain so:

```
/data/client/*
**/comp_detail*
**/salary_detail*
**/individual_comp*
**/*_names*
.env
.envrc
```

Do not remove these patterns from `.gitignore` for any reason.

### Public vs private repo

This repository is currently **public** for portfolio purposes. It contains only synthetic data. Before connecting any real client data or MCP connectors that access live HRIS data, the repository must be made **private** and access restricted to authorized team members.

To make private:
```bash
gh repo edit headcount-agent --visibility private
```

---

## 6. Claude Projects data handling

### What goes in project knowledge

Acceptable to upload to a Claude Project's knowledge base:
- Skill files (SKILL.md)
- Agent definitions (AGENT.md)
- Synthetic datasets
- Anonymized client datasets (Emp IDs only, no names, no raw salaries)

Not acceptable to upload to a Claude Project's knowledge base:
- Real employee rosters with names and salaries
- Unanonymized compensation data
- Any file that would be T3 under the classification in section 2

### Conversation window

Do not type individual salary figures, employee names, or comp band exceptions into the Claude Projects conversation window. This data may be retained as part of conversation history. Upload the data file instead and reference it from project knowledge.

### Conversation history

Assume all Claude Projects conversation history is retained. Do not discuss specific individual compensation cases by name or dollar amount in a Project conversation, even if you believe the conversation is private.

---

## 7. MCP connector rules (Phase 2)

When live HRIS connectors (Workday, BambooHR, Rippling) are enabled:

- **Read-only access only.** No agent in this system writes back to the HRIS.
- **Minimum necessary data.** Connectors should return department, level, base salary range, and headcount counts — not full personnel files.
- **No caching of individual data.** Live connector responses must not be written to files in this repository.
- **Indeed MCP.** Market benchmark data from Indeed contains no individual employee data and is safe for general use. Role category and compensation percentile data is T2.
- **Audit log.** All MCP connector calls that access compensation data must be logged with timestamp, agent, and data fields accessed.

---

## 8. Incident response

If any of the following occur, treat it as a privacy incident and act immediately:

| Incident | Immediate action |
|---|---|
| Real employee data committed to the repo | `git rm --cached <file>`, push, rotate any exposed credentials, notify HR and Legal |
| Individual salary data appears in a shared output | Recall the output, identify recipients, notify HR and the Controller |
| Comp Analysis output distributed without HR approval | Identify recipients, recall, notify VP People & HR |
| Real employee names appear in a Claude Project conversation | Contact Anthropic support, notify HR, review conversation history retention policy |

**Incident owner:** VP People & HR and Controller, jointly.

---

## 9. Synthetic data disclaimer

All data in `/data/synthetic/` is entirely fabricated. It does not represent any real person, organization, or compensation structure. Employee IDs, salaries, department structures, and company names are fictional and used for development and demonstration purposes only.

The synthetic dataset intentionally contains realistic-looking salary figures and compensation data to enable meaningful agent testing. This data must not be mistaken for real employee information and must not be distributed outside a development context as if it were real.

---

## 10. Acknowledgment

Anyone working with this system — including developers, consultants, and client team members — is expected to read this document before accessing any T3 data or running any Compensation Analysis Agent output.

Violations of the rules in section 3 (Absolute rules) are treated as serious incidents regardless of intent.

**Questions:** Contact the VP People & HR or the Controller.
