import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps 
import tkinter as tk 
import speech_recognition as sr 
import threading 
import time 
import os
# --- NEW: Import tkvideo for playing looped video (Requires 'pip install tkvideo') ---
try:
    import tkvideo 
except ImportError:
    print("WARNING: tkvideo library not found. Video playback will be disabled. Install with 'pip install tkvideo'")
    tkvideo = None


# ต้องกำหนดค่าของ DEPT_IMAGE_PATH_BASE ก่อนการใช้งาน เช่น:
# from test3 import DEPT_IMAGE_PATH_BASE 
# หากไม่ต้องการใช้ไฟล์ test3 ให้กำหนดค่านี้โดยตรง
try:
    from test3 import DEPT_IMAGE_PATH_BASE 
except ImportError:
    # หากไม่พบ test3.py ให้กำหนดพาธฐานของรูปภาพเอง
    DEPT_IMAGE_PATH_BASE = "/home/pi/Test_GUI/images/department/" 


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

# ** Navigation Variables ** electronics_window = None 

# --- MODIFIED: เพิ่มคำสั่งเสียงทั้งหมดตามคำขอใหม่ (Keywords Remains the Same) ---
KEYWORDS_ELECTRONICS = ["อิเล็กทรอนิกส์", "อิเล็ก", "อีเล็ก", "แผนกอิเล็ก", "อิเล็กทรอนิก"] 
KEYWORDS_CONSTRUCTION = ["ช่างก่อสร้าง", "ก่อสร้าง"]
KEYWORDS_CIVIL = ["ช่างโยธา", "โยธา"]
KEYWORDS_FURNITURE = ["ช่างเฟอร์นิเจอร์", "ตกแต่งภายใน", "เฟอร์นิเจอร์"]
KEYWORDS_SURVEY = ["ช่างสำรวจ", "สำรวจ"]
KEYWORDS_ARCHITECT = ["สถาปัตยกรรม", "สถาปัตย์"]
KEYWORDS_AUTO = ["ช่างยนต์", "ยนต์"]
KEYWORDS_FACTORY = ["ช่างกลโรงงาน", "กลโรงงาน"]
KEYWORDS_WELDING = ["ช่างเชื่อมโลหะ", "เชื่อมโลหะ", "เชื่อม"]
KEYWORDS_BASICTECH = ["ช่างเทคนิคพื้นฐาน", "เทคนิคพื้นฐาน"]
KEYWORDS_ELECTRIC = ["ช่างไฟฟ้า", "ไฟฟ้า"]
KEYWORDS_AIRCOND = ["เครื่องทำความเย็น", "ปรับอากาศ", "แอร์", "ระบบความเย็น"]
KEYWORDS_IT = ["เทคโนโลยีสารสนเทศ", "ไอที", "สารสนเทศ", "it"]
KEYWORDS_PETROLEUM = ["เทคโนโลยีปิโตรเลียม", "ปิโตรเลียม"]
KEYWORDS_ENERGY = ["เทคนิคพลังงาน", "พลังงาน"]
KEYWORDS_LOGISTICS = ["โลจิสติกส์", "ซัพพลายเชน", "logistics"]
KEYWORDS_RAIL = ["ระบบขนส่งทางราง", "ขนส่งทางราง", "ราง"]
KEYWORDS_MECHATRONICS = ["เมคคาทรอนิกส์", "หุ่นยนต์", "เมคคา", "หุ่นยนต์", "แม็กคา", "แม็คคา", "แมคคา","แมกคา","แม็กคา", "mechatronics"]
KEYWORDS_AIRLINE = ["แผนกการบิน", "การบิน", "aviation"]
KEYWORDS_COMPUTER_TECH = ["เทคโนโลยีคอมพิวเตอร์", "เทคโนโลยีคอม", "คอมพิวเตอร์", "คอมพิว"]
# --------------------

# ** สำหรับการนำทางเฉพาะ **
NAVIGATION_TRIGGER_IMAGE = "60 ปี.jpg" 
navigation_window = None 
MAX_NAVIGATION_MAP_HEIGHT = 750 
NAVIGATION_DISPLAY_MAP_PATH = "/home/pi/Test_GUI/Tower/1.png"
 
# *** NEW: Global Variable สำหรับ Video Path ***
VIDEO_PATH_BASE = "/home/pi/Test_GUI/videos/" 

