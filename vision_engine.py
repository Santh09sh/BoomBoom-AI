import cv2
import mediapipe as mp
import threading
import tkinter as tk
import math
import time
import PIL.Image
import PIL.ImageTk
import pyautogui
from controller import MouseController

# Global state for new gestures
last_gesture_time = 0
prev_wrist_x = None
prev_wrist_y = None
swipe_start_time = 0
from voice_engine import start_voice_assistant, agent_state

# Global state
vision_running = False
app_running = True

def toggle_vision():
    global vision_running
    vision_running = not vision_running
    if vision_running:
        btn_start_stop.config(text="Stop Vision", bg="#e74c3c", fg="white")
    else:
        btn_start_stop.config(text="Start Vision", bg="#2ecc71", fg="black")

def on_closing():
    global app_running
    app_running = False

current_orb_photo = None

def is_fist(landmarks):
    # Rotation-invariant check: compares distance from tip to wrist vs MCP to wrist
    wrist = landmarks.landmark[0]
    for tip_idx, mcp_idx in [(8, 5), (12, 9), (16, 13), (20, 17)]:
        tip = landmarks.landmark[tip_idx]
        mcp = landmarks.landmark[mcp_idx]
        dist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        dist_mcp = math.hypot(mcp.x - wrist.x, mcp.y - wrist.y)
        # If tip is further from wrist than the MCP by a margin, it's not a fist
        if dist_tip > dist_mcp * 1.3:
            return False
    return True

def is_open_hand(landmarks):
    # Rotation-invariant check: tips must be significantly further from wrist than MCPs
    wrist = landmarks.landmark[0]
    for tip_idx, mcp_idx in [(8, 5), (12, 9), (16, 13), (20, 17)]:
        tip = landmarks.landmark[tip_idx]
        mcp = landmarks.landmark[mcp_idx]
        dist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        dist_mcp = math.hypot(mcp.x - wrist.x, mcp.y - wrist.y)
        # If tip is too close to the palm, hand is not open
        if dist_tip < dist_mcp * 1.4:
            return False
    return True

def draw_wavy_circle(canvas, cx, cy, base_r, amplitude, num_waves, phase, color, width):
    pts = []
    steps = 60
    for i in range(steps + 1):
        theta = i * 2 * math.pi / steps
        # Add wave to the radius
        r = base_r + amplitude * math.sin(num_waves * theta + phase)
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        pts.extend([x, y])
    canvas.create_line(pts, fill=color, width=width, smooth=True, tags="wave")

def animate_orb(canvas, status, t, base_img_orig, icon_anchor):
    global current_orb_photo
    canvas.delete("wave")
    w, h = 200, 200
    cx, cy = w/2, h/2
    
    base_scale = 0.25 # Reduced icon size for better spacing
    
    if status == "Idle":
        scale = base_scale + math.sin(t * 2) * 0.02
        new_w = int(base_img_orig.width * scale)
        new_h = int(base_img_orig.height * scale)
        if new_w > 0 and new_h > 0:
            resized_img = base_img_orig.resize((new_w, new_h), PIL.Image.LANCZOS)
            current_orb_photo = PIL.ImageTk.PhotoImage(resized_img)
            canvas.itemconfig(icon_anchor, image=current_orb_photo)
            
    elif status == "Listening":
        scale = base_scale + math.sin(t * 5) * 0.03
        new_w = int(base_img_orig.width * scale)
        new_h = int(base_img_orig.height * scale)
        if new_w > 0 and new_h > 0:
            resized_img = base_img_orig.resize((new_w, new_h), PIL.Image.LANCZOS)
            current_orb_photo = PIL.ImageTk.PhotoImage(resized_img)
            canvas.itemconfig(icon_anchor, image=current_orb_photo)
            
        # Draw concentric circles with oscillating waves on their circumference
        draw_wavy_circle(canvas, cx, cy, base_r=40, amplitude=5, num_waves=6, phase=t*5, color="#50C878", width=3)  # Emerald inner
        draw_wavy_circle(canvas, cx, cy, base_r=50, amplitude=6, num_waves=8, phase=-t*4, color="#FF7F50", width=2) # Coral outer
            
        canvas.tag_raise(icon_anchor)
        
    elif status == "Thinking":
        scale = base_scale + math.sin(t * 15) * 0.05
        new_w = int(base_img_orig.width * scale)
        new_h = int(base_img_orig.height * scale)
        if new_w > 0 and new_h > 0:
            resized_img = base_img_orig.resize((new_w, new_h), PIL.Image.LANCZOS)
            current_orb_photo = PIL.ImageTk.PhotoImage(resized_img)
            canvas.itemconfig(icon_anchor, image=current_orb_photo)
            
        # Faster, closer coral-only waves for thinking
        draw_wavy_circle(canvas, cx, cy, base_r=40, amplitude=6, num_waves=5, phase=t*10, color="#FF7F50", width=4)
        draw_wavy_circle(canvas, cx, cy, base_r=50, amplitude=7, num_waves=7, phase=-t*12, color="#FF7F50", width=3)
            
        canvas.tag_raise(icon_anchor)
        
    elif status == "Executing":
        scale = base_scale + math.sin(t * 20) * 0.05
        new_w = int(base_img_orig.width * scale)
        new_h = int(base_img_orig.height * scale)
        if new_w > 0 and new_h > 0:
            resized_img = base_img_orig.resize((new_w, new_h), PIL.Image.LANCZOS)
            current_orb_photo = PIL.ImageTk.PhotoImage(resized_img)
            canvas.itemconfig(icon_anchor, image=current_orb_photo)

