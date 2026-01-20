# 📺 News Viewership Forecast Web App

미래적인 디자인의 AI 기반 뉴스 시청률 예측 웹 애플리케이션

## ✨ 주요 기능

- 🎨 **미래적 UI**: 다크 테마 + 네온 효과로 구현된 현대적인 디자인
- 📊 **실시간 예측**: Prophet AI 모델을 활용한 최대 180일 장기 예측
- 📈 **인터랙티브 차트**: Plotly 기반의 동적 시각화
- 🔍 **다중 탭 구조**: 대시보드, 추세 분석, 구성요소, 데이터 테이블
- 💾 **자동 캐싱**: 1시간 캐싱으로 빠른 로딩 속도
- 📥 **데이터 다운로드**: CSV 형식으로 예측 결과 다운로드
- 🌅 **일몰 시각 변수**: 서울 일몰 시각을 추가 변수로 활용
- 📅 **한국 공휴일**: 양력/음력 공휴일 자동 반영

## 🚀 설치 및 실행

### 1. 저장소 클론 또는 다운로드

```bash
cd news_forecast_app
```

### 2. 가상환경 생성 (권장)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

**중요**: Prophet과 CmdStan 설치 시간이 소요될 수 있습니다 (3-5분).

### 4. CmdStan 설치 (자동)

Prophet 실행 시 자동으로 CmdStan이 설치됩니다. 수동 설치를 원하는 경우:

```python
import cmdstanpy
cmdstanpy.install_cmdstan()
```

### 5. 웹앱 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱에 접속할 수 있습니다.

## 📖 사용 방법

### 기본 사용

1. **앱 시작**: 자동으로 데이터를 로드하고 분석을 시작합니다
2. **사이드바 설정**:
   - Google Sheets ID 입력
   - 예측 기간 선택 (30~180일)
   - "Run Analysis" 버튼 클릭
3. **결과 확인**: 다양한 탭에서 예측 결과 확인

### 탭별 기능

#### 📊 대시보드 (메인)
- 오늘의 예측값 메트릭 카드
- 4개 채널 비교 차트
- 90%/95% 신뢰구간 표시

#### 📈 Trend Analysis
- 시계열 추세 분석
- 다중 채널 비교
- 개별 채널 상세 분석
- 신뢰구간 시각화

#### 🔍 Components
- 예측 구성요소 분석
- 추세, 계절성, 공휴일 효과
- 일몰 시각 영향 분석

#### 📊 Data Table
- 상세 예측 데이터 테이블
- 채널 및 날짜 필터링
- 통계 요약 정보

#### 📥 Download
- CSV 파일 다운로드
- 오늘의 예측 / 전체 예측
- 데이터 정보 확인

## ⚙️ 설정

### Google Sheets 설정

1. Google Sheets에서 시청률 데이터 준비
2. 시트 URL에서 ID 추출:
   ```
   https://docs.google.com/spreadsheets/d/[SHEETS_ID]/edit#gid=[GID]
   ```
3. 앱 사이드바에 ID 입력

### 데이터 형식

필수 컬럼:
- `날짜`: 날짜 (YYMMDD, YYYYMMDD 형식)
- `뉴스A`: News A 시청률
- `JTBC뉴스룸`: JTBC 시청률
- `MBN뉴스7`: MBN 시청률
- `TV조선뉴스9`: TV조선 시청률

## 🎨 UI 커스터마이징

`app.py`의 CSS 섹션에서 색상과 스타일을 수정할 수 있습니다:

```python
# 그라디언트 색상
background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%);

# 네온 효과
text-shadow: 0 0 30px rgba(123, 47, 247, 0.5);
```

## 📊 모델 파라미터 조정

`forecaster.py`의 Prophet 파라미터를 수정하여 예측 정확도를 조정할 수 있습니다:

```python
m = Prophet(
    seasonality_mode="additive",
    seasonality_prior_scale=5.0,      # 계절성 강도
    holidays_prior_scale=5.0,         # 공휴일 효과
    changepoint_prior_scale=0.05,     # 추세 변화 민감도
    interval_width=0.95               # 신뢰구간 (95%)
)
```

## 🔧 문제 해결

### CmdStan 설치 오류

```bash
pip install --upgrade cmdstanpy
python -c "import cmdstanpy; cmdstanpy.install_cmdstan()"
```

### Prophet 설치 오류

Windows의 경우 C++ 빌드 도구가 필요할 수 있습니다:
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) 설치

### 메모리 부족

예측 기간을 줄이거나 캐시를 클리어하세요:
```bash
streamlit cache clear
```

## 📦 프로젝트 구조

```
news_forecast_app/
├── app.py                 # 메인 Streamlit 앱
├── forecaster.py          # Prophet 예측 엔진
├── requirements.txt       # 의존성 패키지
├── README.md             # 프로젝트 문서
└── cache/                # 캐시 디렉토리 (자동 생성)
```

## 🌟 주요 기술 스택

- **Streamlit**: 웹 프레임워크
- **Prophet**: 시계열 예측 모델
- **Plotly**: 인터랙티브 차트
- **Pandas**: 데이터 처리
- **Ephem**: 천문 계산 (일몰 시각)
- **Korean Lunar Calendar**: 음력 공휴일

## 📈 성능 최적화

- **@st.cache_data**: 1시간 데이터 캐싱
- **Plotly**: 경량 인터랙티브 차트
- **Lazy Loading**: 탭별 지연 로딩

## 🔒 보안 고려사항

- Google Sheets는 공개 또는 링크로 공유 설정 필요
- 민감한 데이터는 환경변수로 관리 권장

## 🚀 배포

### Streamlit Cloud

1. GitHub 저장소에 코드 업로드
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. 저장소 연결 및 배포

### Docker (선택사항)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

## 📝 라이선스

MIT License

## 💡 향후 개선 사항

- [ ] 다국어 지원
- [ ] 모바일 반응형 개선
- [ ] 실시간 데이터 연동
- [ ] 사용자 인증 시스템
- [ ] 예측 정확도 평가 대시보드
- [ ] 알림 기능 (임계값 도달 시)

## 📞 문의

문제가 발생하거나 제안사항이 있으시면 Issue를 등록해주세요.

---

**Made with ❤️ using Streamlit & Prophet**
