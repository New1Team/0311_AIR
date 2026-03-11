from db import get_data, options
import streamlit as st
import pandas as pd
import altair as alt

sql = '''
        SELECT *
        FROM risk_level
        '''

cols = ['년도', '월', '항공사코드', '항공사명', '전체비행수', 'risk1_경미', 'risk2_보통','risk3_위험']
df = get_data(sql, cols)

sql2 = '''
        SELECT 
        항공사코드, 
        항공사명,
        SUM(risk1_경미) AS 'col1', 
        SUM(risk2_보통) AS 'col2', 
        SUM(risk3_위험) AS 'col3'
        FROM risk_level
        GROUP BY 1;
        '''
cols2 = ['항공사코드', '항공사명', '30분 이하', '3시간 미만', '3시간 이상']
df2 = get_data(sql2, cols2)

 # --- 꺾은선 그래프 ---
if not df.empty:
    st.success("데이터베이스 연결 및 데이터 로드 성공!")
    st.line_chart(
        data=df2,
        x="항공사명", 
        y=['30분 이하', '3시간 미만', '3시간 이상'], 
        x_label='항공사', 
        y_label='지연 횟수', 
        color=["#1f77b4", "#0bcfd6", "#582ca0"], 
        width="stretch", 
        height=400,
        use_container_width=None)
    # --- 막대그래프 ---

if not df.empty:
    st.success("데이터베이스 연결 및 데이터 로드 성공!")
   
    st.header("항공사별 지연 그래프")
    # --- 데이터 필터링 ---
    col1, col2, col3 = st.columns(3)
    years = sorted(df['년도'].unique())
    airline = dict(zip(df['항공사명'], df['항공사코드']))
    airline_name = sorted(airline.keys())
    with col1:
        selected_year = st.selectbox(
        label="년도를 선택하세요",
        options=years,
        index=None
    )
    with col2:
        if selected_year == 1987:
            months = [10,11,12]
        else:
            months = sorted(df['월'].unique())
        selected_month = st.selectbox(
            label = "월을 선택하세요",
            options = months,
            index = None
        )
    with col3:
        selected_name = st.selectbox(
            label = "항공사를 선택하세요",
            options = options[1:],
            index = None
        )
    
    # --- 출력 버튼 ---

    if st.button("선택"):
        is_year = (df['년도'].astype(int) == int(selected_year))
        is_month = (df['월'].astype(int) == int(selected_month))
        is_airline = (df['항공사코드'].astype(str).str.strip() == str(selected_name).strip())
        data = df[is_year & is_month & is_airline]
        
        categories = ['risk1_경미', 'risk2_보통', 'risk3_위험']
        views = ['30분미만', '3시간 미만', '3시간 이상']
        chart_list = []
        for cat, view in zip(categories,views):
            chart_list.append(
                {
                    '구분': f'{view}',
                    '유형': f'{view}',
                    '값': data[f'{cat}'].sum()
                }
            )
            print(df)
        plot_df = pd.DataFrame(chart_list)

        chart = alt.Chart(plot_df).mark_bar().encode(
            x = alt.X('유형:N', title=None),
            y = alt.Y('값:Q', title='risk level'),
            color = alt.Color('유형:N'),
            # column = alt.Column('구분:N')
        ).properties(
            width = 200
        )
        st.altair_chart(chart)

else:
    st.warning("데이터를 불러오지 못했습니다. DB 연결 정보를 확인하고 다시 시도해주세요.")