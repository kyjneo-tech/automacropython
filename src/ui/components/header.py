"""
Header - 상단 헤더 (녹화/재생/중지 버튼)
"""

import customtkinter as ctk
from typing import Callable


class Header(ctk.CTkFrame):
    """상단 헤더"""

    def __init__(self, parent, on_record: Callable, on_play: Callable, on_stop: Callable, on_settings: Callable):
        super().__init__(parent, fg_color='transparent')

        self.on_record = on_record
        self.on_play = on_play
        self.on_stop = on_stop
        self.on_settings = on_settings

        self.is_recording = False
        self.is_playing = False

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 로고
        logo_label = ctk.CTkLabel(
            self,
            text='🤖 AutoMacro',
            font=('맑은 고딕', 20, 'bold')
        )
        logo_label.pack(side='left', padx=20)

        # 버튼 프레임
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(side='left', padx=20)

        # 녹화 버튼
        self.record_btn = ctk.CTkButton(
            btn_frame,
            text='⏺️ 녹화 (F9)',
            command=self._toggle_record,
            width=120,
            font=('맑은 고딕', 14)
        )
        self.record_btn.pack(side='left', padx=5)

        # 재생 버튼
        self.play_btn = ctk.CTkButton(
            btn_frame,
            text='▶️ 재생',
            command=self._toggle_play,
            width=120,
            font=('맑은 고딕', 14),
            fg_color='#2FA572'
        )
        self.play_btn.pack(side='left', padx=5)

        # 중지 버튼
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text='⏹️ 중지 (F12)',
            command=self._on_stop_clicked,
            width=120,
            font=('맑은 고딕', 14),
            fg_color='#C94C4C'
        )
        self.stop_btn.pack(side='left', padx=5)

        # 설정 버튼 (우측)
        self.settings_btn = ctk.CTkButton(
            self,
            text='⚙️ 설정',
            command=self.on_settings,
            width=100,
            font=('맑은 고딕', 14)
        )
        self.settings_btn.pack(side='right', padx=20)

    def _toggle_record(self):
        """녹화 토글"""
        if self.is_recording:
            self.set_recording(False)
        else:
            self.on_record()

    def _toggle_play(self):
        """재생 토글"""
        if self.is_playing:
            self.set_playing(False)
        else:
            self.on_play()

    def _on_stop_clicked(self):
        """중지 버튼 클릭"""
        self.on_stop()

    def set_recording(self, recording: bool):
        """녹화 상태 설정"""
        self.is_recording = recording

        if recording:
            self.record_btn.configure(text='⏺️ 녹화 중...', fg_color='#C94C4C')
            self.play_btn.configure(state='disabled')
        else:
            self.record_btn.configure(text='⏺️ 녹화 (F9)', fg_color=['#3B8ED0', '#1F6AA5'])
            self.play_btn.configure(state='normal')

    def set_playing(self, playing: bool):
        """재생 상태 설정"""
        self.is_playing = playing

        if playing:
            self.play_btn.configure(text='▶️ 재생 중...', fg_color='#2FA572')
            self.record_btn.configure(state='disabled')
        else:
            self.play_btn.configure(text='▶️ 재생', fg_color='#2FA572')
            self.record_btn.configure(state='normal')
