# ============================================================
# 뉴스 시청률 예측 웹앱 (Futuristic Design)
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import pickle
from forecaster import NewsViewershipForecaster

# 페이지 설정
st.set_page_config(
    page_title="📺 종편 4사 메인뉴스 시청률 Forecasting (전국)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 미래적인 다크 테마 CSS
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%);
        color: #e0e0e0;
    }

    /* 메인 타이틀 */
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7, #f107a3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(123, 47, 247, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from { filter: drop-shadow(0 0 10px #7b2ff7); }
        to { filter: drop-shadow(0 0 20px #00d4ff); }
    }

    /* 서브타이틀 */
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #00d4ff;
        margin-bottom: 2rem;
        letter-spacing: 2px;
    }

    /* 메트릭 카드 */
    .metric-card {
        background: linear-gradient(135deg, rgba(123, 47, 247, 0.1), rgba(0, 212, 255, 0.1));
        border: 2px solid;
        border-image: linear-gradient(45deg, #7b2ff7, #00d4ff) 1;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(123, 47, 247, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(0, 212, 255, 0.5);
    }

    .metric-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4ff;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #f107a3, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }

    .metric-range {
        font-size: 0.9rem;
        color: #888;
        margin-top: 0.5rem;
    }

    /* 탭 스타일링 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(26, 26, 46, 0.6);
        border-radius: 10px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #888;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(123, 47, 247, 0.2);
        border-color: #7b2ff7;
        color: #00d4ff;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #7b2ff7, #00d4ff) !important;
        color: white !important;
        border-color: #00d4ff !important;
    }

    /* 사이드바 */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0a0e27 100%);
        border-right: 2px solid #7b2ff7;
    }

    /* 버튼 */
    .stButton>button {
        background: linear-gradient(90deg, #7b2ff7, #00d4ff);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(123, 47, 247, 0.4);
    }

    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.6);
    }

    /* 데이터프레임 */
    .dataframe {
        background-color: rgba(26, 26, 46, 0.6) !important;
        border: 1px solid #7b2ff7 !important;
        border-radius: 10px;
    }

    /* 로딩 스피너 */
    .stSpinner > div {
        border-top-color: #00d4ff !important;
    }

    /* 인포 박스 */
    .info-box {
        background: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* 성공 박스 */
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 캐시 디렉토리 설정
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

@st.cache_data(ttl=3600)
def load_and_forecast(sheets_id, gid, predict_days=180):
    """데이터 로드 및 예측 (1시간 캐싱)"""
    forecaster = NewsViewershipForecaster(sheets_id, gid)
    forecaster.load_data()
    forecaster.setup_holidays()
    forecasts, target_dt = forecaster.run_forecast(predict_days)
    predictions = forecaster.get_today_predictions(target_dt)
    forecast_df = forecaster.get_forecast_dataframe(target_dt)

    # Prophet 모델 객체는 캐싱하지 않음 (pickle 문제)
    return {
        "colors": forecaster.colors,
        "order": forecaster.order,
        "forecasts": forecasts,
        "target_dt": target_dt,
        "predictions": predictions,
        "forecast_df": forecast_df,
        "data": forecaster.df,
        "holidays": forecaster.holidays
    }

def create_dashboard_chart(predictions, colors):
    """대시보드 차트 생성 (Plotly)"""
    channels = list(predictions.keys())
    values = [predictions[ch]["forecast"] for ch in channels]
    lower_95 = [predictions[ch]["lower_95"] for ch in channels]
    upper_95 = [predictions[ch]["upper_95"] for ch in channels]

    color_list = [colors[ch] for ch in channels]

    fig = go.Figure()

    # 예측값 바
    fig.add_trace(go.Bar(
        x=channels,
        y=values,
        name="예측값",
        marker=dict(
            color=color_list,
            line=dict(color='rgba(0, 212, 255, 0.8)', width=2)
        ),
        text=[f"{v:.3f}%" for v in values],
        textposition='outside',
        textfont=dict(size=14, color='white', family='Arial Black')
    ))

    # 신뢰구간 에러바
    fig.add_trace(go.Scatter(
        x=channels,
        y=values,
        error_y=dict(
            type='data',
            symmetric=False,
            array=[u - v for v, u in zip(values, upper_95)],
            arrayminus=[v - l for v, l in zip(values, lower_95)],
            color='rgba(0, 212, 255, 0.6)',
            thickness=2,
            width=8
        ),
        mode='markers',
        marker=dict(size=0),
        name='95% 신뢰구간',
        showlegend=True
    ))

    fig.update_layout(
        title=dict(
            text="📊 오늘의 예측 대시보드",
            font=dict(size=24, color='#00d4ff', family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text="채널", font=dict(size=16, color='#00d4ff')),
            tickfont=dict(size=14, color='white'),
            gridcolor='rgba(123, 47, 247, 0.2)'
        ),
        yaxis=dict(
            title=dict(text="시청률 (%)", font=dict(size=16, color='#00d4ff')),
            tickfont=dict(size=14, color='white'),
            gridcolor='rgba(123, 47, 247, 0.2)'
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        height=500,
        showlegend=True,
        legend=dict(
            bgcolor='rgba(26, 26, 46, 0.8)',
            bordercolor='#7b2ff7',
            borderwidth=1
        )
    )

    return fig

def create_trend_chart(forecasts, colors, order, target_dt, days=30, day_filter="All"):
    """채널별 추세 차트 생성"""
    fig = go.Figure()

    start_dt = target_dt - timedelta(days=30)
    end_dt = target_dt + timedelta(days=days)

    for ch in order:
        fc = forecasts[ch]
        fc_filtered = fc[(fc["ds"] >= start_dt) & (fc["ds"] <= end_dt)].copy()

        # 요일 정보 추가
        fc_filtered["dayofweek"] = pd.to_datetime(fc_filtered["ds"]).dt.day_name()
        fc_filtered["dayofweek_num"] = pd.to_datetime(fc_filtered["ds"]).dt.dayofweek
        day_map = {"Monday": "월", "Tuesday": "화", "Wednesday": "수", "Thursday": "목",
                   "Friday": "금", "Saturday": "토", "Sunday": "일"}
        fc_filtered["day_kr"] = fc_filtered["dayofweek"].map(day_map)

        # 주중/주말 필터링
        if day_filter == "Weekday":
            fc_filtered = fc_filtered[fc_filtered["dayofweek_num"] < 5]  # 월~금 (0-4)
        elif day_filter == "Weekend":
            fc_filtered = fc_filtered[fc_filtered["dayofweek_num"] >= 5]  # 토~일 (5-6)

        # 예측선
        fig.add_trace(go.Scatter(
            x=fc_filtered["ds"],
            y=fc_filtered["yhat"],
            name=ch,
            mode='lines',
            line=dict(color=colors[ch], width=3),
            customdata=fc_filtered["day_kr"],
            hovertemplate='<b>%{fullData.name}</b><br>%{x|%Y-%m-%d} (%{customdata})<br>Rating: %{y:.3f}%<extra></extra>'
        ))

        # 95% 신뢰구간
        fig.add_trace(go.Scatter(
            x=fc_filtered["ds"],
            y=fc_filtered["yhat_upper"],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=fc_filtered["ds"],
            y=fc_filtered["yhat_lower"],
            mode='lines',
            line=dict(width=0),
            fillcolor=f'rgba({int(colors[ch][1:3], 16)}, {int(colors[ch][3:5], 16)}, {int(colors[ch][5:7], 16)}, 0.2)',
            fill='tonexty',
            showlegend=False,
            hoverinfo='skip'
        ))

    # Target date 표시
    fig.add_shape(
        type="line",
        x0=target_dt,
        x1=target_dt,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#f107a3", width=2, dash="dash")
    )

    # Today 라벨 추가
    fig.add_annotation(
        x=target_dt,
        y=1,
        yref="paper",
        text="오늘",
        showarrow=False,
        font=dict(color="#f107a3", size=12),
        yshift=10
    )

    # 차트 제목에 필터 상태 표시
    filter_text = ""
    if day_filter == "Weekday":
        filter_text = " - 주중만"
    elif day_filter == "Weekend":
        filter_text = " - 주말만"

    fig.update_layout(
        title=dict(
            text=f"📈 예측 추세 ({days}일){filter_text}",
            font=dict(size=22, color='#00d4ff', family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text="날짜", font=dict(size=14, color='#00d4ff')),
            tickfont=dict(size=12, color='white'),
            gridcolor='rgba(123, 47, 247, 0.2)'
        ),
        yaxis=dict(
            title=dict(text="시청률 (%)", font=dict(size=14, color='#00d4ff')),
            tickfont=dict(size=12, color='white'),
            gridcolor='rgba(123, 47, 247, 0.2)'
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        height=600,
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(26, 26, 46, 0.8)',
            bordercolor='#7b2ff7',
            borderwidth=1,
            font=dict(size=12)
        )
    )

    return fig

def main():
    # 헤더
    st.markdown('<h1 class="main-title">📺 종편 4사 메인뉴스 시청률 Forecasting (전국)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Powered by Prophet - Meta\'s Time Series Forecasting</p>', unsafe_allow_html=True)

    # 사이드바 설정
    with st.sidebar:
        st.markdown("### ⚙️ 설정")

        sheets_id = st.text_input(
            "구글 시트 ID",
            value="1uv9gNT9TDEu2qtPPOnQlhiznnb4lxmogwQFWmQbclIc",
            help="구글 시트 ID를 입력하세요"
        )

        gid = st.text_input(
            "시트 GID",
            value="0",
            help="시트 GID를 입력하세요 (기본값: 0)"
        )

        predict_days = st.slider(
            "예측 기간 (일)",
            min_value=30,
            max_value=180,
            value=180,
            step=30
        )

        st.markdown("---")

        if st.button("🚀 분석 실행", use_container_width=True):
            st.session_state.run_analysis = True

        st.markdown("---")
        st.markdown("### 📊 채널 색상")
        st.markdown("🔵 **News_A** - 파란색")
        st.markdown("🟣 **JTBC** - 보라색")
        st.markdown("🟠 **MBN** - 주황색")
        st.markdown("🔴 **TVCHOSUN** - 빨간색")

        st.markdown("---")
        st.markdown(f"**마지막 업데이트:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        st.markdown("---")

        # About Prophet 확장 섹션
        with st.expander("ℹ️ About Prophet by Meta", expanded=False):
            st.markdown("""
            ### 📖 Prophet Overview

            **Prophet**은 Meta (Facebook)에서 개발한 오픈소스 시계열 예측 라이브러리입니다.

            #### 🎯 주요 특징

            **1. 강력한 계절성 처리**
            - 주간, 연간 패턴 자동 감지
            - 여러 계절성을 동시에 모델링

            **2. 공휴일 효과**
            - 공휴일의 영향을 자동으로 반영
            - 국가별 공휴일 지원

            **3. 변화점 감지**
            - 추세의 급격한 변화를 자동 감지
            - 유연한 비선형 추세 모델링

            **4. 결측값 처리**
            - 결측 데이터에 강건함
            - 이상치 자동 처리

            #### 🔬 기술적 배경

            Prophet은 **가법 회귀 모델** 기반:
            ```
            y(t) = g(t) + s(t) + h(t) + ε
            ```
            - **g(t)**: 추세 (성장 함수)
            - **s(t)**: 계절성 (주기적 변화)
            - **h(t)**: 공휴일 효과
            - **ε**: 오차항

            #### 💡 이 앱에서의 활용

            - **180일 장기 예측** 제공
            - **일몰 시각**을 추가 변수로 활용
            - **90%/95% 신뢰구간** 동시 표시
            - **한국 공휴일** (양력/음력) 반영

            #### 🔗 더 알아보기

            - [Prophet 공식 문서](https://facebook.github.io/prophet/)
            - [GitHub Repository](https://github.com/facebook/prophet)
            - [논문 (Taylor & Letham, 2018)](https://peerj.com/preprints/3190/)

            ---

            **사용 사례**: 수요 예측, 용량 계획, 이상 탐지,
            트렌드 분석 등 다양한 분야에서 활용
            """)

            st.success("✅ Prophet은 Meta의 수백만 예측 작업에서 검증된 안정적인 도구입니다.")

    # 초기 분석 실행
    if 'run_analysis' not in st.session_state:
        st.session_state.run_analysis = True

    if st.session_state.run_analysis:
        with st.spinner("🔮 데이터 로드 및 Prophet 모델 실행 중..."):
            try:
                result = load_and_forecast(sheets_id, gid, predict_days)
                st.session_state.result = result
                st.session_state.run_analysis = False
                st.success("✅ 분석이 성공적으로 완료되었습니다!")
            except Exception as e:
                st.error(f"❌ 오류: {str(e)}")
                return

    if 'result' not in st.session_state:
        st.info("👈 '분석 실행' 버튼을 클릭하여 예측을 시작하세요")
        return

    result = st.session_state.result
    predictions = result["predictions"]
    forecasts = result["forecasts"]
    target_dt = result["target_dt"]
    forecast_df = result["forecast_df"]
    data = result["data"]
    colors = result["colors"]
    order = result["order"]
    holidays_df = result["holidays"]

    # 메인 대시보드
    st.markdown("## 🎯 오늘의 예측")
    st.markdown(f"**예측 날짜:** {target_dt.strftime('%Y-%m-%d')}")

    # 메트릭 카드
    cols = st.columns(4)
    for i, ch in enumerate(order):
        pred = predictions[ch]
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{ch}</div>
                <div class="metric-value">{pred['forecast']:.3f}%</div>
                <div class="metric-range">
                    95% 신뢰구간: {pred['lower_95']:.3f} ~ {pred['upper_95']:.3f}<br>
                    90% 신뢰구간: {pred['lower_90']:.3f} ~ {pred['upper_90']:.3f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 대시보드 차트
    st.plotly_chart(create_dashboard_chart(predictions, colors), use_container_width=True)

    # 탭 구성
    tabs = st.tabs(["📈 추세 분석", "🔍 구성요소", "📊 데이터 테이블", "📥 다운로드"])

    # Tab 1: 추세 분석
    with tabs[0]:
        st.markdown("### 📈 예측 추세 분석")

        col1, col2 = st.columns([2, 1])
        with col1:
            trend_days = st.selectbox(
                "예측 기간 선택",
                options=[30, 60, 90, 180],
                index=1,
                format_func=lambda x: f"{x}일"
            )
        with col2:
            day_filter = st.radio(
                "필터",
                options=["전체", "주중", "주말"],
                horizontal=True,
                key="trend_day_filter",
                help="주중: 월~금 | 주말: 토~일"
            )

        # 영어 필터 이름을 한국어로 매핑
        day_filter_en = {"전체": "All", "주중": "Weekday", "주말": "Weekend"}[day_filter]

        st.plotly_chart(
            create_trend_chart(forecasts, colors, order, target_dt, days=trend_days, day_filter=day_filter_en),
            use_container_width=True
        )

        if day_filter != "전체":
            filter_name = "주중(월~금)" if day_filter == "주중" else "주말(토~일)"
            st.info(f"📌 {filter_name} 데이터만 표시 중")

        # 채널별 개별 차트
        st.markdown("### 🔎 채널별 상세 분석")

        col1, col2 = st.columns([2, 1])
        with col1:
            selected_channel = st.selectbox("채널 선택", order)
        with col2:
            day_filter_individual = st.radio(
                "필터",
                options=["전체", "주중", "주말"],
                horizontal=True,
                key="individual_day_filter",
                help="주중: 월~금 | 주말: 토~일"
            )

        fc = forecasts[selected_channel]
        fc_filtered = fc[fc["ds"] >= target_dt].head(trend_days).copy()

        # 요일 정보 추가
        fc_filtered["dayofweek"] = pd.to_datetime(fc_filtered["ds"]).dt.day_name()
        fc_filtered["dayofweek_num"] = pd.to_datetime(fc_filtered["ds"]).dt.dayofweek
        day_map = {"Monday": "월", "Tuesday": "화", "Wednesday": "수", "Thursday": "목",
                   "Friday": "금", "Saturday": "토", "Sunday": "일"}
        fc_filtered["day_kr"] = fc_filtered["dayofweek"].map(day_map)

        # 주중/주말 필터링
        day_filter_individual_en = {"전체": "All", "주중": "Weekday", "주말": "Weekend"}[day_filter_individual]
        if day_filter_individual_en == "Weekday":
            fc_filtered = fc_filtered[fc_filtered["dayofweek_num"] < 5]  # 월~금
        elif day_filter_individual_en == "Weekend":
            fc_filtered = fc_filtered[fc_filtered["dayofweek_num"] >= 5]  # 토~일

        fig = go.Figure()

        # 예측값
        fig.add_trace(go.Scatter(
            x=fc_filtered["ds"],
            y=fc_filtered["yhat"],
            name="예측값",
            mode='lines+markers',
            line=dict(color=colors[selected_channel], width=3),
            marker=dict(size=6),
            customdata=fc_filtered["day_kr"],
            hovertemplate='%{x|%Y-%m-%d} (%{customdata})<br>시청률: %{y:.3f}%<extra></extra>'
        ))

        # 95% 신뢰구간
        fig.add_trace(go.Scatter(
            x=fc_filtered["ds"],
            y=fc_filtered["yhat_upper"],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=fc_filtered["ds"],
            y=fc_filtered["yhat_lower"],
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(123, 47, 247, 0.2)',
            fill='tonexty',
            name='95% 신뢰구간'
        ))

        # 90% 신뢰구간
        fig.add_trace(go.Scatter(
            x=fc_filtered["ds"],
            y=fc_filtered["yhat_upper_90"],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=fc_filtered["ds"],
            y=fc_filtered["yhat_lower_90"],
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(0, 212, 255, 0.3)',
            fill='tonexty',
            name='90% 신뢰구간'
        ))

        # 차트 제목에 필터 상태 표시
        filter_text_individual = ""
        if day_filter_individual == "주중":
            filter_text_individual = " - 주중만"
        elif day_filter_individual == "주말":
            filter_text_individual = " - 주말만"

        fig.update_layout(
            title=f"{selected_channel} - 상세 예측{filter_text_individual}",
            xaxis_title="날짜",
            yaxis_title="시청률 (%)",
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white'),
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        if day_filter_individual != "전체":
            filter_name_ind = "주중(월~금)" if day_filter_individual == "주중" else "주말(토~일)"
            st.info(f"📌 {filter_name_ind} 데이터만 표시 중")

    # Tab 2: 구성요소
    with tabs[1]:
        st.markdown("### 🔍 예측 구성요소 분석")
        st.info("여러 요인(추세, 계절성, 공휴일, 일몰 시각)이 예측에 어떻게 기여하는지 보여줍니다.")

        component_channel = st.selectbox("구성요소 분석 채널 선택", order, key="component_channel")

        fc = forecasts[component_channel]

        # 1. Trend (추세)
        st.markdown("#### 📈 추세 - 장기 방향성")

        # 요일 정보 추가
        fc_with_day = fc.copy()
        fc_with_day["dayofweek"] = pd.to_datetime(fc_with_day["ds"]).dt.day_name()
        day_map = {"Monday": "월", "Tuesday": "화", "Wednesday": "수", "Thursday": "목",
                   "Friday": "금", "Saturday": "토", "Sunday": "일"}
        fc_with_day["day_kr"] = fc_with_day["dayofweek"].map(day_map)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=fc_with_day["ds"],
            y=fc_with_day["trend"],
            mode='lines',
            line=dict(color='#00d4ff', width=2),
            name='추세',
            customdata=fc_with_day["day_kr"],
            hovertemplate='%{x|%Y-%m-%d} (%{customdata})<br>추세: %{y:.3f}%<extra></extra>'
        ))
        fig_trend.update_layout(
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white'),
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor='rgba(123, 47, 247, 0.2)'),
            yaxis=dict(gridcolor='rgba(123, 47, 247, 0.2)', title="시청률 (%)")
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # 2. Weekly Seasonality (주간 패턴)
        if 'weekly' in fc.columns:
            st.markdown("#### 📅 주간 계절성 - 요일별 패턴")

            # 요일별로 그룹핑하여 평균 계산
            fc_weekly = fc[["ds", "weekly"]].copy()
            fc_weekly["dayofweek"] = pd.to_datetime(fc_weekly["ds"]).dt.dayofweek
            fc_weekly["dayname"] = pd.to_datetime(fc_weekly["ds"]).dt.day_name()

            # 요일별 평균 (월=0, 일=6)
            weekly_avg = fc_weekly.groupby(["dayofweek", "dayname"])["weekly"].mean().reset_index()
            weekly_avg = weekly_avg.sort_values("dayofweek")

            # 한글 요일명
            day_names_kr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_names_display = ["월", "화", "수", "목", "금", "토", "일"]

            fig_weekly = go.Figure()
            fig_weekly.add_trace(go.Bar(
                x=day_names_display,
                y=weekly_avg["weekly"],
                marker=dict(
                    color=weekly_avg["weekly"],
                    colorscale='Purples',
                    line=dict(color='#7b2ff7', width=2)
                ),
                text=[f"{v:+.3f}%" for v in weekly_avg["weekly"]],
                textposition='outside',
                name='주간 효과'
            ))

            fig_weekly.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                font=dict(color='white'),
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(
                    title="요일",
                    gridcolor='rgba(123, 47, 247, 0.2)',
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title="시청률 영향 (%)",
                    gridcolor='rgba(123, 47, 247, 0.2)'
                ),
                showlegend=False
            )
            st.plotly_chart(fig_weekly, use_container_width=True)

            # 인사이트 표시
            max_day = weekly_avg.loc[weekly_avg["weekly"].idxmax()]
            min_day = weekly_avg.loc[weekly_avg["weekly"].idxmin()]
            day_idx_to_kr = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}

            st.info(f"📌 **최고**: {day_idx_to_kr[max_day['dayofweek']]}요일 (+{max_day['weekly']:.3f}%) | **최저**: {day_idx_to_kr[min_day['dayofweek']]}요일 ({min_day['weekly']:+.3f}%)")

        # 3. Yearly Seasonality (연간 패턴)
        if 'yearly' in fc.columns:
            st.markdown("#### 🌍 연간 계절성 - 연중 패턴")
            fig_yearly = go.Figure()
            fig_yearly.add_trace(go.Scatter(
                x=fc_with_day["ds"],
                y=fc_with_day["yearly"],
                mode='lines',
                line=dict(color='#f107a3', width=2),
                name='연간',
                customdata=fc_with_day["day_kr"],
                hovertemplate='%{x|%Y-%m-%d} (%{customdata})<br>효과: %{y:.3f}%<extra></extra>'
            ))
            fig_yearly.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                font=dict(color='white'),
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(gridcolor='rgba(123, 47, 247, 0.2)'),
                yaxis=dict(gridcolor='rgba(123, 47, 247, 0.2)', title="효과")
            )
            st.plotly_chart(fig_yearly, use_container_width=True)

        # 4. Holidays Effect (공휴일 효과)
        if 'holidays' in fc.columns:
            st.markdown("#### 🎉 공휴일 효과")
            # 공휴일 효과가 있는 날만 필터링
            holidays_effect = fc[fc['holidays'].abs() > 0.001].copy()
            if len(holidays_effect) > 0:
                # 공휴일 이름 매핑
                holidays_effect["date_str"] = pd.to_datetime(holidays_effect["ds"]).dt.strftime('%Y-%m-%d')
                holidays_lookup = holidays_df.copy()
                holidays_lookup["ds_str"] = pd.to_datetime(holidays_lookup["ds"]).dt.strftime('%Y-%m-%d')

                # 날짜별로 공휴일 이름 매핑 (window 고려)
                holiday_names = []
                for date_str in holidays_effect["date_str"]:
                    date_obj = pd.to_datetime(date_str)
                    # 해당 날짜와 전후 날짜 확인 (lower_window, upper_window 고려)
                    matched_holidays = []
                    for _, h in holidays_lookup.iterrows():
                        h_date = pd.to_datetime(h["ds"])
                        lower = h.get("lower_window", 0)
                        upper = h.get("upper_window", 0)
                        if h_date + pd.Timedelta(days=lower) <= date_obj <= h_date + pd.Timedelta(days=upper):
                            matched_holidays.append(h["holiday"])

                    if matched_holidays:
                        holiday_names.append(", ".join(matched_holidays))
                    else:
                        holiday_names.append("Unknown")

                holidays_effect["holiday_name"] = holiday_names

                # 한글 공휴일 이름 매핑
                holiday_kr_names = {
                    "new_year": "신정",
                    "lunar_new_year": "설날",
                    "childrens_day": "어린이날",
                    "buddha_birthday": "부처님오신날",
                    "memorial_day": "현충일",
                    "liberation_day": "광복절",
                    "chuseok": "추석",
                    "national_day": "개천절",
                    "hangeul_day": "한글날",
                    "christmas": "크리스마스"
                }

                holidays_effect["holiday_kr"] = holidays_effect["holiday_name"].apply(
                    lambda x: ", ".join([holiday_kr_names.get(h.strip(), h.strip()) for h in x.split(",")])
                )

                # 요일 추가
                holidays_effect["dayofweek"] = pd.to_datetime(holidays_effect["ds"]).dt.day_name()
                day_names_kr_map = {
                    "Monday": "월", "Tuesday": "화", "Wednesday": "수", "Thursday": "목",
                    "Friday": "금", "Saturday": "토", "Sunday": "일"
                }
                holidays_effect["dayofweek_kr"] = holidays_effect["dayofweek"].map(day_names_kr_map)
                holidays_effect["date_with_day"] = pd.to_datetime(holidays_effect["ds"]).dt.strftime('%Y-%m-%d') + " (" + holidays_effect["dayofweek_kr"] + ")"

                fig_holidays = go.Figure()
                fig_holidays.add_trace(go.Scatter(
                    x=holidays_effect["ds"],
                    y=holidays_effect["holidays"],
                    mode='markers',
                    marker=dict(color='#EDB120', size=10),
                    name='공휴일 효과',
                    text=holidays_effect["holiday_kr"],
                    customdata=holidays_effect["date_with_day"],
                    hovertemplate='<b>%{text}</b><br>%{customdata}<br>효과: %{y:+.3f}%<extra></extra>'
                ))
                fig_holidays.update_layout(
                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    paper_bgcolor='rgba(0, 0, 0, 0)',
                    font=dict(color='white'),
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(gridcolor='rgba(123, 47, 247, 0.2)'),
                    yaxis=dict(gridcolor='rgba(123, 47, 247, 0.2)', title="효과")
                )
                st.plotly_chart(fig_holidays, use_container_width=True)
            else:
                st.info("예측 기간에 유의미한 공휴일 효과가 없습니다.")

        # 5. Sunset Time Effect (일몰 시각 효과)
        st.markdown("#### 🌅 일몰 시각 - 일몰 타이밍의 영향")
        col1, col2 = st.columns(2)

        with col1:
            # 일몰 시각 변화
            fig_sunset = go.Figure()
            fig_sunset.add_trace(go.Scatter(
                x=fc_with_day["ds"],
                y=fc_with_day["sunset_time"],
                mode='lines',
                line=dict(color='#FFA500', width=2),
                name='일몰 시각',
                customdata=fc_with_day["day_kr"],
                hovertemplate='%{x|%Y-%m-%d} (%{customdata})<br>일몰: %{y:.1f}시<extra></extra>'
            ))
            fig_sunset.update_layout(
                title="일몰 시각 (24시간 기준)",
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                font=dict(color='white'),
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor='rgba(123, 47, 247, 0.2)'),
                yaxis=dict(gridcolor='rgba(123, 47, 247, 0.2)', title="시각 (24시)")
            )
            st.plotly_chart(fig_sunset, use_container_width=True)

        with col2:
            # 일몰 효과 계산
            # Prophet의 regressor 효과 = 예측값 - (추세 + seasonalities + 공휴일)
            sunset_effect = fc["yhat"].copy()

            if 'trend' in fc.columns:
                sunset_effect = sunset_effect - fc["trend"]
            if 'weekly' in fc.columns:
                sunset_effect = sunset_effect - fc["weekly"]
            if 'yearly' in fc.columns:
                sunset_effect = sunset_effect - fc["yearly"]
            if 'holidays' in fc.columns:
                sunset_effect = sunset_effect - fc["holidays"]

            # 이중 축 차트
            fig_dual = go.Figure()

            # 시청률 (왼쪽 축)
            fig_dual.add_trace(go.Scatter(
                x=fc_with_day["ds"],
                y=fc_with_day["yhat"],
                mode='lines',
                line=dict(color='#00d4ff', width=2),
                name='시청률 (%)',
                yaxis='y',
                customdata=fc_with_day["day_kr"],
                hovertemplate='%{x|%Y-%m-%d} (%{customdata})<br>시청률: %{y:.3f}%<extra></extra>'
            ))

            # 일몰 효과 (오른쪽 축)
            fig_dual.add_trace(go.Scatter(
                x=fc_with_day["ds"],
                y=sunset_effect,
                mode='lines',
                line=dict(color='#FFA500', width=2, dash='dash'),
                name='일몰 효과',
                yaxis='y2',
                customdata=fc_with_day["day_kr"],
                hovertemplate='%{x|%Y-%m-%d} (%{customdata})<br>효과: %{y:.3f}%<extra></extra>'
            ))

            fig_dual.update_layout(
                title="시청률 & 일몰 효과 시계열",
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                font=dict(color='white'),
                height=300,
                margin=dict(l=50, r=50, t=40, b=20),
                xaxis=dict(
                    gridcolor='rgba(123, 47, 247, 0.2)',
                    title="날짜"
                ),
                yaxis=dict(
                    title=dict(text="시청률 (%)", font=dict(color='#00d4ff')),
                    tickfont=dict(color='#00d4ff'),
                    gridcolor='rgba(123, 47, 247, 0.2)'
                ),
                yaxis2=dict(
                    title=dict(text="일몰 효과", font=dict(color='#FFA500')),
                    tickfont=dict(color='#FFA500'),
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    x=0.01,
                    y=0.99,
                    bgcolor='rgba(26, 26, 46, 0.8)',
                    bordercolor='#7b2ff7',
                    borderwidth=1
                ),
                hovermode='x unified'
            )
            st.plotly_chart(fig_dual, use_container_width=True)

        # 요약 정보
        st.markdown("---")
        st.markdown("### 📊 구성요소 요약")
        col1, col2, col3 = st.columns(3)

        with col1:
            trend_change = fc["trend"].iloc[-1] - fc["trend"].iloc[0]
            st.metric(
                "추세 변화",
                f"{trend_change:+.3f}%",
                delta=f"{'↑' if trend_change > 0 else '↓'} {abs(trend_change):.3f}%"
            )

        with col2:
            if 'weekly' in fc.columns:
                weekly_range = fc["weekly"].max() - fc["weekly"].min()
                st.metric(
                    "주간 변동폭",
                    f"±{weekly_range/2:.3f}%"
                )

        with col3:
            if 'sunset_time' in fc.columns:
                sunset_min = fc["sunset_time"].min()
                sunset_max = fc["sunset_time"].max()
                sunset_first = fc["sunset_time"].iloc[0]
                sunset_last = fc["sunset_time"].iloc[-1]
                st.metric(
                    "일몰 시각 범위",
                    f"{sunset_min:.1f}시 - {sunset_max:.1f}시",
                    delta=f"{sunset_first:.1f}시 → {sunset_last:.1f}시"
                )
            else:
                st.metric("일몰 효과", f"±{sunset_effect.std():.3f}%")

    # Tab 3: 데이터 테이블
    with tabs[2]:
        st.markdown("### 📊 예측 데이터 테이블")

        col1, col2 = st.columns(2)
        with col1:
            filter_channel = st.multiselect(
                "채널 필터",
                options=order,
                default=order
            )
        with col2:
            date_range = st.slider(
                "날짜 범위 (오늘부터 일수)",
                min_value=1,
                max_value=predict_days,
                value=(1, 30)
            )

        # 데이터 필터링
        filtered_df = forecast_df[forecast_df["Channel"].isin(filter_channel)].copy()
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])

        start_date = target_dt + timedelta(days=date_range[0]-1)
        end_date = target_dt + timedelta(days=date_range[1]-1)

        filtered_df = filtered_df[
            (filtered_df["Date"] >= start_date) &
            (filtered_df["Date"] <= end_date)
        ]

        # 표시용 데이터프레임 생성 (포맷 조정)
        display_df = filtered_df.copy()
        display_df["Date"] = display_df["Date"].dt.strftime('%Y-%m-%d')  # 시간 제거

        # 숫자 컬럼 소숫점 셋째자리까지만 표시
        numeric_cols = ["Forecast", "Lower_95", "Upper_95", "Lower_90", "Upper_90", "Sunset_Time"]
        for col in numeric_cols:
            if col in display_df.columns:
                display_df[col] = display_df[col].round(3)

        st.dataframe(
            display_df.style.background_gradient(subset=["Forecast"], cmap="viridis"),
            use_container_width=True,
            height=400
        )

        # 통계 요약
        st.markdown("### 📈 통계 요약")
        summary_cols = st.columns(4)

        for i, ch in enumerate(filter_channel):
            ch_data = filtered_df[filtered_df["Channel"] == ch]
            with summary_cols[i % 4]:
                st.metric(
                    label=ch,
                    value=f"{ch_data['Forecast'].mean():.3f}%",
                    delta=f"±{ch_data['Forecast'].std():.3f}"
                )

    # Tab 4: 다운로드
    with tabs[3]:
        st.markdown("### 📥 결과 다운로드")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### CSV 파일")

            # 오늘 예측
            today_csv = forecast_df[forecast_df["Date"] == target_dt.strftime("%Y-%m-%d")].to_csv(index=False)
            st.download_button(
                label="📄 오늘 예측 다운로드",
                data=today_csv,
                file_name=f"forecast_today_{target_dt.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

            # 전체 예측
            full_csv = forecast_df.to_csv(index=False)
            st.download_button(
                label=f"📄 전체 예측 다운로드 ({predict_days}일)",
                data=full_csv,
                file_name=f"forecast_{predict_days}days_{target_dt.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            st.markdown("#### 데이터 정보")
            st.info(f"""
            **데이터 기간:** {data['날짜'].min().strftime('%Y-%m-%d')} ~ {data['날짜'].max().strftime('%Y-%m-%d')}

            **전체 레코드 수:** {len(data)}

            **예측 시작일:** {target_dt.strftime('%Y-%m-%d')}

            **예측 일수:** {predict_days}

            **채널 수:** {len(order)}
            """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 2rem;'>
        <p>🤖 Prophet AI & Streamlit 기반</p>
        <p>📊 실시간 뉴스 시청률 분석</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
