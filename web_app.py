from __future__ import annotations
import json
from typing import Any, Dict
from flask import Flask, request, render_template_string 
import html 
from main import analyze_case

app = Flask(__name__)

# HTML 템플릿
HTML_TEMPLATE = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <title>AI 판사 분석기</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    textarea { width: 100%; height: 200px; }
    .section { margin-top: 20px; }
    details { border: 1px solid #ccc; border-radius: 6px; padding: 10px; background: #fafafa; }
    summary { font-weight: bold; cursor: pointer; }
    pre, .json-body { white-space: pre-wrap; word-break: keep-all; margin: 10px 0 0 0; }
    .kv { margin-left: 20px; }
    .k { font-weight: 600; }
    .v { margin-left: 4px; }
  </style>
</head>
<body>
  <h1>AI 판사 분석기</h1>
  <form method="POST">
    <label for="case">사건 사실 입력:</label><br />
    <textarea id="case" name="case" placeholder="사건의 사실관계를 서술하세요…">{{ case_text|default("") }}</textarea><br />
    <button type="submit">분석 실행</button>
  </form>

  {% if json_dict %}
    {% for key, value in json_dict.items() %}
      <details class="section" {% if loop.first %}open{% endif %}>
        <summary>{{ key.replace('_', ' ').upper() }}</summary>
        <div class="json-body">{{ value|safe }}</div>
      </details>
    {% endfor %}
  {% elif raw_text %}
    <div class="section">
      <h2>원본 출력</h2>
      <pre>{{ raw_text }}</pre>
    </div>
  {% endif %}
</body>
</html>
"""


def _attempt_json_parse(raw: str):
    """Try to parse raw string containing JSON (possibly fenced or with extra text)."""
    try:
        return json.loads(raw)
    except Exception:
        # 가독성 증가
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1 and start < end:
            try:
                return json.loads(raw[start:end + 1])
            except Exception:
                pass
    return None

#변환
def _json_to_html(data):
    """Recursively convert Python data structures to expandable HTML."""
    if isinstance(data, dict):
        parts = []
        for k, v in data.items():
            parts.append(
                f'<div class="kv"><span class="k">{html.escape(str(k))}</span>: {_json_to_html(v)}</div>'
            )
        return "".join(parts)
    if isinstance(data, list):
        items = "".join(f'<li>{_json_to_html(item)}</li>' for item in data)
        return f'<ul>{items}</ul>'
    # Primitive value
    return f'<span class="v">{html.escape(str(data))}</span>'

#실행 코드
@app.route("/", methods=["GET", "POST"])
def index():
    case_text: str | None = None
    json_dict: Dict[str, Any] | None = None
    raw_text: str | None = None

    if request.method == "POST":
        case_text = request.form.get("case", "").strip()
        if case_text:
            result = analyze_case(case_text)

            if isinstance(result, dict) and "raw" in result:
                parsed = _attempt_json_parse(result["raw"])
                if parsed is not None:
                    json_dict = parsed
                else:
                    raw_text = result["raw"]
            elif isinstance(result, dict):
                json_dict = result
            else:
                raw_text = str(result)

            # 상세보기ㅇ
            if json_dict:
                json_dict = {k: _json_to_html(v) for k, v in json_dict.items()}

    return render_template_string(HTML_TEMPLATE, case_text=case_text, json_dict=json_dict, raw_text=raw_text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True) 