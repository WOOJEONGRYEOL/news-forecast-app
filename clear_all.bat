@echo off
taskkill /F /IM python.exe 2>nul
taskkill /F /IM streamlit.exe 2>nul
if exist cache rmdir /s /q cache
if exist .streamlit\cache rmdir /s /q .streamlit\cache
if exist __pycache__ rmdir /s /q __pycache__
del /s /q *.pyc 2>nul
echo Cache cleared!
pause
