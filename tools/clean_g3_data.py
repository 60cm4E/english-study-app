"""
clean_g3_data.py — Post-process generated JSON files to clean up data quality
- Remove duplicate words (keeping the best version)
- Clean example sentences (remove PDF artifacts like ①②③④⑤ and newlines)
- Fix malformed entries
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = Path(__file__).parent.parent / "data"
TEXTBOOKS = ["donga-lee-15", "donga-yoon-15", "neungyul-kim-15"]

def clean_example(ex):
    """Clean up example sentence text."""
    if not ex:
        return ""
    # Remove circled numbers
    ex = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]', '', ex)
    # Remove section headers
    ex = re.sub(r'^(?:Reading|Lesson|All the Dialogue|Listen and (?:Speak|Write|Choose)|Study Points|Think and Talk|Look and Talk|Real Life Talk|Warm Up|Before You Begin).*?\n', '', ex)
    # Replace newlines with spaces
    ex = re.sub(r'\n+', ' ', ex)
    # Remove multiple spaces
    ex = re.sub(r'\s+', ' ', ex).strip()
    # Remove leading labels like "B:" "G:"
    ex = re.sub(r'^[ABGW]:\s*', '', ex)
    # Trim if too long
    if len(ex) > 100:
        # Try to find a sentence boundary
        sentences = re.split(r'(?<=[.!?])\s+', ex)
        if sentences:
            ex = sentences[0]
    return ex.strip()

def is_valid_word(entry):
    """Check if a word entry is valid (not a malformed duplicate)."""
    en = entry.get("en", "")
    ko = entry.get("ko", "")
    
    # Skip entries where 'en' contains Korean pos info (like "same a. 같은")
    if re.search(r'\s+(?:n\.|v\.|a\.|adv\.|prep\.|conj\.)\s', en):
        return False
    
    # Skip entries where 'en' contains Korean characters
    if re.search(r'[가-힣]', en):
        return False
    
    # Skip entries where 'ko' starts with "예문" or "영영"
    if ko.startswith("예문") or ko.startswith("영영"):
        return False
    
    # Skip entries that are too long (probably parse errors)
    if len(en) > 40:
        return False
    
    # Skip entries where en has POS embedded (like "same a. 같은")
    if re.match(r'^[a-zA-Z]+\s+(?:n\.|v\.|a\.|adv\.)', en):
        return False
    
    # Skip entries that include OPP/SYN
    if "OPP" in en or "SYN" in en:
        return False
    
    return True

def deduplicate_words(words):
    """Remove duplicate words, keeping the best version."""
    seen = {}
    for w in words:
        en_key = w["en"].lower().strip()
        
        if not is_valid_word(w):
            continue
        
        if en_key in seen:
            # Keep the one with more info (pos, example)
            existing = seen[en_key]
            if not existing.get("pos") and w.get("pos"):
                existing["pos"] = w["pos"]
            if not existing.get("ex") and w.get("ex"):
                existing["ex"] = clean_example(w["ex"])
            continue
        
        # Clean example
        if w.get("ex"):
            w["ex"] = clean_example(w["ex"])
            if not w["ex"]:
                del w["ex"]
        
        seen[en_key] = w
    
    return list(seen.values())

def clean_content_exercises(content):
    """Clean exercises in content.json."""
    for section in ["communication", "reading", "grammar"]:
        if section in content:
            exercises = content[section].get("exercises", [])
            cleaned = []
            for ex in exercises:
                # Clean question text
                if "q" in ex:
                    ex["q"] = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]', '', ex["q"])
                    ex["q"] = re.sub(r'\n+', ' ', ex["q"])
                    ex["q"] = re.sub(r'\s+', ' ', ex["q"]).strip()
                
                # Clean answer
                if "a" in ex and isinstance(ex["a"], str):
                    ex["a"] = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]', '', ex["a"])
                    ex["a"] = re.sub(r'\n+', ' ', ex["a"])
                    ex["a"] = re.sub(r'\s+', ' ', ex["a"]).strip()
                
                # Clean hint
                if "hint" in ex and isinstance(ex["hint"], str):
                    ex["hint"] = re.sub(r'\n+', ' ', ex["hint"]).strip()
                
                # Clean explanation
                if "exp" in ex and isinstance(ex["exp"], str):
                    ex["exp"] = re.sub(r'\n+', ' ', ex["exp"]).strip()
                
                # Skip empty exercises
                if ex.get("q") and (ex.get("a") or ex.get("a") is False or ex.get("a") is True):
                    cleaned.append(ex)
            
            content[section]["exercises"] = cleaned
    
    # Clean key expressions
    if "communication" in content:
        ke = content["communication"].get("keyExpressions", [])
        for expr in ke:
            for field in ["en", "ko"]:
                if field in expr:
                    expr[field] = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]', '', expr[field])
                    expr[field] = re.sub(r'\n+', ' ', expr[field])
                    expr[field] = re.sub(r'\s+', ' ', expr[field]).strip()
    
    # Clean passages
    if "reading" in content:
        passages = content["reading"].get("passages", [])
        for p in passages:
            for field in ["en", "ko", "title"]:
                if field in p:
                    p[field] = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]', '', p[field])
                    p[field] = re.sub(r'\n+', ' ', p[field])
                    p[field] = re.sub(r'\s+', ' ', p[field]).strip()
    
    # Clean grammar points
    if "grammar" in content:
        points = content["grammar"].get("points", [])
        for pt in points:
            for ex in pt.get("examples", []):
                for field in ["en", "ko"]:
                    if field in ex:
                        ex[field] = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]', '', ex[field])
                        ex[field] = re.sub(r'\n+', ' ', ex[field])
                        ex[field] = re.sub(r'\s+', ' ', ex[field]).strip()
    
    return content

def main():
    total_stats = {}
    
    for tb_id in TEXTBOOKS:
        tb_dir = DATA_DIR / tb_id
        if not tb_dir.exists():
            continue
        
        print(f"\n{'='*50}")
        print(f"Cleaning: {tb_id}")
        print(f"{'='*50}")
        
        for lesson_dir in sorted(tb_dir.iterdir()):
            if not lesson_dir.is_dir() or not lesson_dir.name.startswith("lesson"):
                continue
            
            lesson_num = lesson_dir.name
            
            # Clean wordtest.json
            wt_path = lesson_dir / "wordtest.json"
            if wt_path.exists():
                with open(wt_path, "r", encoding="utf-8") as f:
                    wt = json.load(f)
                
                original_count = len(wt.get("words", []))
                wt["words"] = deduplicate_words(wt.get("words", []))
                new_count = len(wt["words"])
                
                with open(wt_path, "w", encoding="utf-8") as f:
                    json.dump(wt, f, ensure_ascii=False, indent=2)
                
                print(f"  {lesson_num}/wordtest: {original_count} → {new_count} words")
            
            # Clean content.json
            ct_path = lesson_dir / "content.json"
            if ct_path.exists():
                with open(ct_path, "r", encoding="utf-8") as f:
                    ct = json.load(f)
                
                ct = clean_content_exercises(ct)
                
                with open(ct_path, "w", encoding="utf-8") as f:
                    json.dump(ct, f, ensure_ascii=False, indent=2)
                
                comm_ex = len(ct.get("communication", {}).get("exercises", []))
                read_ex = len(ct.get("reading", {}).get("exercises", []))
                gram_ex = len(ct.get("grammar", {}).get("exercises", []))
                print(f"  {lesson_num}/content: comm={comm_ex}, read={read_ex}, gram={gram_ex} exercises")
    
    print("\n✅ Cleaning complete!")

if __name__ == "__main__":
    main()
