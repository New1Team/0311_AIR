import streamlit as st
from db import get_data, options


sql = '''
        SELECT 항공사코드, COUNT(*) AS cnt FROM 항공취소분석
        GROUP BY 항공사코드
        ORDER BY cnt DESC
        LIMIT 5;
        '''

cols = ['항공사코드','취소수']
df = get_data(sql, cols)

st.dataframe(
    data=df, 
    width="stretch",
    height="auto",
    use_container_width=None,
    hide_index=None, 
    column_order=None, 
    column_config=None, 
    key=None, 
    on_select="ignore", 
    selection_mode="multi-row", 
    row_height=None, 
    placeholder=None)