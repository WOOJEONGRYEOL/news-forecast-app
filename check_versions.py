"""버전 확인 스크립트"""
import sys

print("=" * 60)
print("환경 확인")
print("=" * 60)

print(f"Python: {sys.version}")
print()

try:
    import numpy as np
    print(f"✅ NumPy: {np.__version__}")
except Exception as e:
    print(f"❌ NumPy: {e}")

try:
    import pandas as pd
    print(f"✅ Pandas: {pd.__version__}")
except Exception as e:
    print(f"❌ Pandas: {e}")

try:
    import prophet
    print(f"✅ Prophet: {prophet.__version__}")
except Exception as e:
    print(f"❌ Prophet: {e}")

try:
    import cmdstanpy
    print(f"✅ CmdStanPy: {cmdstanpy.__version__}")
except Exception as e:
    print(f"❌ CmdStanPy: {e}")

try:
    import streamlit as st
    print(f"✅ Streamlit: {st.__version__}")
except Exception as e:
    print(f"❌ Streamlit: {e}")

print()
print("=" * 60)
print("Prophet 테스트")
print("=" * 60)

try:
    # NumPy 패치
    import numpy as np
    if not hasattr(np, "float_"):
        np.float_ = np.float64
    if not hasattr(np, "int_"):
        np.int_ = np.int64
    if not hasattr(np, "bool_"):
        np.bool_ = np.bool_

    from prophet import Prophet
    print("✅ Prophet import 성공!")

    # 간단한 테스트
    import pandas as pd
    df = pd.DataFrame({
        'ds': pd.date_range('2020-01-01', periods=100),
        'y': range(100)
    })

    m = Prophet()
    m.fit(df)
    print("✅ Prophet 모델 학습 성공!")

except Exception as e:
    print(f"❌ Prophet 오류: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
