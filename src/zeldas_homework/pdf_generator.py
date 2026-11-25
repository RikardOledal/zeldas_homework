import random
import re
from pathlib import Path
from fpdf import FPDF
from zeldas_homework.data_model import Homework_List


def _create_pdf(title: str, subtitle: str) -> FPDF:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Använder Windows inbyggda Arial för fullt stöd för å, ä, ö och apostrofer
    pdf.add_font("ArialUni", "", r"C:\Windows\Fonts\arial.ttf")
    pdf.add_font("ArialUni", "B", r"C:\Windows\Fonts\arialbd.ttf")

    pdf.set_font("ArialUni", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUni", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, subtitle, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)
    return pdf


def _section_header(pdf: FPDF, text: str):
    pdf.ln(4)
    pdf.set_font("ArialUni", "B", 12)
    pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("ArialUni", "", 11)
    pdf.ln(2)


def _add_grammar(pdf: FPDF, grammar: list):
    if not grammar:
        return
    _section_header(pdf, "Veckans grammatik")
    for g in grammar:
        line = f"{g.english} = {g.swedish}" if g.english else g.swedish
        pdf.multi_cell(0, 6, f"• {line}", new_x="LMARGIN", new_y="NEXT")


def _make_cloze(sentence: str) -> str:
    """Byter ut ca 35% av de lite längre orden i en engelsk mening mot luckor."""
    words = sentence.split()
    candidates = [i for i, w in enumerate(words) if len(re.sub(r"[^a-zA-Z]", "", w)) >= 3]
    num_blanks = max(1, round(len(candidates) * 0.35))
    blank_indices = set(random.sample(candidates, min(num_blanks, len(candidates))))

    result = []
    for i, w in enumerate(words):
        if i in blank_indices:
            punct = w[-1] if w[-1] in ".,!?" else ""
            result.append("__________" + punct)
        else:
            result.append(w)
    return " ".join(result)


def generate_weekly_pdfs(homework: Homework_List, output_dir: Path, week_name: str = "Veckans läxa"):
    output_dir.mkdir(parents=True, exist_ok=True)

    words = [item for item in homework.homework_items if item.kind == "Words"]
    sentences = [item for item in homework.homework_items if item.kind == "Sentences"]
    grammar = [item for item in homework.homework_items if item.kind == "Grammar"]

    # --- DAG 1: Dra linje (Para ihop) ---
    pdf1 = _create_pdf(f"{week_name} - Dag 1: Para ihop", "Dra en linje mellan engelska och svenska.")
    for label, group in [("Ord", words), ("Meningar", sentences)]:
        if not group:
            continue
        if label == "Meningar" and words:
            pdf1.add_page()
        _section_header(pdf1, label)
        eng_list = [x.english for x in group]
        swe_list = [x.swedish for x in group]
        random.shuffle(eng_list)
        random.shuffle(swe_list)

        for eng, swe in zip(eng_list, swe_list):
            y_start = pdf1.get_y()
            pdf1.set_xy(10, y_start)
            pdf1.multi_cell(75, 7, f"{eng}  •", align="L")
            y_left = pdf1.get_y()

            pdf1.set_xy(115, y_start)
            pdf1.multi_cell(85, 7, f"•  {swe}", align="L")
            y_right = pdf1.get_y()

            pdf1.set_y(max(y_left, y_right) + 3)

    _add_grammar(pdf1, grammar)
    pdf1.output(output_dir / "Dag1_Para_ihop.pdf")

    # --- DAG 2: Engelska -> Svenska ---
    pdf2 = _create_pdf(f"{week_name} - Dag 2: Engelska till Svenska", "Översätt orden och meningarna till svenska.")
    for label, group in [("Ord", words), ("Meningar", sentences)]:
        if not group:
            continue
        if label == "Meningar" and words:
            pdf2.add_page()
        _section_header(pdf2, label)
        shuffled = random.sample(group, len(group))
        for item in shuffled:
            if label == "Ord":
                pdf2.cell(80, 9, item.english)
                pdf2.cell(0, 9, "________________________________________", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf2.multi_cell(0, 7, item.english, new_x="LMARGIN", new_y="NEXT")
                pdf2.cell(0, 9, "_______________________________________________________________________", new_x="LMARGIN", new_y="NEXT")
                pdf2.ln(2)

    _add_grammar(pdf2, grammar)
    pdf2.output(output_dir / "Dag2_Engelska_till_Svenska.pdf")

    # --- DAG 3: Svenska -> Engelska (Ord) + Lucktext (Meningar) ---
    pdf3 = _create_pdf(f"{week_name} - Dag 3: Översätt & Fyll i luckor", "Översätt orden till engelska och fyll i de saknade orden i meningarna.")
    if words:
        _section_header(pdf3, "Ord (skriv på engelska)")
        for item in random.sample(words, len(words)):
            pdf3.cell(80, 9, item.swedish)
            pdf3.cell(0, 9, "________________________________________", new_x="LMARGIN", new_y="NEXT")
    if sentences:
        if words:
            pdf3.add_page()
        _section_header(pdf3, "Meningar (fyll i de saknade engelska orden)")
        for item in random.sample(sentences, len(sentences)):
            pdf3.set_font("ArialUni", "", 10)
            pdf3.set_text_color(90, 90, 90)
            pdf3.multi_cell(0, 6, item.swedish, new_x="LMARGIN", new_y="NEXT")
            pdf3.set_text_color(0, 0, 0)
            pdf3.set_font("ArialUni", "", 11)
            pdf3.multi_cell(0, 8, _make_cloze(item.english), new_x="LMARGIN", new_y="NEXT")
            pdf3.ln(3)

    _add_grammar(pdf3, grammar)
    pdf3.output(output_dir / "Dag3_Ord_och_Lucktext.pdf")

    # --- DAG 4: Svenska -> Engelska (Helt prov) ---
    pdf4 = _create_pdf(f"{week_name} - Dag 4: Svenska till Engelska", "Skriv orden och meningarna på engelska.")
    for label, group in [("Ord", words), ("Meningar", sentences)]:
        if not group:
            continue
        if label == "Meningar" and words:
            pdf4.add_page()
        _section_header(pdf4, label)
        shuffled = random.sample(group, len(group))
        for item in shuffled:
            if label == "Ord":
                pdf4.cell(80, 9, item.swedish)
                pdf4.cell(0, 9, "________________________________________", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf4.multi_cell(0, 7, item.swedish, new_x="LMARGIN", new_y="NEXT")
                pdf4.cell(0, 9, "_______________________________________________________________________", new_x="LMARGIN", new_y="NEXT")
                pdf4.ln(2)

    _add_grammar(pdf4, grammar)
    pdf4.output(output_dir / "Dag4_Svenska_till_Engelska.pdf")

    print(f"✅ Skapade 4 övnings-PDF:er i {output_dir}")