# --- UPDATED: DEPARTMENTS_CONFIG ใช้ชื่อไฟล์รูปภาพและวิดีโอใหม่ทั้งหมด ---
# โครงสร้างใหม่: (main_image_filename, video_filename, w1, w2, image_full_path_for_dept_page, color)
# **หมายเหตุ:** image_full_path_for_dept_page อ้างอิงจาก IMAGE_SLIDE_FOLDER
DEPARTMENTS_CONFIG = {
    # แผนกวิชา:                               (รูปภาพ,         วิดีโอ,     w1,  w2, image_full_path,                                                              color)
    "แผนกวิชาช่างอิเล็กทรอนิกส์":              ("B8.jpg",      "z11.mp4", 160, 4, os.path.join(DEPT_IMAGE_PATH_BASE, "B8.jpg"),                       "#87CEFA"),
    "แผนกวิชาช่างก่อสร้าง":                   ("B11.jpg",     "z4.mp4",  120, 3, os.path.join(DEPT_IMAGE_PATH_BASE, "B11.jpg"),                       "#FF8C00"), # DarkOrange
    "แผนกวิชาช่างโยธา":                       ("B9.jpg",      "z4.mp4",  150, 4, os.path.join(DEPT_IMAGE_PATH_BASE, "B9.jpg"),                        "#A52A2A"), # Brown
    "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน":  ("B12.jpg",     "z13.mp4", 180, 5, os.path.join(DEPT_IMAGE_PATH_BASE, "B12.jpg"),                       "#D2691E"), # Chocolate
    "แผนกวิชาช่างสำรวจ":                      ("B6.jpg",      "z6.mp4",  200, 6, os.path.join(DEPT_IMAGE_PATH_BASE, "B6.jpg"),                        "#556B2F"), # DarkOliveGreen
    "แผนกวิชาสถาปัตยกรรม":                     ("B6.jpg",      "z6.mp4",  200, 6, os.path.join(DEPT_IMAGE_PATH_BASE, "B6.jpg"),                        "#708090"), # SlateGray
    "แผนกวิชาช่างยนต์":                        ("B15.jpg",     "z8.mp4",  100, 3, os.path.join(DEPT_IMAGE_PATH_BASE, "B15.jpg"),                       "#DC143C"), # Crimson
    "แผนกวิชาช่างกลโรงงาน":                    ("B16.jpg",     "z9.mp4",  90, 2, os.path.join(DEPT_IMAGE_PATH_BASE, "B16.jpg"),                       "#4682B4"), # SteelBlue
    "แผนกวิชาช่างเชื่อมโลหะ":                  ("B17.jpg",     "z7.mp4",  110, 3, os.path.join(DEPT_IMAGE_PATH_BASE, "B17.jpg"),                       "#FF4500"), # OrangeRed
    "แผนกวิชาช่างเทคนิคพื้นฐาน":               ("B1.jpg",      "z1.mp4",  130, 3, os.path.join(DEPT_IMAGE_PATH_BASE, "B1.jpg"),                        "#BDB76B"), # DarkKhaki
    "แผนกวิชาช่างไฟฟ้า":                       ("B10.jpg",     "z4.mp4",  140, 4, os.path.join(DEPT_IMAGE_PATH_BASE, "B10.jpg"),                       "#FFD700"), # Gold
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ":  ("B2.jpg",      "z3.mp4",  180, 5, os.path.join(DEPT_IMAGE_PATH_BASE, "B2.jpg"),                        "#00BFFF"), # DeepSkyBlue
    "แผนกวิชาเทคโนโลยีสารสนเทศ":               ("B13.jpg",     "z9.mp4",  170, 4, os.path.join(DEPT_IMAGE_PATH_BASE, "B13.jpg"),                       "#9370DB"), # MediumPurple
    "แผนกวิชาเทคโนโลยีปิโตรเลียม":             ("B88.jpg",     "z2.mp4",  190, 5, os.path.join(DEPT_IMAGE_PATH_BASE, "B88.jpg"),                       "#32CD32"), # LimeGreen
    "แผนกวิชาเทคนิคพลังงาน":                   ("B3.jpg",      "z5.mp4",  200, 6, os.path.join(DEPT_IMAGE_PATH_BASE, "B3.jpg"),                        "#3CB371"), # MediumSeaGreen
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน":  ("s15.jpeg",    "z12.mp4", 160, 4, os.path.join(DEPT_IMAGE_PATH_BASE, "s15.jpeg"),                      "#20B2AA"), # LightSeaGreen
    # Note: user provided "z.mp4" for rail, using "z14.mp4" as placeholder to keep pattern
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง":     ("B14.jpg",     "z14.mp4", 210, 6, os.path.join(DEPT_IMAGE_PATH_BASE, "B14.jpg"),                       "#6A5ACD"), # SlateBlue
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์":        ("B3.jpg",      "z5.mp4",  200, 5, os.path.join(DEPT_IMAGE_PATH_BASE, "B3.jpg"),                        "#BA55D3"), # MediumOrchid
    "แผนกวิชาแผนกการบิน":                      ("s15.jpeg",    "z12.mp4", 160, 4, os.path.join(DEPT_IMAGE_PATH_BASE, "s15.jpeg"),                      "#4169E1"), # RoyalBlue
    "แผนกวิชาเทคโนโลยีคอมพิวเตอร์":            ("w11.jpg",     "z10.mp4", 180, 2, os.path.join(DEPT_IMAGE_PATH_BASE, "w11.jpg"),                       "#8A2BE2") # BlueViolet
}

# -------------------- (Global Variables for Image Slides and Waypoints) --------------------
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
# ** Global Variables สำหรับหน้าแผนกและ Waypoints **
# ***************************************************************
# ปรับให้ใช้ Path เดียวกับแผนผังหลัก
ELECTRONICS_MAP_PATH = "/home/pi/Test_GUI/Tower/1.png" 
# กำหนดขนาดของรูปภาพแผนผังที่คุณส่งมา (1152x648)
MAP_DISPLAY_WIDTH_ELEC = 1152
MAP_DISPLAY_HEIGHT_ELEC = 648

# Path สำหรับรูปภาพแผนกวิชาต่างๆ (ใช้ชื่อไฟล์ใหม่ BXX.jpg)
# (Path ที่เหลือใช้ os.path.join(IMAGE_SLIDE_FOLDER, 'ชื่อไฟล์') ซึ่งจะถูกสร้างใน DEPARTMENTS_CONFIG)
DEPT_IMAGE_WIDTH = 950 
DEPT_IMAGE_HEIGHT = 400 
FOOTSTEPS_ICON_PATH = "/home/pi/Test_GUI/icons/footsteps.png"


