from fpdf import FPDF

class ReportGenerator:
    def __init__(self, report_title):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 12)
        self.report_title = report_title
        self.pdf.cell(200, 10, txt=report_title, ln=True, align="C")

    def add_section(self, section_title, content):
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 10, txt=section_title, ln=True)
        self.pdf.set_font("Arial", "", 12)
        self.pdf.multi_cell(0, 10, txt=content)

    def save_report(self, file_path):
        self.pdf.output(file_path)

# Sử dụng ReportGenerator
if __name__ == "__main__":
    report = ReportGenerator("Báo cáo tiến bộ học tập ngôn ngữ ký hiệu")
    report.add_section("Ký hiệu A", "Độ chính xác trung bình: 95%, Thời gian trung bình: 1.5 giây.")
    report.save_report("data/reports/progress_report.pdf")
