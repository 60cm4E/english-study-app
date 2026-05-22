"""
generate_g3_json.py — Generate content.json + wordtest.json for all Grade 3 textbooks
Reads raw extracted text and produces structured JSON for the learning app.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

EXTRACTED_DIR = Path(__file__).parent / "g3_extracted"
OUTPUT_BASE = Path(__file__).parent.parent / "data"

# ─── Word Extraction ───────────────────────────────────────
def extract_words_from_wordtest(text):
    """Extract words from WORD TEST PDF text (단어·숙어장 Word List format)."""
    words = []
    seen = set()
    
    # Pattern: Ÿ word\n pos. meaning (the Ÿ bullet marker format)
    # Lines like:  Ÿ same\n a. 같은
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Detect word entry: starts with Ÿ or bullet
        word_match = re.match(r'^[Ÿ•·▪▸►‣]\s*(.+)$', line)
        if word_match:
            en_word = word_match.group(1).strip()
            # Check next lines for pos and meaning
            pos = ""
            ko = ""
            j = i + 1
            while j < len(lines) and j <= i + 4:
                next_line = lines[j].strip()
                if not next_line:
                    j += 1
                    continue
                
                # Check if it's pos + meaning like "a. 같은" or "n. 문제"
                pos_match = re.match(r'^(n\.|v\.|a\.|adv\.|prep\.|conj\.|interj\.)\s*(.*)', next_line)
                if pos_match:
                    pos = pos_match.group(1)
                    ko = pos_match.group(2).strip()
                    break
                
                # Check for Korean meaning without pos
                if re.search(r'[가-힣]', next_line) and not re.match(r'^[Ÿ•·▪▸►‣]', next_line):
                    ko = next_line
                    break
                
                # Check for next word entry
                if re.match(r'^[Ÿ•·▪▸►‣]', next_line):
                    break
                j += 1
            
            if en_word and ko and en_word.lower() not in seen:
                # Clean up
                en_word = re.sub(r'\s+', ' ', en_word).strip()
                ko = re.sub(r'\s+', ' ', ko).strip()
                # Remove asterisks
                ko = ko.replace('*', '').strip()
                
                # Skip if it looks like a test instruction
                if len(en_word) > 1 and not en_word.startswith('(') and 'Test' not in en_word:
                    seen.add(en_word.lower())
                    entry = {"en": en_word, "ko": ko}
                    if pos:
                        entry["pos"] = pos
                    words.append(entry)
        i += 1
    
    # Also try Phrase List pattern
    phrase_section = text.find("Phrase List")
    if phrase_section > 0:
        phrase_text = text[phrase_section:]
        phrase_lines = phrase_text.split('\n')
        pi = 0
        while pi < len(phrase_lines):
            pline = phrase_lines[pi].strip()
            phrase_match = re.match(r'^[Ÿ•·▪▸►‣]\s*(.+)$', pline)
            if phrase_match:
                phrase_en = phrase_match.group(1).strip()
                # Next line should be Korean meaning
                if pi + 1 < len(phrase_lines):
                    next_pline = phrase_lines[pi+1].strip()
                    if re.search(r'[가-힣]', next_pline) and phrase_en.lower() not in seen:
                        seen.add(phrase_en.lower())
                        words.append({"en": phrase_en, "ko": next_pline})
            pi += 1
    
    return words


def add_example_sentences(words, content_text):
    """Add example sentences from content text to words."""
    # Find sentences containing each word
    sentences = re.findall(r'([A-Z][^.!?]{15,80}[.!?])', content_text)
    
    for word in words:
        if word.get("ex"):
            continue
        en = word["en"].lower()
        for sent in sentences:
            if en in sent.lower() and len(sent) < 100:
                word["ex"] = sent.strip()
                break


# ─── Communication Section ─────────────────────────────────
def extract_communication(content_text):
    """Extract communication expressions and exercises from content text."""
    key_expressions = []
    exercises = []
    
    # Find dialogue patterns: English line followed by Korean translation
    lines = content_text.split('\n')
    
    # Pattern 1: A: / B: / G: / Boy: etc patterns
    dialogue_patterns = []
    i = 0
    while i < len(lines) - 1:
        line = lines[i].strip()
        # Match dialogue lines like "B: text" or "G: text"
        dial_match = re.match(r'^[ABGW]:\s*(.+)$', line)
        if dial_match:
            en_text = dial_match.group(1).strip()
            # Check if next lines have Korean translation
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j].strip()
                ko_match = re.match(r'^(?:소[녀년]|[AB]):\s*(.+)$', next_line)
                if ko_match and re.search(r'[가-힣]', next_line):
                    ko_text = ko_match.group(1).strip()
                    if len(en_text) > 10 and len(ko_text) > 3:
                        dialogue_patterns.append({"en": en_text, "ko": ko_text})
                    break
        i += 1
    
    # Find key expressions - look for üPick markers or special expression patterns
    key_expr_patterns = [
        (r'(?:안부\s*묻고\s*답하기|How have you been)', "안부 묻고 답하기"),
        (r'(?:기쁨|유감)\s*표현', "기쁨/유감 표현"),
        (r'(?:I\'m happy to hear|I\'m sorry to hear)', "기쁨/유감 표현"),
        (r'(?:I hope|I wish)', "희망 표현"),
        (r'(?:Don\'t worry|Relax|Take it easy)', "안심시키기"),
        (r'(?:Could you|Would you|Can you)', "요청"),
        (r'(?:You should|had better|Why don\'t)', "조언"),
        (r'(?:Let\'s|How about|Shall we)', "제안"),
        (r'(?:Thank you|Thanks)', "감사"),
        (r'(?:I\'m sorry|Excuse me)', "사과"),
    ]
    
    # Extract specific communication expressions
    seen_en = set()
    
    # First pass: find üPick marked expressions
    upick_sections = re.finditer(r'üPick\s+(.+?)[:：](.+?)(?=\n[①②③④⑤⑥⑦⑧⑨⑩]|\nAll|\n✔|\n구문|\n$)', content_text, re.DOTALL)
    for match in upick_sections:
        category = match.group(1).strip()
        context = match.group(2).strip()
        # Try to find example sentences in context
        en_sents = re.findall(r'([A-Z][^.!?]+[.!?])', context)
        for en in en_sents[:2]:
            en = en.strip()
            if en.lower() not in seen_en and len(en) > 10:
                seen_en.add(en.lower())
                key_expressions.append({
                    "en": en,
                    "ko": "",
                    "category": category
                })
    
    # Find paired English-Korean sentences for key expressions
    for pair in dialogue_patterns:
        if pair["en"].lower() not in seen_en and len(pair["en"]) > 10:
            seen_en.add(pair["en"].lower())
            cat = "일반 표현"
            for pattern, category in key_expr_patterns:
                if re.search(pattern, pair["en"], re.IGNORECASE):
                    cat = category
                    break
            key_expressions.append({
                "en": pair["en"],
                "ko": pair["ko"],
                "category": cat
            })

    # Limit and ensure quality
    key_expressions = [e for e in key_expressions if e.get("en") and len(e["en"]) > 5][:15]
    
    # Generate exercises from key expressions
    for expr in key_expressions:
        en = expr["en"]
        # Find a content word to blank out
        key_word = find_key_word(en)
        if key_word:
            blanked = en.replace(key_word, "___", 1)
            exercises.append({
                "type": "fill-blank",
                "q": blanked,
                "a": key_word,
                "hint": expr.get("ko", "")
            })
    
    # Add multi-choice exercises
    for expr in key_expressions[:5]:
        en = expr["en"]
        if "(" in en and "/" in en and ")" in en:
            # Already has choices format
            exercises.append({
                "type": "multi-choice",
                "q": en,
                "a": expr.get("ko", ""),
            })
    
    return {
        "keyExpressions": key_expressions,
        "exercises": exercises
    }


# ─── Reading Section ───────────────────────────────────────
def extract_reading(content_text):
    """Extract reading passages and exercises from content text."""
    passages = []
    exercises = []
    
    # Look for reading passage sections (본문)
    # Pattern: Find consecutive English paragraphs with Korean translations
    
    # Method 1: Look for explicit passage markers
    passage_markers = [
        r'본문[❶❷❸❹❺①②③④⑤1-5]',
        r'Read\s*(?:and|&)',
        r'Reading\s+\d',
        r'Main Text',
    ]
    
    # Find sentence pairs (English followed by Korean)
    en_ko_pairs = []
    lines = content_text.split('\n')
    i = 0
    while i < len(lines) - 1:
        en_line = lines[i].strip()
        # Check if this is an English sentence (starts with capital, has some length)
        if (re.match(r'^[A-Z]', en_line) and 
            len(en_line) > 20 and
            re.search(r'[.!?]$', en_line) and
            not re.match(r'^(?:All|Lesson|Test|Word|Grammar|Phrase|Warm|Before|Real|Listen|Think|Look|Speak|Read)', en_line)):
            
            # Look for Korean translation in next few lines
            for j in range(i+1, min(i+4, len(lines))):
                ko_line = lines[j].strip()
                if re.search(r'[가-힣]{3,}', ko_line) and len(ko_line) > 5:
                    en_ko_pairs.append({"en": en_line, "ko": ko_line})
                    i = j + 1
                    break
            else:
                i += 1
        else:
            i += 1
    
    # Group into passages by looking for long continuous English text blocks
    text_blocks = re.split(r'\n\s*\n', content_text)
    passage_en_blocks = []
    
    for block in text_blocks:
        block = block.strip()
        # Check if block is primarily English text
        en_chars = sum(1 for c in block if c.isascii() and c.isalpha())
        total_chars = sum(1 for c in block if c.isalpha())
        word_count = len(block.split())
        
        if total_chars > 0 and en_chars / total_chars > 0.7 and word_count > 30:
            # Clean the block
            clean_block = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]', '', block)
            clean_block = re.sub(r'\s+', ' ', clean_block).strip()
            passage_en_blocks.append(clean_block)
    
    # Create passage entries
    for idx, en_block in enumerate(passage_en_blocks[:5]):
        # Find corresponding Korean translation
        ko_translation = ""
        for pair in en_ko_pairs:
            if any(sent.strip() in pair["en"] for sent in en_block.split('.') if len(sent.strip()) > 10):
                ko_translation += pair["ko"] + " "
        
        passages.append({
            "id": f"r{idx+1}",
            "title": f"본문❷ - {idx+1}",
            "en": en_block,
            "ko": ko_translation.strip()
        })
    
    # If no long passages found, use sentence pairs
    if not passages and en_ko_pairs:
        # Group sentence pairs into passages
        batch_size = 5
        for batch_idx in range(0, min(len(en_ko_pairs), 15), batch_size):
            batch = en_ko_pairs[batch_idx:batch_idx+batch_size]
            if batch:
                passages.append({
                    "id": f"r{batch_idx//batch_size + 1}",
                    "title": f"본문 - {batch_idx//batch_size + 1}",
                    "en": " ".join(p["en"] for p in batch),
                    "ko": " ".join(p["ko"] for p in batch)
                })
    
    # Generate reading exercises
    for p in passages:
        en = p.get("en", "")
        if not en:
            continue
        
        # fill-blank from passage
        en_sentences = re.split(r'(?<=[.!?])\s+', en)
        for sent in en_sentences[:3]:
            key_word = find_key_word(sent)
            if key_word and len(key_word) > 2:
                blanked = sent.replace(key_word, "___", 1)
                exercises.append({
                    "type": "fill-blank",
                    "q": blanked,
                    "a": key_word,
                    "passage": p["id"]
                })
        
        # true-false
        if p.get("ko"):
            ko_text = p["ko"][:60] + ("..." if len(p["ko"]) > 60 else "")
            exercises.append({
                "type": "true-false",
                "q": ko_text,
                "a": True,
                "exp": "본문 내용과 일치"
            })
    
    return {
        "passages": passages,
        "exercises": exercises
    }


# ─── Grammar Section ──────────────────────────────────────
def extract_grammar(content_text, grammar_text):
    """Extract grammar points and exercises."""
    points = []
    exercises = []
    
    combined_text = content_text + "\n" + grammar_text
    
    # Common grammar topics for Grade 3
    grammar_topics = {
        "to부정사": {
            "keywords": ["to부정사", "to+동사원형", "to-infinitive"],
            "subtopics": {
                "형용사적 용법": "to부정사가 앞의 명사를 꾸며주는 형용사 역할을 합니다.",
                "부사적 용법": "to부정사가 동사, 형용사, 부사를 수식하는 부사 역할을 합니다.",
                "명사적 용법": "to부정사가 주어, 목적어, 보어 역할을 합니다.",
            }
        },
        "관계대명사": {
            "keywords": ["관계대명사", "who", "which", "that", "what", "whose", "whom"],
            "explanation": "'관계대명사'는 두 문장을 하나로 연결하는 접속사+대명사 역할을 합니다."
        },
        "현재완료": {
            "keywords": ["현재완료", "have/has + p.p.", "have been", "has been"],
            "explanation": "'have/has + 과거분사'로 과거에 시작된 일이 현재까지 영향을 미침을 나타냅니다."
        },
        "수동태": {
            "keywords": ["수동태", "be + p.p.", "by + 행위자"],
            "explanation": "'be동사 + 과거분사(p.p.)'로 '~되다, ~당하다'의 의미를 나타냅니다."
        },
        "분사": {
            "keywords": ["분사", "현재분사", "과거분사", "-ing", "-ed"],
            "explanation": "현재분사(-ing)와 과거분사(-ed)가 명사를 수식하는 형용사 역할을 합니다."
        },
        "가정법": {
            "keywords": ["가정법", "if + 과거", "I wish"],
            "explanation": "현실과 반대되거나 불가능한 상황을 가정할 때 사용합니다."
        },
        "간접의문문": {
            "keywords": ["간접의문문", "의문사+주어+동사"],
            "explanation": "의문문이 다른 문장의 일부로 사용될 때 '의문사+주어+동사' 어순을 씁니다."
        },
        "접속사": {
            "keywords": ["접속사", "that", "because", "although", "while", "when", "if"],
            "explanation": "절과 절을 연결하는 접속사의 사용법입니다."
        },
        "it ~ to 가주어": {
            "keywords": ["가주어", "It ~ to", "It is ~ to", "It was ~ for"],
            "explanation": "'It is + 형용사 + (for ~) + to부정사'에서 It은 가주어, to부정사가 진주어입니다."
        },
        "make + O + C": {
            "keywords": ["make + 목적어", "make + O + C", "사역동사"],
            "explanation": "'make + 목적어 + 형용사/동사원형'으로 '~를 …하게 만들다'를 나타냅니다."
        },
        "동명사": {
            "keywords": ["동명사", "~ing", "동사+-ing"],
            "explanation": "동명사(동사원형+ing)가 문장에서 명사 역할(주어, 목적어, 보어)을 합니다."
        },
        "비교급/최상급": {
            "keywords": ["비교급", "최상급", "more", "most", "-er", "-est", "as ~ as"],
            "explanation": "형용사/부사의 비교급(-er/more)과 최상급(-est/most)을 사용하여 비교를 나타냅니다."
        },
        "감탄문": {
            "keywords": ["감탄문", "What a", "How"],
            "explanation": "'What a(n) + 형용사 + 명사!'또는 'How + 형용사/부사 + 주어 + 동사!'로 감탄을 표현합니다."
        },
    }
    
    found_grammar = []
    for topic, info in grammar_topics.items():
        for kw in info.get("keywords", []):
            if kw in combined_text:
                found_grammar.append(topic)
                break
    
    # Extract grammar explanations and examples
    for idx, topic in enumerate(found_grammar[:4]):
        info = grammar_topics[topic]
        
        # Find examples in text
        examples = []
        
        # Look for English-Korean sentence pairs near the grammar topic keywords
        for kw in info.get("keywords", []):
            keyword_pos = combined_text.find(kw)
            if keyword_pos >= 0:
                # Get surrounding context
                context = combined_text[max(0, keyword_pos-200):min(len(combined_text), keyword_pos+500)]
                
                # Find EN-KO pairs in context
                context_lines = context.split('\n')
                for ci in range(len(context_lines) - 1):
                    cline = context_lines[ci].strip()
                    # Find example sentences
                    if re.match(r'^[A-Z]', cline) and re.search(r'[.!?]$', cline) and len(cline) > 10 and len(cline) < 80:
                        # Check next line for Korean
                        nline = context_lines[ci+1].strip() if ci+1 < len(context_lines) else ""
                        if re.search(r'[가-힣]{3,}', nline):
                            examples.append({"en": cline, "ko": nline})
                            if len(examples) >= 4:
                                break
                if len(examples) >= 4:
                    break
        
        explanation = info.get("explanation", f"{topic}에 관한 문법 포인트입니다.")
        if isinstance(info.get("subtopics"), dict):
            for sub_name, sub_exp in info["subtopics"].items():
                if sub_name in combined_text:
                    explanation = sub_exp
                    break
        
        points.append({
            "id": f"g{idx+1}",
            "title": topic,
            "explanation": explanation,
            "examples": examples[:4]
        })
    
    # Generate grammar exercises
    # word-order exercises from sentence pairs
    all_sentences = re.findall(r'([A-Z][a-zA-Z\s,\'-]+[.!?])', combined_text)
    good_sentences = [s for s in all_sentences if 4 <= len(s.split()) <= 12 and len(s) < 80]
    
    for sent in good_sentences[:6]:
        words_list = sent.rstrip(".!?").split()
        if 4 <= len(words_list) <= 10:
            exercises.append({
                "type": "word-order",
                "words": words_list,
                "a": sent
            })
    
    # Error correction exercises from grammar workbook
    error_patterns = [
        (r'\binterested\b', "interesting", "interested", "감정을 느끼는 주체는 과거분사 -ed"),
        (r'\bexcited\b', "exciting", "excited", "감정을 느끼는 주체는 과거분사 -ed"),
        (r'\bbored\b', "boring", "bored", "감정을 느끼는 주체는 과거분사 -ed"),
        (r'\bsurprised\b', "surprising", "surprised", "감정을 느끼는 주체는 과거분사 -ed"),
    ]
    
    for sent in good_sentences[:20]:
        for pattern, wrong, correct, exp in error_patterns:
            match = re.search(pattern, sent)
            if match:
                wrong_sent = sent[:match.start()] + wrong + sent[match.end():]
                exercises.append({
                    "type": "error-correction",
                    "q": wrong_sent,
                    "a": correct,
                    "wrong": wrong,
                    "exp": exp
                })
                break
    
    # Multi-choice grammar exercises
    grammar_exercises_text = grammar_text or ""
    # Look for questions in grammar workbook
    mc_questions = re.finditer(
        r'(?:다음|밑줄|빈칸|어법상).+?(?:\n|$)(.+?\([^)]+\/.+?\).+?)(?:\n|$)',
        grammar_exercises_text
    )
    for match in mc_questions:
        q_text = match.group(1).strip()
        if len(q_text) > 10:
            exercises.append({
                "type": "multi-choice",
                "q": q_text,
                "a": "",
            })
    
    return {
        "points": points,
        "exercises": exercises[:15]
    }


# ─── Utility Functions ────────────────────────────────────
def find_key_word(sentence):
    """Find the best word to blank out in a sentence."""
    stopwords = {
        "i", "you", "he", "she", "it", "we", "they", "a", "an", "the",
        "is", "am", "are", "was", "were", "be", "been", "being",
        "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "and", "or", "but", "not", "no", "so", "if", "my", "your",
        "his", "her", "its", "our", "their", "this", "that", "do",
        "does", "did", "will", "would", "can", "could", "should",
        "have", "has", "had", "me", "him", "us", "them", "the"
    }
    words = re.findall(r"[a-zA-Z']+", sentence)
    candidates = [w for w in words if w.lower() not in stopwords and len(w) > 2]
    if candidates:
        return max(candidates, key=len)
    return ""


def guess_pos(en, ko):
    """Guess part of speech."""
    if " " in en.strip():
        return ""
    ko_s = ko.strip()
    if ko_s.startswith("~을") or ko_s.startswith("~를") or "하다" in ko_s:
        return "v."
    if ko_s.endswith("한") or ko_s.endswith("된") or ko_s.endswith("적인") or ko_s.endswith("인"):
        return "a."
    if ko_s.endswith("게") or ko_s.endswith("히") or ko_s.endswith("으로"):
        return "adv."
    if en.endswith("ly"):
        return "adv."
    if en.endswith(("tion", "ment", "ness", "ity")):
        return "n."
    if en.endswith(("ful", "ous", "ive", "ed", "al")):
        return "a."
    return "n."


# ─── Main Generation ──────────────────────────────────────
def generate_lesson_data(raw_data, textbook_id, lesson_num):
    """Generate content.json and wordtest.json for one lesson."""
    content_text = raw_data.get("content", "")
    wordtest_text = raw_data.get("wordtest", "")
    grammar_text = raw_data.get("grammar", "")
    
    # 1. Extract words
    words = extract_words_from_wordtest(wordtest_text)
    
    # Add POS if missing
    for w in words:
        if not w.get("pos"):
            w["pos"] = guess_pos(w["en"], w["ko"])
    
    # Add example sentences from content
    add_example_sentences(words, content_text)
    
    # 2. Build wordtest.json
    wordtest_json = {
        "lessonInfo": {
            "textbook": textbook_id,
            "lesson": lesson_num,
            "title": f"Lesson {lesson_num}"
        },
        "words": words
    }
    
    # 3. Build content.json
    communication = extract_communication(content_text)
    reading = extract_reading(content_text)
    grammar = extract_grammar(content_text, grammar_text)
    
    content_json = {
        "lessonInfo": {
            "textbook": textbook_id,
            "lesson": lesson_num,
            "title": f"Lesson {lesson_num}"
        },
        "communication": communication,
        "reading": reading,
        "grammar": grammar
    }
    
    return content_json, wordtest_json


def process_textbook(textbook_id):
    """Process all lessons for a textbook."""
    raw_file = EXTRACTED_DIR / f"{textbook_id}_raw.json"
    if not raw_file.exists():
        print(f"[ERROR] Raw file not found: {raw_file}")
        return
    
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"Generating JSON for: {textbook_id}")
    print(f"{'='*60}")
    
    lessons_created = []
    
    for lesson_key in sorted(raw_data.keys()):
        lesson_num = int(lesson_key.replace("lesson", ""))
        lesson_data = raw_data[lesson_key]
        
        print(f"\n  Lesson {lesson_num}:")
        
        content_json, wordtest_json = generate_lesson_data(lesson_data, textbook_id, lesson_num)
        
        # Save files
        out_dir = OUTPUT_BASE / textbook_id / f"lesson{lesson_num}"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        content_path = out_dir / "content.json"
        wordtest_path = out_dir / "wordtest.json"
        
        with open(content_path, "w", encoding="utf-8") as f:
            json.dump(content_json, f, ensure_ascii=False, indent=2)
        
        with open(wordtest_path, "w", encoding="utf-8") as f:
            json.dump(wordtest_json, f, ensure_ascii=False, indent=2)
        
        # Stats
        word_count = len(wordtest_json.get("words", []))
        comm_expr = len(content_json.get("communication", {}).get("keyExpressions", []))
        comm_ex = len(content_json.get("communication", {}).get("exercises", []))
        read_pass = len(content_json.get("reading", {}).get("passages", []))
        read_ex = len(content_json.get("reading", {}).get("exercises", []))
        gram_pts = len(content_json.get("grammar", {}).get("points", []))
        gram_ex = len(content_json.get("grammar", {}).get("exercises", []))
        
        print(f"    Words: {word_count}")
        print(f"    Communication: {comm_expr} expressions, {comm_ex} exercises")
        print(f"    Reading: {read_pass} passages, {read_ex} exercises")
        print(f"    Grammar: {gram_pts} points, {gram_ex} exercises")
        print(f"    Saved: {out_dir}")
        
        lessons_created.append(lesson_num)
    
    return lessons_created


def main():
    textbooks = ["donga-lee-15", "donga-yoon-15", "neungyul-kim-15"]
    all_lessons = {}
    
    for tb in textbooks:
        lessons = process_textbook(tb)
        if lessons:
            all_lessons[tb] = lessons
    
    # Print final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    for tb, lessons in all_lessons.items():
        print(f"  {tb}: Lessons {lessons}")
    
    print(f"\nAll data saved to: {OUTPUT_BASE}")


if __name__ == "__main__":
    main()
