# mic_control.py

import speech_recognition as sr 
import threading 
import time

# นำเข้าตัวแปร Global
from config import * # --- ฟังก์ชันช่วยเหลือในการพิมพ์สถานะ (จำเป็นต้องมีในทุกไฟล์) ---
def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

# -----------------------------------------------------------------
# --- ฟังก์ชัน Speech Recognition (ทำงานใน Thread แยก) ---
# -----------------------------------------------------------------

def listen_for_speech():
    """ฟังก์ชันหลักในการรับเสียงจากไมค์และแปลงเป็นข้อความ"""
    global is_listening
    # Import main_app locally เพื่อเข้าถึง show_electronics_page
    try:
        import main_app
        show_electronics_page = main_app.show_electronics_page
    except ImportError:
        print_status("--- [MIC ERROR]: ไม่สามารถโหลด main_app functions ได้ ---\n")
        is_listening = False
        return

    r = sr.Recognizer()
    LANGUAGE = "th-TH" 

    is_listening = True 
    print_status("--- [MIC STATUS]: โปรดพูดตอนนี้ (Listening...) ---")
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.8) 
        
        try:
            audio = r.listen(source, timeout=7, phrase_time_limit=15)
            print_status("--- [MIC STATUS]: ได้รับเสียงแล้ว กำลังประมวลผล... ---")
            
            text = r.recognize_google(audio, language=LANGUAGE) 
            
            print("\n*** [RECOGNIZED TEXT] ***")
            print(f"ผลลัพธ์: {text}")
            print("***************************\n")
            
            found_command = False
            for keyword in KEYWORDS_ELECTRONICS:
                if keyword in text.lower(): # ใช้อักษรเล็กทั้งหมดเพื่อตรวจสอบที่ง่ายขึ้น
                    found_command = True
                    break 
            if found_command:
                print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกอิเล็กทรอนิกส์ ---")
                if root:
                    root.after(0, show_electronics_page) # สลับหน้าใน Main Thread
            
        except sr.WaitTimeoutError:
            print_status("--- [MIC ERROR]: ไม่ได้รับเสียงภายใน 7 วินาที ---\n")
        except sr.UnknownValueError:
            print_status("--- [MIC ERROR]: ไม่สามารถเข้าใจคำพูด (UnknownValueError) ---\n")
        except sr.RequestError as e:
            print_status(f"--- [MIC ERROR]: ไม่สามารถเชื่อมต่อกับ Google Speech (ตรวจสอบอินเทอร์เน็ต); {e} ---\n")
        except Exception as e:
            print_status(f"--- [MIC ERROR]: เกิดข้อผิดพลาดในการประมวลผล: {e} ---\n") 
            
    is_listening = False
    print_status("--- [MIC STATUS]: การฟังเสร็จสิ้น (IDLE) ---")


def start_listening_thread(event):
    """ฟังก์ชันสำหรับเริ่มต้นการฟังใน Thread แยก เพื่อไม่ให้ GUI ค้าง"""
    global is_listening
    if not is_listening:
        threading.Thread(target=listen_for_speech, daemon=True).start()
    else:
        print_status("--- [SYSTEM]: ระบบกำลังฟังอยู่ กรุณารอสักครู่ ---")