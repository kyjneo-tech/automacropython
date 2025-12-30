import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from src.infra.screen import MacScreenManager

class InputDriver:
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        # Cache screen info for coordinate conversion if needed
        # In a real app, we might check this dynamicall
        
    def click(self, x: int = 0, y: int = 0, double=False, button="left"):
        """
        Move and Click. If x,y are 0, click at current position.
        """
        if x != 0 or y != 0:
            self.mouse.position = (x, y)
            time.sleep(0.05)
        
        btn = Button.left if button == "left" else Button.right
        if button == "middle": btn = Button.middle
        
        self.mouse.click(btn, 2 if double else 1)
        print(f"[Driver] Clicked {button}")

    def move(self, x: int, y: int):
        self.mouse.position = (x, y)
        print(f"[Driver] Moved to ({x}, {y})")

    def scroll(self, dx: int, dy: int, x: int = 0, y: int = 0):
        import sys
        # Move to position if provided
        if x != 0 or y != 0:
            self.mouse.position = (x, y)
            time.sleep(0.1)

        # Platform-specific sensitivity multiplier
        # macOS pynput scroll units are often weak, while Windows units represent "notches"
        multiplier = 10 if sys.platform == "darwin" else 1
        
        # Execute vertical scroll in chunks
        if dy != 0:
            total_dy = int(dy * multiplier)
            abs_dy = abs(total_dy)
            # Use smaller steps for Mac, direct for Windows if small
            step_y = (5 if sys.platform == "darwin" else 1) * (1 if total_dy > 0 else -1)
            
            steps = abs_dy // abs(step_y)
            for _ in range(steps):
                self.mouse.scroll(0, step_y)
                time.sleep(0.005)
            # Remaining steps
            rem = abs_dy % abs(step_y)
            if rem != 0:
                self.mouse.scroll(0, rem if total_dy > 0 else -rem)

        # Execute horizontal scroll in chunks
        if dx != 0:
            total_dx = int(dx * multiplier)
            abs_dx = abs(total_dx)
            step_x = 5 if total_dx > 0 else -5
            for _ in range(abs_dx // 5):
                self.mouse.scroll(step_x, 0)
                time.sleep(0.005)
            if abs_dx % 5 != 0:
                self.mouse.scroll(total_dx % 5 if total_dx > 0 else -(abs_dx % 5), 0)
            
        print(f"[Driver] Scrolled DX={dx}, DY={dy} (Scaled x{multiplier})")

    def drag(self, start: tuple, end: tuple):
        self.mouse.position = start
        time.sleep(0.1)
        self.mouse.press(Button.left)
        time.sleep(0.1)
        self.mouse.position = end
        time.sleep(0.1)
        self.mouse.release(Button.left)
        print(f"[Driver] Dragged {start} -> {end}")

    def type_text(self, text: str, interval: float = 0.05):
        for char in text:
            self.keyboard.type(char)
            time.sleep(interval)
        print(f"[Driver] Typed: {text}")
        
    def press_key(self, keys: str):
        # Handle combinations like "cmd+c"
        import pynput.keyboard as kb
        
        parts = [p.strip().lower() for p in keys.split('+')]
        
        # Map string names to Key objects
        key_map = {
            "cmd": kb.Key.cmd,
            "win": kb.Key.cmd, # pynput uses Key.cmd for Windows key too
            "ctrl": kb.Key.ctrl,
            "shift": kb.Key.shift,
            "alt": kb.Key.alt,
            "enter": kb.Key.enter,
            "space": kb.Key.space,
            "backspace": kb.Key.backspace,
            "tab": kb.Key.tab,
            "esc": kb.Key.esc
        }
        
        # Convert strings to pynput Key objects or raw characters
        real_keys = []
        for p in parts:
            if p in key_map:
                real_keys.append(key_map[p])
            else:
                real_keys.append(p)
        
        if not real_keys:
            return

        # Execute combination using recursion to handle multiple modifiers
        def _press_recursive(idx):
            if idx == len(real_keys) - 1:
                # Last key: press and release
                k = real_keys[idx]
                self.keyboard.press(k)
                time.sleep(0.05)
                self.keyboard.release(k)
            else:
                # Modifier: hold while pressing the rest
                with self.keyboard.pressed(real_keys[idx]):
                    time.sleep(0.05)
                    _press_recursive(idx + 1)
        
        try:
            _press_recursive(0)
            print(f"[Driver] Executed Hotkey: {keys}")
        except Exception as e:
            print(f"[Driver] Hotkey Failed ({keys}): {e}")

    def read_text_at(self, x: int, y: int, w: int, h: int) -> str:
        """Read text from a specific screen region (Cross-platform)."""
        import sys
        
        if sys.platform == "darwin":
            try:
                from PySide6.QtWidgets import QApplication
                import Quartz
                import Vision
                screen = QApplication.primaryScreen()
                ratio = screen.devicePixelRatio()
                rect = Quartz.CGRectMake(x * ratio, y * ratio, w * ratio, h * ratio)
                image_ref = Quartz.CGWindowListCreateImage(
                    rect, Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID, Quartz.kCGWindowImageDefault
                )
                if not image_ref: return ""
                text_results = []
                def completion_handler(request, error):
                    if not error:
                        for obs in request.results():
                            if obs.topCandidates_(1): text_results.append(obs.topCandidates_(1)[0].string())
                request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(completion_handler)
                request.setRecognitionLevel_(Vision.VNRequestRecognitionLevelAccurate)
                request.setRecognitionLanguages_(["ko-KR", "en-US"])
                handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(image_ref, None)
                handler.performRequests_error_([request], None)
                return " ".join(text_results)
            except: return ""

        elif sys.platform == "win32":
            try:
                import pytesseract
                from PIL import ImageGrab
                # On Windows, we need to handle DPI Scaling
                # ImageGrab.grab takes screen coordinates. 
                # Some setups need scaling adjustment.
                bbox = (x, y, x + w, y + h)
                screenshot = ImageGrab.grab(bbox=bbox)
                # Ensure tesseract is installed or path is set
                # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                text = pytesseract.image_to_string(screenshot, lang='kor+eng')
                return text.strip()
            except Exception as e:
                print(f"[Driver] Windows OCR Error: {e}. Ensure 'pytesseract' and Tesseract-OCR are installed.")
                return ""
        
        return ""

    def wait(self, seconds: float):
        print(f"[Driver] Waiting {seconds}s...")
        time.sleep(seconds)

    def find_image(self, image_path: str, confidence: float = 0.9):
        import cv2
        import numpy as np
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QImage
        import os

        if not os.path.exists(image_path):
            print(f"[Driver] Image not found: {image_path}")
            return None

        # Load Template
        template = cv2.imread(image_path)
        if template is None:
             print("[Driver] Failed to load template image.")
             return None
             
        t_h, t_w = template.shape[:2]
        
        # Search all screens
        screens = QApplication.screens()
        
        # Global best match
        best_val = -1
        best_loc = None
        best_screen_origin = (0, 0)
        scale_factor = 1.0
        
        # Helper for matching
        def try_match(img, tmpl, method=cv2.TM_CCOEFF_NORMED):
            res = cv2.matchTemplate(img, tmpl, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            return max_val, max_loc

        for screen in screens:
            # ... (Screen Grab logic same as before, assuming already in loop)
            # Grab from the specific target screen
            pixmap = screen.grabWindow(0) 
            
            # DEBUG SAVE
            debug_path = f"debug_screen_{screens.index(screen)}.png"
            pixmap.save(debug_path)
            
            # Conversion
            qimage = pixmap.toImage().convertToFormat(QImage.Format_RGB888)
            width, height = qimage.width(), qimage.height()
            ptr = qimage.bits()
            arr = np.array(ptr).reshape(height, width, 3)
            screen_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            
            # Skip if template too big
            if t_h > height or t_w > width:
                continue

            # 1. Color Match
            max_val, max_loc = try_match(screen_bgr, template)
            print(f"[Driver] Screen {screens.index(screen)} Color Match: {max_val:.4f}")
            
            # 2. Grayscale Fallback (if Color failed to meet strict confidence but might be close)
            # Actually, sometimes Color is 0.85, Gray is 0.95 (lighting diffs).
            # Let's try both and take best? 
            # Or only try Gray if Color < Confidence.
            
            if max_val < confidence:
                screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                g_val, g_loc = try_match(screen_gray, template_gray)
                print(f"[Driver] Screen {screens.index(screen)} Gray Match: {g_val:.4f}")
                
                if g_val > max_val:
                    max_val = g_val
                    max_loc = g_loc
            
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_screen_origin = screen.geometry().topLeft()
                scale_factor = screen.devicePixelRatio()
        
        print(f"[Driver] Final Best Match: {best_val} (Required: {confidence})")
        
        if best_val >= confidence:
            # Calculate Center
            center_x = best_loc[0] + t_w // 2
            center_y = best_loc[1] + t_h // 2
            
            # Convert Physical (from grabWindow) to Logical (for pynput)
            # This assumes grabWindow returns physical pixels (Retina).
            # And pynput takes logical.
            
            logical_x = (center_x / scale_factor) + best_screen_origin.x()
            logical_y = (center_y / scale_factor) + best_screen_origin.y()
            
            print(f"[Driver] Found at Physical({center_x}, {center_y}) -> Logical({logical_x}, {logical_y})")
            return (int(logical_x), int(logical_y))
            
        return None
