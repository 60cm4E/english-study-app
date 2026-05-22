"""
enrich_g3_grammar.py — Enrich grammar sections with exercises from Grammar Build Up workbook PDFs
Reads the raw extracted grammar text and generates word-order, fill-blank, multi-choice, 
and error-correction exercises.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

EXTRACTED_DIR = Path(__file__).parent / "g3_extracted"
DATA_DIR = Path(__file__).parent.parent / "data"
TEXTBOOKS = ["donga-lee-15", "donga-yoon-15", "neungyul-kim-15"]


def find_english_korean_pairs(text):
    """Find English-Korean sentence pairs from grammar workbook text."""
    pairs = []
    lines = text.split('\n')
    
    for i in range(len(lines) - 1):
        en_line = lines[i].strip()
        
        # Clean circled numbers and annotations
        en_clean = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩✔→·▸►‣üPick]', '', en_line).strip()
        
        # Check if it's a proper English sentence
        if (re.match(r'^[A-Z]', en_clean) and 
            re.search(r'[.!?]$', en_clean) and 
            len(en_clean) > 15 and len(en_clean) < 100 and
            not re.match(r'^(?:All|Lesson|Test|Word|Grammar|Phrase|Warm|Before)', en_clean)):
            
            # Look for Korean translation
            for j in range(i+1, min(i+4, len(lines))):
                ko_line = lines[j].strip()
                ko_clean = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩✔→]', '', ko_line).strip()
                
                if re.search(r'[가-힣]{3,}', ko_clean) and len(ko_clean) > 5:
                    # Clean up
                    en_clean = re.sub(r'\s+', ' ', en_clean).strip()
                    ko_clean = re.sub(r'\s+', ' ', ko_clean).strip()
                    pairs.append({"en": en_clean, "ko": ko_clean})
                    break
    
    return pairs


def extract_grammar_exercises_from_workbook(grammar_text, content_text):
    """Extract and generate grammar exercises from the Grammar Build Up workbook."""
    exercises = []
    combined = content_text + "\n" + grammar_text
    
    # Find good English-Korean sentence pairs
    pairs = find_english_korean_pairs(combined)
    
    # 1. WORD-ORDER exercises: Use clean sentences with 4-10 words
    word_order_candidates = []
    for pair in pairs:
        en = pair["en"]
        words = en.rstrip(".!?").split()
        if 4 <= len(words) <= 10 and len(en) < 70:
            word_order_candidates.append({
                "type": "word-order",
                "words": words,
                "a": en
            })
    
    # Add up to 6 word-order exercises
    seen_wo = set()
    for ex in word_order_candidates:
        key = ex["a"].lower()
        if key not in seen_wo:
            seen_wo.add(key)
            exercises.append(ex)
            if len([e for e in exercises if e["type"] == "word-order"]) >= 6:
                break
    
    # 2. FILL-BLANK exercises: Find good sentences and blank key words
    stopwords = {
        "i", "you", "he", "she", "it", "we", "they", "a", "an", "the",
        "is", "am", "are", "was", "were", "be", "been", "being",
        "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "and", "or", "but", "not", "no", "so", "if", "my", "your",
        "his", "her", "its", "our", "their", "this", "that", "do",
        "does", "did", "will", "would", "can", "could", "should",
        "have", "has", "had", "me", "him", "us", "them"
    }
    
    fill_blank_count = 0
    for pair in pairs:
        if fill_blank_count >= 5:
            break
        en = pair["en"]
        ko = pair["ko"]
        words = re.findall(r"[a-zA-Z']+", en)
        candidates = [w for w in words if w.lower() not in stopwords and len(w) > 2]
        
        if candidates:
            key_word = max(candidates, key=len)
            blanked = en.replace(key_word, "___", 1)
            exercises.append({
                "type": "fill-blank",
                "q": blanked,
                "a": key_word,
                "hint": ko
            })
            fill_blank_count += 1
    
    # 3. ERROR-CORRECTION exercises
    error_rules = [
        # (pattern to find, wrong replacement, explanation)
        (r'\binterested\b', "interesting", "감정을 느끼는 주체는 과거분사(-ed)"),
        (r'\bexcited\b', "exciting", "감정을 느끼는 주체는 과거분사(-ed)"),
        (r'\bsurprised\b', "surprising", "감정을 느끼는 주체는 과거분사(-ed)"),
        (r'\bbored\b', "boring", "감정을 느끼는 주체는 과거분사(-ed)"),
        (r'\bplayed\b', "plaied", "자음+y → yed (y 앞이 모음이면 그대로)"),
        (r'\bto (\w{4,})\b', lambda m: m.group(1) + "ing", "to부정사: to + 동사원형"),
        (r'\bhappily\b', "happy", "동사를 수식하려면 부사(-ly)"),
        (r'\bfreely\b', "free", "동사를 수식하려면 부사(-ly)"),
        (r'\bcarefully\b', "careful", "동사를 수식하려면 부사(-ly)"),
    ]
    
    ec_count = 0
    ec_seen = set()
    for pair in pairs:
        if ec_count >= 4:
            break
        en = pair["en"]
        for pattern, wrong_fn, exp in error_rules:
            match = re.search(pattern, en)
            if match and en.lower() not in ec_seen:
                ec_seen.add(en.lower())
                if callable(wrong_fn):
                    wrong = wrong_fn(match)
                    correct = match.group(0)
                else:
                    wrong = wrong_fn
                    correct = match.group(0)
                
                wrong_sent = en[:match.start()] + wrong + en[match.end():]
                exercises.append({
                    "type": "error-correction",
                    "q": wrong_sent,
                    "a": correct,
                    "wrong": wrong,
                    "exp": exp
                })
                ec_count += 1
                break
    
    # 4. MULTI-CHOICE exercises: Look for grammar choice questions
    # Pattern: text with (option1 / option2) format
    mc_patterns = re.finditer(
        r'([A-Z][^.!?\n]*?\(([^/\n]+)\s*/\s*([^)\n]+)\)[^.!?\n]*[.!?])',
        combined
    )
    
    mc_count = 0
    mc_seen = set()
    for match in mc_patterns:
        if mc_count >= 4:
            break
        q_text = match.group(1).strip()
        opt1 = match.group(2).strip()
        opt2 = match.group(3).strip()
        
        if q_text.lower() not in mc_seen and len(q_text) > 15 and len(q_text) < 100:
            mc_seen.add(q_text.lower())
            # Clean
            q_text = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]', '', q_text).strip()
            exercises.append({
                "type": "multi-choice",
                "q": q_text,
                "a": opt1,  # First option is usually correct in textbooks
                "opts": [opt1, opt2],
            })
            mc_count += 1
    
    return exercises


def enrich_grammar_points(grammar_text, content_text, existing_points):
    """Improve grammar points with better examples."""
    combined = content_text + "\n" + grammar_text
    pairs = find_english_korean_pairs(combined)
    
    for point in existing_points:
        title = point["title"]
        
        # Find examples related to this grammar point
        if not point.get("examples") or len(point["examples"]) < 2:
            new_examples = []
            keywords = title.lower().split()
            
            for pair in pairs:
                en = pair["en"]
                # Check relevance
                relevant = False
                if title == "to부정사" and re.search(r'\bto\s+\w+\b', en):
                    relevant = True
                elif title == "관계대명사" and re.search(r'\b(?:who|which|that|what|whose|whom)\b', en, re.IGNORECASE):
                    relevant = True
                elif title == "현재완료" and re.search(r'\b(?:have|has)\s+(?:been|done|made|played|seen|lived|worked|studied)\b', en, re.IGNORECASE):
                    relevant = True
                elif title == "수동태" and re.search(r'\b(?:is|are|was|were)\s+\w+ed\b', en, re.IGNORECASE):
                    relevant = True
                elif title == "분사" and re.search(r'\b\w+(?:ing|ed)\b', en):
                    relevant = True
                elif title == "가정법" and re.search(r'\bif\b', en, re.IGNORECASE):
                    relevant = True
                elif title == "간접의문문" and re.search(r'\b(?:what|where|when|how|why|who)\b', en, re.IGNORECASE):
                    relevant = True
                elif title == "접속사" and re.search(r'\b(?:because|although|while|when|if|that)\b', en, re.IGNORECASE):
                    relevant = True
                elif "make" in title.lower() and re.search(r'\bmade?\b', en, re.IGNORECASE):
                    relevant = True
                elif title == "동명사" and re.search(r'\b\w+ing\b', en):
                    relevant = True
                elif "비교" in title and re.search(r'\b(?:more|most|er|est|as\b.*\bas)\b', en, re.IGNORECASE):
                    relevant = True
                elif title == "감탄문" and re.search(r'\b(?:What a|How)\b', en):
                    relevant = True
                elif "가주어" in title and re.search(r'\bIt\s+(?:is|was)\b', en):
                    relevant = True
                
                if relevant and len(en) > 15 and len(en) < 80:
                    new_examples.append(pair)
                    if len(new_examples) >= 4:
                        break
            
            if new_examples:
                point["examples"] = new_examples[:4]
    
    return existing_points


def main():
    for tb_id in TEXTBOOKS:
        raw_file = EXTRACTED_DIR / f"{tb_id}_raw.json"
        if not raw_file.exists():
            print(f"[SKIP] {raw_file} not found")
            continue
        
        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        print(f"\n{'='*50}")
        print(f"Enriching grammar: {tb_id}")
        print(f"{'='*50}")
        
        for lesson_key in sorted(raw_data.keys()):
            lesson_num = int(lesson_key.replace("lesson", ""))
            lesson_data = raw_data[lesson_key]
            
            content_text = lesson_data.get("content", "")
            grammar_text = lesson_data.get("grammar", "")
            
            # Load existing content.json
            ct_path = DATA_DIR / tb_id / f"lesson{lesson_num}" / "content.json"
            if not ct_path.exists():
                print(f"  [SKIP] {ct_path} not found")
                continue
            
            with open(ct_path, "r", encoding="utf-8") as f:
                ct = json.load(f)
            
            # Generate grammar exercises
            new_exercises = extract_grammar_exercises_from_workbook(grammar_text, content_text)
            
            # Enrich grammar points
            ct["grammar"]["points"] = enrich_grammar_points(
                grammar_text, content_text, 
                ct["grammar"].get("points", [])
            )
            
            # Merge exercises (keep existing, add new)
            existing_ex = ct["grammar"].get("exercises", [])
            ct["grammar"]["exercises"] = existing_ex + new_exercises
            
            # Save
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
