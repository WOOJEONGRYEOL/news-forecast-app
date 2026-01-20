# ============================================================
# Prophet 예측 엔진 (Refactored for Web App)
# ============================================================

import os
import re
import io
import warnings
import shutil
import site
import pathlib
from datetime import datetime, timedelta
import numpy as np

# NumPy 2.x 호환 패치 (Prophet import 전에 실행 필수!)
if not hasattr(np, "float_"):
    np.float_ = np.float64
if not hasattr(np, "int_"):
    np.int_ = np.int64
if not hasattr(np, "bool_"):
    np.bool_ = np.bool_

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from prophet import Prophet
from korean_lunar_calendar import KoreanLunarCalendar
import requests
import ephem

warnings.filterwarnings("ignore")
try:
    plt.rcParams["font.family"] = "DejaVu Sans"
except:
    pass  # 폰트 설정 실패 시 무시
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.max_open_warning"] = 0


class NewsViewershipForecaster:
    """뉴스 시청률 예측 클래스"""

    def __init__(self, sheets_id, gid="0"):
        self.sheets_id = sheets_id
        self.gid = gid
        self.sheets_csv_url = f"https://docs.google.com/spreadsheets/d/{sheets_id}/export?format=csv&gid={gid}"

        self.channels = {
            "뉴스A": "News_A",
            "JTBC뉴스룸": "JTBC",
            "MBN뉴스7": "MBN",
            "TV조선뉴스9": "TVCHOSUN"
        }
        self.colors = {
            "News_A": "#0072BD",
            "JTBC": "#7E2F8E",
            "MBN": "#EDB120",
            "TVCHOSUN": "#D95319"
        }
        self.order = ["News_A", "JTBC", "MBN", "TVCHOSUN"]

        self.df = None
        self.holidays = None
        self.forecasts = {}
        self.models = {}
        self.predict_days = 180

    def get_seoul_sunset_float(self, date_val):
        """서울 일몰 시각을 float로 반환 (예: 18.5)"""
        obs = ephem.Observer()
        obs.lat = '37.5665'
        obs.lon = '126.9780'

        target_dt = pd.to_datetime(date_val)
        noon_kst = target_dt.replace(hour=12, minute=0, second=0)
        noon_utc = noon_kst - pd.Timedelta(hours=9)

        obs.date = noon_utc
        try:
            sunset_utc = obs.next_setting(ephem.Sun()).datetime()
            sunset_kst = sunset_utc + pd.Timedelta(hours=9)
            return sunset_kst.hour + sunset_kst.minute / 60.0
        except:
            return 18.5

    def load_data(self):
        """Google Sheets에서 데이터 로드"""
        resp = requests.get(self.sheets_csv_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        resp.raise_for_status()
        raw = resp.content.decode("utf-8-sig", errors="replace")

        df = pd.read_csv(io.StringIO(raw))
        clean = lambda s: str(s).replace("\ufeff", "").replace("\u200b", "").strip()
        df.columns = [clean(c) for c in df.columns]

        if "날짜" not in df.columns:
            raise ValueError("'날짜' 컬럼이 없습니다.")

        # 날짜 파싱
        def parse_date(v):
            s = re.sub(r"[^0-9]", "", str(v))
            if len(s) == 6:
                return pd.to_datetime("20" + s, format="%Y%m%d", errors="coerce")
            if len(s) == 8:
                return pd.to_datetime(s, format="%Y%m%d", errors="coerce")
            return pd.to_datetime(v, errors="coerce")

        df["날짜"] = df["날짜"].apply(parse_date)

        # 숫자 변환
        _num = re.compile(r"^-?\d+(?:\.\d+)?$")
        def to_float_safe(x):
            if pd.isna(x): return np.nan
            s = str(x).strip().replace(",", "")
            if s in {"", "-", "—", "–"}: return np.nan
            return float(s) if _num.match(s) else np.nan

        req = list(self.channels.keys())
        miss = [c for c in req if c not in df.columns]
        if miss:
            raise ValueError(f"채널 컬럼 누락: {miss}")

        for c in req:
            df[c] = df[c].apply(to_float_safe)

        df = (df.dropna(subset=["날짜"])
              .sort_values("날짜")
              .drop_duplicates("날짜")
              .reset_index(drop=True))

        # 일몰 시각 추가
        df["sunset_time"] = df["날짜"].apply(self.get_seoul_sunset_float)

        self.df = df
        return df

    def setup_holidays(self):
        """공휴일 설정"""
        solar = []
        for y in range(2023, 2027):
            solar += [
                {"holiday": "new_year", "ds": f"{y}-01-01", "lower_window": 0, "upper_window": 0},
                {"holiday": "childrens_day", "ds": f"{y}-05-05", "lower_window": 0, "upper_window": 1},
                {"holiday": "memorial_day", "ds": f"{y}-06-06", "lower_window": 0, "upper_window": 0},
                {"holiday": "liberation_day", "ds": f"{y}-08-15", "lower_window": 0, "upper_window": 0},
                {"holiday": "national_day", "ds": f"{y}-10-03", "lower_window": 0, "upper_window": 0},
                {"holiday": "hangeul_day", "ds": f"{y}-10-09", "lower_window": 0, "upper_window": 0},
                {"holiday": "christmas", "ds": f"{y}-12-25", "lower_window": 0, "upper_window": 1},
            ]

        lunar = []
        try:
            cal = KoreanLunarCalendar()
            for y in range(2023, 2027):
                cal.setLunarDate(y, 1, 1, False)
                Y, M, D = cal.SolarIsoFormat().split("-")
                lunar.append({"holiday": "lunar_new_year", "ds": f"{Y}-{M}-{D}", "lower_window": -1, "upper_window": 1})

                cal.setLunarDate(y, 4, 8, False)
                Y, M, D = cal.SolarIsoFormat().split("-")
                lunar.append({"holiday": "buddha_birthday", "ds": f"{Y}-{M}-{D}", "lower_window": 0, "upper_window": 0})

                cal.setLunarDate(y, 8, 15, False)
                Y, M, D = cal.SolarIsoFormat().split("-")
                lunar.append({"holiday": "chuseok", "ds": f"{Y}-{M}-{D}", "lower_window": -1, "upper_window": 1})
        except Exception as e:
            print(f"음력 공휴일 로드 실패: {e}")

        self.holidays = pd.DataFrame(solar + lunar)
        return self.holidays

    def run_forecast(self, predict_days=180):
        """Prophet 예측 실행"""
        self.predict_days = predict_days

        latest_data_dt = pd.to_datetime(self.df["날짜"].max()).normalize()
        target_dt = latest_data_dt + pd.Timedelta(days=1)

        for kr, en in self.channels.items():
            d = pd.DataFrame({
                "ds": self.df["날짜"],
                "y": self.df[kr],
                "sunset_time": self.df["sunset_time"]
            }).dropna(subset=["ds", "y", "sunset_time"])

            m = Prophet(
                weekly_seasonality=False,
                yearly_seasonality=False,
                holidays=self.holidays,
                seasonality_mode="additive",
                seasonality_prior_scale=5.0,
                holidays_prior_scale=5.0,
                changepoint_prior_scale=0.1,
                interval_width=0.95
            )
            m.add_seasonality(name="weekly", period=7, fourier_order=6)
            m.add_seasonality(name="yearly", period=365.25, fourier_order=10)
            m.add_regressor("sunset_time")

            m.fit(d)

            fut = m.make_future_dataframe(periods=predict_days)
            fut["sunset_time"] = fut["ds"].apply(self.get_seoul_sunset_float)

            # 95% CI
            fc_95 = m.predict(fut)

            # 90% CI
            m.interval_width = 0.90
            fc_90 = m.predict(fut)

            fc = fc_95.copy()
            fc['yhat_lower_90'] = fc_90['yhat_lower']
            fc['yhat_upper_90'] = fc_90['yhat_upper']
            fc["ds"] = pd.to_datetime(fc["ds"]).dt.normalize()

            # 시청률은 0 이상이어야 하므로 음수 제거
            fc['yhat'] = fc['yhat'].clip(lower=0)
            fc['yhat_lower'] = fc['yhat_lower'].clip(lower=0)
            fc['yhat_upper'] = fc['yhat_upper'].clip(lower=0)
            fc['yhat_lower_90'] = fc['yhat_lower_90'].clip(lower=0)
            fc['yhat_upper_90'] = fc['yhat_upper_90'].clip(lower=0)

            self.forecasts[en] = fc
            self.models[en] = m

        return self.forecasts, target_dt

    def get_today_predictions(self, target_dt):
        """오늘 예측값 반환"""
        predictions = {}
        for ch in self.order:
            fc = self.forecasts[ch]
            row = fc[fc["ds"] == target_dt]
            if len(row):
                predictions[ch] = {
                    "forecast": float(row["yhat"].iloc[0]),
                    "lower_95": float(row["yhat_lower"].iloc[0]),
                    "upper_95": float(row["yhat_upper"].iloc[0]),
                    "lower_90": float(row["yhat_lower_90"].iloc[0]),
                    "upper_90": float(row["yhat_upper_90"].iloc[0]),
                    "sunset_time": float(row["sunset_time"].iloc[0])
                }
            else:
                predictions[ch] = {
                    "forecast": float(fc["yhat"].iloc[-1]),
                    "lower_95": float(fc["yhat_lower"].iloc[-1]),
                    "upper_95": float(fc["yhat_upper"].iloc[-1]),
                    "lower_90": float(fc["yhat_lower_90"].iloc[-1]),
                    "upper_90": float(fc["yhat_upper_90"].iloc[-1]),
                    "sunset_time": float(fc["sunset_time"].iloc[-1])
                }
        return predictions

    def get_forecast_dataframe(self, target_dt):
        """전체 예측 데이터프레임 반환"""
        rows = []
        for ch in self.order:
            fc = self.forecasts[ch]
            fut_period = fc[fc["ds"] >= target_dt].head(self.predict_days + 1)
            for _, r in fut_period.iterrows():
                rows.append({
                    "Channel": ch,
                    "Date": pd.to_datetime(r["ds"]).strftime("%Y-%m-%d"),
                    "Forecast": round(float(r["yhat"]), 3),
                    "Lower_95": round(float(r["yhat_lower"]), 3),
                    "Upper_95": round(float(r["yhat_upper"]), 3),
                    "Lower_90": round(float(r["yhat_lower_90"]), 3),
                    "Upper_90": round(float(r["yhat_upper_90"]), 3),
                    "Sunset_Time": round(float(r["sunset_time"]), 2)
                })
        return pd.DataFrame(rows)
