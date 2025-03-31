import streamlit as st
import openai

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

# 탭 구분 (기존 시장 vs 최초 시장 진입)
tab_choice = st.radio("분석 목적 선택", ["기존 시장 분석", "최초진입시장 욕구 분석"])

if tab_choice == "기존 시장 분석":
    st.markdown("### 리뷰 기반 분석")
    col1, col2 = st.columns(2)
    with col1:
        review_count = st.number_input("입력할 리뷰 개수", min_value=1, max_value=200, value=6, step=1)
    with col2:
        analysis_goal = st.text_input("이 분석 결과를 어디에 활용하시겠습니까?", value="브랜드 이미지 개선, 신규 브랜드 런칭, 퍼포먼스 마케팅 전략 등")

    st.markdown("---")
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

    analyze_now = st.button("🚀 분석 시작", key="analyze_button")

elif tab_choice == "최초진입시장 욕구 분석":
    st.markdown("### 신시장 진입 아이템 분석")
    with st.form("new_market_form"):
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("아이템명", value="")
            item_function = st.text_area("아이템의 기능/효과")
            target_audience = st.text_area("주요 타깃 (연령, 성별, 라이프스타일 등)")
        with col2:
            use_context = st.text_area("사용 상황 또는 사용 시나리오")
            positioning_goal = st.text_area("기획 의도 또는 포지셔닝 목표")
        submitted = st.form_submit_button("🚀 분석 시작")

        if submitted:
            st.markdown("### 분석 진행 중...")
            # 이곳에 분석 로직 삽입 가능
            st.success("분석이 완료되었습니다. 결과는 아래에 표시됩니다.")
            # 향후 실제 분석 결과 출력

