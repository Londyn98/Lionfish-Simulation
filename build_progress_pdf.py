"""
build_progress_pdf.py
Generates the M2 progress report PDF.
"""

import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, PageBreak
)

# ── Colour palette ─────────────────────────────────────────────────────────
OCEAN   = colors.HexColor("#005B96")
LION    = colors.HexColor("#CC5500")
REEF    = colors.HexColor("#22783C")
LGRAY   = colors.HexColor("#F5F5F5")
DGRAY   = colors.HexColor("#3C3C3C")
WHITE   = colors.white

W, H = letter


def build_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("title",
            fontSize=20, textColor=LION, fontName="Helvetica-Bold",
            spaceAfter=4, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle",
            fontSize=12, textColor=OCEAN, fontName="Helvetica-BoldOblique",
            spaceAfter=2, alignment=TA_CENTER),
        "meta": ParagraphStyle("meta",
            fontSize=9, textColor=DGRAY, fontName="Helvetica",
            spaceAfter=10, alignment=TA_CENTER),
        "h1": ParagraphStyle("h1",
            fontSize=13, textColor=OCEAN, fontName="Helvetica-Bold",
            spaceBefore=12, spaceAfter=4, borderPadding=(0,0,2,0)),
        "h2": ParagraphStyle("h2",
            fontSize=11, textColor=DGRAY, fontName="Helvetica-Bold",
            spaceBefore=8, spaceAfter=3),
        "body": ParagraphStyle("body",
            fontSize=10, textColor=DGRAY, fontName="Helvetica",
            leading=15, spaceAfter=6, alignment=TA_JUSTIFY),
        "bullet": ParagraphStyle("bullet",
            fontSize=10, textColor=DGRAY, fontName="Helvetica",
            leading=14, spaceAfter=3, leftIndent=14,
            bulletIndent=4),
        "caption": ParagraphStyle("caption",
            fontSize=8, textColor=colors.HexColor("#666666"),
            fontName="Helvetica-Oblique", spaceAfter=8,
            alignment=TA_CENTER),
        "metric_label": ParagraphStyle("metric_label",
            fontSize=9, textColor=OCEAN, fontName="Helvetica-Bold"),
        "metric_val": ParagraphStyle("metric_val",
            fontSize=16, textColor=LION, fontName="Helvetica-Bold",
            spaceAfter=2),
        "metric_sub": ParagraphStyle("metric_sub",
            fontSize=8, textColor=DGRAY, fontName="Helvetica"),
    }
    return styles


def rule(color=OCEAN, thickness=1.2):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=6, spaceBefore=2)


def section_header(text, styles):
    return [
        Paragraph(text, styles["h1"]),
        rule(OCEAN, 0.8),
    ]


def img(path, width, caption_text, styles):
    elements = []
    if Path(path).exists():
        im = Image(path, width=width, height=width * 0.56)
        im.hAlign = "CENTER"
        elements.append(im)
        elements.append(Paragraph(caption_text, styles["caption"]))
    return elements