# Waypoints constants (เดิมและใหม่) - ใช้จุด (545, 500) เป็นจุดเริ่มต้น
WAYPOINTS_ELECTRONICS = [545, 500, 400, 390, 400, 300, 250, 200, 150, 180]
WAYPOINTS_CONSTRUCTION = [545, 500, 700, 450, 800, 550, 950, 520, 900, 400]
WAYPOINTS_ELECTRICAL = [545, 500, 500, 600, 300, 650, 100, 600, 80, 500]
WAYPOINTS_INTERIOR_DECORATION = [545, 500, 750, 400, 850, 250, 700, 150, 600, 200]
WAYPOINTS_TUK11 = [545, 500, 450, 650, 300, 750, 150, 700, 100, 750]
WAYPOINTS_PETROLEUM = [545, 500, 650, 600, 800, 700, 950, 650, 1000, 750]

# --- NEW WAYPOINTS FOR REMAINING DEPARTMENTS (SMOOTH PATHS) ---
WAYPOINTS_CIVIL = [545, 500, 700, 480, 850, 520, 900, 600] # ช่างโยธา
WAYPOINTS_FURNITURE = [545, 500, 750, 380, 880, 200, 720, 100] # ช่างเฟอร์นิเจอร์และตกแต่งภายใน
WAYPOINTS_SURVEY = [545, 500, 600, 350, 480, 200, 350, 180] # ช่างสำรวจ
WAYPOINTS_ARCHITECT = [545, 500, 400, 300, 250, 250, 100, 300] # สถาปัตยกรรม
WAYPOINTS_AUTO = [545, 500, 350, 550, 200, 620, 150, 700] # ช่างยนต์
WAYPOINTS_FACTORY = [545, 500, 700, 650, 850, 700, 950, 800] # ช่างกลโรงงาน
WAYPOINTS_WELDING = [545, 500, 550, 750, 400, 800, 200, 900] # ช่างเชื่อมโลหะ
WAYPOINTS_BASICTECH = [545, 500, 600, 400, 700, 300, 800, 250] # ช่างเทคนิคพื้นฐาน
WAYPOINTS_AIRCOND = [545, 500, 300, 450, 200, 300, 150, 400] # เครื่องทำความเย็นและปรับอากาศ
WAYPOINTS_IT = [545, 500, 450, 650, 300, 750, 150, 700, 100, 750] # เทคโนโลยีสารสนเทศ (ใช้ Waypoint ร่วมกับ ตึก11/เดิม)
WAYPOINTS_ENERGY = [545, 500, 400, 700, 250, 800, 100, 850] # เทคนิคพลังงาน
WAYPOINTS_LOGISTICS = [545, 500, 600, 650, 700, 750, 850, 800] # โลจิสติกส์
WAYPOINTS_RAIL = [545, 500, 450, 250, 300, 150, 100, 200] # ระบบขนส่งทางราง
WAYPOINTS_MECHATRONICS = [545, 500, 350, 400, 200, 250, 100, 150] # เมคคาทรอนิกส์และหุ่นยนต์
WAYPOINTS_AIRLINE = [545, 500, 650, 550, 800, 600, 900, 580] # แผนกการบิน
WAYPOINTS_COMPUTER_TECH = [545, 500, 700, 400, 850, 300, 950, 250] # เทคโนโลยีคอมพิวเตอร์
# ***************************************************************


# ** Global UI Components (ประกาศไว้ด้านบนเพื่อเข้าถึงใน show_frame) **
image_slide_frame = None
survey_frame = None
credit_frame = None
bottom_bar = None
fanpage_ctk_image_global = None 

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

# --- ฟังก์ชันช่วยเหลือในการพิมพ์สถานะ ---
def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

# -----------------------------------------------------------------
# --- NEW/MODIFIED: ฟังก์ชันควบคุมหน้าต่างนำทางแบบมีเส้นทาง (Guided Page) ---
# -----------------------------------------------------------------

