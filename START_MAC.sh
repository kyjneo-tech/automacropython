#!/bin/bash

echo "=================================================="
echo "🤖 AutoMacro Python - macOS Launcher"
echo "=================================================="

# 1. Python 3 체크
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3가 설치되어 있지 않습니다."
    echo "https://www.python.org/ 에서 Python 3를 설치해주세요."
    exit 1
fi

# 2. 가상환경(venv) 생성
if [ ! -d "venv" ]; then
    echo "📦 가상환경을 생성하는 중..."
    python3 -m venv venv
fi

# 3. 가상환경 활성화
source venv/bin/activate

# 4. 필수 라이브러리 설치
echo "⬇️ 의존성 라이브러리 확인 및 설치 중..."
# requirements.txt의 일부 패키지가 맥에서 문제가 될 수 있어 핵심 패키지를 직접 설치합니다.
pip install customtkinter pillow pyautogui pynput pyperclip opencv-python numpy mss pytesseract

# 5. 실행
echo "🚀 AutoMacro Python 실행 중..."
python src/main.py
