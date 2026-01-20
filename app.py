import streamlit as st

st.set_page_config(
    page_title="테스트",
    page_icon="📊",
)

st.title("📺 종편 4사 메인뉴스 시청률 Forecasting (전국)")
st.write("✅ 기본 앱 작동 테스트")

# 단계별 import 테스트
try:
    import pandas as pd
    st.write("✅ Pandas import 성공")
except Exception as e:
    st.error(f"❌ Pandas: {e}")

try:
    import plotly.graph_objects as go
    st.write("✅ Plotly import 성공")
except Exception as e:
    st.error(f"❌ Plotly: {e}")

try:
    from forecaster import NewsViewershipForecaster
    st.write("✅ Forecaster import 성공")
except Exception as e:
    st.error(f"❌ Forecaster: {e}")
    st.exception(e)

st.success("앱이 정상적으로 실행되었습니다!")
