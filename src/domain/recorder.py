from typing import List, Dict, Any
from src.domain.actions import ActionNode, ActionType

class EventProcessor:
    @staticmethod
    def process_events(events: List[Dict[str, Any]]) -> List[ActionNode]:
        nodes = []
        i = 0
        n = len(events)
        
        current_text = ""
        drag_start = None
        scroll_acc = {"dx": 0, "dy": 0, "count": 0}
        
        # Modifier tracking
        held_keys = set()
        
        def normalize_key(k):
            import sys
            k = k.replace("'", "")
            # Mac Cmd key is Key.cmd
            # Windows Ctrl key is Key.ctrl, Windows key is Key.cmd
            if "Key.cmd" in k: 
                return "cmd" if sys.platform == "darwin" else "win"
            if "Key.ctrl" in k: return "ctrl"
            if "Key.alt" in k: return "alt"
            if "Key.shift" in k: return "shift"
            return k.replace("Key.", "")

        def is_modifier(k):
            return k in ["cmd", "ctrl", "alt", "shift"]

        def flush_text():
            nonlocal current_text
            if current_text:
                nodes.append(ActionNode(type=ActionType.KEYBOARD_INPUT, label=f"Type '{current_text}'", params={"mode": "text", "text": current_text}))
                current_text = ""
                
        def flush_scroll():
            nonlocal scroll_acc
            if scroll_acc["count"] > 0:
                print(f"DEBUG: Flushing Scroll. Total DX={scroll_acc['dx']}, DY={scroll_acc['dy']}, Count={scroll_acc['count']}")
                nodes.append(ActionNode(type=ActionType.SCROLL, label=f"Scroll", params={"dx": scroll_acc["dx"], "dy": scroll_acc["dy"]}))
                scroll_acc = {"dx": 0, "dy": 0, "count": 0}

        while i < n:
            evt = events[i]
            e_type = evt["type"]
            data = evt["data"]
            
            # 1. Time gap handling
            if i > 0:
                dt = evt["time"] - events[i-1]["time"]
                if dt > 1.5 and not drag_start and not held_keys:
                     flush_text()
                     flush_scroll()
                     nodes.append(ActionNode(type=ActionType.WAIT, label=f"Wait {round(dt,1)}s", params={"seconds": round(dt, 1)}))

            # 2. Mouse Handling
            if e_type == "click":
                if data["pressed"]:
                    flush_text()
                    flush_scroll()
                    drag_start = (data["x"], data["y"], evt["time"])
                else:
                    if drag_start:
                        x1, y1, t1 = drag_start
                        x2, y2 = data["x"], data["y"]
                        drag_start = None
                        dist = ((x2-x1)**2 + (y2-y1)**2)**0.5
                        if dist > 20:
                            nodes.append(ActionNode(type=ActionType.DRAG, label="Drag", params={"x1": x1, "y1": y1, "x2": x2, "y2": x2}))
                        else:
                            btn = "left"
                            if "right" in data["button"]: btn = "right"
                            nodes.append(ActionNode(type=ActionType.CLICK, label="Click", params={"x": x1, "y": y1, "button": btn}))
            
            elif e_type == "scroll":
                import sys
                flush_text()
                s_dx, s_dy = data["dx"], data["dy"]
                if sys.platform == "darwin":
                    s_dx /= 2.0; s_dy /= 2.0
                scroll_acc["dx"] += s_dx; scroll_acc["dy"] += s_dy; scroll_acc["count"] += 1
                # print(f"DEBUG: Scroll Accumulating... current dy={scroll_acc['dy']}")
            
            # 3. Keyboard Handling (The Core Logic)
            elif e_type == "key_down":
                k = normalize_key(data["key"])
                if k == "f9": # Ignore stop key
                    i += 1; continue
                
                held_keys.add(k)
                
                # Check if this is a shortcut (any modifier held)
                modifiers_held = [m for m in held_keys if is_modifier(m)]
                
                if modifiers_held:
                    # If we just pressed a non-modifier while modifiers are held, it's a shortcut
                    if not is_modifier(k):
                        flush_text()
                        # Sort modifiers for consistent label: cmd+shift+c
                        shortcut = "+".join(sorted(modifiers_held) + [k])
                        nodes.append(ActionNode(type=ActionType.KEYBOARD_INPUT, label=f"Hotkey {shortcut}", params={"mode": "shortcut", "keys": shortcut}))
                else:
                    # Normal typing
                    if len(k) == 1:
                        current_text += k
                    elif k == "space":
                        current_text += " "
                    elif k == "enter":
                        flush_text()
                        nodes.append(ActionNode(type=ActionType.KEYBOARD_INPUT, label="Key Enter", params={"mode": "shortcut", "keys": "enter"}))
                    # Ignore other standalone special keys for now or add as shortcut
            
            elif e_type == "key_up":
                k = normalize_key(data["key"])
                if k in held_keys:
                    held_keys.remove(k)

            i += 1
            
        flush_text(); flush_scroll()
        return nodes
