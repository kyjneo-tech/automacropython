"""
FileManager - 프로젝트 및 설정 파일 관리
JSON 저장/로드 담당
"""

import json
import os
from pathlib import Path
from typing import List, Optional

# 절대 경로 임포트로 변경
try:
    from models.action_block import ActionBlock
    from models.settings import Settings, Profile
except ImportError:
    from ..models.action_block import ActionBlock
    from ..models.settings import Settings, Profile


class FileManager:
    """파일 저장/로드 관리자"""

    def __init__(self):
        # 사용자 데이터 디렉토리
        self.user_dir = Path.home() / '.automacro'
        self.projects_dir = self.user_dir / 'projects'
        self.profiles_dir = self.user_dir / 'profiles'
        self.settings_file = self.user_dir / 'settings.json'

        # 디렉토리 생성
        self.user_dir.mkdir(exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)
        self.profiles_dir.mkdir(exist_ok=True)

    def save_project(self, blocks: List[ActionBlock], file_path: str) -> bool:
        """
        프로젝트 저장 (JSON)

        Args:
            blocks: ActionBlock 리스트
            file_path: 저장 경로 (상대 또는 절대)

        Returns:
            성공 여부
        """
        try:
            # 상대 경로 처리
            if not os.path.isabs(file_path):
                file_path = str(self.projects_dir / file_path)

            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # JSON 직렬화
            data = {
                'version': '2.0',
                'blocks': [block.to_dict() for block in blocks]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f'[FileManager] ✓ Project saved: {file_path}')
            return True

        except Exception as e:
            print(f'[FileManager] ✗ Save failed: {e}')
            return False

    def load_project(self, file_path: str) -> Optional[List[ActionBlock]]:
        """
        프로젝트 로드 (JSON)

        Args:
            file_path: 파일 경로 (상대 또는 절대)

        Returns:
            ActionBlock 리스트 (실패 시 None)
        """
        try:
            # 상대 경로 처리
            if not os.path.isabs(file_path):
                file_path = str(self.projects_dir / file_path)

            if not os.path.exists(file_path):
                print(f'[FileManager] ✗ File not found: {file_path}')
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 버전 확인 (선택 사항)
            version = data.get('version', '1.0')

            # ActionBlock 역직렬화
            blocks = [ActionBlock.from_dict(block_data) for block_data in data.get('blocks', [])]

            print(f'[FileManager] ✓ Project loaded: {file_path} ({len(blocks)} blocks)')
            return blocks

        except Exception as e:
            print(f'[FileManager] ✗ Load failed: {e}')
            return None

    def save_settings(self, settings: Settings) -> bool:
        """설정 저장"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, ensure_ascii=False, indent=2)

            print(f'[FileManager] ✓ Settings saved')
            return True

        except Exception as e:
            print(f'[FileManager] ✗ Settings save failed: {e}')
            return False

    def load_settings(self) -> Settings:
        """설정 로드 (파일 없으면 기본값)"""
        try:
            if not self.settings_file.exists():
                print('[FileManager] Using default settings')
                return Settings()

            with open(self.settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            settings = Settings.from_dict(data)
            print('[FileManager] ✓ Settings loaded')
            return settings

        except Exception as e:
            print(f'[FileManager] ✗ Settings load failed, using defaults: {e}')
            return Settings()

    def save_profile(self, profile: Profile) -> bool:
        """프로파일 저장"""
        try:
            file_path = self.profiles_dir / f'{profile.name}.json'

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)

            print(f'[FileManager] ✓ Profile saved: {profile.name}')
            return True

        except Exception as e:
            print(f'[FileManager] ✗ Profile save failed: {e}')
            return False

    def load_profile(self, name: str) -> Optional[Profile]:
        """프로파일 로드"""
        try:
            file_path = self.profiles_dir / f'{name}.json'

            if not file_path.exists():
                print(f'[FileManager] ✗ Profile not found: {name}')
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            profile = Profile.from_dict(data)
            print(f'[FileManager] ✓ Profile loaded: {name}')
            return profile

        except Exception as e:
            print(f'[FileManager] ✗ Profile load failed: {e}')
            return None

    def list_projects(self) -> List[str]:
        """프로젝트 목록 가져오기"""
        try:
            return [f.name for f in self.projects_dir.glob('*.json')]
        except Exception as e:
            print(f'[FileManager] ✗ List projects failed: {e}')
            return []

    def list_profiles(self) -> List[str]:
        """프로파일 목록 가져오기"""
        try:
            return [f.stem for f in self.profiles_dir.glob('*.json')]
        except Exception as e:
            print(f'[FileManager] ✗ List profiles failed: {e}')
            return []
