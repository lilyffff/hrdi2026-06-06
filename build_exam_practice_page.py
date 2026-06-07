from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import fitz

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional fallback
    PdfReader = None


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "generated_exam_page"
ASSET_DIR = OUT_DIR / "assets"
OUT_HTML = OUT_DIR / "2026_06_g1_math_practice.html"
ANSWER_PDF_NAME = "answer_explanation.pdf"
TOTAL_PROBLEMS = 30
TOP_MARGIN_PX = 100
EXAM_MINUTES = 50
SHORT_ANSWER_RE = re.compile(r"\(([가-힣])\)")
POINT_RE = re.compile(r"\[([0-9])점\]")
EXPLANATION_START_RE = re.compile(r"^([1-9]|[12][0-9]|30)\. \[출제의도\]")
EXPLANATION_COLUMN_BOUNDS = [
    (45, 220),
    (215, 375),
    (375, 555),
]
CIRCLED_CHOICE_MAP = {
    "①": "1",
    "②": "2",
    "③": "3",
    "④": "4",
    "⑤": "5",
}
PDF_DIGIT_MAP = {
    chr(0xE034): "1",
    chr(0xE035): "2",
    chr(0xE036): "3",
    chr(0xE037): "4",
    chr(0xE038): "5",
    chr(0xE039): "6",
    chr(0xE03A): "7",
    chr(0xE03B): "8",
    chr(0xE03C): "9",
    chr(0xE03D): "0",
}
DEFAULT_SHORT_ANSWER_LABELS = {
    14: ["가", "나", "다"],
    22: ["정답"],
    23: ["정답"],
    24: ["정답"],
    25: ["정답"],
    26: ["정답"],
    27: ["정답"],
    28: ["정답"],
    29: ["정답"],
    30: ["정답"],
}
DEFAULT_EXAM_NAME = "2026학년도 6월 고1 전국연합학력평가 문제지.pdf"


PAGE_IMAGE_RECTS: dict[int, tuple[int, float, float, float, float]] = {
    1: (1, 0, 55, 535, 225),
    2: (1, 0, 635, 535, 875),
    3: (1, 555, 0, 1088, 225),
    4: (1, 555, 635, 1088, 875),
    5: (2, 0, 0, 535, 270),
    6: (2, 0, 710, 535, 985),
    7: (2, 555, 0, 1088, 270),
    8: (3, 0, 0, 535, 245),
    9: (3, 0, 710, 535, 1025),
    10: (3, 555, 0, 1088, 245),
    11: (4, 0, 0, 535, 260),
    12: (4, 555, 0, 1088, 450),
    13: (5, 0, 0, 535, 265),
    14: (5, 555, 0, 1088, 825),
    15: (6, 0, 0, 535, 285),
    16: (6, 555, 0, 1088, 350),
    17: (7, 0, 0, 535, 280),
    18: (7, 555, 0, 1088, 650),
    19: (8, 0, 0, 535, 310),
    20: (8, 555, 0, 1088, 310),
    21: (9, 0, 0, 535, 330),
    22: (9, 555, 80, 1088, 260),
    23: (9, 555, 700, 1088, 850),
    24: (10, 0, 0, 535, 230),
    25: (10, 0, 660, 535, 940),
    26: (10, 555, 0, 1088, 260),
    27: (11, 0, 0, 535, 660),
    28: (11, 555, 0, 1088, 270),
    29: (12, 0, 0, 535, 310),
    30: (12, 555, 0, 1088, 310),
}


def find_question_pdf() -> Path | None:
    local_candidates = sorted(ROOT.glob("*문제지.pdf"))
    if local_candidates:
        return local_candidates[0]

    downloads = Path.home() / "Downloads"
    candidates = []
    for pdf in downloads.glob("*.pdf"):
        name = pdf.name
        if "2026" in name and "6" in name and "1" in name:
            candidates.append(pdf)
    for pdf in candidates:
        if "문제지" in pdf.name:
            return pdf
    return candidates[0] if candidates else None


def find_answer_pdf() -> Path | None:
    local_candidates = sorted(ROOT.glob("*해설지.pdf"))
    if local_candidates:
        return local_candidates[0]

    downloads = Path.home() / "Downloads"
    candidates = []
    for pdf in downloads.glob("*.pdf"):
        name = pdf.name
        if "2026" in name and "6" in name and "1" in name and "해설지" in name:
            candidates.append(pdf)
    return candidates[0] if candidates else None


def publish_answer_pdf(answer_pdf_path: Path | None) -> str:
    if answer_pdf_path is None:
        return ""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUT_DIR / ANSWER_PDF_NAME
    shutil.copyfile(answer_pdf_path, target)
    return ANSWER_PDF_NAME