# *** MODIFIED: เพิ่ม video_filename ในอาร์กิวเมนต์ ***
def show_guided_page(title, header_bg_color, dept_image_path, video_filename, waypoints):
    """
    แสดงเนื้อหาแผนก/กิจกรรมแบบมีเส้นทางนำทาง
    :param title: หัวข้อที่จะแสดงบน Header
    :param header_bg_color: สีพื้นหลังของ Header
    :param dept_image_path: Path รูปภาพที่จะแสดงใต้ Header
    :param video_filename: ชื่อไฟล์วิดีโอ (.mp4) สำหรับแผนที่นำทาง
    :param waypoints: รายการพิกัด [x1, y1, x2, y2, ...] สำหรับวาดเส้นทาง
    """
    global ELECTRONICS_MAP_PATH, MAP_DISPLAY_WIDTH_ELEC, MAP_DISPLAY_HEIGHT_ELEC
    global DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT, VIDEO_PATH_BASE # เพิ่ม VIDEO_PATH_BASE
    
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
         ctk.CTkButton(electronics_content_frame, text="❮ กลับสู่หน้าหลัก", command=lambda: show_frame(home_content_frame), font=("Kanit", 28, "bold"), fg_color="#00C000", hover_color="#008000", width=250, height=70, corner_radius=15).pack(pady=(20, 40))
         show_frame(electronics_content_frame)
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


    # 3. กรอบสำหรับใส่ไฟล์วิดีโอ MP4 แผนที่ <<< MODIFIED: เพิ่ม Video Player >>>
    mp4_placeholder_frame = ctk.CTkFrame(electronics_content_frame, fg_color="#E0E0E0", width=DEPT_IMAGE_WIDTH, height=350) 
    mp4_placeholder_frame.pack(pady=(10, 10))

    # ** NEW: Video Playback Implementation (using tkvideo) **
    video_full_path = os.path.join(VIDEO_PATH_BASE, video_filename)
    
    video_label = tk.Label(mp4_placeholder_frame, bg=mp4_placeholder_frame.cget("fg_color"))
    video_label.pack(fill="both", expand=True)

    if tkvideo and os.path.exists(video_full_path):
        try:
            # ใช้ tkvideo ในการเล่นไฟล์ MP4 แบบวนซ้ำ (loop=1)
            player = tkvideo.tkvideo(
                video_full_path, 
                video_label, 
                loop=1, 
                sizex=DEPT_IMAGE_WIDTH, 
                sizey=300 # ใช้ความสูงที่เหมาะสม
            )
            player.play()
            print_status(f"--- [VIDEO PLAYER]: เริ่มเล่นวิดีโอ: {video_filename} ---")
            
        except Exception as e:
            print_status(f"--- [VIDEO PLAYER ERROR]: ไม่สามารถเล่นวิดีโอ {video_filename}: {e} ---")
            ctk.CTkLabel(mp4_placeholder_frame,
                         text=f"⚠️ ไม่สามารถเล่นวิดีโอ: {video_filename}\n(โปรดตรวจสอบไฟล์วิดีโอ หรือติดตั้งไลบรารี tkvideo: pip install tkvideo)",
                         font=("Kanit", 18, "italic"),
                         text_color="red").pack(pady=10, padx=10)
    else:
        # กรณีไม่พบไฟล์ หรือ tkvideo ไม่ถูก import
        ctk.CTkLabel(mp4_placeholder_frame,
                     text=f"⚠️ ไม่พบไฟล์วิดีโอแผนที่ MP4: {video_filename} ⚠️",
                     font=("Kanit", 18, "italic"),
                     text_color="red").pack(pady=10, padx=10)
    # ***************************************************************
        
    # 4. กรอบสำหรับข้อความนำทาง
    guide_frame = ctk.CTkFrame(electronics_content_frame, fg_color="transparent")
    guide_frame.pack(pady=(10, 5))
      
    # ข้อความนำทาง (สีม่วงเข้ม)
    ctk.CTkLabel(guide_frame, 
                 text="โปรดเดินตามเส้นทางที่กำหนดในแผนผังนี้ (เส้นประสีน้ำเงิน)", 
                 font=("Kanit", 22, "bold"), 
                 text_color="#8000FF").pack(side="left")

    
    # 5. แผนผังการเดิน (Map Image) พร้อมเส้นประ
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
            width=7, 
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


    # 6. ปุ่มกลับสู่หน้าหลัก
    ctk.CTkButton(electronics_content_frame, 
                  text="❮ กลับสู่หน้าหลัก", 
                  command=lambda: show_frame(home_content_frame), 
                  font=("Kanit", 28, "bold"),
                  fg_color="#00C000",
                  hover_color="#008000",
                  width=250,
                  height=70,
                  corner_radius=15).pack(pady=(20, 40))
                  
    # แสดงเฟรมนี้
    show_frame(electronics_content_frame) 

# -----------------------------------------------------------------
# --- NEW/UPDATED: ฟังก์ชัน Wrapper สำหรับแผนกทั้งหมด (20 แผนก + 1 กิจกรรม) ---
# -----------------------------------------------------------------

# *** MODIFIED: get_dept_info เพื่อดึงชื่อไฟล์วิดีโอออกมาด้วย ***
def get_dept_info(name):
    """Helper function to get config data (image_filename, video_filename, image_path, color) by department name"""
    # New: (main_image_filename, video_filename, w1, w2, image_full_path, color)
    config = DEPARTMENTS_CONFIG.get(name, ("", "", 0, 0, "", "#000000"))
    # Return: image_filename, video_filename, image_full_path, color
    return config[0], config[1], config[4], config[5] 

# ------------------------------------------------------------------------------------------------
# *** MODIFIED: ส่ง video_filename เข้าไปใน show_guided_page() สำหรับทุกแผนก ***
# ------------------------------------------------------------------------------------------------

# แผนก 1: ก่อสร้าง (Existing)
def show_construction_page():
    title = "แผนกวิชาช่างก่อสร้าง"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_CONSTRUCTION)

# แผนก 2: โยธา (New)
def show_civil_page():
    title = "แผนกวิชาช่างโยธา"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_CIVIL)

# แผนก 3: เฟอร์นิเจอร์และตกแต่งภายใน (New)
def show_furniture_page():
    title = "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_FURNITURE)

# แผนก 4: ช่างสำรวจ (New)
def show_survey_page():
    title = "แผนกวิชาช่างสำรวจ"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_SURVEY)

# แผนก 5: สถาปัตยกรรม (New)
def show_architect_page():
    title = "แผนกวิชาสถาปัตยกรรม"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_ARCHITECT)

# แผนก 6: ช่างยนต์ (New)
def show_auto_page():
    title = "แผนกวิชาช่างยนต์"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_AUTO)

# แผนก 7: ช่างกลโรงงาน (New)
def show_factory_page():
    title = "แผนกวิชาช่างกลโรงงาน"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_FACTORY)

# แผนก 8: ช่างเชื่อมโลหะ (New)
def show_welding_page():
    title = "แผนกวิชาช่างเชื่อมโลหะ"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_WELDING)

# แผนก 9: ช่างเทคนิคพื้นฐาน (New)
def show_basic_tech_page():
    title = "แผนกวิชาช่างเทคนิคพื้นฐาน"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_BASICTECH)

