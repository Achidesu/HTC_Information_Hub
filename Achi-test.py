import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps 
import tkinter as tk 
import speech_recognition as sr 
import threading 
import time 
import os

from test3 import DEPT_IMAGE_PATH_BASE 

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

# ** Navigation Variables ** #ค่อยเอาโค้ดคีย์แผนกมาใส่
electronics_window = None 
# --- MODIFIED: เพิ่มคำสั่งเสียงทั้งหมดตามคำขอใหม่ ---
KEYWORDS_ELECTRONICS = ["อิเล็กทรอนิกส์", "อิเล็ก", "อีเล็ก", "แผนกอิเล็ก", "อิเล็กทรอนิก"] 
KEYWORDS_CONSTRUCTION = ["ช่างก่อสร้าง", "ก่อสร้าง"]
KEYWORDS_CIVIL = ["ช่างโยธา", "โยธา"]
KEYWORDS_FURNITURE = ["ช่างเฟอร์นิเจอร์", "ตกแต่งภายใน", "เฟอร์นิเจอร์"]
KEYWORDS_SURVEY = ["ช่างสำรวจ", "สำรวจ"]
KEYWORDS_ARCHITECT = ["สถาปัตยกรรม", "สถาปัตย์"]
KEYWORDS_AUTO = ["ช่างยนต์", "ยนต์"]
KEYWORDS_FACTORY = ["ช่างกลโรงงาน", "กลโรงงาน"]
KEYWORDS_WELDING = ["ช่างเชื่อมโลหะ", "เชื่อมโลหะ", "เชื่อม"]
# *** NEW: เพิ่ม ช่างเทคนิคพื้นฐาน ***
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
# โปรดกำหนดค่าของ DEPT_IMAGE_PATH_BASE ก่อนการใช้งาน เช่น:
# DEPT_IMAGE_PATH_BASE = "images/department/" 

