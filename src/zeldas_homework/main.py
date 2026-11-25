from pathlib import Path
from zeldas_homework.agent import english_teacher, build_agent_input
from zeldas_homework.pdf_generator import generate_weekly_pdfs

if __name__ == "__main__":
    skript_mapp = Path(__file__).parent
    pdf_sökväg = skript_mapp / "Homeworkfile" / "Engerskav48.pdf"
    utdata_mapp = Path(r"C:\Users\user\Documents\Zelda_homework\Vecka47")

    payload = build_agent_input(pdf_sökväg)
    result = english_teacher.run_sync(payload)

    generate_weekly_pdfs(result.output, utdata_mapp, week_name="Vecka 48")