# แผนก 10: ช่างไฟฟ้า (Existing)
def show_electrical_page():
    title = "แผนกวิชาช่างไฟฟ้า"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_ELECTRICAL)

# แผนก 11: ช่างอิเล็กทรอนิกส์ (Existing)
def show_electronics_page():
    title = "แผนกวิชาช่างอิเล็กทรอนิกส์"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_ELECTRONICS)

# แผนก 12: เครื่องทำความเย็นและปรับอากาศ (New)
def show_aircond_page():
    title = "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_AIRCOND)

# แผนก 13: เทคโนโลยีสารสนเทศ (New)
def show_it_page():
    title = "แผนกวิชาเทคโนโลยีสารสนเทศ"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_IT)

# แผนก 14: เทคโนโลยีปิโตรเลียม (Existing)
def show_petroleum_page():
    title = "แผนกวิชาเทคโนโลยีปิโตรเลียม"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_PETROLEUM)

# แผนก 15: เทคนิคพลังงาน (New)
def show_energy_page():
    title = "แผนกวิชาเทคนิคพลังงาน"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_ENERGY)

# แผนก 16: การจัดการโลจิสติกส์ซัพพลายเชน (New)
def show_logistics_page():
    title = "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_LOGISTICS)

# แผนก 17: เทคนิคควบคุมระบบขนส่งทางราง (New)
def show_rail_page():
    title = "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_RAIL)

# แผนก 18: เมคคาทรอนิกส์และหุ่นยนต์ (New)
def show_mechatronics_page():
    title = "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_MECHATRONICS)

# แผนก 19: แผนกการบิน (New)
def show_airline_page():
    title = "แผนกวิชาแผนกการบิน"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_AIRLINE)

# แผนก 20: เทคโนโลยีคอมพิวเตอร์ (New)
def show_computer_tech_page():
    title = "แผนกวิชาเทคโนโลยีคอมพิวเตอร์"
    _, video_filename, dept_image_path, color = get_dept_info(title) 
    show_guided_page(title=title, header_bg_color=color, dept_image_path=dept_image_path, video_filename=video_filename, waypoints=WAYPOINTS_COMPUTER_TECH)

# กิจกรรมพิเศษ: 60 ปี
def show_60_years_page():
    ... # (ใช้ฟังก์ชันเดิม)
# ตึก 11 
def show_tuk11_page():
    ... # (ใช้ฟังก์ชันเดิม)


