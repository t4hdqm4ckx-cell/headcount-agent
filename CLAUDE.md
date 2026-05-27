# Headcount & People Cost Agent System

> Multi-agent system for headcount planning, compensation analysis, and people cost forecasting. Built as a consulting portfolio piece demonstrating AI-assisted Finance and HR workflows for CFOs, CHROs, and FP&A leaders.

## 1. Architecture overview

Three agents on a shared layer of Skills, MCP connectors, and data sources:

| Agent | Role | Primary outputs |
|---|---|---|
| **Headcount Forecast** | Projects people costs by department against budget and prior period. Builds the MoM headcount bridge and flags cost variances. | Variance report (xlsx), people cost forecast (xlsx), forecast memo (md) |
| **Hiring Pipeline** | Analyzes open requisitions against the hiring plan, flags roles past their target start date, and quantifies budget exposure from unfilled headcount. | Pipeline status report (xlsx), budget exposure memo (md) |
| **Compensation Analysis** | Flags roles where comp is out of band vs. internal salary ranges or external market benchmarks. Surfaces retention risks and pay equity signals. | Comp review memo (md — HR restricted), comp exceptions list (xlsx — HR restricted) |

**Sequencing:** the three agents are independent — they do not invoke each other and can run in any order. The Headcount Forecast Agent is the natural starting point since its output (who is on payroll and at what cost) provides context for the other two.

**Human-in-the-loop:** no compensation change is proposed or actioned without explicit HR and Controller approval. Agents surface findings; humans decide.

**Privacy rule — absolute:** individual employee names and dollar salaries never appear in shared outputs. All findings aggregate to department and level. Individual data stays in restricted HR workpapers only. This rule cannot be overridden by any prompt.

## 2. Domain conventions

### Demo company

`Lumina Streaming Co.` — same synthetic company as the close system. Consistent conventions across both repos.

- ~600 employees globally; ~400 in LuminaUS (80 sampled in the synthetic dataset)
- Three entities: LuminaUS, LuminaEMEA, LuminaAPAC
- Compensation in USD; EMEA and APAC base salaries converted at period-average FX rate
- People costs approximately 65% of total operating expense base
- Fiscal year end: December 31; reporting currency USD

### Departments

| Dept code | Department | Approx LuminaUS headcount |
|---|---|---|
| Engineering | Engineering (software, ML, DevOps) | ~200 |
| G&A | Finance, HR, Legal, Operations | ~80 |
| Sales | Sales, Revenue, SDRs | ~80 |
| Marketing | Brand, Performance, Product Marketing | ~60 |
| Content | Original content, Licensing, Content strategy | ~80 |

### Level taxonomy

| Level | Description | Example titles |
|---|---|---|
| L1 | Entry level | Coordinator, Associate |
| L2 | Mid-level IC | Analyst, Specialist, Engineer |
| L3 | Senior IC / Team lead | Senior Engineer, Sr Manager |
| L4 | Manager / Director | Manager, Director |
| L5 | Senior Director / VP | VP, Senior Director |
| L6 | SVP / EVP | SVP, EVP |
| L7 | C-Suite | CFO, CTO, CMO, CRO, COO |

### Fully loaded cost

Always use fully loaded cost — never base salary alone. Fully loaded cost = base salary × **1.25** loading factor. The loading factor covers payroll taxes, benefits, and equity. Bonus accrues separately and is not included in the run rate.

Calibrate the loading factor per client in `config/thresholds.yaml`.

### Materiality thresholds

- People cost variance trigger: > $50,000 AND > 5% vs budget (department level; both conditions must be true)
- Out-of-band comp flag: > 15% above or below band midpoint (compa-ratio outside 0.85–1.15)
- Open role risk flag: target start date > 30 days past
- Attrition flag: monthly rate > 2% of department headcount

All thresholds live in `config/thresholds.yaml`. Changing a value there changes it everywhere.

## 3. Build surfaces

| Surface | Used for |
|---|---|
| **Claude Code** (this repo) | Agent development, skill iteration, dataset generation, version control |
| **Claude Projects** (claude.ai) | Productized demo. One Project per agent. System prompt + Skills + project knowledge files |
| **MCP connectors** | Phase 2 — priority: Indeed (market comp benchmarks), Google Drive (roster and pipeline files), Gmail (HR communications). Later: HRIS connectors (Workday, BambooHR, Rippling) |

## 4. Skills (in `/skills`)

Each skill follows the standard SKILL.md format. All three skills are loaded by the relevant agent; `headcount-analysis` is shared across all three.

- `headcount-analysis/` — variance methodology, attrition calculation, MoM bridge, aggregation rules, triage thresholds. Shared across all three agents.
- `compensation-benchmarking/` — compa-ratio methodology, market comparison, pay equity lens, privacy rules, output format.
- `people-cost-forecast/` — fully loaded cost rate, forecasting methodology, open role treatment, sensitivity analysis.

## 5. Repository layout

```
/headcount-agent/
├── CLAUDE.md                          # this file
├── README.md                          # public-facing overview
├── /agents/
│   ├── headcount-forecast/
│   │   └── AGENT.md
│   ├── hiring-pipeline/
│   │   └── AGENT.md
│   └── compensation-analysis/
│       └── AGENT.md
├── /skills/
│   ├── headcount-analysis/SKILL.md
│   ├── compensation-benchmarking/SKILL.md
│   └── people-cost-forecast/SKILL.md
├── /config/
│   └── thresholds.yaml
├── /data/
│   ├── synthetic/
│   │   └── lumina_headcount_dataset.xlsx
│   └── client/                        # gitignored; real client data
├── /outputs/
│   └── YYYY-MM/                       # one folder per analysis period
│       ├── headcount-forecast/
│       ├── hiring-pipeline/
│       └── compensation-analysis/
└── /scripts/
    ├── build_dataset.py               # regenerates the synthetic dataset
    └── push.sh                        # stage, commit, push shortcut
```

