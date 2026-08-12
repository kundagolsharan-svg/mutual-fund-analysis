"""Generate the final PDF report for the Bluestock mutual fund capstone."""

import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT / "Final_Report.pdf"
CHARTS = {
    "NAV Trends": ROOT / "outputs" / "plots" / "nav_trends_all_schemes.png",
    "AUM by House": ROOT / "outputs" / "plots" / "aum_by_house_year.png",
    "SIP Trends": ROOT / "outputs" / "plots" / "monthly_sip_trend.png",
    "Benchmark Comparison": ROOT / "outputs" / "charts" / "benchmark_comparison.png",
    "Daily Returns": ROOT / "outputs" / "charts" / "daily_returns_histograms.png",
    "Sector Allocation": ROOT / "outputs" / "plots" / "sector_allocation_donut.png",
}


def make_image(path, width=6.5 * inch):
    if path.exists():
        img = Image(str(path), width=width, height=width * 0.6)
        img.hAlign = "CENTER"
        return img
    return None


def build_report():
    doc = SimpleDocTemplate(str(OUTPUT_FILE), pagesize=letter, leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SectionTitle", fontSize=18, leading=22, spaceAfter=12, textColor=colors.HexColor("#0B3D91")))
    styles.add(ParagraphStyle(name="SubHeading", fontSize=14, leading=18, spaceAfter=10, textColor=colors.HexColor("#0B3D91")))
    styles.add(ParagraphStyle(name="CustomBody", fontSize=11, leading=16))
    styles.add(ParagraphStyle(name="SmallText", fontSize=10, leading=14, textColor=colors.gray))

    story = []

    # Title page
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("Bluestock Mutual Fund Performance Capstone", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Final Report", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Prepared by Bluestock Analytics", styles["BodyText"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("August 2026", styles["BodyText"]))
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("This report summarizes the end-to-end mutual fund analysis pipeline, data sources, exploratory findings, performance metrics, dashboard highlights, limitations, and recommendations.", styles["BodyText"]))
    story.append(Spacer(1, 1 * inch))
    story.append(Paragraph("Confidential report for internal Bluestock review.", styles["SmallText"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(PageBreak())

    def add_section(title, content, image_name=None, image_caption=None):
        story.append(Paragraph(title, styles["SectionTitle"]))
        for paragraph in content:
            story.append(Paragraph(paragraph, styles["CustomBody"]))
            story.append(Spacer(1, 0.12 * inch))
        story.append(Spacer(1, 0.2 * inch))
        if image_name and image_caption:
            img = make_image(CHARTS.get(image_name))
            if img:
                story.append(img)
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(image_caption, styles["SmallText"]))
                story.append(Spacer(1, 0.2 * inch))
        story.append(Spacer(1, 0.2 * inch))

    # Executive summary
    add_section(
        "Executive Summary",
        [
            "Bluestock Mutual Fund Performance Capstone uses cleaned mutual fund records, NAV history, benchmark indices, investor transactions, portfolio holdings, and fund metadata to build a reproducible analytics pipeline.",
            "The analysis identifies fund performance through CAGR, Sharpe ratios, Sortino ratios, alpha/beta, drawdowns, and risk-adjusted benchmarking relative to NIFTY50 and NIFTY100 indices.",
            "The report captures exploratory data analysis (EDA) insights, performance patterns, investor behavior, and a dashboard-ready view of the final findings.",
        ],
        image_name="NAV Trends",
        image_caption="Daily NAV trend across all schemes highlights the 2023 bull run and subsequent 2024 corrections."
    )
    story.append(PageBreak())

    # Data sources
    add_section(
        "Data Sources",
        [
            "The primary data sources include raw mutual fund files for fund master, NAV history, AUM by fund house, monthly SIP inflows, category inflows, industry folio counts, scheme performance, investor transactions, portfolio holdings, and benchmark indices.",
            "Data files were ingested from the project's raw data folder and then cleaned, standardized, and stored in a processed folder for analysis.",
            "Benchmark index data includes NIFTY50 and NIFTY100 series used for alpha/beta and tracking error calculations.",
        ]
    )

    # ETL design
    add_section(
        "ETL Design",
        [
            "The ETL pipeline begins with data cleaning, duplicate removal, date parsing, numeric conversion, missing value handling, and NAV validation.",
            "Processed CSV outputs are produced in a structured data/processed folder and loaded into SQLite for exploration and optional dashboard use.",
            "Each script is modular, with dedicated steps for ingestion, cleaning, analytics computation, validation, and output generation so the pipeline remains repeatable and auditable.",
        ],
        image_name="AUM by House",
        image_caption="AUM growth by fund house demonstrates market share concentration and the size of key players."
    )
    story.append(PageBreak())

    # EDA findings
    add_section(
        "EDA Findings",
        [
            "The EDA uncovered a strong increase in monthly SIP inflows that peaked in late 2025, indicating sustained retail investment momentum.",
            "AUM concentration analysis shows a few large fund houses dominate the industry, while fund performance remains correlated across groups of schemes.",
            "Investor demographics are concentrated in middle age segments, while geographic analysis shows transaction amounts are heavily weighted toward a small number of states.",
            "Correlation analysis of NAV returns reveals clusters of highly correlated funds, suggesting common factor exposures and sector/regional overlap.",
        ],
        image_name="SIP Trends",
        image_caption="Monthly SIP inflows and investor behavior demonstrate industry growth and contribution patterns."
    )
    story.append(PageBreak())

    # Performance analysis
    add_section(
        "Performance Analysis",
        [
            "Funds were evaluated using 1-, 3-, and 5-year CAGR, annualized Sharpe and Sortino ratios, maximum drawdown, alpha, beta, and tracking error relative to benchmark indices.",
            "A composite fund score was created from normalized rankings across return, volatility, alpha, expense ratio, and drawdown to highlight top-performing schemes.",
            "Benchmark comparison charts compare the top-ranked funds against NIFTY50 and NIFTY100, showing relative performance stability and benchmark-relative risk.",
        ],
        image_name="Benchmark Comparison",
        image_caption="Top ranked funds plotted against NIFTY benchmarks for the last three years."
    )
    story.append(PageBreak())

    add_section(
        "Dashboard Visuals",
        [
            "The project includes a dashboard-style artifact with charts for NAV trends, AUM concentration, SIP inflows, sector allocation, and risk-vs-return metrics.",
            "Dashboard screenshots capture the core insights and make the analysis accessible to stakeholders and portfolio managers.",
        ],
        image_name="Daily Returns",
        image_caption="Daily return distributions across funds reveal volatility patterns and tail risk exposure."
    )
    story.append(PageBreak())

    # Limitations
    add_section(
        "Limitations",
        [
            "The analysis is constrained by the available raw datasets and may not include the latest market entries or updated fund documents beyond the provided timeframe.",
            "Live NAV data retrieval is optional and depends on external API availability; the core report relies on cleaned historical NAV data included in the repository.",
            "Some metrics, such as investor cohort segmentation, are based on the available transaction fields and would benefit from additional investor profile and behavior attributes.",
        ]
    )
    story.append(PageBreak())

    # Recommendations
    add_section(
        "Recommendations",
        [
            "Use the fund scorecard and benchmark comparison metrics to prioritize funds with high risk-adjusted returns and lower drawdown profiles.",
            "Monitor industry concentration and investor flows in dominant fund houses to assess systemic risk and portfolio allocation bias.",
            "Extend the dashboard with interactive filters for categories, fund houses, risk levels, and time windows to support decision-making in monthly review meetings.",
        ]
    )
    story.append(PageBreak())

    # Closing
    story.append(Paragraph("Conclusion", styles["SectionTitle"]))
    story.append(Paragraph(
        "The Bluestock analysis pipeline delivers a repeatable workflow for mutual fund performance evaluation and stakeholder reporting. Further work can add interactive dashboard deployment, scenario analysis, and live market refresh capability.",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Generated with Python and the Bluestock analytics toolchain.", styles["SmallText"]))

    doc.build(story)


if __name__ == "__main__":
    build_report()
    print(f"Final report saved to: {OUTPUT_FILE}")
