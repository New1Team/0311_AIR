# import streamlit as st
# from db import get_data, options

# sql = '''
#         SELECT 항공사코드, COUNT(*) AS cnt FROM 항공취소분석
#         GROUP BY 항공사코드
#         ORDER BY cnt DESC
#         LIMIT 5;
#         '''

# cols = ['항공사코드','취소수']
# df = get_data(sql, cols)

# st.dataframe(
#     data=df, 
#     width="stretch",
#     height="auto",
#     use_container_width=None,
#     hide_index=None, 
#     column_order=None, 
#     column_config=None, 
#     key=None, 
#     on_select="ignore", 
#     selection_mode="multi-row", 
#     row_height=None, 
#     placeholder=None)

import streamlit as st
import pandas as pd
import mariadb



# 1. 데이터베이스 연결 설정
conn_params = {
    "user": "root",
    "password": "1234",
    "host": "192.168.0.201",
    "database": "db_to_air",
    "port": 3306
}

@st.cache_data
def get_all_airlines():
    """DB에서 모든 항공사 코드를 가져옵니다."""
    try:
        conn = mariadb.connect(**conn_params)
        cursor = conn.cursor()
        query = "SELECT DISTINCT `항공사코드` FROM `항공취소분석` ORDER BY `항공사코드` "
        cursor.execute(query)
        airlines = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return airlines
    except Exception as e:
        st.error(f"항공사 목록 로드 실패: {e}")
        return []

@st.cache_data
def get_airline_stats(year):
    try:
        conn = mariadb.connect(**conn_params)
        query = f"""
        SELECT `항공사코드`, COUNT(*) as cnt
        FROM `항공취소분석`
        WHERE `년도` = {year}
        GROUP BY `항공사코드`
        ORDER BY cnt DESC
        """
        df_all = pd.read_sql(query, conn)
        conn.close()
        return df_all
    except Exception as e:
        st.error(f"통계 로드 실패: {e}")
        return pd.DataFrame()
 
@st.cache_data
def load_cancellation_data(year, airline):
    try:
        conn = mariadb.connect(**conn_params)
        query = f"""
        SELECT `년도`, `월`, `일`, `요일`, `항공사코드`, `항공편번호`, `출발공항코드` 
        FROM `항공취소분석` 
        WHERE `년도` = {year} 
        AND `항공사코드` = '{airline}'
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

# --- 화면 구성 ---
st.set_page_config(layout="wide")
st.title("취소 트렌드 분석")
st.markdown("◾ 운항 안정성 추세 파악")
st.markdown("◾ 취소 발생 패턴 분석")

airline_list = get_all_airlines()
st.subheader(" 조회 조건 설정")
col_sel1, col_sel2 = st.columns(2)

with col_sel1:
    selected_year = st.selectbox("년도 선택", [1987, 1988, 1989], index=2)

with col_sel2:
    selected_airline = st.selectbox("항공사 코드 선택", options=airline_list)

st.divider()

all_stats = get_airline_stats(selected_year) # 전체 통계 가져오기
data = load_cancellation_data(selected_year, selected_airline)

if not all_stats.empty:
    st.subheader(f"{selected_year}년 전체 항공사 취소 현황")
    total_market_cancelled = all_stats['cnt'].sum()
    market_avg = all_stats['cnt'].mean()
   

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("전체 항공사 총 쉬소", f"{total_market_cancelled:,}건")
    
    with m_col2:
        st.metric("전체 항공사 평균 취소", f"{market_avg:.1f}건")
    
    st.divider()


# 데이터 로드

if not data.empty and not all_stats.empty:
   
    my_cancel_count = len(data)
    my_montly_avg = my_cancel_count / data['월'].nunique()
    avg_cancel_count = all_stats['cnt'].mean()
    try:
        rank = all_stats[all_stats['항공사코드'] == selected_airline].index[0] + 1
        total_airlines = len(all_stats)
    except IndexError:
        rank = "-"

    st.header(f" {selected_year}년 {selected_airline} 취소 데이터 분석")

    # --- 3개의 지표를 가로로 배치 ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("선택 항공사 취소 건수", f"{my_cancel_count:,}건")
        
    with col2:
        # 평균 대비 얼마나 많고 적은지 delta 표시 (선택사항)
        diff = my_cancel_count - avg_cancel_count
        st.metric(
            label="항공사별 평균 취소 건수",
            value= f"{my_montly_avg:.1f}건", 
        )
        
    with col3:
        st.metric("취소 횟수 순위", f"{rank}위 / {total_airlines}개")

    st.divider()
    
    # --- 차트 영역 ---
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader(" 월별 취소 건수")
        st.bar_chart(data.groupby('월').size())

    with col_chart2:
        st.subheader(" 요일별 취소 건수")
        st.bar_chart(data.groupby('요일').size())

    with st.expander(" 상세 데이터 보기"):
        st.dataframe(data, use_container_width=True)

else:
    st.warning("데이터를 불러올 수 없습니다.")