# -----------------------------------------------------------------
# --- ฟังก์ชันควบคุมเสียง (Keywords mapping remains the same) ---
# -----------------------------------------------------------------
# ... (process_speech_command remains the same, but now calls the modified show_xxx_page)
def process_speech_command(text):
    """ประมวลผลคำสั่งเสียงที่แปลงมาแล้ว"""
    global is_listening
    text_lower = text.lower()
    print_status(f"--- [MIC RECOGNIZE]: ได้รับข้อความ: '{text}' ---")
    try:
        # 1. ตรวจสอบคำสั่งเสียงสำหรับทุกแผนก (ใช้ Keyword ที่กำหนดไว้ด้านบน)
        # ก่อสร้าง
        if any(keyword in text_lower for keyword in KEYWORDS_CONSTRUCTION):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ก่อสร้าง' นำทางไปยังหน้าแผนกก่อสร้าง ---")
            root.after(0, show_construction_page)
            return
        # โยธา
        if any(keyword in text_lower for keyword in KEYWORDS_CIVIL):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'โยธา' นำทางไปยังหน้าแผนกโยธา ---")
            root.after(0, show_civil_page)
            return
        # เฟอร์นิเจอร์และตกแต่งภายใน
        if any(keyword in text_lower for keyword in KEYWORDS_FURNITURE):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'เฟอร์นิเจอร์/ตกแต่งภายใน' นำทางไปยังหน้าแผนกเฟอร์นิเจอร์ ---")
            root.after(0, show_furniture_page)
            return
        # สำรวจ
        if any(keyword in text_lower for keyword in KEYWORDS_SURVEY):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'สำรวจ' นำทางไปยังหน้าแผนกสำรวจ ---")
            root.after(0, show_survey_page)
            return
        # สถาปัตยกรรม
        if any(keyword in text_lower for keyword in KEYWORDS_ARCHITECT):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'สถาปัตย์' นำทางไปยังหน้าแผนกสถาปัตยกรรม ---")
            root.after(0, show_architect_page)
            return
        # ช่างยนต์
        if any(keyword in text_lower for keyword in KEYWORDS_AUTO):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ช่างยนต์' นำทางไปยังหน้าแผนกช่างยนต์ ---")
            root.after(0, show_auto_page)
            return
        # ช่างกลโรงงาน
        if any(keyword in text_lower for keyword in KEYWORDS_FACTORY):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ช่างกลโรงงาน' นำทางไปยังหน้าแผนกช่างกลโรงงาน ---")
            root.after(0, show_factory_page)
            return
        # ช่างเชื่อมโลหะ
        if any(keyword in text_lower for keyword in KEYWORDS_WELDING):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ช่างเชื่อมโลหะ' นำทางไปยังหน้าแผนกช่างเชื่อมโลหะ ---")
            root.after(0, show_welding_page)
            return
        # ช่างเทคนิคพื้นฐาน
        if any(keyword in text_lower for keyword in KEYWORDS_BASICTECH):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ช่างเทคนิคพื้นฐาน' นำทางไปยังหน้าแผนกช่างเทคนิคพื้นฐาน ---")
            root.after(0, show_basic_tech_page)
            return
        # ช่างไฟฟ้า (เดิม)
        if any(keyword in text_lower for keyword in KEYWORDS_ELECTRIC):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ไฟฟ้า' นำทางไปยังหน้าแผนกช่างไฟฟ้า ---")
            root.after(0, show_electrical_page)
            return
        # ช่างอิเล็กทรอนิกส์ (เดิม)
        if any(keyword in text_lower for keyword in KEYWORDS_ELECTRONICS):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'อิเล็กทรอนิกส์' นำทางไปยังหน้าแผนกอิเล็กทรอนิกส์ ---")
            root.after(0, show_electronics_page)
            return
        # เครื่องทำความเย็นและปรับอากาศ
        if any(keyword in text_lower for keyword in KEYWORDS_AIRCOND):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'เครื่องทำความเย็น/ปรับอากาศ' นำทางไปยังหน้าแผนกเครื่องทำความเย็นและปรับอากาศ ---")
            root.after(0, show_aircond_page)
            return
        # เทคโนโลยีสารสนเทศ
        if any(keyword in text_lower for keyword in KEYWORDS_IT):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ไอที' นำทางไปยังหน้าแผนกเทคโนโลยีสารสนเทศ ---")
            root.after(0, show_it_page)
            return
        # เทคโนโลยีปิโตรเลียม
        if any(keyword in text_lower for keyword in KEYWORDS_PETROLEUM):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ปิโตรเลียม' นำทางไปยังหน้าแผนกเทคโนโลยีปิโตรเลียม ---")
            root.after(0, show_petroleum_page)
            return
        # เทคนิคพลังงาน
        if any(keyword in text_lower for keyword in KEYWORDS_ENERGY):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'พลังงาน' นำทางไปยังหน้าแผนกเทคนิคพลังงาน ---")
            root.after(0, show_energy_page)
            return
        # โลจิสติกส์
        if any(keyword in text_lower for keyword in KEYWORDS_LOGISTICS):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'โลจิสติกส์' นำทางไปยังหน้าแผนกโลจิสติกส์ ---")
            root.after(0, show_logistics_page)
            return
        # ระบบขนส่งทางราง
        if any(keyword in text_lower for keyword in KEYWORDS_RAIL):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ขนส่งทางราง' นำทางไปยังหน้าแผนกควบคุมระบบขนส่งทางราง ---")
            root.after(0, show_rail_page)
            return
        # เมคคาทรอนิกส์และหุ่นยนต์
        if any(keyword in text_lower for keyword in KEYWORDS_MECHATRONICS):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'เมคคาทรอนิกส์' นำทางไปยังหน้าแผนกเมคคาทรอนิกส์ ---")
            root.after(0, show_mechatronics_page)
            return
        # แผนกการบิน
        if any(keyword in text_lower for keyword in KEYWORDS_AIRLINE):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'การบิน' นำทางไปยังหน้าแผนกการบิน ---")
            root.after(0, show_airline_page)
            return
        # เทคโนโลยีคอมพิวเตอร์
        if any(keyword in text_lower for keyword in KEYWORDS_COMPUTER_TECH):
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'เทคโนโลยีคอมพิวเตอร์' นำทางไปยังหน้าแผนกเทคโนโลยีคอมพิวเตอร์ ---")
            root.after(0, show_computer_tech_page)
            return
            
        # คำสั่งนำทางพิเศษอื่นๆ
        # ตรวจสอบ "ตึก 11" (เดิม)
        if "ตึก 11" in text_lower:
            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'ตึก 11' นำทางไปยังหน้าตึก 11 ---")
            root.after(0, show_tuk11_page)
            return
        # ตรวจสอบ "ตึก 60 ปี" (เดิม)
        for keyword in ["ตึก 60 ปี", "60 ปี"]:
            if keyword in text_lower:
                print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้ากิจกรรม 60 ปี ---")
                root.after(0, show_60_years_page)
                return
        print_status("--- [SYSTEM]: ไม่พบคำสั่งที่เกี่ยวข้องกับแผนกใดๆ ---")
    except sr.WaitTimeoutError:
        print_status("--- [MIC ERROR]: ไม่ได้รับเสียงภายใน 7 วินาที ---")
    except sr.UnknownValueError:
        print_status("--- [MIC ERROR]: ไม่สามารถเข้าใจคำพูด (UnknownValueError) ---")
    except sr.RequestError as e:
        print_status(f"--- [MIC ERROR]: ไม่สามารถเชื่อมต่อกับ Google Speech (ตรวจสอบอินเทอร์เน็ต); {e} ---")
    except Exception as e:
        print_status(f"--- [MIC ERROR]: เกิดข้อผิดพลาดในการประมวลผล: {e} ---")
    finally:
        # ** FIX: บล็อกนี้จะทำงานเสมอ แม้จะมี return หรือ Exception **
        is_listening = False
        print_status("--- [MIC STATUS]: การฟังเสร็จสิ้น (IDLE) ---")
        
