from __future__ import annotations

import json
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "generated_exam_page"
ASSET_DIR = OUT_DIR / "assets"
OUT_HTML = OUT_DIR / "2026_06_g1_math_practice.html"
TOTAL_PROBLEMS = 20


# These rectangles crop the already-rendered PDF page images into one image per problem.
# Coordinates are in the page_XX_problems.png image coordinate system.
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
}


def render_problem_images() -> list[dict[str, object]]:
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
        clip = fitz.Rect(x0, y0, x1, y1) & page.rect
        pix = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), clip=clip, alpha=False)
        image_name = f"problem_{number:02d}.png"
        pix.save(str(ASSET_DIR / image_name))
        problems.append(
            {
                "number": number,
                "page": page_no,
                "image": f"assets/{image_name}",
                "width": pix.width,
                "height": pix.height,
            }
        )

    return problems


def write_html(problems: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    problems_json = json.dumps(problems, ensure_ascii=False)

    OUT_HTML.write_text(
        f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>&#49688;&#54617;&#47928;&#51228; &#45813;&#50504;&#49440;&#53469;</title>
  <style>
    :root {{
      --bg: #f3f4f6;
      --paper: #ffffff;
      --ink: #111827;
      --muted: #4b5563;
      --line: #cfd5dd;
      --green: #008000;
      --blue: #1d4ed8;
      --soft: #eef4ff;
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
    .layout {{
      height: 100%;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 132px;
      gap: 4px;
      padding: 2px;
    }}
    .question-area {{
      min-height: 0;
      background: var(--paper);
      border: 1px solid var(--line);
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
    }}
    .question-head {{
      min-height: 38px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 6px 10px;
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
    .problem-view {{
      min-height: 0;
      overflow: auto;
      padding: 14px;
      background: #fff;
    }}
    .problem-image {{
      display: block;
      max-width: 100%;
      height: auto;
      margin: 0 auto;
    }}
    .answer-sheet {{
      min-height: 0;
      background: var(--paper);
      border: 1px solid var(--line);
      display: grid;
      grid-template-rows: 30px minmax(0, 1fr) auto;
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
    .sheet-actions {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4px;
      padding: 4px;
      border-top: 1px solid var(--line);
    }}
    .sheet-actions button {{
      min-height: 28px;
      border: 1px solid var(--line);
      background: #fff;
      cursor: pointer;
      font-size: 12px;
    }}
    @media (max-width: 760px) {{
      body {{ overflow: auto; }}
      .layout {{
        min-height: 100%;
        height: auto;
        grid-template-columns: 1fr;
      }}
      .answer-sheet {{
        min-height: 340px;
      }}
    }}
  </style>
</head>
<body>
  <main class="layout">
    <section class="question-area">
      <div class="question-head">
        <div class="question-title" id="questionTitle">1&#48264; &#47928;&#51228;</div>
        <div class="hint"><span id="answeredCount">0</span> / {TOTAL_PROBLEMS}</div>
      </div>
      <div class="problem-view">
        <img id="problemImage" class="problem-image" alt="&#49688;&#54617; &#47928;&#51228;" />
      </div>
    </section>

    <aside class="answer-sheet">
      <div class="subject">1&#44284;&#47785;</div>
      <div class="answer-rows" id="answerRows"></div>
      <div class="sheet-actions">
        <button id="resetBtn" type="button">&#52488;&#44592;&#54868;</button>
        <button id="nextBtn" type="button">&#45796;&#51020;</button>
      </div>
    </aside>
  </main>

  <script>
    const problems = {problems_json};
    const total = {TOTAL_PROBLEMS};
    const storageKey = "math-20-answer-sheet-ui";
    const labels = ["①", "②", "③", "④", "⑤"];
    let current = 1;
    let answers = loadAnswers();

    function loadAnswers() {{
      try {{
        return JSON.parse(localStorage.getItem(storageKey) || "{{}}");
      }} catch {{
        return {{}};
      }}
    }}

    function saveAnswers() {{
      localStorage.setItem(storageKey, JSON.stringify(answers));
      renderRows();
      updateCount();
    }}

    function updateCount() {{
      document.getElementById("answeredCount").textContent = Object.keys(answers).length;
    }}

    function getProblem(number) {{
      return problems.find(problem => problem.number === number);
    }}

    function selectProblem(number) {{
      current = number;
      const problem = getProblem(number);
      document.getElementById("questionTitle").textContent = `${{number}}번 문제`;
      const image = document.getElementById("problemImage");
      image.src = problem.image;
      image.width = problem.width;
      image.height = problem.height;
      image.alt = `${{number}}번 문제`;
      document.querySelector(".problem-view").scrollTop = 0;
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
      for (let number = 1; number <= total; number++) {{
        const row = document.createElement("div");
        row.className = "answer-row";
        row.classList.toggle("current", number === current);
        row.classList.toggle("answered", Boolean(answers[number]));

        const num = document.createElement("button");
        num.type = "button";
        num.className = "num";
        num.textContent = number;
        num.addEventListener("click", () => selectProblem(number));
        row.appendChild(num);

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

        box.appendChild(row);
      }}
    }}

    document.getElementById("resetBtn").addEventListener("click", () => {{
      answers = {{}};
      localStorage.removeItem(storageKey);
      renderRows();
      updateCount();
    }});

    document.getElementById("nextBtn").addEventListener("click", () => {{
      selectProblem(current === total ? 1 : current + 1);
    }});

    updateCount();
    selectProblem(1);
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    problems = render_problem_images()
    write_html(problems)
    print(OUT_HTML)


if __name__ == "__main__":
    main()