def build_pdf(out_path: str = "CS4632_M2_LastName_FirstName.pdf"):
    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=0.85*inch, rightMargin=0.85*inch,
        topMargin=0.85*inch,  bottomMargin=0.85*inch,
    )
    S = build_styles()
    story = []

    # ── PAGE 1 ── Title & Status ─────────────────────────────────────────── #
    story += [
        Spacer(1, 0.1*inch),
        Paragraph("Lionfish Invasion Simulation", S["title"]),
        Paragraph("CS 4632 — Modeling and Simulation | Initial Implementation Report", S["subtitle"]),
        Paragraph(
            "Kennesaw State University &nbsp;|&nbsp; "
            "github.com/Londyn98/Lionfish-Simulation",
            S["meta"]),
        rule(LION, 1.5),
        Spacer(1, 0.1*inch),
    ]

    # ── Metrics summary table ────────────────────────────────────────────── #
    story += section_header("1. Project Status Summary", S)

    story.append(Paragraph(
        "The initial simulation prototype is complete and fully functional. "
        "All core entity classes have been implemented, two primary mathematical "
        "models are integrated and running, the spatial dispersal engine is operational, "
        "and the data collection pipeline exports both CSV and JSON output. "
        "The simulation successfully reproduces the explosive population growth and "
        "reef-wide collapse documented in the empirical lionfish invasion literature.",
        S["body"]))

    # Key metrics from run
    metrics_data = [
        ["Metric", "No Culling (104 wk)", "With Culling (104 wk)"],
        ["Final Lionfish Count",  "22,677",  "21"],
        ["Mean Prey / Zone",      "24.3",    "456.8"],
        ["Spread Radius",         "9.85 cells", "9.2 cells"],
        ["Zones Colonised",       "80 / 80", "14 / 80"],
        ["Zones Collapsed",       "80 (100%)", "0 (0%)"],
        ["Peak Lionfish",         "~22,677", "~21"],
    ]

    tbl = Table(metrics_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), OCEAN),
        ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,0), 9),
        ("BACKGROUND",  (0,1), (-1,-1), LGRAY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,1), (-1,-1), 9),
        ("FONTNAME",    (0,1), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (0,1), (0,-1), DGRAY),
        ("ALIGN",       (1,0), (-1,-1), "CENTER"),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.15*inch))

    # ── Implementation progress ──────────────────────────────────────────── #
    story += section_header("2. Implementation Progress", S)
    story.append(Paragraph("<b>Completed this phase:</b>", S["h2"]))

    completed = [
        "<b>ReefZone entity</b> — 10×8 grid of reef zones with heterogeneous "
        "carrying capacities, prey populations, and a 3-state health machine "
        "(Healthy → Degraded → Collapsed) driven by prey depletion thresholds.",

        "<b>LionfishAgent entity</b> — Individual agents with full lifecycle: "
        "age tracking, sex-based reproduction, Poisson-distributed spawning, "
        "energy-dependent reproduction gating, and stochastic natural mortality.",

        "<b>Model 1 — Extended Lotka-Volterra</b> — Per-zone ODE solver computing "
        "weekly prey logistic growth and lionfish-driven predation loss. Key "
        "adaptation: near-zero delta_L (0.0004/wk) reflecting absence of Atlantic predators.",

        "<b>Model 2 — Reaction-Diffusion Dispersal</b> — Larval dispersal kernel "
        "combining Gaussian distance decay with directional current bias. Larvae "
        "settle stochastically in destination zones based on normalised weights.",

        "<b>DataCollector</b> — Records 8 metrics per step: total lionfish, mean prey, "
        "spread radius, zones colonised, health state counts, depletion rate, and agent "
        "count. Exports CSV and JSON at end of run.",

        "<b>Visualizer</b> — Generates 4 publication-quality plots: population time "
        "series, reef health area chart, spread radius, and dual heatmap (density + "
        "health state).",

        "<b>CLI runner</b> — Parameterised entry point supporting grid size, step "
        "count, culling toggle, culling rate, and random seed for reproducibility.",
    ]
    for item in completed:
        story.append(Paragraph(f"• &nbsp; {item}", S["bullet"]))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph("<b>Remaining for next phase:</b>", S["h2"]))
    remaining = [
        "Parameter calibration against Albins & Schofield empirical spread data",
        "CullingManager scheduling interface (currently inline; needs class extraction)",
        "Sensitivity analysis across alpha, sigma, and survival_rate parameter space",
        "Final write-up and results discussion",
    ]
    for item in remaining:
        story.append(Paragraph(f"• &nbsp; {item}", S["bullet"]))

    story.append(PageBreak())

    # ── PAGE 2 ── Screenshots ───────────────────────────────────────────── #
    story += section_header("3. Simulation Screenshots", S)

    plot_w = 6.2 * inch

    story += img(
        "output/plot_populations.png", plot_w,
        "Figure 1 — Population dynamics over 104 weeks. Lionfish grow exponentially from 5 "
        "to 22,677 as prey collapses from 415 to 24 fish/zone on average.",
        S)

    story += img(
        "output/plot_reef_health.png", plot_w,
        "Figure 2 — Reef health state distribution. All 80 zones transition from Healthy "
        "to Collapsed by week 96 as lionfish density overwhelms carrying capacity.",
        S)

    story.append(PageBreak())

    # ── PAGE 3 ── More screenshots ────────────────────────────────────────── #
    story += section_header("3. Simulation Screenshots (continued)", S)

    story += img(
        "output/plot_spread_radius.png", plot_w,
        "Figure 3 — Spatial spread of the invasion. Lionfish reach the full 9.85-cell grid "
        "radius by week 40 as larval dispersal carries juveniles across all reef zones.",
        S)

    story += img(
        "output/plot_heatmap.png", plot_w,
        "Figure 4 — Grid heatmap at week 103. Left: lionfish density peaks near the "
        "coastal entry point (bottom-left) and radiates outward. "
        "Right: all zones show Collapsed health state (dark red).",
        S)

    story.append(PageBreak())

    # ── PAGE 4 ── Project board + notes ──────────────────────────────────── #
    story += section_header("4. Project Board Snapshot", S)

    story.append(Paragraph(
        "The GitHub Project board tracks all implementation tasks as Issues. "
        "The board URL is: "
        "<link href='https://github.com/Londyn98/Lionfish-Simulation/issues' "
        "color='#005B96'>github.com/Londyn98/Lionfish-Simulation/issues</link>. "
        "Issues are organised into three columns: Backlog, In Progress, and Done.",
        S["body"]))

    story.append(Paragraph(
        "<i>Note: Add a screenshot of your GitHub Project board here. "
        "Go to your repo → Projects tab → take a screenshot showing your issues "
        "and their status columns, then insert the image.</i>",
        S["caption"]))

    story.append(Spacer(1, 0.15*inch))

    # Issues table (stand-in for board screenshot)
    issues = [
        ["#", "Issue / Task", "Status"],
        ["1",  "Create ReefZone entity class with health state machine",  "Done"],
        ["2",  "Create LionfishAgent lifecycle (feed, reproduce, die)",   "Done"],
        ["3",  "Implement Lotka-Volterra ODE solver (Model 1)",           "Done"],
        ["4",  "Implement Reaction-Diffusion dispersal kernel (Model 2)", "Done"],
        ["5",  "Build SimulationModel controller and weekly step loop",   "Done"],
        ["6",  "Implement DataCollector (CSV + JSON export)",             "Done"],
        ["7",  "Build Visualizer (4 chart types)",                        "Done"],
        ["8",  "Implement CLI runner with full parameterisation",         "Done"],
        ["9",  "Add CullingManager as standalone class",                  "In Progress"],
        ["10", "Parameter calibration against empirical data",            "Backlog"],
        ["11", "Sensitivity analysis (alpha, sigma, survival_rate)",      "Backlog"],
        ["12", "Final report and results write-up",                       "Backlog"],
    ]

    done_bg   = colors.HexColor("#E8F5E9")
    prog_bg   = colors.HexColor("#FFF8E1")
    back_bg   = colors.HexColor("#F5F5F5")

    issue_tbl = Table(issues, colWidths=[0.35*inch, 4.5*inch, 1.3*inch])
    style = [
        ("BACKGROUND",  (0,0), (-1,0), OCEAN),
        ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8.5),
        ("ALIGN",       (0,0), (0,-1), "CENTER"),
        ("ALIGN",       (2,0), (2,-1), "CENTER"),
        ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#DDDDDD")),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
    ]
    # Row colour by status
    for i, row in enumerate(issues[1:], start=1):
        status = row[2]
        bg = done_bg if status == "Done" else (prog_bg if status == "In Progress" else back_bg)
        style.append(("BACKGROUND", (0,i), (-1,i), bg))
        if status == "Done":
            style.append(("TEXTCOLOR", (2,i), (2,i), REEF))
            style.append(("FONTNAME",  (2,i), (2,i), "Helvetica-Bold"))
        elif status == "In Progress":
            style.append(("TEXTCOLOR", (2,i), (2,i), colors.HexColor("#E07B00")))
            style.append(("FONTNAME",  (2,i), (2,i), "Helvetica-Bold"))

    issue_tbl.setStyle(TableStyle(style))
    story.append(issue_tbl)
    story.append(Spacer(1, 0.2*inch))

    # ── Status paragraph ────────────────────────────────────────────────── #
    story += section_header("5. Status Summary", S)

    story.append(Paragraph(
        "The simulation prototype is complete and exceeds the initial expectations "
        "set out in the project proposal. Both proposed core models (Lotka-Volterra "
        "and Reaction-Diffusion dispersal) are fully implemented and producing "
        "ecologically meaningful results consistent with the lionfish invasion "
        "literature. The agent-based architecture successfully reproduces the "
        "explosive growth dynamics documented by Albins & Hixon (2008) — lionfish "
        "populations grow from 5 seed individuals to over 22,000 agents within two "
        "simulated years in the no-culling scenario.",
        S["body"]))

    story.append(Paragraph(
        "The culling intervention scenario demonstrates the simulation's practical "
        "utility: periodic removal events (60% removal rate, every 12 weeks) suppress "
        "the final population from 22,677 to just 21 lionfish, keeping all reef zones "
        "in Healthy status and prey populations near carrying capacity. This aligns "
        "with the management thresholds reported by Cote et al. (2013).",
        S["body"]))

    story.append(Paragraph(
        "Remaining work focuses on calibration, sensitivity analysis, and the final "
        "report. The core simulation engine is stable and ready for the analysis phase.",
        S["body"]))

    story += [
        Spacer(1, 0.1*inch),
        rule(LION, 0.8),
        Paragraph(
            "<i>AI Usage Note: Claude (Anthropic) was used to assist with code "
            "formatting, LaTeX layout, and timeline planning. All simulation logic, "
            "model equations, and source research were completed independently.</i>",
            ParagraphStyle("footnote", fontSize=7.5, textColor=colors.HexColor("#888888"),
                           fontName="Helvetica-Oblique", alignment=TA_CENTER)
        ),
    ]

    doc.build(story)
    print(f"PDF written → {out_path}")


if __name__ == "__main__":
    build_pdf("docs/CS4632_M2_LastName_FirstName.pdf")
