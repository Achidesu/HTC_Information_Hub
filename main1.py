import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps 
import tkinter as tk 
import speech_recognition as sr 
import threading 
import time 
import os 

from test4 import WAYPOINTS_BASIC_SUBJECTS, WAYPOINTS_CONSTRUCTION, WAYPOINTS_ELECTRICAL, WAYPOINTS_ELECTRONICS, WAYPOINTS_INTERIOR_DECORATION, WAYPOINTS_SOUTHERN_CENTER

# --- ตั้งค่า appearance และ theme ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --- สร้างหน้าต่างหลัก ---
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry("1080x1920") 
root.configure(fg_color="white")

# ***************************************************************
# ** Global Variables สำหรับควบคุมสถานะและ UI **
# ***************************************************************
is_blinking_on = True
blinking_dot = None 
is_listening = False 
mic_canvas = None 
aura_circles = [] 
alpha_value = [0.0] 
direction = [1] 

# ** Navigation Variables **
electronics_window = None 
# --- MODIFIED: เพิ่มคำสั่งเสียงทั้งหมดตามคำขอใหม่ ---
KEYWORDS_NAVIGATION = [
    "อิเล็กทรอนิกส์", "อิเล็ก", "อีเล็ก", "แผนกอิเล็ก", "อิเล็กทรอนิก", 
    "ก่อสร้าง", "แผนกก่อสร้าง", "ช่างก่อสร้าง", 
    "ตึก 60 ปี", "60 ปี", 
    "ช่างไฟฟ้า", "ไฟฟ้า", "แผนกไฟฟ้า", 
    "ตกแต่งภายใน", "แผนกตกแต่งภายใน",
    "ตึก 11", # ตึก 11 โดยตรง
    "สารสนเทศ", "ไอที", "IT", "คอมพิวเตอร์" , # สารสนเทศ (เดี่ยวหรือตึก 11)
    "ปิโตรเลียม", "แผนกปิโตรเลียม", 
    # --- NEW KEYWORDS ---
    "ระบบราง", "รถไฟ", 
    "วิชาพื้นฐาน", "พื้นฐาน", "วิชาสามัญ",
    "ศูนย์ส่งเสริม", "อาชีวศึกษาภาคใต้", "ส่งเสริม",
    "สถาปัตยกรรม", "สำรวจ", "ช่างสำรวจ",
    "เครื่องกล", "เครื่องทำความเย็น", "ปรับอากาศ", "แอร์",
    "เทคนิคพื้นฐาน", "พื้นฐานช่าง", 
    "โยธา", "ช่างโยธา", 
    "โรงงาน", "โลจิสติกส์", "พลังงาน", "เชื่อม", "การเชื่อมและผลิต", "โลหะ",
    # --------------------
] 

# ** สำหรับการนำทางเฉพาะ **
NAVIGATION_TRIGGER_IMAGE = "60 ปี.jpg" 
navigation_window = None 
MAX_NAVIGATION_MAP_HEIGHT = 750 
NAVIGATION_DISPLAY_MAP_PATH = "/home/pi/Test_GUI/Tower/1.png"

# *** Global Variables สำหรับ Image Slides ***
IMAGE_SLIDE_FOLDER = "/home/pi/Test_GUI/Picture_slide" 
IMAGE_SLIDE_HEIGHT = 300 
IMAGE_SLIDE_WIDTH_LIMIT = 900 
SLIDE_GAP = 55 
SLIDE_FRAME_WIDTH = 5 
SLIDE_FRAME_COLOR = "black" 
current_slide_index = -1
slide_images = [] 
slide_photo_images = [] 
image_slide_canvas = None 
active_slide_items = []
next_image_x_placement = 1080 
mic_frame = None 

# Variables for manual slide control
last_x = 0
is_dragging = False

# ***************************************************************
# ** NEW/UPDATED: Global Variables สำหรับหน้าแผนกและ Waypoints **
# ***************************************************************
# ปรับให้ใช้ Path เดียวกับแผนผังหลัก
ELECTRONICS_MAP_PATH = "/home/pi/Test_GUI/Tower/1.png" 
# กำหนดขนาดของรูปภาพแผนผังที่คุณส่งมา (1152x648)
MAP_DISPLAY_WIDTH_ELEC = 1152
MAP_DISPLAY_HEIGHT_ELEC = 648

# Path สำหรับรูปภาพแผนกวิชาต่างๆ (เดิม)
ELECTRONICS_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/อิเล็กทรอนิกส์.jpg"
SIXTY_YEARS_DEPT_IMAGE_PATH = os.path.join(IMAGE_SLIDE_FOLDER, NAVIGATION_TRIGGER_IMAGE)
CONSTRUCTION_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/ก่อสร้าง.jpg" 
ELECTRICAL_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/ช่างไฟฟ้า.jpg"
INTERIOR_DECORATION_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/ตกแต่งภายใน.jpg"
TUK11_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/ตึก11.jpg"
IT_DEPT_IMAGE_PATH = TUK11_DEPT_IMAGE_PATH
PETROLEUM_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/ปิโตรเลียม.jpg" 

DEPT_IMAGE_WIDTH = 950 
DEPT_IMAGE_HEIGHT = 400 
FOOTSTEPS_ICON_PATH = "/home/pi/Test_GUI/icons/footsteps.png"


# NEW: Path และ Waypoints สำหรับแผนกใหม่ (ตามคำขอ)

# สถาปัตยกรรม (Architecture) และ ช่างสำรวจ (Surveying) - ตึกเดียวกัน
ARCH_SURVEY_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/สถาปัตยกรรม_สำรวจ.jpg" 
WAYPOINTS_ARCH_SURVEY = [545, 500, 600, 200, 750, 150, 850, 200] # เส้นทางไปทางขวาบน (สมมติ)
# เครื่องกล (Mechanical) และ เครื่องทำความเย็นและปรับอากาศ (Refrigeration) - ตึกเดียวกัน
MECH_REFRIG_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/เครื่องกล_ทำความเย็น.jpg"
WAYPOINTS_MECH_REFRIG = [545, 500, 300, 450, 200, 300, 150, 400] # เส้นทางไปทางซ้ายบน (สมมติ)
# โยธา (Civil Engineering), โรงงาน (Workshop), และ สารสนเทศ (IT) - ตึกเดียวกัน
CIVIL_WORKSHOP_IT_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/โยธา_โรงงาน_สารสนเทศ.jpg"
WAYPOINTS_CIVIL_WORKSHOP_IT = [545, 500, 700, 650, 850, 700, 900, 800] # เส้นทางไปทางขวาล่างไกล (สมมติ)
# โลจิสติกส์ (Logistics), พลังงาน (Energy), และ การเชื่อมและผลิต (Welding) - ตึกเดียวกัน
LOGISTICS_ENERGY_WELDING_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/โลจิสติกส์_พลังงาน_เชื่อม.jpg"
WAYPOINTS_LOGISTICS_ENERGY_WELDING = [545, 500, 500, 750, 400, 800, 200, 900] # เส้นทางไปทางซ้ายล่างไกล (สมมติ)

# แผนกเดี่ยว
RAIL_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/ระบบราง.jpg"
WAYPOINTS_RAIL = [545, 500, 450, 250, 300, 150, 100, 200] 

BASIC_SUBJECTS_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/วิชาพื้นฐาน.jpg"
WAYPOINTS_BASIC_SUBJECTS = [545, 500, 600, 400, 700, 300, 800, 250]

SOUTHERN_CENTER_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/ศูนย์ส่งเสริม.jpg"
WAYPOINTS_SOUTHERN_CENTER = [545, 500, 400, 550, 300, 600, 250, 500]

BASIC_TECH_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/เทคนิคพื้นฐาน.jpg"
WAYPOINTS_BASIC_TECH = [545, 500, 550, 700, 600, 800, 500, 900]

METALWORKING_DEPT_IMAGE_PATH = "/home/pi/Test_GUI/Picture_slide/โลหะ.jpg"
WAYPOINTS_METALWORKING = [545, 500, 650, 500, 750, 400, 850, 350]


# Waypoints constants (เดิม)
WAYPOINTS_ELECTRONICS = [545, 500, 400, 390, 400, 300, 250, 200, 150, 180]
WAYPOINTS_CONSTRUCTION = [545, 500, 700, 450, 800, 550, 950, 520, 900, 400]
WAYPOINTS_ELECTRICAL = [545, 500, 500, 600, 300, 650, 100, 600, 80, 500]
WAYPOINTS_INTERIOR_DECORATION = [545, 500, 750, 400, 850, 250, 700, 150, 600, 200]
WAYPOINTS_TUK11 = [545, 500, 450, 650, 300, 750, 150, 700, 100, 750]
WAYPOINTS_PETROLEUM = [545, 500, 650, 600, 800, 700, 950, 650, 1000, 750]
# ***************************************************************


# ** Global UI Components (ประกาศไว้ด้านบนเพื่อเข้าถึงใน show_frame) **
image_slide_frame = None
survey_frame = None
credit_frame = None
bottom_bar = None
fanpage_ctk_image_global = None 


# --- ฟังก์ชันช่วยเหลือในการพิมพ์สถานะ ---
def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")


