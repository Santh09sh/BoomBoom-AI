import nest_asyncio
nest_asyncio.apply()

import os
from dotenv import load_dotenv
load_dotenv()  # Load GOOGLE_API_KEY and any future secrets from .env

import ollama
import json
import os
import pyautogui
import time
import urllib.parse
import screen_brightness_control as sbc
import subprocess
from playwright.sync_api import sync_playwright
class AIAgent:
    def __init__(self):
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_browser_open = False

    def launch_browser(self):
        if not self.is_browser_open:
            self.pw = sync_playwright().start()
            user_data_dir = os.path.join(os.getcwd(), "agent_data")
            self.context = self.pw.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=["--start-maximized"]
            )
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self.is_browser_open = True
            print("🌐 Agent Browser Spawned Persistent Context.")

    def parse_intent(self, voice_text):
        system_prompt = (
            "You are a PC automation routing unit. Translate human speech into a JSON action list.\n"
            "Actions:\n"
            "- 'navigate': URL to open\n"
            "- 'web_search': Search query for youtube or google\n"
            "- 'click': Visible text to click\n"
            "- 'scroll': 'up' or 'down'\n"
            "- 'desktop_macro': Requires 'app', 'contact', and 'message' keys\n"
            "- 'system_command': Used for native OS and hardware controls. Requires a 'command' key. Valid 'command' values MUST be strictly one of the following: 'brightness_up', 'brightness_down', 'volume_up', 'volume_down', 'mute', 'screenshot', 'open_camera', 'zoom_in', 'zoom_out'.\n"
            "- 'chat': Used for casual conversation, greetings, or answering general knowledge questions. The 'parameter' must be the text you want to speak back to the user.\n"
            "Respond ONLY with a valid JSON array of dictionaries. YOU MUST USE THE EXACT KEYS: 'action' and 'parameter'. Do not use the key 'type'. Do not nest inside an 'actions' object. No markdown.\n"
            "UNDER NO CIRCUMSTANCES are you allowed to invent new actions. You MUST use 'system_command' for taking screenshots or changing brightness. Do NOT use 'capture_screenshot'."
        )
        
        try:
            response = ollama.generate(
                model='gemma:2b',
                prompt=f"System: {system_prompt}\nUser Command: {voice_text}\nJSON Output:"
            )
            raw_output = response['response'].strip()
            if raw_output.startswith("```json"): raw_output = raw_output[7:]
            elif raw_output.startswith("```"): raw_output = raw_output[3:]
            if raw_output.endswith("```"): raw_output = raw_output[:-3]
            raw_output = raw_output.strip()
            return json.loads(raw_output)
        except Exception as e:
            print(f"LLM Parsing Error: {e}")
            return []

    def execute_agent_plan(self, voice_text, agent_state=None):
        if agent_state is not None: agent_state["status"] = "Thinking"
        plan = self.parse_intent(voice_text)
        print(f"📋 AI Agent Executing Plan: {plan}")

        if not plan: return
        if isinstance(plan, dict) and "actions" in plan: plan = plan["actions"]
        elif isinstance(plan, dict): plan = [plan]
        if not isinstance(plan, list): return

        if agent_state is not None: agent_state["status"] = "Executing"
        for step in plan:
            action = str(step.get("action") or step.get("type") or step.get("task") or "").lower().strip()
            
            raw_param = step.get("parameter") or step.get("url") or step.get("query") or step.get("text") or step.get("target") or ""
            if isinstance(raw_param, dict):
                raw_param = raw_param.get("url") or raw_param.get("query") or raw_param.get("text") or raw_param.get("target") or raw_param.get("parameter") or str(raw_param)
            param = str(raw_param).strip()

            if action == "desktop_macro":
                try:
                    app_name = step.get("app", "")
                    contact = step.get("contact", "")
                    message = step.get("message", "")
                    
                    print(f"🖥️ Executing Desktop Macro: App={app_name}, Contact={contact}")
                    pyautogui.press('win')
                    time.sleep(0.5)
                    if app_name: pyautogui.write(app_name)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(4.0)
                    
                    if contact:
                        pyautogui.hotkey('ctrl', 'f')
                        time.sleep(0.5)
                        pyautogui.write(contact)
                        time.sleep(1.0)
                        pyautogui.press('enter')
                        time.sleep(0.5)
                    
                    if message:
                        pyautogui.write(message)
                        time.sleep(0.5)
                except Exception as e:
                    print(f"Desktop Macro Error: {e}")

            # Catch hallucinated hardware actions
            if action in ["capture_screenshot", "take_screenshot", "screenshot"]:
                action = "system_command"
                command = "screenshot"
            elif action == "system_command":
                # Dig into the parameter if the LLM nested it as a dictionary
                if isinstance(step.get("parameter"), dict) and "command" in step.get("parameter"):
                    command = step["parameter"].get("command", "").lower()
                else:
                    command = str(step.get("command") or param).lower().strip()
                
                if command == "set_brightness":
                    print(f"☀️ Setting Brightness to {param}%")
                    try: sbc.set_brightness(int(param))
                    except Exception as e: print(f"Brightness error: {e}")
                    
                elif command == "brightness_up":
                    print("☀️ Increasing Brightness")
                    try: sbc.set_brightness('+15')
                    except Exception as e: print(f"Brightness error: {e}")
                    
                elif command == "brightness_down":
                    print("🔅 Decreasing Brightness")
                    try: sbc.set_brightness('-15')
                    except Exception as e: print(f"Brightness error: {e}")
                    
                elif command == "volume_up":
                    print("🔊 Increasing Volume")
                    pyautogui.press('volumeup', presses=5)
                    
                elif command == "volume_down":
                    print("🔉 Decreasing Volume")
                    pyautogui.press('volumedown', presses=5)
                    
                elif command == "mute":
                    print("🔇 Muting Volume")
                    pyautogui.press('volumemute')
                    
                elif command == "screenshot":
                    print("📸 Taking Screenshot")
                    filename = f"screenshot_{int(time.time())}.png"
                    pyautogui.screenshot(filename)
                    print(f"✅ Saved as {filename} in project directory.")
                    
                elif command == "open_camera":
                    print("📷 Opening Windows Camera")
                    subprocess.Popen('start microsoft.windows.camera:', shell=True)
                    
                elif command == "zoom_in":
                    print("🔎 Zooming In")
                    pyautogui.hotkey('win', '+')
                    
                elif command == "zoom_out":
                    print("🔍 Zooming Out")
                    pyautogui.hotkey('win', '-')

            elif action == "chat":
                print(f"🤖 Agent replies: {param}")
                # Run TTS in a completely isolated process to avoid COM locks
                import subprocess
                import sys
                import base64
                
                encoded_text = base64.b64encode(param.encode('utf-8')).decode('utf-8')
                script = f"""
import pyttsx3
import base64
text = base64.b64decode('{encoded_text}').decode('utf-8')
try:
    tts = pyttsx3.init()
    tts.setProperty('rate', 175)
    voices = tts.getProperty('voices')
    for voice in voices:
        if 'Zira' in voice.name or 'female' in voice.name.lower():
            tts.setProperty('voice', voice.id)
            break
    tts.say(text)
    tts.runAndWait()
except Exception as e:
    pass
"""
                subprocess.Popen([sys.executable, '-c', script])

            elif action == "navigate" or action == "maps":
                self.launch_browser()
                param = param.replace("chrome://search?q=", "").replace("chrome://chrome.google.com/search/label/", "").replace("chrome://", "").replace("chrome.url('", "").replace("')", "").strip()
                param = param.replace("chrome.google.com", "www.google.com")
                if "chrome.exe url=" in param: param = param.replace("chrome.exe url=", "").strip("'\"")
                
                if not param:
                    continue

                if param.startswith("http"):
                    url = param
                elif "youtube" in param.lower() and "." not in param:
                    url = "https://www.youtube.com"
                elif "." in param and " " not in param:
                    url = f"https://{param}"
                else:
                    safe_query = urllib.parse.quote(param)
                    url = f"https://www.google.com/search?q={safe_query}"
                
                if "webstore/detail" in url or "chrome-extension" in url:
                    print("⚠️ Intercepted LLM 404 hallucination. Redirecting to Google.")
                    url = "https://www.google.com"
                
                print(f"🌐 Navigating strictly to: {url}")
                try:
                    self.page.goto(url, timeout=15000)
                    self.page.wait_for_timeout(1500)
                except Exception as e:
                    print(f"Playwright Navigation Error: {e}")
                
            elif action == "web_search":
                self.launch_browser()
                query = param.replace("chrome://search?q=", "").replace("chrome://", "").replace("chrome.url('", "").replace("')", "").strip()
                query = query.replace("chrome.google.com", "www.google.com")
                if "chrome.exe url=" in query: query = query.replace("chrome.exe url=", "").strip("'\"")

                if not query:
                    continue

                safe_query = urllib.parse.quote(query)
                if "youtube" in query.lower():
                    clean_query = query.lower().replace("youtube", "").strip()
                    if clean_query:
                        safe_clean_query = urllib.parse.quote(clean_query)
                        url = f"https://www.youtube.com/results?search_query={safe_clean_query}"
                    else:
                        url = "https://www.youtube.com"
                else:
                    url = f"https://www.google.com/search?q={safe_query}"

                print(f"🌐 Web Searching: {url}")
                try:
                    self.page.goto(url, timeout=15000)
                    self.page.wait_for_timeout(1500)
                except Exception as e:
                    print(f"Playwright Web Search Error: {e}")

            elif action == "click" and self.is_browser_open:
                try:
                    print(f"🎯 Agent searching UI elements for text: '{param}'")
                    ordinal_keywords = ["first", "1", "one", "top"]
                    if any(word in param.lower() for word in ordinal_keywords):
                        self.page.locator("h3, #video-title").first.click()
                    elif any(word in param.lower() for word in ["second", "2", "two"]):
                        self.page.locator("h3, #video-title").nth(1).click()
                    elif any(word in param.lower() for word in ["third", "3", "three"]):
                        self.page.locator("h3, #video-title").nth(2).click()
                    else:
                        self.page.locator(f"text={param}").first.click()
                except Exception as e:
                    print(f"Could not click element: {e}")
                    
            elif action == "scroll" and self.is_browser_open:
                try:
                    if param == "down": self.page.mouse.wheel(0, 600)
                    elif param == "up": self.page.mouse.wheel(0, -600)
                except Exception as e:
                    print(f"Playwright Scroll Error: {e}")
        
        if agent_state is not None: agent_state["status"] = "Idle"
