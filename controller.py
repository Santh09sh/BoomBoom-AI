import pyautogui
import math
import time

pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Smooth movement variables
        self.prev_x, self.prev_y = 0, 0
        self.smoothing = 0.35
        self.deadzone = 4
        
        # State tracking
        self.is_dragging = False
        self.last_right_click_time = 0
        self.scroll_speed = 30
        self.left_prev_y = 0
        self.left_pinch_start_time = 0
        
        # --- RESOLUTION-INDEPENDENT ACTIVE ZONE ---
        self.box_x_min_pct, self.box_x_max_pct = 0.25, 0.75
        self.box_y_min_pct, self.box_y_max_pct = 0.25, 0.75

    def is_finger_up(self, tip_id, pip_id, landmarks):
        return landmarks.landmark[tip_id].y < landmarks.landmark[pip_id].y

    def spatial_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

    def process_gestures(self, hand_landmarks, mp_label):
        is_physical_right_hand = (mp_label == "Right")
        is_physical_left_hand = (mp_label == "Left")

        # -----------------------------------------------------------------
        # DOMINANT HAND (PHYSICAL RIGHT) -> SMOOTH CURSOR NAVIGATION ONLY
        # -----------------------------------------------------------------
        if is_physical_right_hand:
            # Track Knuckle (Landmark 5: INDEX_FINGER_MCP)
            knuckle = hand_landmarks.landmark[5]
            
            # Constrain to relative bounding box
            clamped_x = max(self.box_x_min_pct, min(knuckle.x, self.box_x_max_pct))
            clamped_y = max(self.box_y_min_pct, min(knuckle.y, self.box_y_max_pct))

            # Normalize to 0.0 -> 1.0 within the zone
            relative_x = (clamped_x - self.box_x_min_pct) / (self.box_x_max_pct - self.box_x_min_pct)
            relative_y = (clamped_y - self.box_y_min_pct) / (self.box_y_max_pct - self.box_y_min_pct)
            
            # Map to screen resolution
            target_x = int(relative_x * self.screen_w)
            target_y = int(relative_y * self.screen_h)

            # Deadzone and EMA Smoothing
            move_distance = math.hypot(target_x - self.prev_x, target_y - self.prev_y)
            if move_distance > self.deadzone:
                curr_x = self.prev_x + (target_x - self.prev_x) * self.smoothing
                curr_y = self.prev_y + (target_y - self.prev_y) * self.smoothing
            else:
                curr_x, curr_y = self.prev_x, self.prev_y

            try:
                pyautogui.moveTo(int(curr_x), int(curr_y))
                self.prev_x, self.prev_y = curr_x, curr_y
            except Exception:
                pass
            return

        # -----------------------------------------------------------------
        # NON-DOMINANT HAND (PHYSICAL LEFT) -> TRIGGER CLICKING & SCROLLING
        # -----------------------------------------------------------------
        if is_physical_left_hand:
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            thumb_tip = hand_landmarks.landmark[4]

            # Read finger extensions
            fingers = [
                self.is_finger_up(8, 6, hand_landmarks),   # Index
                self.is_finger_up(12, 10, hand_landmarks), # Middle
                self.is_finger_up(16, 14, hand_landmarks), # Ring
                self.is_finger_up(20, 18, hand_landmarks)  # Pinky
            ]

            # SCROLL MODE: Index + Middle finger straight up (Ignore pinky for better reliability)
            if fingers[0] and fingers[1] and not fingers[2]:
                # Average index and middle tips for a more stable y-coordinate
                current_y = ((index_tip.y + middle_tip.y) / 2) * self.screen_h
                if self.left_prev_y != 0:
                    delta_y = self.left_prev_y - current_y
                    
                    # Require 12 pixels of movement per scroll notch
                    if abs(delta_y) > 12.0:
                        chunks = int(abs(delta_y) / 12.0)
                        # Windows requires scroll events in multiples of 120 to register reliably
                        scroll_amount = 120 * chunks if delta_y > 0 else -120 * chunks
                        pyautogui.scroll(scroll_amount)
                        print(f"[Action] Scroll {'Up' if delta_y > 0 else 'Down'} ({scroll_amount})")
                        
                        # Update anchor by the amount consumed to preserve remainder
                        if delta_y > 0:
                            self.left_prev_y -= 12.0 * chunks
                        else:
                            self.left_prev_y += 12.0 * chunks
                else:
                    self.left_prev_y = current_y
                return

            self.left_prev_y = 0

            # Reference Normalization for Depth-Independent Gestures
            wrist = hand_landmarks.landmark[0]
            middle_mcp = hand_landmarks.landmark[9]
            # Use 2D distance for stability; z-axis from single camera is too noisy
            ref_length = math.hypot(wrist.x - middle_mcp.x, wrist.y - middle_mcp.y)
            
            raw_idx_dist = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
            raw_mid_dist = math.hypot(middle_tip.x - thumb_tip.x, middle_tip.y - thumb_tip.y)
            
            index_dist = raw_idx_dist / (ref_length + 1e-6)
            middle_dist = raw_mid_dist / (ref_length + 1e-6)

            # Tuned thresholds for higher accuracy and preventing false positives
            is_pinch_index = index_dist < 0.12
            is_pinch_middle = middle_dist < 0.12

            # LEFT CLICK & DRAG (Index pinch must be closer than middle pinch to avoid conflict)
            if is_pinch_index and (index_dist < middle_dist):
                if self.left_pinch_start_time == 0:
                    self.left_pinch_start_time = time.time()
                elif not self.is_dragging and (time.time() - self.left_pinch_start_time > 0.25):
                    pyautogui.mouseDown()
                    self.is_dragging = True
                    print("[Action] Mouse Down (Drag Started)")
            else:
                if self.left_pinch_start_time != 0:
                    pinch_duration = time.time() - self.left_pinch_start_time
                    if self.is_dragging:
                        pyautogui.mouseUp()
                        self.is_dragging = False
                        print("[Action] Mouse Up (Drag Ended)")
                    elif pinch_duration <= 0.25:
                        pyautogui.click()
                        print("[Action] Left Click (Tap)")
                    self.left_pinch_start_time = 0

            # RIGHT CLICK (Middle pinch must be closer than index pinch)
            if is_pinch_middle and (middle_dist < index_dist):
                current_time = time.time()
                if current_time - self.last_right_click_time > 0.8:
                    pyautogui.rightClick()
                    print("[Action] Right Click")
                    self.last_right_click_time = current_time
