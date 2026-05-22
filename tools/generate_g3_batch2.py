"""
generate_g3_batch2.py — Batch 2 (lessons 5-8) JSON generation
Reuses the generate_g3_json.py functions for batch2 raw files.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))

from generate_g3_json import generate_lesson_data

EXTRACTED_DIR = Path(__file__).parent / "g3_extracted"
OUTPUT_BASE = Path(__file__).parent.parent / "data"

TEXTBOOKS = {
    "donga-lee-15": "donga-lee-15_batch2_raw.json",
    "donga-yoon-15": "donga-yoon-15_batch2_raw.json",
    "neungyul-kim-15": "neungyul-kim-15_batch2_raw.json",
}

def main():
    all_lessons = {}

    for tb_id, raw_filename in TEXTBOOKS.items():
        raw_file = EXTRACTED_DIR / raw_filename
        if not raw_file.exists():
            print(f"[SKIP] {raw_file}")
            continue

        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        print(f"\n{'='*60}")
        print(f"Generating: {tb_id} (batch 2)")
        print(f"{'='*60}")

        lessons_created = []

        for lesson_key in sorted(raw_data.keys()):
            lesson_num = int(lesson_key.replace("lesson", ""))
            lesson_data = raw_data[lesson_key]

            print(f"\n  Lesson {lesson_num}:")

            content_json, wordtest_json = generate_lesson_data(lesson_data, tb_id, lesson_num)

            out_dir = OUTPUT_BASE / tb_id / f"lesson{lesson_num}"
            out_dir.mkdir(parents=True, exist_ok=True)

            with open(out_dir / "content.json", "w", encoding="utf-8") as f:
                json.dump(content_json, f, ensure_ascii=False, indent=2)
            with open(out_dir / "wordtest.json", "w", encoding="utf-8") as f:
                json.dump(wordtest_json, f, ensure_ascii=False, indent=2)

            wc = len(wordtest_json.get("words", []))
            ce = len(content_json.get("communication", {}).get("exercises", []))
            re_ = len(content_json.get("reading", {}).get("exercises", []))
            ge = len(content_json.get("grammar", {}).get("exercises", []))
            print(f"    Words: {wc}")
            print(f"    Exercises: comm={ce}, read={re_}, gram={ge}")
            print(f"    Saved: {out_dir}")

            lessons_created.append(lesson_num)

        all_lessons[tb_id] = lessons_created

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for tb, ls in all_lessons.items():
        print(f"  {tb}: Lessons {ls}")

if __name__ == "__main__":
    main()
