import streamlit as st

st.title('항공사 운항 리스크와 노선 전략 인사이트')

st.set_page_config(
    page_title="1팀",
    page_icon="🛫",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

st.badge("First", color="red", icon="🗺")
st.markdown("취항 노선 분석")
st.badge("Second", color="yellow", icon="⚠")
st.markdown("지연 리스크 분석")
st.badge("Third", color="blue", icon="🚥")
st.markdown("우회 노선 분석")
st.badge("Fourth", color="green" , icon="❌")
st.markdown("취소율 분석")