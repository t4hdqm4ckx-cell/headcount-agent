# Client Onboarding Guide

How to move from the synthetic demo dataset to a live client engagement.
This guide covers data preparation, threshold calibration, Claude Projects
setup, and the go-live checklist.

**Estimated time:** 3–5 days for a prepared client with clean HRIS data.

---

## Prerequisites

Before starting, confirm the following are in place:

- [ ] Client has signed an engagement agreement with data handling provisions
- [ ] This GitHub repository has been set to **private** (`gh repo edit headcount-agent --visibility private`)
- [ ] Anthropic Claude account with Projects access (Pro or Teams tier)
- [ ] Client's HRIS admin can export the required data fields (see section 2)
- [ ] Authorized HR and Finance contacts identified for output review
- [ ] Python 3.10+ installed locally (`python --version`)
- [ ] Dependencies installed (`pip install -r requirements.txt --break-system-packages`)

---

## Step 1 — Understand the client's data structure

Before requesting any data, spend 30–60 minutes with the client's HRIS admin to understand:

1. **HRIS platform** — Workday, BambooHR, Rippling, ADP, or other. This determines the export format and field names.
2. **Org structure** — how departments are defined, whether levels are standardized, whether there are matrix reporting lines that complicate headcount attribution.
3. **Comp structure** — whether base salary is stored as annual or hourly, whether there are multiple pay components (base + allowances + COLA), whether equity is tracked in the HRIS or separately.
4. **Headcount definition** — does the client count contractors in headcount? Interns? Part-time employees as 0.5 FTE? The synthetic dataset uses only full-time employees — clarify this before building the roster.

Document the answers in a client context note and save it to `/data/client/client-context.md` (gitignored).

---

## Step 2 — Prepare the data files

The system expects data in the same structure as `lumina_headcount_dataset.xlsx`. The easiest path is to export from the HRIS and reshape to match the synthetic dataset's column structure.

### Required exports from the HRIS

| Sheet | Required fields | Notes |
|---|---|---|
| `Headcount_Roster` | Emp ID, Department, Level, Title, Entity, Start Date, Base Salary, Bonus %, FTE Status | No names. Emp IDs only in the file that goes into Claude Projects |
| `Prior_Roster` | Same fields, prior month snapshot | Pull from HRIS as of prior month-end |
| `Headcount_Budget` | Department, Month, Budgeted HC count, Budgeted cost | Finance team typically owns this in a budget tool or Excel |
| `Open_Pipeline` | Req ID, Department, Level, Title, Entity, Req Open Date, Target Start, Budgeted Comp, Stage, Hiring Manager ID | ATS export (Greenhouse, Lever, Workday Recruiting) |
| `Comp_Bands` | Department, Level, Band Min, Midpoint, Max | HR Compensation team owns this |
| `Market_Benchmarks` | Role Category, Level, P25, P50, P75, Source | Radford/Mercer, or pull live from Indeed MCP |
| `Attrition_Log` | Emp ID, Department, Level, Title, Entity, Last Day, Departure Type, Reason Category, Regrettable | HR exit interview data |

### Anonymization step — required before uploading to Claude Projects

Remove employee names before uploading any file to a Claude Project. The file that goes into project knowledge should contain Emp IDs only. Names are retained in a separate HR-controlled file that never leaves the HRIS or a secured shared drive.

```bash
# Quick Python anonymization check
python -c "
import openpyxl
wb = openpyxl.load_workbook('data/client/roster_raw.xlsx', data_only=True)
ws = wb['Headcount_Roster']
# Print column headers to verify no name column is present
print([ws.cell(1, c).value for c in range(1, ws.max_column+1)])
"
```

If a `Name`, `Full Name`, `First Name`, or `Last Name` column is present, remove it before saving to `/data/client/`.

### Reshape to match the synthetic structure

The `scripts/build_dataset.py` script is a template. Copy it and adapt it for the client's data:

```bash
cp scripts/build_dataset.py scripts/build_client_dataset.py
# Edit build_client_dataset.py to read from data/client/ and
# produce a correctly structured workbook in data/client/
```

Do not commit `build_client_dataset.py` if it contains client-specific field mappings. Add it to `.gitignore`.

---

## Step 3 — Calibrate the thresholds

Edit `config/thresholds.yaml` with client-specific values. Run `python config.py` after each change to verify.

### Calibration guide

**People cost variance trigger:**

The standard formula is: amount threshold = 0.5% of annual people cost budget; percentage threshold stays at 5%.

```
Annual people cost budget ÷ 12 months × 0.5% = monthly amount threshold
```

Example: $80M annual people cost budget → $80M ÷ 12 × 0.005 = **$33,333**. Round to $35,000.

**Comp out-of-band threshold:**

Default 15% works for most clients. Tighten to 10% for clients with formal compensation governance and narrow bands. Loosen to 20% for clients in high-variance markets (e.g., deep tech, quant finance) where wide ranges are normal.

**Open role risk days:**

