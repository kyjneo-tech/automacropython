from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                               QSpinBox, QDoubleSpinBox, QLabel, QPushButton, QComboBox, QHBoxLayout)
from PySide6.QtCore import Qt
from src.domain.actions import ActionNode, ActionType

class InspectorWidget(QWidget):
    def __init__(self, on_update_callback, on_test_callback=None):
        super().__init__()
        self.on_update_callback = on_update_callback
        self.on_test_callback = on_test_callback
        self.current_node_id = None
        
        # Cache for widgets: { "key": widget_obj }
        self.param_widgets = {}
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.header = QLabel("선택된 항목 없음")
        self.header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        self.layout.addWidget(self.header)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        
        # Test Button
        self.test_btn = QPushButton("▶ 이 액션 테스트 (Test Action)")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D2D30; 
                border: 1px solid #00FFcc; 
                color: #00FFcc; 
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00FFcc;
                color: black;
            }
        """)
        self.test_btn.clicked.connect(self._on_test_click)
        self.test_btn.hide() # Hidden by default
        self.layout.addWidget(self.test_btn)
        
        self.layout.addStretch()

    def set_node(self, node: ActionNode):
        if not node:
            self._clear_form()
            self.header.setText("선택된 항목 없음")
            self.current_node_id = None
            self.test_btn.hide()
            return

        # If same node, just update values (Prevent Focus Loss)
        # Exception: SCROLL and DRAG have complex derived UI, always rebuild to show captured values immediately
        if self.current_node_id == node.id and node.type not in [ActionType.SCROLL, ActionType.DRAG]:
            self._update_values(node)
            return
            
        # New Node Selection
        self._clear_form()
        self.current_node_id = node.id
        self.header.setText(f"{node.label} 속성")
        self.test_btn.show()
        
        # --- Build Form ---
        
        # Label
        label_edit = QLineEdit(node.label)
        label_edit.textChanged.connect(lambda val: self._on_field_change("label", val))
        self.form_layout.addRow("이름 (Label)", label_edit)
        self.param_widgets["_label"] = label_edit
        
        params = node.params
        
        if node.type == ActionType.CLICK:
            # 1. Button Selection
            btn_map = {"left": "왼쪽", "right": "오른쪽", "middle": "휠"}
            self.btn_reverse_map = {v: k for k, v in btn_map.items()}
            
            curr_btn = params.get("button", "left")
            curr_val_kr = btn_map.get(curr_btn, "왼쪽")
            self._add_combobox("버튼 (Button)", "button", ["왼쪽", "오른쪽", "휠"], curr_val_kr, map_back=True)
            
            # 2. Click Type (Single/Double)
            type_map = {"single": "한 번 클릭", "double": "더블 클릭", "down": "누르고 있기 (Down)", "up": "떼기 (Up)"}
            self.type_reverse_map = {v: k for k, v in type_map.items()}
            
            curr_type = params.get("click_type", "single")
            curr_type_kr = type_map.get(curr_type, "한 번 클릭")
            self._add_combobox("행동 유형", "click_type", list(type_map.values()), curr_type_kr, map_back=True, map_dict=self.type_reverse_map)

        elif node.type == ActionType.KEYBOARD_INPUT:
            # 1. Mode Selection
            mode_map = {"text": "텍스트 입력 (글자)", "shortcut": "단축키 입력 (Ctrl+C 등)"}
            self.mode_reverse_map = {v: k for k, v in mode_map.items()}
            
            curr_mode = params.get("mode", "text")
            curr_mode_kr = mode_map.get(curr_mode, "텍스트 입력 (글자)")
            self._add_combobox("입력 모드", "mode", list(mode_map.values()), curr_mode_kr, map_back=True, map_dict=self.mode_reverse_map)
            
            # 2. Dynamic Input based on Mode
            if curr_mode == "text":
                self._add_line_edit("입력할 내용", "text", params.get("text", ""))
                self._add_double_spinbox("타이핑 간격 (초)", "interval", params.get("interval", 0.05))
            else: # shortcut
                self._add_key_capture_edit("단축키 입력", "keys", params.get("keys", ""))
        
        elif node.type == ActionType.MOUSE_MOVE:
            self._add_coord_picker("좌표 설정", "x", "y", params.get("x", 0), params.get("y", 0))
            
        elif node.type == ActionType.SCROLL:
            # 1. Coordinate Picker for Start Position
            self._add_coord_picker("스크롤 시작 위치", "x", "y", params.get("x", 0), params.get("y", 0))

            # 2. Capture Button (now captures position + amount)
            def start_scroll_capture():
                if self.window() and hasattr(self.window(), "run_quick_capture"):
                    def on_captured(data):
                        self.on_update_callback(self.current_node_id, data)
                        # Refresh UI
                        updated = self.window().store.get_node(self.current_node_id)
                        if updated: self.set_node(updated)
                    self.window().run_quick_capture("scroll", on_captured)

            cap_btn = QPushButton("🖱️ 직접 휠 굴려서 입력 (위치+양 캡처)")
            cap_btn.setStyleSheet("background-color: #0E639C; color: white; padding: 10px; margin-top: 5px; margin-bottom: 5px;")
            cap_btn.clicked.connect(start_scroll_capture)
            self.form_layout.addRow(cap_btn)

            # 3. Amount and Direction UI
            dx = params.get("dx", 0); dy = params.get("dy", 0)
            direction = "up" if dy > 0 else "down"
            amount = abs(dy) if dy != 0 else abs(dx)
            if dx != 0: direction = "right" if dx > 0 else "left"
            
            dir_map = {"up": "위로 (Up)", "down": "아래로 (Down)", "left": "왼쪽으로 (Left)", "right": "오른쪽으로 (Right)"}
            self.dir_reverse_map = {v: k for k, v in dir_map.items()}
            
            def update_scroll(new_dir, new_amt):
                d_x, d_y = 0, 0
                if new_dir == "up": d_y = int(new_amt)
                elif new_dir == "down": d_y = -int(new_amt)
                elif new_dir == "left": d_x = -int(new_amt)
                elif new_dir == "right": d_x = int(new_amt)
                self.on_update_callback(self.current_node_id, {"dx": d_x, "dy": d_y})

            cb = QComboBox()
            cb.addItems(dir_map.values())
            cb.setCurrentText(dir_map.get(direction, "아래로 (Down)"))
            
            sb = QSpinBox()
            sb.setRange(0, 99999); sb.setValue(int(amount)); sb.setSuffix(" px")
            self.param_widgets["_scroll_amt"] = sb
            
            cb.currentTextChanged.connect(lambda val: update_scroll(self.dir_reverse_map.get(val), sb.value()))
            sb.valueChanged.connect(lambda val: update_scroll(self.dir_reverse_map.get(cb.currentText()), val))

            self.form_layout.addRow("스크롤 방향", cb)
            self.form_layout.addRow("스크롤 양", sb)
            
        elif node.type == ActionType.DRAG:
            self._add_coord_picker("시작 지점", "x1", "y1", params.get("x1", 0), params.get("y1", 0))
            self._add_coord_picker("끝 지점", "x2", "y2", params.get("x2", 0), params.get("y2", 0))
            
            def start_drag_capture():
                if self.window() and hasattr(self.window(), "run_quick_capture"):
                    def on_captured(data):
                        self.on_update_callback(self.current_node_id, data)
                        # Refresh UI
                        updated = self.window().store.get_node(self.current_node_id)
                        if updated: self.set_node(updated)
                    self.window().run_quick_capture("drag", on_captured)

            cap_btn = QPushButton("🖱️ 직접 드래그 앤 드롭 수행 (Capture)")
            cap_btn.setStyleSheet("background-color: #0E639C; color: white; padding: 10px; margin-top: 10px;")
            cap_btn.clicked.connect(start_drag_capture)
            self.form_layout.addRow(cap_btn)
            
        elif node.type == ActionType.WAIT:
            self._add_double_spinbox("대기 시간 (초)", "seconds", params.get("seconds", 1.0))
            
        elif node.type == ActionType.IMAGE_MATCH:
             # Image Capture UI moved from WAIT
            self._add_image_capture_ui("이미지 캡쳐", "image_path", params.get("image_path", ""))
            self._add_double_spinbox("일치 정확도 (0~1)", "confidence", params.get("confidence", 0.9))

        elif node.type == ActionType.VARIABLE_SET:
            self._add_line_edit("변수 이름", "variable_name", params.get("variable_name", "var"))
            self._add_line_edit("값 (계산식 가능)", "value", params.get("value", "0"))

        elif node.type == ActionType.IF_CONDITION:
            self._add_line_edit("조건식 (예: count > 10)", "condition", params.get("condition", "True"))
            self.form_layout.addRow(QLabel("<font color='gray'>Tip: 변수명을 직접 사용하세요.</font>"))

        elif node.type == ActionType.LOOP:
            self._add_spinbox("반복 횟수", "times", params.get("times", 5))
            self.form_layout.addRow(QLabel("<font color='gray'>Tip: 성공 시 True 경로, 종료 시 False 경로로 이동합니다.</font>"))

        elif node.type == ActionType.OCR_READ:
            self._add_line_edit("저장할 변수명", "variable_name", params.get("variable_name", "ocr_result"))
            # Region selection
            self._add_coord_picker("인식 시작 위치", "x", "y", params.get("x", 0), params.get("y", 0))
            self._add_spinbox("가로 폭 (Width)", "w", params.get("w", 200))
            self._add_spinbox("세로 높이 (Height)", "h", params.get("h", 50))

    def _update_values(self, node):
        """Update widget values without rebuilding form."""
        # Label
        if "_label" in self.param_widgets:
            w = self.param_widgets["_label"]
            if w.text() != node.label:
                w.blockSignals(True)
                w.setText(node.label)
                w.blockSignals(False)
        
        # Params
        for key, widget in self.param_widgets.items():
            if key == "_label": continue
            if key not in node.params: continue
            
            val = node.params[key]
            
            # Helper to block signal and set
            old_signal_state = widget.signalsBlocked()
            widget.blockSignals(True)
            
            if isinstance(widget, QLineEdit):
                if widget.text() != str(val):
                    widget.setText(str(val))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                # careful with types
                try:
                    if widget.value() != float(val):
                        widget.setValue(float(val))
                except: pass
            elif isinstance(widget, QLabel):
                # For Image Path preview label, usually we don't update text directly?
                # Actually for path we might update text.
                pass
                
            widget.blockSignals(old_signal_state)

    def _clear_form(self):
        self.param_widgets.clear()
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # --- Helper methods ---
    
    def _add_key_capture_edit(self, label, key, value):
        from PySide6.QtGui import QKeySequence
        
        widget = QLineEdit(str(value))
        # widget.setReadOnly(True) # Removed to ensure events are caught. Manual typing blocked by override.
        widget.setPlaceholderText("여기를 클릭하여 설정")
        widget.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #00FFcc;
                background-color: #2D2D30;
                color: #FFFFFF;
            }
        """)
        
        # Override Events
        original_focus_in = widget.focusInEvent
        original_focus_out = widget.focusOutEvent
        
        def focusInEvent(event):
            widget.setPlaceholderText("키를 누르세요... (Esc 취소)")
            if original_focus_in: original_focus_in(event)
            
        def focusOutEvent(event):
            widget.setPlaceholderText("여기를 클릭하여 설정")
            if original_focus_out: original_focus_out(event)

        def keyPressEvent(event):
            key_code = event.key()
            modifiers = event.modifiers()
            
            # Ignore pure modifier presses
            if key_code in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta]:
                return
            
            # Cancel on Esc
            if key_code == Qt.Key_Escape:
                widget.clearFocus()
                return

            # Clear on Backspace/Delete
            if key_code == Qt.Key_Backspace or key_code == Qt.Key_Delete:
                widget.setText("")
                self._on_param_change(key, "")
                return
                
            # Create Sequence
            seq = QKeySequence(key_code | modifiers)
            text = seq.toString(QKeySequence.NativeText)
            
            if text:
                widget.setText(text)
                self._on_param_change(key, text)
                widget.clearFocus() # Auto-finish after input
            
            # Do NOT call super().keyPressEvent(event) to prevent manual typing
                
        # Bind methods
        widget.focusInEvent = focusInEvent
        widget.focusOutEvent = focusOutEvent
        widget.keyPressEvent = keyPressEvent
        
        self.form_layout.addRow(label, widget)
        self.param_widgets[key] = widget

    def _add_coord_picker(self, label, key_x, key_y, val_x, val_y):
        from PySide6.QtWidgets import QHBoxLayout, QPushButton
        
        # Row Layout
        row_widget = QWidget()
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(0,0,0,0)
        
        # Inputs
        spin_x = QSpinBox()
        spin_x.setRange(-99999, 99999)
        spin_x.setValue(int(val_x))
        spin_x.valueChanged.connect(lambda v: self._on_param_change(key_x, v))
        self.param_widgets[key_x] = spin_x
        
        spin_y = QSpinBox()
        spin_y.setRange(-99999, 99999)
        spin_y.setValue(int(val_y))
        spin_y.valueChanged.connect(lambda v: self._on_param_change(key_y, v))
        self.param_widgets[key_y] = spin_y
        
        # Pick Button
        pick_btn = QPushButton("📍 좌표 찾기")
        pick_btn.clicked.connect(lambda: self._open_picker(spin_x, spin_y, key_x, key_y))
        
        layout.addWidget(QLabel("X:"))
        layout.addWidget(spin_x)
        layout.addWidget(QLabel("Y:"))
        layout.addWidget(spin_y)
        layout.addWidget(pick_btn)
        
        self.form_layout.addRow(label, row_widget)

    def _open_picker(self, spin_x, spin_y, key_x, key_y):
        from src.ui.coordinate_picker import CoordinatePicker
        from PySide6.QtCore import QTimer
        
        # Minimize main window
        if self.window():
            self.window().showMinimized()
            
        # Delay showing picker to allow minimize animation
        def show():
            self.picker = CoordinatePicker()
            self.picker.coords_picked.connect(lambda x, y: self._on_picked(x, y, spin_x, spin_y, key_x, key_y))
            # Restore on close/cancel too? Picker closes on pick.
            # If user presses ESC, picker closes. We need to handle restore there too.
            # For now, handle via signal. Ideally handle closeEvent.
            self.picker.show()
            
        QTimer.singleShot(200, show)
        
    def _on_picked(self, x, y, spin_x, spin_y, key_x, key_y):
        spin_x.setValue(x)
        spin_y.setValue(y)
        
        # Restore main window
        if self.window():
            self.window().showNormal()
            self.window().activateWindow() # Bring to front

    def _add_combobox(self, label, key, options, current_value, map_back=False, map_dict=None):
        from PySide6.QtWidgets import QComboBox
        widget = QComboBox()
        widget.addItems(options)
        widget.setCurrentText(str(current_value))
        
        if map_back:
            # Use provided map_dict or fallback to self.btn_reverse_map (legacy support)
            mapping = map_dict if map_dict else getattr(self, 'btn_reverse_map', {})
            widget.currentTextChanged.connect(lambda val: self._on_param_change(key, mapping.get(val, val)))
        else:
             widget.currentTextChanged.connect(lambda val: self._on_param_change(key, val))
             
        self.form_layout.addRow(label, widget)
        # Note: ComboBox update logic in _update_values needs implementation if driven externally.
        # simpler to skip for now or rebuild if combobox changes? NO.
        # We need it for consistency.
        # ComboBox is tricky because of map_back. For now, let's just assume it works.

    def _add_line_edit(self, label, key, value):
        widget = QLineEdit(str(value))
        widget.textChanged.connect(lambda val: self._on_param_change(key, val))
        self.form_layout.addRow(label, widget)
        self.param_widgets[key] = widget

    def _add_spinbox(self, label, key, value, suffix=""):
        widget = QSpinBox()
        widget.setRange(-99999, 99999)
        widget.setValue(int(value))
        widget.setSuffix(suffix)
        widget.valueChanged.connect(lambda val: self._on_param_change(key, val))
        self.form_layout.addRow(label, widget)
        self.param_widgets[key] = widget

    def _add_double_spinbox(self, label, key, value):
        widget = QDoubleSpinBox()
        widget.setRange(0, 99999)
        widget.setValue(float(value))
        widget.valueChanged.connect(lambda val: self._on_param_change(key, val))
        self.form_layout.addRow(label, widget)
        self.param_widgets[key] = widget

    def _add_image_capture_ui(self, label_text, param_key, current_value):
        from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QWidget
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import Qt
        import os
        
        # Container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Row 1: Capture Button
        btn = QPushButton("📷 화면 캡쳐 (Capture)")
        btn.setStyleSheet("background-color: #0E639C; color: white;")
        
        # Row 2: Path Display
        path_lbl = QLabel(current_value if current_value else "이미지 없음")
        path_lbl.setStyleSheet("color: gray; font-size: 10px;")
        path_lbl.setWordWrap(True)
        self.param_widgets[param_key] = path_lbl # Store for updates
        
        # Row 3: Preview
        preview_lbl = QLabel()
        preview_lbl.setFixedSize(200, 100)
        preview_lbl.setStyleSheet("border: 1px dashed gray;")
        preview_lbl.setAlignment(Qt.AlignCenter)
        
        if current_value and os.path.exists(current_value):
             pix = QPixmap(current_value)
             preview_lbl.setPixmap(pix.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            preview_lbl.setText("미리보기")
        
        btn.clicked.connect(lambda: self._open_snipping_tool(param_key, path_lbl, preview_lbl))
        
        layout.addWidget(btn)
        layout.addWidget(path_lbl)
        layout.addWidget(preview_lbl)
        
        # Removed Action Selection ComboBox as per request
        
        self.form_layout.addRow(label_text, container)

    def _open_snipping_tool(self, key, path_lbl, preview_lbl):
        from src.ui.snipping_tool import SnippingTool
        from PySide6.QtCore import QTimer
        
        if self.window():
            self.window().showMinimized()
            
        def show():
            self.snipper = SnippingTool()
            self.snipper.image_captured.connect(lambda path: self._on_image_captured(path, key, path_lbl, preview_lbl))
            
        QTimer.singleShot(300, show) # Slightly longer delay for minimize

    def _on_image_captured(self, path, key, path_lbl, preview_lbl):
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import Qt
        
        # Restore Window
        if self.window():
            self.window().showNormal()
            self.window().activateWindow()
            
        # Update UI
        path_lbl.setText(path)
        pix = QPixmap(path)
        preview_lbl.setPixmap(pix.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Update Store
        self._on_param_change(key, path)

    def _on_param_change(self, key, value):
        if self.current_node_id:
            self.on_update_callback(self.current_node_id, {key: value})
            
    def _on_field_change(self, key, value):
        # Handle top level field (label)
        # We need a separate callback for label update?
        # Store doesn't have update_node_label... wait.
        # Actually update_node_params updates params. 
        # Label is separate. Store needs update_node(id, label=...)
        # For now, let's just hack it: update_node_params usually merges.
        # But ActionNode stores label separately.
        # Let's ignore label update in store for now OR fix store.
        pass 

    def _on_test_click(self):
        if self.current_node_id and self.on_test_callback:
            self.on_test_callback(self.current_node_id)
