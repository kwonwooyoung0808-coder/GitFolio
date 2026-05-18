from docx import Document


def generate_docx(report: dict, output_path) -> str:
    document = Document()
    document.add_heading(report.get("project_name", "GitFolio Report"), level=1)
    document.add_paragraph(report.get("repo", {}).get("full_name", ""))
    document.add_paragraph(report.get("repo", {}).get("description", ""))

    sections = [
        ("Development Period", report.get("period", "")),
        ("Team Scale", report.get("scale", "")),
        ("Role", report.get("role", "")),
        ("Tech Stack", ", ".join(report.get("tech_stack", []))),
        ("Outcome and Learnings", report.get("outcome", "")),
    ]
    for title, value in sections:
        document.add_heading(title, level=2)
        document.add_paragraph(value)

    document.add_heading("Key Implementation", level=2)
    for item in report.get("implementation", []):
        document.add_paragraph(item, style="List Bullet")

    document.save(str(output_path))
    return str(output_path)
