import os
import sys
import json
import textwrap
from typing import Dict, Any
import google.generativeai as genai  



genai.configure(api_key="AIzaSyC5m8MMSDU5Dzht5tqfGTvnsxYO1eQsw3Y")
model = genai.GenerativeModel("gemini-1.5-flash")


#프롬프트트
LEGAL_PROMPT = textwrap.dedent(
    """
    당신은 **Lexi**라는 편향 없이 일관된 사법 분석을 제공하도록 설계된 AI 법률 보조 시스템입니다. 모든 출력은 반드시 한국어로 작성하십시오.

    작업 1 – 엄격한 법률 분석:
      1. 관련 사실을 요약하십시오.
      2. 적용 가능한 법령과 판례를 식별하십시오.
      3. 감정, 동정 요소를 배제하고 법과 판례에 근거해 1차적 유ㆍ무죄 및 법리 판단을 제시하십시오.

    작업 2 – 윤리·동정 고려:
      피고인의 개인적·사회적 배경, 반성 정도, 피해자 의사 등을 고려하여 형 감경 또는 선처 사유를 논의하십시오.

    작업 3 – 공정성·편향 감사:
      성별·인종·사회·경제적 지위 등 보호 대상 속성이 판결에 편향을 일으킬 위험이 있는지 평가하고, 위험이 있을 경우 완화 방안을 제시하십시오.

    작업 4 – 최종 권고 판결:
      위의 모든 분석을 종합하여 최종 판결과 형량을 제안하고, 법적 근거·윤리적 근거·공정성 근거를 명확히 설명하십시오.

    다음과 같은 키를 갖는 **JSON** 형식으로 결과를 반환하십시오.
      엄격한 분석, 윤리적 고려 사항, 공정성 감사, 최종 판결
    """
)   

#인공지능 입력 코드
def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    try:
        response = model.generate_content(prompt, safety_settings={})
        return response.text
    except Exception as exc:
        print(f"Gemini API error: {exc}")
        sys.exit(1)


def analyze_case(case_description: str) -> Dict[str, Any]:
    """Run the complete analysis pipeline on a single legal case description."""
    full_prompt = LEGAL_PROMPT + "\n\nCASE DESCRIPTION:\n" + case_description.strip()
    raw_output = ask_gemini(full_prompt)

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {"raw": raw_output}

    return result

#실행 코드
def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <case_file>|--interactive")
        sys.exit(1)

    if sys.argv[1] == "--interactive":
        print("Enter the factual description of the case. End input with an empty line:\n")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        case_text = "\n".join(lines)
    else:
        case_path = sys.argv[1]
        if not os.path.exists(case_path):
            print(f"File not found: {case_path}")
            sys.exit(1)
        with open(case_path, "r", encoding="utf-8") as f:
            case_text = f.read()

    analysis = analyze_case(case_text)

    print("\n===== AI JUDGE ANALYSIS =====\n")
    if "raw" in analysis:
        print(analysis["raw"])
        sys.exit(0)

    # Pretty-print structured output
    for key, value in analysis.items():
        print(f"--- {key.replace('_', ' ').upper()} ---\n{value}\n")


if __name__ == "__main__":
    main()

