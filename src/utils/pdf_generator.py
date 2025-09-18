"""
PDF Generator Utility for Meeting Minutes Generator.
Day 6 Implementation - Professional PDF export functionality.
"""

import io
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import base64

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)

def validate_pdf_requirements() -> tuple[bool, str]:
    """Validate PDF generation requirements."""
    if not REPORTLAB_AVAILABLE:
        return False, "ReportLab library not installed. Install with: pip install reportlab"

    try:
        # Test basic functionality
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph("Test", styles['Normal'])]
        doc.build(story)
        buffer.close()
        return True, "PDF generation available"
    except Exception as e:
        return False, f"PDF generation test failed: {e}"

def generate_pdf_report(state: Dict[str, Any], formatted_minutes: str, company_info: Optional[Dict[str, str]] = None) -> bytes:
    """
    Generate professional PDF report from meeting minutes.

    Args:
        state: Processing state with meeting data
        formatted_minutes: Formatted meeting minutes
        company_info: Optional company branding information

    Returns:
        PDF data as bytes
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab not available. Install with: pip install reportlab")

    logger.info("Generating PDF report...")

    # Create PDF buffer
    buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title="Meeting Minutes Report"
    )

    # Get styles
    styles = getSampleStyleSheet()

    # Build story (content)
    story = []

    # Title
    story.append(Paragraph("Meeting Minutes Report", styles['Title']))
    story.append(Spacer(1, 20))

    # Meeting metadata
    metadata = state.get("meeting_metadata", {})
    if metadata.get('date'):
        story.append(Paragraph(f"<b>Date:</b> {metadata['date']}", styles['Normal']))

    story.append(Paragraph(f"<b>Meeting Type:</b> {state.get('meeting_type', 'General Meeting')}", styles['Normal']))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d at %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Executive summary
    executive_summary = state.get("executive_summary", "")
    if executive_summary:
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(executive_summary, styles['Normal']))
        story.append(Spacer(1, 15))

    # Action items
    action_items = state.get("action_items", [])
    if action_items:
        story.append(Paragraph("Action Items", styles['Heading2']))

        for i, item in enumerate(action_items, 1):
            story.append(Paragraph(f"<b>{i}. {item.get('task', 'Unknown task')}</b>", styles['Normal']))
            story.append(Paragraph(f"Assignee: {item.get('assignee', 'Unassigned')}", styles['Normal']))
            story.append(Paragraph(f"Deadline: {item.get('deadline', 'Not specified')}", styles['Normal']))
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 15))

    # Full minutes
    if formatted_minutes:
        story.append(Paragraph("Complete Meeting Minutes", styles['Heading2']))
        # Simple text conversion
        lines = formatted_minutes.split('\n')
        for line in lines:
            if line.strip():
                story.append(Paragraph(line.strip(), styles['Normal']))

    # Build PDF
    doc.build(story)

    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()

    logger.info(f"PDF report generated successfully ({len(pdf_data)} bytes)")
    return pdf_data

def test_pdf_generation():
    """Test PDF generation functionality."""
    logger.info("Testing PDF generation...")

    # Check requirements
    available, message = validate_pdf_requirements()
    if not available:
        logger.error(f"PDF generation not available: {message}")
        return False

    try:
        # Create test data
        test_state = {
            "meeting_metadata": {"date": "2024-01-15"},
            "meeting_type": "Test Meeting",
            "executive_summary": "Test summary",
            "action_items": [{"task": "Test task", "assignee": "Test user"}]
        }

        # Generate PDF
        pdf_data = generate_pdf_report(test_state, "# Test Minutes")

        # Validate
        if len(pdf_data) > 1000:
            logger.info(f"PDF generation test successful ({len(pdf_data)} bytes)")
            return True
        else:
            logger.error("PDF generation produced insufficient data")
            return False

    except Exception as e:
        logger.error(f"PDF generation test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    print(f"PDF Generation Test: {'✅ PASS' if success else '❌ FAIL'}")
