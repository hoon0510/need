import requests
import streamlit as st
import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 기본 UI 설정
st.set_page_config(page_title="리뷰 분석기", layout="wide")
st.title("🔍 리뷰 기반 욕구 분석기 (A/B + 목적 분기 방식)")

# 스타일
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
textarea { font-size: 16px !important; min-height: 150px !important; }
input[type="number"] { font-size: 16px !important; padding: 10px !important; }
div.stButton > button { font-size: 16px !important; padding: 15px !important; width: 100%; }
h1 { font-size: 24px !important; }
.block-container { padding-left: 10px !important; padding-right: 10px !important; }
</style>
""", unsafe_allow_html=True)

# 비밀번호
ACCESS_PASSWORD = "need987!@"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    pw = st.text_input("비밀번호 입력", type="password")
    if pw == ACCESS_PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pw:
        st.error("잘못된 비밀번호입니다.")
    st.stop()

# 사용 횟수 제한
MAX_USAGE = 10
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if st.session_state.usage_count >= MAX_USAGE:
    st.error("사용 횟수 초과")
    st.stop()

# 구글폼 URL
google_form_url = "https://docs.google.com/forms/d/1-QR2XTeoXMpEVlLAJglt-xw_4Xxnuu54WegEiAc92R8/formResponse"
def submit_to_google_form(review_text, analysis_result):
    form_data = {
        'entry.1331771366': review_text,
        'entry.760801242': analysis_result
    }
    try:
        requests.post(google_form_url, data=form_data)
    except Exception as e:
        print(f"Google Form 제출 실패: {e}")

# A안 프롬프트
def build_prompt_A(reviews):
    return f"""
[고객 리뷰 원문]
{reviews}

---

1. 가설 설정
2. 감정 진입점
3. 욕구 도출 (매슬로우 기반)
4. 공통된 핵심 욕구 요약
5. 전략적 활용 포인트
6. 카피 3종 ([공감 - 유혹 - 충족])
"""

# B안 프롬프트 (목적 분기 포함)
def build_prompt_B(reviews, purpose):
    prompt_intro = "당신은 세계 최고의 사기꾼이자 심리학에 기반한 욕구 분석 전문 마케터입니다. 고객의 무의식적 감정과 욕구를 분석해, 행동을 유도하는 전략가입니다. 아래의 리뷰를 바탕으로 목적에 따라 분석 전략을 달리 적용하세요."

    if purpose == "신규유입":
        scenario = "이 리뷰는 아직 플랫폼을 사용하지 않은 고객의 시선에서, 흥미와 기대를 자하는 분석이 필요합니다."
    else:
        scenario = "이 리뷰는 기존 고객 또는 이탈 위기 고객의 시선에서, 신뢰 회복과 만족 증대 전략이 필요합니다."

    prompt_body = f"""
[분석 목적: {purpose}]
{scenario}

[고객 리뷰 원문]
{reviews}

1. 숨겨진 결핍 가설
2. 감정 유발 트리거
3. 기저 욕구 분해 (매슬로우 기반)
4. 투사된 욕망 시나리오
5. 심리 전환 공식 (감정 → 욕구 → 욕망 → 자기 정당화 → 전환)
6. 마케팅 자극 포인트
7. 감정 유도형 카피 3종 ([공감 → 욕구 자극 → 자기 정당화])
"""
    return prompt_intro + "\n" + prompt_body

# GPT 분석 호출
def analyze_reviews_AB(reviews, purpose):
    response_a = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 뛰어난 욕구 기반 마케팅 전략가입니다."},
            {"role": "user", "content": build_prompt_A(reviews)}
        ]
    )
    result_a = response_a.choices[0].message.content.strip()

    response_b = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 욕망을 유도하는 전략가입니다."},
            {"role": "user", "content": build_prompt_B(reviews, purpose)}
        ]
    )
    result_b = response_b.choices[0].message.content.strip()

    submit_to_google_form(reviews, f"A안 결과:\n{result_a}\n\nB안 결과:\n{result_b}")
    return result_a, result_b

# UI 입력
col1, col2, col3 = st.columns([1, 2, 3])
with col1:
    review_count = st.number_input("리뷰 수", min_value=1, max_value=100, value=6, step=1)
with col2:
    goal = st.selectbox("분석 목적", ["신규유입", "리텐션"])
with col3:
    if st.button("🚀 분석 시작"):
        st.session_state.start_analysis = True

st.markdown("---")

review_inputs = []
for i in range(review_count):
    cols = st.columns(2)
    for j in range(2):
        index = i * 2 + j
        if index < review_count:
            review = cols[j].text_area(f"리뷰 {index+1}", key=f"review_{index}")
            if review.strip():
                review_inputs.append(review.strip())

if st.button("🚀 분석 실행"):
    if not review_inputs:
        st.warning("리뷰를 1개 이상 입력해주세요.")
    else:
        with st.spinner("분석 중..."):
            combined_reviews = "\n\n".join(review_inputs)
            result_a, result_b = analyze_reviews_AB(combined_reviews, goal)

            st.markdown("## ✅ 분석 결과 비교 (A vs B)")
            tab1, tab2 = st.tabs(["🅰️ 기본 분석", "🅱️ 욕망 유도 분석"])

            with tab1:
                st.markdown("### 🅰️ A안 결과")
                st.write(result_a)
            with tab2:
                st.markdown(f"### 🅱️ B안 결과 ({goal} 모드)")
                st.write(result_b)

            st.session_state.usage_count += 1
            st.info(f"남은 사용 가능 횟수: {MAX_USAGE - st.session_state.usage_count}")