# ***************************************************************
# ** NEW: Timer Inactivity Variables **
# ***************************************************************
TIMEOUT_MS = 3 * 60 * 1000  # 3 นาที = 180,000 มิลลิวินาที
inactivity_timer_id = None  # ตัวแปรสำหรับเก็บ ID ของ root.after
# ตัวแปรสำหรับเก็บการผูก Event (เพื่อยกเลิกการผูกเฉพาะที่จำเป็น)
event_key_press_id = None
event_button_1_id = None
# ***************************************************************


# ***************************************************************
# ** NEW: Inactivity Control Functions **
# ***************************************************************

def show_main_screen_ui():
    """ฟังก์ชันสำหรับแสดงหน้าจอหลัก (Home Screen)"""
    # ฟังก์ชัน show_frame ถูกกำหนดไว้ด้านล่าง
    show_frame(home_content_frame) 
    print_status("กลับสู่หน้าหลักแล้ว")

def unbind_inactivity_reset():
    """ยกเลิกการผูก Event และยกเลิก Timer"""
    global inactivity_timer_id, event_key_press_id, event_button_1_id
    
    # 1. ยกเลิก Timer ที่กำลังทำงาน
    if inactivity_timer_id is not None:
        root.after_cancel(inactivity_timer_id)
        inactivity_timer_id = None
    
    # 2. ยกเลิกการผูก Event การโต้ตอบกับหน้าจอหลัก
    if event_key_press_id:
        root.unbind('<KeyPress>', event_key_press_id)
        event_key_press_id = None
    if event_button_1_id:
        root.unbind('<Button-1>', event_button_1_id)
        event_button_1_id = None
    
    print_status("Timer ถูกยกเลิกและ unbound event แล้ว") 


def go_to_main_screen():
    """ฟังก์ชันที่ทำงานเมื่อหมดเวลา 3 นาที หรือเมื่อผู้ใช้คลิกปุ่ม 'กลับหน้าหลัก'"""
    # 1. หยุด Timer และ Event ก่อนกลับ
    unbind_inactivity_reset() 
    
    # 2. สลับไปหน้าหลัก
    show_main_screen_ui() 


def on_inactivity_timeout():
    """ฟังก์ชันที่ถูกเรียกโดย root.after เมื่อครบกำหนด 3 นาที"""
    print_status("ไม่มีการตอบสนองครบ 3 นาที, กำลังกลับสู่หน้าหลัก...")
    go_to_main_screen()


def reset_inactivity_timer(event=None):
    """ยกเลิก Timer เก่าและเริ่ม Timer ใหม่ทุกครั้งที่มีการโต้ตอบ"""
    global inactivity_timer_id
    
    # 1. ยกเลิก Timer เก่า (ถ้ามี)
    if inactivity_timer_id is not None:
        root.after_cancel(inactivity_timer_id)
    
    # 2. เริ่ม Timer ใหม่: เรียก on_inactivity_timeout เมื่อครบเวลา
    inactivity_timer_id = root.after(TIMEOUT_MS, on_inactivity_timeout)
    # print_status("Timer ถูกรีเซ็ต/เริ่มใหม่") # สำหรับ debugging


def bind_inactivity_reset():
    """ผูก Event การโต้ตอบกับหน้าจอเพื่อรีเซ็ต Timer และเริ่ม Timer ครั้งแรก"""
    global event_key_press_id, event_button_1_id
    
    # ตรวจสอบและยกเลิกการผูก/Timer เก่าก่อนเสมอ เพื่อความสะอาด
    unbind_inactivity_reset() 
    
    # ผูกกับ Event การกดปุ่มใดๆ และการคลิกซ้าย
    # ต้องเก็บ ID ที่ root.bind คืนมาเพื่อใช้ในการ unbind
    event_key_press_id = root.bind('<KeyPress>', reset_inactivity_timer)
    event_button_1_id = root.bind('<Button-1>', reset_inactivity_timer)
    
    # เริ่ม Timer ครั้งแรกทันทีที่เข้าหน้าแผนก
    reset_inactivity_timer()
    print_status("Timer Inactivity 3 นาที เริ่มทำงานแล้ว.")

# ***************************************************************


# ***************************************************************
# ** เฟรมสำหรับสลับหน้า (Frame Switching) **
# ***************************************************************
home_content_frame = ctk.CTkFrame(root, fg_color="white")
# ใช้ electronics_content_frame สำหรับการนำทางแบบ Guided ทั้งหมด
electronics_content_frame = ctk.CTkFrame(root, fg_color="white")
# navigation_content_frame จะใช้สำหรับแผนที่ Full Screen แบบเดิม
navigation_content_frame = ctk.CTkFrame(root, fg_color="white")

def show_frame(frame_to_show):
    """ฟังก์ชันสลับเฟรมที่แสดงบนหน้าจอหลัก (root) และจัดการการแสดงผลของส่วนล่าง"""
    global image_slide_frame, survey_frame, credit_frame, bottom_bar
    
    # ซ่อนเฟรมเนื้อหาทั้งหมด
    home_content_frame.pack_forget()
    electronics_content_frame.pack_forget()
    navigation_content_frame.pack_forget()
    
    # -------------------------------------------------------------
    # จัดการการแสดงผลของส่วนล่าง
    # -------------------------------------------------------------
    
    # กำหนดสถานะการแสดงผลส่วนล่างเริ่มต้นเป็นซ่อนทั้งหมด
    should_show_slides = False
    should_show_survey = False
    should_show_credit = False
    
    if frame_to_show == home_content_frame:
        should_show_slides = True
        should_show_survey = True
        should_show_credit = True
        
    elif frame_to_show == electronics_content_frame:
        # หน้าที่มี Guided Map 
        should_show_survey = True
        should_show_credit = True
        
    elif frame_to_show == navigation_content_frame:
        # หน้านำทาง Full Screen (ซ่อนทั้งหมด)
        pass 

    # ทำการ pack/pack_forget ตามสถานะที่กำหนด
    if image_slide_frame:
        if should_show_slides:
            image_slide_frame.pack(side="bottom", fill="x", pady=(0, 0))
        else:
            image_slide_frame.pack_forget()

    if survey_frame:
        if should_show_survey:
            survey_frame.pack(side="bottom", fill="x", pady=(0, 0))
        else:
            survey_frame.pack_forget()

    if credit_frame:
        if should_show_credit:
            credit_frame.pack(side="bottom", fill="x")
        else:
            credit_frame.pack_forget()
            
    if bottom_bar: bottom_bar.pack(side="bottom", fill="x") # Bottom bar แสดงเสมอ
             
    # แสดงเฟรมที่ต้องการ
    frame_to_show.pack(side="top", fill="both", expand=True)
             
    # ยก Top Bar และ Mic Frame ขึ้นมาด้านบนสุดเสมอ
    top_bar.lift()
    try:
        if mic_frame is not None:
            # ไมค์ไม่ควรแสดงบนหน้านำทางที่อาจจะเป็น Full Screen (navigation_content_frame)
            if frame_to_show != navigation_content_frame: 
                 mic_frame.lift() 
            else:
                 mic_frame.lower(top_bar) # ลดระดับ
    except:
        pass


# -----------------------------------------------------------------
# --- NEW/MODIFIED: ฟังก์ชันควบคุมหน้าต่างนำทางแบบมีเส้นทาง (Guided Page) ---
# -----------------------------------------------------------------

