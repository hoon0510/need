import streamlit as st
import openai

# API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 페이지 설정
st.set_page_config(page_title="리뷰 기반 욕구 분석기", layout="wide")
st.title("🔍 리뷰 기반 욕구 분석기")

# 개념 설명
with st.expander("📘 욕구 기반 퍼널 파괴 마케팅 전략 개요"):
    st.markdown("""
    ### 개념 설명: 욕구 기반 퍼널 파괴 마케팅 전략
    욕구 기반 퍼널 파괴 마케팅은 전통적인 AIDA(인지→관심→욕망→행동) 퍼널을 넘어, 고객의 감정과 무의식적 욕구를 즉각 자극해 의사결정 단계를 단축시키는 전략입니다. 핵심은:
    1. **감정 트리거 발굴**
    2. **욕구 전환**
    3. **즉각적 행동 유도**
    4. **파괴적 자극 메시지 활용**

    이 분석기는 인간의 욕구를 매슬로 이론보다 더 세분화하여 감정, 기저욕구, 반사욕구, 저항요인까지 구조적으로 분석합니다.
    """)

# 리뷰 개수
st.markdown("### 리뷰 개수 선택")
review_count = st.number_input("입력할 리뷰 개수", min_value=1, max_value=200, value=6, step=1)
st.markdown("---")

# 분석 목적
st.markdown("### 분석 목적 입력")
analysis_goal = st.text_input("이 분석 결과를 어디에 활용하시겠습니까?", value="브랜드 이미지 개선, 신규 브랜드 런칭, 퍼포먼스 마케팅 전략 등 자유롭게 목적을 입력해주세요")
st.markdown("---")

# 리뷰 입력
st.markdown("### 리뷰 입력")
review_inputs = []
rows = (review_count + 1) // 2
for i in range(rows):
    cols = st.columns(2)
    for j in range(2):
        index = i * 2 + j
        if index < review_count:
            review = cols[j].text_area(f"리뷰 {index+1}", key=f"review_{index}")
            if review.strip():
                review_inputs.append(review.strip())

# 최초진입시장 분석 입력
st.markdown("### 🧭 최초진입시장 욕구 분석")
st.markdown("신제품 또는 시장이 형성되지 않은 아이템의 감정 및 욕구 예측 분석")
product_name = st.text_input("아이템명 (예: AI 감정 기록기)")
product_features = st.text_area("핵심 기능/특징 (예: 감정을 분석해 하루를 기록)")
product_target = st.text_input("타깃 고객층 (예: 20대 감성 중심 소비자)")
product_context = st.text_area("사용 상황/맥락 (예: 하루를 마무리하며 감정 상태를 기록하는 루틴)")
product_mission = st.text_area("기획 의도 및 해결하려는 문제 (예: 감정 표현이 어려운 사람들의 정서 순환)")
st.markdown("---")

# 분석 버튼
analyze_now = st.button("🚀 분석 시작", key="analyze_button")
st.markdown("---")

# 프롬프트 (15개 항목 유지)
def build_deep_prompt(reviews, goal):
    return f"""
당신은 고객의 감정과 무의식적 욕구, 그리고 감정 유도형 행동 메커니즘을 정확히 해석해 전환 전략을 수립하는 최고의 마케팅 전략가이자 직관적이며 직설적인 언어를 다루는 카피라이터입니다. 밈, 파괴적 언어, 자극적인 카피까지 전략적으로 사용하는 크리에이티브 디렉터입니다.

분석 목적: {goal}

고객 리뷰:
{reviews}

---

다음 항목을 빠짐없이, 간결하고 명확하게 작성하세요. 각 항목은 실무자가 이해할 수 있도록 **구조화된 언어**로 정리하세요:

1. 감정 기반 주요 단어 분석  
2. 감정 트리거 요인  
3. 감정 → 욕구 흐름 분석  
4. 심리 전환 공식  
5. 정당화 내러티브 구조  
6. 반사 욕구 분석  
7. 욕구 간 충돌 시나리오  
8. 욕구 저항 요인  
9. 실행 방해 요인 + 제거 전략  
10. 핵심 욕구 기반 카피 제안 (자극적 언어 포함)  
11. 킬러 키워드 추천 (한 단어 위주)  
12. 마케팅 실행 전략 상세  
13. 콘텐츠 포맷 / 톤 / 콘셉트 / 채널 제안  
14. 성과 예측 및 KPI  
15. [보조] 세분화된 욕구 사전 기반 분석 (매슬로우보다 정교한 구조 적용)
"""

