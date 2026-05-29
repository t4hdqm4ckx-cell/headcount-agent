"""
config.py — Headcount & People Cost Agent System
=================================================
Central configuration module. All thresholds, paths, entity mappings,
domain constants, and helper functions live here.

Usage:
    from config import cfg, Paths, Entities, Departments, Levels

Never hardcode a threshold, path, or constant in agent or script code.
Reference this module instead. Change a value here and it changes everywhere.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml

# ─────────────────────────────────────────────────────────────────────────────
# Repository root
# ─────────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.resolve()


# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

class Paths:
    """All file system paths used by agents and scripts."""

    # Config
    THRESHOLDS_YAML     = REPO_ROOT / "config" / "thresholds.yaml"

    # Data
    DATA_DIR            = REPO_ROOT / "data"
    SYNTHETIC_DIR       = DATA_DIR / "synthetic"
    CLIENT_DIR          = DATA_DIR / "client"        # gitignored — real client data only

    # Primary dataset
    SYNTHETIC_DATASET   = SYNTHETIC_DIR / "lumina_headcount_dataset.xlsx"

    # Agents
    AGENTS_DIR          = REPO_ROOT / "agents"
    HEADCOUNT_FORECAST_AGENT    = AGENTS_DIR / "headcount-forecast" / "AGENT.md"
    HIRING_PIPELINE_AGENT       = AGENTS_DIR / "hiring-pipeline" / "AGENT.md"
    COMPENSATION_ANALYSIS_AGENT = AGENTS_DIR / "compensation-analysis" / "AGENT.md"

    # Skills
    SKILLS_DIR          = REPO_ROOT / "skills"
    SKILL_HEADCOUNT     = SKILLS_DIR / "headcount-analysis" / "SKILL.md"
    SKILL_COMP          = SKILLS_DIR / "compensation-benchmarking" / "SKILL.md"
    SKILL_FORECAST      = SKILLS_DIR / "people-cost-forecast" / "SKILL.md"

    # Outputs — organised by period then agent
    OUTPUTS_DIR         = REPO_ROOT / "outputs"

    @staticmethod
    def period_outputs(period: str, agent: str) -> Path:
        """
        Return the output directory for a given period and agent.

        Args:
            period: Period string in YYYY-MM format, e.g. "2026-11"
            agent:  Agent slug: "headcount-forecast" | "hiring-pipeline" | "compensation-analysis"

        Returns:
            Path object; directory is created if it does not exist.

        Example:
            Paths.period_outputs("2026-11", "headcount-forecast")
            # → <repo>/outputs/2026-11/headcount-forecast/
        """
        path = Paths.OUTPUTS_DIR / period / agent
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def output_filename(period: str, entity: str, artifact: str, version: int, ext: str) -> str:
        """
        Build a canonical output filename.

        Convention: YYYY-MM_<Entity>_<Artifact>_v<n>.<ext>

        Args:
            period:   "2026-11"
            entity:   "LuminaUS" | "LuminaEMEA" | "LuminaAPAC"
            artifact: "HeadcountVariance" | "PipelineStatus" | "CompReview" | etc.
            version:  Integer version number
            ext:      File extension without dot: "xlsx" | "md" | "json"

        Example:
            Paths.output_filename("2026-11", "LuminaUS", "HeadcountVariance", 1, "xlsx")
            # → "2026-11_LuminaUS_HeadcountVariance_v1.xlsx"
        """
        return f"{period}_{entity}_{artifact}_v{version}.{ext}"


# ─────────────────────────────────────────────────────────────────────────────
# Dataset sheets
# ─────────────────────────────────────────────────────────────────────────────

class Sheets:
    """Sheet names in lumina_headcount_dataset.xlsx."""
    README          = "README"
    ROSTER          = "Headcount_Roster"
    PRIOR_ROSTER    = "Prior_Roster"
    BUDGET          = "Headcount_Budget"
    PIPELINE        = "Open_Pipeline"
    COMP_BANDS      = "Comp_Bands"
    MARKET_BENCH    = "Market_Benchmarks"
    ATTRITION       = "Attrition_Log"

    ALL = [README, ROSTER, PRIOR_ROSTER, BUDGET, PIPELINE,
           COMP_BANDS, MARKET_BENCH, ATTRITION]


# ─────────────────────────────────────────────────────────────────────────────
# Entities
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Entity:
    code:             str
    name:             str
    currency:         str
    fx_rate_to_usd:   float   # period-average rate; update each period
    approx_headcount: int

class Entities:
    US   = Entity("LuminaUS",   "Lumina US",   "USD", 1.000, 400)
    EMEA = Entity("LuminaEMEA", "Lumina EMEA", "EUR", 1.085, 130)
    APAC = Entity("LuminaAPAC", "Lumina APAC", "SGD", 0.742,  70)

    ALL:  List[Entity] = [US, EMEA, APAC]
    CODES: List[str]   = [e.code for e in ALL]


# ─────────────────────────────────────────────────────────────────────────────
# Departments
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Department:
    code:             str
    name:             str
    approx_us_hc:     int
    cost_center_prefix: str

class Departments:
    ENGINEERING = Department("Engineering", "Engineering",  200, "6100")
    GA          = Department("G&A",         "G&A",           80, "6200")
    SALES       = Department("Sales",        "Sales",         80, "6300")
    MARKETING   = Department("Marketing",    "Marketing",     60, "6400")
    CONTENT     = Department("Content",      "Content",       80, "6500")

    ALL:  List[Department] = [ENGINEERING, GA, SALES, MARKETING, CONTENT]
    CODES: List[str]       = [d.code for d in ALL]


# ─────────────────────────────────────────────────────────────────────────────
# Level taxonomy
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Level:
    code:         str
    description:  str
    example_titles: List[str]

class Levels:
    L1 = Level("L1", "Entry level",              ["Coordinator", "Associate"])
    L2 = Level("L2", "Mid-level IC",             ["Analyst", "Specialist", "Engineer"])
    L3 = Level("L3", "Senior IC / Team lead",    ["Senior Engineer", "Sr Manager", "Lead"])
    L4 = Level("L4", "Manager / Director",       ["Manager", "Director"])
    L5 = Level("L5", "Senior Director / VP",     ["VP", "Senior Director"])
    L6 = Level("L6", "SVP / EVP",                ["SVP", "EVP"])
    L7 = Level("L7", "C-Suite",                  ["CFO", "CTO", "CMO", "CRO", "COO", "CEO"])

    ALL: List[Level] = [L1, L2, L3, L4, L5, L6, L7]
    CODES: List[str] = [lv.code for lv in ALL]


# ─────────────────────────────────────────────────────────────────────────────
# People cost constants
# ─────────────────────────────────────────────────────────────────────────────

class PeopleCost:
    """
    Constants for people cost calculations.

    Loading factor covers: employer payroll taxes (FICA, FUTA, SUTA),
    benefits (health, dental, vision, 401k match), equity (annualised
    grant value), and other employer costs.

    Calibrate LOADING_FACTOR per client in config/thresholds.yaml.
    The value here is the Lumina default.
    """
    LOADING_FACTOR: float = 1.25   # fully loaded cost = base salary × 1.25
    MONTHS_IN_YEAR: int   = 12
    WORKING_DAYS_PER_MONTH: int = 21

    @staticmethod
    def fully_loaded_annual(base_salary: float) -> float:
        """Return fully loaded annual cost from base salary."""
        return base_salary * PeopleCost.LOADING_FACTOR

    @staticmethod
    def fully_loaded_monthly(base_salary: float) -> float:
        """Return fully loaded monthly cost from annual base salary."""
        return (base_salary * PeopleCost.LOADING_FACTOR) / PeopleCost.MONTHS_IN_YEAR

    @staticmethod
    def prorate_monthly(base_salary: float, days_worked: int, days_in_month: int) -> float:
        """
        Return prorated monthly fully loaded cost for a partial month.

        Args:
            base_salary:    Annual base salary
            days_worked:    Number of days the employee worked in the month
            days_in_month:  Total calendar days in the month

        Example:
            # Employee starts Nov 15 (16 days remaining of 30)
            PeopleCost.prorate_monthly(200000, 16, 30)
        """
        monthly = PeopleCost.fully_loaded_monthly(base_salary)
        return monthly * (days_worked / days_in_month)


# ─────────────────────────────────────────────────────────────────────────────
# Materiality thresholds
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Thresholds:
    """
    Materiality thresholds loaded from config/thresholds.yaml.
    Override defaults by editing that file — do not edit values here.
    """
    # People cost variance (both conditions must be true to trigger)
    people_cost_amount_usd:   float = 50_000.0
    people_cost_pct:          float = 0.05          # 5%

    # Compensation band analysis
    comp_out_of_band_pct:     float = 0.15          # 15% above or below midpoint
    comp_compa_ratio_high:    float = 1.15           # above band
    comp_compa_ratio_low:     float = 0.85           # below band

    # Market positioning
    comp_above_market_p75_pct: float = 0.15         # > 15% above P75 = potentially overpaying
    comp_below_market_p25_pct: float = 0.10         # > 10% below P25 = retention risk

    # Hiring pipeline
    open_role_risk_days:      int   = 30            # flag if past target start by > 30 days
    pipeline_stall_days:      int   = 21            # flag if in same stage > 21 days
    hiring_manager_max_reqs:  int   = 3             # flag if > 3 active reqs per manager

    # Attrition
    attrition_flag_monthly:   float = 0.02          # 2% monthly rate
    attrition_regrettable_escalation: float = 0.01  # 1% regrettable attrition — escalate to dept head

    # Budget exposure
    single_role_exposure_usd: float = 150_000.0     # single role annual budget exposure
    dept_exposure_usd:        float = 500_000.0     # department-level exposure


def _load_thresholds() -> Thresholds:
    """
    Load threshold overrides from config/thresholds.yaml.
    Falls back to dataclass defaults if file is missing or keys are absent.
    """
    t = Thresholds()
    yaml_path = Paths.THRESHOLDS_YAML
    if not yaml_path.exists():
        return t
    with open(yaml_path) as f:
        data = yaml.safe_load(f) or {}

    vc = data.get("people_cost_variance", {})
    if "amount_threshold_usd" in vc:
        t.people_cost_amount_usd = float(vc["amount_threshold_usd"])
    if "pct_threshold" in vc:
        t.people_cost_pct = float(vc["pct_threshold"])

    comp = data.get("compensation", {})
    if "out_of_band_pct" in comp:
        t.comp_out_of_band_pct = float(comp["out_of_band_pct"])
        t.comp_compa_ratio_high = 1.0 + t.comp_out_of_band_pct
        t.comp_compa_ratio_low  = 1.0 - t.comp_out_of_band_pct
    if "open_role_risk_days" in comp:
        t.open_role_risk_days = int(comp["open_role_risk_days"])

    hc = data.get("headcount", {})
    if "attrition_flag_pct" in hc:
        t.attrition_flag_monthly = float(hc["attrition_flag_pct"])

    return t


# ─────────────────────────────────────────────────────────────────────────────
# Triage classification
# ─────────────────────────────────────────────────────────────────────────────

class Triage:
    """
    Triage labels used in agent output envelopes and variance reports.
    Applied at department level by the headcount and forecast agents.
    """
    INVESTIGATE = "INVESTIGATE"   # both $ and % thresholds exceeded — requires commentary
    NOTE        = "NOTE"          # one threshold exceeded — surface in workpaper
    WATCH       = "WATCH"         # below threshold but adverse trend across periods
    CLEAN       = "CLEAN"         # within threshold, no trend concern

    @staticmethod
    def classify(amount_variance: float, pct_variance: float, thresholds: Thresholds) -> str:
        """
        Return the triage classification for a department cost variance.

        Args:
            amount_variance: Absolute dollar variance (actual minus budget); may be negative
            pct_variance:    Percentage variance (amount / budget); may be negative
            thresholds:      Thresholds instance

        Returns:
            One of: INVESTIGATE, NOTE, WATCH, CLEAN
        """
        abs_amt = abs(amount_variance)
        abs_pct = abs(pct_variance)
        both    = abs_amt > thresholds.people_cost_amount_usd and abs_pct > thresholds.people_cost_pct
        either  = abs_amt > thresholds.people_cost_amount_usd or  abs_pct > thresholds.people_cost_pct
        if both:
            return Triage.INVESTIGATE
        if either:
            return Triage.NOTE
        return Triage.CLEAN


# ─────────────────────────────────────────────────────────────────────────────
# Data classification
# ─────────────────────────────────────────────────────────────────────────────

class DataTier:
    """
    Data sensitivity tiers. See PRIVACY.md section 2 for full definitions.

    T1 — Public:     dept headcount, org structure, job titles
    T2 — Internal:   dept cost variances, budget vs actual, attrition rates
    T3 — Restricted: individual salaries, compa-ratios, departure reasons
    """
    T1 = "T1_PUBLIC"
    T2 = "T2_INTERNAL"
    T3 = "T3_RESTRICTED"

    # Agent output classifications
    AGENT_OUTPUTS: Dict[str, str] = {
        "headcount-forecast":    T2,
        "hiring-pipeline":       T2,
        "compensation-analysis": T3,   # always restricted regardless of content
    }

    @staticmethod
    def requires_hr_approval(agent: str) -> bool:
        """Return True if the agent's output requires HR approval before distribution."""
        return DataTier.AGENT_OUTPUTS.get(agent) == DataTier.T3