def show_guided_page(title, header_bg_color, dept_image_path, waypoints):
    """
    แสดงเนื้อหาแผนก/กิจกรรมแบบมีเส้นทางนำทาง
    :param title: หัวข้อที่จะแสดงบน Header
    :param header_bg_color: สีพื้นหลังของ Header
    :param dept_image_path: Path รูปภาพที่จะแสดงใต้ Header
    :param waypoints: รายการพิกัด [x1, y1, x2, y2, ...] สำหรับวาดเส้นทาง
    """
    global ELECTRONICS_MAP_PATH, MAP_DISPLAY_WIDTH_ELEC, MAP_DISPLAY_HEIGHT_ELEC
    global DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT
    
    # ล้างเนื้อหาเก่า
    for widget in electronics_content_frame.winfo_children():
        widget.destroy()

    # ******************************************************************
    # ** กำหนดพิกัด Start/End จาก Waypoints **
    # ******************************************************************
    
    # ตรวจสอบ Waypoints
    if len(waypoints) < 4:
         print_status("--- [GUIDED PAGE ERROR]: Waypoints ไม่ถูกต้อง ---")
         # สร้างหน้าจอข้อผิดพลาดแทน
         header_frame = ctk.CTkFrame(electronics_content_frame, height=150, fg_color=header_bg_color)
         header_frame.pack(side="top", fill="x")
         ctk.CTkLabel(header_frame, text=title, font=("Kanit", 36, "bold"), text_color="white").pack(pady=(50, 20), padx=20)
         ctk.CTkLabel(electronics_content_frame, text="⚠️ ไม่สามารถสร้างเส้นทางนำทางได้: Waypoints ไม่เพียงพอ ⚠️", font=("Kanit", 24), text_color="red").pack(pady=50)
         ctk.CTkButton(electronics_content_frame, text="❮ กลับสู่หน้าหลัก", command=go_to_main_screen, font=("Kanit", 28, "bold"), fg_color="#00C000", hover_color="#008000", width=250, height=70, corner_radius=15).pack(pady=(20, 40))
         show_frame(electronics_content_frame)
         # NEW: ถ้าเป็นหน้า error ก็ยังคงต้อง unbind timer
         unbind_inactivity_reset() 
         return

    START_X, START_Y = waypoints[0], waypoints[1]
    END_X, END_Y = waypoints[-2], waypoints[-1]
    
    # ***************************************************
    # ** สร้างเนื้อหาสำหรับหน้าแผนก **
    # ***************************************************
    
    # 1. Header 
    header_frame = ctk.CTkFrame(electronics_content_frame, height=150, fg_color=header_bg_color)
    header_frame.pack(side="top", fill="x")
    
    # หัวข้อสีขาว
    ctk.CTkLabel(header_frame, 
                 text=title, # ใช้ Title ที่ส่งเข้ามา
                 font=("Kanit", 36, "bold"),
                 text_color="white").pack(pady=(50, 20), padx=20) 
                 
    # 2. รูปภาพแผนก (จาก Path ที่กำหนด)
    try:
         if os.path.exists(dept_image_path):
             dept_img = Image.open(dept_image_path)
             dept_img_resized = dept_img.resize((DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT), Image.LANCZOS)
             dept_ctk_image = ctk.CTkImage(light_image=dept_img_resized, dark_image=dept_img_resized, size=(DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT))
             
             ctk.CTkLabel(electronics_content_frame, 
                          image=dept_ctk_image, 
                          text="").pack(pady=(20, 10))
         else:
             ctk.CTkLabel(electronics_content_frame, 
                      text=f"[ไม่พบรูปภาพ: {os.path.basename(dept_image_path)}]", 
                      font=("Kanit", 24)).pack(pady=(20, 10))
    except Exception as e:
         print_status(f"ไม่พบรูปภาพแผนก: {e}")
         ctk.CTkLabel(electronics_content_frame, 
                      text="[พื้นที่สำหรับรูปภาพ]", 
                      font=("Kanit", 24)).pack(pady=(20, 10))


    # 3. กรอบสำหรับข้อความนำทาง
    guide_frame = ctk.CTkFrame(electronics_content_frame, fg_color="transparent")
    guide_frame.pack(pady=(10, 5))
        
    # ข้อความนำทาง (สีม่วงเข้ม)
    ctk.CTkLabel(guide_frame, 
                 text="โปรดเดินตามเส้นทางที่กำหนดในแผนผังนี้ (เส้นประสีน้ำเงิน)", 
                 font=("Kanit", 22, "bold"), 
                 text_color="#8000FF").pack(side="left")

    
    # 4. แผนผังการเดิน (Map Image) พร้อมเส้นประ
    try:
        # ใช้ ELECTRONICS_MAP_PATH ซึ่งถูกกำหนดเป็น /home/pi/Test_GUI/Tower/1.png
        map_img = Image.open(ELECTRONICS_MAP_PATH)
        
        # ปรับขนาดรูปภาพตามขนาดจริง (1152x648)
        map_img_resized = map_img.resize((MAP_DISPLAY_WIDTH_ELEC, MAP_DISPLAY_HEIGHT_ELEC), Image.LANCZOS)
        map_tk_img = ImageTk.PhotoImage(map_img_resized) # ใช้ ImageTk.PhotoImage สำหรับ Canvas
        
        # --- ใช้ Tkinter Canvas เพื่อรองรับการวาดเส้น ---
        map_container_frame = ctk.CTkFrame(
            electronics_content_frame, 
            fg_color="white", 
            width=MAP_DISPLAY_WIDTH_ELEC, 
            height=MAP_DISPLAY_HEIGHT_ELEC
        )
        map_container_frame.pack(pady=10)
        
        map_canvas = tk.Canvas(
            map_container_frame,
            width=MAP_DISPLAY_WIDTH_ELEC,
            height=MAP_DISPLAY_HEIGHT_ELEC,
            bg="white",
            highlightthickness=0,
            bd=0
        )
        map_canvas.pack()
        
        # แสดงรูปภาพแผนผังบน Canvas
        map_canvas.create_image(0, 0, image=map_tk_img, anchor="nw")
        map_canvas.image = map_tk_img # เก็บ reference

        
        # ====================================================================
        # ** วาดเส้นประแสดงเส้นทางการเดินแบบหลายจุด (Waypoints) **
        # ====================================================================
        
        map_canvas.create_line(
            *waypoints, # ใช้ Waypoints ที่ส่งเข้ามา
            fill="#0000FF", # สีน้ำเงิน
            width=7,       # เพิ่มความหนาเพื่อให้เห็นชัดขึ้น
            dash=(15, 8),  # กำหนดให้เป็นเส้นประ
            smooth=True    # ทำให้เส้นโค้งมนที่จุดเลี้ยว
        )
        
        # 2. วาดจุดเริ่มต้น (สีเขียว)
        blink_radius = 15 # เพิ่มขนาดเล็กน้อยเพื่อความชัดเจน
        map_canvas.create_oval(
            START_X - blink_radius, START_Y - blink_radius, 
            START_X + blink_radius, START_Y + blink_radius, 
            fill="#00C000", # สีเขียว
            outline="white", 
            width=4
        )
        
        # 3. วาดจุดเป้าหมาย (สีแดง)
        map_canvas.create_oval(
            END_X - blink_radius, END_Y - blink_radius, 
            END_X + blink_radius, END_Y + blink_radius, 
            fill="#FF0000", # สีแดง
            outline="white", 
            width=4
        )
        # ====================================================================

        
        # ข้อความใต้แผนผัง
        ctk.CTkLabel(electronics_content_frame, 
                 text=f"เส้นทางนำทาง: จุดเริ่มต้น (เขียว) ไปยัง {title} (แดง)", 
                 font=("Kanit", 18),
                 text_color="#00AA00").pack(pady=(5, 10))
        
    except FileNotFoundError:
        ctk.CTkLabel(electronics_content_frame, 
                     text=f"⚠️ ไม่พบรูปภาพแผนผัง '{ELECTRONICS_MAP_PATH}' ⚠️", 
                     font=("Kanit", 24),
                     text_color="red").pack(pady=20)
    except Exception as e:
        ctk.CTkLabel(electronics_content_frame, 
                     text=f"⚠️ ข้อผิดพลาดในการโหลดรูปภาพ: {e} ⚠️", 
                     font=("Kanit", 24),
                     text_color="red").pack(pady=20)


    # 5. ปุ่มกลับสู่หน้าหลัก
    ctk.CTkButton(electronics_content_frame, 
                  text="❮ กลับสู่หน้าหลัก", 
                  # MODIFIED: เปลี่ยนเป็นเรียก go_to_main_screen() เพื่อหยุด Timer
                  command=go_to_main_screen, 
                  font=("Kanit", 28, "bold"),
                  fg_color="#00C000",
                  hover_color="#008000",
                  width=250,
                  height=70,
                  corner_radius=15).pack(pady=(20, 40))
                  
    # แสดงเฟรมนี้
    show_frame(electronics_content_frame) 
    
    # NEW: เริ่ม Timer ทันทีที่เข้าหน้าแผนก
    bind_inactivity_reset() 


def show_electronics_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้าแผนกวิชาอิเล็กทรอนิกส์"""
    global WAYPOINTS_ELECTRONICS, ELECTRONICS_DEPT_IMAGE_PATH
    # สีฟ้าอ่อน
    BLUE_BACKGROUND = "#87CEFA" 
    show_guided_page(
        title="แผนกวิชาอิเล็กทรอนิกส์", 
        header_bg_color=BLUE_BACKGROUND, 
        dept_image_path=ELECTRONICS_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_ELECTRONICS
    )

def show_60_years_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้า 60 ปี"""
    global WAYPOINTS_ELECTRONICS, SIXTY_YEARS_DEPT_IMAGE_PATH
    # สีทอง/เหลือง
    GOLD_BACKGROUND = "#FFD700" 
    show_guided_page(
        title="60 ปี วิทยาลัยเทคนิคหาดใหญ่", 
        header_bg_color=GOLD_BACKGROUND, 
        dept_image_path=SIXTY_YEARS_DEPT_IMAGE_PATH, # ใช้รูป 60 ปี.jpg จากโฟลเดอร์สไลด์
        waypoints=WAYPOINTS_ELECTRONICS # ใช้เส้นทางเดียวกับอิเล็กทรอนิกส์ (สมมติ)
    )

def show_construction_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้าแผนกวิชาก่อสร้าง"""
    global WAYPOINTS_CONSTRUCTION, CONSTRUCTION_DEPT_IMAGE_PATH
    # สีส้ม/น้ำตาล สำหรับก่อสร้าง
    ORANGE_BACKGROUND = "#FF8C00" 
    show_guided_page(
        title="แผนกวิชาก่อสร้าง", 
        header_bg_color=ORANGE_BACKGROUND, 
        dept_image_path=CONSTRUCTION_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_CONSTRUCTION
    )

def show_electrical_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้าแผนกวิชาไฟฟ้ากำลัง"""
    global WAYPOINTS_ELECTRICAL, ELECTRICAL_DEPT_IMAGE_PATH
    # สีเหลืองสด สำหรับไฟฟ้า
    YELLOW_BACKGROUND = "#FFD100" 
    show_guided_page(
        title="แผนกวิชาไฟฟ้ากำลัง", 
        header_bg_color=YELLOW_BACKGROUND, 
        dept_image_path=ELECTRICAL_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_ELECTRICAL
    )