def build_plan_prompt(reviews, goal):
    return f"""
당신은 욕구 기반 분석을 통해 실제 마케팅 전략을 기획하는 전문가입니다. 다음 리뷰를 바탕으로 전략 문서 항목별로 마크다운 형식으로 작성하세요. 설명 없이 항목 제목과 내용만 출력하세요.

분석 목적: {goal}
리뷰 데이터:
{reviews}

---

1. 시장 및 소비자 인사이트
2. 타깃 페르소나 정의
3. 핵심 니즈 및 욕구
4. 제품/서비스 포지셔닝
5. 브랜드 메시지 구조
6. 전환 유도 흐름
7. 카피 제안 (유입/전환/충성)
8. 콘텐츠 전략
9. 미디어 믹스/예산 배분
10. KPI 및 성과 계획
"""

def build_killer_summary(reviews, goal):
    return f"""
다음 리뷰를 분석하고, 고객의 감정과 욕망을 동시에 자극할 수 있는 한 줄 카피를 작성하세요. 이 문장은 짧고 파괴적이어야 하며, 행동을 유도해야 합니다.

분석 목적: {goal}
리뷰 데이터:
{reviews}

형식: [한 문장 요약]
"""

def analyze_reviews(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 감정과 욕망을 분석하는 최고의 마케팅 전략가입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# 분석 실행
if analyze_now:
    if not review_inputs and not product_name:
        st.warning("리뷰나 신시장 입력 중 하나는 반드시 필요합니다.")
    else:
        info_placeholder = st.empty()
        info_placeholder.warning("🔄 잠시만 기다려주세요. 분석이 진행 중입니다.")
        with st.spinner("분석 중..."):
            combined_reviews = "\n\n".join([
                r if len(r.split('.')) <= 5 else '.'.join(r.split('.')[:5]) + "..." for r in review_inputs
            ])
            if not combined_reviews.strip():
                combined_reviews = f"""
[아이템명]: {product_name}
[기능]: {product_features}
[타깃]: {product_target}
[상황]: {product_context}
[의도]: {product_mission}
"""
            result_summary = analyze_reviews(build_killer_summary(combined_reviews, analysis_goal))
            result_3 = analyze_reviews(build_deep_prompt(combined_reviews, analysis_goal))
            result_4 = analyze_reviews(build_plan_prompt(combined_reviews, analysis_goal))

        info_placeholder.empty()

        st.markdown("<div id='scroll_target'></div>", unsafe_allow_html=True)
        st.markdown("## ✅ 분석 결과")
        st.markdown("### 🔥 한 문장 요약")
        st.markdown(f"**{result_summary}**")

        tab1, tab2 = st.tabs(["⚙️ 다층 욕구 기반 분석", "🧠 전문가용 마케팅 기획안"])

        with tab1:
            st.subheader("⚙️ 다층 욕구 기반 분석")
            st.markdown(result_3)

        with tab2:
            st.subheader("🧠 전문가용 마케팅 기획안")
            st.markdown(result_4)

        st.success("✅ 분석이 완료되었습니다.")

        st.markdown("""
            <script>
                const element = document.getElementById("scroll_target");
                if (element) {
                    element.scrollIntoView({ behavior: "smooth" });
                }
            </script>
        """, unsafe_allow_html=True)