def read_pdf_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    return "\n".join(page.get_text() for page in doc)


def normalize_answer_token(token: str) -> str:
    token = token.strip()
    if token in CIRCLED_CHOICE_MAP:
        return CIRCLED_CHOICE_MAP[token]
    normalized = "".join(PDF_DIGIT_MAP.get(char, char) for char in token)
    return re.sub(r"\s+", "", normalized)


def extract_answer_key(answer_pdf_path: Path | None) -> dict[int, str]:
    if answer_pdf_path is None:
        return {}

    text = read_pdf_text(answer_pdf_path)
    start = text.find("정 답")
    end = text.find("해 설", start)
    table_text = text[start:end if end != -1 else len(text)]
    token_chars = "①②③④⑤" + "".join(PDF_DIGIT_MAP)
    pair_re = re.compile(
        rf"(?:^|\n)\s*([1-9]|[12][0-9]|30)\s*(?:\n|\s+)\s*([{re.escape(token_chars)}0-9]+)"
    )

    answers: dict[int, str] = {}
    for number_text, token in pair_re.findall(table_text):
        number = int(number_text)
        if 1 <= number <= TOTAL_PROBLEMS:
            answers[number] = normalize_answer_token(token)
    return answers


def extract_problem_scores(question_pdf_path: Path | None) -> dict[int, int]:
    if question_pdf_path is None:
        return {}

    points = POINT_RE.findall(read_pdf_text(question_pdf_path))
    return {
        number: int(point)
        for number, point in enumerate(points[:TOTAL_PROBLEMS], start=1)
    }


def explanation_column_index(x0: float) -> int:
    for index, (left, right) in enumerate(EXPLANATION_COLUMN_BOUNDS):
        if left <= x0 < right:
            return index
    return min(
        range(len(EXPLANATION_COLUMN_BOUNDS)),
        key=lambda index: abs(EXPLANATION_COLUMN_BOUNDS[index][0] - x0),
    )


def collect_explanation_starts(answer_pdf_path: Path) -> list[dict[str, object]]:
    starts: list[dict[str, object]] = []
    doc = fitz.open(str(answer_pdf_path))
    for page_index, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(span["text"] for span in line["spans"]).strip()
                match = EXPLANATION_START_RE.match(text)
                if not match:
                    continue

                x0, y0, x1, y1 = line["bbox"]
                starts.append(
                    {
                        "number": int(match.group(1)),
                        "page_index": page_index,
                        "column": explanation_column_index(x0),
                        "bbox": (x0, y0, x1, y1),
                    }
                )
    return sorted(starts, key=lambda item: int(item["number"]))


def render_explanation_images(answer_pdf_path: Path | None) -> dict[int, dict[str, object]]:
    if answer_pdf_path is None:
        return {}

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(answer_pdf_path))
    starts = collect_explanation_starts(answer_pdf_path)
    grouped: dict[tuple[int, int], list[dict[str, object]]] = {}
    for item in starts:
        grouped.setdefault((int(item["page_index"]), int(item["column"])), []).append(item)

    explanations: dict[int, dict[str, object]] = {}
    for group in grouped.values():
        group.sort(key=lambda item: item["bbox"][1])
        for index, item in enumerate(group):
            number = int(item["number"])
            page = doc[int(item["page_index"])]
            column = int(item["column"])
            x0, x1 = EXPLANATION_COLUMN_BOUNDS[column]
            if number in {29, 30}:
                x1 = min(page.rect.width - 35, 555)
            _, y0, _, _ = item["bbox"]
            if index + 1 < len(group):
                next_y = group[index + 1]["bbox"][1]
            else:
                next_y = page.rect.height - 70

            top_padding = 0 if number == 30 else 2
            clip = fitz.Rect(x0, max(0, y0 - top_padding), x1, min(page.rect.height, next_y - 6))
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip, alpha=False)
            image_name = f"explanation_{number:02d}.png"
            pix.save(str(ASSET_DIR / image_name))
            explanations[number] = {
                "image": f"assets/{image_name}",
                "width": pix.width,
                "height": pix.height,
            }

    return explanations


def split_problem_texts(pdf_path: Path) -> dict[int, str]:
    if PdfReader is None:
        return {}
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:
        return {}

    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    matches = list(re.finditer(r"(?m)(?:^|\n)\s*([1-9]|[12][0-9]|30)\s*\.", text))
    problems: dict[int, str] = {}
    for idx, match in enumerate(matches):
        number = int(match.group(1))
        if not 1 <= number <= TOTAL_PROBLEMS:
            continue
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        problems[number] = text[start:end]
    return problems