def show_interior_decoration_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้าแผนกวิชาตกแต่งภายใน"""
    global WAYPOINTS_INTERIOR_DECORATION, INTERIOR_DECORATION_DEPT_IMAGE_PATH
    # สีน้ำตาลอ่อน/เทา สำหรับตกแต่งภายใน
    BROWN_BACKGROUND = "#A52A2A" 
    show_guided_page(
        title="แผนกวิชาตกแต่งภายใน", 
        header_bg_color=BROWN_BACKGROUND, 
        dept_image_path=INTERIOR_DECORATION_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_INTERIOR_DECORATION
    )

# --- ฟังก์ชัน Wrapper สำหรับหน้าแผนกวิชาสารสนเทศ (ตึก 11) ---
def show_tuk11_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้าตึก 11 และ สารสนเทศ"""
    global WAYPOINTS_TUK11, TUK11_DEPT_IMAGE_PATH
    # สีม่วงอ่อน
    PURPLE_BACKGROUND = "#8A2BE2" 
    show_guided_page(
        title="ตึก 11 (แผนกวิชาสารสนเทศ)", 
        header_bg_color=PURPLE_BACKGROUND, 
        dept_image_path=TUK11_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_TUK11
    )
    
def show_it_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้าแผนกสารสนเทศ (เรียกหน้าเดียวกับตึก 11)"""
    global WAYPOINTS_TUK11, IT_DEPT_IMAGE_PATH 
    # สีน้ำเงินเข้ม
    DARK_BLUE_BACKGROUND = "#483D8B" 
    show_guided_page(
        title="แผนกวิชาสารสนเทศ", 
        header_bg_color=DARK_BLUE_BACKGROUND, 
        dept_image_path=IT_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_TUK11
    )

# --- ฟังก์ชัน Wrapper สำหรับหน้าแผนกวิชาปิโตรเลียม ---
def show_petroleum_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้าแผนกวิชาปิโตรเลียม"""
    global WAYPOINTS_PETROLEUM, PETROLEUM_DEPT_IMAGE_PATH
    # สีเขียวเข้ม สำหรับปิโตรเลียม
    GREEN_BACKGROUND = "#006400" 
    show_guided_page(
        title="แผนกวิชาปิโตรเลียม", 
        header_bg_color=GREEN_BACKGROUND, 
        dept_image_path=PETROLEUM_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_PETROLEUM
    )
    
# ***************************************************************
# --- NEW: ฟังก์ชัน Wrapper สำหรับแผนกใหม่ (ตามคำขอ) ---
# ***************************************************************

# --- ระบบราง ---
def show_rail_page():
    global WAYPOINTS_RAIL, RAIL_DEPT_IMAGE_PATH
    ORANGE_BACKGROUND = "#FF9900" 
    show_guided_page(
        title="แผนกวิชาระบบราง", 
        header_bg_color=ORANGE_BACKGROUND, 
        dept_image_path=RAIL_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_RAIL
    )

# --- วิชาพื้นฐาน ---
def show_basic_subjects_page():
    global WAYPOINTS_BASIC_SUBJECTS, BASIC_SUBJECTS_DEPT_IMAGE_PATH
    TEAL_BACKGROUND = "#008080" 
    show_guided_page(
        title="แผนกวิชาพื้นฐาน (วิชาสามัญ)", 
        header_bg_color=TEAL_BACKGROUND, 
        dept_image_path=BASIC_SUBJECTS_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_BASIC_SUBJECTS
    )

# --- ศูนย์ส่งเสริมและพัฒนาอาชีวศึกษาภาคใต้ ---
def show_southern_center_page():
    global WAYPOINTS_SOUTHERN_CENTER, SOUTHERN_CENTER_IMAGE_PATH
    INDIGO_BACKGROUND = "#4B0082" 
    show_guided_page(
        title="ศูนย์ส่งเสริมและพัฒนาอาชีวศึกษาภาคใต้", 
        header_bg_color=INDIGO_BACKGROUND, 
        dept_image_path=SOUTHERN_CENTER_IMAGE_PATH,
        waypoints=WAYPOINTS_SOUTHERN_CENTER
    )

# --- สถาปัตยกรรม, ช่างสำรวจ (ตึกเดียวกัน) ---
def show_arch_survey_page():
    global WAYPOINTS_ARCH_SURVEY, ARCH_SURVEY_DEPT_IMAGE_PATH
    BROWN_BACKGROUND = "#8B4513" 
    show_guided_page(
        title="แผนกสถาปัตยกรรมและช่างสำรวจ", 
        header_bg_color=BROWN_BACKGROUND, 
        dept_image_path=ARCH_SURVEY_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_ARCH_SURVEY
    )

# --- เครื่องกล, เครื่องทำความเย็น (ตึกเดียวกัน) ---
def show_mech_refrig_page():
    global WAYPOINTS_MECH_REFRIG, MECH_REFRIG_DEPT_IMAGE_PATH
    SILVER_BACKGROUND = "#C0C0C0" 
    show_guided_page(
        title="แผนกเครื่องกลและทำความเย็น", 
        header_bg_color=SILVER_BACKGROUND, 
        dept_image_path=MECH_REFRIG_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_MECH_REFRIG
    )

# --- เทคนิคพื้นฐาน ---
def show_basic_tech_page():
    global WAYPOINTS_BASIC_TECH, BASIC_TECH_DEPT_IMAGE_PATH
    DARK_YELLOW_BACKGROUND = "#B8860B" 
    show_guided_page(
        title="แผนกวิชาเทคนิคพื้นฐาน", 
        header_bg_color=DARK_YELLOW_BACKGROUND, 
        dept_image_path=BASIC_TECH_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_BASIC_TECH
    )

# --- โยธา, โรงงาน, สารสนเทศ (ตึกเดียวกัน) ---
def show_civil_workshop_it_page():
    global WAYPOINTS_CIVIL_WORKSHOP_IT, CIVIL_WORKSHOP_IT_DEPT_IMAGE_PATH
    GRAY_BACKGROUND = "#708090" 
    show_guided_page(
        title="แผนกโยธา (รวมโรงงาน/สารสนเทศ)", 
        header_bg_color=GRAY_BACKGROUND, 
        dept_image_path=CIVIL_WORKSHOP_IT_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_CIVIL_WORKSHOP_IT
    )

# --- โลจิสติกส์, พลังงาน, เชื่อม (ตึกเดียวกัน) ---
def show_logistics_energy_welding_page():
    global WAYPOINTS_LOGISTICS_ENERGY_WELDING, LOGISTICS_ENERGY_WELDING_DEPT_IMAGE_PATH
    RED_ORANGE_BACKGROUND = "#FF4500" 
    show_guided_page(
        title="แผนกโลจิสติกส์ พลังงาน และการเชื่อม", 
        header_bg_color=RED_ORANGE_BACKGROUND, 
        dept_image_path=LOGISTICS_ENERGY_WELDING_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_LOGISTICS_ENERGY_WELDING
    )

# --- โลหะ ---
def show_metalworking_page():
    global WAYPOINTS_METALWORKING, METALWORKING_DEPT_IMAGE_PATH
    BLACK_BACKGROUND = "#222222" 
    show_guided_page(
        title="แผนกวิชาโลหะ", 
        header_bg_color=BLACK_BACKGROUND, 
        dept_image_path=METALWORKING_DEPT_IMAGE_PATH,
        waypoints=WAYPOINTS_METALWORKING
    )

# -----------------------------------------------------------------
    
# -----------------------------------------------------------------
# --- ฟังก์ชันควบคุมหน้าต่างนำทางเฉพาะ (60 ปี.jpg เดิม - ยังคงเก็บไว้) ---
# -----------------------------------------------------------------

