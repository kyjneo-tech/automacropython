@echo off
chcp 65001 >nul
echo ========================================
echo   AutoMacro Python 간단 실행
echo ========================================
echo.

REM 최소 라이브러리만 설치 (더 빠름)
echo 필수 라이브러리 설치 중...
python -m pip install --upgrade pip
python -m pip install customtkinter pillow pyautogui pynput pyperclip opencv-python numpy mss

if %errorlevel% neq 0 (
    echo.
    echo ❌ 설치 실패. 아래 명령을 수동으로 실행해보세요:
    echo.
    echo python -m pip install customtkinter
    echo python -m pip install pillow
    echo python -m pip install pyautogui pynput pyperclip
    echo python -m pip install opencv-python numpy mss
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ 설치 완료!
echo.
echo 프로그램 실행 중...
python src\main.py

pause