# ─────────────────────────────────────────────────────────────────────────────
# Agent metadata
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AgentMeta:
    slug:           str
    name:           str
    version:        str
    output_folder:  str
    data_tier:      str
    primary_skill:  str
    skills:         List[str]

class Agents:
    HEADCOUNT_FORECAST = AgentMeta(
        slug           = "headcount-forecast",
        name           = "Headcount Forecast Agent",
        version        = "0.1.0",
        output_folder  = "headcount-forecast",
        data_tier      = DataTier.T2,
        primary_skill  = "headcount-analysis",
        skills         = ["headcount-analysis", "people-cost-forecast", "finance-conventions"],
    )
    HIRING_PIPELINE = AgentMeta(
        slug           = "hiring-pipeline",
        name           = "Hiring Pipeline Agent",
        version        = "0.1.0",
        output_folder  = "hiring-pipeline",
        data_tier      = DataTier.T2,
        primary_skill  = "headcount-analysis",
        skills         = ["headcount-analysis", "people-cost-forecast", "finance-conventions"],
    )
    COMPENSATION_ANALYSIS = AgentMeta(
        slug           = "compensation-analysis",
        name           = "Compensation Analysis Agent",
        version        = "0.1.0",
        output_folder  = "compensation-analysis",
        data_tier      = DataTier.T3,
        primary_skill  = "compensation-benchmarking",
        skills         = ["compensation-benchmarking", "headcount-analysis", "finance-conventions"],
    )

    ALL: List[AgentMeta] = [HEADCOUNT_FORECAST, HIRING_PIPELINE, COMPENSATION_ANALYSIS]
    BY_SLUG: Dict[str, AgentMeta] = {a.slug: a for a in ALL}


