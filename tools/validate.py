"""
validate.py — 생성된 JSON 파일의 스키마 검증
"""
import json
import sys
from pathlib import Path


def validate_wordtest(filepath: str) -> list:
    """wordtest.json 검증"""
    errors = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"JSON 파싱 오류: {e}"]

    # lessonInfo 확인
    if "lessonInfo" not in data:
        errors.append("lessonInfo 누락")
    else:
        for field in ["textbook", "lesson", "title"]:
            if field not in data["lessonInfo"]:
                errors.append(f"lessonInfo.{field} 누락")

    # words 확인
    if "words" not in data:
        errors.append("words 배열 누락")
        return errors

    words = data["words"]
    if not isinstance(words, list):
        errors.append("words가 배열이 아닙니다")
        return errors

    if len(words) == 0:
        errors.append("words가 비어있습니다")

    for i, w in enumerate(words):
        if "en" not in w:
            errors.append(f"words[{i}]: 'en' 필드 누락")
        if "ko" not in w:
            errors.append(f"words[{i}]: 'ko' 필드 누락")
        if w.get("en") and len(w["en"].strip()) < 1:
            errors.append(f"words[{i}]: 'en' 비어있음")
        if w.get("ko") and len(w["ko"].strip()) < 1:
            errors.append(f"words[{i}]: 'ko' 비어있음")

    return errors


def validate_content(filepath: str) -> list:
    """content.json 검증"""
    errors = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"JSON 파싱 오류: {e}"]

    # lessonInfo
    if "lessonInfo" not in data:
        errors.append("lessonInfo 누락")

    # sections 확인
    valid_types = {"fill-blank", "multi-choice", "true-false", "word-order", "error-correction"}

    for section in ["communication", "reading", "grammar"]:
        if section not in data:
            errors.append(f"'{section}' 섹션 누락")
            continue

        sec = data[section]

        if section == "communication":
            if "keyExpressions" not in sec:
                errors.append(f"{section}.keyExpressions 누락")
            elif isinstance(sec["keyExpressions"], list):
                for i, ke in enumerate(sec["keyExpressions"]):
                    if "en" not in ke:
                        errors.append(f"{section}.keyExpressions[{i}]: 'en' 누락")
                    if "ko" not in ke:
                        errors.append(f"{section}.keyExpressions[{i}]: 'ko' 누락")

        if section == "reading":
            if "passages" not in sec:
                errors.append(f"{section}.passages 누락")
            elif isinstance(sec["passages"], list):
                for i, p in enumerate(sec["passages"]):
                    if "en" not in p:
                        errors.append(f"{section}.passages[{i}]: 'en' 누락")

        if "exercises" not in sec:
            errors.append(f"{section}.exercises 누락")
        elif isinstance(sec["exercises"], list):
            for i, ex in enumerate(sec["exercises"]):
                if "type" not in ex:
                    errors.append(f"{section}.exercises[{i}]: 'type' 누락")
                elif ex["type"] not in valid_types:
                    errors.append(f"{section}.exercises[{i}]: 잘못된 type '{ex['type']}'")

                if ex.get("type") in {"fill-blank", "multi-choice", "true-false"}:
                    if "q" not in ex:
                        errors.append(f"{section}.exercises[{i}]: 'q' 누락")
                    if "a" not in ex:
                        errors.append(f"{section}.exercises[{i}]: 'a' 누락")

                if ex.get("type") == "word-order":
                    if "words" not in ex:
                        errors.append(f"{section}.exercises[{i}]: 'words' 누락")
                    if "a" not in ex:
                        errors.append(f"{section}.exercises[{i}]: 'a' 누락")

                if ex.get("type") == "error-correction":
                    if "wrong" not in ex:
                        errors.append(f"{section}.exercises[{i}]: 'wrong' 누락")

    return errors


def validate_lesson_dir(lesson_dir: str) -> dict:
    """레슨 디렉토리의 모든 JSON 검증"""
    d = Path(lesson_dir)
    results = {"valid": True, "errors": {}}

    wordtest_path = d / "wordtest.json"
    content_path = d / "content.json"

    if wordtest_path.exists():
        errs = validate_wordtest(str(wordtest_path))
        if errs:
            results["valid"] = False
            results["errors"]["wordtest.json"] = errs
    else:
        results["valid"] = False
        results["errors"]["wordtest.json"] = ["파일 없음"]

    if content_path.exists():
        errs = validate_content(str(content_path))
        if errs:
            results["valid"] = False
            results["errors"]["content.json"] = errs
    else:
        results["valid"] = False
        results["errors"]["content.json"] = ["파일 없음"]

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate.py <lesson_directory>")
        sys.exit(1)

    results = validate_lesson_dir(sys.argv[1])
    if results["valid"]:
        print("✅ 모든 검증 통과!")
    else:
        print("❌ 검증 실패:")
        for file, errs in results["errors"].items():
            print(f"\n  📄 {file}:")
            for e in errs:
                print(f"    ⚠️ {e}")
        sys.exit(1)
