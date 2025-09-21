from __future__ import annotations

from pathlib import Path
from typing import Dict

from fpdf import FPDF

from ..models import AnalysisResult
from .firebase import FirebaseStorage


class ReportGenerator:
    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._firebase = FirebaseStorage()

    def create_reports(self, analysis: AnalysisResult) -> Dict[str, Path]:
        summary_path = self._create_pdf(analysis, kind="summary")
        detailed_path = self._create_pdf(analysis, kind="detailed")
        founder_path = self._create_founder_pdf(analysis)

        artifacts = {
            "summary": summary_path,
            "detailed": detailed_path,
            "founder": founder_path,
        }

        if self._firebase.available:
            for label, path in artifacts.items():
                dest = f"reports/{analysis.startup.name}_{label}.pdf"
                self._firebase.upload_file(path, dest)
        return artifacts

    def _create_pdf(self, analysis: AnalysisResult, kind: str) -> Path:
        filename = f"{analysis.startup.name}_{kind}.pdf".replace(" ", "_")
        path = self.output_dir / filename
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        title = f"{analysis.startup.name} - {'Summary' if kind == 'summary' else 'Detailed'} Investment Note"
        pdf.multi_cell(0, 10, title)
        pdf.ln(4)

        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 8, f"Total Score: {analysis.total_score:.2f}")
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, "Strengths")
        pdf.set_font("Helvetica", size=11)
        for item in analysis.strengths:
            pdf.multi_cell(0, 6, f"• {item}")
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, "Risks")
        pdf.set_font("Helvetica", size=11)
        for item in analysis.risks:
            pdf.multi_cell(0, 6, f"• {item}")
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, "Benchmark Comparison")
        pdf.set_font("Helvetica", size=11)
        for key, value in analysis.benchmarks.items():
            pdf.multi_cell(0, 6, f"{key}: {value}")
        pdf.ln(2)

        note = analysis.summary_note if kind == "summary" else analysis.detailed_note
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, "Analyst Narrative")
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, note)

        pdf.output(str(path))
        return path

    def _create_founder_pdf(self, analysis: AnalysisResult) -> Path:
        filename = f"{analysis.startup.name}_founder_profile.pdf".replace(" ", "_")
        path = self.output_dir / filename
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, f"Founder & Team Profile - {analysis.startup.name}")
        pdf.ln(4)

        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, analysis.founder_profile_note)

        pdf.output(str(path))
        return path


_report_generator: ReportGenerator | None = None


def get_report_generator() -> ReportGenerator:
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator
