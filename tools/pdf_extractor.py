"""
pdf_extractor.py — PDF 텍스트 추출 + 구조 분석
PyMuPDF(fitz) 사용, 텍스트 블록 단위로 추출하여 섹션별 분리
"""
import fitz  # PyMuPDF
import re
import json
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> dict:
    """PDF에서 텍스트를 추출하고 구조를 분석합니다."""
    doc = fitz.open(pdf_path)
    pages = []
    full_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        pages.append({
            "page": page_num + 1,
            "text": text.strip()
        })
        full_text.append(text)

    doc.close()
    raw_text = "\n".join(full_text)

    return {
        "file": str(pdf_path),
        "totalPages": len(pages),
        "pages": pages,
        "rawText": raw_text,
        "sections": analyze_sections(raw_text)
    }


def analyze_sections(text: str) -> dict:
    """텍스트에서 교과서 섹션을 자동 분류합니다."""
    sections = {
        "words": extract_word_candidates(text),
        "sentences": extract_sentence_pairs(text),
        "grammar_patterns": extract_grammar_patterns(text),
        "passages": extract_passages(text)
    }
    return sections


def extract_word_candidates(text: str) -> list:
    """영어 단어 + 한글 뜻 패턴을 찾습니다."""
    words = []
    seen = set()

    # 패턴 1: "english_word    한글뜻" (탭/공백 구분)
    p1 = re.findall(
        r'([a-zA-Z][a-zA-Z\s\'\-]{1,30}?)\s{2,}([가-힣][가-힣\s,~·()（）]{1,40})',
        text
    )
    for en, ko in p1:
        en = en.strip()
        ko = ko.strip()
        if len(en) >= 2 and en.lower() not in seen:
            seen.add(en.lower())
            words.append({"en": en, "ko": ko})

    # 패턴 2: "english_word — 한글뜻" 또는 "english_word - 한글뜻"
    p2 = re.findall(
        r'([a-zA-Z][a-zA-Z\s\'\-]{1,30}?)\s*[—\-–]\s*([가-힣][가-힣\s,~·()（）]{1,40})',
        text
    )
    for en, ko in p2:
        en = en.strip()
        ko = ko.strip()
        if len(en) >= 2 and en.lower() not in seen:
            seen.add(en.lower())
            words.append({"en": en, "ko": ko})

    # 패턴 3: 번호 + 영어 + 한글 (교과서 단어장 형태)
    p3 = re.findall(
        r'\d+[.)]\s*([a-zA-Z][a-zA-Z\s\'\-]{1,30}?)\s+([가-힣][가-힣\s,~·()（）]{1,40})',
        text
    )
    for en, ko in p3:
        en = en.strip()
        ko = ko.strip()
        if len(en) >= 2 and en.lower() not in seen:
            seen.add(en.lower())
            words.append({"en": en, "ko": ko})

    # 품사 추정
    for w in words:
        w["pos"] = guess_pos(w["en"], w["ko"])

    return words


def guess_pos(en: str, ko: str) -> str:
    """품사를 추정합니다."""
    if " " in en.strip():
        return ""  # 구 (phrase)
    ko_lower = ko.strip()
    if ko_lower.startswith("~을") or ko_lower.startswith("~를") or "하다" in ko_lower:
        return "v."
    if ko_lower.endswith("한") or ko_lower.endswith("된") or ko_lower.endswith("적인") or ko_lower.endswith("인"):
        return "a."
    if ko_lower.endswith("게") or ko_lower.endswith("히") or ko_lower.endswith("으로"):
        return "adv."
    if en.endswith("ly"):
        return "adv."
    if en.endswith("tion") or en.endswith("ment") or en.endswith("ness") or en.endswith("ity"):
        return "n."
    if en.endswith("ful") or en.endswith("ous") or en.endswith("ive") or en.endswith("ed"):
        return "a."
    return "n."


