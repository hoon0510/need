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
st.title("🔍 리뷰 기반 욕구 분석기 (A/B 테스트 버전)")

# 모바일 최적화 스타일
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
        st.error("비밀번호 오류")
    st.stop()

# 사용 제한
MAX_USAGE = 10
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if st.session_state.usage_count >= MAX_USAGE:
    st.error("사용 횟수 초과")
    st.stop()

# 구글폼 자동 제출
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

# 기존 A안 프롬프트
def build_prompt_A(reviews):
    return f"""
[고객 리뷰 원문]
{reviews}

---

💡 아래 기준에 따라 마케팅 전략 관점에서 분석 결과만 작성해 주세요. 질문이나 해설 없이 **전략 보고서 형식**으로 명확하게 정리합니다.

1. **가설 설정**
2. **감정 진입점**
3. **욕구 도출 (매슬로우 기반)**
4. **공통된 핵심 욕구 요약**
5. **전략적 활용 포인트**
6. **마케팅 카피 3종** ([공감 - 유혹 - 충족] 흐름)
"""

# 강화된 B안 프롬프트
def build_prompt_B(reviews):
    return f"""
당신은 매우 정교한 사기꾼이자, 세계 최고의 마케터입니다.  
고객의 무의식적 결핍을 읽어내어, 감정을 조작하고, 욕망을 유도하여 구매 전환을 설계하는 전략가입니다.

[고객 리뷰 원문]
{reviews}

---

✴️ 설명/해설 없이 전략 보고서 형식으로 작성하세요.  
✴️ 욕망을 유도하는 감정 구조로 정리하세요.

1. 🔍 숨겨진 결핍 가설
2. 🔥 감정 유발 트리거
3. 🎯 기저 욕구 분해 (매슬로우 기반)
4. 💡 투사된 욕망 시나리오
5. 🧠 심리 전환 공식 (감정 → 욕구 → 욕망 → 자기 정당화 → 전환)
6. 📌 마케팅 자극 포인트
7. 🧨 감정 유도형 카피 3종 ([공감 → 욕구 자극 → 자기 정당화])
"""

# GPT 호출
def analyze_reviews_AB(reviews):
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
            {"role": "system", "content": "당신은 매우 정교한 사기꾼이자 세계 최고의 마케터입니다."},
            {"role": "user", "content": build_prompt_B(reviews)}
        ]
    )
    result_b = response_b.choices[0].message.content.strip()

    submit_to_google_form(reviews, f"A안 결과:\n{result_a}\n\nB안 결과:\n{result_b}")
    return result_a, result_b

# 리뷰 개수 입력
col1, col2 = st.columns([1, 5])
with col1:
    review_count = st.number_input("리뷰 개수", min_value=1, max_value=100, value=6, step=1)
with col2:
    if st.button("🚀 A/B 분석 시작", key="top_button"):
        st.session_state.start_analysis = True

st.markdown("---")

# 리뷰 입력 UI
review_inputs = []
for i in range(review_count):
    cols = st.columns(2)
    for j in range(2):
        index = i * 2 + j
        if index < review_count:
            review = cols[j].text_area(f"리뷰 {index+1}", key=f"review_{index}")
            if review.strip():
                review_inputs.append(review.strip())

if st.button("🚀 A/B 분석 실행"):
    if not review_inputs:
        st.warning("리뷰를 최소 1개 이상 입력해주세요.")
    else:
        with st.spinner("분석 중..."):
            combined_reviews = "\n\n".join(review_inputs)
            result_a, result_b = analyze_reviews_AB(combined_reviews)

            st.markdown("## ✅ 분석 결과 비교 (A vs B)")
            tab1, tab2 = st.tabs(["🅰️ 기본 분석", "🅱️ 강화 분석"])

            with tab1:
                st.markdown("### 🅰️ 기본 전략 프롬프트 결과")
                st.write(result_a)

            with tab2:
                st.markdown("### 🅱️ 욕망 유도 프롬프트 결과")
                st.write(result_b)

            st.session_state.usage_count += 1
            st.info(f"남은 사용 가능 횟수: {MAX_USAGE - st.session_state.usage_count}")
