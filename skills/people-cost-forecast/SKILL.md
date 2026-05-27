---
name: people-cost-forecast
description: "Use this skill when projecting people costs forward by department, building a headcount-driven cost model, estimating the budget impact of open roles, or producing a people cost forecast. Triggers include phrases like 'people cost forecast', 'project headcount costs', 'what will salaries cost', 'hiring plan impact', 'cost of open roles', 'annualized run rate', 'people cost by department', or any request to estimate future compensation and benefits expense based on current or planned headcount. Use when a headcount roster, open pipeline, and budget are provided and the task is to project what people costs will be over the forecast horizon."
---

# People cost forecasting

## Purpose

A people cost forecast projects salary and benefits expense forward from the current headcount base, layering in planned hires, known departures, and open role timing assumptions. It answers the CFO's most common question about the people line: given what we know today, what will we spend?

People cost is typically 60–70% of total operating expense. A one-month delay in a planned hire or an unexpected departure in a high-cost department can move the quarterly forecast by hundreds of thousands of dollars. The forecast model makes those sensitivities visible before they hit the P&L.

## Fully loaded cost rate

All projections use **fully loaded cost**, not base salary alone.

Fully loaded cost = base salary × loading factor.

The loading factor covers: employer payroll taxes (FICA, FUTA, SUTA), benefits (health, dental, vision, 401k match, life insurance), equity (annualised grant value), and other employer costs (workers comp, professional development).

**Lumina loading factor: 1.25** (calibrate per client in `config/thresholds.yaml`). For a $200K base, fully loaded cost = $250K annually or approximately $20,833 per month.

Do not load bonus in the monthly run rate — accrue bonus separately as a liability. The forecast models base + benefits only.

## Forecasting methodology

### Step 1 — Establish the opening run rate

Opening monthly run rate = sum of fully loaded monthly cost for all active employees as of the forecast start date.

Fully loaded monthly cost per employee = (base salary × 1.25) ÷ 12.

Group by department for the variance analysis. Do not group by individual — department is the lowest meaningful level for a people cost forecast.

### Step 2 — Layer in planned hires from the pipeline

For each open role in the pipeline, estimate the monthly cost impact based on the budgeted base salary and the expected start date.

If the start date has passed and the role is unfilled, use the revised expected start date (or flag as "timing unknown" if no revised date is available). Do not assume a role will start on its original target date if it is already past that date.

Contribution of a new hire in month M = budgeted base × loading factor × (days remaining in month ÷ days in month) ÷ 12. For simplicity, use 0.5 for mid-month starts and 1.0 for first-of-month starts unless exact dates are known.

### Step 3 — Remove known departures

If an employee's last day is known (e.g., from the attrition log or an accepted resignation), remove their cost from the month following their last day. For the current month, prorate: cost = (last day ÷ days in month) × monthly fully loaded cost.

### Step 4 — Apply budget comparison

For each department and each forecast month:

- Budget cost = budget headcount × avg budgeted fully loaded cost per head
- Forecast cost = opening run rate + planned hires − departures
- Forecast vs budget variance = forecast cost − budget cost

Flag any month where the forecast variance exceeds the trigger threshold ($50K AND 5% at department level).

### Step 5 — Annualise and sensitise

Produce a full-year view:

- YTD actuals (from the budget sheet or GL actuals where available)
- Remaining months forecast
- Full-year total = YTD + forecast
- Full-year variance vs full-year budget

Sensitivities to flag:
- If all open roles fill on their current revised target date — base case
- If open roles slip 30 days — downside case (favorable to cost, unfavorable to revenue/growth)
- If attrition continues at current rate — attrition case

## Open headcount treatment

Open headcount is a source of forecast uncertainty. Three approaches depending on data quality:

- **Known start date:** model at the revised expected start date from the pipeline
- **Unknown start date:** model at 90 days from today as a conservative assumption; flag in the exceptions
- **Approved but not yet posted:** model at 120 days; highest uncertainty, flag clearly

Never assume open roles fill immediately. The average time-to-fill for technical roles is 45–90 days from posting. Budget the optimistic case (original target) and flag the realistic case (target + 30 days) separately.

## Output format

### Forecast file (xlsx)

Filename: `YYYY-MM_<entity>_PeopleCostForecast_v<n>.xlsx`

Tabs:
1. **Summary** — monthly people cost: actuals YTD, forecast remaining months, full-year total vs budget
2. **By Department** — department-level detail with variance vs budget by month
3. **Headcount Bridge** — opening HC + hires − departures = closing HC by month
4. **Open Role Timing** — pipeline roles with start date assumptions and cost impact
5. **Sensitivities** — base / 30-day slip / continued attrition scenarios
6. **Audit Trail** — sources, assumptions, agent version, timestamp

### Summary memo (md)

Filename: `YYYY-MM_<entity>_PeopleCostForecast_v<n>_memo.md`

Sections: full-year outlook → key assumptions → department highlights → open role risks → sensitivity summary → recommended actions → metadata.

## Output envelope

```json
{
  "result": {
    "forecast_period": "2026-11 through 2026-12",
    "entity": "LuminaUS",
    "ytd_actual_cost_usd": 85000000,
    "forecast_remaining_usd": 14500000,
    "full_year_total_usd": 99500000,
    "full_year_budget_usd": 96000000,
    "full_year_variance_usd": 3500000,
    "open_role_budget_exposure_usd": 720000
  },
  "exceptions": []
}
```

## Common pitfalls

- **Don't use base salary as the cost figure.** Fully loaded cost is 20–30% higher. A model that uses base salary understates the people cost line and will be wrong when compared to actual GL spend.
- **Don't model open roles at day one.** The single biggest forecast error is assuming all open requisitions fill on their original target date. Use the pipeline's revised dates or apply a slip factor.
- **Don't forget partial months.** A new hire on November 15 costs half a month in November. Ignoring this creates a systematic forecast error that compounds as hiring volume increases.
- **Don't confuse headcount with cost.** Engineering may be 5 over on headcount but the variance to budget in dollars depends on whether the over-plan hires were at the average loaded cost or above it. Always compute the dollar variance, not just the count.
- **Bonus is not in the run rate.** Bonus accrues separately. If the forecast includes bonus, label it clearly and separate it from base + benefits. Mixing them creates a cost line that cannot be reconciled to payroll.