# ─────────────────────────────────────────────────────────────────────────────
# MCP connectors (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────

class MCPConnectors:
    """
    MCP connector configuration for Phase 2 live data integration.

    Phase 1 (current): all data sourced from synthetic dataset.
    Phase 2: replace with live connector calls.

    Credentials must never be stored here — use environment variables.
    """

    INDEED = {
        "name":    "Indeed",
        "url":     "https://mcp.indeed.com/claude/mcp",
        "phase":   2,
        "purpose": "Live market comp benchmarks by role category",
        "fields":  ["role_category", "location", "p25", "p50", "p75"],
        "enabled": False,   # flip to True when connector is configured
    }

    GOOGLE_DRIVE = {
        "name":    "Google Drive",
        "url":     "https://drivemcp.googleapis.com/mcp/v1",
        "phase":   2,
        "purpose": "Roster, pipeline, and budget file retrieval",
        "enabled": False,
    }

    GMAIL = {
        "name":    "Gmail",
        "url":     "https://gmailmcp.googleapis.com/mcp/v1",
        "phase":   2,
        "purpose": "HR communications and approval workflows",
        "enabled": False,
    }

    # Future HRIS connectors — not yet available
    WORKDAY = {
        "name":    "Workday",
        "phase":   3,
        "purpose": "Live roster, comp, and org data",
        "enabled": False,
        "note":    "Requires Workday Studio integration or third-party MCP adapter",
    }

    BAMBOO_HR = {
        "name":    "BambooHR",
        "phase":   3,
        "purpose": "Live roster, comp, and attrition data",
        "enabled": False,
    }

    ALL = [INDEED, GOOGLE_DRIVE, GMAIL, WORKDAY, BAMBOO_HR]
    ENABLED = [c for c in ALL if c.get("enabled")]


