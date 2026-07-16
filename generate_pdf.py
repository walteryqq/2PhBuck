from fpdf import FPDF
import os

class SpecPDF(FPDF):
    def header(self):
        # Header banner
        self.set_text_color(100, 116, 139) # slate gray
        self.set_font("Heiti", size=8)
        self.cell(w=self.epw, h=10, text="2KW 两相交错并联 Buck 耦合电感设计规格书", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(226, 232, 240) # light gray line
        self.line(15, 18, 195, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Heiti", size=8)
        self.set_text_color(148, 163, 184)
        # Page number
        self.cell(w=self.epw, h=10, text=f"第 {self.page_no()} 页 / {{nb}}", align="C", new_x="LMARGIN", new_y="NEXT")

def build_pdf():
    txt_path = "DesignDoc/2KW_Coupled_Buck_Specification.txt"
    pdf_path = "DesignDoc/2KW_Coupled_Buck_Specification.pdf"
    
    if not os.path.exists(txt_path):
        print(f"Error: {txt_path} not found.")
        return

    # Initialize PDF
    pdf = SpecPDF()
    pdf.alias_nb_pages()
    
    # Register Chinese Fonts
    font_path = "/System/Library/Fonts/STHeiti Light.ttc"
    pdf.add_font("Heiti", style="", fname=font_path)
    pdf.add_font("HeitiB", style="", fname="/System/Library/Fonts/STHeiti Medium.ttc")
    
    pdf.add_page()
    pdf.set_margins(15, 20, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # Read spec file
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    in_title = True
    
    for line in lines:
        line_strip = line.strip()
        
        # Image insertion check
        if line_strip.startswith("[IMAGE:") and line_strip.endswith("]"):
            img_path = line_strip[7:-1].strip()
            # Resolve path relative to current or DesignDoc folder
            if not os.path.exists(img_path) and os.path.exists(os.path.join("DesignDoc", img_path)):
                img_path = os.path.join("DesignDoc", img_path)
            if os.path.exists(img_path):
                pdf.ln(2)
                pdf.image(img_path, x=(pdf.w - 140)/2, w=140)
                pdf.ln(4)
            continue

        # Skip empty lines
        if not line_strip:
            pdf.ln(3)
            continue
            
        # Skip divider lines
        if line_strip.startswith("===") or line_strip.startswith("---"):
            continue
            
        # Title block handling
        if "规格书" in line_strip and in_title:
            pdf.set_font("HeitiB", size=18)
            pdf.set_text_color(30, 58, 138) # Deep navy blue
            pdf.cell(w=pdf.epw, h=12, text=line_strip, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            continue
            
        if "文档版本:" in line_strip or "发布日期:" in line_strip or "设计状态:" in line_strip:
            if in_title:
                pdf.set_font("Heiti", size=9.5)
                pdf.set_text_color(100, 116, 139) # slate gray
                pdf.cell(w=pdf.epw, h=6, text=line_strip, align="C", new_x="LMARGIN", new_y="NEXT")
                continue
                
        # End title section
        if in_title and not (line_strip.startswith("文档") or line_strip.startswith("发布") or line_strip.startswith("设计")):
            in_title = False
            pdf.ln(8)
            
        # Section Header (lines starting with number like "1.", "2.")
        if any(line_strip.startswith(f"{i}.") for i in range(1, 10)):
            pdf.ln(4)
            pdf.set_font("HeitiB", size=13)
            pdf.set_text_color(37, 99, 235) # Premium royal blue
            pdf.cell(w=pdf.epw, h=10, text=line_strip, new_x="LMARGIN", new_y="NEXT")
            
            # Draw section underline
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            pdf.set_draw_color(37, 99, 235)
            pdf.set_line_width(0.4)
            pdf.line(15, y_start, 195, y_start)
            pdf.ln(3)
            continue
            
        # Bullet points / Bold subsections
        if line_strip.startswith("*"):
            pdf.set_font("HeitiB", size=10)
            pdf.set_text_color(15, 23, 42) # dark slate
            title_text = line_strip.replace("*", "").strip()
            pdf.cell(w=pdf.epw, h=8, text=f"■  {title_text}", new_x="LMARGIN", new_y="NEXT")
            continue
            
        if line_strip.startswith("- "):
            pdf.set_font("Heiti", size=9.5)
            pdf.set_text_color(51, 65, 85) # medium slate
            text = "  • " + line_strip[2:].strip()
            pdf.multi_cell(w=pdf.epw, h=6, text=text, new_x="LMARGIN", new_y="NEXT")
            continue
            
        # Standard Key-Value lines
        if ":" in line_strip or "：" in line_strip:
            delimiter = ":" if ":" in line_strip else "："
            parts = line_strip.split(delimiter, 1)
            key = parts[0].strip()
            val = parts[1].strip()
            
            # Format nicely as table row with explicit widths
            pdf.set_font("Heiti", size=9.5)
            pdf.set_text_color(71, 85, 105) # label gray
            pdf.cell(w=60, h=7, text=f"    {key}:", new_x="RIGHT", new_y="TOP")
            
            pdf.set_font("HeitiB", size=9.5)
            pdf.set_text_color(15, 23, 42) # value dark slate
            pdf.cell(w=pdf.epw - 60, h=7, text=val, new_x="LMARGIN", new_y="NEXT")
            continue
            
        # Paragraph text or explanations
        pdf.set_font("Heiti", size=9.5)
        pdf.set_text_color(51, 65, 85) # medium slate
        pdf.multi_cell(w=pdf.epw, h=6, text=line_strip, new_x="LMARGIN", new_y="NEXT")
        
    pdf.output(pdf_path)
    print(f"PDF successfully generated at: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
