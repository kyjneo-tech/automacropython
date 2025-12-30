import sys
import time
import json
import threading
import argparse
from pynput import mouse, keyboard
import tkinter as tk

# Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--mode", default="full", choices=["full", "scroll", "drag"])
args = parser.parse_args()

# Global State
events = []
start_time = time.time()
is_recording = True
mode = args.mode

# For Quick Capture Modes
last_action_time = time.time()
quick_captured_data = {}

def add_event(event_type, data):
    global last_action_time
    last_action_time = time.time()
    events.append({
        "time": time.time() - start_time,
        "type": event_type,
        "data": data
    })

# --- Listeners ---

def on_click(x, y, button, pressed):
    global quick_captured_data
    add_event("click", {"x": x, "y": y, "button": str(button), "pressed": pressed})
    sys.stderr.write(f"[RecorderProcess] Click detected. Total: {len(events)}\n")
    
    if mode == "drag":
        if pressed:
            quick_captured_data["x1"], quick_captured_data["y1"] = x, y
        else:
            quick_captured_data["x2"], quick_captured_data["y2"] = x, y
            # Check distance to see if it was a real drag
            dist = ((quick_captured_data["x2"]-quick_captured_data["x1"])**2 + (quick_captured_data["y2"]-quick_captured_data["y1"])**2)**0.5
            if dist > 10:
                stop_recording()

def on_scroll(x, y, dx, dy):
    import sys
    global quick_captured_data
    
    # Scale down scroll values on macOS to match user expectation (approx 1/2)
    if sys.platform == "darwin":
        dx /= 2.0
        dy /= 2.0

    add_event("scroll", {"dx": dx, "dy": dy})
    sys.stderr.write(f"[RecorderProcess] Scroll detected: dx={dx:.2f}, dy={dy:.2f}. Total events: {len(events)}\n")
    
    if mode == "scroll":
        # Capture starting position from the first scroll event
        if "x" not in quick_captured_data:
            quick_captured_data["x"] = x
            quick_captured_data["y"] = y
            
        quick_captured_data["dx"] = quick_captured_data.get("dx", 0) + dx
        quick_captured_data["dy"] = quick_captured_data.get("dy", 0) + dy

def on_key_press(key):
    try:
        # Check F9 for Stop
        if key == keyboard.Key.f9:
            sys.stderr.write("[RecorderProcess] F9 Detected! Stopping...\n")
            stop_recording()
            return
            
        add_event("key_down", {"key": str(key)})
        sys.stderr.write(f"[RecorderProcess] Key detected: {key}. Total: {len(events)}\n")
    except:
        pass

def on_key_release(key):
    add_event("key_up", {"key": str(key)})

def start_listeners():
    sys.stderr.write(f"[RecorderProcess] Starting listeners in {mode} mode...\n")
    m_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    m_listener.start()
    k_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    k_listener.start()
    return m_listener, k_listener

# --- UI (Overlay) ---

def stop_recording():
    global is_recording
    is_recording = False
    try: root.quit()
    except: pass

def run_overlay():
    global root
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.8) # Slightly more opaque for Windows readability
    
    # Position: Bottom Right, with safety margin for taskbars
    try:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        width = 160
        height = 50
        # Use more margin (50px) to avoid being covered by Mac Dock or Win Taskbar
        x = screen_width - width - 50
        y = screen_height - height - 70
        root.geometry(f"{width}x{height}+{x}+{y}")
    except:
        root.geometry("160x50+100+100") # Fallback
    
    txt = "🔴 REC (F9)"
    if mode == "scroll": txt = "🖱️ Scroll now"
    elif mode == "drag": txt = "🖱️ Drag now"
    
    label = tk.Label(root, text=txt, fg="white", bg="#222222", font=("Arial", 12, "bold"))
    label.pack(fill="both", expand=True)
    
    def auto_close():
        if not is_recording:
            root.destroy()
            return
        
        # Scroll Mode Auto-Stop: 1 second after last action
        if mode == "scroll" and len(events) > 0:
            if time.time() - last_action_time > 1.0:
                stop_recording()
                
        root.after(100, auto_close)
            
    auto_close()
    root.mainloop()

# --- Main ---

if __name__ == "__main__":
    try:
        m, k = start_listeners()
        run_overlay()
        m.stop(); k.stop()
        
        if mode == "full":
            print(json.dumps(events))
        else:
            # Return captured summary for quick modes
            print(json.dumps(quick_captured_data))
            
        sys.stdout.flush()
    except Exception as e:
        sys.stderr.write(f"[RecorderProcess] Error: {str(e)}\n")