def show_navigation_page():
    """
    ฟังก์ชันเดิมสำหรับแสดงแผนผังนำทางแบบ Full Screen
    """
    global NAVIGATION_DISPLAY_MAP_PATH, MAX_NAVIGATION_MAP_HEIGHT
    
    # NEW: หากเข้าหน้า Full Screen Navigation ให้หยุด Timer แผนก
    unbind_inactivity_reset() 
    
    # ... (โค้ดภายในเหมือนเดิม) ...
    for widget in navigation_content_frame.winfo_children():
        widget.destroy()
        
    back_button_frame = ctk.CTkFrame(navigation_content_frame, fg_color="transparent", height=120)
    back_button_frame.pack(side="top", fill="x", pady=(30, 0), padx=40)
    
    # MODIFIED: เปลี่ยนเป็นเรียก go_to_main_screen() เพื่อกลับหน้าหลัก
    ctk.CTkButton(back_button_frame, 
                  text="❮ กลับสู่หน้าหลัก", 
                  command=go_to_main_screen,
                  font=("Kanit", 28, "bold"),
                  fg_color="#2FED39", 
                  hover_color="#555555",
                  text_color="white",
                  width=280,
                  height=70,
                  corner_radius=15).pack(side="left", anchor="nw")
                  
    ctk.CTkLabel(navigation_content_frame, 
                 text="🗺️ แผนผังภายในวิทยาลัย 🗺️", 
                 font=("Kanit", 48, "bold"),
                 text_color="#FF4500").pack(pady=(40, 20))
                 
    map_image_label = ctk.CTkLabel(navigation_content_frame, text="", fg_color="white")
    map_image_label.pack(pady=(0, 0), padx=20, fill="both", expand=True) 
    
    try:
        map_path_to_load = NAVIGATION_DISPLAY_MAP_PATH 
        original_map_img = Image.open(map_path_to_load)
        
        def resize_and_display_map():
            target_width = map_image_label.winfo_width()
            target_height = map_image_label.winfo_height()
            
            if target_width > 0 and target_height > 0:
                original_width, original_height = original_map_img.size
                max_h = min(target_height, MAX_NAVIGATION_MAP_HEIGHT) 
                ratio_w = target_width / original_width
                ratio_h = max_h / original_height
                final_ratio = min(ratio_w, ratio_h)
                new_width = int(original_width * final_ratio)
                new_height = int(original_map_img.height * final_ratio)
                
                if new_width <= 0 or new_height <= 0:
                      root.after(100, resize_and_display_map) 
                      return
                      
                resized_img = original_map_img.resize((new_width, new_height), Image.LANCZOS)
                map_tk_img = ImageTk.PhotoImage(resized_img)
                
                map_image_label.configure(image=map_tk_img, text="")
                map_image_label.image = map_tk_img # Store reference
            else:
                root.after(100, resize_and_display_map)
                
        map_image_label.bind('<Configure>', lambda e: resize_and_display_map())
        
    except FileNotFoundError:
        map_image_label.configure(text=f"ไม่พบไฟล์แผนผัง: {map_path_to_load}", font=("Kanit", 24), text_color="red")
    except Exception as e:
        map_image_label.configure(text=f"ข้อผิดพลาดในการโหลดรูปภาพ: {e}", font=("Kanit", 24), text_color="red")
    
    show_frame(navigation_content_frame)

# -----------------------------------------------------------------
# --- ฟังก์ชันควบคุม Image Slides (Marquee) ---
# -----------------------------------------------------------------

def get_next_slide():
    """คำนวณและคืนค่ารูปภาพสำหรับสไลด์ถัดไป"""
    global current_slide_index, slide_images, slide_photo_images
    if not slide_images:
        return None, None, None, -1
    
    # วนกลับไปที่ภาพแรกเมื่อถึงภาพสุดท้าย
    current_slide_index = (current_slide_index + 1) % len(slide_images)
    image_info = slide_images[current_slide_index]
    image_photo = slide_photo_images[current_slide_index]
    image_width = image_info['width']
    image_filename = image_info['filename']
    
    return image_photo, image_width, image_filename, current_slide_index


def get_previous_slide():
    """คำนวณและคืนค่ารูปภาพสำหรับสไลด์ก่อนหน้า"""
    global current_slide_index, slide_images, slide_photo_images
    if not slide_images:
        return None, None, None, -1
        
    # วนกลับไปที่ภาพสุดท้ายเมื่อถึงภาพแรก
    current_slide_index = (current_slide_index - 1 + len(slide_images)) % len(slide_images)
    image_info = slide_images[current_slide_index]
    image_photo = slide_photo_images[current_slide_index]
    image_width = image_info['width']
    image_filename = image_info['filename']
    
    return image_photo, image_width, image_filename, current_slide_index


def place_next_slide(start_immediately_at_right_edge=True):
    """
    สร้างและวางรูปภาพถัดไปลงบน Canvas ที่ตำแหน่งด้านขวา
    :param start_immediately_at_right_edge: True: วางติดขอบขวาของรูปสุดท้าย, False: วางที่ตำแหน่งเริ่มต้นของ canvas (1080)
    """
    global next_image_x_placement, active_slide_items, image_slide_canvas
    
    image_photo, image_width, image_filename, next_slide_index = get_next_slide()
    
    if image_photo is None:
        return
        
    if start_immediately_at_right_edge and active_slide_items:
        # วางรูปภาพใหม่ต่อจากขอบขวาของรูปภาพสุดท้าย
        prev_right_edge = active_slide_items[-1]['right_edge']
        new_x_center = prev_right_edge + SLIDE_GAP + (image_width / 2)
    else:
        # วางรูปภาพที่ตำแหน่งเริ่มต้นของ Canvas (1080)
        new_x_center = 1080 + SLIDE_GAP + (image_width / 2)
        
    canvas_item_id = image_slide_canvas.create_image(
        new_x_center, 
        IMAGE_SLIDE_HEIGHT // 2, 
        image=image_photo, 
        anchor="center"
    )

    new_item = {
        'id': canvas_item_id,
        'width': image_width,
        'photo': image_photo,
        'right_edge': new_x_center + image_width / 2,
        'slide_index': next_slide_index
    }
    
    active_slide_items.append(new_item)
    
    # 4. Bind event
    # ***************************************************************
    # ** BINDING **
    # ***************************************************************
    # 60 ปี
    if image_filename == NAVIGATION_TRIGGER_IMAGE: # "60 ปี.jpg"
        def handle_60_years_click(event):
            if not is_dragging:
                root.after(0, show_60_years_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_60_years_click)
    # ก่อสร้าง
    elif image_filename == "ก่อสร้าง.jpg":
        def handle_construction_click(event):
            if not is_dragging:
                root.after(0, show_construction_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_construction_click)
    # อิเล็กทรอนิกส์
    elif image_filename == "อิเล็กทรอนิกส์.jpg":
        def handle_electronics_click(event):
            if not is_dragging:
                root.after(0, show_electronics_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_electronics_click)
    # ไฟฟ้ากำลัง
    elif image_filename == "ช่างไฟฟ้า.jpg":
        def handle_electrical_click(event):
            if not is_dragging:
                root.after(0, show_electrical_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_electrical_click)
    # ตกแต่งภายใน
    elif image_filename == "ตกแต่งภายใน.jpg":
        def handle_interior_decoration_click(event):
            if not is_dragging:
                root.after(0, show_interior_decoration_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_interior_decoration_click)
    # ตึก 11 / สารสนเทศ
    elif image_filename == "ตึก11.jpg":
        def handle_tuk11_click(event):
            if not is_dragging:
                root.after(0, show_tuk11_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_tuk11_click)
    # ปิโตรเลียม
    elif image_filename == "ปิโตรเลียม.jpg":
        def handle_petroleum_click(event):
            if not is_dragging:
                root.after(0, show_petroleum_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_petroleum_click)
    # --- NEW: แผนกใหม่ ---
    # ระบบราง
    elif image_filename == "ระบบราง.jpg":
        def handle_rail_click(event):
            if not is_dragging:
                root.after(0, show_rail_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_rail_click)
    # วิชาพื้นฐาน
    elif image_filename == "วิชาพื้นฐาน.jpg":
        def handle_basic_subjects_click(event):
            if not is_dragging:
                root.after(0, show_basic_subjects_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_basic_subjects_click)
    # ศูนย์ส่งเสริมฯ
    elif image_filename == "ศูนย์ส่งเสริม.jpg":
        def handle_southern_center_click(event):
            if not is_dragging:
                root.after(0, show_southern_center_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_southern_center_click)
    # สถาปัตยกรรม/สำรวจ
    elif image_filename == "สถาปัตยกรรม_สำรวจ.jpg":
        def handle_arch_survey_click(event):
            if not is_dragging:
                root.after(0, show_arch_survey_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_arch_survey_click)
    # เครื่องกล/ทำความเย็น
    elif image_filename == "เครื่องกล_ทำความเย็น.jpg":
        def handle_mech_refrig_click(event):
            if not is_dragging:
                root.after(0, show_mech_refrig_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_mech_refrig_click)
    # เทคนิคพื้นฐาน
    elif image_filename == "เทคนิคพื้นฐาน.jpg":
        def handle_basic_tech_click(event):
            if not is_dragging:
                root.after(0, show_basic_tech_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_basic_tech_click)
    # โยธา/โรงงาน/สารสนเทศ
    elif image_filename == "โยธา_โรงงาน_สารสนเทศ.jpg":
        def handle_civil_workshop_it_click(event):
            if not is_dragging:
                root.after(0, show_civil_workshop_it_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_civil_workshop_it_click)
    # โลจิสติกส์/พลังงาน/เชื่อม
    elif image_filename == "โลจิสติกส์_พลังงาน_เชื่อม.jpg":
        def handle_logistics_energy_welding_click(event):
            if not is_dragging:
                root.after(0, show_logistics_energy_welding_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_logistics_energy_welding_click)
    # โลหะ
    elif image_filename == "โลหะ.jpg":
        def handle_metalworking_click(event):
            if not is_dragging:
                root.after(0, show_metalworking_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_metalworking_click)


