# Headcount & People Cost Agent System

> Multi-agent system for headcount planning, compensation analysis, and people
> cost forecasting. Built as a consulting portfolio piece for CFOs, CHROs, and
> FP&A leaders.

## Architecture

Three agents on a shared layer of Skills and data sources:

| Agent | Role | Primary outputs |
|---|---|---|
| **Headcount Forecast** | Projects people costs by department against budget and prior period | People cost forecast, department variance report |
| **Hiring Pipeline** | Analyzes open roles vs. hiring plan, flags budget risk from open headcount | Pipeline status report, budget exposure summary |
| **Compensation Analysis** | Flags roles where comp is out of band vs. market and internal equity | Comp review memo, out-of-band flag list |

## Demo company

`Lumina Streaming Co.` — same synthetic company as the close system.

- ~600 employees across Engineering, G&A, Sales, Marketing, Content
- Three entities: LuminaUS, LuminaEMEA, LuminaAPAC
- Compensation in USD; EMEA and APAC converted at period-average FX rate
- People costs ~65% of total operating expense base

## Data sources

- Headcount roster (name, role, department, level, start date, salary, entity)
- Open role pipeline (role, department, target start, budgeted comp)
- Budget (headcount count and cost by department by month)
- Market comp data (via Indeed MCP or uploaded benchmark file)

## Materiality thresholds

- People cost variance trigger: > $50,000 AND > 5% vs budget (department level)
- Out-of-band comp flag: > 15% above or below role band midpoint
- Open headcount budget risk flag: any open role with target start > 30 days past

## Output conventions

File naming: `YYYY-MM_<entity>_<artifact>_v<n>.<ext>`
Example: `2026-11_LuminaUS_HeadcountForecast_v1.xlsx`

## Operating rules

- Never display individual employee salaries in shared outputs
- Aggregate to department level for executive reporting
- Individual comp data only in restricted workpapers
- All proposed comp adjustments require HR and Controller approval
