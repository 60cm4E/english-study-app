"""
enrich_g3_batch2_grammar.py — Enrich grammar for batch 2 (lessons 5-8)
Reads batch2 raw files and enriches the corresponding content.json files.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))

from enrich_g3_grammar import extract_grammar_exercises_from_workbook, enrich_grammar_points

EXTRACTED_DIR = Path(__file__).parent / "g3_extracted"
DATA_DIR = Path(__file__).parent.parent / "data"

BATCH2_FILES = {
    "donga-lee-15": "donga-lee-15_batch2_raw.json",
    "donga-yoon-15": "donga-yoon-15_batch2_raw.json",
    "neungyul-kim-15": "neungyul-kim-15_batch2_raw.json",
}

def main():
    for tb_id, raw_filename in BATCH2_FILES.items():
        raw_file = EXTRACTED_DIR / raw_filename
        if not raw_file.exists():
            print(f"[SKIP] {raw_file}")
            continue

        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        print(f"\n{'='*50}")
        print(f"Enriching grammar: {tb_id} (batch 2)")
        print(f"{'='*50}")

        for lesson_key in sorted(raw_data.keys()):
            lesson_num = int(lesson_key.replace("lesson", ""))
            lesson_data = raw_data[lesson_key]

            content_text = lesson_data.get("content", "")
            grammar_text = lesson_data.get("grammar", "")

            ct_path = DATA_DIR / tb_id / f"lesson{lesson_num}" / "content.json"
            if not ct_path.exists():
                print(f"  [SKIP] {ct_path}")
                continue

            with open(ct_path, "r", encoding="utf-8") as f:
                ct = json.load(f)

            new_exercises = extract_grammar_exercises_from_workbook(grammar_text, content_text)
            ct["grammar"]["points"] = enrich_grammar_points(
                grammar_text, content_text,
                ct["grammar"].get("points", [])
            )
            existing_ex = ct["grammar"].get("exercises", [])
            ct["grammar"]["exercises"] = existing_ex + new_exercises

            with open(ct_path, "w", encoding="utf-8") as f:
                json.dump(ct, f, ensure_ascii=False, indent=2)

            wo = len([e for e in ct["grammar"]["exercises"] if e["type"] == "word-order"])
            fb = len([e for e in ct["grammar"]["exercises"] if e["type"] == "fill-blank"])
            mc = len([e for e in ct["grammar"]["exercises"] if e["type"] == "multi-choice"])
            ec = len([e for e in ct["grammar"]["exercises"] if e["type"] == "error-correction"])

            print(f"  lesson{lesson_num}: wo={wo}, fb={fb}, mc={mc}, ec={ec} (total {len(ct['grammar']['exercises'])})")

    print("\n✅ Grammar enrichment complete!")

if __name__ == "__main__":
    main()
