# 빌드 가이드

## 개발 환경 설정

### 1. Python 설치
- Python 3.9 이상 필요
- https://www.python.org/downloads/

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 개발 모드 실행
```bash
python src/main.py
```

## 프로덕션 빌드

### Windows

```bash
# PyInstaller로 빌드
pyinstaller build.spec

# 결과물: dist/AutoMacro/AutoMacro.exe
```

### macOS

```bash
# PyInstaller로 빌드
pyinstaller build.spec

# 결과물: dist/AutoMacro/AutoMacro.app
```

## 빌드 옵션

### 단일 파일 빌드 (onefile)
```bash
pyinstaller --onefile --windowed --name AutoMacro src/main.py
```

### 디버그 빌드 (콘솔 포함)
```bash
pyinstaller --console build.spec
```

## 문제 해결

### OpenCV 누락
```bash
pip install opencv-python --upgrade
```

### CustomTkinter 테마 누락
빌드 시 `customtkinter` 폴더를 수동으로 복사:
```bash
cp -r venv/Lib/site-packages/customtkinter dist/AutoMacro/
```

### 권한 문제 (Windows)
관리자 권한으로 실행 필요 (전역 후킹)

## 배포

1. `dist/AutoMacro` 폴더를 압축
2. README.md와 함께 배포
3. VirusTotal 검사 권장 (오탐 방지)

## 자동 빌드 (CI/CD)

GitHub Actions, GitLab CI 등에서 자동 빌드 설정 가능
`.github/workflows/build.yml` 참고
