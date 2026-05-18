import os
from dotenv import load_dotenv
load_dotenv()  # Load GOOGLE_API_KEY and any future secrets from .env

import speech_recognition as sr
import subprocess
import winsound
import pyperclip
import pyautogui
import pyttsx3
import time
import re
from agent_engine import AIAgent

engine = None

def init_engine():
    global engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    # Set voice to female (Zira)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Zira" in voice.name or "female" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

def speak(text):
    global engine
    if engine is None:
        init_engine()
    print(f"🔊 System Speaks: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️ TTS Error: {e}")
        # Sometimes pyttsx3 gets stuck, re-init might help next time
        engine = None

agent_state = {"status": "Starting..."}
browser_agent = AIAgent()

def execute_command(text):
    global agent_state
    
    text_lower = text.lower().replace("boom boom", "").replace("boomboom", "").strip()
    if not text_lower:
        return False

    # Notepad and Calc
    notepad_commands = ["open notepad", "notepad kholo", "నోట్ప్యాడ్ తెరవండి"]
    calc_commands = ["open calculator", "calculator kholo", "కాల్క్యులేటర్ తెరవండి"]
    
    if any(cmd in text_lower for cmd in notepad_commands):
        agent_state["status"] = "Executing"
        subprocess.Popen(["notepad.exe"])
        agent_state["status"] = "Idle"
        return True
    if any(cmd in text_lower for cmd in calc_commands):
        agent_state["status"] = "Executing"
        subprocess.Popen(["calc.exe"])
        agent_state["status"] = "Idle"
        return True

    # --- 1. HARDWARE SHORT-CIRCUIT (0 LATENCY, NO BROWSER) ---
    if "screenshot" in text_lower:
        speak("Taking a screenshot.")
        browser_agent.execute_agent_plan([{"action": "system_command", "command": "screenshot"}], agent_state)
        return True
        
    # --- VOLUME SHORT-CIRCUIT ---
    if any(w in text_lower for w in ["volume", "sound", "audio"]):
        if any(w in text_lower for w in ["up", "increase", "higher", "max"]):
            speak("Increasing volume.")
            for _ in range(5): pyautogui.press('volumeup') # Press 5 times for a noticeable jump
            return True
        elif any(w in text_lower for w in ["down", "decrease", "lower", "min", "mute"]):
            speak("Decreasing volume.")
            for _ in range(5): pyautogui.press('volumedown')
            return True

    # --- SMART BRIGHTNESS SHORT-CIRCUIT ---
    if "brightness" in text_lower:
        # Check for absolute numbers or max/min
        numbers = re.findall(r'\d+', text_lower)
        level = None
        
        if "max" in text_lower or "full" in text_lower:
            level = 100
        elif "min" in text_lower or "zero" in text_lower:
            level = 0
        elif numbers:
            level = max(0, min(100, int(numbers[0]))) # Clamp between 0 and 100

        if level is not None:
            speak(f"Setting brightness to {level} percent.")
            browser_agent.execute_agent_plan([{"action": "system_command", "command": "set_brightness", "parameter": str(level)}], agent_state)
        elif any(w in text_lower for w in ["up", "increase", "more", "high", "penchu", "badha"]):
            speak("Increasing brightness.")
            browser_agent.execute_agent_plan([{"action": "system_command", "command": "brightness_up"}], agent_state)
        else:
            speak("Decreasing brightness.")
            browser_agent.execute_agent_plan([{"action": "system_command", "command": "brightness_down"}], agent_state)
        return True

    # --- ZOOM SHORT-CIRCUIT ---
    if "zoom in" in text_lower or "make it bigger" in text_lower:
        speak("Zooming in.")
        browser_agent.execute_agent_plan([{"action": "system_command", "command": "zoom_in"}], agent_state)
        return True
    elif "zoom out" in text_lower or "make it smaller" in text_lower:
        speak("Zooming out.")
        browser_agent.execute_agent_plan([{"action": "system_command", "command": "zoom_out"}], agent_state)
        return True

    # --- GHOST READER (CLIPBOARD CONTEXT) ---
    read_triggers = [
        "read this", "summarize this", "explain this", "explain it to me", "explain this to me", 
        "is padho", "ise samjhao", "ise summarize karo", 
        "idi chaduvu", "idi vivarinchu", "deenni summarize chey" 
    ]
    
    if any(trigger in text_lower for trigger in read_triggers):
        try:
            set_orb_state("thinking")
        except NameError:
            pass 
            
        speak("Analyzing.")
        
        # 1. THE RETRY LOOP (Mechanical Accuracy)
        # The OS sometimes drops hotkeys under heavy CPU load. We try up to 3 times.
        clipboard_text = ""
        for attempt in range(3):
            pyperclip.copy('') # Clear the buffer
            time.sleep(0.1)
            
            # Fire the copy command
            pyautogui.keyDown('ctrl')
            pyautogui.press('c')
            pyautogui.keyUp('ctrl')
            
            time.sleep(0.5) # Wait for OS to register
            
            text = pyperclip.paste().strip()
            if text:
                clipboard_text = text
                break # Success, break the loop
                
        # 2. FAILURE HANDLING
        if not clipboard_text:
            speak("Capture failed. Please ensure the text is highlighted and the window is active.")
            try:
                set_orb_state("idle")
            except NameError:
                pass
            return True
            
        # 3. HIGH-ACCURACY PROMPT INJECTION (Negative Constraints & Analogy)
        print(f"📄 Ghost Reader successfully extracted: {clipboard_text[:60]}...")
        
        prompt = (
            f"Act as an expert teacher. The user needs an explanation of this exact text:\n\n"
            f"\"{clipboard_text}\"\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. DO NOT just read or repeat the text back to the user.\n"
            f"2. You MUST explain the core concept in your own words.\n"
            f"3. Use a simple analogy if possible to make it easy to understand.\n"
            f"4. You MUST respond ONLY with a valid JSON array using the 'chat' action.\n"
            f"5. DO NOT use any double quotes (\") inside your explanation string. Use single quotes (') instead if needed to prevent breaking the JSON.\n\n"
            f"Example format: [{{\"action\": \"chat\", \"parameter\": \"Basically, this means... [your explanation]\"}}]"
        )
        
        browser_agent.execute_agent_plan(prompt) 
        return True

    # --- 2. WEB SEARCH SHORT-CIRCUIT (FIXES 404 HALLUCINATIONS) ---
    if "search for" in text_lower or "search" in text_lower:
        # Extract the exact search query
        if "search for" in text_lower:
            query = text_lower.split("search for")[-1].strip()
        else:
            query = text_lower.split("search")[-1].strip()
            
        # Clean up stray words like "in chrome" or "on google"
        query = query.replace("in chrome", "").replace("on google", "").replace("in youtube", "").strip()
        
        if query:
            platform = "youtube" if "youtube" in text_lower else "google"
            browser_agent.execute_agent_plan([{"action": "web_search", "platform": platform, "query": query}], agent_state)
            return True

    # --- 3. FALLBACK TO LLM ---
    # Only run Gemma if it's a complex command (like WhatsApp or specific URL navigation)
    print(f"🤖 Routing to LLM: {text_lower}")

    # Inject strict conversational context
    llm_prompt = (
        f"The user said: '{text_lower}'. "
        "If this is a casual greeting, a general question, or a request to talk, use the 'chat' action to reply. "
        "DO NOT use 'web_search' unless the user explicitly asks you to search the internet or look something up."
    )

    browser_agent.execute_agent_plan(llm_prompt, agent_state)
    return True

