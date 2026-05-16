"""
server.py — Admin Dashboard 서버
폴더 스캔 → PDF 감지 → 자동 처리 → JSON 생성

사용법: python tools/server.py
→ http://localhost:8090/admin 에서 관리자 대시보드 접속
"""
import http.server
import json
import os
import sys
import traceback
import urllib.parse
from pathlib import Path
from io import BytesIO

# 프로젝트 루트 (english-study-app/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
TOOLS_DIR = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"

# 모듈 import
sys.path.insert(0, str(TOOLS_DIR))
from pdf_extractor import extract_text_from_pdf, detect_textbook
from content_generator import generate_all
from validate import validate_lesson_dir

PORT = 8090


class AdminHandler(http.server.SimpleHTTPRequestHandler):
    """관리자 대시보드 HTTP 핸들러"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/admin":
            self._serve_admin_page()
        elif parsed.path == "/api/textbooks":
            self._api_textbooks()
        elif parsed.path == "/api/existing":
            self._api_existing_lessons()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        body = self._read_body()

        if parsed.path == "/api/scan":
            self._api_scan(body)
        elif parsed.path == "/api/process":
            self._api_process(body)
        elif parsed.path == "/api/validate":
            self._api_validate(body)
        else:
            self._json_response({"error": "Not found"}, 404)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except:
            return {}

    def _json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_admin_page(self):
        admin_path = TOOLS_DIR / "admin.html"
        if admin_path.exists():
            content = admin_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._json_response({"error": "admin.html not found"}, 404)

    # ─── API Endpoints ─────────────────────────────

    def _api_textbooks(self):
        """교과서 목록 반환"""
        config_path = TOOLS_DIR / "textbook_config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self._json_response(config)

    def _api_existing_lessons(self):
        """이미 존재하는 레슨 데이터 목록"""
        existing = {}
        if DATA_DIR.exists():
            for tb_dir in DATA_DIR.iterdir():
                if tb_dir.is_dir():
                    lessons = []
                    for lesson_dir in sorted(tb_dir.iterdir()):
                        if lesson_dir.is_dir() and lesson_dir.name.startswith("lesson"):
                            num = lesson_dir.name.replace("lesson", "")
                            if num.isdigit():
                                has_content = (lesson_dir / "content.json").exists()
                                has_wordtest = (lesson_dir / "wordtest.json").exists()
                                lessons.append({
                                    "lesson": int(num),
                                    "hasContent": has_content,
                                    "hasWordtest": has_wordtest
                                })
                    existing[tb_dir.name] = lessons
        self._json_response(existing)

    def _api_scan(self, body):
        """폴더를 스캔하여 PDF 목록 + 자동 감지 결과 반환"""
        folder = body.get("folder", "")
        if not folder:
            self._json_response({"error": "folder 경로가 필요합니다"}, 400)
            return

        folder_path = Path(folder)
        if not folder_path.exists():
            self._json_response({"error": f"폴더가 존재하지 않습니다: {folder}"}, 400)
            return

        pdfs = list(folder_path.glob("*.pdf")) + list(folder_path.glob("**/*.pdf"))
        pdfs = sorted(set(pdfs))

        results = []
        for pdf in pdfs:
            try:
                # 빠른 감지를 위해 첫 2페이지만 읽기
                import fitz
                doc = fitz.open(str(pdf))
                preview_text = ""
                for i in range(min(2, len(doc))):
                    preview_text += doc[i].get_text("text")
                doc.close()

                detection = detect_textbook(pdf.name, preview_text)
                results.append({
                    "path": str(pdf),
                    "filename": pdf.name,
                    "size": pdf.stat().st_size,
                    "textbook": detection.get("textbook"),
                    "lesson": detection.get("lesson"),
                    "confidence": detection.get("confidence", 0),
                    "previewText": preview_text[:300]
                })
            except Exception as e:
                results.append({
                    "path": str(pdf),
                    "filename": pdf.name,
                    "size": pdf.stat().st_size,
                    "error": str(e)
                })

        self._json_response({
            "folder": str(folder_path),
            "totalPdfs": len(results),
            "files": results
        })

    def _api_process(self, body):
        """선택된 PDF들을 처리하여 JSON 생성"""
        files = body.get("files", [])
        if not files:
            self._json_response({"error": "처리할 파일이 없습니다"}, 400)
            return

        results = []
        for f in files:
            pdf_path = f.get("path")
            textbook = f.get("textbook")
            lesson = f.get("lesson")

            if not all([pdf_path, textbook, lesson]):
                results.append({
                    "file": pdf_path,
                    "status": "error",
                    "message": "textbook과 lesson 정보가 필요합니다"
                })
                continue

            try:
                # 1. PDF 추출
                extracted = extract_text_from_pdf(pdf_path)

                # 2. JSON 생성
                output_dir = str(DATA_DIR / textbook / f"lesson{lesson}")
                gen_result = generate_all(extracted, textbook, int(lesson), output_dir)

                # 3. 검증
                validation = validate_lesson_dir(output_dir)

                results.append({
                    "file": pdf_path,
                    "status": "success",
                    "output": output_dir,
                    "stats": gen_result["stats"],
                    "validation": validation
                })
            except Exception as e:
                results.append({
                    "file": pdf_path,
                    "status": "error",
                    "message": str(e),
                    "traceback": traceback.format_exc()
                })

        # schoolMap.js의 AVAILABLE_LESSONS 업데이트
        try:
            update_available_lessons()
        except Exception as e:
            print(f"Warning: schoolMap.js 업데이트 실패: {e}")

        self._json_response({
            "processed": len(results),
            "results": results
        })

    def _api_validate(self, body):
        """레슨 디렉토리 검증"""
        lesson_dir = body.get("lessonDir", "")
        if not lesson_dir:
            self._json_response({"error": "lessonDir이 필요합니다"}, 400)
            return
        result = validate_lesson_dir(lesson_dir)
        self._json_response(result)

    def log_message(self, format, *args):
        """콘솔 로그 (한글 지원)"""
        sys.stderr.write(f"[Admin] {args[0]} {args[1]} {args[2]}\n")


def update_available_lessons():
    """data/ 폴더를 스캔하여 schoolMap.js의 AVAILABLE_LESSONS 업데이트"""
    if not DATA_DIR.exists():
        return

    available = {}
    for tb_dir in DATA_DIR.iterdir():
        if tb_dir.is_dir():
            lessons = []
            for lesson_dir in sorted(tb_dir.iterdir()):
                if lesson_dir.is_dir() and lesson_dir.name.startswith("lesson"):
                    num = lesson_dir.name.replace("lesson", "")
                    if num.isdigit():
                        # content.json 또는 wordtest.json이 있으면 유효
                        if (lesson_dir / "content.json").exists() or (lesson_dir / "wordtest.json").exists():
                            lessons.append(int(num))
            available[tb_dir.name] = sorted(lessons)

    # schoolMap.js 업데이트
    schoolmap_path = PROJECT_ROOT / "js" / "schoolMap.js"
    if schoolmap_path.exists():
        content = schoolmap_path.read_text(encoding="utf-8")

        # AVAILABLE_LESSONS 블록 교체
        new_block = "const AVAILABLE_LESSONS = " + json.dumps(available, indent=2) + ";"

        import re
        content = re.sub(
            r'const AVAILABLE_LESSONS\s*=\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\};',
            new_block,
            content
        )
        schoolmap_path.write_text(content, encoding="utf-8")
        print(f"✅ schoolMap.js AVAILABLE_LESSONS 업데이트됨: {available}")


def main():
    print(f"""
╔══════════════════════════════════════════╗
║  📚 영어 학습 콘텐츠 관리자 대시보드     ║
║                                          ║
║  http://localhost:{PORT}/admin              ║
║                                          ║
║  Ctrl+C 로 종료                          ║
╚══════════════════════════════════════════╝
    """)
    print(f"프로젝트 루트: {PROJECT_ROOT}")
    print(f"데이터 폴더: {DATA_DIR}")
    print()

    server = http.server.HTTPServer(("", PORT), AdminHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버 종료")
        server.server_close()


if __name__ == "__main__":
    main()
