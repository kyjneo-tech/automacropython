@echo off
chcp 65001 >nul
echo ========================================
echo   Pillow 설치 문제 해결 스크립트
echo ========================================
echo.

echo [방법 1] 미리 빌드된 Pillow 설치 시도...
python -m pip uninstall pillow -y
python -m pip install --upgrade pillow --only-binary :all:

if %errorlevel% equ 0 (
    echo ✓ Pillow 설치 성공!
    goto success
)

echo.
echo [방법 2] 캐시 삭제 후 재시도...
python -m pip cache purge
python -m pip install pillow --no-cache-dir

if %errorlevel% equ 0 (
    echo ✓ Pillow 설치 성공!
    goto success
)

echo.
echo [방법 3] 특정 버전으로 시도...
python -m pip install pillow==9.5.0

if %errorlevel% equ 0 (
    echo ✓ Pillow 설치 성공!
    goto success
)

echo.
echo ❌ 모든 방법 실패
echo.
echo 수동 해결 방법:
echo 1. Microsoft C++ Build Tools 설치
echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo.
echo 2. 또는 Python 재설치 (3.11 버전 권장)
echo    https://www.python.org/downloads/release/python-3119/
echo.
pause
exit /b 1

:success
echo.
echo ========================================
echo   이제 START.bat 를 실행하세요!
echo ========================================
pause
