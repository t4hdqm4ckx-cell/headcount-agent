# Demo Script — Prospect Walkthrough

**Audience:** CFO, CHRO, VP Finance, FP&A Director
**Duration:** 20–30 minutes live | 5–10 minutes recorded
**Goal:** Show that this system does real analytical work — not just answers questions

---

## Before the call

Open these tabs in advance. Do not navigate during the demo.

1. GitHub repo — `https://github.com/t4hdqm4ckx-cell/headcount-agent`
2. Headcount Forecast Claude Project — prompt pre-typed, not yet sent
3. Compensation Analysis Claude Project — prompt pre-typed, not yet sent
4. `outputs/2026-11/headcount-forecast/` reference output in the repo

Have `config/thresholds.yaml` open in a text editor. You will use it to demonstrate calibration.

---

## Step 1 — Open with the problem (2 minutes)

Start with the repo closed. Lead with the business problem.

*"People costs are typically 60–70% of a company's operating expense base. Most FP&A teams are running their headcount analysis in a spreadsheet that gets emailed around after the close — by the time it reaches the CFO it's two weeks stale, it doesn't include a forward forecast, and the comp review is a completely separate process that HR runs once a year if you're lucky.*

*The specific problems I see at most companies: Engineering hires above the approved plan without anyone catching it until the annual budget review. Open roles that were budgeted in Q1 still haven't filled by Q3 — that's money that looked like a savings but was actually a capacity gap. And compensation outliers — people who are 20% above their band midpoint or below market — that show up only after they've already put in their notice.*

*This system surfaces all three of those before they become problems."*

---

## Step 2 — Show the architecture (3 minutes)

Open the GitHub repo. Scroll the folder structure slowly.

*"Three agents, each with a focused job. The Headcount Forecast Agent projects people costs against the budget and builds the month-over-month bridge. The Hiring Pipeline Agent analyzes open requisitions and quantifies the budget exposure from unfilled seats. The Compensation Analysis Agent flags roles where pay is out of band versus internal ranges and external market data.*

*Everything is version-controlled. Each agent has a definition file — think of it as a job description — and a set of skill files that define the methodology. The config file controls every threshold in the system. Change a number there and every agent picks it up automatically.*

*The synthetic dataset has six embedded findings — real issues I've designed the agents to surface. Let me show you what that looks like in practice."*

---

## Step 3 — Run the Headcount Forecast Agent (8 minutes)

Switch to the Headcount Forecast Claude Project. Show the knowledge files — dataset, three skill files.

*"One Project per agent. The knowledge base has the skill files and the dataset. The custom instructions tell the agent its role, what it can and can't do, and what format to produce."*

Send the prompt:

> "Analyze headcount for LuminaUS, November 2026. Compare actual to budget by department, build the MoM bridge, flag variances above the trigger threshold, and draft the forecast memo."

Let it run. Do not narrate while the output is generating.

Point at two things when it returns:

*"Engineering is five heads over the approved budget. The agent calculated the fully loaded cost of that overage — $220,000 per month, $860,000 for the full year — and it's asking the right question: were these hires approved via a budget exception, or did Engineering just hire without going through the process? That's the question the Controller needs to answer.*

*Content lost three people in November. The agent calculated the attrition rate — 31.6% monthly — flagged it against the 2% threshold, separated the regrettable from the non-regrettable departure, and proposed specific actions: HR retention check-ins with the remaining eight Content employees, prioritizing L3 and above.*

*This is what a senior FP&A analyst produces in three hours. The agent did it in about 30 seconds."*

---

## Step 4 — Show the comp agent (5 minutes)

Switch to the Compensation Analysis Project.

*"The Compensation Analysis Agent has a different access profile. Its outputs are HR-restricted — individual comp data, compa-ratios, band exceptions. Nothing in this output goes to a manager or a department head without explicit HR approval."*

Send the prompt:

> "Run a compensation review for LuminaUS, November 2026. Flag anyone more than 15% above or below their band midpoint. Cross-reference against market benchmarks and the attrition log."

Point at the output when it returns:

*"Two Marketing Managers are 17–22% above their band midpoint. The agent isn't saying they're paid wrong — it's saying HR needs a documented rationale on file. Maybe they were counter-offered to stay. Maybe the band is stale. Either way, it's not documented, and that's an audit finding waiting to happen.*

*One Finance Analyst in G&A is 18% below their band midpoint and also below the market P25. The agent cross-referenced the attrition log and found that a recent G&A departure cited compensation as the reason. That's a retention risk — and it's the kind of thing that doesn't get caught until the person has already started interviewing."*

Then scroll to the bottom and show the output envelope.

*"Every output has this structured block at the bottom. Machine-readable. Package complete, findings count, data tier, whether HR approval is required before distribution. This is what makes it auditable — not just a memo, a traceable artifact."*

---

## Step 5 — Show the calibration story (3 minutes)

Open `config/thresholds.yaml` in the text editor.

*"Every number in this system comes from here. The $50,000 cost variance trigger. The 15% comp band threshold. The 30-day open role flag. These are calibrated for Lumina — a $1.8 billion streaming company with 600 employees.*

*For a 100-person SaaS company, these numbers would be different. Smaller dollar thresholds, tighter attrition flags, probably a lower out-of-band percentage because the comp bands are narrower. I change these numbers here, and every agent across the entire system recalibrates automatically. No touching the agent definitions, no touching the skills."*

---

## Step 6 — Close (2 minutes)

Close the demo browser. Face the prospect.

*"What you just saw is a working system — not a prototype, not a concept. It runs against real data structures, produces outputs your Controller and HR team can act on, and has a complete audit trail. The privacy controls are structural — individual salary data cannot appear in a shared output regardless of how you prompt it.*

*The path from here to your data is a four-to-six week engagement. Week one is data preparation and threshold calibration. Weeks two and three are running the agents against your actual HRIS export and iterating the outputs until they match your Controller's expectations. Week four is go-live and handoff.*

*What does your current headcount review process look like today?"*

That last question is the buying signal question. The answer tells you where the pain is — whether it's the close process, the comp cycle, the hiring plan, or all three.

---

## Objection handling

**"Can this connect to our Workday?"**
*"Phase 1 uses an HRIS export — a clean spreadsheet that your Workday admin can pull in about ten minutes. Phase 2 wires directly to Workday via an MCP connector, which means the analysis runs against live data with no export step. Phase 1 is how we start; Phase 2 is typically the second engagement once the outputs are trusted."*

**"We already have an HRIS with reporting."**
*"HRIS reporting shows you what happened. This system interprets it — it applies your materiality thresholds, builds the variance commentary, flags the comp outliers, and surfaces the retention risks. Your HRIS report tells you there were three Content departures in November. This system tells you the monthly attrition rate is 31.6%, one of those departures was regrettable, and here are the retention check-ins HR should schedule by next Friday."*

**"What happens when the AI gets something wrong?"**
*"Every output routes to a human reviewer before anyone acts on it. The agents propose, humans decide. Nothing gets posted to the HRIS, nothing gets communicated to an employee, nothing changes a budget line without a person approving it. The system also has a structured output envelope on every memo — if the finding looks anomalous, the reviewer opens the source data and checks it. The audit trail is the control."*

**"Is this secure enough for salary data?"**
*"Two things. First, the synthetic data in this demo never touches your real employee data. Second, when we move to real data: individual salaries never appear in any output that leaves the HR team — that's a structural control in the agent, not a setting. The SECURITY.md and PRIVACY.md in the repo document every control in detail. I'd suggest sharing those with your IT security team before the engagement starts."*