DEPARTMENTS_CONFIG = {
    "แผนกวิชาช่างก่อสร้าง": ("ช่างก่อสร้าง.jpg", "ช่างก่อสร้าง.jpg", 120, 3, DEPT_IMAGE_PATH_BASE + "ช่างก่อสร้าง.jpg", "#FF8C00"), # DarkOrange
    "แผนกวิชาช่างโยธา": ("ช่างโยธา.jpg", "ช่างโยธา.jpg", 150, 4, DEPT_IMAGE_PATH_BASE + "ช่างโยธา.jpg", "#A52A2A"), # Brown
    "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน": ("ช่างเฟอร์นิเจอร์และตกแต่งภายใน.jpg", "ช่างเฟอร์นิเจอร์และตกแต่งภายใน.jpg", 180, 5, DEPT_IMAGE_PATH_BASE + "ช่างเฟอร์นิเจอร์และตกแต่งภายใน.jpg", "#D2691E"), # Chocolate
    "แผนกวิชาช่างสำรวจ": ("ช่างสำรวจ.jpg", "ช่างสำรวจ.jpg", 200, 6, DEPT_IMAGE_PATH_BASE + "ช่างสำรวจ.jpg", "#556B2F"), # DarkOliveGreen
    "แผนกวิชาสถาปัตยกรรม": ("สถาปัตยกรรม.jpg", "สถาปัตยกรรม.jpg", 200, 6, DEPT_IMAGE_PATH_BASE + "สถาปัตยกรรม.jpg", "#708090"), # SlateGray
    "แผนกวิชาช่างยนต์": ("ช่างยนต์.jpg", "ช่างยนต์.jpg", 100, 3, DEPT_IMAGE_PATH_BASE + "ช่างยนต์.jpg", "#DC143C"), # Crimson
    "แผนกวิชาช่างกลโรงงาน": ("ช่างกลโรงงาน.jpg", "ช่างกลโรงงาน.jpg", 90, 2, DEPT_IMAGE_PATH_BASE + "ช่างกลโรงงาน.jpg", "#4682B4"), # SteelBlue
    "แผนกวิชาช่างเชื่อมโลหะ": ("ช่างเชื่อมโลหะ.jpg", "ช่างเชื่อมโลหะ.jpg", 110, 3, DEPT_IMAGE_PATH_BASE + "ช่างเชื่อมโลหะ.jpg", "#FF4500"), # OrangeRed
    "แผนกวิชาช่างเทคนิคพื้นฐาน": ("ช่างเทคนิคพื้นฐาน.jpg", "ช่างเทคนิคพื้นฐาน.jpg", 130, 3, DEPT_IMAGE_PATH_BASE + "ช่างเทคนิคพื้นฐาน.jpg", "#BDB76B"), # DarkKhaki
    "แผนกวิชาช่างไฟฟ้า": ("ช่างไฟฟ้า.jpg", "ช่างไฟฟ้า.jpg", 140, 4, DEPT_IMAGE_PATH_BASE + "ช่างไฟฟ้า.jpg", "#FFD700"), # Gold
    "แผนกวิชาช่างอิเล็กทรอนิกส์": ("อิเล็กทรอนิกส์.jpg", "อิเล็กทรอนิกส์.jpg", 160, 4, DEPT_IMAGE_PATH_BASE + "อิเล็กทรอนิกส์.jpg", "#87CEFA"), # LightSkyBlue (สีเดิม)
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ": ("เครื่องทำความเย็นและปรับอากาศ.jpg", "เครื่องทำความเย็นและปรับอากาศ.jpg", 180, 5, DEPT_IMAGE_PATH_BASE + "เครื่องทำความเย็นและปรับอากาศ.jpg", "#00BFFF"), # DeepSkyBlue
    "แผนกวิชาเทคโนโลยีสารสนเทศ": ("เทคโนโลยีสารสนเทศ.jpg", "เทคโนโลยีสารสนเทศ.jpg", 170, 4, DEPT_IMAGE_PATH_BASE + "เทคโนโลยีสารสนเทศ.jpg", "#9370DB"), # MediumPurple
    "แผนกวิชาเทคโนโลยีปิโตรเลียม": ("เทคโนโลยีปิโตรเลียม.jpg", "เทคโนโลยีปิโตรเลียม.jpg", 190, 5, DEPT_IMAGE_PATH_BASE + "เทคโนโลยีปิโตรเลียม.jpg", "#32CD32"), # LimeGreen
    "แผนกวิชาเทคนิคพลังงาน": ("เทคนิคพลังงาน.jpg", "เทคนิคพลังงาน.jpg", 200, 6, DEPT_IMAGE_PATH_BASE + "เทคนิคพลังงาน.jpg", "#3CB371"), # MediumSeaGreen
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": ("การจัดการโลจิสติกส์ซัพพลายเชน.jpg", "การจัดการโลจิสติกส์ซัพพลายเชน.jpg", 160, 4, DEPT_IMAGE_PATH_BASE + "การจัดการโลจิสติกส์ซัพพลายเชน.jpg", "#20B2AA"), # LightSeaGreen
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง": ("เทคนิคควบคุมระบบขนส่งทางราง.jpg", "เทคนิคควบคุมระบบขนส่งทางราง.jpg", 210, 6, DEPT_IMAGE_PATH_BASE + "เทคนิคควบคุมระบบขนส่งทางราง.jpg", "#6A5ACD"), # SlateBlue
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": ("เมคคาทรอนิกส์และหุ่นยนต์.jpg", "เมคคาทรอนิกส์และหุ่นยนต์.jpg", 200, 5, DEPT_IMAGE_PATH_BASE + "เมคคาทรอนิกส์และหุ่นยนต์.jpg", "#BA55D3"), # MediumOrchid
    "แผนกวิชาแผนกการบิน": ("แผนกการบิน.jpg", "แผนกการบิน.jpg", 160, 4, DEPT_IMAGE_PATH_BASE + "แผนกการบิน.jpg", "#4169E1"), # RoyalBlue
    "แผนกวิชาเทคโนโลยีคอมพิวเตอร์": ("เทคโนโลยีคอมพิวเตอร์.jpg", "เทคโนโลยีคอมพิวเตอร์.jpg", 180, 2, DEPT_IMAGE_PATH_BASE + "เทคโนโลยีคอมพิวเตอร์.jpg", "#8A2BE2") # BlueViolet
}
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
                  command=lambda: show_frame(home_content_frame), 
                  font=("Kanit", 28, "bold"),
                  fg_color="#00C000",
                  hover_color="#008000",
                  width=250,
                  height=70,
                  corner_radius=15).pack(pady=(20, 40))
                  
    # แสดงเฟรมนี้
    show_frame(electronics_content_frame) 


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
    
    # ... (โค้ดภายในเหมือนเดิม) ...
    for widget in navigation_content_frame.winfo_children():
        widget.destroy()
        
    back_button_frame = ctk.CTkFrame(navigation_content_frame, fg_color="transparent", height=120)
    back_button_frame.pack(side="top", fill="x", pady=(30, 0), padx=40)
    
    ctk.CTkButton(back_button_frame, 
                  text="❮ กลับสู่หน้าหลัก", 
                  command=lambda: show_frame(home_content_frame),
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
                map_image_label.image = map_tk_img 
                
                if hasattr(map_image_label, 'image_item_id'):
                     if isinstance(map_image_label.image_item_id, ctk.CTkLabel):
                         map_image_label.image_item_id.destroy()

                image_display = ctk.CTkLabel(
                     map_image_label, 
                     image=map_tk_img, 
                     text="", 
                     width=new_width, 
                     height=new_height,
                     fg_color="white" 
                )
                image_display.pack(expand=False)
                
                image_display.image = map_tk_img
                map_image_label.image_item_id = image_display
                
            else:
                 root.after(100, resize_and_display_map) 
        
        root.after(100, resize_and_display_map) 
        
    except FileNotFoundError:
        map_image_label.configure(
            text=f"⚠️ ไม่พบไฟล์รูปภาพแผนที่ '{map_path_to_load}' ⚠️",
            font=("Kanit", 32, "bold"),
            text_color="red",
            fg_color="#FFF0F0"
        )
    except Exception as e:
        map_image_label.configure(
            text=f"⚠️ ข้อผิดพลาดในการแสดงผลรูปภาพ: {e} ⚠️",
            font=("Kanit", 28),
            text_color="red",
            fg_color="#FFF0F0"
        )
                 
    show_frame(navigation_content_frame) 

# -----------------------------------------------------------------
# --- ฟังก์ชัน Speech Recognition (ทำงานใน Thread แยก) ---
# -----------------------------------------------------------------
def listen_for_speech():
    """ฟังก์ชันหลักในการรับเสียงจากไมค์และแปลงเป็นข้อความ พร้อมแก้ปัญหาค้าง"""
    global is_listening
    r = sr.Recognizer()
    LANGUAGE = "th-TH" 

    is_listening = True 
    print_status("--- [MIC STATUS]: โปรดพูดตอนนี้ (Listening...) ---")
    
    try: # Outer try block เพื่อจับ Exception ใหญ่ และส่งต่อไปยัง finally
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
                
                # --- MODIFIED: ตรวจสอบคำสั่งทั้งหมด (เพิ่มใหม่ตั้งแต่ข้อ 9 เป็นต้นไป) ---
                
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
                
                # --- NEW: 9. ตรวจสอบ ระบบราง ---
                for keyword in ["ระบบราง", "รถไฟ"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกวิชาระบบราง ---")
                        root.after(0, show_rail_page) 
                        return
                        
                # --- NEW: 10. ตรวจสอบ วิชาพื้นฐาน ---
                for keyword in ["วิชาพื้นฐาน", "พื้นฐาน", "วิชาสามัญ"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกวิชาพื้นฐาน ---")
                        root.after(0, show_basic_subjects_page) 
                        return
                        
                # --- NEW: 11. ตรวจสอบ ศูนย์ส่งเสริมและพัฒนาอาชีวศึกษาภาคใต้ ---
                for keyword in ["ศูนย์ส่งเสริม", "อาชีวศึกษาภาคใต้", "ส่งเสริม"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าศูนย์ส่งเสริมฯ ---")
                        root.after(0, show_southern_center_page) 
                        return
                        
                # --- NEW: 12. ตรวจสอบ สถาปัตยกรรม/ช่างสำรวจ ---
                for keyword in ["สถาปัตยกรรม", "สำรวจ", "ช่างสำรวจ"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกสถาปัตยกรรม/ช่างสำรวจ ---")
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
                for keyword in ["โยธา", "ช่างโยธา", "โรงงาน", "สารสนเทศ"]:
                    if keyword in text_lower:
                         # ใช้ตรรกะตรวจจับคำสั่งรวมตึกโยธา/โรงงาน/สารสนเทศ (หากพูดคำใดคำหนึ่ง)
                         if any(k in text_lower for k in ["โยธา", "โรงงาน", "ช่างโยธา"]):
                            print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'โยธา/โรงงาน/สารสนเทศ' นำทางไปยังหน้าตึกโยธา ---")
                            root.after(0, show_civil_workshop_it_page)
                            return
                         # ถ้าพูดแค่ "สารสนเทศ" ให้เรียกหน้า สารสนเทศเดี่ยว (ข้อ 8)
                         elif keyword in ["สารสนเทศ", "ไอที", "it", "คอมพิวเตอร์"]:
                             pass # ให้ไปเช็คในข้อ 8 ต่อ
                         

                # 8. (สำรอง) ตรวจสอบ "สารสนเทศ" (เดิม)
                for keyword in ["สารสนเทศ", "ไอที", "it", "คอมพิวเตอร์"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนกสารสนเทศ (เดี่ยว) ---")
                        root.after(0, show_it_page) 
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


def start_listening_thread(event):
    """ฟังก์ชันสำหรับเริ่มต้นการฟังใน Thread แยก เพื่อไม่ให้ GUI ค้าง"""
    global is_listening
    if not is_listening:
        threading.Thread(target=listen_for_speech, daemon=True).start()
    else:
        print_status("--- [SYSTEM]: ระบบกำลังฟังอยู่ กรุณารอสักครู่ ---")


# -----------------------------------------------------------------
# --- ฟังก์ชันควบคุมการลากสไลด์ ---
# -----------------------------------------------------------------

def start_drag(event):
    """บันทึกตำแหน่งเริ่มต้นเมื่อกดคลิกที่ Canvas"""
    global last_x, is_dragging
    is_dragging = True
    last_x = event.x
    
def do_drag(event):
    """คำนวณระยะการลากและเลื่อนรูปภาพทั้งหมดใน Canvas"""
    global last_x, active_slide_items, next_image_x_placement
    
    if not is_dragging:
        return

    delta_x = event.x - last_x
    
    # 1. เลื่อนทุกอย่างบน Canvas
    image_slide_canvas.move("all", delta_x, 0)
    
    # 2. อัปเดตตำแหน่งทางตรรกะ (Logical Position)
    next_image_x_placement += delta_x
    for item in active_slide_items:
        item['right_edge'] += delta_x
        
    last_x = event.x
    
    # NEW: ตรวจสอบและเพิ่มรูปภาพ "ก่อนหน้า" เมื่อลากย้อนกลับ (ไปทางขวา)
    if active_slide_items and delta_x > 0:
        first_item = active_slide_items[0]
        coords = image_slide_canvas.coords(first_item['id'])
        current_x_center = coords[0]
        
        first_item_left_edge = current_x_center - (first_item['width'] / 2)
        
        if first_item_left_edge > -100: 
             place_previous_slide() 


def stop_drag(event):
    """สิ้นสุดการลาก"""
    global is_dragging
    is_dragging = False
    
    # เมื่อปล่อยเมาส์ ให้ตรวจสอบทันทีว่าต้องโหลดรูปภาพใหม่ที่ด้านขวาหรือไม่
    if active_slide_items and active_slide_items[-1]['right_edge'] < 1080 + SLIDE_GAP:
        place_next_slide()
        
    # ตรวจสอบว่ารูปภาพด้านซ้ายถูกลบหมดหรือไม่ ถ้าใช่ ให้เริ่มโหลดใหม่
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
                    target_image_height = original_height 
                
            # --- ตรวจสอบความกว้าง (จำกัดความกว้างของ *ตัวรูปภาพ*) ---
            target_image_width_limit = IMAGE_SLIDE_WIDTH_LIMIT - (SLIDE_FRAME_WIDTH * 2)
            if img.width > target_image_width_limit:
                 ratio = target_image_width_limit / img.width
                 new_height = int(img.height * ratio)
                 img = img.resize((target_image_width_limit, new_height), Image.LANCZOS)
                 target_image_height = img.height

            # --- เพิ่มกรอบ (Frame) ให้กับรูปภาพ ---
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
    global current_slide_index, image_slide_canvas, slide_photo_images, slide_images
    global next_image_x_placement, active_slide_items, SLIDE_GAP, NAVIGATION_TRIGGER_IMAGE
    global IT_DEPT_IMAGE_PATH 

    if not slide_photo_images or not image_slide_canvas:
        return

    if active_slide_items:
        last_slide_index = active_slide_items[-1]['slide_index']
        next_slide_index = (last_slide_index + 1) % len(slide_photo_images)
    else:
        next_slide_index = (current_slide_index + 1) % len(slide_photo_images)

    
    image_data = slide_photo_images[next_slide_index] 
    image_to_place = slide_images[next_slide_index]
    
    image_width = image_to_place.width
    image_photo = image_data['photo']
    image_filename = image_data['filename'] 


    # 2. คำนวณตำแหน่ง X
    if start_immediately_at_right_edge:
        start_x_center = 1080 + image_width / 2
    else:
        start_x_center = next_image_x_placement + SLIDE_GAP + image_width / 2

    canvas_item_id = image_slide_canvas.create_image(
        start_x_center, IMAGE_SLIDE_HEIGHT // 2, 
        image=image_photo, 
        anchor="center"
    )

    # 3. อัปเดต Global Placement และรายการ Active Items
    next_image_x_placement = start_x_center + image_width / 2 

    active_slide_items.append({
        'id': canvas_item_id, 
        'width': image_width, 
        'photo': image_photo, 
        'right_edge': next_image_x_placement,
        'slide_index': next_slide_index 
    })
    
    current_slide_index = next_slide_index
    
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

    # สถาปัตยกรรม_สำรวจ
    elif image_filename == "สถาปัตยกรรม_สำรวจ.jpg":
        def handle_arch_survey_click(event):
            if not is_dragging:
                root.after(0, show_arch_survey_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_arch_survey_click)

    # เครื่องกล_ทำความเย็น
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

    # โยธา_โรงงาน_สารสนเทศ
    elif image_filename == "โยธา_โรงงาน_สารสนเทศ.jpg":
        def handle_civil_workshop_it_click(event):
            if not is_dragging:
                root.after(0, show_civil_workshop_it_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_civil_workshop_it_click)

    # โลจิสติกส์_พลังงาน_เชื่อม
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
    # ***************************************************************

def place_previous_slide():
    """วางรูปภาพสไลด์ 'ก่อนหน้า' บน Canvas ทางด้านซ้าย"""
    global image_slide_canvas, slide_photo_images, slide_images
    global active_slide_items, SLIDE_GAP
    global IT_DEPT_IMAGE_PATH 


    if not active_slide_items or not image_slide_canvas or not slide_photo_images:
        return
        
    current_first_index = active_slide_items[0]['slide_index']
    prev_slide_index = (current_first_index - 1 + len(slide_photo_images)) % len(slide_photo_images)
    
    if active_slide_items[0]['slide_index'] == prev_slide_index:
        return 
    
    image_data = slide_photo_images[prev_slide_index]
    image_to_place = slide_images[prev_slide_index]
    
    image_width = image_to_place.width
    image_photo = image_data['photo']
    image_filename = image_data['filename'] 
    
    first_item = active_slide_items[0]
    coords = image_slide_canvas.coords(first_item['id'])
    current_x_center = coords[0]
    
    first_item_left_edge = current_x_center - (first_item['width'] / 2)
    new_x_center = first_item_left_edge - SLIDE_GAP - (image_width / 2)
    
    canvas_item_id = image_slide_canvas.create_image(
        new_x_center, IMAGE_SLIDE_HEIGHT // 2, 
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

    # สถาปัตยกรรม_สำรวจ
    elif image_filename == "สถาปัตยกรรม_สำรวจ.jpg":
        def handle_arch_survey_click(event):
            if not is_dragging:
                root.after(0, show_arch_survey_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_arch_survey_click)

    # เครื่องกล_ทำความเย็น
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

    # โยธา_โรงงาน_สารสนเทศ
    elif image_filename == "โยธา_โรงงาน_สารสนเทศ.jpg":
        def handle_civil_workshop_it_click(event):
            if not is_dragging:
                root.after(0, show_civil_workshop_it_page)
        image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_civil_workshop_it_click)

    # โลจิสติกส์_พลังงาน_เชื่อม
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
    # ***************************************************************

    print_status(f"--- [SLIDE CONTROL]: เพิ่มรูปภาพก่อนหน้า Index {prev_slide_index} สำเร็จ ---")


def animate_image_slide():
    """ควบคุมการสไลด์ต่อเนื่องและการจัดการรายการรูปภาพ"""
    global image_slide_canvas, active_slide_items, next_image_x_placement, SLIDE_GAP
    global is_dragging 

    if not image_slide_canvas or not slide_images:
        root.after(25, animate_image_slide)
        return

    if not is_dragging:
        if not active_slide_items:
            place_next_slide(start_immediately_at_right_edge=True)
            place_next_slide() 

            if not active_slide_items:
                root.after(25, animate_image_slide)
                return

        move_distance = -3 
        
        for item in active_slide_items:
            image_slide_canvas.move(item['id'], move_distance, 0)
            item['right_edge'] += move_distance
            
        next_image_x_placement += move_distance

        if active_slide_items and active_slide_items[0]['right_edge'] < 0:
            item_to_remove = active_slide_items.pop(0)
            image_slide_canvas.delete(item_to_remove['id'])

        if active_slide_items and active_slide_items[-1]['right_edge'] < 1080 + SLIDE_GAP:
            place_next_slide()

    root.after(25, animate_image_slide)


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
credit_frame = ctk.CTkFrame(root, height=55, fg_color="#D6B0FF")
credit_frame.pack(side="bottom", fill="x") 

canvas = tk.Canvas(
    credit_frame,
    height=55,
    bg="#D6B0FF",
    highlightthickness=0,
    bd=0,
)
canvas.pack(fill="both", expand=True)

credit_text = "จัดทำโดย นักศึกษา แผนกภาควิชาเทคโนโลยีคอมพิวเตอร์"

try:
    marquee_font = ("Kanit", 26, "bold")
except:
    marquee_font = ("Arial", 26, "bold")

text_id = canvas.create_text(
    1080, 28,
    text=credit_text,
    fill="black",
    font=marquee_font,
    anchor="w"
)

def scroll_text():
    canvas.move(text_id, -2, 0)
    x = canvas.coords(text_id)[0]

    try:
        bbox = canvas.bbox(text_id)
        if bbox:
            text_width = bbox[2] - bbox[0]
        else:
            text_width = 1080 
    except:
        text_width = 1080

    if x < -text_width:
        canvas.coords(text_id, 1080, 28)

    root.after(16, scroll_text)

scroll_text()


# --- 2. ช่องแบบสอบถามความพึงพอใจ ---
survey_frame = ctk.CTkFrame(root, height=180, fg_color="#F5F0FF", corner_radius=0)
survey_frame.pack(side="bottom", fill="x", pady=(0, 0)) 

inner_survey_frame = ctk.CTkFrame(survey_frame, fg_color="transparent")
inner_survey_frame.pack(fill="both", expand=True, padx=40, pady=25)

survey_text_frame = ctk.CTkFrame(inner_survey_frame, fg_color="transparent")
survey_text_frame.pack(side="left", fill="both", expand=True)

title_container = ctk.CTkFrame(survey_text_frame, fg_color="transparent")
title_container.pack(anchor="w")

try:
    survey_icon_img = Image.open("/home/pi/Test_GUI/icons/star.png").resize((40, 40))
    survey_icon_ctk = ctk.CTkImage(light_image=survey_icon_img, dark_image=survey_icon_img, size=(40, 40))
    survey_icon = ctk.CTkLabel(title_container, image=survey_icon_ctk, text="")
    survey_icon.pack(side="left", padx=(0, 15))
except Exception as e:
    print_status(f"ไม่พบไอคอนแบบสอบถาม: {e}")
    survey_icon = ctk.CTkLabel(
        title_container,
        text="★", 
        font=("Arial", 32, "bold"),
        text_color="#8000FF"
    )
    survey_icon.pack(side="left", padx=(0, 15))

survey_title = ctk.CTkLabel(
    title_container,
    text="ช่วยทำแบบสอบถามความพึงพอใจ",
    font=("Kanit", 32, "bold"),
    text_color="#8000FF"
)
survey_title.pack(side="left")

survey_subtitle = ctk.CTkLabel(
    survey_text_frame,
    text="ความคิดเห็นของท่านมีค่ามากสำหรับเรา\nกรุณาเลือก QR Code เพื่อทำแบบสอบถาม",
    font=("Kanit", 20),
    text_color="#666666",
    justify="left"
)
survey_subtitle.pack(anchor="w", pady=(10, 0))

try:
    qr_image = Image.open("/home/pi/Test_GUI/QR/qrcode.png").resize((140, 140))
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
    mic_frame = tk.Frame(root, bg="white", width=180, height=180)
    mic_frame.place(x=-25, y=725) 

    mic_canvas = tk.Canvas(
        mic_frame,
        width=180,
        height=180,
        bg="white",
        highlightthickness=0,
        bd=0
    )
    mic_canvas.pack()
    
    mic_canvas.bind("<Button-1>", start_listening_thread) 
    mic_frame.bind("<Button-1>", start_listening_thread)

    mic_image = Image.open("/home/pi/Test_GUI/microphone/microphone.png").resize((90, 90))
    mic_photo = ImageTk.PhotoImage(mic_image)

    colors = ["#E0B0FF", "#C77DFF", "#9D4EDD"]
    radii = [80, 60, 40]

    for i, (color, radius) in enumerate(zip(colors, radii)):
        circle = mic_canvas.create_oval(
            90 - radius, 90 - radius,
            90 + radius, 90 + radius,
            fill="",
            outline=color,
            width=3,
            tags="aura"
        )
        aura_circles.append((circle, radius)) 

    mic_canvas.create_image(90, 90, image=mic_photo, tags="mic")
    mic_canvas.image = mic_photo

    def animate_aura():
        global is_listening, alpha_value, direction, mic_canvas, aura_circles
        
        if is_listening:
            base_color_hex = ["#FFD700", "#FFA500", "#FF4500"] 
            speed = 3.5
            border_width = 4
        else:
            base_color_hex = ["#E0B0FF", "#C77DFF", "#9D4EDD"] 
            speed = 1.5
            border_width = 3
        
        alpha_value[0] += direction[0] * speed

        if alpha_value[0] >= 100:
            alpha_value[0] = 100
            direction[0] = -1
        elif alpha_value[0] <= 0:
            alpha_value[0] = 0
            direction[0] = 1

        intensity = alpha_value[0] / 100.0
        
        colors_animated = []
        for hex_color in base_color_hex:
            r_base = int(hex_color[1:3], 16)
            g_base = int(hex_color[3:5], 16)
            b_base = int(hex_color[5:7], 16)
            
            r_final = int(r_base * (0.6 + 0.4 * intensity)) 
            g_final = int(g_base * (0.6 + 0.4 * intensity))
            b_final = int(b_base * (0.6 + 0.4 * intensity))
            
            r_final = min(255, r_final)
            g_final = min(255, g_final)
            b_final = min(255, b_final)
            
            colors_animated.append(f"#{r_final:02x}{g_final:02x}{b_final:02x}")


        for i, (circle, _) in enumerate(aura_circles):
            mic_canvas.itemconfig(circle, outline=colors_animated[i], width=border_width)

        root.after(16, animate_aura)

    animate_aura()
    mic_frame.lift()

except Exception as e:
    print_status(f"ไม่พบรูปไมค์ หรือเกิดข้อผิดพลาดในการสร้างออร่า: {e}")


# --- รูปแฟนเพจตรงกลาง (ย้ายไปอยู่บน home_content_frame) ---
try:
    fanpage_image = Image.open("/home/pi/Test_GUI/Facebook/FF.png").resize((950, 400))
    fanpage_ctk_image = ctk.CTkImage(light_image=fanpage_image, dark_image=fanpage_image, size=(950,400))
    fanpage_label = ctk.CTkLabel(home_content_frame, image=fanpage_ctk_image, text="")
    fanpage_label.pack(pady=(50, 10))
except Exception as e:
    print_status(f"ไม่พบรูปแฟนเพจ: {e}")

# --- ข้อความ: แผนผังภายในวิทยาลัย (ย้ายไปอยู่บน home_content_frame) ---
plan_label = ctk.CTkLabel(home_content_frame, text="แผนผังภายในวิทยาลัย", font=("Kanit", 32, "bold"))
plan_label.pack(pady=(0, 20))


# --- ส่วนแสดงแผนผังพร้อมจุดกระพริบ (ย้ายไปอยู่บน home_content_frame) ---
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
    map_image_path = "/home/pi/Test_GUI/Tower/1.png" 
    original_map_image = Image.open(map_image_path)

    map_image_resized = original_map_image.resize((MAP_WIDTH, MAP_HEIGHT), Image.LANCZOS)
    map_photo = ImageTk.PhotoImage(map_image_resized) 
    
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
# ** การเริ่มต้นแสดงหน้าจอและการสไลด์รูปภาพ **
# ***************************************************************

# เริ่มต้นการโหลดและการสไลด์รูปภาพ
root.after(100, load_slide_images)
root.after(200, animate_image_slide)

# แสดงหน้าหลักเป็นหน้าแรก
show_frame(home_content_frame) 

root.mainloop()
