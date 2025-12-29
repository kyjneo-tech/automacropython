# 설치 및 실행 가이드

## 🚀 빠른 시작 (Windows)

### 방법 1: 자동 실행 스크립트 (권장)

1. `START.bat` 파일을 더블클릭
2. 자동으로 Python 확인 → 라이브러리 설치 → 프로그램 실행

### 방법 2: 수동 설치

#### 1단계: Python 설치 확인

**명령 프롬프트** 또는 **PowerShell**을 열고:

```bash
python --version
```

**Python이 없다면:**
1. https://www.python.org/downloads/ 접속
2. "Download Python 3.12" 클릭
3. 설치 시 **"Add Python to PATH"** 반드시 체크!
4. 설치 후 컴퓨터 재부팅

#### 2단계: 의존성 설치

프로젝트 폴더에서:

```bash
cd C:\Users\김영준\Desktop\dev\automacro-python
pip install -r requirements.txt
```

설치되는 라이브러리:
- `customtkinter` - UI
- `pyautogui` - 마우스/키보드 제어
- `pynput` - 전역 후킹
- `opencv-python` - 이미지 인식
- `mss` - 스크린샷
- `pyperclip` - 클립보드 (한글 입력)
- 기타...

#### 3단계: 실행

```bash
python src\main.py
```

## 🐧 Linux/macOS

```bash
# 의존성 설치
pip3 install -r requirements.txt

# 실행
python3 src/main.py
```

## ❓ 문제 해결

### "Python을 찾을 수 없습니다" 에러

**원인:** Python이 설치되지 않았거나 PATH에 없음

**해결:**
1. Python 재설치 (위 1단계 참고)
2. 설치 시 "Add Python to PATH" 체크
3. 컴퓨터 재부팅

### pip 설치 실패

**원인:** 관리자 권한 필요 또는 네트워크 문제

**해결:**
```bash
# 관리자 권한으로 실행
pip install -r requirements.txt --user

# 또는 특정 라이브러리만 설치
pip install customtkinter pyautogui pynput opencv-python mss pyperclip
```

### "권한이 거부되었습니다" 에러

**원인:** 전역 후킹에 관리자 권한 필요

**해결:**
- 명령 프롬프트를 **관리자 권한으로 실행**
- 또는 `START.bat`를 우클릭 → "관리자 권한으로 실행"

### OpenCV 오류

```bash
pip install opencv-python --upgrade
```

### 한글이 깨짐

- Windows: 콘솔 인코딩을 UTF-8로 설정
  ```bash
  chcp 65001
  ```

## 📦 가상환경 사용 (선택)

더 깔끔한 관리를 원한다면:

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate

# 활성화 (Linux/Mac)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 실행
python src/main.py
```

## ✅ 설치 확인

정상적으로 설치되었다면:

1. CustomTkinter UI가 나타남
2. 콘솔에 다음과 같은 메시지:
   ```
   ==================================================
   🤖 AutoMacro Python v2.0
   ==================================================
   [FileManager] User directory: ...
   [Main] Settings loaded: theme=dark, language=ko
   [Main] CustomTkinter configured
   [Automation] Initialized
   [Player] Initialized
   [Recorder] Initialized
   [VisionEngine] Initialized
   [Main] ✓ Application ready!
   ```

## 🎯 첫 실행 테스트

1. **좌측 사이드바**에서 "클릭" 버튼 클릭
2. **타임라인**에 클릭 액션 추가됨
3. **우측 상세 패널**에서 X, Y 좌표 입력
4. **▶️ 재생** 버튼 클릭
5. 설정한 좌표에 마우스 클릭 실행됨

성공하면 프로그램이 정상 작동하는 것입니다! 🎉

## 📞 도움이 필요하면

에러 메시지와 함께 GitHub Issues에 문의하세요.
