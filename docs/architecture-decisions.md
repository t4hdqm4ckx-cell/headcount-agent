# Architecture Decisions

Why the Headcount & People Cost Agent System is built the way it is. Each decision here was made deliberately — this document explains the reasoning so future builders and clients can evaluate, adapt, or challenge it.

---

## 1. Three independent agents, not one

**Decision:** Three separate agents (Headcount Forecast, Hiring Pipeline, Compensation Analysis) rather than a single monolithic agent.

**Why:** Each agent has a distinct audience, data access level, and output distribution. The Comp Analysis output is HR-restricted (T3). The Headcount Forecast output goes to the CFO and Controller (T2). The Hiring Pipeline output goes to FP&A and hiring managers (T2). Combining them into one agent would either over-restrict outputs (everything becomes T3) or under-restrict them (individual comp data leaks into a broadly distributed report).

Separate agents also fail cleanly. If the compensation benchmarking data is unavailable, the Headcount Forecast and Hiring Pipeline agents can still run. A monolithic agent would halt entirely.

**Trade-off:** Three Projects to set up and three prompts to run. Mitigated by the Orchestrator (Phase 2), which sequences all three from a single prompt.

---

## 2. Agents are independent — they do not invoke each other

**Decision:** None of the three agents calls or depends on another agent's output at runtime.

**Why:** Chained agents create fragile pipelines where one failure cascades. If the Headcount Forecast Agent fails to run, a chained Comp Analysis Agent cannot start. Independence means each agent can run in any order, be re-run independently when data changes, and be deployed to a client without requiring the full suite.

The Headcount Forecast output does provide useful context for the Comp Analysis Agent (e.g., the Content attrition finding suggests the below-band Finance Analyst flag is higher urgency). That context is surfaced by running both agents and reading the outputs together — not by wiring them together at the code level.

**Trade-off:** The Orchestrator (Phase 2) must synthesize findings from three separate output envelopes manually. This is acceptable — synthesis is exactly what an Orchestrator is designed to do.

---

## 3. config.py as the single source of truth

**Decision:** All thresholds, paths, entity codes, and domain constants live in `config.py`, loaded from `config/thresholds.yaml`. No inline constants anywhere else in the codebase.

**Why:** A people cost system gets calibrated per client. The $50K cost variance trigger that works for a 600-person streaming company is wrong for a 50-person startup or a 5,000-person enterprise. If thresholds are scattered across three AGENT.md files and two SKILL.md files, recalibrating for a new client requires finding and updating every instance — and missing one causes inconsistent agent behavior.

With `config.py`, calibration for a new client is: edit `config/thresholds.yaml`, run `python config.py` to verify, commit. Every agent picks up the new thresholds automatically.

**Trade-off:** Agents running in Claude Projects read the AGENT.md, not config.py. The thresholds in AGENT.md must be kept in sync with the YAML manually when calibrating for a new client. This is a known limitation of the Claude Projects surface — mitigated by keeping the threshold values in one place (the YAML) and treating AGENT.md values as documentation of the current config.

---

## 4. Privacy-by-default, not privacy-by-permission

**Decision:** Individual salary data never appears in any output unless the user explicitly requests a T3 restricted workpaper. Aggregation to department and level is the default for all outputs.

**Why:** The failure mode of surfacing individual comp data in the wrong context — a memo forwarded to a manager, a dashboard screenshot shared on Slack — is severe and irreversible. The failure mode of being too cautious (a manager has to ask HR for individual data rather than seeing it in an agent output) is recoverable.

Privacy-by-default also makes the system easier to audit. Every output can be shared with any T2-authorized reviewer without checking whether it accidentally contains T3 data. The restriction is structural, not dependent on reviewer judgment.

**Trade-off:** The Comp Analysis Agent cannot produce the one-page "here is what each person earns and how far they are from their band" view that some HR teams expect. Those teams can get individual data from the HRIS directly — that is not a use case this system is designed to replace.

---

## 5. Fully loaded cost, not base salary

**Decision:** All people cost calculations use fully loaded cost (base × 1.25 loading factor), never base salary alone.

**Why:** When a CFO asks "what did we spend on people in November?", the answer is fully loaded cost. The GL records employer payroll taxes, benefits, and equity — not just base salaries. A model built on base salaries will always understate actual spend by 20–30% and cannot be reconciled to the P&L.

Using fully loaded cost also makes the forecast actionable. When the Headcount Forecast Agent flags Engineering at $220K over budget per month, that is a number the Controller can trace directly to the GL.

**Trade-off:** The loading factor (1.25) is an approximation. Actual loading varies by employee level (equity grants are larger at senior levels), employment type (contractors have no benefits), and jurisdiction (EMEA social contributions differ from US FICA). For a first-pass analysis, 1.25 is directionally correct. For a final close workpaper, the Controller should apply level-specific loading factors. The `config/thresholds.yaml` file supports a `loading_factor` override for clients who have calculated their actual rate.

---

## 6. Read-only agents — no write-back to any system

**Decision:** No agent in this system modifies any source data, HRIS record, or connected system. All agents produce analysis outputs only.

**Why:** An agent that can write back to the HRIS creates an irreversible risk surface. A prompt injection attack (see `SECURITY.md`) or a hallucinated finding could trigger a compensation change, a headcount deletion, or a payroll modification without human review. The damage would be real and potentially unrecoverable.

Read-only agents have a narrow, auditable blast radius. The worst outcome of a bad run is a misleading memo that a human reviewer catches before acting on it.

**Trade-off:** Approved comp adjustments, new hire records, and headcount plan updates must be entered manually into the HRIS by an authorized person. This is not a bug — it is the human-in-the-loop control that makes the system safe to deploy with real compensation data.

---

## 7. Synthetic data for Phase 1

**Decision:** The repository ships with a fully synthetic dataset containing fabricated employees, salaries, and pipeline data. Real client data is gitignored and never committed.

**Why:** A consulting portfolio that requires real employee data to demonstrate cannot be shown to prospects. The synthetic dataset is designed to contain realistic-looking findings (six embedded issues that match what agents are supposed to surface) so that the demo is indistinguishable from a real run in terms of output quality.

Shipping with synthetic data also means the repo can remain public for portfolio purposes without risk of exposing real PII.

**Trade-off:** The synthetic data does not exercise every edge case (partial-month starts, mid-year equity grants, EMEA social cost variations). These are addressed in the client onboarding process when the real dataset is prepared.

---

## 8. Indeed MCP for market benchmarks (Phase 2)

**Decision:** Market compensation benchmarks will be sourced from the Indeed MCP connector rather than a static survey file.

**Why:** Compensation surveys (Radford, Mercer) are expensive, updated annually, and require a subscription. The Indeed MCP provides role-level comp data that is continuously updated from real job postings. For the volume roles in a typical FP&A client engagement (engineers, analysts, managers), Indeed data is directionally accurate and accessible at zero marginal cost.

For C-suite and senior executive benchmarking, Radford/Mercer data remains more appropriate. The `Market_Benchmarks` sheet in the synthetic dataset notes the source for each role category, allowing a hybrid approach.

**Trade-off:** Indeed data reflects posted salaries, not actual paid salaries, and may skew toward companies that post publicly. Senior technical roles at FAANG-tier companies are systematically under-represented. Use Indeed benchmarks as a floor check and directional signal, not as the sole basis for a comp decision.

