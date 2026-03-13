import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from db import get_data, options

if 'options' not in st.session_state:
	st.session_state.options = 0


st.set_page_config(layout="wide")

st.title("항공사별 공항 위치 및 분포")
st.markdown("◾ 노선 확장 전략 수립")
st.markdown("◾ 경쟁 항공사 비교")

# 데이터 로드
sql = '''
        SELECT distinct *
        FROM 공항2
        ORDER BY 1, 2;
        '''
cols = ['항공사코드', '공항명', '공항코드', '도시', '위도', '경도']
df = get_data(sql, cols)
if not df.empty:
    st.success("데이터베이스 연결 및 데이터 로드 성공!")

    # --- 데이터 필터링 ---
    selected = st.selectbox(
    label="항공사를 선택하세요",
    options=options,
    index=0,
    placeholder="수집 대상을 선택하세요."
    ) 
    if selected == '전체':
        filtered_df = df
    else:
        filtered_df = df[df['항공사코드'] == selected]


    # 1. 지도 데이터 준비 (기존과 동일)
    st.header("공항 위치 지도")
    st.markdown(f"**{selected}** 항공사의 공항 위치입니다.")

    map_df = filtered_df[['위도', '경도', '도시']].copy()
    map_df.rename(columns={'위도': 'lat', '경도': 'lon'}, inplace=True)
    
    # 2. Pydeck을 이용한 지도 시각화
    st.pydeck_chart(pdk.Deck(
        map_style= None,
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
                'ScatterplotLayer', # 점을 찍는 레이어
                data=map_df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]', # RGBA 색상
                get_radius=50000 if selected == '전체' else 20000, # 점 크기
                pickable=True, # ⭐️ 중요: 이게 True여야 툴팁이 작동함
            ),
        ],
    ))
    st.markdown("---")

    # 2. 분포도 차트 (항공사별 취항 공항 수)
    st.header("항공사별 취항 공항 수")
    airline_counts = df['공항명'].value_counts().sort_index()
    st.bar_chart(airline_counts)

    st.markdown("---")
    # 3. 데이터 테이블
    st.header("상세 데이터")
    st.markdown(f"{selected} 항공사의 상세 데이터입니다.")
    st.dataframe(filtered_df)

else:
    st.warning("데이터를 불러오지 못했습니다. DB 연결 정보를 확인하고 다시 시도해주세요.")

