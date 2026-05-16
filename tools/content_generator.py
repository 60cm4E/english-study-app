"""
content_generator.py — 추출된 텍스트를 content.json + wordtest.json으로 변환
10개 학습 모듈에 맞는 문제를 자동 생성합니다.
"""
import json
import random
import re
from pathlib import Path


def generate_all(extracted: dict, textbook_id: str, lesson_num: int, output_dir: str) -> dict:
    """추출된 데이터로 content.json + wordtest.json 생성"""
    sections = extracted.get("sections", {})

    # 1) wordtest.json 생성
    wordtest = generate_wordtest(sections, textbook_id, lesson_num)

    # 2) content.json 생성
    content = generate_content(sections, textbook_id, lesson_num)

    # 3) 파일 저장
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    wordtest_path = out / "wordtest.json"
    content_path = out / "content.json"

    with open(wordtest_path, "w", encoding="utf-8") as f:
        json.dump(wordtest, f, ensure_ascii=False, indent=2)

    with open(content_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    return {
        "wordtest": str(wordtest_path),
        "content": str(content_path),
        "stats": {
            "words": len(wordtest.get("words", [])),
            "communication_exercises": len(content.get("communication", {}).get("exercises", [])),
            "communication_keyExpressions": len(content.get("communication", {}).get("keyExpressions", [])),
            "reading_passages": len(content.get("reading", {}).get("passages", [])),
            "reading_exercises": len(content.get("reading", {}).get("exercises", [])),
            "grammar_points": len(content.get("grammar", {}).get("points", [])),
            "grammar_exercises": len(content.get("grammar", {}).get("exercises", []))
        }
    }


def generate_wordtest(sections: dict, textbook_id: str, lesson_num: int) -> dict:
    """단어 데이터 생성 (FlashCard, SpellingQuiz, MatchGame용)"""
    raw_words = sections.get("words", [])
    sentences = sections.get("sentences", [])

    words = []
    for w in raw_words:
        entry = {
            "en": w["en"].strip(),
            "ko": w["ko"].strip(),
        }
        if w.get("pos"):
            entry["pos"] = w["pos"]

        # 예문 매칭: sentences에서 해당 단어가 포함된 문장 찾기
        ex = find_example_sentence(w["en"], sentences)
        if ex:
            entry["ex"] = ex

        words.append(entry)

    return {
        "lessonInfo": {
            "textbook": textbook_id,
            "lesson": lesson_num,
            "title": f"Lesson {lesson_num}"
        },
        "words": words
    }


def find_example_sentence(word: str, sentences: list) -> str:
    """단어가 포함된 예문을 찾습니다."""
    word_lower = word.lower()
    for s in sentences:
        if word_lower in s.get("en", "").lower():
            return s["en"]
    return ""


def generate_content(sections: dict, textbook_id: str, lesson_num: int) -> dict:
    """content.json 생성 (7개 문제 유형 모듈용)"""
    words = sections.get("words", [])
    sentences = sections.get("sentences", [])
    passages = sections.get("passages", [])
    grammar = sections.get("grammar_patterns", [])

    content = {
        "lessonInfo": {
            "textbook": textbook_id,
            "lesson": lesson_num,
            "title": f"Lesson {lesson_num}"
        },
        "communication": {
            "keyExpressions": generate_key_expressions(sentences),
            "exercises": []
        },
        "reading": {
            "passages": generate_reading_passages(passages, sentences),
            "exercises": []
        },
        "grammar": {
            "points": generate_grammar_points(grammar),
            "exercises": []
        }
    }

    # 의사소통 문제 생성
    content["communication"]["exercises"] = generate_comm_exercises(
        content["communication"]["keyExpressions"], words
    )

    # 리딩 문제 생성
    content["reading"]["exercises"] = generate_reading_exercises(
        content["reading"]["passages"], sentences
    )

    # 문법 문제 생성
    content["grammar"]["exercises"] = generate_grammar_exercises(
        sentences, words, grammar
    )

    return content


# ─── Key Expressions ─────────────────────────────────

def generate_key_expressions(sentences: list) -> list:
    """의사소통 핵심 표현 생성"""
    expressions = []
    for s in sentences[:15]:  # 최대 15개
        if s.get("en") and s.get("ko"):
            cat = guess_expression_category(s["en"])
            expressions.append({
                "en": s["en"],
                "ko": s["ko"],
                "category": cat
            })
    return expressions


def guess_expression_category(en: str) -> str:
    """표현의 카테고리를 추정합니다."""
    en_lower = en.lower()
    if any(kw in en_lower for kw in ["hope", "wish", "want"]):
        return "희망 표현"
    if any(kw in en_lower for kw in ["don't worry", "relax", "take it easy", "no worries"]):
        return "안심시키기"
    if any(kw in en_lower for kw in ["thank", "thanks", "grateful"]):
        return "감사"
    if any(kw in en_lower for kw in ["sorry", "apologize", "excuse"]):
        return "사과"
    if any(kw in en_lower for kw in ["could you", "would you", "can you", "please"]):
        return "요청"
    if any(kw in en_lower for kw in ["should", "had better", "why don't"]):
        return "조언"
    if any(kw in en_lower for kw in ["let's", "how about", "shall we"]):
        return "제안"
    if "?" in en:
        return "질문"
    return "일반 표현"


# ─── Reading Passages ─────────────────────────────────

def generate_reading_passages(raw_passages: list, sentences: list) -> list:
    """리딩 본문 데이터 생성"""
    results = []

    for i, passage in enumerate(raw_passages[:5]):  # 최대 5개 본문
        # 해당 본문에 대응하는 한글 번역 찾기
        ko_translation = find_korean_translation(passage, sentences)
        results.append({
            "id": f"r{i + 1}",
            "title": f"본문❷ - {i + 1}",
            "en": passage.strip(),
            "ko": ko_translation
        })

    # 본문이 없으면 문장 쌍에서 생성
    if not results and sentences:
        combined_en = " ".join(s["en"] for s in sentences[:10] if s.get("en"))
        combined_ko = " ".join(s["ko"] for s in sentences[:10] if s.get("ko"))
        if combined_en:
            results.append({
                "id": "r1",
                "title": "본문",
                "en": combined_en,
                "ko": combined_ko
            })

    return results


def find_korean_translation(en_passage: str, sentences: list) -> str:
    """영어 본문에 대응하는 한글 번역을 찾습니다."""
    ko_parts = []
    en_sentences_in_passage = re.split(r'(?<=[.!?])\s+', en_passage)

    for en_sent in en_sentences_in_passage:
        for pair in sentences:
            if pair.get("en") and en_sent.strip() in pair["en"]:
                ko_parts.append(pair.get("ko", ""))
                break

    return " ".join(ko_parts) if ko_parts else ""


# ─── Grammar Points ─────────────────────────────────

def generate_grammar_points(grammar_patterns: list) -> list:
    """문법 포인트 생성"""
    points = []
    for i, g in enumerate(grammar_patterns[:4]):  # 최대 4개
        points.append({
            "id": f"g{i + 1}",
            "title": g["term"],
            "explanation": f"{g['term']}에 관한 설명입니다.",
            "examples": []
        })
    return points


# ─── Exercise Generators ─────────────────────────────────

def generate_comm_exercises(key_expressions: list, words: list) -> list:
    """의사소통 섹션 문제 생성"""
    exercises = []

    for expr in key_expressions:
        en = expr["en"]
        # fill-blank: 핵심 단어 하나를 빈칸으로
        key_word = find_key_word(en)
        if key_word:
            blanked = en.replace(key_word, "___", 1)
            distractors = generate_distractors(key_word, words)
            ex = {"type": "fill-blank", "q": blanked, "a": key_word}
            if distractors:
                ex["opts"] = [key_word] + distractors[:2]
            exercises.append(ex)

    # multi-choice 추가
    for expr in key_expressions[:5]:
        en = expr["en"]
        key_word = find_key_word(en)
        if key_word and len(key_word) > 2:
            distractors = generate_distractors(key_word, words)
            if distractors:
                exercises.append({
                    "type": "multi-choice",
                    "q": en.replace(key_word, f"({' / '.join([key_word] + distractors[:1])})", 1),
                    "a": key_word,
                    "opts": [key_word] + distractors[:2]
                })

    # true-false 추가
    for expr in key_expressions[:5]:
        if expr.get("ko") and expr.get("en"):
            exercises.append({
                "type": "true-false",
                "q": f'"{expr["en"]}"의 의미는 "{expr["ko"]}"이다.',
                "a": True
            })

    return exercises


def generate_reading_exercises(passages: list, sentences: list) -> list:
    """리딩 섹션 문제 생성"""
    exercises = []

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

        # true-false from passage
        if p.get("ko"):
            exercises.append({
                "type": "true-false",
                "q": p["ko"][:60] + ("..." if len(p["ko"]) > 60 else ""),
                "a": True,
                "exp": "본문 내용과 일치"
            })

    return exercises


def generate_grammar_exercises(sentences: list, words: list, grammar_patterns: list) -> list:
    """문법 섹션 문제 생성"""
    exercises = []

    # word-order: 문장의 단어를 섞어서 배열 문제 생성
    for s in sentences[:6]:
        en = s.get("en", "")
        if 4 <= len(en.split()) <= 12:
            word_list = en.rstrip(".!?").split()
            exercises.append({
                "type": "word-order",
                "words": word_list,
                "a": en
            })

    # error-correction: 일반적인 문법 오류 패턴 적용
    error_patterns = [
        (r'\binterested\b', "interesting", "interested", "감정을 느끼는 주체는 -ed"),
        (r'\bexcited\b', "exciting", "excited", "감정을 느끼는 주체는 -ed"),
        (r'\bto (\w+)\b', lambda m: m.group(1) + "ing", lambda m: "to " + m.group(1), "to부정사: to+동사원형"),
    ]

    for s in sentences[:10]:
        en = s.get("en", "")
        for pattern, wrong_fn, correct_fn, exp in error_patterns:
            match = re.search(pattern, en)
            if match:
                if callable(wrong_fn):
                    wrong = wrong_fn(match)
                    correct = correct_fn(match)
                else:
                    wrong = wrong_fn
                    correct = correct_fn

                wrong_sentence = en[:match.start()] + wrong + en[match.end():]
                exercises.append({
                    "type": "error-correction",
                    "q": wrong_sentence,
                    "a": correct,
                    "wrong": wrong,
                    "exp": exp
                })
                break  # 한 문장에서 하나만

    return exercises


# ─── Utility Functions ─────────────────────────────────

def find_key_word(sentence: str) -> str:
    """문장에서 빈칸으로 만들기 적합한 핵심 단어를 찾습니다."""
    # 불용어 제외
    stopwords = {
        "i", "you", "he", "she", "it", "we", "they", "a", "an", "the",
        "is", "am", "are", "was", "were", "be", "been", "being",
        "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "and", "or", "but", "not", "no", "so", "if", "my", "your",
        "his", "her", "its", "our", "their", "this", "that", "do",
        "does", "did", "will", "would", "can", "could", "should",
        "have", "has", "had", "me", "him", "us", "them"
    }

    words = re.findall(r"[a-zA-Z']+", sentence)
    candidates = [w for w in words if w.lower() not in stopwords and len(w) > 2]

    if candidates:
        # 가장 긴 단어를 선택 (보통 핵심 어휘)
        return max(candidates, key=len)
    return ""


def generate_distractors(correct: str, words: list) -> list:
    """오답 선택지를 생성합니다."""
    distractors = []
    correct_lower = correct.lower()

    # 같은 품사/비슷한 길이의 다른 단어
    for w in words:
        w_en = w["en"].strip().lower()
        if w_en != correct_lower and abs(len(w_en) - len(correct_lower)) < 5:
            distractors.append(w["en"].strip())
            if len(distractors) >= 3:
                break

    # 부족하면 일반 오답 추가
    fallbacks = ["always", "never", "sometimes", "together", "carefully",
                 "different", "important", "interesting", "beautiful", "special"]
    for fb in fallbacks:
        if fb.lower() != correct_lower and len(distractors) < 3:
            distractors.append(fb)

    return distractors[:3]


if __name__ == "__main__":
    print("content_generator.py — 직접 실행하려면 server.py를 사용하세요.")
