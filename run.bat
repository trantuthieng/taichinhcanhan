@echo off
chcp 65001 >nul
title Quản lý Tài chính Cá nhân
echo ========================================
echo   Quản lý Tài chính Cá nhân
echo ========================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [LỖI] Python chưa được cài đặt!
    echo Tải Python tại: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Kiểm tra venv
if not exist "venv" (
    echo [INFO] Tạo virtual environment...
    python -m venv venv
)

REM Kích hoạt venv
call venv\Scripts\activate.bat

REM Cài đặt gói
echo [INFO] Kiểm tra và cài đặt gói phụ thuộc...
pip install -r requirements.txt -q

REM Tạo file .env nếu chưa có
if not exist ".env" (
    echo [INFO] Tạo file .env từ mẫu...
    copy .env.example .env >nul
)

REM Chạy ứng dụng
echo.
echo [INFO] Khởi chạy ứng dụng...
echo [INFO] Mở trình duyệt tại: http://localhost:8501
echo.
streamlit run app.py --server.port 8501

pause
