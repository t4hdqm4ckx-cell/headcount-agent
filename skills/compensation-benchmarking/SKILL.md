---
name: compensation-benchmarking
description: "Use this skill when comparing employee compensation to internal salary bands or external market benchmarks, identifying out-of-band roles, assessing pay equity, or producing a compensation review memo. Triggers include phrases like 'comp review', 'out of band', 'above band', 'below band', 'market comparison', 'pay equity', 'salary benchmarking', 'comp outliers', or any request to evaluate whether the company is paying competitively or consistently. Use when a headcount roster, comp bands file, or market benchmark file is provided and the task is to identify roles where compensation is inconsistent with policy or market."
---

# Compensation benchmarking

## Purpose

Compensation benchmarking identifies roles where pay is inconsistent with internal policy (the comp band) or external market rates. The output is an exception list that HR and the Controller can act on — not a decision to change compensation, but a flag that a review is warranted.

All compensation data is sensitive. Individual salary information must never appear in shared reports. All findings are aggregated to role category and level, or described in terms of percentage deviation rather than dollar amounts, in any output that leaves the HR team.

## Trigger thresholds

Load `config/thresholds.yaml` for client-specific values. Lumina defaults:

- **Out-of-band flag:** actual base salary is more than 15% above or below the band midpoint for the role and level. Either direction triggers a flag.
- **Market flag:** actual base salary is more than 15% above the market P75 (potentially overpaying) or more than 10% below the market P25 (retention risk).

## Internal band analysis

The comp band defines min, midpoint, and max for each department and level combination. The midpoint is the target; the range represents acceptable variation for tenure, performance, and location.

**Compa-ratio** = actual base ÷ band midpoint. A compa-ratio above 1.15 is above-band. A compa-ratio below 0.85 is below-band. Between 0.85 and 1.15 is in-band.

Steps:

1. Join the headcount roster to the comp bands on department + level.
2. Calculate the compa-ratio for each employee.
3. Flag anyone with compa-ratio outside the 0.85–1.15 range.
4. Aggregate flags to role category and level — never report individual names in shared output.

**Interpreting above-band:**

Above-band employees are typically the result of market counter-offers accepted to retain key talent, acquisitions where target comp didn't normalise, or outdated bands. Above-band is not necessarily wrong, but it requires a documented rationale and regular review.

**Interpreting below-band:**

Below-band employees represent retention risk. Common causes: long-tenured employees whose comp did not keep pace with market, roles reclassified upward without comp adjustment, or new hires brought in below midpoint on a growth plan. Below-band at a junior level is lower risk; below-band at a senior level is a flight risk.

## Market benchmarking

Market benchmarks provide external reference points by role category. The Lumina benchmark source is the Indeed MCP (for volume roles) and Radford/Mercer survey data (for leadership roles), updated quarterly.

Compare each role category to:

- **P25** (25th percentile): below this is below market. Roles here are retention risks.
- **P50** (50th percentile / median): target market rate for in-range talent.
- **P75** (75th percentile): above this suggests above-market pay. Often intentional for critical roles.

Flag: actual base > P75 by more than 15% → potentially overpaying.
Flag: actual base < P25 by more than 10% → below market, retention risk.

## Pay equity lens

When reviewing comp, note any patterns across demographic or role dimensions that suggest systematic bias. This skill does not perform a full pay equity regression — that requires a dedicated statistical analysis with HR. But flag obvious clusters: all employees of a particular type consistently at the bottom of their band, or a single department where the below-band flags concentrate.

Do not draw conclusions — raise the pattern for HR to investigate.

## Privacy rules

These rules are absolute and cannot be overridden:

1. Never include individual names in shared outputs. Use employee ID or role category.
2. Never include individual dollar salaries in shared memos, dashboards, or slides.
3. Individual comp data belongs only in restricted workpapers with HR access controls.
4. Percentage deviations (e.g., "18% below midpoint") are acceptable in restricted workpapers.
5. All proposed comp adjustments require HR sign-off and Controller approval before actioning.

## Output format

### Comp review memo (md)

Filename: `YYYY-MM_<entity>_CompReview_v<n>_memo.md`

This is a **restricted document** — HR access only. Contains: exception summary by department and level, compa-ratio distribution, market positioning summary, proposed actions.

Do not distribute to managers or the broader finance team without HR approval.

Sections: executive summary → in-band summary → above-band exceptions → below-band exceptions → market positioning → proposed actions → open items → metadata.

### Exception list (xlsx)

Filename: `YYYY-MM_<entity>_CompExceptions_v<n>.xlsx` — **HR restricted**

Columns: Emp ID, Department, Level, Role Category, Compa-Ratio, Band Status, Market Position, Flag Type, Proposed Action.

Note: Emp ID only — no names, no dollar amounts in the shareable version.

## Output envelope

```json
{
  "result": {
    "snapshot_date": "2026-11-30",
    "entity": "LuminaUS",
    "total_employees_reviewed": 80,
    "in_band": 77,
    "above_band": 2,
    "below_band": 1,
    "above_market_p75": 0,
    "below_market_p25": 1
  },
  "exceptions": [
    {
      "severity": "medium",
      "category": "above_band",
      "department": "Marketing",
      "level": "L3",
      "role_category": "Marketing Manager",
      "count": 2,
      "avg_compa_ratio": 1.20,
      "proposed_action": "HR to review — above band, rationale required"
    }
  ]
}
```

## Common pitfalls

- **Don't use total comp (base + bonus) for band comparison.** Comp bands are set on base salary. Bonus is variable and comparing total comp to a base band overstates the compa-ratio.
- **Don't flag without context.** An above-band employee who was counter-offered to stay six months ago has a documented rationale. Pull the HR notes before flagging as an exception.
- **Don't conflate band and market.** A role can be in-band but below market (band is out of date) or above-band but in-market (band is conservative). Both need updating.
- **Level accuracy matters.** A misclassified level makes the band comparison meaningless. If a role looks dramatically out-of-band, check whether the level in the system is correct before escalating.
