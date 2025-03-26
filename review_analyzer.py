import streamlit as st
import openai
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit 기본 설정
st.set_page_config(page_title="리뷰 분석기", layout="wide")
st.title("🔍 리뷰 기반 욕구 분석기")

# 비밀번호 설정
ACCESS_PASSWORD = "need987!@"  # 원하는 비밀번호 입력

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

# 사용 횟수 제한 설정
MAX_USAGE = 10

if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

if st.session_state.usage_count >= MAX_USAGE:
    st.error("사용 횟수 초과")
    st.stop()

# 프롬프트 설정
def build_prompt(reviews):
    prompt = f"""
[고객 리뷰 원문]
{reviews}

---

💡 아래 기준에 따라 마케팅 전략 관점에서 분석 결과만 작성해 주세요. 질문이나 해설 없이 **전략 보고서 형식**으로 명확하게 정리합니다.

1. **가설 설정**  
   - 이 리뷰들을 통해 추정할 수 있는 고객의 핵심 상태 또는 상황을 한 문장으로 정리해 주세요.  
     (예: 고객은 외로움을 달래기 위해 맛집을 찾는다)

2. **감정 진입점**  
   - 리뷰에 나타난 고객의 감정 상태를 요약해 주세요. (예: 외로움, 스트레스, 휴식 필요 등)

3. **욕구 도출**  
   - 감정에 따른 욕구를 매슬로우 이론 기반으로 정리해 주세요. (각 리뷰별로 추론 가능하면 함께 작성)

4. **공통된 핵심 욕구 요약**  
   - 전체 리뷰에 반복 등장하는 주된 욕구를 요약해 주세요.

5. **전략적 활용 포인트**  
   - 어떤 문구나 이미지, 환경을 활용하면 위 욕구를 자극할 수 있는지 구체적으로 제시해 주세요.

6. **마케팅 카피 3종 제안**  
   - 고객의 감정과 욕구에 직접 연결되는 카피를 3가지 제안해 주세요.  
   - 각 카피는 [공감 - 유혹 - 충족] 구조로 구성해 주세요.

[출력 형식은 마케팅 전략 문서처럼 명확하게 정리해 주세요.]
"""
    return prompt

def analyze_reviews(reviews):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 뛰어난 욕구 기반 마케팅 전략가입니다."},
            {"role": "user", "content": build_prompt(reviews)}
        ]
    )
    return response.choices[0].message.content.strip()

# 👉 리뷰 개수 입력 & 상단 버튼
col1, col2 = st.columns([1, 5])
with col1:
    review_count = st.number_input("리뷰 개수", min_value=1, max_value=200, value=6, step=1)
with col2:
    if st.button("🚀 분석 시작", key="top_button"):
        st.session_state.start_analysis = True

st.markdown("---")

# ✅ 리뷰 입력칸 생성 (2칸씩)
review_inputs = []
for i in range(review_count):
    cols = st.columns(2)
    for j in range(2):
        index = i * 2 + j
        if index < review_count:
            review = cols[j].text_area(f"리뷰 {index+1}", key=f"review_{index}")
            if review.strip():
                review_inputs.append(review.strip())

if st.button("🚀 분석 시작"):
    if not review_inputs:
        st.warning("리뷰를 최소 1개 이상 입력해주세요.")
    else:
        with st.spinner("분석 중..."):
            combined_reviews = "\n\n".join(review_inputs)
            result = analyze_reviews(combined_reviews)
            st.markdown("### 🔑 분석 결과")
            st.write(result)
            st.session_state.usage_count += 1
            st.info(f"남은 사용 가능 횟수: {MAX_USAGE - st.session_state.usage_count}")