# -----------------------------------------------------------------
def load_slide_images():
    """โหลดรูปภาพจากโฟลเดอร์สำหรับทำ Image Slide"""
    global slide_images, slide_photo_images, IMAGE_SLIDE_FOLDER, IMAGE_SLIDE_HEIGHT, SLIDE_FRAME_WIDTH, IMAGE_SLIDE_WIDTH_LIMIT, SLIDE_FRAME_COLOR
    slide_images = [] # รีเซ็ตลิสต์
    slide_photo_images = []
    
    # 1. รวบรวมชื่อไฟล์รูปภาพทั้งหมดที่ใช้ทำสไลด์ (จาก DEPARTMENTS_CONFIG และ NAVIGATION_TRIGGER_IMAGE)
    slide_file_names = {config[0] for config in DEPARTMENTS_CONFIG.values()}
    slide_file_names.add(NAVIGATION_TRIGGER_IMAGE)
    
    if not os.path.isdir(IMAGE_SLIDE_FOLDER):
        print_status(f"--- [IMAGE SLIDE ERROR]: ไม่พบโฟลเดอร์รูปภาพ: {IMAGE_SLIDE_FOLDER} ---")
        return 
        
    # 2. กรองเฉพาะไฟล์ที่ต้องการจากโฟลเดอร์
    for filename in sorted(os.listdir(IMAGE_SLIDE_FOLDER)):
        if filename not in slide_file_names:
            continue
            
        full_path = os.path.join(IMAGE_SLIDE_FOLDER, filename)
        if not os.path.isfile(full_path):
            continue
            
        valid_extensions = ('.jpg', '.jpeg', '.png')
        if not filename.lower().endswith(valid_extensions):
            continue
            
        try:
            img = Image.open(full_path)
            # ปรับขนาด
            if img.width > IMAGE_SLIDE_WIDTH_LIMIT:
                scale_factor = IMAGE_SLIDE_WIDTH_LIMIT / img.width
                new_width = IMAGE_SLIDE_WIDTH_LIMIT
                new_height = int(img.height * scale_factor)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                
            img = img.resize((int(img.width * (IMAGE_SLIDE_HEIGHT / img.height)), IMAGE_SLIDE_HEIGHT), Image.LANCZOS)

            # เพิ่มกรอบ (Frame)
            # ------------------------------------------------
            img = ImageOps.expand(img, border=SLIDE_FRAME_WIDTH, fill=SLIDE_FRAME_COLOR) 
            # ------------------------------------------------
            
            slide_images.append(img)
            slide_photo_images.append({
                'photo': ImageTk.PhotoImage(img),
                'filename': filename
            })
            print_status(f"--- [IMAGE SLIDE]: โหลดรูปภาพ (รวมกรอบ): {filename} ({img.width}x{img.height}) ---")
        except Exception as e:
            print_status(f"--- [IMAGE SLIDE ERROR]: ไม่สามารถโหลดรูปภาพ {filename}: {e} ---")

    if not slide_images:
        print_status("--- [IMAGE SLIDE]: ไม่พบรูปภาพที่สามารถโหลดได้ ---")

def place_next_slide(start_immediately_at_right_edge=False):
    """วางรูปภาพสไลด์ถัดไปบน Canvas โดยเว้นช่องไฟ"""
    global current_slide_index, image_slide_canvas, slide_photo_images, next_image_x_placement, active_slide_items, SLIDE_GAP
    if not slide_photo_images:
        return

    # เลื่อน index
    current_slide_index = (current_slide_index + 1) % len(slide_photo_images)
    slide_data = slide_photo_images[current_slide_index]
    image_to_place = slide_data['photo']
    image_filename = slide_data['filename']
    image_width = image_to_place.width()
    image_height = image_to_place.height()

    if start_immediately_at_right_edge:
        start_x = image_slide_canvas.winfo_width() # เริ่มที่ขอบขวาของ Canvas
    else:
        start_x = next_image_x_placement # วางรูปภาพ

    # ตำแหน่ง Y จะอยู่กึ่งกลางความสูงของสไลด์
    center_y = image_slide_canvas.winfo_height() / 2
    canvas_item_id = image_slide_canvas.create_image(
        start_x,
        center_y,
        image=image_to_place,
        anchor="center"
    )

    # กำหนด Click Handler ให้กับ Item ID นั้น
    setup_slide_click_handlers(canvas_item_id, image_filename)

    # เก็บรายการ Active Slide Items (สำหรับควบคุมการเคลื่อนที่)
    active_slide_items.append({
        'id': canvas_item_id,
        'width': image_width,
        'filename': image_filename
    })

    # คำนวณตำแหน่ง X สำหรับรูปถัดไป
    next_image_x_placement = start_x + (image_width / 2) + SLIDE_GAP + (image_to_place.width() / 2)

# --- MODIFIED: Refactor การจัดการ Click Handler ให้ครอบคลุมทุกแผนก ---
# *** NEW/UPDATED: Global Map สำหรับการคลิกสไลด์ไปหน้าแผนก ***
DEPT_PAGE_MAPPING = {
    # รูปภาพใหม่ทั้งหมด (BXX.jpg, s15.jpeg, w11.jpg)
    "B8.jpg": show_electronics_page,
    "B11.jpg": show_construction_page,
    "B9.jpg": show_civil_page,
    "B12.jpg": show_furniture_page,
    "B15.jpg": show_auto_page,
    "B16.jpg": show_factory_page,
    "B17.jpg": show_welding_page,
    "B1.jpg": show_basic_tech_page,
    "B10.jpg": show_electrical_page,
    "B2.jpg": show_aircond_page,
    "B13.jpg": show_it_page,
    "B88.jpg": show_petroleum_page,
    "B14.jpg": show_rail_page,
    "w11.jpg": show_computer_tech_page,
    
    # รูปภาพที่ใช้ซ้ำกัน
    "B6.jpg": show_architect_page, # B6.jpg ใช้สำหรับ ช่างสำรวจ และ สถาปัตยกรรม (เลือกไป สถาปัตยกรรม)
    "B3.jpg": show_mechatronics_page, # B3.jpg ใช้สำหรับ เทคนิคพลังงาน และ เมคคาทรอนิกส์ (เลือกไป เมคคาทรอนิกส์)
    "s15.jpeg": show_logistics_page, # s15.jpeg ใช้สำหรับ โลจิสติกส์ และ การบิน (เลือกไป โลจิสติกส์)
    
    # รูปภาพกิจกรรม
    "60 ปี.jpg": show_60_years_page, 
}

