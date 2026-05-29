# MCP integration guide

How to connect the close system's agents to live source systems in Phase 2 of a client engagement. Phase 1 uses file drops; Phase 2 replaces the file layer with live MCP connectors. The agent logic does not change between phases.

---

## What is MCP

Model Context Protocol (MCP) is an open standard that lets AI agents connect to external systems — ERPs, databases, communication tools, file storage — via standardized connectors. Instead of reading a CSV exported from NetSuite, the agent calls the NetSuite MCP directly and pulls the trial balance live.

From the agent's perspective, the interface is identical: it asks for data, it receives data. The difference is where the data comes from — a file on disk vs. a live API call.

---

## Phase 1 vs Phase 2

| | Phase 1 (file drops) | Phase 2 (MCP connectors) |
|---|---|---|
| Data source | Excel / CSV files in Google Drive or SharePoint | Live ERP via MCP |
| Setup time | Day 1 — no integration work | Weeks 3–6 of engagement |
| ERP access required | No | Yes — read-only API credentials |
| Data freshness | As of last export | Real-time or near-real-time |
| Agent changes | None | Data access layer only (`agents/<name>/data.py`) |
| Client IT involvement | Minimal | Required for API credential provisioning |

Start every engagement in Phase 1. The agent quality is the same; the only difference is where the data comes from. Move to Phase 2 once the client has seen the output and wants to eliminate the manual export step.

---

## Priority connectors

### Tier 1 — Start here

**Google Drive**
- Purpose: close artifact storage, file drop workflow, prior period rec access
- Connector: native Google Drive MCP (already available in Claude)
- What it unlocks: agents can read TB and sub-ledger files directly from Drive without manual upload; outputs are written back to Drive automatically
- Setup: OAuth connection, read/write access to the close folder

**Gmail**
- Purpose: close communications, exception routing, approval workflows
- Connector: native Gmail MCP (already available in Claude)
- What it unlocks: Orchestrator can send status memos and exception notifications directly; approval responses can be read and acted on
- Setup: OAuth connection, send and read access

**Google Calendar**
- Purpose: close calendar management, BD tracking, deadline reminders
- Connector: native Google Calendar MCP (already available in Claude)
- What it unlocks: Orchestrator can create close calendar events, track BD progress, and send reminders when tasks are at risk
- Setup: OAuth connection, read/write access to the close calendar

### Tier 2 — Add for full workflow

**Microsoft 365 (OneDrive / SharePoint / Outlook)**
- Purpose: same as Google Drive + Gmail for Microsoft-shop clients
- Connector: Microsoft 365 MCP
- What it unlocks: file drop and communication workflow for clients on the Microsoft stack
- Setup: Azure AD app registration, delegated permissions

**Slack**
- Purpose: real-time close status updates, blocker escalations, exception routing to channel owners
- Connector: Slack MCP
- What it unlocks: Orchestrator posts BD status to the close Slack channel; exceptions are routed to the right owner's DM or team channel
- Setup: Slack app with bot token, channel and DM write permissions

### Tier 3 — ERP connectors (Phase 2 core)

**NetSuite**
- Purpose: live TB pull, sub-ledger detail, JE log, period locking
- Connector: NetSuite MCP (Oracle MCP or community connector)
- What it unlocks: eliminates the manual TB export step; agents read directly from the GL; JE approval workflow can write back to NetSuite
- Setup: NetSuite REST API credentials, read access to GL and sub-ledger modules; write access if JE posting approval is in scope
- Typical setup time: 1–2 weeks with client IT involvement

**Sage Intacct**
- Purpose: GL detail, sub-ledger feeds, multi-entity consolidation
- Connector: Sage Intacct MCP (community or custom)
- What it unlocks: multi-entity close with live data pull per entity; IC matching can pull both sides simultaneously
- Setup: Intacct Web Services credentials, company-level API access

**Workday Financials**
- Purpose: journal entries, close tasks, period management
- Connector: Workday MCP (custom or partner connector)
- What it unlocks: JE approval workflow integrates with Workday's existing controls; close tasks tracked in Workday rather than a separate calendar
- Setup: Workday Integration System User, required domain security groups

**QuickBooks Online**
- Purpose: SMB deployments
- Connector: Intuit MCP or QBO REST API
- What it unlocks: full close automation for companies on QBO; lower setup complexity than enterprise ERPs
- Setup: QBO app credentials, accounting scope

---

## How the data access layer works

Each agent has a `data.py` module in its folder (`agents/<name>/data.py`). This module is the only place where data access logic lives. Swapping Phase 1 for Phase 2 means rewriting `data.py` for each agent — the agent's skills, prompts, and output contracts stay identical.

Phase 1 `data.py` (file-based):
```python
def get_trial_balance(period, entity):
    import openpyxl
    wb = openpyxl.load_workbook('/data/synthetic/lumina_close_dataset.xlsx')
    ws = wb['TrialBalance']
    # ... read and return TB data
```

Phase 2 `data.py` (MCP-based):
```python
def get_trial_balance(period, entity):
    # Call NetSuite MCP directly
    # ... authenticate, query GL, return TB data in the same format
```

The agent never knows which phase it is in. It calls `get_trial_balance()` and gets back data in the same format either way.

---

## Data governance considerations

Before connecting any MCP connector to a client system, confirm the following with the client's IT and legal teams:

- **Authentication:** use service accounts or OAuth, not personal credentials
- **Permissions:** read-only by default; write access only for approved actions (JE posting, close task updates) with explicit sign-off
- **Data residency:** confirm that Anthropic's data handling policies meet the client's requirements; review the Anthropic Business Associate Agreement if applicable
- **Audit logging:** confirm that MCP connector calls are logged in the client's system for SOC 2 / SOX compliance purposes
- **Credential rotation:** establish a rotation schedule for API keys and OAuth tokens

---

## Engagement timeline

| Week | Phase 1 activities | Phase 2 activities |
|---|---|---|
| 1 | Set up file drop workflow (Drive/SharePoint), run first demo close against synthetic data | Begin ERP connector scoping with client IT |
| 2 | Run first close cycle against client's actual exported TB and sub-ledgers | Provision API credentials, test connectivity |
| 3 | Iterate agents based on client data patterns | Integrate Tier 1 connectors (Drive, Gmail) |
| 4 | Validate output quality against client's prior close | Integrate ERP connector (read-only TB pull) |
| 5 | Controller sign-off on output quality | End-to-end test: live TB → agents → outputs |
| 6 | Pilot close with live data | Full MCP workflow live; file drops retired |