def place_previous_slide():
    """สร้างและวางรูปภาพก่อนหน้าลงบน Canvas ที่ตำแหน่งด้านซ้าย"""
    global active_slide_items, image_slide_canvas
    
    image_photo, image_width, image_filename, prev_slide_index = get_previous_slide()
    
    if image_photo is None:
        return
        
    # วางรูปภาพใหม่ต่อจากขอบซ้ายของรูปภาพแรก (ที่ active_slide_items[0])
    first_item = active_slide_items[0]
    first_item_left_edge = first_item['right_edge'] - first_item['width']
    
    new_x_center = first_item_left_edge - SLIDE_GAP - (image_width / 2)
        
    canvas_item_id = image_slide_canvas.create_image(
        new_x_center, 
        IMAGE_SLIDE_HEIGHT // 2, 
        image=image_photo, 
        anchor="center"
    )

    new_item = {
        'id': canvas_item_id,
        'width': image_width,
        'photo': image_photo,
        'right_edge': new_x_center + image_width / 2,
        'slide_index': prev_slide_index
    }
    
    active_slide_items.insert(0, new_item) # <-- ใส่ไว้ข้างหน้าสุด
    
    # 6. ผูก Event
    # ***************************************************************
    # ** BINDING **
    # ***************************************************************
    # (Binding code for previous slide is similar to place_next_slide, omitted for brevity)
    # 60 ปี
    if image_filename == NAVIGATION_TRIGGER_IMAGE:
        def handle_60_years_click(event):
            if not is_dragging:
                root.after(0, show_60_years_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_60_years_click)
    # ก่อสร้าง
    elif image_filename == "ก่อสร้าง.jpg":
        def handle_construction_click(event):
            if not is_dragging:
                root.after(0, show_construction_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_construction_click)
    # อิเล็กทรอนิกส์
    elif image_filename == "อิเล็กทรอนิกส์.jpg":
        def handle_electronics_click(event):
            if not is_dragging:
                root.after(0, show_electronics_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_electronics_click)
    # ไฟฟ้ากำลัง
    elif image_filename == "ช่างไฟฟ้า.jpg":
        def handle_electrical_click(event):
            if not is_dragging:
                root.after(0, show_electrical_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_electrical_click)
    # ตกแต่งภายใน
    elif image_filename == "ตกแต่งภายใน.jpg":
        def handle_interior_decoration_click(event):
            if not is_dragging:
                root.after(0, show_interior_decoration_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_interior_decoration_click)
    # ตึก 11 / สารสนเทศ
    elif image_filename == "ตึก11.jpg":
        def handle_tuk11_click(event):
            if not is_dragging:
                root.after(0, show_tuk11_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_tuk11_click)
    # ปิโตรเลียม
    elif image_filename == "ปิโตรเลียม.jpg":
        def handle_petroleum_click(event):
            if not is_dragging:
                root.after(0, show_petroleum_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_petroleum_click)
    # --- NEW: แผนกใหม่ ---
    # ระบบราง
    elif image_filename == "ระบบราง.jpg":
        def handle_rail_click(event):
            if not is_dragging:
                root.after(0, show_rail_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_rail_click)
    # วิชาพื้นฐาน
    elif image_filename == "วิชาพื้นฐาน.jpg":
        def handle_basic_subjects_click(event):
            if not is_dragging:
                root.after(0, show_basic_subjects_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_basic_subjects_click)
    # ศูนย์ส่งเสริมฯ
    elif image_filename == "ศูนย์ส่งเสริม.jpg":
        def handle_southern_center_click(event):
            if not is_dragging:
                root.after(0, show_southern_center_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_southern_center_click)
    # สถาปัตยกรรม/สำรวจ
    elif image_filename == "สถาปัตยกรรม_สำรวจ.jpg":
        def handle_arch_survey_click(event):
            if not is_dragging:
                root.after(0, show_arch_survey_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_arch_survey_click)
    # เครื่องกล/ทำความเย็น
    elif image_filename == "เครื่องกล_ทำความเย็น.jpg":
        def handle_mech_refrig_click(event):
            if not is_dragging:
                root.after(0, show_mech_refrig_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_mech_refrig_click)
    # เทคนิคพื้นฐาน
    elif image_filename == "เทคนิคพื้นฐาน.jpg":
        def handle_basic_tech_click(event):
            if not is_dragging:
                root.after(0, show_basic_tech_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_basic_tech_click)
    # โยธา/โรงงาน/สารสนเทศ
    elif image_filename == "โยธา_โรงงาน_สารสนเทศ.jpg":
        def handle_civil_workshop_it_click(event):
            if not is_dragging:
                root.after(0, show_civil_workshop_it_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_civil_workshop_it_click)
    # โลจิสติกส์/พลังงาน/เชื่อม
    elif image_filename == "โลจิสติกส์_พลังงาน_เชื่อม.jpg":
        def handle_logistics_energy_welding_click(event):
            if not is_dragging:
                root.after(0, show_logistics_energy_welding_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_logistics_energy_welding_click)
    # โลหะ
    elif image_filename == "โลหะ.jpg":
        def handle_metalworking_click(event):
            if not is_dragging:
                root.after(0, show_metalworking_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_metalworking_click)
    
    # 7. ปรับ next_image_x_placement (ใช้สำหรับ animate)
    # next_image_x_placement ถูกใช้สำหรับตำแหน่งเริ่มต้นของรูปภาพที่จะถูกสร้างใน place_next_slide
    # ดังนั้นเมื่อมีการสร้างรูปภาพทางซ้าย เราไม่จำเป็นต้องอัปเดต next_image_x_placement
    

def start_drag(event):
    """เริ่มต้นการลาก"""
    global last_x, is_dragging
    last_x = event.x
    is_dragging = True
    
def do_drag(event):
    """ทำการลาก (เคลื่อนย้าย) องค์ประกอบทั้งหมด"""
    global last_x, image_slide_canvas, active_slide_items
    
    if not is_dragging or not active_slide_items:
        return
        
    # คำนวณระยะการเคลื่อนที่
    move_distance = event.x - last_x
    last_x = event.x
    
    # เคลื่อนย้ายรูปภาพทั้งหมด
    for item in active_slide_items:
        image_slide_canvas.move(item['id'], move_distance, 0)
        item['right_edge'] += move_distance
    
    # ตรวจสอบว่ารูปภาพด้านขวาสุดเริ่มหายไปจากขอบหรือไม่ ถ้าใช่ ให้สร้างรูปภาพถัดไป
    if active_slide_items[-1]['right_edge'] < 1080 + SLIDE_GAP:
        place_next_slide()
        
    # ตรวจสอบว่ารูปภาพด้านซ้ายสุดเข้ามาในขอบหรือไม่ ถ้าใช่ ให้สร้างรูปภาพก่อนหน้า
    first_item = active_slide_items[0]
    first_item_left_edge = first_item['right_edge'] - first_item['width']
    if first_item_left_edge > -100:
        place_previous_slide()
        
    # ลบรูปภาพที่ออกไปจากขอบซ้ายแล้ว
    if active_slide_items[0]['right_edge'] < 0:
        item_to_remove = active_slide_items.pop(0)
        image_slide_canvas.delete(item_to_remove['id'])


def stop_drag(event):
    """สิ้นสุดการลาก"""
    global is_dragging
    is_dragging = False
    # ตรวจสอบว่ารูปภาพด้านขวาถูกลบหมดหรือไม่ ถ้าใช่ ให้เริ่มโหลดใหม่
    if not active_slide_items:
        place_next_slide(start_immediately_at_right_edge=False)
        place_next_slide()

# -----------------------------------------------------------------
# --- ฟังก์ชันสำหรับรูปภาพสไลด์ (Image Marquee) ---
# -----------------------------------------------------------------
def load_slide_images():
    """โหลดรูปภาพทั้งหมดจากโฟลเดอร์ที่กำหนด"""
    global slide_images, slide_photo_images, SLIDE_FRAME_WIDTH, SLIDE_FRAME_COLOR, IMAGE_SLIDE_HEIGHT
    slide_images = []
    slide_photo_images = []
    if not os.path.exists(IMAGE_SLIDE_FOLDER):
        print_status(f"--- [IMAGE SLIDE ERROR]: ไม่พบโฟลเดอร์: {IMAGE_SLIDE_FOLDER} ---")
        return
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    image_files = [f for f in os.listdir(IMAGE_SLIDE_FOLDER) if f.lower().endswith(valid_extensions)]
    image_files.sort()
    if not image_files:
        print_status(f"--- [IMAGE SLIDE]: ไม่พบรูปภาพในโฟลเดอร์: {IMAGE_SLIDE_FOLDER} ---")
        return
    target_image_height = IMAGE_SLIDE_HEIGHT - (SLIDE_FRAME_WIDTH * 2)
    for filename in image_files:
        try:
            filepath = os.path.join(IMAGE_SLIDE_FOLDER, filename)
            img = Image.open(filepath)
            original_width, original_height = img.size
            # --- ปรับขนาดรูปภาพ (ตามความสูง) ---
            if original_height > target_image_height:
                ratio = target_image_height / original_height
                new_width = int(original_width * ratio)
                img = img.resize((new_width, target_image_height), Image.LANCZOS)
            else:
                if original_height < target_image_height:
                    target_image_height = original_height # ใช้ความสูงเดิม
                # ปรับความกว้าง (ถ้าเกิน limit)
                target_image_width_limit = IMAGE_SLIDE_WIDTH_LIMIT - (SLIDE_FRAME_WIDTH * 2)
                if img.width > target_image_width_limit:
                    ratio = target_image_width_limit / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((target_image_width_limit, new_height), Image.LANCZOS)
                    target_image_height = img.height

            # --- เพิ่มกรอบ (Frame) ให้กับรูปภาพ ---
            img = ImageOps.expand(img, border=SLIDE_FRAME_WIDTH, fill=SLIDE_FRAME_COLOR)
            
            slide_images.append({
                'filename': filename,
                'width': img.width,
                'height': img.height
            })
            slide_photo_images.append(ImageTk.PhotoImage(img))
            
        except Exception as e:
            print_status(f"ไม่สามารถโหลดรูปภาพ {filename}: {e}")


