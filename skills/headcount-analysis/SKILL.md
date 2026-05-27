---
name: headcount-analysis
description: "Use this skill when analyzing headcount data against budget or prior period, calculating attrition rates, identifying departments over or under plan, or producing headcount variance reports. Triggers include phrases like 'analyze headcount', 'headcount vs budget', 'attrition rate', 'headcount bridge', 'who is over plan', 'department headcount variance', or any request to evaluate whether current staffing levels are on track against a hiring plan or budget. Use when a headcount roster, budget, or pipeline file is provided and the task is to identify what has changed, what is off plan, and what action is needed."
---

# Headcount analysis

## Purpose

Headcount analysis answers three questions for every department: how many people do we have, how many did we plan for, and what is driving the difference. It is the starting point for all three headcount agents — the Forecast Agent to project costs, the Pipeline Agent to assess hiring risk, and the Comp Agent to understand the population being reviewed.

## Trigger thresholds

Load `config/thresholds.yaml` for client-specific values. Lumina defaults:

- **People cost variance trigger:** > $50,000 AND > 5% vs budget at the department level. Both conditions must be true.
- **Attrition flag:** monthly attrition rate exceeds 2% of department headcount.
- **Open headcount risk flag:** any open role with a target start date more than 30 days in the past.

## Headcount variance methodology

The core analysis compares three states for each department:

1. **Budget headcount** — what was approved in the annual plan for this period
2. **Actual headcount** — current active employees as of the snapshot date
3. **Prior headcount** — prior month's active employees, for MoM bridge

Variance = actual minus budget. Positive variance means over plan; negative means under plan.

**Cost variance** uses the fully loaded cost rate. Fully loaded cost = base salary × loading factor. The standard loading factor for Lumina is **1.25** (captures employer taxes, benefits, and equity). Do not compute individual fully loaded cost — apply the loading factor at the department level to the average base salary.

Compute: cost variance = (actual HC − budget HC) × avg fully loaded cost per head by department.

## MoM headcount bridge

The bridge explains the movement from prior month to current month:

```
Prior month headcount
+ New hires (start date in current month)
- Departures (last day in current month)
= Current month headcount
```

Source new hires from the current roster (start dates in the period). Source departures from the attrition log. If the bridge does not close — i.e., prior + hires − departures ≠ current — flag the discrepancy as a data quality issue for HR to investigate.

## Attrition rate calculation

Monthly attrition rate = departures in period ÷ average headcount in period.

Average headcount = (opening headcount + closing headcount) ÷ 2.

Annualised rate = monthly rate × 12.

Flag any department where the monthly rate exceeds 2%. A single month above threshold is a watch item; two consecutive months is an investigation item.

Classify departures as **regrettable** (would rehire if possible) or **non-regrettable** (performance exit, mutual separation). Regrettable attrition above 1% monthly warrants escalation to HR and the department head.

## Department-level aggregation rules

All outputs aggregate to department level. Never surface individual employee names, salaries, or comp details in shared reports. Individual data belongs in restricted workpapers with HR access controls.

When producing variance tables:

- Show HC: actual, budget, variance (count and %)
- Show cost: actual, budget, variance ($)
- Sort by absolute cost variance descending
- Flag any row that exceeds the trigger threshold

## Triage classification

Apply these classifications to each department finding:

- **Investigate** — cost variance exceeds both trigger thresholds ($50K AND 5%); requires explanation and proposed action
- **Note** — exceeds one threshold but not both; worth surfacing in the workpaper
- **Watch** — below threshold but trending in a concerning direction (e.g., second consecutive month of overage)
- **Clean** — within threshold and no trend concern

## Output format

### Variance report (xlsx)

Filename: `YYYY-MM_<entity>_HeadcountVariance_v<n>.xlsx`

Tabs:
1. **Summary** — department-level HC and cost variance, triage classification, exceptions count
2. **Bridge** — MoM headcount bridge by department
3. **Attrition** — attrition rate by department, trend, regrettable vs non-regrettable
4. **Exceptions** — flagged items with proposed action
5. **Audit Trail** — sources, timestamp, agent version, reviewer

### Memo (md)

Filename: `YYYY-MM_<entity>_HeadcountVariance_v<n>_memo.md`

Sections: executive summary → department findings → attrition summary → proposed actions → open items → metadata.

## Output envelope

```json
{
  "result": {
    "snapshot_date": "2026-11-30",
    "entity": "LuminaUS",
    "total_actual_hc": 80,
    "total_budget_hc": 75,
    "hc_variance": 5,
    "cost_variance_usd": 280000,
    "departments_over_plan": 1,
    "departments_under_plan": 1,
    "attrition_flags": 1
  },
  "exceptions": []
}
```

## Common pitfalls

- **Don't conflate open roles with under-plan headcount.** An open role means the budget was approved but the seat is not yet filled — it is a hiring timing issue, not a cost saving. The cost of the open role is a budget exposure, not a favorable variance.
- **Don't use end-of-month headcount for attrition denominators.** Use the average of opening and closing headcount to avoid distortion from large hire or departure events.
- **Don't surface individual data.** If you find yourself writing a sentence that identifies a specific person's comp or departure reason by name, stop and aggregate.
- **Partial months matter.** An employee who starts November 15 costs half a month of base salary in November. The budget typically assumes a full month. Note partial-month timing in the bridge commentary.
