# Changelog

All notable changes to the headcount agent system are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.3.0] — 2026-05-28

### Added
- `CLAUDE.md` — project-wide conventions: architecture overview, domain conventions (Lumina company, department codes, level taxonomy, fully loaded cost rate), materiality thresholds, build surfaces, skills reference, repository layout, output conventions, data access, demo flow script, and related systems link back to close-system
- `agents/headcount-forecast/AGENT.md` — Headcount Forecast Agent v0.1.0: role, skills loaded, inputs accepted, outputs produced, operating principles, fully loaded cost methodology, structured output envelope, invocation patterns
- `agents/hiring-pipeline/AGENT.md` — Hiring Pipeline Agent v0.1.0: role, aging analysis methodology, budget exposure calculation, pipeline health indicators, Indeed MCP Phase 2 integration note, structured output envelope, invocation patterns
- `agents/compensation-analysis/AGENT.md` — Compensation Analysis Agent v0.1.0: role, compa-ratio methodology, market benchmarking, pay equity lens, absolute privacy rules, HR restricted output protocol, structured output envelope, invocation patterns
- `skills/headcount-analysis/SKILL.md` — shared skill covering headcount variance methodology, MoM bridge construction, attrition rate calculation, department aggregation rules, triage classification, and output format. Loaded by all three agents.
- `skills/compensation-benchmarking/SKILL.md` — compa-ratio methodology, market benchmark comparison (P25/P50/P75), pay equity signals, privacy rules, and output format. Loaded by Compensation Analysis Agent.
- `skills/people-cost-forecast/SKILL.md` — fully loaded cost rate, forecasting methodology (5-step), open role treatment, partial month handling, sensitivity analysis, and output format. Loaded by Headcount Forecast Agent.

### Changed
- `agents/*/README.md` — updated from "Pending" stubs to point to completed AGENT.md definitions
- `skills/*/README.md` — updated from "Pending" stubs to point to completed SKILL.md definitions

---

## [0.2.0] — 2026-05-28

### Added
- `data/synthetic/lumina_headcount_dataset.xlsx` — 8-sheet synthetic dataset for Lumina Streaming Co., November 2026 snapshot, with six intentionally seeded findings:
  - Finding 1: Engineering 5 over budget (30 actual vs 25 budgeted) — $220K monthly cost overage
  - Finding 2: Three Engineering open roles 46–90 days past target start — $720K combined budget exposure
  - Finding 3: Two Marketing Managers paid 17–22% above comp band midpoint (compa-ratio ~1.20)
  - Finding 4: One G&A Finance Analyst paid 18% below band midpoint (compa-ratio ~0.82, also below market P25)
  - Finding 5: Content team — 3 voluntary departures in November, annualised attrition 379%, 1 regrettable
  - Finding 6: Sales AE open role 45 days past target, commission plan not yet assigned
- `scripts/build_dataset.py` — synthetic dataset builder; regenerates `lumina_headcount_dataset.xlsx` (203 formulas, 0 errors)
- Dataset sheets: `README`, `Headcount_Roster` (80 LuminaUS employees), `Prior_Roster` (83 employees inc. Nov departures), `Headcount_Budget` (monthly by department, full FY2026), `Open_Pipeline` (15 open requisitions), `Comp_Bands` (salary bands by department and level), `Market_Benchmarks` (P25/P50/P75 by role category), `Attrition_Log` (trailing 3-month departures)

---

## [0.1.0] — 2026-05-27

### Added
- `README.md` — public-facing project overview: purpose, three-agent table, quick start, related systems link
- `CLAUDE.md` — initial stub (expanded in v0.3.0)
- `config/thresholds.yaml` — materiality thresholds: people cost variance trigger ($50K AND 5%), out-of-band comp flag (15%), open role risk flag (30 days past target), attrition flag (2% monthly)
- `agents/headcount-forecast/README.md` — stub
- `agents/hiring-pipeline/README.md` — stub
- `agents/compensation-analysis/README.md` — stub
- `skills/headcount-analysis/README.md` — stub
- `skills/compensation-benchmarking/README.md` — stub
- `skills/people-cost-forecast/README.md` — stub
- `data/synthetic/.gitkeep` — placeholder; dataset added in v0.2.0
- `data/client/.gitkeep` — placeholder; gitignored; real client data never committed
- `outputs/.gitkeep` — placeholder for agent-generated artifacts
- `scripts/push.sh` — reusable commit-and-push shortcut
- `.gitignore` — excludes `/data/client/`, individual comp detail files, build artifacts

---

## Roadmap

| Version | Target | Scope |
|---|---|---|
| 0.4.0 | TBD | Headcount Forecast Agent v0.1.0 — reference outputs for November 2026 |
| 0.5.0 | TBD | Hiring Pipeline Agent v0.1.0 — reference outputs for November 2026 |
| 0.6.0 | TBD | Compensation Analysis Agent v0.1.0 — reference outputs for November 2026 |
| 0.7.0 | TBD | Close Orchestrator — sequences all three agents, produces consolidated people cost summary |
| 1.0.0 | TBD | Full people cost review cycle — all three agents, MCP connectors (Indeed, HRIS), client pilot ready |
