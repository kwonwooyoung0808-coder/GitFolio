from app.services.report.formatter import report_to_html


def generate_pdf(report: dict, output_path) -> str:
    from weasyprint import HTML

    html = report_to_html(report)
    HTML(string=html).write_pdf(str(output_path))
    return str(output_path)