def detect_short_answer_numbers(pdf_path: Path | None) -> dict[int, list[str]]:
    detected: dict[int, list[str]] = {}
    if pdf_path is not None:
        for number, text in split_problem_texts(pdf_path).items():
            labels = sorted(set(SHORT_ANSWER_RE.findall(text)))
            if labels:
                detected[number] = labels

    detected.pop(21, None)
    for number, labels in DEFAULT_SHORT_ANSWER_LABELS.items():
        if number >= 22:
            detected[number] = labels
        else:
            detected.setdefault(number, labels)

    return {
        number: labels
        for number, labels in detected.items()
        if 1 <= number <= TOTAL_PROBLEMS
    }


def render_problem_images(
    short_answers: dict[int, list[str]],
    answer_key: dict[int, str],
    scores: dict[int, int],
    explanations: dict[int, dict[str, object]],
) -> list[dict[str, object]]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    problems: list[dict[str, object]] = []

    for number in range(1, TOTAL_PROBLEMS + 1):
        page_no, x0, y0, x1, y1 = PAGE_IMAGE_RECTS[number]
        page_image = ASSET_DIR / f"page_{page_no:02d}_problems.png"
        if not page_image.exists():
            raise FileNotFoundError(
                f"Missing {page_image}. Run the PDF page rendering step first."
            )

        doc = fitz.open(str(page_image))
        page = doc[0]
        clip = fitz.Rect(x0, max(0, y0 - TOP_MARGIN_PX), x1, y1) & page.rect
        pix = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), clip=clip, alpha=False)
        image_name = f"problem_{number:02d}.png"
        pix.save(str(ASSET_DIR / image_name))

        labels = short_answers.get(number, [])
        if number <= 21 and answer_key.get(number) in {"1", "2", "3", "4", "5"}:
            labels = []
        if number >= 22:
            labels = DEFAULT_SHORT_ANSWER_LABELS.get(number, labels or ["정답"])
        problems.append(
            {
                "number": number,
                "page": page_no,
                "image": f"assets/{image_name}",
                "width": pix.width,
                "height": pix.height,
                "kind": "short" if labels else "choice",
                "labels": labels,
                "correct": answer_key.get(number, ""),
                "score": scores.get(number, 0),
                "explanation": explanations.get(number, {}),
            }
        )

    return problems


