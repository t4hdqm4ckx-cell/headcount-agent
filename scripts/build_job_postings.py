"""
build_job_postings.py
Generates LinkedIn-style job posting PDFs for all 15 open positions
at Lumina Streaming Co. — November 2026 pipeline.

Outputs:
  job-postings/individual/  — one PDF per role
  job-postings/             — combined All_Open_Positions.pdf
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import KeepTogether
from pypdf import PdfWriter, PdfReader
import io

# ── Brand colours ────────────────────────────────────────────────────────────
NAVY      = HexColor('#1F4E78')
MID_BLUE  = HexColor('#2E75B6')
LIGHT_BLUE= HexColor('#DDEBF7')
GRAY      = HexColor('#F2F2F2')
MID_GRAY  = HexColor('#666666')
DARK_GRAY = HexColor('#333333')
GREEN     = HexColor('#375623')
GREEN_BG  = HexColor('#E2EFDA')

# ── Styles ───────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s['company'] = ParagraphStyle('company',
        fontName='Helvetica-Bold', fontSize=11, textColor=MID_GRAY,
        spaceAfter=2, alignment=TA_LEFT)

    s['role_title'] = ParagraphStyle('role_title',
        fontName='Helvetica-Bold', fontSize=22, textColor=NAVY,
        spaceAfter=6, leading=26)

    s['meta'] = ParagraphStyle('meta',
        fontName='Helvetica', fontSize=10, textColor=MID_GRAY,
        spaceAfter=4, leading=14)

    s['req'] = ParagraphStyle('req',
        fontName='Helvetica', fontSize=9, textColor=MID_GRAY,
        spaceAfter=12)

    s['section_head'] = ParagraphStyle('section_head',
        fontName='Helvetica-Bold', fontSize=12, textColor=NAVY,
        spaceBefore=14, spaceAfter=6)

    s['body'] = ParagraphStyle('body',
        fontName='Helvetica', fontSize=10, textColor=DARK_GRAY,
        spaceAfter=6, leading=15)

    s['bullet'] = ParagraphStyle('bullet',
        fontName='Helvetica', fontSize=10, textColor=DARK_GRAY,
        leftIndent=14, firstLineIndent=-10,
        spaceAfter=4, leading=14)

    s['comp_label'] = ParagraphStyle('comp_label',
        fontName='Helvetica-Bold', fontSize=10, textColor=NAVY)

    s['comp_value'] = ParagraphStyle('comp_value',
        fontName='Helvetica', fontSize=10, textColor=DARK_GRAY)

    s['footer'] = ParagraphStyle('footer',
        fontName='Helvetica', fontSize=8, textColor=MID_GRAY,
        alignment=TA_CENTER, leading=11)

    s['tag'] = ParagraphStyle('tag',
        fontName='Helvetica-Bold', fontSize=9, textColor=NAVY)

    return s

# ── Header band ──────────────────────────────────────────────────────────────
def header_band():
    """Navy top band with company name and tagline."""
    data = [[
        Paragraph('<font color="white"><b>LUMINA STREAMING CO.</b></font>',
                  ParagraphStyle('hdr', fontName='Helvetica-Bold',
                                 fontSize=14, textColor=white)),
        Paragraph('<font color="#DDEBF7">Bringing stories to life, everywhere</font>',
                  ParagraphStyle('sub', fontName='Helvetica',
                                 fontSize=9, textColor=LIGHT_BLUE,
                                 alignment=TA_RIGHT))
    ]]
    t = Table(data, colWidths=[3.5*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (0,-1),  14),
        ('RIGHTPADDING',  (-1,0),(-1,-1), 14),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

# ── Status tag table ─────────────────────────────────────────────────────────
def status_tags(dept, entity, location, work_type, req_id, urgency=None):
    tags = [dept, entity, location, work_type]
    if urgency:
        tags.append(urgency)
    cells = []
    for tag in tags:
        color = LIGHT_BLUE
        tcolor = NAVY
        if tag == urgency and urgency:
            color = HexColor('#FFE699')
            tcolor = HexColor('#7F6000')
        p = Paragraph(f'<b>{tag}</b>',
                      ParagraphStyle('t', fontName='Helvetica-Bold',
                                     fontSize=8.5, textColor=tcolor))
        cells.append(p)

    col_w = 7.0 / len(cells)
    t = Table([cells], colWidths=[col_w*inch]*len(cells))
    bg_list = []
    for i, tag in enumerate(tags):
        c = HexColor('#FFE699') if (tag == urgency and urgency) else LIGHT_BLUE
        bg_list.append(('BACKGROUND', (i,0), (i,0), c))

    t.setStyle(TableStyle([
        *bg_list,
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('ROUNDEDCORNERS', [4]),
    ]))
    return t

# ── Compensation table ───────────────────────────────────────────────────────
def comp_table(rows):
    """rows = list of (label, value) tuples."""
    data = [[Paragraph(f'<b>{r[0]}</b>',
                       ParagraphStyle('cl', fontName='Helvetica-Bold',
                                      fontSize=10, textColor=NAVY)),
             Paragraph(r[1],
                       ParagraphStyle('cv', fontName='Helvetica',
                                      fontSize=10, textColor=DARK_GRAY))]
            for r in rows]
    t = Table(data, colWidths=[2.2*inch, 4.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('LINEBELOW',     (0,0), (-1,-2), 0.5, HexColor('#CCCCCC')),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ]))
    return t

# ── About Lumina block ───────────────────────────────────────────────────────
ABOUT_LUMINA = (
    "Lumina Streaming Co. is a global streaming platform delivering premium "
    "original content, live sports, and an extensive library of films and series "
    "to over 40 million subscribers in 60+ countries. Headquartered in San Jose, "
    "CA, with offices in London, Singapore, and beyond, we combine world-class "
    "storytelling with cutting-edge technology to redefine how audiences experience "
    "entertainment."
)

# ── Role definitions ──────────────────────────────────────────────────────────
ROLES = [
  {
    "req_id": "REQ-101", "entity": "LuminaUS", "dept": "Engineering",
    "level": "L2", "title": "Software Engineer",
    "location": "San Jose, CA (Hybrid)", "type": "Full-Time",
    "urgency": "Urgent — 90 days open",
    "about": (
        "Join our Core Platform team and help build the distributed systems that "
        "power Lumina's streaming experience for millions of viewers. You'll work "
        "across backend services, data pipelines, and APIs that must perform "
        "reliably at global scale."
    ),
    "responsibilities": [
        "Design, build, and maintain backend services in Go and Python",
        "Contribute to architecture discussions and technical design reviews",
        "Write clean, well-tested, production-ready code with appropriate documentation",
        "Participate in on-call rotations and incident response",
        "Collaborate with product managers and designers to ship new features",
        "Identify and address technical debt in existing systems",
    ],
    "requirements": [
        "2+ years of software engineering experience in a production environment",
        "Proficiency in at least one backend language (Go, Python, Java, or Kotlin)",
        "Solid understanding of distributed systems, REST APIs, and microservices",
        "Experience with cloud infrastructure (AWS, GCP, or Azure)",
        "Strong fundamentals in data structures, algorithms, and system design",
        "Collaborative mindset with clear written and verbal communication",
    ],
    "nice_to_haves": [
        "Experience with streaming protocols (HLS, DASH, WebRTC)",
        "Familiarity with Kafka, Flink, or other real-time data platforms",
        "Contributions to open source projects",
        "Experience at a high-growth technology company",
    ],
    "comp": [
        ("Base Salary", "$155,000 — $195,000 USD annually"),
        ("Target Bonus", "10% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $2,000 annual learning budget"),
    ],
  },
  {
    "req_id": "REQ-102", "entity": "LuminaUS", "dept": "Engineering",
    "level": "L3", "title": "Senior Software Engineer",
    "location": "San Jose, CA (Hybrid)", "type": "Full-Time",
    "urgency": "Urgent — 61 days open",
    "about": (
        "We're looking for a Senior Software Engineer to join our Streaming Delivery "
        "team, focused on reducing latency and improving reliability for Lumina's "
        "global CDN and video delivery infrastructure. You'll drive technical "
        "decisions and mentor junior engineers."
    ),
    "responsibilities": [
        "Lead design and implementation of scalable streaming delivery systems",
        "Define engineering standards, conduct code reviews, and mentor L1/L2 engineers",
        "Drive technical decisions for reliability, performance, and security",
        "Partner with infrastructure and DevOps teams on capacity planning",
        "Own complex projects end-to-end from scoping through production launch",
        "Represent Engineering in cross-functional planning discussions",
    ],
    "requirements": [
        "5+ years of software engineering experience, with at least 2 years at senior IC level",
        "Deep expertise in backend systems — Go, Python, or C++ preferred",
        "Experience designing and operating high-availability distributed systems at scale",
        "Strong knowledge of CDN architecture, video streaming, or media delivery",
        "Track record of technical leadership: design docs, code reviews, mentoring",
        "Excellent communication — comfortable in architecture reviews with senior stakeholders",
    ],
    "nice_to_haves": [
        "Experience with video codecs (H.264, H.265, AV1) or adaptive bitrate algorithms",
        "Background in network engineering or low-latency system optimization",
        "Prior experience at a streaming, media, or platform-scale company",
        "Open source contributions or published technical writing",
    ],
    "comp": [
        ("Base Salary", "$195,000 — $240,000 USD annually"),
        ("Target Bonus", "15% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $3,000 annual learning budget · Home office stipend"),
    ],
  },
  {
    "req_id": "REQ-103", "entity": "LuminaUS", "dept": "Engineering",
    "level": "L2", "title": "Software Engineer — ML Platform",
    "location": "San Jose, CA (Hybrid)", "type": "Full-Time",
    "urgency": "Urgent — 46 days open",
    "about": (
        "Lumina's ML Platform team builds the infrastructure that powers "
        "personalized recommendations, content discovery, and audience intelligence "
        "for 40M+ subscribers. You'll help build and scale the ML serving layer, "
        "feature stores, and experimentation platform."
    ),
    "responsibilities": [
        "Build and maintain ML platform infrastructure — model serving, feature stores, pipelines",
        "Develop tooling that enables data scientists to ship models faster and more reliably",
        "Implement A/B testing and experimentation frameworks",
        "Optimize inference performance for real-time recommendation serving",
        "Collaborate closely with Data Science and Product on new ML capabilities",
        "Maintain high engineering standards through code reviews and design documentation",
    ],
    "requirements": [
        "2+ years of software engineering with exposure to ML systems or data infrastructure",
        "Proficiency in Python; familiarity with ML frameworks (TensorFlow, PyTorch, or scikit-learn)",
        "Experience with data pipeline tooling (Spark, Airflow, dbt, or similar)",
        "Solid understanding of software engineering fundamentals and system design",
        "Ability to work across teams and communicate technical concepts clearly",
    ],
    "nice_to_haves": [
        "Experience with feature stores (Feast, Tecton) or model serving frameworks (Triton, TorchServe)",
        "Background in recommendation systems or personalization engines",
        "Familiarity with streaming data platforms (Kafka, Flink)",
        "Graduate degree in Computer Science, Statistics, or related field",
    ],
    "comp": [
        ("Base Salary", "$155,000 — $195,000 USD annually"),
        ("Target Bonus", "10% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $2,000 annual learning budget"),
    ],
  },
  {
    "req_id": "REQ-104", "entity": "LuminaUS", "dept": "Engineering",
    "level": "L4", "title": "Engineering Manager — Security",
    "location": "San Jose, CA (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina is building a dedicated Security Engineering team and we're looking "
        "for a founding Engineering Manager to lead it. You'll hire and develop a "
        "team of security engineers, define the security roadmap, and partner with "
        "Engineering and Infrastructure to embed security across Lumina's platform."
    ),
    "responsibilities": [
        "Build, hire, and develop a high-performing security engineering team of 5-8 engineers",
        "Define and drive Lumina's platform security roadmap — identity, data protection, threat detection",
        "Partner with Engineering leads to embed security practices in the SDLC",
        "Lead the response to security incidents and build post-incident review processes",
        "Own relationships with compliance, legal, and external security auditors",
        "Report security posture and program progress to the CTO and executive team",
    ],
    "requirements": [
        "5+ years of security engineering experience, including 2+ years in an engineering leadership role",
        "Deep technical background in at least one security domain: AppSec, CloudSec, IdentitySec, or InfraSec",
        "Track record of hiring, growing, and retaining strong engineering talent",
        "Experience operating security programs at scale in a cloud-native environment (AWS/GCP/Azure)",
        "Strong communication skills — able to translate technical risk for non-technical executives",
        "Relevant certifications (CISSP, CISM, or equivalent) preferred",
    ],
    "nice_to_haves": [
        "Experience at a consumer platform with 10M+ users or equivalent regulated environment",
        "Background in SOC2, ISO 27001, or GDPR compliance programs",
        "Experience building security tooling or open source security contributions",
        "Prior experience in both startup and enterprise security environments",
    ],
    "comp": [
        ("Base Salary", "$240,000 — $285,000 USD annually"),
        ("Target Bonus", "20% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $3,000 annual learning budget · Executive coaching"),
    ],
  },
  {
    "req_id": "REQ-105", "entity": "LuminaUS", "dept": "Engineering",
    "level": "L3", "title": "Senior Software Engineer — Data Platform",
    "location": "San Jose, CA (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "The Data Platform team at Lumina owns the real-time and batch data "
        "infrastructure that processes billions of events daily — viewing sessions, "
        "user interactions, and content signals. We're looking for a Senior Engineer "
        "to lead key initiatives in our streaming data and analytics platform."
    ),
    "responsibilities": [
        "Lead design and delivery of real-time data pipelines processing billions of daily events",
        "Architect and build scalable data warehouse and lakehouse solutions",
        "Define data engineering best practices, tooling standards, and platform roadmap",
        "Mentor junior data engineers and participate in technical hiring",
        "Partner with Data Science, Analytics, and Product on data platform capabilities",
        "Drive data quality, observability, and SLAs across the platform",
    ],
    "requirements": [
        "5+ years of data or software engineering experience, with 2+ years senior-level",
        "Expert knowledge of distributed data processing (Spark, Flink, or Beam)",
        "Strong SQL and experience with cloud data warehouses (Snowflake, BigQuery, or Redshift)",
        "Experience building and operating real-time streaming pipelines (Kafka, Kinesis)",
        "Track record of technical leadership on complex, high-scale data projects",
    ],
    "nice_to_haves": [
        "Experience with data mesh or data product architecture patterns",
        "Familiarity with dbt, Apache Iceberg, or Delta Lake",
        "Background in streaming media analytics or recommendation data",
        "Published technical writing or conference presentations",
    ],
    "comp": [
        ("Base Salary", "$195,000 — $240,000 USD annually"),
        ("Target Bonus", "15% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $3,000 annual learning budget"),
    ],
  },
  {
    "req_id": "REQ-201", "entity": "LuminaUS", "dept": "Sales",
    "level": "L2", "title": "Account Executive",
    "location": "New York, NY (Hybrid)", "type": "Full-Time",
    "urgency": "Urgent — 45 days open",
    "about": (
        "Lumina's Advertising Sales team partners with brand advertisers and agencies "
        "to connect them with Lumina's premium streaming audience. As an Account "
        "Executive, you'll manage a portfolio of advertising accounts, drive revenue "
        "against quarterly targets, and develop long-term client relationships."
    ),
    "responsibilities": [
        "Manage and grow a portfolio of advertising accounts ($5M–$15M annual book)",
        "Prospect, qualify, and close new advertising partnerships",
        "Develop tailored advertising solutions across Lumina's premium content inventory",
        "Build and maintain senior relationships at client and agency partners",
        "Partner with Ad Operations, Marketing, and Research to deliver client campaigns",
        "Accurately forecast pipeline and revenue in Salesforce on a weekly basis",
    ],
    "requirements": [
        "2+ years of digital advertising sales experience, ideally in streaming, OTT, or CTV",
        "Demonstrated track record of meeting or exceeding revenue quotas",
        "Strong understanding of digital advertising ecosystems (programmatic, direct IO, branded content)",
        "Excellent presentation and communication skills with C-suite audiences",
        "Experience managing full sales cycles from prospecting through close",
        "Proficiency in Salesforce or comparable CRM",
    ],
    "nice_to_haves": [
        "Established relationships with top advertising agencies (Omnicom, WPP, IPG, Publicis)",
        "Experience selling against a premium content or data-driven audience story",
        "Background in branded content or custom sponsorship sales",
        "Familiarity with measurement and attribution tools (iSpot, VideoAmp, Nielsen)",
    ],
    "comp": [
        ("Base Salary", "$72,000 — $95,000 USD annually"),
        ("On-Target Earnings", "$120,000 — $160,000 (60% variable at 100% quota attainment)"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision · 401(k) with 4% match · Unlimited PTO · Sales incentive trips"),
    ],
  },
  {
    "req_id": "REQ-202", "entity": "LuminaUS", "dept": "Sales",
    "level": "L3", "title": "Senior Account Executive — Enterprise",
    "location": "New York, NY (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "We're looking for a Senior Account Executive to own our largest and most "
        "strategic advertising relationships. You'll manage a portfolio of enterprise "
        "accounts, lead complex multi-platform deals, and shape how Lumina's premium "
        "advertising products are positioned in market."
    ),
    "responsibilities": [
        "Own and grow a portfolio of enterprise advertising accounts ($20M+ annual book)",
        "Lead complex, multi-product sales cycles involving custom content, data partnerships, and programmatic",
        "Develop executive-level relationships at client organizations and holding companies",
        "Collaborate with Product and Marketing to shape go-to-market strategy for new ad products",
        "Mentor junior Account Executives and contribute to team knowledge sharing",
        "Represent Lumina at industry events (CES, Upfronts, Cannes Lions)",
    ],
    "requirements": [
        "5+ years of digital advertising sales, with 2+ years managing enterprise accounts",
        "Consistent track record of exceeding $15M+ annual quota targets",
        "Deep expertise in CTV/OTT advertising, branded content, and data-driven targeting",
        "Executive presence — proven ability to build C-suite relationships at Fortune 500 companies",
        "Strong analytical skills — comfortable with media measurement, attribution, and ROI modeling",
    ],
    "nice_to_haves": [
        "Existing book of relationships at top advertising accounts and holding companies",
        "Experience leading joint business planning processes with major advertisers",
        "Background in content partnerships or co-production commercial deals",
        "MBA or equivalent advanced degree",
    ],
    "comp": [
        ("Base Salary", "$92,000 — $118,000 USD annually"),
        ("On-Target Earnings", "$155,000 — $210,000 (50% variable at 100% quota attainment)"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision · 401(k) with 4% match · Unlimited PTO · Sales incentive trips · Presidents Club"),
    ],
  },
  {
    "req_id": "REQ-301", "entity": "LuminaUS", "dept": "G&A",
    "level": "L2", "title": "FP&A Analyst",
    "location": "San Jose, CA (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina's FP&A team is a strategic partner to the business, providing financial "
        "insights and decision support that drive growth. As an FP&A Analyst, you'll "
        "support the annual budgeting process, build financial models, and produce "
        "analysis that influences how Lumina invests in content, technology, and talent."
    ),
    "responsibilities": [
        "Support monthly and quarterly financial close processes — variance analysis, commentary, and reporting",
        "Build and maintain financial models for budgeting, forecasting, and scenario analysis",
        "Produce the monthly management reporting package for the CFO and executive team",
        "Partner with department heads to understand cost drivers and forecast people and operating costs",
        "Analyze content investment performance and return on streaming content spend",
        "Contribute to special projects: strategic planning, M&A support, investor materials",
    ],
    "requirements": [
        "2+ years of FP&A, investment banking, consulting, or related analytical experience",
        "Advanced Excel and financial modeling skills — you build clean, auditable models",
        "Experience with FP&A planning tools (Workday Adaptive Planning, Anaplan, or similar)",
        "Strong written and verbal communication — able to turn data into a clear narrative",
        "High attention to detail with the ability to manage multiple priorities under deadline",
        "Bachelor's degree in Finance, Accounting, Economics, or related field",
    ],
    "nice_to_haves": [
        "Experience at a high-growth technology or media company",
        "Familiarity with streaming or subscription business metrics (LTV, CAC, churn, ARPU)",
        "SQL proficiency for self-service data extraction",
        "CFA candidate or MBA in progress",
    ],
    "comp": [
        ("Base Salary", "$90,000 — $125,000 USD annually"),
        ("Target Bonus", "10% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $2,000 learning budget"),
    ],
  },
  {
    "req_id": "REQ-302", "entity": "LuminaUS", "dept": "G&A",
    "level": "L3", "title": "Senior HR Manager",
    "location": "San Jose, CA (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina is scaling rapidly and we need a Senior HR Manager to be a trusted "
        "business partner to our Engineering and G&A organizations. You'll advise "
        "leaders on organizational design, performance, compensation, and employee "
        "relations while driving the people programs that make Lumina a great place to work."
    ),
    "responsibilities": [
        "Serve as the primary HRBP for Engineering and G&A organizations (~200 employees combined)",
        "Partner with department heads on organizational design, headcount planning, and talent strategy",
        "Lead compensation review cycles — partner with Finance on band calibration and equity adjustments",
        "Manage complex employee relations matters including performance, investigations, and exits",
        "Drive HR programs: engagement surveys, manager effectiveness, career development",
        "Use data and analytics to identify workforce trends and advise on proactive interventions",
    ],
    "requirements": [
        "5+ years of HRBP or HR generalist experience, with 2+ years supporting technology organizations",
        "Track record of influencing senior leaders through data, insight, and interpersonal credibility",
        "Deep knowledge of California employment law and HR compliance requirements",
        "Experience managing compensation processes — band design, market benchmarking, equity cycles",
        "Strong analytical skills — comfortable building and interpreting headcount and comp analytics",
        "Bachelor's degree in HR, Business, or related field; SHRM-CP or PHR preferred",
    ],
    "nice_to_haves": [
        "Experience in high-growth technology, media, or consumer company environments",
        "Background in organizational effectiveness or learning & development",
        "Familiarity with HRIS platforms (Workday, BambooHR, Rippling)",
        "SHRM-SCP, SPHR, or equivalent senior certification",
    ],
    "comp": [
        ("Base Salary", "$145,000 — $180,000 USD annually"),
        ("Target Bonus", "15% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $2,000 learning budget"),
    ],
  },
  {
    "req_id": "REQ-401", "entity": "LuminaUS", "dept": "Marketing",
    "level": "L2", "title": "Marketing Specialist — Performance",
    "location": "San Jose, CA (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina's Performance Marketing team drives subscriber acquisition through "
        "paid digital channels at scale. As a Marketing Specialist, you'll manage "
        "paid social and search campaigns, optimize spend against subscriber CAC "
        "targets, and contribute to the audience strategy that fuels Lumina's growth."
    ),
    "responsibilities": [
        "Manage day-to-day execution of paid social campaigns across Meta, TikTok, and YouTube",
        "Optimize paid search campaigns on Google and Bing for subscriber acquisition efficiency",
        "Monitor CAC, ROAS, and conversion metrics daily — surface anomalies and opportunities",
        "Collaborate with Creative on ad copy and visual asset testing",
        "Build and maintain performance dashboards and weekly reporting for Marketing leadership",
        "Support budget management across channels — pacing, reallocation, and scenario planning",
    ],
    "requirements": [
        "2+ years of performance marketing experience managing paid social and/or search campaigns",
        "Hands-on experience with Meta Ads Manager, Google Ads, and TikTok Ads Manager",
        "Strong analytical skills — comfortable with Excel, Google Sheets, and campaign dashboards",
        "Understanding of attribution models, conversion tracking, and pixel implementation",
        "Detail-oriented with strong project management skills in a fast-moving environment",
    ],
    "nice_to_haves": [
        "Experience marketing a subscription product (streaming, SaaS, or similar)",
        "Familiarity with MMM (media mix modeling) or incrementality testing",
        "SQL proficiency for self-service analytics",
        "Google Ads or Meta Blueprint certifications",
    ],
    "comp": [
        ("Base Salary", "$82,000 — $110,000 USD annually"),
        ("Target Bonus", "10% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $2,000 learning budget"),
    ],
  },
  {
    "req_id": "REQ-501", "entity": "LuminaUS", "dept": "Content",
    "level": "L3", "title": "Senior Content Manager — Original Series",
    "location": "Los Angeles, CA (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina's Original Content team is behind some of the most-watched series "
        "on the platform. We're looking for a Senior Content Manager to manage the "
        "development and production pipeline for original series — from greenlight "
        "through delivery — working closely with showrunners, studios, and distributors."
    ),
    "responsibilities": [
        "Manage the development and production pipeline for 8–12 original series simultaneously",
        "Serve as the primary operational liaison between Lumina and production partners",
        "Track production budgets, schedules, and deliverables against content agreements",
        "Review cuts, provide editorial notes, and ensure content meets Lumina's quality standards",
        "Coordinate across Legal, Marketing, and Distribution for series launches",
        "Build and maintain relationships with showrunners, agents, and production companies",
    ],
    "requirements": [
        "4+ years of experience in scripted content development or production management",
        "Deep knowledge of the television production process from development through post",
        "Strong project management skills — able to track complex, multi-project pipelines",
        "Experience negotiating and managing production agreements with studios and talent",
        "Excellent interpersonal skills — this role requires trusted relationships across the creative community",
    ],
    "nice_to_haves": [
        "Prior experience at a streaming platform, premium cable network, or major studio",
        "International content experience — international co-productions or acquisitions",
        "Background in scripted drama or limited series (Lumina's primary investment area)",
        "Existing relationships in the creative talent community",
    ],
    "comp": [
        ("Base Salary", "$130,000 — $168,000 USD annually"),
        ("Target Bonus", "15% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO · $2,500 learning budget"),
    ],
  },
  {
    "req_id": "REQ-502", "entity": "LuminaUS", "dept": "Content",
    "level": "L2", "title": "Content Associate — Licensing",
    "location": "Los Angeles, CA (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina's Content Licensing team acquires films, series, and specials that "
        "complement our original programming. As a Content Associate, you'll support "
        "the licensing team in identifying acquisition targets, managing deal flow, "
        "and coordinating content delivery from distribution partners."
    ),
    "responsibilities": [
        "Research and evaluate potential content acquisitions — films, series, and library deals",
        "Prepare content analysis and financial summaries for acquisition approval",
        "Coordinate deal administration: tracking term sheets, rights schedules, and delivery milestones",
        "Manage relationships with distribution partners and support contract negotiations",
        "Maintain the licensing pipeline database and produce status reports for leadership",
        "Support special projects: market analysis, competitive tracking, content strategy research",
    ],
    "requirements": [
        "1–2 years of experience in content licensing, business affairs, or media distribution",
        "Strong analytical skills — able to model content valuations and ROI scenarios",
        "Detail-oriented with excellent organization and project management habits",
        "Excellent written communication — able to produce clear deal summaries and briefings",
        "Bachelor's degree in Film, Media, Business, or related field",
    ],
    "nice_to_haves": [
        "Experience at a streaming platform, studio, or content distributor",
        "Familiarity with content rights structures and windowing strategies",
        "International market knowledge — particularly EMEA or APAC content landscapes",
        "Conversational proficiency in a second language",
    ],
    "comp": [
        ("Base Salary", "$78,000 — $105,000 USD annually"),
        ("Target Bonus", "10% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical, dental, vision (100% employer-paid) · 401(k) with 4% match · Unlimited PTO"),
    ],
  },
  {
    "req_id": "REQ-601", "entity": "LuminaEMEA", "dept": "Engineering",
    "level": "L3", "title": "Senior Software Engineer — Backend",
    "location": "London, UK (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina's EMEA Engineering hub in London builds and operates the platform "
        "services that support our European subscriber base. We're looking for a "
        "Senior Backend Engineer to join the team and lead development of core "
        "platform services serving tens of millions of European users."
    ),
    "responsibilities": [
        "Lead development of high-availability backend services powering Lumina's EMEA platform",
        "Design scalable systems for user authentication, content delivery, and personalisation",
        "Conduct code reviews and mentor junior engineers across the EMEA team",
        "Collaborate with US-based platform teams on shared infrastructure and API contracts",
        "Participate in incident response and contribute to SRE practices",
        "Contribute to EMEA platform roadmap planning with Engineering and Product leadership",
    ],
    "requirements": [
        "5+ years of backend engineering experience, with 2+ years at senior level",
        "Strong proficiency in Go, Python, or Java with experience in distributed systems",
        "Experience building and operating microservices at scale in cloud environments",
        "Understanding of GDPR and data residency requirements for European platforms",
        "Excellent communication — comfortable working across time zones with global teams",
    ],
    "nice_to_haves": [
        "Prior experience at a streaming, media, or consumer internet platform",
        "Familiarity with European data regulation (GDPR, DSA, DMA)",
        "Experience with event-driven architectures and messaging platforms",
        "Additional European language proficiency",
    ],
    "comp": [
        ("Base Salary", "£155,000 — £195,000 GBP annually (~$195,000 — $245,000 USD)"),
        ("Target Bonus", "15% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Private medical · Pension (5% employer match) · 28 days annual leave · £2,500 learning budget"),
    ],
  },
  {
    "req_id": "REQ-701", "entity": "LuminaAPAC", "dept": "Engineering",
    "level": "L2", "title": "Software Engineer",
    "location": "Singapore (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina's APAC Engineering team in Singapore supports our rapidly growing "
        "Asia-Pacific subscriber base across 18 markets. We're looking for a Software "
        "Engineer to join the team and contribute to platform development, localisation "
        "infrastructure, and APAC-specific product features."
    ),
    "responsibilities": [
        "Build and maintain backend services powering Lumina's APAC platform",
        "Develop localisation and internationalisation features for APAC markets",
        "Collaborate with APAC Product and Content teams on regional feature development",
        "Contribute to platform reliability and observability across the APAC stack",
        "Work closely with US and EMEA platform teams on shared infrastructure",
        "Participate in on-call rotation for APAC production systems",
    ],
    "requirements": [
        "2+ years of software engineering in a production environment",
        "Proficiency in Python, Go, or Java; experience with cloud infrastructure (AWS)",
        "Solid understanding of REST APIs, microservices, and distributed systems fundamentals",
        "Ability to collaborate effectively across time zones",
        "Strong written and verbal communication in English",
    ],
    "nice_to_haves": [
        "Experience working on products serving Southeast Asian or broader APAC markets",
        "Familiarity with APAC-specific compliance or data residency requirements",
        "Proficiency in a second APAC language (Mandarin, Bahasa, Japanese, Korean)",
        "Experience with streaming or media technology platforms",
    ],
    "comp": [
        ("Base Salary", "SGD 185,000 — SGD 245,000 annually (~$135,000 — $182,000 USD)"),
        ("Target Bonus", "10% of base salary"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical & dental · CPF employer contributions · 21 days annual leave · SGD 2,500 learning budget"),
    ],
  },
  {
    "req_id": "REQ-702", "entity": "LuminaAPAC", "dept": "Sales",
    "level": "L2", "title": "Account Executive — APAC Advertising",
    "location": "Singapore (Hybrid)", "type": "Full-Time",
    "urgency": None,
    "about": (
        "Lumina's APAC Advertising Sales team is growing to match our expanding "
        "subscriber footprint across Southeast Asia, ANZ, and North Asia. As an "
        "Account Executive, you'll develop advertising partnerships with regional "
        "brands and agencies and drive revenue against APAC advertising targets."
    ),
    "responsibilities": [
        "Build and manage a portfolio of advertising accounts across APAC markets",
        "Prospect and develop new advertising relationships with regional brands, agencies, and trading desks",
        "Develop custom advertising solutions across Lumina's premium APAC content inventory",
        "Represent Lumina at key industry events across the region (Advertising Week Asia, Spikes Asia)",
        "Forecast pipeline and revenue in Salesforce; provide weekly updates to Sales leadership",
        "Partner with Ad Operations and Marketing to deliver campaigns and drive renewals",
    ],
    "requirements": [
        "2+ years of digital advertising sales experience in an APAC market",
        "Demonstrated track record of meeting or exceeding revenue targets",
        "Understanding of digital and CTV/OTT advertising ecosystems in APAC",
        "Strong existing relationships with regional advertisers or media agencies",
        "Excellent English communication skills; additional APAC language proficiency a strong plus",
    ],
    "nice_to_haves": [
        "Experience in streaming, OTT, or video advertising sales specifically",
        "Regional market expertise in SEA, ANZ, or Greater China",
        "Familiarity with programmatic advertising and data-driven audience targeting",
        "Existing agency relationships across the APAC holding company landscape",
    ],
    "comp": [
        ("Base Salary", "SGD 95,000 — SGD 125,000 annually (~$70,000 — $93,000 USD)"),
        ("On-Target Earnings", "SGD 160,000 — SGD 210,000 (60% variable at 100% quota)"),
        ("Equity", "RSU grant, 4-year vest with 1-year cliff"),
        ("Benefits", "Medical & dental · CPF employer contributions · 21 days annual leave · Sales incentive trips"),
    ],
  },
]

# ── Build one PDF story for a single role ────────────────────────────────────
def build_story(role, s):
    story = []

    # Header band
    story.append(header_band())
    story.append(Spacer(1, 14))

    # Company line
    story.append(Paragraph("Lumina Streaming Co. is hiring", s['company']))

    # Role title
    story.append(Paragraph(role['title'], s['role_title']))

    # Status tags
    urgency = role.get('urgency')
    story.append(status_tags(
        role['dept'], role['entity'],
        role['location'], role['type'], role['req_id'],
        urgency
    ))
    story.append(Spacer(1, 8))

    # Req ID line
    story.append(Paragraph(
        f"Requisition ID: {role['req_id']}  ·  Level: {role['level']}  ·  Posted: November 2026",
        s['req']
    ))

    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE, spaceAfter=6))

    # About Lumina
    story.append(Paragraph("About Lumina", s['section_head']))
    story.append(Paragraph(ABOUT_LUMINA, s['body']))

    # About the role
    story.append(Paragraph("The Role", s['section_head']))
    story.append(Paragraph(role['about'], s['body']))

    # Responsibilities
    story.append(Paragraph("What You'll Do", s['section_head']))
    for item in role['responsibilities']:
        story.append(Paragraph(f"• {item}", s['bullet']))

    # Requirements
    story.append(Paragraph("What You'll Bring", s['section_head']))
    for item in role['requirements']:
        story.append(Paragraph(f"• {item}", s['bullet']))

    # Nice to haves
    story.append(Paragraph("Nice to Have", s['section_head']))
    for item in role['nice_to_haves']:
        story.append(Paragraph(f"◦ {item}", s['bullet']))

    # Compensation
    story.append(Paragraph("Compensation &amp; Benefits", s['section_head']))
    story.append(comp_table(role['comp']))
    story.append(Spacer(1, 12))

    # Equal opportunity
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#CCCCCC'), spaceAfter=8))
    story.append(Paragraph(
        "Lumina Streaming Co. is an equal opportunity employer. We celebrate diversity "
        "and are committed to creating an inclusive environment for all employees. "
        "All qualified applicants will receive consideration without regard to race, "
        "color, religion, gender, gender identity, sexual orientation, national origin, "
        "disability, or age.",
        s['footer']
    ))
    story.append(Paragraph(
        "To apply, visit lumina.com/careers or search for this role on LinkedIn.",
        s['footer']
    ))

    return story


# ── Generate all PDFs ────────────────────────────────────────────────────────
def generate_pdfs(output_dir):
    os.makedirs(f"{output_dir}/individual", exist_ok=True)
    s = make_styles()
    individual_paths = []

    for role in ROLES:
        slug = role['title'].replace(' ', '-').replace('/', '-').replace('—', '').replace('  ','-')
        filename = f"{role['req_id']}_{slug}.pdf"
        filepath = f"{output_dir}/individual/{filename}"

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=letter,
            leftMargin=0.75*inch, rightMargin=0.75*inch,
            topMargin=0.6*inch, bottomMargin=0.75*inch
        )
        doc.build(build_story(role, s))
        pdf_bytes = buf.getvalue()
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        individual_paths.append(filepath)
        print(f"  ✓  {filename}")

    # Combined PDF
    combined_path = f"{output_dir}/Lumina_All_Open_Positions_Nov2026.pdf"
    writer = PdfWriter()
    for path in individual_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    with open(combined_path, 'wb') as f:
        writer.write(f)
    print(f"\n  ✓  Combined: Lumina_All_Open_Positions_Nov2026.pdf ({len(individual_paths)} roles)")
    return individual_paths, combined_path


if __name__ == "__main__":
    output_dir = "/home/claude/job-postings"
    print(f"Generating {len(ROLES)} job posting PDFs...\n")
    generate_pdfs(output_dir)
    print(f"\nAll PDFs written to {output_dir}/")
