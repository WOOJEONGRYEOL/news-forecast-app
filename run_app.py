"""
간편 실행 스크립트 (PATH 문제 우회)
"""
import sys
import subprocess

if __name__ == "__main__":
    # streamlit을 모듈로 실행 (PATH 문제 우회)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
