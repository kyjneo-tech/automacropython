"""
VisionEngine - 이미지/색상 인식 엔진
OpenCV + mss 기반
"""

import cv2
import numpy as np
import mss
from typing import Optional, Tuple, List
from pathlib import Path


class VisionEngine:
    """비전 인식 엔진"""

    def __init__(self):
        self.sct = mss.mss()
        self.screenshot_cache = None
        self.cache_time = 0
        self.cache_ttl = 0.1  # 100ms

        print('[VisionEngine] Initialized')
        print(f'[VisionEngine] Monitors: {len(self.sct.monitors)} ({self.sct.monitors})')

    def get_screen_size(self) -> Tuple[int, int]:
        """전체 화면 크기 (모든 모니터 합산)"""
        monitor = self.sct.monitors[0]  # 전체 화면
        return monitor['width'], monitor['height']

    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        스크린샷 촬영

        Args:
            region: (left, top, width, height) 영역, None이면 전체 화면

        Returns:
            OpenCV 이미지 (BGR)
        """
        import time

        # 캐시 확인
        current_time = time.time()
        if self.screenshot_cache is not None and (current_time - self.cache_time) < self.cache_ttl:
            if region is None:
                return self.screenshot_cache.copy()

        # 스크린샷 촬영
        if region:
            left, top, width, height = region
            monitor = {
                'left': left,
                'top': top,
                'width': width,
                'height': height
            }
        else:
            monitor = self.sct.monitors[0]  # 전체 화면

        screenshot = self.sct.grab(monitor)

        # BGRA -> BGR 변환
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 전체 화면이면 캐시 저장
        if region is None:
            self.screenshot_cache = img.copy()
            self.cache_time = current_time

        return img

    def find_image(
        self,
        template_path: str,
        confidence: float = 0.75,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True,
        multiscale: bool = True
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        이미지 찾기 (템플릿 매칭)

        Args:
            template_path: 찾을 이미지 경로
            confidence: 신뢰도 (0.0 ~ 1.0)
            region: 검색 영역 (None이면 전체 화면)
            grayscale: 흑백 변환 여부 (속도 향상)
            multiscale: 다중 스케일 매칭 (Retina/HiDPI 대응)

        Returns:
            (left, top, width, height) or None
        """
        print(f'[VisionEngine] Finding image: {template_path} (confidence={confidence})')

        # 템플릿 로드
        template = cv2.imread(template_path)
        if template is None:
            print(f'[VisionEngine] ✗ Template not found: {template_path}')
            return None

        # 스크린샷 촬영
        screenshot = self.take_screenshot(region)

        # 그레이스케일 변환
        if grayscale:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # 다중 스케일 매칭
        if multiscale:
            scales = [0.9, 1.0, 1.1]  # Retina/HiDPI 대응
        else:
            scales = [1.0]

        best_match = None
        best_confidence = 0

        for scale in scales:
            # 템플릿 크기 조정
            if scale != 1.0:
                scaled_template = cv2.resize(
                    template,
                    None,
                    fx=scale,
                    fy=scale,
                    interpolation=cv2.INTER_AREA
                )
            else:
                scaled_template = template

            # 크기 검증
            if (scaled_template.shape[0] > screenshot.shape[0] or
                scaled_template.shape[1] > screenshot.shape[1]):
                continue

            # 템플릿 매칭
            result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_confidence:
                best_confidence = max_val
                h, w = scaled_template.shape[:2]
                x, y = max_loc

                # region 오프셋 보정
                if region:
                    x += region[0]
                    y += region[1]

                best_match = (x, y, w, h)

        # 신뢰도 확인
        if best_match and best_confidence >= confidence:
            print(f'[VisionEngine] ✓ Image found: {best_match} (confidence={best_confidence:.3f})')
            return best_match
        else:
            print(f'[VisionEngine] ✗ Image not found (best confidence={best_confidence:.3f})')
            return None

    def find_all_images(
        self,
        template_path: str,
        confidence: float = 0.75,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True
    ) -> List[Tuple[int, int, int, int]]:
        """
        모든 이미지 찾기

        Returns:
            [(left, top, width, height), ...]
        """
        print(f'[VisionEngine] Finding all images: {template_path}')

        # 템플릿 로드
        template = cv2.imread(template_path)
        if template is None:
            return []

        # 스크린샷 촬영
        screenshot = self.take_screenshot(region)

        # 그레이스케일 변환
        if grayscale:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # 템플릿 매칭
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        h, w = template.shape[:2]

        # 임계값 이상의 모든 위치
        locations = np.where(result >= confidence)
        matches = []

        for pt in zip(*locations[::-1]):
            x, y = pt

            # region 오프셋 보정
            if region:
                x += region[0]
                y += region[1]

            matches.append((x, y, w, h))

        print(f'[VisionEngine] ✓ Found {len(matches)} matches')
        return matches

    def wait_for_image(
        self,
        template_path: str,
        confidence: float = 0.75,
        timeout: float = 10.0,
        interval: float = 0.5,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        이미지가 나타날 때까지 대기

        Args:
            timeout: 최대 대기 시간 (초)
            interval: 확인 간격 (초)

        Returns:
            (left, top, width, height) or None (타임아웃)
        """
        import time

        print(f'[VisionEngine] Waiting for image: {template_path} (timeout={timeout}s)')

        start_time = time.time()

        while True:
            # 이미지 찾기
            match = self.find_image(template_path, confidence, region)

            if match:
                elapsed = time.time() - start_time
                print(f'[VisionEngine] ✓ Image appeared after {elapsed:.1f}s')
                return match

            # 타임아웃 확인
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                print(f'[VisionEngine] ✗ Timeout ({timeout}s)')
                return None

            # 대기
            time.sleep(interval)

    def find_color(
        self,
        target_color: Tuple[int, int, int],
        tolerance: int = 50,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Tuple[int, int]]:
        """
        색상 찾기 (HSV 기반)

        Args:
            target_color: (R, G, B) 색상
            tolerance: 색상 허용 오차
            region: 검색 영역

        Returns:
            (x, y) or None
        """
        print(f'[VisionEngine] Finding color: RGB{target_color} (tolerance={tolerance})')

        # 스크린샷 촬영
        screenshot = self.take_screenshot(region)

        # BGR -> HSV 변환
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

        # RGB -> BGR -> HSV
        r, g, b = target_color
        target_bgr = np.uint8([[[b, g, r]]])
        target_hsv = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2HSV)[0][0]

        # 색상 범위
        lower = np.array([
            max(0, target_hsv[0] - tolerance // 2),
            max(0, target_hsv[1] - tolerance),
            max(0, target_hsv[2] - tolerance)
        ])
        upper = np.array([
            min(179, target_hsv[0] + tolerance // 2),
            min(255, target_hsv[1] + tolerance),
            min(255, target_hsv[2] + tolerance)
        ])

        # 마스크 생성
        mask = cv2.inRange(hsv, lower, upper)

        # 매칭 픽셀 찾기
        locations = np.where(mask > 0)

        if len(locations[0]) > 0:
            # 첫 번째 매칭 위치
            y, x = locations[0][0], locations[1][0]

            # region 오프셋 보정
            if region:
                x += region[0]
                y += region[1]

            print(f'[VisionEngine] ✓ Color found at: ({x}, {y})')
            return (x, y)
        else:
            print(f'[VisionEngine] ✗ Color not found')
            return None

    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """
        특정 위치의 픽셀 색상 가져오기

        Returns:
            (R, G, B)
        """
        screenshot = self.take_screenshot(region=(x, y, 1, 1))
        b, g, r = screenshot[0, 0]
        return (int(r), int(g), int(b))

    def save_template(self, region: Tuple[int, int, int, int], output_path: str):
        """
        영역을 템플릿 이미지로 저장

        Args:
            region: (left, top, width, height)
            output_path: 저장 경로
        """
        screenshot = self.take_screenshot(region)

        # 디렉토리 생성
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 저장
        cv2.imwrite(output_path, screenshot)
        print(f'[VisionEngine] ✓ Template saved: {output_path}')
