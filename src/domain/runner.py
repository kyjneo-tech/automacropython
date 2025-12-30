import time
from src.state.store import Store
from src.domain.actions import ActionType
from src.infra.input_driver import InputDriver
import threading

class WorkflowRunner:
    def __init__(self, store: Store, driver: InputDriver = None):
        self.store = store
        self.driver = driver if driver else InputDriver()
        self._stop_flag = False
        self.variables = {} # Memory for automation variables
        
    def run(self, start_node_id=None):
        self.variables = {} # Reset variables on each run
        self._run_loop(start_node_id)

    def _run_loop(self, start_node_id=None):
        if not start_node_id:
            nodes = self.store.get_all_nodes()
            if not nodes:
                print("No nodes to execute.")
                return
            current_id = nodes[0].id
        else:
            current_id = start_node_id
            
        print("--- Workflow Started ---")
        
        while current_id and not self._stop_flag:
            node = self.store.get_node(current_id)
            if not node: break
                
            print(f"Executing: {node.label} ({node.type.name})")
            
            try:
                # Execution now returns a boolean (for branching) or None
                result = self._execute_node(node)
                
                # Logic Branching
                if node.type == ActionType.IF_CONDITION or node.type == ActionType.IMAGE_MATCH:
                    # IF and IMAGE_MATCH can branch based on result
                    if result:
                        current_id = node.true_node_id if node.true_node_id else node.next_node_id
                    else:
                        current_id = node.false_node_id if node.false_node_id else node.next_node_id
                else:
                    # Normal flow
                    current_id = node.next_node_id
                    
            except Exception as e:
                print(f"Execution Error at {node.label}: {e}")
                import traceback
                traceback.print_exc()
                break
                
        print("--- Workflow Finished ---")

    def _execute_node(self, node):
        params = node.params
        
        if node.type == ActionType.CLICK:
            click_type = params.get("click_type", "single")
            self.driver.click(
                x=int(params.get("x", 0)), 
                y=int(params.get("y", 0)),
                double=(click_type == "double"),
                button=params.get("button", "left")
            )

        elif node.type == ActionType.KEYBOARD_INPUT:
            mode = params.get("mode", "text")
            if mode == "text":
                # Support variable interpolation in text: {my_var}
                raw_text = params.get("text", "")
                try:
                    interpolated_text = raw_text.format(**self.variables)
                except:
                    interpolated_text = raw_text
                self.driver.type_text(
                    interpolated_text,
                    float(params.get("interval", 0.05))
                )
            else: # shortcut
                self.driver.press_key(params.get("keys", ""))

        elif node.type == ActionType.MOUSE_MOVE:
            self.driver.move(int(params.get("x", 0)), int(params.get("y", 0)))

        elif node.type == ActionType.SCROLL:
            self.driver.scroll(
                int(params.get("dx", 0)), 
                int(params.get("dy", 0)),
                x=int(params.get("x", 0)),
                y=int(params.get("y", 0))
            )
            
        elif node.type == ActionType.DRAG:
            self.driver.drag(
                (int(params.get("x1", 0)), int(params.get("y1", 0))),
                (int(params.get("x2", 0)), int(params.get("y2", 0)))
            )

        elif node.type == ActionType.WAIT:
            self.driver.wait(float(params.get("seconds", 1.0)))
            
        elif node.type == ActionType.IMAGE_MATCH:
            image_path = params.get("image_path", "")
            confidence = float(params.get("confidence", 0.9))
            
            start_time = time.time()
            match_pos = None
            # Retry loop for 5 seconds
            while time.time() - start_time < 5.0:
                match_pos = self.driver.find_image(image_path, confidence)
                if match_pos: break
                time.sleep(0.5)
            
            if match_pos:
                self.driver.move(match_pos[0], match_pos[1])
                return True
            return False

        elif node.type == ActionType.VARIABLE_SET:
            var_name = params.get("variable_name", "var")
            var_value = params.get("value", "")
            try:
                # Basic calculation support
                self.variables[var_name] = eval(str(var_value), {}, self.variables)
            except:
                self.variables[var_name] = var_value
            print(f"[Runner] Set {var_name} = {self.variables[var_name]}")

        elif node.type == ActionType.IF_CONDITION:
            cond = params.get("condition", "True")
            try:
                return bool(eval(cond, {}, self.variables))
            except Exception as e:
                print(f"[Runner] Condition Error: {e}")
                return False

        elif node.type == ActionType.LOOP:
            times = int(params.get("times", 5))
            loop_var = f"_loop_cnt_{node.id}"
            
            curr = self.variables.get(loop_var, 0)
            if curr < times:
                self.variables[loop_var] = curr + 1
                print(f"[Runner] Loop {curr + 1}/{times}")
                return True # Continue loop
            else:
                # Loop finished, reset counter for next time if needed
                self.variables[loop_var] = 0
                return False # Exit loop

        elif node.type == ActionType.OCR_READ:
            var_name = params.get("variable_name", "ocr_result")
            text = self.driver.read_text_at(
                int(params.get("x", 0)), 
                int(params.get("y", 0)),
                int(params.get("w", 100)),
                int(params.get("h", 50))
            )
            self.variables[var_name] = text
            return True
            
        return None
