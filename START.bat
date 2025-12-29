@echo off
chcp 65001 >nul
echo ========================================
echo   AutoMacro Python 실행 스크립트
echo ========================================
echo.

REM Python 설치 확인
echo [1단계] Python 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
    echo.
    echo Python 설치 방법:
    echo 1. https://www.python.org/downloads/ 접속
    echo 2. "Download Python 3.12" 클릭
    echo 3. 설치 시 "Add Python to PATH" 체크!
    echo.
    pause
    exit /b 1
)

python --version
echo ✓ Python 설치 확인됨
echo.

REM 의존성 설치
echo [2단계] 필요한 라이브러리 설치 중...
echo (처음 실행 시 시간이 걸릴 수 있습니다)
echo.

REM pip 업그레이드
python -m pip install --upgrade pip --quiet

REM 핵심 라이브러리만 먼저 설치 (미리 빌드된 버전)
echo 핵심 라이브러리 설치 중...
python -m pip install pillow --only-binary :all: --upgrade
python -m pip install numpy --only-binary :all:
python -m pip install opencv-python --only-binary :all:

REM 나머지 설치
echo 추가 라이브러리 설치 중...
python -m pip install customtkinter pyautogui pynput pyperclip mss

if %errorlevel% neq 0 (
    echo.
    echo ❌ 라이브러리 설치 실패
    echo 인터넷 연결을 확인하고 다시 시도하세요.
    pause
    exit /b 1
)

echo.
echo ✓ 모든 라이브러리 설치 완료!
echo.

REM 프로그램 실행
echo [3단계] AutoMacro Python 실행 중...
echo.
echo ========================================
echo   프로그램 시작!
echo   F9: 녹화 시작/중지
echo   F12: 긴급 중지
echo ========================================
echo.

python src\main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 프로그램 실행 실패
    echo 에러 메시지를 확인하세요.
    pause
)