def animate_image_slide():
    """เคลื่อนย้ายรูปภาพสไลด์ไปทางซ้ายอย่างต่อเนื่อง"""
    global active_slide_items, next_image_x_placement
    
    # ระยะการเคลื่อนที่ต่อเฟรม
    move_distance = -3
    
    # เคลื่อนย้ายรูปภาพทั้งหมด
    for item in active_slide_items:
        image_slide_canvas.move(item['id'], move_distance, 0)
        item['right_edge'] += move_distance
    
    # อัปเดต next_image_x_placement (ถ้ามี)
    # next_image_x_placement ไม่ถูกใช้ในการสร้างรูปภาพอีกต่อไป แต่ถูกแทนที่ด้วย active_slide_items[-1]['right_edge']
    # ลบโค้ดส่วนนี้ออกเพื่อให้การลาก/ปล่อยทำงานได้ดีขึ้น
    # next_image_x_placement += move_distance 

    # 1. ตรวจสอบและลบรูปภาพที่ออกไปจากขอบซ้ายแล้ว
    if active_slide_items and active_slide_items[0]['right_edge'] < 0:
        item_to_remove = active_slide_items.pop(0)
        image_slide_canvas.delete(item_to_remove['id'])
    
    # 2. ตรวจสอบและสร้างรูปภาพใหม่ที่ขอบขวา
    if active_slide_items and active_slide_items[-1]['right_edge'] < 1080 + SLIDE_GAP:
        place_next_slide()
    
    root.after(25, animate_image_slide) # วนซ้ำทุก 25 มิลลิวินาที

# -------------------------------------------------------------------
# --- การสร้าง UI ที่เป็น Fixed (Top Bar และ Bottom Widgets) ---
# -------------------------------------------------------------------

# --- แถบด้านบนสีม่วง (Fixed บน root) ---
top_bar = ctk.CTkFrame(root, height=150, fg_color="#8000FF")
top_bar.pack(side="top", fill="x")
# โลโก้
try:
    logo_image = Image.open("/home/pi/Test_GUI/logo.png").resize((120, 120))
    logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(120,120))
    logo_label = ctk.CTkLabel(top_bar, image=logo_ctk_image, text="")
    logo_label.pack(side="left", padx=(20,10), pady=15)
except Exception as e:
    print_status(f"ไม่พบไฟล์โลโก้ (logo.png): {e}")
# ข้อความบนแถบ
title_label = ctk.CTkLabel(top_bar, text="HTC Smart Hub", text_color="white", font=("Kanit", 36, "bold"))
title_label.pack(side="left", padx=10, pady=15)


# ***************************************************************
# ** ส่วนของ UI ด้านล่าง (Fixed Bottom Widgets - ต้อง Pack ก่อนส่วนกลาง) **
# ***************************************************************

# --- 4. แถบล่างอีกชั้น (Bottom Bar - ล่างสุดของหน้าจอ) ---
bottom_bar = ctk.CTkFrame(root, height=45, fg_color="#A070FF")
bottom_bar.pack(side="bottom", fill="x")
bottom_label = ctk.CTkLabel(
    bottom_bar, 
    text="© 2025 HatYai Technical College", 
    font=("Arial", 20, "bold"), 
    text_color="white"
)
bottom_label.pack(pady=5)

# --- 3. ข้อความเลื่อนด้านล่าง (Text Marquee) ---
credit_frame = ctk.CTkFrame(root, height=40, fg_color="#5B0094", corner_radius=0)
credit_frame.pack(side="bottom", fill="x")
# (โค้ดสำหรับ Text Marquee ถูกตัดออก)

# --- 2. ส่วนสำรวจและ QR Code ---
survey_frame = ctk.CTkFrame(root, height=180, fg_color="#EFEFEF", corner_radius=0)
survey_frame.pack(side="bottom", fill="x", pady=(0, 0))

inner_survey_frame = ctk.CTkFrame(survey_frame, fg_color="#EFEFEF")
inner_survey_frame.pack(pady=20, padx=20, fill="x")

# ข้อความทางซ้าย
survey_label = ctk.CTkLabel(
    inner_survey_frame, 
    text="โปรดทำแบบสำรวจความพึงพอใจ\nเพื่อนำไปพัฒนาการบริการต่อไป", 
    font=("Kanit", 28, "bold"), 
    text_color="#8000FF"
)
survey_label.pack(side="left", padx=(0, 20), pady=10, anchor="w")

# QR Code
try:
    qr_image = Image.open("/home/pi/Test_GUI/qr_code.png").resize((140, 140))
    qr_ctk_image = ctk.CTkImage(light_image=qr_image, dark_image=qr_image, size=(140, 140))
    qr_label = ctk.CTkLabel(
        inner_survey_frame, 
        image=qr_ctk_image, 
        text="", 
        fg_color="white", 
        corner_radius=10 
    )
    qr_label.pack(side="right", padx=(20, 0))
except Exception as e:
    print_status(f"ไม่พบรูป QR Code: {e}")
    qr_placeholder = ctk.CTkLabel(
        inner_survey_frame, 
        text="QR\nCODE", 
        font=("Arial", 24, "bold"), 
        text_color="#8000FF", 
        fg_color="white", 
        width=140, 
        height=140, 
        corner_radius=10 
    )
    qr_placeholder.pack(side="right", padx=(20, 0))


# --- 1. ส่วนแสดงรูปภาพสไลด์ (Image Marquee) ---
image_slide_frame = ctk.CTkFrame(root, height=IMAGE_SLIDE_HEIGHT, fg_color="#F0F0F0", corner_radius=0)
image_slide_frame.pack(side="bottom", fill="x", pady=(0, 0))

image_slide_canvas = tk.Canvas(
    image_slide_frame, 
    height=IMAGE_SLIDE_HEIGHT, 
    bg="#F0F0F0", 
    highlightthickness=0, 
    bd=0,
)
image_slide_canvas.pack(fill="both", expand=True)

# NEW: ผูก Event สำหรับการลาก (Drag)
image_slide_canvas.bind("<Button-1>", start_drag)
image_slide_canvas.bind("<B1-Motion>", do_drag)
image_slide_canvas.bind("<ButtonRelease-1>", stop_drag)


# -------------------------------------------------------------------
# --- การสร้าง UI ส่วนกลาง (Home Content Frame) ---
# -------------------------------------------------------------------

# === ไอคอนไมค์พร้อมเอฟเฟกต์ออร่า (Fixed บน root) ===
try:
    mic_frame = tk.Frame(root, bg="white", width=120, height=120)
    mic_frame.place(x=920, y=20) 
    mic_frame.lift()
    # (โค้ดสำหรับ Mic Icon และ Aura Effect ถูกตัดออก)
except Exception as e:
    print_status(f"ไม่สามารถสร้าง Mic Frame ได้: {e}")
    mic_frame = None

# === แผนผังในหน้าหลัก (Home Content Frame) ===
# (โค้ดสำหรับแสดงแผนผังในหน้าหลัก ถูกตัดออก)
MAP_WIDTH = 800
MAP_HEIGHT = 400
MAP_Y_POSITION_ON_FRAME = 600
map_canvas_widget = tk.Canvas(
    home_content_frame, 
    width=MAP_WIDTH, 
    height=MAP_HEIGHT, 
    bg="white", 
    highlightthickness=0, 
    bd=0
)
map_canvas_widget.place(x=140, y=MAP_Y_POSITION_ON_FRAME)

try:
    map_image_path = "/home/pi/Test_GUI/map_home.png"
    original_map_img = Image.open(map_image_path)
    map_photo = ImageTk.PhotoImage(original_map_img.resize((MAP_WIDTH, MAP_HEIGHT), Image.LANCZOS))
    map_canvas_widget.create_image(0, 0, image=map_photo, anchor="nw")
    map_canvas_widget.image = map_photo 

    blink_x = 375 
    blink_y = 312 
    blink_radius = 10 
    
    blinking_dot = map_canvas_widget.create_oval(
        blink_x - blink_radius, blink_y - blink_radius,
        blink_x + blink_radius, blink_y + blink_radius,
        fill="#FF3333", 
    )

    def animate_blinking_dot():
        global is_blinking_on 
        global blinking_dot 

        if is_blinking_on:
            map_canvas_widget.itemconfig(blinking_dot, 
                                         fill="#FF3333", 
                                         outline="#FF3333", 
                                         width=2,
                                         state='normal') 
        else:
            map_canvas_widget.itemconfig(blinking_dot, state='hidden') 
            
        is_blinking_on = not is_blinking_on
        root.after(400, animate_blinking_dot) 

    animate_blinking_dot() 

except Exception as e:
    print_status(f"ไม่พบไฟล์รูปแผนผัง หรือเกิดข้อผิดพลาดในการโหลด: {e}")
    blinking_dot = None 


