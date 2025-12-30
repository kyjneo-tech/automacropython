from PySide6.QtWidgets import (QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
                               QLabel, QListWidget, QGraphicsView, QGraphicsScene, QApplication, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, Signal, Slot, QProcess
import sys
import os
import json
from src.state.store import Store

class MainWindow(QMainWindow):
    recording_finished = Signal(list) # Signal to handle recording finish from another thread
    quick_capture_finished = Signal(dict) # Signal for quick capture (scroll/drag)

    def __init__(self, store: Store):
        super().__init__()
        self.store = store
        
        # Connect Signals
        self.recording_finished.connect(self._on_recording_finished)
        self.quick_capture_finished.connect(self._on_quick_capture_finished)
        
        self.setWindowTitle("AutoFlow X")
        self.resize(1280, 800)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 3-Pane Layout using Splitters
        # [ Toolbox | Canvas | Inspector ]
        
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # 1. Toolbox (Left)
        self.toolbox_container = QWidget()
        self.toolbox_layout = QVBoxLayout(self.toolbox_container)
        self.toolbox_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbox_header = QLabel("도구 모음")
        self.toolbox_header.setObjectName("Header")
        self.toolbox_list = QListWidget()
        # Korean Labels for Toolbox
        self.toolbox_items = {
            "마우스 클릭 (Click)": "CLICK",
            "마우스 이동 (Move)": "MOUSE_MOVE",
            "키보드 입력 (Keyboard)": "KEYBOARD_INPUT",
            "대기 (Wait)": "WAIT",
            "이미지 찾아 이동 (Image)": "IMAGE_MATCH",
            "스크롤 (Scroll)": "SCROLL",
            "드래그 (Drag)": "DRAG",
            "논리 분기 (IF)": "IF_CONDITION",
            "변수 설정 (Set)": "VARIABLE_SET",
            "문자 인식 (OCR)": "OCR_READ"
        }
        self.toolbox_list.addItems(self.toolbox_items.keys())
        self.toolbox_list.setDragEnabled(True) # Enable Drag
        self.toolbox_list.itemClicked.connect(self.on_toolbox_item_click) # Click to add
        self.toolbox_layout.addWidget(self.toolbox_header)
        self.toolbox_layout.addWidget(self.toolbox_list)
        
        # 2. Graph Canvas (Center)
        self.canvas_container = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_container)
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Layout (Label + Run Button)
        self.canvas_header_widget = QWidget()
        self.canvas_header_widget.setStyleSheet("background-color: #252526;")
        self.canvas_header_layout = QHBoxLayout(self.canvas_header_widget)
        self.canvas_header_layout.setContentsMargins(5, 5, 5, 5)
        
        self.canvas_header = QLabel("워크플로우")
        self.canvas_header.setObjectName("Header")
        
        self.run_btn = QPushButton("▶ 실행")
        self.run_btn.setStyleSheet("background-color: #0E639C; color: white; border: none; padding: 5px;")
        self.run_btn.clicked.connect(self.run_workflow)
        
        self.canvas_header_layout.addWidget(self.canvas_header)
        self.canvas_header_layout.addStretch()
        
        # Record Button
        self.record_btn = QPushButton("● 녹화 (Record)")
        self.record_btn.setStyleSheet("""
            QPushButton {
                 background-color: #2D2D30; 
                 color: #FF4081; 
                 border: 1px solid #FF4081; 
                 padding: 5px 10px;
                 font-weight: bold;
            }
            QPushButton:hover {
                 background-color: #FF4081;
                 color: white;
            }
        """)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.canvas_header_layout.addWidget(self.record_btn)

        self.canvas_header_layout.addWidget(self.run_btn)
        
        self.canvas_layout.addWidget(self.canvas_header_widget)
        
        # Initialize Graph
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-50000, -50000, 100000, 100000) # Infinite-ish
        from src.ui.graph.view import GraphView
        self.view = GraphView(self.scene, 
                              on_drop_callback=self.on_node_drop,
                              on_connect_callback=self.store.connect_nodes)
        
        self.canvas_layout.addWidget(self.canvas_header)
        self.canvas_layout.addWidget(self.view)
        
        # 3. Inspector (Right)
        self.inspector_container = QWidget()
        self.inspector_layout = QVBoxLayout(self.inspector_container)
        self.inspector_layout.setContentsMargins(0, 0, 0, 0)
        
        from src.ui.inspector import InspectorWidget
        self.inspector = InspectorWidget(
            on_update_callback=self.store.update_node_params,
            on_test_callback=self.test_single_node
        )
        self.inspector_layout.addWidget(self.inspector)
        
        # Add to Splitter
        self.main_splitter.addWidget(self.toolbox_container)
        self.main_splitter.addWidget(self.canvas_container)
        self.main_splitter.addWidget(self.inspector_container)
        
        # Set Initial Sizes (15%, 60%, 25%)
        self.main_splitter.setSizes([200, 800, 300])
        
        main_layout.addWidget(self.main_splitter)
        
        # Connect Observer
        self.store.subscribe(self.on_store_update)
        
        # Initial Render
        self.on_store_update()

    def on_store_update(self, event_type="ALL", payload=None):
        """
        Handle Store updates intelligently to avoid crash-inducing re-renders.
        
        event_type: "STRUCTURE" (Add/Remove/Link), "SELECTION", "POSITION", "PARAMS", "ALL"
        """
        
        # 1. Selection Changed: Update Inspector ONLY. 
        # DO NOT TOUCH SCENE. The Item handles its own visual selection state.
        if event_type == "SELECTION":
            self._update_inspector()
            return

        # 2. Position Changed:
        # If triggered by Item Drag, the Item is already at new pos.
        # If triggered by Undo/Redo (not impl yet) or Code, we might need to update Item.
        # For now, we assume Store update comes from Item Drag, so we do nothing to Scene.
        if event_type == "POSITION":
            return
            
        # 3. Params Changed: Update Inspector if selected. Update Node Label if changed.
        if event_type == "PARAMS":
            self._update_inspector()
            # If label changed, we might need to repaint node.
            # Ideally find specific item and call update()
            # For simplicity, if label is critical, we might need structure update or smart search.
            # Let's simple re-search item and update text.
            if payload: 
                # payload is node_id in this case
                # We don't have easy lookup table unless we maintain it. 
                # naive approach: full re-render for label change is safer than crash, 
                # but "PARAMS" usually doesn't change geometry much.
                pass 
            return

        # 4. Structure (Add/Remove/Link) or ALL: Full Re-render
        # This is the heavy hammer, but safe for Add/Remove.
        self._render_scene()
        self._update_inspector()

    def _update_inspector(self):
        if self.store.state.selected_node_id:
            node = self.store.get_node(self.store.state.selected_node_id)
            self.inspector.set_node(node)
        else:
            self.inspector.set_node(None)

    def _render_scene(self):
        nodes = self.store.get_all_nodes()
        print(f"DEBUG: Rendering scene with {len(nodes)} nodes...")
        self.scene.clear()
        
        from src.ui.graph.node_item import NodeItem
        
        # Dictionary to store node items by ID for edge linking
        node_items = {}
        
        for node in nodes:
            item = NodeItem(node, 
                            on_select_callback=self.store.select_node,
                            on_move_callback=self.store.update_node_position)
            
            # Sync Selection State
            if self.store.state.selected_node_id == node.id:
                item.setSelected(True)
                
            self.scene.addItem(item)
            node_items[node.id] = item
            
        # Draw Edges
        from src.ui.graph.edge_item import EdgeItem
        from PySide6.QtCore import QPointF
        
        for node in nodes:
            if node.next_node_id and node.next_node_id in node_items:
                source_item = node_items[node.id]
                target_item = node_items[node.next_node_id]
                
                edge = EdgeItem(source_item, target_item)
                self.scene.addItem(edge)
                
                # Register edge with both nodes for updates
                source_item.add_edge(edge)
                target_item.add_edge(edge)

    def on_toolbox_item_click(self, item):
        type_str = item.text()
        # Add to center of view or default position
        # For simplicity, add at (200, 200) plus some jitter or last pos
        self.on_node_drop(type_str, 200, 200)

    def on_node_drop(self, type_str: str, x: float, y: float):
        from src.domain.actions import ActionNode, ActionType
        
        # Map string to ActionType
        # type_str comes from the list widget text (Korean)
        try:
            # Check if it's one of our Korean keys
            if type_str in self.toolbox_items:
                english_type = self.toolbox_items[type_str]
                action_type = ActionType(english_type)
            else:
                # Fallback if raw string passed
                action_type = ActionType(type_str)
        except ValueError:
            # Fallback
            action_type = ActionType.CLICK
            
        new_node = ActionNode(
            type=action_type,
            label=type_str.split('(')[0].strip(), # Use Korean part as default label
            x=x,
            y=y
        )
        
        self.store.add_node(new_node)
        self.store.select_node(new_node.id)
        
    def keyPressEvent(self, event):
        # Handle Shortcuts
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            # Handle Item Deletion (Node or Edge)
            selected_items = self.scene.selectedItems()
            if not selected_items and self.store.state.selected_node_id:
                 # Fallback if store has selection but scene doesn't (rare)
                 self.store.remove_node(self.store.state.selected_node_id)
                 return

            for item in selected_items:
                from src.ui.graph.node_item import NodeItem
                from src.ui.graph.edge_item import EdgeItem
                
                if isinstance(item, NodeItem):
                    self.store.remove_node(item.node_id)
                elif isinstance(item, EdgeItem):
                    # Disconnect
                    # Update source node to next_node_id = None
                    self.store.connect_nodes(item.source_node_id, None)
                
        elif event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_C:
                # Copy
                if self.store.state.selected_node_id:
                    node = self.store.get_node(self.store.state.selected_node_id)
                    if node:
                        import json
                        clip = QApplication.clipboard()
                        clip.setText(json.dumps(node.to_dict()))
            
            elif event.key() == Qt.Key_V:
                # Paste
                clip = QApplication.clipboard()
                text = clip.text()
                if text:
                    try:
                        import json
                        import uuid
                        data = json.loads(text)
                        # Create new ID and shift position
                        data['id'] = str(uuid.uuid4())
                        data['x'] += 20
                        data['y'] += 20
                        
                        from src.domain.actions import ActionNode
                        new_node = ActionNode.from_dict(data)
                        self.store.add_node(new_node)
                        self.store.select_node(new_node.id)
                    except Exception as e:
                        print(f"Paste failed: {e}")
                        
        super().keyPressEvent(event)

    def run_workflow(self):
        from src.domain.runner import WorkflowRunner
        from src.infra.input_driver import InputDriver
        from PySide6.QtCore import QThread, Signal
        
        # Minimize Window only (do not hide, to ensure easy restoration)
        self.showMinimized() 
        
        # Instantiate Driver on Main Thread
        # This is CRITICAL for macOS pynput compatibility
        if not hasattr(self, 'global_driver'):
            self.global_driver = InputDriver()
        
        class RunnerWorker(QThread):
            finished_run = Signal()
            
            def __init__(self, store, driver):
                super().__init__()
                self.store = store
                self.driver = driver
                
            def run(self):
                # Pass existing driver
                runner = WorkflowRunner(self.store, self.driver)
                try:
                    runner.run()
                except Exception as e:
                    print(f"Run Error: {e}")
                
                self.finished_run.emit()
                
        self.worker = RunnerWorker(self.store, self.global_driver)
        self.worker.finished_run.connect(self._on_run_finished)
        self.worker.start()
        
    def _on_run_finished(self):
        print("Workflow Finished. Restoring UI.")
        
        # Standard restore
        self.show()
        self.showNormal()
        self.raise_()
        self.activateWindow()
        
        if sys.platform == "darwin":
            # Power-restore for macOS (only if needed)
            self.setWindowState(Qt.WindowActive)
            # Trick: Temporary StaysOnTop to force focus
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
            
            from PySide6.QtCore import QTimer
            def remove_topmost():
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
                self.show() # Re-show to apply flags
                self.activateWindow()
            QTimer.singleShot(100, remove_topmost)
        
        # Clean up
        if hasattr(self, 'worker'):
             self.worker.wait()
             del self.worker

    def test_single_node(self, node_id: str):
        """
        Execute a single node action immediately for testing/debugging.
        """
        node = self.store.get_node(node_id)
        if not node:
            return
            
        print(f"Testing Node: {node.label}")
        
        # We can reuse part of Workflow Runner or just instantiate Driver
        # Reusing Runner's _execute_node logic is best to ensure consistency.
        # But Runner is designed for Threading? 
        # For a single action, running in main thread might freeze UI for a split second (Wait),
        # but it's okay for "Test". Or use thread for safety.
        
    
    def test_single_node(self, node_id: str):
        """
        Execute a single node action immediately for testing/debugging.
        """
        node = self.store.get_node(node_id)
        if not node:
            return
            
        print(f"Testing Node: {node.label}")
        
        # Accessing runner logic directly.
        # Run in main thread to avoid macOS threading issues (Trace Trap).
        # Use QTimer to allow UI to refresh (e.g. button click state) before running.
        from src.domain.runner import WorkflowRunner
        from PySide6.QtCore import QTimer
        
        def _run():
            runner = WorkflowRunner(self.store)
            try:
                runner._execute_node(node)
                print(f"Test Complete: {node.label}")
                # Optional: Show a small tooltip/status
            except Exception as e:
                print(f"Test Failed: {e}")
                
        # Delay 100ms
        QTimer.singleShot(100, _run)

    def run_quick_capture(self, mode: str, callback):
        """Run recorder process in a specific mode (scroll/drag) and callback with results."""
        self._quick_capture_callback = callback
        self.hide()
        
        self.quick_process = QProcess()
        python_exe = sys.executable
        script_path = os.path.join(os.getcwd(), "src", "recorder_process.py")
        
        def finished(exit_code, exit_status):
            output = self.quick_process.readAllStandardOutput().data().decode('utf-8')
            data = {}
            try:
                if output.strip():
                    data = json.loads(output)
            except: pass
            self.quick_capture_finished.emit(data)

        self.quick_process.finished.connect(finished)
        self.quick_process.start(python_exe, [script_path, "--mode", mode])

    @Slot(dict)
    def _on_quick_capture_finished(self, data):
        self.showNormal()
        self.raise_()
        self.activateWindow()
        
        if hasattr(self, '_quick_capture_callback') and self._quick_capture_callback:
            self._quick_capture_callback(data)
            self._quick_capture_callback = None

    def toggle_recording(self):
        # Check if already recording
        if hasattr(self, 'recorder_process') and self.recorder_process.state() == QProcess.Running:
            # Should be handled by process itself (F9), but if button clicked manually
            # we can try to kill it or send signal? 
            # For now, let's just let F9 handle it or kill if button clicked.
            self.recorder_process.kill()
            return

        # Start Recording Process
        
        # Show Guide
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("녹화를 시작합니다.")
        msg.setInformativeText("프로그램 창이 숨겨집니다.\n\n화면 우측 하단의 [🔴 REC] 표시를 확인하세요.\n종료하려면 키보드의 [F9] 키를 누르세요.")
        msg.setWindowTitle("녹화 시작")
        msg.exec()
        
        try:
            print("DEBUG: Starting Recorder Process...")
            
            # Hide Window immediately
            self.hide()
            
            # Use QProcess
            import sys
            import os
            
            self.recorder_process = QProcess()
            
            # Path to python executable and script
            python_exe = sys.executable
            script_path = os.path.join(os.getcwd(), "src", "recorder_process.py")
            
            self.recorder_process.finished.connect(self.on_recorder_process_finished)
            self.recorder_process.start(python_exe, [script_path])
            
            # Update Button State (though invisible)
            self.record_btn.setText("■ 중지 (F9)")
            self.record_btn.setStyleSheet("background-color: #FF4081; color: white; font-weight: bold; padding: 5px;")
            
        except Exception as e:
            print(f"ERROR: Failed to start recorder process: {e}")
            self.show() # Restore if failed
            import traceback
            traceback.print_exc()

    def on_recorder_process_finished(self, exit_code, exit_status):
        print(f"Recorder Process Finished. Code: {exit_code}, Status: {exit_status}")
        
        # Read Output
        raw_output = self.recorder_process.readAllStandardOutput().data()
        output = raw_output.decode('utf-8', errors='ignore') # Ignore decoding errors
        
        raw_error = self.recorder_process.readAllStandardError().data()
        error = raw_error.decode('utf-8', errors='ignore')
        
        print(f"Recorder Stdout Len: {len(output)}")
        if error:
            print(f"Recorder Stderr: {error}")
            
        new_nodes = []
        try:
            import json
            from src.domain.recorder import EventProcessor
            
            # Parse JSON
            if output.strip():
                # Attempt to find JSON array in case of extra output
                # Simple heuristic: find first '[' and last ']'
                start = output.find('[')
                end = output.rfind(']')
                
                if start != -1 and end != -1:
                    json_str = output[start:end+1]
                    events = json.loads(json_str)
                    print(f"Parsed {len(events)} raw events from JSON.")
                    
                    if not events:
                        QMessageBox.warning(self, "녹화 데이터 없음", 
                                            "수집된 이벤트가 없습니다.\n\nmacOS의 '손쉬운 사용(Accessibility)' 또는 '입력 모니터링' 권한이 허용되어 있는지 확인해주세요.")
                    else:
                        new_nodes = EventProcessor.process_events(events)
                        print(f"Processed into {len(new_nodes)} action nodes.")
                else:
                    print(f"No JSON array found in output: {output[:200]}...")
            else:
                print("No output from recorder (Empty).")
                
        except json.JSONDecodeError as e:
            print(f"Failed to decode recorder output: {e}\nOutput preview: {output[:500]}")
        except Exception as e:
            print(f"Error processing recorded events: {e}")
            import traceback
            traceback.print_exc()

        # Signal to restore UI
        self.recording_finished.emit(new_nodes)

    @Slot(list)
    def _on_recording_finished(self, new_nodes):
        print("Recording Finished Signal Received.")
        
        # Restore Window
        self.showNormal()
        self.raise_()
        self.activateWindow()
        
        # Reset Button
        self.record_btn.setText("● 녹화 (Record)")
        self.record_btn.setStyleSheet("""
            QPushButton {
                 background-color: #2D2D30; 
                 color: #FF4081; 
                 border: 1px solid #FF4081; 
                 padding: 5px 10px;
                 font-weight: bold;
            }
            QPushButton:hover {
                 background-color: #FF4081;
                 color: white;
            }
        """)
        self.setWindowTitle("AutoFlow X")
        
        # Add nodes to graph
        if new_nodes:
            print(f"Adding {len(new_nodes)} recorded nodes...")
            
            # Determine Start Position: Center of Current Viewport
            view_center = self.view.mapToScene(self.view.viewport().rect().center())
            start_x = view_center.x()
            start_y = view_center.y()
            
            current_y = start_y
            prev_id = None
            
            # If there is a selected node, try to connect first recorded node to it
            if self.store.state.selected_node_id:
                prev_id = self.store.state.selected_node_id
            
            for node in new_nodes:
                node.x = start_x
                node.y = current_y
                self.store.add_node(node)
                
                if prev_id:
                    self.store.connect_nodes(prev_id, node.id)
                    
                prev_id = node.id
                current_y += 100 # Vertical spacing
                
            print(f"Recording processed. Last node at ({node.x}, {node.y})")
            
            # Force refresh
            self.view.viewport().update()
        else:
            print("No events captured.")
                    
                
