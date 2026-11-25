from pydantic_ai import Agent, BinaryContent
from zeldas_homework.data_model import Homework_List
from zeldas_homework.model import nvidia_model
from pathlib import Path
from pypdf import PdfReader
import pymupdf

english_teacher = Agent(
    model=nvidia_model(),
    instructions=(
        "You are a precise data parser for a Swedish student's English homework. "
        "You will receive raw, messy text extracted from a PDF containing vocabulary words, "
        "example sentences/phrases, and grammar rules.\n\n"
        "Follow these rules strictly:\n"
        "1. Extract every single word pair, sentence pair, and grammar item.\n"
        "2. Assign a sequential 'index' starting at 1 (1, 2, 3...) across the entire list, "
        "even if the original text restarts numbering.\n"
        "3. Classify 'kind' strictly as:\n"
        "   - 'Words': single words or short expressions.\n"
        "   - 'Sentences': full sentences or phrases.\n"
        "   - 'Grammar': grammar explanations, verb conjugations, or rules.\n"
        "4. Fix broken line wraps and remove stray formatting characters like '|' or numbering.\n"
        "5. For 'Grammar' items: if it's a translation pair (e.g. 'I am = Jag är'), put English in 'english' "
        "and Swedish in 'swedish'. If it's a general rule written only in Swedish, put the rule in 'swedish' "
        "and leave 'english' as an empty string ''."
    ),        
    output_type=Homework_List
)

def build_agent_input(pdf_path: Path):
    reader = PdfReader(pdf_path)
    raw_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    # Har PDF:en ett riktigt textlager -> skicka ren text
    if len(raw_text) > 50:
        print("📄 Läste som text-PDF")
        return raw_text

    # Annars -> rendera sidorna till bilder för Vision-modellen
    print("🖼️ Ingen text hittad, skickar som bilder")
    with pymupdf.open(pdf_path) as doc:
        images = [
            BinaryContent(data=page.get_pixmap(dpi=150).tobytes("png"), media_type="image/png")
            for page in doc
        ]

    return [
        "Extract all vocabulary words, sentences, and grammar rules from these homework pages.",
        *images,
    ]

if __name__ == "__main__":
    HOMEWORK_PATH = Path(__file__).parent / "Homeworkfile"
    FILE_PATH = HOMEWORK_PATH / "Engerskav47.pdf"
    test_text = build_agent_input(FILE_PATH)
    result = english_teacher.run_sync(test_text)
    
    for item in result.output.homework_items:
        print(item)