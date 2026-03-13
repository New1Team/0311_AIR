import streamlit as st
import pandas as pd
import pydeck as pdk
from db import get_data

st.set_page_config(layout="wide")

# -----------------------------
# 스타일
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}
.small-help {
    font-size: 0.95rem;
    color: #6b7280;
    margin-bottom: 1rem;
}
.metric-card {
    padding: 18px;
    border-radius: 16px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    min-height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.metric-title {
    font-size: 1rem;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.2;
}
.metric-sub {
    font-size: 0.95rem;
    color: #4b5563;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 제목
# -----------------------------
st.title("항공사별 공항 위치 및 분포")
st.markdown(
    '<div class="small-help">선택한 항공사의 공항 위치를 지도에서 확인하고, 취항 공항 수를 전체 평균과 비교합니다.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# 데이터 로드
# -----------------------------
sql = """
SELECT DISTINCT *
FROM 공항2
ORDER BY 1, 2;
"""
cols = ['항공사코드', '공항명', '공항코드', '도시', '위도', '경도']
df = get_data(sql, cols)

if not df.empty:
    st.success("데이터베이스 연결 및 데이터 로드 성공!")

    # 전처리
    df['항공사코드'] = df['항공사코드'].astype(str).str.strip()
    df['공항코드'] = df['공항코드'].astype(str).str.strip()
    df['공항명'] = df['공항명'].astype(str).str.strip()
    df['도시'] = df['도시'].astype(str).str.strip()

    # -----------------------------
    # 항공사 선택 옵션: DB 기준
    # -----------------------------
    airline_list = sorted(df['항공사코드'].dropna().unique().tolist())
    select_options = ['전체'] + airline_list

    selected = st.selectbox(
        label="항공사를 선택하세요",
        options=select_options,
        index=0
    )

    if selected == '전체':
        filtered_df = df.copy()
    else:
        filtered_df = df[df['항공사코드'] == selected].copy()

    # -----------------------------
    # 지도
    # -----------------------------
    st.header("공항 위치 지도")
    st.markdown(f"**{selected}** 항공사의 공항 위치입니다.")

    map_df = filtered_df[['위도', '경도', '도시']].copy()
    map_df = map_df.dropna(subset=['위도', '경도'])
    map_df.rename(columns={'위도': 'lat', '경도': 'lon'}, inplace=True)

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=map_df['lat'].mean() if not map_df.empty else 37.5,
            longitude=map_df['lon'].mean() if not map_df.empty else 127.0,
            zoom=1 if selected == '전체' else 3,
            pitch=0,
        ),
        tooltip={
            "html": "<b>공항:</b> {도시}",
            "style": {"color": "white"}
        },
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=map_df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=50000 if selected == '전체' else 20000,
                pickable=True,
            ),
        ],
    ))

    st.markdown("---")

    # -----------------------------
    # 항공사별 취항 공항 수 계산
    # -----------------------------
    airline_airport_counts = (
        df.groupby('항공사코드')['공항코드']
        .nunique()
        .sort_index()
    )

    avg_airports = airline_airport_counts.mean()

    if selected == '전체':
        selected_airport_count = df['공항코드'].nunique()
    else:
        selected_airport_count = filtered_df['공항코드'].nunique()

    # 항공사 순위
    rank_df = airline_airport_counts.sort_values(ascending=False).reset_index()
    rank_df.columns = ['항공사코드', '취항공항수']
    rank_df['순위'] = rank_df.index + 1
    total_airlines = len(rank_df)

    if selected == '전체':
        selected_rank_text = "전체 조회"
    else:
        selected_rank = int(rank_df.loc[rank_df['항공사코드'] == selected, '순위'].iloc[0])
        selected_rank_text = f"{selected_rank}위 / {total_airlines}"

    # -----------------------------
    # 카드 뉴스형 요약
    # -----------------------------
    st.header("항공사별 취항 공항 수")

    if selected == '전체':
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">전체 평균 취항 공항 수</div>
                <div class="metric-value">{avg_airports:.1f}개</div>
                <div class="metric-sub">항공사당 평균 고유 공항 수</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">전체 고유 공항 수</div>
                <div class="metric-value">{selected_airport_count}개</div>
                <div class="metric-sub">전체 항공사 기준 고유 공항 수</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        total_airports = df['공항코드'].nunique()
        selected_ratio = (selected_airport_count / total_airports * 100) if total_airports else 0

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">전체 평균 취항 공항 수</div>
                <div class="metric-value">{avg_airports:.1f}개</div>
                <div class="metric-sub">항공사당 평균 고유 공항 수</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{selected} 취항 공항 수</div>
                <div class="metric-value">{selected_airport_count}개</div>
                <div class="metric-sub">{selected_rank_text}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">전체 공항 대비 비중</div>
                <div class="metric-value">{selected_ratio:.1f}%</div>
                <div class="metric-sub">전체 고유 공항 {total_airports}개 중</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 항공사별 취항 공항 수 비교")
    st.bar_chart(airline_airport_counts)

    st.markdown("---")

    # -----------------------------
    # 상세 데이터
    # -----------------------------
    st.header("상세 데이터")
    st.markdown(f"{selected} 항공사의 상세 데이터입니다.")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.warning("데이터를 불러오지 못했습니다. DB 연결 정보를 확인하고 다시 시도해주세요.")