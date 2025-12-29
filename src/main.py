"""
AutoMacro Python - 메인 진입점
"""

import sys
import os

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from models import ActionBlock, Settings
from utils import FileManager
from core import Automation, Player, Recorder
from vision import VisionEngine


def main():
    """애플리케이션 메인 함수"""
    print('='*50)
    print('🤖 AutoMacro Python v2.0')
    print('='*50)

    # 파일 매니저 초기화
    file_manager = FileManager()
    print(f'[Main] User directory: {file_manager.user_dir}')

    # 설정 로드
    settings = file_manager.load_settings()
    print(f'[Main] Settings loaded: theme={settings.theme}, language={settings.language}')

    # CustomTkinter 설정
    ctk.set_appearance_mode(settings.theme)
    ctk.set_default_color_theme(settings.color_theme)
    print('[Main] CustomTkinter configured')

    # 코어 컴포넌트 초기화
    automation = Automation()
    player = Player(automation)
    recorder = Recorder()
    vision_engine = VisionEngine()

    print('[Main] Core components initialized')

    # MainWindow 실행
    from ui.main_window import MainWindow

    print('[Main] Launching MainWindow...')
    app = MainWindow(file_manager, settings, automation, player, recorder, vision_engine)

    print('[Main] ✓ Application ready!')
    print('[Main] Press F9 to start recording, F12 to stop')
    app.mainloop()


if __name__ == '__main__':
    main()
