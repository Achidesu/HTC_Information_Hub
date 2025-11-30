# main_app.py

import customtkinter as ctk
import tkinter as tk 
from PIL import Image, ImageTk
import threading 
import time 
import os 

# 1. Import config โมดูล (เพื่อใช้ในการกำหนดค่า global)
import config 

# 2. Import Global Variables and Modules
from config import * # นำเข้าตัวแปร global ทั้งหมด
import slide_control   
import mic_control 
import general_ui 

# --- ฟังก์ชันช่วยเหลือในการพิมพ์สถานะ ---
def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")


# --- ฟังก์ชันสลับหน้า ---
def show_frame(frame_to_show):
    """ฟังก์ชันสลับเฟรมที่แสดงบนหน้าจอหลัก (root)"""
    home_content_frame.pack_forget()
    electronics_content_frame.pack_forget()
    navigation_content_frame.pack_forget()
    
    frame_to_show.pack(side="top", fill="both", expand=True)
    
    top_bar.lift()
    try:
        if mic_frame is not None:
            if frame_to_show != navigation_content_frame:
                 mic_frame.lift() 
            else:
                 mic_frame.lower(top_bar) # ซ่อนไมค์เมื่ออยู่หน้าแผนที่
    except NameError:
        pass


# --- ฟังก์ชันควบคุมหน้าต่างนำทาง (Electronics) ---
def show_electronics_page():
    """แสดงเนื้อหาแผนกอิเล็กทรอนิกส์บนหน้าจอหลัก (Full Screen)"""
    # ⚠️ โค้ดนี้ถูกตัดออกเพื่อความกระชับ
    # หากต้องการใช้ฟังก์ชันนี้ ต้องมั่นใจว่า electronics_content_frame ถูกกำหนดค่าใน config.py
    print_status("--- [NAVIGATION]: แสดงหน้าต่างแผนกอิเล็กทรอนิกส์ ---")
    show_frame(electronics_content_frame)

# -----------------------------------------------------------------
# --- MAIN UI SETUP ---
# -----------------------------------------------------------------

def setup_ui():
    """ตั้งค่า UI หลักของแอปพลิเคชัน"""
    # 1. สร้างหน้าต่างหลักและกำหนดค่า root ใน config
    root = ctk.CTk()
    root.title("HTC Smart Hub")
    root.geometry("1080x1920") 
    root.configure(fg_color="white")
    config.root = root 

    # 2. สร้าง Content Frames
    global home_content_frame, electronics_content_frame, navigation_content_frame
    home_content_frame = ctk.CTkFrame(root, fg_color="white")
    electronics_content_frame = ctk.CTkFrame(root, fg_color="white")
    navigation_content_frame = ctk.CTkFrame(root, fg_color="white")
    
    # กำหนดค่า Frame ใน config
    config.home_content_frame = home_content_frame
    config.electronics_content_frame = electronics_content_frame
    config.navigation_content_frame = navigation_content_frame

    # 3. สร้าง UI ส่วน Fixed (Top Bar)
    global top_bar
    top_bar = general_ui.create_top_bar(root)
    config.top_bar = top_bar
    
    # 4. สร้าง UI ส่วน Fixed (Bottom Widgets)
    # ⚠️ ส่งฟังก์ชัน drag/scroll control เข้าไป
    image_slide_canvas = general_ui.create_fixed_bottom_widgets( 
        root, 
        slide_control.start_drag, 
        slide_control.do_drag, 
        slide_control.stop_drag
    )
    config.image_slide_canvas = image_slide_canvas
    
    # 5. สร้าง UI ส่วน Home Content และ Aura (รวมถึง Mic Frame)
    global mic_frame
    (mic_frame, mic_canvas_ref, blinking_dot_ref) = general_ui.create_home_content(
        home_content_frame, 
        mic_control.start_listening_thread
    )
    # กำหนดค่าตัวแปร Global
    config.mic_frame = mic_frame
    config.mic_canvas = mic_canvas_ref
    config.blinking_dot = blinking_dot_ref
    
    # 6. สร้าง UI ภายใน Frames อื่น ๆ (ใช้ show_electronics_page/show_navigation_page)
    general_ui.create_electronics_page_content(electronics_content_frame, show_frame, home_content_frame)
    general_ui.create_navigation_page_content(navigation_content_frame, show_frame, home_content_frame)

    # 7. เริ่มต้น UI: แสดงหน้าหลัก
    show_frame(home_content_frame) 
    
    # 8. เริ่ม Animation
    general_ui.animate_aura()
    general_ui.animate_blinking_dot()

    # 9. เริ่มต้นการโหลดและการสไลด์รูปภาพ
    root.after(100, slide_control.load_slide_images)
    root.after(200, slide_control.animate_image_slide)

    # 10. Start Mainloop
    root.mainloop()

if __name__ == "__main__":
    setup_ui()