def setup_slide_click_handlers(canvas_item_id, image_filename):
    """กำหนดฟังก์ชันเมื่อคลิกที่รูปภาพสไลด์ โดยใช้ DEPT_PAGE_MAPPING"""
    global is_dragging, DEPT_PAGE_MAPPING
    if image_filename in DEPT_PAGE_MAPPING:
        target_function = DEPT_PAGE_MAPPING[image_filename]
        def handle_click(event):
            if not is_dragging: # ป้องกันการคลิกเมื่อกำลังลาก
                # เรียกใช้ฟังก์ชันที่ Map ไว้
                root.after(0, target_function)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_click)

def move_slides():
    ... # (remains the same)

def create_image_slide():
    ... # (remains the same)
    
# -------------------- (UI and Main Loop remains the same) --------------------

# ***************************************************************
# ** ส่วนของ UI ด้านบน (Fixed Top Widgets) **
# ***************************************************************
# --- 1. แถบด้านบน (Top Bar) ---
top_bar = ctk.CTkFrame(root, height=80, fg_color="#4F009D")
top_bar.pack(side="top", fill="x")

# โลโก้ (ถ้ามี)
try:
    logo_image = Image.open("/home/pi/Test_GUI/icons/logo.png").resize((50, 50))
    logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(50, 50))
    ctk.CTkLabel(top_bar, image=logo_ctk_image, text="").pack(side="left", padx=15, pady=15)
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
bottom_label = ctk.CTkLabel(bottom_bar, 
                            text="วิทยาลัยเทคนิคหาดใหญ่ 🇹🇭", 
                            text_color="white", 
                            font=("Kanit", 20, "bold"))
bottom_label.pack(pady=5)


# --- 3. Credit Frame ---
credit_frame = ctk.CTkFrame(root, height=120, fg_color="white")
# (code for credit frame contents)
# ... (contents remain the same)


# --- 2. Survey Frame (ปุ่มกลับหน้าหลัก) ---
survey_frame = ctk.CTkFrame(root, height=120, fg_color="#EFEFEF")
# (code for survey frame contents)
# ... (contents remain the same)


# --- 1. Image Slide Frame (แถบเลื่อนรูปภาพ) ---
# ... (code for creating image slide frame and canvas)
image_slide_frame = ctk.CTkFrame(root, height=IMAGE_SLIDE_HEIGHT + SLIDE_FRAME_WIDTH*2, fg_color="white")
# (code for creating canvas and loading images)
# ... (contents remain the same)


# ***************************************************************
# ** ส่วนของ UI กลาง (Content Area - ต้อง Pack ลำดับสุดท้าย) **
# ***************************************************************
# เนื้อหาหลักเริ่มต้นด้วย Home Frame
show_frame(home_content_frame) 

# === ไอคอนไมค์พร้อมเอฟเฟกต์ออร่า (Fixed บน root) ===
# ... (code for mic frame and canvas)

def start_drag_slides(event):
    """เริ่มต้นการลากสไลด์"""
    global last_x, is_dragging
    is_dragging = True
    last_x = event.x

def drag_slides(event):
    """ดำเนินการลากสไลด์"""
    global last_x, image_slide_canvas, next_image_x_placement
    if image_slide_canvas is None:
        return
        
    dx = event.x - last_x
    image_slide_canvas.move("all", dx, 0)
    next_image_x_placement += dx
    last_x = event.x

def stop_drag_slides(event):
    """หยุดการลากสไลด์และตั้งค่าสถานะ"""
    global is_dragging
    # หน่วงเวลาเล็กน้อยเพื่อป้องกันการคลิกที่เกิดขึ้นพร้อมกับการปล่อยเมาส์
    root.after(100, lambda: set_dragging_false())

def set_dragging_false():
    global is_dragging
    is_dragging = False

# (โค้ดส่วน mic, start_blinking, start_listening, create_ui, start_app)
# ...
# ...
# ...

# สร้าง UI และเริ่มลูปหลัก
# create_ui() 
# start_app()

if __name__ == "__main__":
    # ฟังก์ชันเหล่านี้ควรถูกเรียกใน create_ui() แต่ถ้าไม่มี create_ui() ในโค้ดที่ให้มา
    # จะต้องเรียกใช้ฟังก์ชันที่สร้าง UI และเริ่ม Main Loop ตรงนี้
    
    # โหลดรูปภาพสไลด์
    load_slide_images() 
    
    # (สมมติว่ามีฟังก์ชันสร้าง UI อื่นๆ เช่น create_image_slide, create_mic_frame ฯลฯ)

    # *** Note: เนื่องจากโค้ดที่ให้มาไม่ครบถ้วนในส่วน Main App initialization
    #             (missing create_ui(), start_app()), ผมจะเรียกใช้ฟังก์ชันที่จำเป็น
    #             เพื่อเปิดใช้งานแถบสไลด์และ Mic Frame ถ้ามี)

    # 1. สร้าง Image Slide (หากยังไม่ได้สร้าง)
    if image_slide_canvas is None:
        create_image_slide() 
        
    # 2. เริ่มต้นแสดงผลเฟรมหลัก
    show_frame(home_content_frame)

    # 3. เริ่มต้นลูป
    root.mainloop()