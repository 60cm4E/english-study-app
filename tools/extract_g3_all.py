"""
extract_g3_all.py — 중3 교과서 PDF 전체 텍스트 추출
3개 교과서 × 4과 × 3파일(내용정리, WORD TEST, Grammar Build Up) = 36 PDF
"""
import fitz  # PyMuPDF
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(r"C:\Users\chenc\Downloads\작업물\중3")

# Textbook folder → textbook ID mapping
TEXTBOOK_FOLDERS = {
    "중3 동아 이병민": "donga-lee-15",
    "중3 동아 윤정미": "donga-yoon-15",
    "중3 능률 김성곤": "neungyul-kim-15",
}

def extract_pdf_text(pdf_path):
    """Extract all text from a PDF file."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        pages.append({
            "page": page_num + 1,
            "text": text.strip()
        })
    doc.close()
    return pages

def classify_pdf(filename):
    """Classify PDF by type and lesson number."""
    fn = filename.lower()
    
    # Extract lesson number
    lesson = None
    for i in range(1, 9):
        if f"_{i}과_" in filename:
            lesson = i
            break
    
    # Classify type
    if "[01]" in filename or "내용정리" in filename:
        pdf_type = "content"  # 내용정리 (Content Summary)
    elif "[04]" in filename or "WORD TEST" in filename:
        pdf_type = "wordtest"  # Word Test
    elif "[13]" in filename or "Grammar" in filename:
        pdf_type = "grammar"  # Grammar Build Up
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
        
        # Get all PDFs
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
                
                textbook_data[key][pdf_type] = full_text
                
                print(f"    → {len(pages)} pages, {len(full_text)} chars")
            except Exception as e:
                print(f"    [ERROR] {e}")
        
        all_results[textbook_id] = textbook_data
        
        # Save individual textbook extraction
        out_file = output_dir / f"{textbook_id}_raw.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(textbook_data, f, ensure_ascii=False, indent=2)
        print(f"\nSaved: {out_file}")
    
    # Save combined results
    combined_file = output_dir / "all_g3_raw.json"
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\nAll saved: {combined_file}")
    
    # Print summary
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
