import streamlit as st

st.set_page_config(
    page_title="테스트 앱",
    page_icon="📊",
    layout="wide"
)

st.title("📺 종편 4사 메인뉴스 시청률 Forecasting (전국)")
st.write("앱이 정상적으로 시작되었습니다!")

if st.button("테스트 버튼"):
    st.success("버튼이 작동합니다!")
