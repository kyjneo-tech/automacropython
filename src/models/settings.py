"""
Settings - 애플리케이션 설정 데이터 모델
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Settings:
    """애플리케이션 설정"""

    # 전역 설정
    auto_hide: bool = True  # 재생 시 창 자동 숨김
    language: str = 'ko'  # 'ko', 'en'

    # 단축키
    panic_key: str = 'F12'  # 긴급 중지
    record_start_key: str = 'F9'  # 녹화 시작
    record_stop_key: str = 'F10'  # 녹화 중지
    play_key: str = ''  # 재생 (기본값 없음)

    # 알림 설정
    sound_enabled: bool = True
    notification_enabled: bool = True
    webhook_url: str = ''
    email_smtp_host: str = ''
    email_smtp_port: int = 587
    email_from: str = ''
    email_to: str = ''
    email_password: str = ''

    # 고급 설정
    screenshot_cache_ttl: int = 100  # ms
    default_confidence: float = 0.75
    default_color_tolerance: int = 50

    # UI 설정
    theme: str = 'dark'  # 'light', 'dark'
    color_theme: str = 'blue'  # 'blue', 'green', 'dark-blue'

    # 프로파일 설정
    current_profile: str = 'default'

    def to_dict(self) -> dict:
        """JSON 직렬화"""
        return {
            'auto_hide': self.auto_hide,
            'language': self.language,
            'panic_key': self.panic_key,
            'record_start_key': self.record_start_key,
            'record_stop_key': self.record_stop_key,
            'play_key': self.play_key,
            'sound_enabled': self.sound_enabled,
            'notification_enabled': self.notification_enabled,
            'webhook_url': self.webhook_url,
            'email_smtp_host': self.email_smtp_host,
            'email_smtp_port': self.email_smtp_port,
            'email_from': self.email_from,
            'email_to': self.email_to,
            'email_password': self.email_password,
            'screenshot_cache_ttl': self.screenshot_cache_ttl,
            'default_confidence': self.default_confidence,
            'default_color_tolerance': self.default_color_tolerance,
            'theme': self.theme,
            'color_theme': self.color_theme,
            'current_profile': self.current_profile
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Settings':
        """JSON 역직렬화"""
        return cls(
            auto_hide=data.get('auto_hide', True),
            language=data.get('language', 'ko'),
            panic_key=data.get('panic_key', 'F12'),
            record_start_key=data.get('record_start_key', 'F9'),
            record_stop_key=data.get('record_stop_key', 'F10'),
            play_key=data.get('play_key', ''),
            sound_enabled=data.get('sound_enabled', True),
            notification_enabled=data.get('notification_enabled', True),
            webhook_url=data.get('webhook_url', ''),
            email_smtp_host=data.get('email_smtp_host', ''),
            email_smtp_port=data.get('email_smtp_port', 587),
            email_from=data.get('email_from', ''),
            email_to=data.get('email_to', ''),
            email_password=data.get('email_password', ''),
            screenshot_cache_ttl=data.get('screenshot_cache_ttl', 100),
            default_confidence=data.get('default_confidence', 0.75),
            default_color_tolerance=data.get('default_color_tolerance', 50),
            theme=data.get('theme', 'dark'),
            color_theme=data.get('color_theme', 'blue'),
            current_profile=data.get('current_profile', 'default')
        )


@dataclass
class Profile:
    """프로파일 설정 (Phase 8)"""

    name: str = 'default'
    settings: Settings = field(default_factory=Settings)
    hotkeys: Dict[str, str] = field(default_factory=dict)  # {combo: macro_path}
    variables: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'settings': self.settings.to_dict(),
            'hotkeys': self.hotkeys,
            'variables': self.variables
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Profile':
        return cls(
            name=data.get('name', 'default'),
            settings=Settings.from_dict(data.get('settings', {})),
            hotkeys=data.get('hotkeys', {}),
            variables=data.get('variables', {})
        )
