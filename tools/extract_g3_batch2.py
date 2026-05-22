"""
extract_g3_batch2.py — 중3 2차 교과서 PDF (5~8과) 텍스트 추출
"""
import fitz  # PyMuPDF
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"C:\Users\chenc\Downloads\작업물\중3\2차")

TEXTBOOK_FOLDERS = {
    "중3 동아 이병민 - 복사본": "donga-lee-15",
    "중3 동아 윤정미 - 복사본": "donga-yoon-15",
    "중3 능률 김성곤 - 복사본": "neungyul-kim-15",
}

def extract_pdf_text(pdf_path):
    doc = fitz.open(str(pdf_path))
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        pages.append({"page": page_num + 1, "text": text.strip()})
    doc.close()
    return pages

def classify_pdf(filename):
    lesson = None
    for i in range(1, 9):
        if f"_{i}과_" in filename:
            lesson = i
            break

    if "[01]" in filename or "내용정리" in filename:
        pdf_type = "content"
    elif "[04]" in filename or "WORD TEST" in filename:
        pdf_type = "wordtest"
    elif "[13]" in filename or ("Grammar" in filename and "객관식" not in filename):
        pdf_type = "grammar"
    elif "[14]" in filename or "객관식" in filename:
        pdf_type = "grammar_mc"  # extra grammar MC file
    else:
        pdf_type = "unknown"

    return lesson, pdf_type

def main():
    output_dir = Path(__file__).parent / "g3_extracted"
    output_dir.mkdir(exist_ok=True)

    all_results = {}

    for folder_name, textbook_id in TEXTBOOK_FOLDERS.items():
        folder_path = BASE_DIR / folder_name
        if not folder_path.exists():
            print(f"[SKIP] Folder not found: {folder_path}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing: {folder_name} → {textbook_id}")
        print(f"{'='*60}")

        textbook_data = {}
        pdfs = sorted(folder_path.glob("*.pdf"))
        for pdf_path in pdfs:
            lesson, pdf_type = classify_pdf(pdf_path.name)
            if lesson is None:
                print(f"  [WARN] Could not detect lesson: {pdf_path.name}")
                continue

            print(f"  Lesson {lesson} [{pdf_type}]: {pdf_path.name}")

            try:
                pages = extract_pdf_text(pdf_path)
                full_text = "\n".join(p["text"] for p in pages)

                key = f"lesson{lesson}"
                if key not in textbook_data:
                    textbook_data[key] = {"content": "", "wordtest": "", "grammar": ""}

                if pdf_type == "grammar_mc":
                    # Append grammar MC to grammar text
                    textbook_data[key]["grammar"] += "\n\n--- GRAMMAR MC ---\n\n" + full_text
                else:
                    textbook_data[key][pdf_type] = full_text

                print(f"    → {len(pages)} pages, {len(full_text)} chars")
            except Exception as e:
                print(f"    [ERROR] {e}")

        all_results[textbook_id] = textbook_data

        out_file = output_dir / f"{textbook_id}_batch2_raw.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(textbook_data, f, ensure_ascii=False, indent=2)
        print(f"\nSaved: {out_file}")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for tb_id, lessons in all_results.items():
        print(f"\n{tb_id}:")
        for lesson_key, types in sorted(lessons.items()):
            parts = []
            for t, text in types.items():
                if text:
                    parts.append(f"{t}={len(text)}c")
            print(f"  {lesson_key}: {', '.join(parts)}")

if __name__ == "__main__":
    main()