## 6. Output conventions

**File naming:** `YYYY-MM_<entity>_<artifact>_v<n>.<ext>`

Examples:
- `2026-11_LuminaUS_HeadcountVariance_v1.xlsx`
- `2026-11_LuminaUS_PipelineStatus_v1_memo.md`
- `2026-11_LuminaUS_CompReview_v1_memo.md` ← HR restricted

**Access control tagging:**

Every Compensation Analysis output is marked HR restricted at the top of the file. Do not distribute to managers or the broader finance team without explicit HR sign-off. The file name suffix `_HR-RESTRICTED` is appended when writing to `outputs/`.

**Agent output envelope** — every agent returns:

```json
{
  "result": { ... },
  "exceptions": [
    { "severity": "high|medium|low", "category": "...", "description": "...", "proposed_action": "..." }
  ],
  "_metadata": {
    "agent": "headcount-forecast|hiring-pipeline|compensation-analysis",
    "version": "0.1.0",
    "run_timestamp": "ISO-8601",
    "sources": [{ "path": "...", "sheet": "..." }],
    "human_reviewer": null
  }
}
```

## 7. Data access

**Current phase (synthetic):** source of truth is `/data/synthetic/lumina_headcount_dataset.xlsx`. All agents read from this workbook.

Eight sheets: `README`, `Headcount_Roster`, `Prior_Roster`, `Headcount_Budget`, `Open_Pipeline`, `Comp_Bands`, `Market_Benchmarks`, `Attrition_Log`.

**Synthetic dataset embedded findings (for demo validation):**

| # | Finding | Agent | Sheet |
|---|---|---|---|
| 1 | Engineering 5 over budget (30 actual vs 25 budgeted) | Headcount Forecast | Headcount_Roster, Headcount_Budget |
| 2 | Three Engineering open roles > 30 days past target start, $720K exposure | Hiring Pipeline | Open_Pipeline |
| 3 | Two Marketing Managers paid > 15% above comp band midpoint | Comp Analysis | Headcount_Roster, Comp_Bands |
| 4 | One G&A Finance Analyst paid 18% below band midpoint | Comp Analysis | Headcount_Roster, Comp_Bands |
| 5 | Content team: 3 departures in November, annualised attrition 36% | Headcount Forecast | Prior_Roster, Attrition_Log |
| 6 | Sales AE open role 45 days past target, commission plan not assigned | Hiring Pipeline | Open_Pipeline |

**Phase 2 (client deployment):** replace the synthetic workbook with MCP connectors:
- Workday / BambooHR / Rippling → live roster and org data
- Indeed MCP → live market comp benchmarks
- Google Drive / SharePoint → pipeline and budget files
- Gmail → HR communications and approval workflows

Each agent's data access is isolated in its folder so the Phase 1 → Phase 2 swap touches only that module.

## 8. Demo flow (for prospects)

Recommended walkthrough for a CFO, CHRO, or FP&A leader:

1. **Open with the pain.** "People costs are 65% of your OpEx, and most FP&A teams are running their headcount analysis in a spreadsheet that's two weeks stale by the time it reaches the CFO. By the time you know Engineering is five heads over budget, you've already spent the money."

2. **Show the Headcount Forecast Agent.** Feed it the roster and budget. Watch it identify Engineering running 5 over plan, quantify the cost overage, build the November bridge (3 Content departures in, 5 Engineering over-hires out), and flag the attrition rate.

3. **Show the Hiring Pipeline Agent.** Three Engineering roles are 46–90 days past their target start dates. Total budget exposure: $720K. The prospect immediately understands this is money they budgeted for but haven't spent — which looks good on the P&L today but means the team is under-resourced.

4. **Show the Compensation Analysis Agent.** Two Marketing Managers are 17–22% above their band midpoint. One Finance Analyst is 18% below — and compensation was cited in a recent departure in the same function. The agent flags both, routes appropriately, never shows a dollar amount or a name.

5. **Close on the privacy architecture.** Open the comp exceptions output. Show that it contains Emp IDs and compa-ratios — no names, no dollar amounts. "This output goes to HR and the Controller only. When you're ready to have that conversation with a manager, HR brings the detail. Until then, the system enforces the access boundary automatically."

The prospect's question will be "can this connect to our Workday?" — that is the buying signal. Answer: "Phase 1 uses a file export from your HRIS. Phase 2 wires directly via MCP connector. Four to six weeks to a working pilot."

## 9. What this project is NOT

- Not a replacement for HR. It is a force multiplier — surfaces what needs attention so HR can act, not a system that acts on HR's behalf.
- Not making comp decisions. Every proposed action routes to a human for approval.
- Not surfacing individual data in shared outputs. The privacy rule is absolute.
- Not connected to live HRIS in the demo. Phase 2 work.
- Not a performance management system. Compensation analysis is backward-looking (are people paid correctly?) not forward-looking (should this person get a raise?).

## 10. Related systems

- [close-system](https://github.com/t4hdqm4ckx-cell/close-system) — month-end close automation. People cost variances in the close system (e.g., Engineering salaries above budget) can be explained by findings from this system.