def main():
    global btn_start_stop, app_running, vision_running
    
    voice_thread = threading.Thread(target=start_voice_assistant, daemon=True)
    voice_thread.start()

    # --- CONTROL PANEL ---
    control_panel = tk.Tk()
    control_panel.title("Agent Control")
    control_panel.geometry("300x150")
    control_panel.configure(bg="#1e1e1e")
    control_panel.protocol("WM_DELETE_WINDOW", on_closing)

    lbl_title = tk.Label(control_panel, text="AI Vision & Voice Agent", fg="white", bg="#1e1e1e", font=("Arial", 14, "bold"))
    lbl_title.pack(pady=15)

    btn_start_stop = tk.Button(control_panel, text="Start Vision", bg="#2ecc71", fg="black", font=("Arial", 12, "bold"), command=toggle_vision, relief="flat", padx=20, pady=5)
    btn_start_stop.pack(pady=10)

    # --- FLOATING ORB HUD ---
    hud = tk.Toplevel(control_panel)
    hud.overrideredirect(True) # Remove window borders
    hud.attributes("-topmost", True) # Always on top
    hud.geometry("200x200+100+100") # 200x200 square, top left of screen
    
    # Windows Transparency Hack: Makes black pixels invisible
    try:
        hud.wm_attributes("-transparentcolor", "black") 
    except Exception:
        pass
    
    orb_canvas = tk.Canvas(hud, width=200, height=200, bg="black", highlightthickness=0)
    orb_canvas.pack()

    # Load the branded asset
    try:
        base_img_orig = PIL.Image.open("ai_orb_base.png")
    except Exception:
        # Fallback if image is missing, just create a solid square to prevent crash
        base_img_orig = PIL.Image.new('RGB', (100, 100), color='white')
        
    base_photo_orig = PIL.ImageTk.PhotoImage(base_img_orig)
    
    # Create a central anchor image for the icon to live in
    icon_anchor = orb_canvas.create_image(100, 100, image=base_photo_orig)

    mouse = MouseController()
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2, 
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    cap = cv2.VideoCapture(0)
    print("[Vision] Pipeline Orchestrator Started.")

    start_time = time.time()

    while app_running:
        t = time.time() - start_time
        status = agent_state.get("status", "Idle")
        
        # Update Orb Animation
        animate_orb(orb_canvas, status, t, base_img_orig, icon_anchor)

        if vision_running:
            success, frame = cap.read()
            if success:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                h, w, _ = frame.shape
                x_min = int(w * mouse.box_x_min_pct)
                y_min = int(h * mouse.box_y_min_pct)
                x_max = int(w * mouse.box_x_max_pct)
                y_max = int(h * mouse.box_y_max_pct)
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                global last_gesture_time, prev_wrist_x, prev_wrist_y, swipe_start_time
                current_time = time.time()

                if results.multi_hand_landmarks and results.multi_handedness:
                    # --- GESTURE 1: DOUBLE FIST -> MINIMIZE ALL (Show Desktop) ---
                    if len(results.multi_hand_landmarks) == 2:
                        hand1 = results.multi_hand_landmarks[0]
                        hand2 = results.multi_hand_landmarks[1]

                        if is_fist(hand1) and is_fist(hand2):
                            if current_time - last_gesture_time > 2.0: # 2-second cooldown
                                print("✊✊ Double Fist Detected! Minimizing all windows.")
                                pyautogui.hotkey('win', 'd')
                                last_gesture_time = current_time

                    # --- GESTURE 2: OPEN HAND SWIPES -> SWITCH APPS & VOLUME ---
                    # Only process swipe if it's a single hand to prevent conflict with the double fist
                    elif len(results.multi_hand_landmarks) == 1:
                        hand = results.multi_hand_landmarks[0]
                        wrist_x = hand.landmark[0].x
                        wrist_y = hand.landmark[0].y

                        if is_open_hand(hand):
                            if prev_wrist_x is None or prev_wrist_y is None:
                                # Initialize anchor
                                prev_wrist_x = wrist_x
                                prev_wrist_y = wrist_y
                                swipe_start_time = current_time
                            else:
                                delta_x = wrist_x - prev_wrist_x
                                delta_y = wrist_y - prev_wrist_y
                                delta_t = current_time - swipe_start_time

                                # Check for a quick rightward swipe (12% of screen within 0.6 seconds)
                                if delta_x > 0.12 and abs(delta_y) < 0.1 and delta_t < 0.6:
                                    if current_time - last_gesture_time > 1.5:
                                        print("✋➡️ Swipe Right Detected! Switching apps forward.")
                                        pyautogui.hotkey('alt', 'tab')
                                        last_gesture_time = current_time
                                        prev_wrist_x = None # reset anchor after successful swipe
                                        prev_wrist_y = None
                                        
                                # Check for a quick leftward swipe (12% of screen within 0.6 seconds)
                                elif delta_x < -0.12 and abs(delta_y) < 0.1 and delta_t < 0.6:
                                    if current_time - last_gesture_time > 1.5:
                                        print("✋⬅️ Swipe Left Detected! Switching apps backward.")
                                        pyautogui.hotkey('alt', 'shift', 'tab')
                                        last_gesture_time = current_time
                                        prev_wrist_x = None # reset anchor after successful swipe
                                        prev_wrist_y = None
                                        
                                # Check for swipe UP (Volume Up)
                                elif delta_y < -0.15 and abs(delta_x) < 0.1 and delta_t < 0.6:
                                    if current_time - last_gesture_time > 0.5:
                                        print("✋⬆️ Swipe Up Detected! Volume Up.")
                                        pyautogui.press('volumeup', presses=5)
                                        last_gesture_time = current_time
                                        prev_wrist_x = None
                                        prev_wrist_y = None
                                        
                                # Check for swipe DOWN (Volume Down)
                                elif delta_y > 0.15 and abs(delta_x) < 0.1 and delta_t < 0.6:
                                    if current_time - last_gesture_time > 0.5:
                                        print("✋⬇️ Swipe Down Detected! Volume Down.")
                                        pyautogui.press('volumedown', presses=5)
                                        last_gesture_time = current_time
                                        prev_wrist_x = None
                                        prev_wrist_y = None
                                
                                # Reset anchor if taking too long
                                elif delta_t > 0.6:
                                    prev_wrist_x = wrist_x
                                    prev_wrist_y = wrist_y
                                    swipe_start_time = current_time
                        else:
                            prev_wrist_x = None # Reset if hand closes
                            prev_wrist_y = None
                            
                    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        hand_label = results.multi_handedness[i].classification[0].label
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        mouse.process_gestures(hand_landmarks, hand_label)
                else:
                    prev_wrist_x = None # Reset tracking if no hands are in frame
                    prev_wrist_y = None

                cv2.imshow('Vision Tracking', frame)
            
            # Handle CV2 Window closing/quitting
            if cv2.waitKey(1) & 0xFF == ord('q'):
                vision_running = False
                btn_start_stop.config(text="Start Vision", bg="#2ecc71", fg="black")
                try:
                    cv2.destroyWindow('Vision Tracking')
                except:
                    pass
        else:
            # If vision is toggled off, close the cv2 window if it exists
            try:
                cv2.destroyWindow('Vision Tracking')
            except Exception:
                pass

        # Update Tkinter Windows
        try:
            control_panel.update_idletasks()
            control_panel.update()
            hud.update_idletasks()
            hud.update()
        except tk.TclError:
            # Occurs if windows are closed
            app_running = False

        # Sleep briefly when vision is off to avoid spiking CPU
        if not vision_running:
            time.sleep(0.03)

    cap.release()
    cv2.destroyAllWindows()
    try:
        control_panel.destroy()
        hud.destroy()
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("🚨 FATAL CRASH REPORT 🚨")
        traceback.print_exc()