Default 30 days. Adjust based on the client's average time-to-fill:
- Engineering roles: typical TTF 45–60 days → set to 45
- G&A/Finance roles: typical TTF 30–45 days → set to 30
- Exec/VP roles: typical TTF 60–90 days → set to 60

**Attrition flag:**

Default 2% monthly. Adjust for industry norms:
- Tech: 2% is standard
- Media/Content: 2.5–3% is more typical
- Consulting: 3–4% is expected

```yaml
# Example — 200-person B2B SaaS company
client: acme-software

people_cost_variance:
  amount_threshold_usd: 35000
  pct_threshold: 0.05

compensation:
  out_of_band_pct: 0.12
  open_role_risk_days: 45

headcount:
  attrition_flag_pct: 0.025
```

After calibrating, verify the thresholds produce sensible classifications against the prior period's data before going live.

---

## Step 4 — Update CLAUDE.md with client context

Replace the Lumina-specific sections with client context:

- Company name and entity codes
- Department names and codes
- Headcount size by entity
- FY end date and reporting currency
- Loading factor (if the client has calculated their actual rate)
- Calibrated thresholds (reference the YAML)

Do not commit client-identifying information to the public repo. If the repo is private, this is acceptable.

---

## Step 5 — Set up Claude Projects (one per agent)

Create three new Claude Projects in the client's authorized Claude account:

| Project name | Custom instructions | Knowledge files |
|---|---|---|
| `[Client] — Headcount Forecast` | Paste `agents/headcount-forecast/AGENT.md` | `skills/headcount-analysis/SKILL.md`, `skills/people-cost-forecast/SKILL.md`, `skills/finance-conventions/SKILL.md`, anonymized client dataset |
| `[Client] — Hiring Pipeline` | Paste `agents/hiring-pipeline/AGENT.md` | Same 3 skills + dataset |
| `[Client] — Compensation Analysis` | Paste `agents/compensation-analysis/AGENT.md` | `skills/compensation-benchmarking/SKILL.md`, `skills/headcount-analysis/SKILL.md`, `skills/finance-conventions/SKILL.md`, dataset |

Update the threshold values in each AGENT.md to match the calibrated values in `config/thresholds.yaml` before pasting. The AGENT.md is the agent's working brief — it should reflect the client's configuration, not the Lumina defaults.

**Access control:** The Compensation Analysis Project should be accessible only to HR and the Controller. Confirm who has access to the Claude account before uploading the anonymized dataset.

---

## Step 6 — Test run against a prior period

Before running against the current period, run each agent against the most recently closed period where you already know the findings. This verifies that:

- The dataset loaded correctly
- Thresholds are calibrated appropriately (not too noisy, not too quiet)
- Output format matches the client's expectations
- The Comp Analysis output correctly aggregates to department/level only

Compare the agent output to whatever analysis the client's team produced manually for that period. Every finding the agent surfaces should either match a known issue or be explainable. Any finding that surprises the client's team is worth investigating — it may be a real gap the manual process missed, or it may indicate a data quality issue.

Document the test run findings in `/data/client/test-run-notes.md` (gitignored).

---

## Step 7 — Go-live checklist

Complete before running against live current-period data:

- [ ] Repository is private
- [ ] Client dataset is anonymized (no names in any uploaded file)
- [ ] Thresholds calibrated and verified against prior period
- [ ] AGENT.md custom instructions updated with client thresholds
- [ ] Claude Projects access restricted to authorized users
- [ ] Designated human reviewer identified for each agent's outputs
- [ ] Output distribution list confirmed with HR and Finance
- [ ] Comp Analysis output confirmed as HR-restricted — not distributed to managers
- [ ] Client IT/Security has reviewed `SECURITY.md` and signed off
- [ ] Incident response contacts confirmed (see `SECURITY.md` section 10)

---

## Step 8 — Ongoing operations

After go-live, the monthly operating rhythm is:

1. HRIS admin exports the updated roster and attrition log (typically 2–3 days after month-end)
2. FP&A updates the budget sheet with current period actuals
3. ATS admin exports the updated open pipeline
4. Files are loaded into the anonymized dataset and uploaded to Claude Projects
5. Each agent is run with the standard test prompt
6. Outputs are reviewed by the designated human reviewer
7. Findings are distributed per the access control matrix in `PRIVACY.md`
8. Approved actions are entered into the HRIS by an authorized HR team member

The full cycle from data receipt to distributed outputs typically takes 2–4 hours once the system is calibrated. The client's team retains all decision-making authority; the agents surface findings and draft commentary only.

---

## Phase 2 — MCP connector integration

When the client is ready to eliminate the manual export step:

1. Confirm the HRIS supports MCP connectivity or has an API the MCP adapter can call
2. Configure the connector with read-only service account credentials
3. Test the connector against the anonymized dataset structure to verify field mapping
4. Run a parallel period (one month with manual export, one month with connector) to verify output consistency before switching fully to the live connector

See `SECURITY.md` section 7 for MCP connector security requirements.