# ***************************************************************
# ** Speech Recognition Functions (ทำงานใน Thread แยก) **
# ***************************************************************
# (โค้ด Speech Recognition ถูกตัดออก)
def listen_for_speech():
    """ฟังก์ชันหลักในการรับเสียงจากไมค์และแปลงเป็นข้อความ พร้อมแก้ปัญหาค้าง"""
    # ... (โค้ด sr.Recognizer() และ sr.Microphone() ถูกตัดออก)
    r = sr.Recognizer() 
    LANGUAGE = "th-TH" 
    global is_listening 
    
    # ... (โค้ด listen_for_speech: ตรวจสอบคำสั่งเสียงและเรียก show_xxx_page) 
    # ** ในส่วนนี้เมื่อมีการตรวจพบคำสั่งให้เรียก show_xxx_page() ซึ่งจะเรียก bind_inactivity_reset() เอง **
    
    is_listening = True
    print_status("--- [MIC STATUS]: โปรดพูดตอนนี้ (Listening...) ---") 
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = r.listen(source, timeout=7, phrase_time_limit=15)
                print_status("--- [MIC STATUS]: ได้รับเสียงแล้ว กำลังประมวลผล... ---")
                text = r.recognize_google(audio, language=LANGUAGE)
                print("\n*** [RECOGNIZED TEXT] ***")
                print(f"ผลลัพธ์: {text}")
                print("***************************\n")
                text_lower = text.lower()
                
                # -------------------------------------------------------
                # การตรวจสอบคำสั่งเสียงและการนำทาง (ตัวอย่าง)
                # -------------------------------------------------------
                
                # 1. ตรวจสอบ "ตึก 11" (เดิม)
                if "ตึก 11" in text_lower: 
                    print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ตึก 11' นำทางไปยังหน้าตึก 11 ---")
                    root.after(0, show_tuk11_page)
                    return
                # 2. ตรวจสอบ "ปิโตรเลียม" (เดิม)
                for keyword in ["ปิโตรเลียม", "แผนกปิโตรเลียม"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกปิโตรเลียม ---")
                        root.after(0, show_petroleum_page)
                        return
                # 3. ตรวจสอบ "ก่อสร้าง" (เดิม)
                for keyword in ["ก่อสร้าง", "แผนกก่อสร้าง", "ช่างก่อสร้าง"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกก่อสร้าง ---")
                        root.after(0, show_construction_page)
                        return
                # 4. ตรวจสอบ "ตึก 60 ปี" (เดิม)
                for keyword in ["ตึก 60 ปี", "60 ปี"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: 'ตึก 60 ปี' นำทางไปยังหน้ากิจกรรม 60 ปี ---")
                        root.after(0, show_60_years_page)
                        return
                # 5. ตรวจสอบ "อิเล็กทรอนิกส์" (เดิม)
                for keyword in ["อิเล็กทรอนิกส์", "อิเล็ก", "อีเล็ก", "แผนกอิเล็ก", "อิเล็กทรอนิก"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกอิเล็กทรอนิกส์ ---")
                        root.after(0, show_electronics_page)
                        return
                # 6. ตรวจสอบ "ไฟฟ้า" (เดิม)
                for keyword in ["ช่างไฟฟ้า", "ไฟฟ้า", "แผนกไฟฟ้า", "ไฟฟ้ากำลัง"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกไฟฟ้ากำลัง ---")
                        root.after(0, show_electrical_page)
                        return
                # 7. ตรวจสอบ "ตกแต่งภายใน" (เดิม)
                for keyword in ["ตกแต่งภายใน", "แผนกตกแต่งภายใน", "ช่างตกแต่งภายใน"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกตกแต่งภายใน ---")
                        root.after(0, show_interior_decoration_page)
                        return
                # 8. ตรวจสอบ "สารสนเทศ" (เดี่ยว)
                for keyword in ["สารสนเทศ", "ไอที", "it", "คอมพิวเตอร์"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกสารสนเทศ (เดี่ยว) ---")
                        root.after(0, show_it_page)
                        return
                
                # --- NEW: 9. ตรวจสอบ ระบบราง --- 
                for keyword in ["ระบบราง", "รถไฟ"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกระบบราง ---")
                        root.after(0, show_rail_page)
                        return
                
                # --- NEW: 10. ตรวจสอบ วิชาพื้นฐาน --- 
                for keyword in ["วิชาพื้นฐาน", "พื้นฐาน", "วิชาสามัญ"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกวิชาพื้นฐาน ---")
                        root.after(0, show_basic_subjects_page)
                        return

                # --- NEW: 11. ตรวจสอบ ศูนย์ส่งเสริม --- 
                for keyword in ["ศูนย์ส่งเสริม", "อาชีวศึกษาภาคใต้", "ส่งเสริม"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าศูนย์ส่งเสริมฯ ---")
                        root.after(0, show_southern_center_page)
                        return

                # --- NEW: 12. ตรวจสอบ สถาปัตยกรรม/สำรวจ --- 
                for keyword in ["สถาปัตยกรรม", "สำรวจ", "ช่างสำรวจ"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกสถาปัตยกรรม/สำรวจ ---")
                        root.after(0, show_arch_survey_page)
                        return
                
                # --- NEW: 13. ตรวจสอบ เครื่องกล/ทำความเย็น --- 
                for keyword in ["เครื่องกล", "เครื่องทำความเย็น", "ปรับอากาศ", "แอร์"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกเครื่องกล/ทำความเย็น ---")
                        root.after(0, show_mech_refrig_page)
                        return
                
                # --- NEW: 14. ตรวจสอบ เทคนิคพื้นฐาน --- 
                for keyword in ["เทคนิคพื้นฐาน", "พื้นฐานช่าง"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกเทคนิคพื้นฐาน ---")
                        root.after(0, show_basic_tech_page)
                        return
                
                # --- NEW: 15. ตรวจสอบ โยธา/โรงงาน/สารสนเทศ (ตึกเดียวกัน) --- 
                for keyword in ["โยธา", "ช่างโยธา", "โรงงาน"]:
                    if keyword in text_lower: 
                        print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'โยธา/โรงงาน/สารสนเทศ' นำทางไปยังหน้าตึกโยธา ---")
                        root.after(0, show_civil_workshop_it_page) 
                        return
                
                # --- NEW: 16. ตรวจสอบ โลจิสติกส์/พลังงาน/เชื่อม --- 
                for keyword in ["โลจิสติกส์", "พลังงาน", "เชื่อม", "การเชื่อมและผลิต"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกโลจิสติกส์/พลังงาน/เชื่อม ---")
                        root.after(0, show_logistics_energy_welding_page)
                        return
                
                # --- NEW: 17. ตรวจสอบ โลหะ --- 
                for keyword in ["โลหะ", "แผนกโลหะ"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกวิชาโลหะ ---")
                        root.after(0, show_metalworking_page)
                        return
                        
                # -------------------------------------------------------

            except sr.WaitTimeoutError:
                print_status("--- [MIC ERROR]: ไม่ได้รับเสียงภายใน 7 วินาที ---")
            except sr.UnknownValueError:
                print_status("--- [MIC ERROR]: ไม่สามารถเข้าใจคำพูด ---")
            except sr.RequestError as e:
                print_status(f"--- [MIC ERROR]: ไม่สามารถเชื่อมต่อกับบริการ Google Speech Recognition ได้: {e} ---")
            except Exception as e:
                print_status(f"--- [MIC ERROR]: ข้อผิดพลาดอื่น ๆ: {e} ---")
            
    except Exception as e:
        print_status(f"--- [MIC ERROR]: ข้อผิดพลาดในการเริ่มต้นไมค์: {e} ---")
    finally:
        is_listening = False
        print_status("--- [MIC STATUS]: หยุดรอรับเสียง ---")
        root.after(0, lambda: stop_aura_animation(True))


def start_listening_thread():
    """เริ่มต้น Thread สำหรับการฟังเสียง"""
    global is_listening
    if not is_listening:
        thread = threading.Thread(target=listen_for_speech)
        thread.daemon = True
        thread.start()
        start_aura_animation()
        
def toggle_mic_click(event):
    """ฟังก์ชันที่ถูกเรียกเมื่อคลิกไอคอนไมค์"""
    start_listening_thread()

# ***************************************************************
# ** Aura Animation Functions (ถูกตัดออก) **
# ***************************************************************
def start_aura_animation():
    pass
def stop_aura_animation(restart_mic_after_delay=False):
    pass
def animate_aura():
    pass

# ***************************************************************
# ** Initialization and Main Loop **
# ***************************************************************

# เริ่มต้นโหลดรูปภาพสไลด์
load_slide_images()

# เริ่มต้นแสดงสไลด์ชุดแรก
if slide_images:
    for _ in range(3): # สร้าง 3-4 สไลด์แรกเพื่อครอบหน้าจอ
        place_next_slide(start_immediately_at_right_edge=False)

# เริ่มต้น Animation
animate_image_slide()


# ผูกไอคอนไมค์กับฟังก์ชันคลิก
try:
    mic_canvas.tag_bind("mic_tag", "<Button-1>", toggle_mic_click)
except:
    pass


# แสดงเฟรมเริ่มต้น (Home)
show_frame(home_content_frame)

# Main Loop
root.mainloop()