def extract_sentence_pairs(text: str) -> list:
    """영어-한글 문장 쌍을 추출합니다."""
    pairs = []

    # 영어 문장 다음에 한글 문장이 오는 패턴
    lines = text.split("\n")
    i = 0
    while i < len(lines) - 1:
        en_line = lines[i].strip()
        ko_line = lines[i + 1].strip()

        # 영어 문장 감지: 알파벳으로 시작, 마침표/물음표/느낌표로 끝남
        if (re.match(r'^[A-Z]', en_line) and
            re.search(r'[.!?]$', en_line) and
            len(en_line) > 15 and
            # 한글 문장 감지
            re.match(r'^[가-힣]', ko_line) and
            len(ko_line) > 5):
            pairs.append({"en": en_line, "ko": ko_line})
            i += 2
            continue
        i += 1

    return pairs


def extract_grammar_patterns(text: str) -> list:
    """문법 관련 패턴을 추출합니다."""
    patterns = []

    # 문법 용어 감지
    grammar_terms = [
        "to부정사", "동명사", "관계대명사", "수동태", "현재완료",
        "비교급", "최상급", "접속사", "전치사", "분사",
        "간접의문문", "가정법", "사역동사", "지각동사", "감탄문",
        "목적격보어", "형용사적", "부사적", "명사적", "관계부사",
        "used to", "be going to", "have to", "had better",
        "too...to", "enough to", "so...that", "such...that",
        "make + O + C", "let + O + V", "help + O + V",
        "It...to", "It...that", "what", "how"
    ]

    for term in grammar_terms:
        if term in text:
            # 해당 문법 용어 주변 텍스트 추출
            idx = text.find(term)
            context_start = max(0, idx - 100)
            context_end = min(len(text), idx + 200)
            context = text[context_start:context_end].strip()
            patterns.append({
                "term": term,
                "context": context
            })

    return patterns


def extract_passages(text: str) -> list:
    """긴 영어 문단(본문)을 추출합니다."""
    passages = []

    # 연속된 영어 문장 블록 감지
    blocks = re.split(r'\n\s*\n', text)
    for block in blocks:
        block = block.strip()
        # 영어 문장이 주로 포함된 블록 (단어 수 50+, 영문 비율 70%+)
        en_chars = sum(1 for c in block if c.isascii() and c.isalpha())
        total_chars = sum(1 for c in block if c.isalpha())
        if total_chars > 0 and en_chars / total_chars > 0.7 and len(block.split()) > 40:
            passages.append(block)

    return passages


def detect_textbook(filename: str, text: str) -> dict:
    """파일명과 내용으로 교과서를 추정합니다."""
    filename_lower = filename.lower()
    result = {"textbook": None, "lesson": None, "confidence": 0}

    # 교과서 감지 규칙
    textbook_rules = [
        (["동아", "윤정미"], ["22개정", "2022"], "donga-yoon-22"),
        (["동아", "윤정미"], ["15개정", "2015", "중3"], "donga-yoon-15"),
        (["ybm", "박준언"], [], "ybm-park-22"),
        (["동아", "이병민"], [], "donga-lee-15"),
        (["능률", "김성곤"], [], "neungyul-kim-15"),
    ]

    combined = filename + " " + text[:500]
    for primary_kw, secondary_kw, tb_id in textbook_rules:
        if any(kw in combined for kw in primary_kw):
            result["textbook"] = tb_id
            result["confidence"] = 0.5
            if secondary_kw and any(kw in combined for kw in secondary_kw):
                result["confidence"] = 0.9
            elif not secondary_kw:
                result["confidence"] = 0.7
            break

    # Lesson 번호 감지
    lesson_match = re.search(r'[Ll]esson\s*(\d+)', combined)
    if not lesson_match:
        lesson_match = re.search(r'(\d+)\s*과', combined)
    if not lesson_match:
        lesson_match = re.search(r'[Ll](\d+)', filename)
    if lesson_match:
        result["lesson"] = int(lesson_match.group(1))

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <pdf_path>")
        sys.exit(1)

    result = extract_text_from_pdf(sys.argv[1])
    print(f"Pages: {result['totalPages']}")
    print(f"Words found: {len(result['sections']['words'])}")
    print(f"Sentence pairs: {len(result['sections']['sentences'])}")
    print(f"Grammar patterns: {len(result['sections']['grammar_patterns'])}")
    print(f"Passages: {len(result['sections']['passages'])}")

    detection = detect_textbook(Path(sys.argv[1]).name, result['rawText'])
    print(f"Detected textbook: {detection}")
