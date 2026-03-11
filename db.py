import mariadb
import streamlit as st
import pandas as pd


conn_params = {
  "user": "root",
  "password": "1234",
  "host": "192.168.0.201",
  "database" : "db_to_air",
  "port" : int(3306)
}

options = ['전체','AA', 'AS', 'CO', 'DL', 'EA']

@st.cache_data
def get_data(sql:str, cols:list):
    """데이터베이스에서 공항 데이터를 가져옵니다."""
    try:
        conn = mariadb.connect(**conn_params)
        cursor = conn.cursor()
        sql = f'''
        {sql}
        '''
        cursor.execute(sql)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=cols)
        cursor.close()
        conn.close()        
        return df

    except mariadb.Error as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        st.info("왼쪽 사이드바의 'DB 연결 정보'를 올바르게 입력했는지 확인하세요.")
        return pd.DataFrame()