def write_html(
    exam_name: str,
    problems: list[dict[str, object]],
    explanation_pdf: str,
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    exam_files = [
        {
            "id": "math_2026_06_g1",
            "name": exam_name,
            "explanationPdf": explanation_pdf,
            "problems": problems,
        }
    ]
    exam_files_json = json.dumps(exam_files, ensure_ascii=False)

    OUT_HTML.write_text(
        f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>수학문제 응시</title>
  <style>
    :root {{
      --bg: #f5f5f5;
      --paper: #ffffff;
      --ink: #111827;
      --muted: #4b5563;
      --line: #cfd5dd;
      --green: #008000;
      --blue: #1d4ed8;
      --soft: #eef4ff;
      --short: #fff7ed;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ height: 100%; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Malgun Gothic", "Segoe UI", system-ui, sans-serif;
      overflow: hidden;
    }}
    button, input {{ font: inherit; }}
    .hidden {{ display: none !important; }}
    .start-screen {{
      height: 100%;
      display: grid;
      place-items: center;
      padding: 24px;
    }}
    .start-box {{
      width: min(720px, 100%);
      background: var(--paper);
      border: 1px solid var(--line);
      padding: 20px;
    }}
    .start-box h1 {{
      margin: 0 0 16px;
      font-size: 20px;
      color: var(--green);
      text-align: center;
    }}
    .file-list {{
      display: grid;
      gap: 8px;
    }}
    .file-item {{
      min-height: 44px;
      border: 1px solid var(--line);
      background: #fff;
      cursor: pointer;
      text-align: left;
      padding: 8px 10px;
    }}
    .file-item:hover {{
      background: var(--soft);
    }}
    .exam-screen {{
      height: 100%;
      display: grid;
      grid-template-rows: 60px minmax(0, 1fr) 62px;
    }}
    .topbar {{
      border: 1px solid var(--line);
      border-bottom: 0;
      background: var(--paper);
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: center;
      padding: 0 14px;
      gap: 12px;
    }}
    .top-center {{
      text-align: center;
      font-weight: 800;
      color: var(--green);
    }}
    .timer {{
      color: #111;
      font-weight: 500;
      margin-left: 12px;
    }}
    .home-btn {{
      min-width: 64px;
      min-height: 32px;
      border: 1px solid var(--green);
      background: #fff;
      cursor: pointer;
    }}
    .main-layout {{
      min-height: 0;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 132px;
      gap: 4px;
      padding: 0 4px;
    }}
    .question-area {{
      min-height: 0;
      background: var(--paper);
      border: 1px solid var(--line);
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
    }}
    .question-head {{
      min-height: 34px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 5px 10px;
    }}
    .question-title {{
      font-weight: 800;
      font-size: 16px;
    }}
    .hint {{
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }}
    .explain-btn {{
      min-width: 72px;
      min-height: 28px;
      border: 1px solid var(--blue);
      background: #fff;
      color: var(--blue);
      cursor: pointer;
      font-size: 13px;
      font-weight: 700;
    }}
    .problem-view {{
      min-height: 0;
      overflow: auto;
      padding: 1cm 14px 14px;
      background: #fff;
    }}
    .problem-image {{
      display: block;
      max-width: 100%;
      height: auto;
      margin: 0 auto;
    }}
    .short-answer-panel {{
      display: none;
      border-top: 1px solid var(--line);
      background: var(--short);
      padding: 10px 12px;
    }}
    .short-answer-panel.visible {{
      display: block;
    }}
    .short-title {{
      font-weight: 800;
      margin-bottom: 8px;
    }}
    .short-inputs {{
      display: grid;
      grid-template-columns: repeat(3, minmax(120px, 1fr));
      gap: 8px;
    }}
    .short-field {{
      display: grid;
      gap: 5px;
      font-weight: 700;
    }}
    .short-field input {{
      min-height: 34px;
      border: 1px solid var(--line);
      padding: 4px 8px;
      background: #fff;
    }}
    .answer-sheet {{
      min-height: 0;
      background: var(--paper);
      border: 1px solid var(--line);
      display: grid;
      grid-template-rows: 30px minmax(0, 1fr) 42px;
      overflow: hidden;
    }}
    .subject {{
      display: grid;
      place-items: center;
      border-bottom: 1px solid var(--line);
      color: var(--green);
      font-weight: 800;
      font-size: 14px;
    }}
    .answer-rows {{
      min-height: 0;
      overflow-y: auto;
    }}
    .answer-row {{
      display: grid;
      grid-template-columns: 25px repeat(5, 20px);
      align-items: center;
      min-height: 25px;
      border-bottom: 1px solid #e5e7eb;
      background: #fff;
    }}
    .answer-row.short-row {{
      grid-template-columns: 25px 1fr;
      background: var(--short);
    }}
    .answer-row.current {{
      background: var(--soft);
      outline: 2px solid rgba(29, 78, 216, .25);
      outline-offset: -2px;
    }}
    .answer-row.answered .num {{
      background: #ecfdf5;
    }}
    .num {{
      height: 100%;
      border: 0;
      border-right: 1px solid #e5e7eb;
      background: transparent;
      color: var(--green);
      font-weight: 800;
      cursor: pointer;
      padding: 0;
      font-size: 14px;
    }}
    .short-open {{
      height: 24px;
      border: 0;
      background: transparent;
      cursor: pointer;
      color: #9a3412;
      font-weight: 800;
      font-size: 12px;
    }}
    .bubble {{
      position: relative;
      display: grid;
      place-items: center;
      height: 24px;
      cursor: pointer;
      user-select: none;
      font-size: 13px;
      line-height: 1;
    }}
    .bubble input {{
      position: absolute;
      opacity: 0;
      pointer-events: none;
    }}
    .bubble span {{
      width: 17px;
      height: 17px;
      display: grid;
      place-items: center;
      border-radius: 50%;
    }}
    .bubble input:checked + span {{
      background: var(--ink);
      color: #fff;
      font-weight: 800;
    }}
    .submit-wrap {{
      display: grid;
      place-items: center;
      border-top: 1px solid var(--line);
      background: #fff;
    }}
    .submit-btn {{
      min-width: 78px;
      min-height: 30px;
      border: 1px solid var(--line);
      background: #fff;
      cursor: pointer;
    }}
    .bottom-nav {{
      border: 1px solid var(--line);
      border-top: 0;
      background: var(--paper);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 22px;
    }}
    .nav-btn {{
      min-width: 45px;
      min-height: 31px;
      border: 1px solid var(--line);
      background: #fff;
      cursor: pointer;
    }}
    .score-modal-backdrop {{
      position: fixed;
      inset: 0;
      z-index: 50;
      display: grid;
      place-items: center;
      padding: 20px;
      background: rgba(17, 24, 39, .38);
    }}
    .score-modal {{
      width: min(360px, 100%);
      background: #fff;
      border: 1px solid var(--line);
      padding: 18px;
      box-shadow: 0 18px 40px rgba(17, 24, 39, .2);
    }}
    .score-modal h2 {{
      margin: 0 0 14px;
      color: var(--green);
      font-size: 19px;
      text-align: center;
    }}
    .score-main {{
      display: grid;
      gap: 8px;
      margin-bottom: 16px;
      text-align: center;
    }}
    .score-value {{
      font-size: 32px;
      font-weight: 800;
      color: var(--ink);
    }}
    .score-detail {{
      color: var(--muted);
      font-size: 14px;
    }}
    .score-close {{
      width: 100%;
      min-height: 34px;
      border: 1px solid var(--green);
      background: #fff;
      cursor: pointer;
    }}
    .explanation-modal-backdrop {{
      position: fixed;
      inset: 0;
      z-index: 60;
      display: grid;
      place-items: center;
      padding: 18px;
      background: rgba(17, 24, 39, .45);
    }}
    .explanation-modal {{
      width: min(980px, 100%);
      height: min(760px, 92vh);
      background: #fff;
      border: 1px solid var(--line);
      display: grid;
      grid-template-rows: 42px minmax(0, 1fr);
    }}
    .explanation-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 6px 10px;
      border-bottom: 1px solid var(--line);
      font-weight: 800;
      color: var(--green);
    }}
    .explanation-close {{
      min-width: 54px;
      min-height: 28px;
      border: 1px solid var(--line);
      background: #fff;
      cursor: pointer;
    }}
    .explanation-body {{
      min-height: 0;
      overflow: auto;
      padding: 12px;
      background: #fff;
    }}
    .explanation-image {{
      display: block;
      max-width: 100%;
      height: auto;
      margin: 0 auto;
    }}
    .explanation-empty {{
      min-height: 160px;
      display: grid;
      place-items: center;
      color: var(--muted);
    }}
    .explanation-frame {{
      width: 100%;
      height: 100%;
      border: 0;
      background: #fff;
    }}
    @media (max-width: 760px) {{
      body {{ overflow: auto; }}
      .exam-screen {{
        min-height: 100%;
        height: auto;
        grid-template-rows: auto auto auto;
      }}
      .topbar {{
        grid-template-columns: 1fr;
        padding: 10px;
      }}
      .main-layout {{
        grid-template-columns: 1fr;
      }}
      .answer-sheet {{
        min-height: 340px;
      }}
      .short-inputs {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <section id="startScreen" class="start-screen">
    <div class="start-box">
      <h1>문제지 파일 목록</h1>
      <div id="fileList" class="file-list"></div>
    </div>
  </section>

  <section id="examScreen" class="exam-screen hidden">
    <header class="topbar">
      <div class="top-center">
        <span id="examFileName"></span>
        <span class="timer">Timer <span id="timerText">50분 00초</span></span>
      </div>
      <button id="homeBtn" class="home-btn" type="button">첫화면</button>
    </header>

    <main class="main-layout">
      <section class="question-area">
        <div class="question-head">
          <div class="question-title" id="questionTitle">1번 문제</div>
          <button id="explanationBtn" class="explain-btn hidden" type="button">해설보기</button>
          <div class="hint"><span id="answeredCount">0</span> / {TOTAL_PROBLEMS}</div>
        </div>
        <div class="problem-view">
          <img id="problemImage" class="problem-image" alt="수학 문제" />
        </div>
        <div id="shortAnswerPanel" class="short-answer-panel"></div>
      </section>

      <aside class="answer-sheet">
        <div class="subject">1과목</div>
        <div class="answer-rows" id="answerRows"></div>
        <div class="submit-wrap">
          <button id="submitBtn" class="submit-btn" type="button">답안제출</button>
        </div>
      </aside>
    </main>

    <footer class="bottom-nav">
      <button id="prevBtn" class="nav-btn" type="button">이전</button>
      <button id="nextBtn" class="nav-btn" type="button">다음</button>
    </footer>
  </section>

  <div id="scoreModal" class="score-modal-backdrop hidden" role="dialog" aria-modal="true" aria-labelledby="scoreTitle">
    <div class="score-modal">
      <h2 id="scoreTitle">채점 결과</h2>
      <div class="score-main">
        <div id="scoreValue" class="score-value">0점</div>
        <div id="scoreDetail" class="score-detail"></div>
      </div>
      <button id="scoreCloseBtn" class="score-close" type="button">확인</button>
    </div>
  </div>

  <div id="explanationModal" class="explanation-modal-backdrop hidden" role="dialog" aria-modal="true" aria-labelledby="explanationTitle">
    <div class="explanation-modal">
      <div class="explanation-head">
        <span id="explanationTitle">해설</span>
        <button id="explanationCloseBtn" class="explanation-close" type="button">닫기</button>
      </div>
      <div id="explanationBody" class="explanation-body"></div>
    </div>
  </div>

  <script>
    const examFiles = {exam_files_json};
    const total = {TOTAL_PROBLEMS};
    const examSeconds = {EXAM_MINUTES} * 60;
    const labels = ["\\u2460", "\\u2461", "\\u2462", "\\u2463", "\\u2464"];
    let activeExam = examFiles[0];
    let current = 1;
    let answers = {{}};
    let remainingSeconds = examSeconds;
    let timerId = null;
    let reviewMode = false;
    let reviewNumbers = [];
    let lastGrading = null;
    let gradingConfirmCount = 0;
    let explanationEnabled = false;

    function storageKey() {{
      return `math-answer-sheet-${{activeExam.id}}`;
    }}

    function loadAnswers() {{
      try {{
        return JSON.parse(localStorage.getItem(storageKey()) || "{{}}");
      }} catch {{
        return {{}};
      }}
    }}

    function saveAnswers() {{
      localStorage.setItem(storageKey(), JSON.stringify(answers));
      renderRows();
      updateCount();
    }}

    function answerIsFilled(value) {{
      if (!value) return false;
      if (typeof value === "string") return value.trim().length > 0;
      return Object.values(value).some(text => String(text || "").trim().length > 0);
    }}

    function updateCount() {{
      const visible = getVisibleNumbers();
      const count = visible.filter(number => answerIsFilled(answers[number])).length;
      document.getElementById("answeredCount").textContent = count;
      const denominator = reviewMode ? reviewNumbers.length : total;
      document.querySelector(".hint").lastChild.textContent = ` / ${{denominator}}`;
    }}

    function getProblem(number) {{
      return activeExam.problems.find(problem => problem.number === number);
    }}

    function getVisibleNumbers() {{
      if (reviewMode && reviewNumbers.length > 0) return reviewNumbers;
      return Array.from({{ length: total }}, (_, index) => index + 1);
    }}

    function sanitizeAnswers() {{
      activeExam.problems.forEach(problem => {{
        const value = answers[problem.number];
        if (value === undefined) return;
        if (problem.kind === "choice" && typeof value !== "string") {{
          delete answers[problem.number];
        }}
        if (problem.kind === "short" && (typeof value !== "object" || Array.isArray(value))) {{
          delete answers[problem.number];
        }}
      }});
    }}

    function formatTime(seconds) {{
      const safe = Math.max(0, seconds);
      const minutes = Math.floor(safe / 60);
      const rest = safe % 60;
      return `${{minutes}}분 ${{String(rest).padStart(2, "0")}}초`;
    }}

    function startTimer(reset = false) {{
      if (reset) remainingSeconds = examSeconds;
      document.getElementById("timerText").textContent = formatTime(remainingSeconds);
      if (timerId) clearInterval(timerId);
      timerId = setInterval(() => {{
        remainingSeconds -= 1;
        document.getElementById("timerText").textContent = formatTime(remainingSeconds);
        if (remainingSeconds <= 0) {{
          clearInterval(timerId);
          timerId = null;
          alert("시험 시간이 종료되었습니다.");
        }}
      }}, 1000);
    }}

    function showStartScreen() {{
      if (timerId) {{
        clearInterval(timerId);
        timerId = null;
      }}
      reviewMode = false;
      reviewNumbers = [];
      lastGrading = null;
      gradingConfirmCount = 0;
      explanationEnabled = false;
      document.getElementById("examScreen").classList.add("hidden");
      document.getElementById("startScreen").classList.remove("hidden");
      renderFileList();
    }}

    function startExam(examId) {{
      activeExam = examFiles.find(file => file.id === examId) || examFiles[0];
      answers = loadAnswers();
      reviewMode = false;
      reviewNumbers = [];
      lastGrading = null;
      gradingConfirmCount = 0;
      explanationEnabled = false;
      sanitizeAnswers();
      saveAnswers();
      current = 1;
      document.getElementById("examFileName").textContent = activeExam.name;
      document.getElementById("startScreen").classList.add("hidden");
      document.getElementById("examScreen").classList.remove("hidden");
      startTimer(true);
      updateCount();
      selectProblem(1);
    }}

    function renderFileList() {{
      const box = document.getElementById("fileList");
      box.innerHTML = "";
      examFiles.forEach(file => {{
        const button = document.createElement("button");
        button.type = "button";
        button.className = "file-item";
        button.textContent = file.name;
        button.addEventListener("click", () => startExam(file.id));
        box.appendChild(button);
      }});
    }}

    function labelText(label) {{
      if (label === "정답") return "정답";
      return `(${{label}})`;
    }}

    function placeholderText(label) {{
      if (label === "정답") return "정답";
      return `${{labelText(label)}} 정답`;
    }}

    function renderShortAnswerPanel(problem) {{
      const panel = document.getElementById("shortAnswerPanel");
      panel.innerHTML = "";
      panel.classList.toggle("visible", problem.kind === "short");
      if (problem.kind !== "short") return;

      const title = document.createElement("div");
      title.className = "short-title";
      title.textContent = "단답형 정답 표시";
      panel.appendChild(title);

      const inputs = document.createElement("div");
      inputs.className = "short-inputs";
      const saved = answers[problem.number] || {{}};
      problem.labels.forEach(label => {{
        const field = document.createElement("label");
        field.className = "short-field";
        field.innerHTML = `<span>${{labelText(label)}}</span>`;
        const input = document.createElement("input");
        input.type = "text";
        input.value = saved[label] || "";
        input.placeholder = placeholderText(label);
        input.addEventListener("input", event => {{
          const currentAnswer = answers[problem.number] || {{}};
          currentAnswer[label] = event.target.value;
          answers[problem.number] = currentAnswer;
          saveAnswers();
        }});
        field.appendChild(input);
        inputs.appendChild(field);
      }});
      panel.appendChild(inputs);
    }}

    function updateExplanationButton() {{
      const problem = getProblem(current);
      const button = document.getElementById("explanationBtn");
      const canShow =
        reviewMode &&
        explanationEnabled &&
        problem &&
        problem.explanation &&
        problem.explanation.image &&
        lastGrading &&
        lastGrading.wrongNumbers.includes(current);
      button.classList.toggle("hidden", !canShow);
    }}

    function openExplanation() {{
      const problem = getProblem(current);
      const explanation = problem && problem.explanation;
      if (!explanation || !explanation.image) return;
      const body = document.getElementById("explanationBody");
      body.innerHTML = "";
      document.getElementById("explanationTitle").textContent = `${{current}}번 해설`;

      const image = document.createElement("img");
      image.className = "explanation-image";
      image.src = explanation.image;
      image.width = explanation.width || 0;
      image.height = explanation.height || 0;
      image.alt = `${{current}}번 해설`;
      body.appendChild(image);
      document.getElementById("explanationModal").classList.remove("hidden");
    }}

    function closeExplanation() {{
      document.getElementById("explanationBody").innerHTML = "";
      document.getElementById("explanationModal").classList.add("hidden");
    }}

    function selectProblem(number) {{
      const visible = getVisibleNumbers();
      if (reviewMode && visible.length > 0 && !visible.includes(number)) {{
        number = visible[0];
      }}
      current = Math.min(total, Math.max(1, number));
      const problem = getProblem(current);
      document.getElementById("questionTitle").textContent = `${{current}}번 문제`;
      const image = document.getElementById("problemImage");
      image.src = problem.image;
      image.width = problem.width;
      image.height = problem.height;
      image.alt = `${{current}}번 문제`;
      renderShortAnswerPanel(problem);
      document.querySelector(".problem-view").scrollTop = 0;
      updateExplanationButton();
      renderRows();
    }}

    function chooseAnswer(number, value) {{
      answers[number] = value;
      current = number;
      selectProblem(number);
      saveAnswers();
    }}

    function renderRows() {{
      const box = document.getElementById("answerRows");
      box.innerHTML = "";
      getVisibleNumbers().forEach(number => {{
        const problem = getProblem(number);
        const row = document.createElement("div");
        row.className = "answer-row";
        row.classList.toggle("short-row", problem.kind === "short");
        row.classList.toggle("current", number === current);
        row.classList.toggle("answered", answerIsFilled(answers[number]));

        const num = document.createElement("button");
        num.type = "button";
        num.className = "num";
        num.textContent = number;
        num.addEventListener("click", () => selectProblem(number));
        row.appendChild(num);

        if (problem.kind === "short") {{
          const open = document.createElement("button");
          open.type = "button";
          open.className = "short-open";
          open.textContent = "단답";
          open.addEventListener("click", () => selectProblem(number));
          row.appendChild(open);
        }} else {{
          labels.forEach((label, index) => {{
            const value = String(index + 1);
            const bubble = document.createElement("label");
            bubble.className = "bubble";
            bubble.title = `${{number}}번 ${{value}}번`;
            bubble.innerHTML = `
              <input type="radio" name="answer-${{number}}" value="${{value}}" ${{answers[number] === value ? "checked" : ""}} />
              <span>${{label}}</span>
            `;
            bubble.querySelector("input").addEventListener("change", () => chooseAnswer(number, value));
            row.appendChild(bubble);
          }});
        }}

        box.appendChild(row);
      }});
    }}

    function normalizeForGrading(value) {{
      return String(value ?? "")
        .trim()
        .replace(/[０-９]/g, char => String(char.charCodeAt(0) - 0xff10))
        .replace(/\s+/g, "");
    }}

    function getStudentAnswer(problem) {{
      const value = answers[problem.number];
      if (!value) return "";
      if (problem.kind === "choice") return normalizeForGrading(value);
      if (problem.labels.length === 1) {{
        return normalizeForGrading(value[problem.labels[0]] || "");
      }}
      return normalizeForGrading(problem.labels.map(label => value[label] || "").join(""));
    }}

    function gradeAnswers() {{
      let earned = 0;
      let maxScore = 0;
      let correctCount = 0;
      const wrongNumbers = [];
      activeExam.problems.forEach(problem => {{
        const score = Number(problem.score || 0);
        const correct = normalizeForGrading(problem.correct);
        const student = getStudentAnswer(problem);
        maxScore += score;
        if (correct && student === correct) {{
          earned += score;
          correctCount += 1;
        }} else {{
          wrongNumbers.push(problem.number);
        }}
      }});
      return {{ earned, maxScore, correctCount, wrongNumbers }};
    }}

    function showScoreModal(result, answeredCount) {{
      document.getElementById("scoreValue").textContent = `${{result.earned}}점`;
      document.getElementById("scoreDetail").textContent =
        `총점 ${{result.maxScore}}점 / 정답 ${{result.correctCount}}문항 / 응답 ${{answeredCount}}문항`;
      document.getElementById("scoreModal").classList.remove("hidden");
    }}

    function submitAnswers() {{
      const count = Object.values(answers).filter(answerIsFilled).length;
      lastGrading = gradeAnswers();
      showScoreModal(lastGrading, count);
    }}

    function enterWrongReview() {{
      if (!lastGrading || lastGrading.wrongNumbers.length === 0) return;
      reviewMode = true;
      reviewNumbers = [...lastGrading.wrongNumbers];
      selectProblem(reviewNumbers[0]);
      updateCount();
      updateExplanationButton();
    }}

    function moveProblem(direction) {{
      if (!reviewMode || reviewNumbers.length === 0) {{
        selectProblem(current + direction);
        return;
      }}
      const index = reviewNumbers.indexOf(current);
      const nextIndex = Math.min(reviewNumbers.length - 1, Math.max(0, index + direction));
      selectProblem(reviewNumbers[nextIndex]);
    }}

    document.getElementById("homeBtn").addEventListener("click", showStartScreen);
    document.getElementById("prevBtn").addEventListener("click", () => moveProblem(-1));
    document.getElementById("nextBtn").addEventListener("click", () => moveProblem(1));
    document.getElementById("submitBtn").addEventListener("click", submitAnswers);
    document.getElementById("scoreCloseBtn").addEventListener("click", () => {{
      document.getElementById("scoreModal").classList.add("hidden");
      gradingConfirmCount += 1;
      if (gradingConfirmCount >= 2) {{
        explanationEnabled = true;
      }}
      enterWrongReview();
      updateExplanationButton();
    }});
    document.getElementById("scoreModal").addEventListener("click", event => {{
      if (event.target.id === "scoreModal") {{
        event.currentTarget.classList.add("hidden");
      }}
    }});
    document.getElementById("explanationBtn").addEventListener("click", openExplanation);
    document.getElementById("explanationCloseBtn").addEventListener("click", closeExplanation);
    document.getElementById("explanationModal").addEventListener("click", event => {{
      if (event.target.id === "explanationModal") {{
        closeExplanation();
      }}
    }});

    renderFileList();
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    pdf_path = find_question_pdf()
    answer_pdf_path = find_answer_pdf()
    explanation_pdf = publish_answer_pdf(answer_pdf_path)
    answer_key = extract_answer_key(answer_pdf_path)
    scores = extract_problem_scores(pdf_path)
    explanations = render_explanation_images(answer_pdf_path)
    short_answers = detect_short_answer_numbers(pdf_path)
    problems = render_problem_images(short_answers, answer_key, scores, explanations)
    exam_name = pdf_path.name if pdf_path is not None else DEFAULT_EXAM_NAME
    write_html(exam_name, problems, explanation_pdf)
    print(OUT_HTML)


if __name__ == "__main__":
    main()