def run_assistant():
    global agent_state
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("[Voice] Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("[Voice] Engine Online. Listening for commands...")
        agent_state["status"] = "Idle"
        
        while True:
            try:
                agent_state["status"] = "Listening"
                # timeout=5 forces it to give up if no one speaks, preventing thread lock
                # phrase_time_limit=8 stops it from listening forever if background noise is constant
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
                agent_state["status"] = "Thinking"
                
                languages = ['en-IN', 'te-IN', 'hi-IN']
                parsed = False
                for lang in languages:
                    try:
                        recognized_text = recognizer.recognize_google(audio, language=lang)
                        if recognized_text:
                            print(f"\n[🎙️ {lang}] Heard: '{recognized_text}'")
                            clean_lower = recognized_text.lower()
                            if "boom boom" in clean_lower or "boomboom" in clean_lower:
                                winsound.Beep(500, 200)
                                clean_text = clean_lower.replace("boom boom", "").replace("boomboom", "").strip()
                                if clean_text:
                                    if execute_command(clean_text):
                                        print(f"[⚙️] Executing command via Agent...")
                                    else:
                                        print(f"[⚠️] Ignored: No valid trigger keywords found in phrase.")
                                else:
                                    print(f"[⚠️] Ignored: Empty command after wake word.")
                            else:
                                print(f"[⚠️] Ignored: Wake word not detected.")
                            parsed = True
                            break
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        print(f"[Voice] Google API Error: {e}")
                        break
                
                if not parsed:
                    agent_state["status"] = "Idle"
            except sr.WaitTimeoutError:
                # Normal behavior when room is quiet. Just loop and listen again.
                agent_state["status"] = "Idle"
                continue
            except Exception as e:
                print(f"⚠️ Microphone capture error: {e}")
                agent_state["status"] = "Idle"
                continue

def start_voice_assistant():
    run_assistant()
