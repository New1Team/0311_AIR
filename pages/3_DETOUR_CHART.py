import streamlit as st
import mariadb
import pandas as pd


st.set_page_config(layout="wide")
st.title("항공사별 우회 분석")

conn_params = {
  "user": "root",
  "password": "1234",
  "host": "192.168.0.201",
  "database" : "db_to_air",
  "port" : int(3306)
}

@st.cache_data
def get_data():
    """데이터베이스에서 공항 데이터를 가져옵니다."""
    try:
        conn = mariadb.connect(**conn_params)
        cursor = conn.cursor()
        query= '''
        select 
        d.`년도`, 
        d.`월`, 
        d.`일`, 
        d.`요일`, 
        d.`항공사코드`,
        d.`항공편번호`,
        d.`출발공항코드`,
        d.`도착지공항코드`,
        d.`비행거리`
        FROM `항공우회분석` AS d
        
        ORDER BY d.`년도`,d.`월`
        '''
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['년도', '월', '일', '요일','항공사코드','항공편번호','출발공항코드','도착지공항코드','비행거리'])
        cursor.close()
        conn.close()

        df['년도'] = pd.to_numeric(df['년도'], errors='coerce')
        df['비행거리'] = pd.to_numeric(df['비행거리'], errors='coerce')
        return df

    except mariadb.Error as e:
        st.error(f"데이터베이스 연결 오류:{e}")
        st.info("왼쪽 사이드바의 'DB 연결 정보'를 올바르게 입력했는지 확인하세요.")
        return pd.DataFrame()