# ─────────────────────────────────────────────────────────────────────────────
# Output envelope helper
# ─────────────────────────────────────────────────────────────────────────────

def build_metadata(
    agent_slug:      str,
    snapshot_date:   str,
    entity:          str,
    source_sheets:   List[str],
    run_timestamp:   Optional[str] = None,
) -> dict:
    """
    Build the standard _metadata block for an agent output envelope.

    Args:
        agent_slug:     e.g. "headcount-forecast"
        snapshot_date:  ISO date string e.g. "2026-11-30"
        entity:         e.g. "LuminaUS"
        source_sheets:  List of sheet names read from the dataset
        run_timestamp:  ISO-8601 datetime string; defaults to now

    Returns:
        dict suitable for the _metadata field of an output envelope
    """
    from datetime import datetime, timezone
    agent = Agents.BY_SLUG.get(agent_slug)
    return {
        "agent":           agent_slug,
        "version":         agent.version if agent else "unknown",
        "run_timestamp":   run_timestamp or datetime.now(timezone.utc).isoformat(),
        "snapshot_date":   snapshot_date,
        "entity":          entity,
        "sources": [
            {"path": str(Paths.SYNTHETIC_DATASET), "sheet": s}
            for s in source_sheets
        ],
        "human_reviewer":  None,
        "data_tier":       agent.data_tier if agent else DataTier.T2,
        "hr_restricted":   DataTier.requires_hr_approval(agent_slug),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Convenience singleton — import cfg and use cfg.thresholds, cfg.paths, etc.
# ─────────────────────────────────────────────────────────────────────────────

class Config:
    """Single importable config object for use in agent scripts."""
    paths        = Paths
    sheets       = Sheets
    entities     = Entities
    departments  = Departments
    levels       = Levels
    people_cost  = PeopleCost
    thresholds   = _load_thresholds()
    triage       = Triage
    data_tier    = DataTier
    agents       = Agents
    mcp          = MCPConnectors

cfg = Config()


# ─────────────────────────────────────────────────────────────────────────────
# Module self-test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Headcount Agent — Config Self-Test ===\n")

    print(f"Repo root:          {REPO_ROOT}")
    print(f"Synthetic dataset:  {cfg.paths.SYNTHETIC_DATASET}")
    print(f"Thresholds YAML:    {cfg.paths.THRESHOLDS_YAML} "
          f"({'found' if cfg.paths.THRESHOLDS_YAML.exists() else 'NOT FOUND — using defaults'})")
    print()

    print("Thresholds:")
    print(f"  People cost trigger:     > ${cfg.thresholds.people_cost_amount_usd:,.0f} "
          f"AND > {cfg.thresholds.people_cost_pct:.0%}")
    print(f"  Comp out-of-band:        > {cfg.thresholds.comp_out_of_band_pct:.0%} from midpoint "
          f"(compa-ratio < {cfg.thresholds.comp_compa_ratio_low} or > {cfg.thresholds.comp_compa_ratio_high})")
    print(f"  Open role risk:          > {cfg.thresholds.open_role_risk_days} days past target start")
    print(f"  Attrition flag:          > {cfg.thresholds.attrition_flag_monthly:.0%} monthly rate")
    print()

    print("People cost helpers:")
    print(f"  $200K base → fully loaded annual:   ${cfg.people_cost.fully_loaded_annual(200_000):,.0f}")
    print(f"  $200K base → fully loaded monthly:  ${cfg.people_cost.fully_loaded_monthly(200_000):,.0f}")
    print(f"  $200K base, 16/30 days:             ${cfg.people_cost.prorate_monthly(200_000, 16, 30):,.0f}")
    print()

    print("Triage classification:")
    print(f"  $280K, 20% variance → {cfg.triage.classify(280_000, 0.20, cfg.thresholds)}")
    print(f"  $45K,  4% variance  → {cfg.triage.classify(45_000,  0.04, cfg.thresholds)}")
    print(f"  $60K,  3% variance  → {cfg.triage.classify(60_000,  0.03, cfg.thresholds)}")
    print()

    print("Agents registered:")
    for a in cfg.agents.ALL:
        print(f"  {a.slug:<28} v{a.version}  {a.data_tier}")
    print()

    print("Enabled MCP connectors:", cfg.mcp.ENABLED or "None (Phase 1 — synthetic data only)")
    print()

    print("Output filename example:")
    print(f"  {cfg.paths.output_filename('2026-11', 'LuminaUS', 'HeadcountVariance', 1, 'xlsx')}")
    print()

    print("Self-test complete.")
