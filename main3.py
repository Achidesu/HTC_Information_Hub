import customtkinter as ctk 
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps 
import tkinter as tk 
import speech_recognition as sr 
import threading 
import time 
import os 

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

# ***************************************************************
# ** 1. KEYWORDS (สำหรับ Speech Recognition) **
# ***************************************************************
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

# ***************************************************************
# ** 2. DEPARTMENT_INFO (รวมข้อมูลแผนกไว้ในที่เดียว) **
# ***************************************************************
# โครงสร้าง: 
# "ชื่อแผนก": (Trigger_Image, Animation_GIF, Distance, Time, Dept_Image_Path, Header_Color)
# ---------------------------------------------------------------
# Path รูปภาพแผนก (สมมติว่าอยู่ในโฟลเดอร์เดียวกัน)
DEPT_IMAGE_PATH_BASE = "/home/pi/Test_GUI/Picture_slide/"

DEPARTMENT_INFO = {
    "แผนกวิชาช่างก่อสร้าง": ("B11.jpg", "s2.gif", 120, 3, DEPT_IMAGE_PATH_BASE + "ช่างก่อสร้าง.jpg", "#FF8C00"), # DarkOrange
    "แผนกวิชาช่างโยธา": ("B9.jpg", "s2.gif", 150, 4, DEPT_IMAGE_PATH_BASE + "ช่างโยธา.jpg", "#A52A2A"), # Brown
    "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน": ("B12.jpg", "s14.gif", 180, 5, DEPT_IMAGE_PATH_BASE + "ช่างเฟอร์นิเจอร์และตกแต่งภายใน.jpg", "#D2691E"), # Chocolate
    "แผนกวิชาช่างสำรวจ": ("B6.jpg", "s8.gif", 200, 6, DEPT_IMAGE_PATH_BASE + "ช่างสำรวจ.jpg", "#556B2F"), # DarkOliveGreen
    "แผนกวิชาสถาปัตยกรรม": ("B6.jpg", "s8.gif", 200, 6, DEPT_IMAGE_PATH_BASE + "สถาปัตยกรรม.jpg", "#708090"), # SlateGray
    "แผนกวิชาช่างยนต์": ("B15.jpg", "s5.gif", 100, 3, DEPT_IMAGE_PATH_BASE + "ช่างยนต์.jpg", "#DC143C"), # Crimson
    "แผนกวิชาช่างกลโรงงาน": ("B16.jpg", "s6.gif", 90, 2, DEPT_IMAGE_PATH_BASE + "ช่างกลโรงงาน.jpg", "#4682B4"), # SteelBlue
    "แผนกวิชาช่างเชื่อมโลหะ": ("B17.jpg", "s9.gif", 110, 3, DEPT_IMAGE_PATH_BASE + "ช่างเชื่อมโลหะ.jpg", "#FF4500"), # OrangeRed
    "แผนกวิชาช่างเทคนิคพื้นฐาน": ("B1.jpg", "s12.gif", 130, 3, DEPT_IMAGE_PATH_BASE + "ช่างเทคนิคพื้นฐาน.jpg", "#BDB76B"), # DarkKhaki
    "แผนกวิชาช่างไฟฟ้า": ("B10.jpg", "s2.gif", 140, 4, DEPT_IMAGE_PATH_BASE + "ช่างไฟฟ้า.jpg", "#FFD700"), # Gold
    "แผนกวิชาช่างอิเล็กทรอนิกส์": ("B8.jpg", "s1.gif", 160, 4, DEPT_IMAGE_PATH_BASE + "อิเล็กทรอนิกส์.jpg", "#87CEFA"), # LightSkyBlue (สีเดิม)
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ": ("B2.jpg", "s10.gif", 180, 5, DEPT_IMAGE_PATH_BASE + "เครื่องทำความเย็นและปรับอากาศ.jpg", "#00BFFF"), # DeepSkyBlue
    "แผนกวิชาเทคโนโลยีสารสนเทศ": ("B13.jpg", "s6.gif", 170, 4, DEPT_IMAGE_PATH_BASE + "เทคโนโลยีสารสนเทศ.jpg", "#9370DB"), # MediumPurple
    "แผนกวิชาเทคโนโลยีปิโตรเลียม": ("B88.jpg", "s11.gif", 190, 5, DEPT_IMAGE_PATH_BASE + "เทคโนโลยีปิโตรเลียม.jpg", "#32CD32"), # LimeGreen
    "แผนกวิชาเทคนิคพลังงาน": ("B3.jpg", "s7.gif", 200, 6, DEPT_IMAGE_PATH_BASE + "เทคนิคพลังงาน.jpg", "#3CB371"), # MediumSeaGreen
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": ("s15.jpeg", "s13.gif", 160, 4, DEPT_IMAGE_PATH_BASE + "การจัดการโลจิสติกส์ซัพพลายเชน.jpg", "#20B2AA"), # LightSeaGreen
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง": ("B14.jpg", "s4.gif", 210, 6, DEPT_IMAGE_PATH_BASE + "เทคนิคควบคุมระบบขนส่งทางราง.jpg", "#6A5ACD"), # SlateBlue
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": ("B3.1.jpg", "s7.gif", 200, 5, DEPT_IMAGE_PATH_BASE + "เมคคาทรอนิกส์และหุ่นยนต์.jpg", "#BA55D3"), # MediumOrchid
    "แผนกวิชาแผนกการบิน": ("s15.jpeg", "s13.gif", 160, 4, DEPT_IMAGE_PATH_BASE + "แผนกการบิน.jpg", "#4169E1"), # RoyalBlue
    "แผนกวิชาเทคโนโลยีคอมพิวเตอร์": ("w11.jpg", "w11.jpg", 180, 2, DEPT_IMAGE_PATH_BASE + "เทคโนโลยีคอมพิวเตอร์.jpg", "#8A2BE2") # BlueViolet
}

# ***************************************************************
# ** 3. DEPARTMENT_WAYPOINTS (พิกัดเส้นทาง) **
# ***************************************************************
# !!! TODO: คุณต้องอัปเดตพิกัดเหล่านี้ตามแผนที่จริงของคุณ !!!
# พิกัดเริ่มต้น (จุดเครื่อง) คือ (570, 390)
# ---------------------------------------------------------------
DEPARTMENT_WAYPOINTS = {
    "แผนกวิชาช่างอิเล็กทรอนิกส์": [570, 390, 400, 390, 400, 300, 250, 200, 150, 180], # (พิกัดจริง)
    "แผนกวิชาช่างก่อสร้าง": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาช่างโยธา": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาช่างสำรวจ": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาสถาปัตยกรรม": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาช่างยนต์": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาช่างกลโรงงาน": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาช่างเชื่อมโลหะ": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาช่างเทคนิคพื้นฐาน": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาช่างไฟฟ้า": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาเทคโนโลยีสารสนเทศ": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาเทคโนโลยีปิโตรเลียม": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาเทคนิคพลังงาน": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาแผนกการบิน": [570, 390, 500, 350, 450, 350], # (พิกัดสมมติ - ต้องแก้ไข)
    "แผนกวิชาเทคโนโลยีคอมพิวเตอร์": [570, 390, 500, 350, 450, 350] # (พิกัดสมมติ - ต้องแก้ไข)
}


# ** Global Variables สำหรับ Image Slides **
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

# ** Global Variables สำหรับการนำทางเฉพาะ **
NAVIGATION_TRIGGER_IMAGE = "60 ปี.jpg" 
NAVIGATION_DISPLAY_MAP_PATH = "/home/pi/Test_GUI/Tower/1.png"
MAX_NAVIGATION_MAP_HEIGHT = 750 

# ** Global Variables สำหรับขนาดแผนที่ (ใช้ร่วมกัน) **
GENERAL_MAP_PATH = "/home/pi/Test_GUI/Tower/1.png"
MAP_DISPLAY_WIDTH = 1152 # ขนาดที่ Canvas จะวาด (ตามตัวอย่างอิเล็กฯ)
MAP_DISPLAY_HEIGHT = 648 # ขนาดที่ Canvas จะวาด (ตามตัวอย่างอิเล็กฯ)
DEPT_IMAGE_WIDTH = 950 
DEPT_IMAGE_HEIGHT = 400 
FOOTSTEPS_ICON_PATH = "/home/pi/Test_GUI/icons/footsteps.png"


# ** Global UI Components (ประกาศไว้ด้านบนเพื่อเข้าถึงใน show_frame) **
image_slide_frame = None
survey_frame = None
credit_frame = None
bottom_bar = None
fanpage_ctk_image_global = None 

# ***************************************************************
# ** 4. สร้างเฟรมสำหรับสลับหน้า (Frame Switching) **
# ***************************************************************
home_content_frame = ctk.CTkFrame(root, fg_color="white")
navigation_content_frame = ctk.CTkFrame(root, fg_color="white")

# --- NEW: สร้างเฟรมสำหรับทุกแผนก ---
electronics_content_frame = ctk.CTkFrame(root, fg_color="white")
construction_content_frame = ctk.CTkFrame(root, fg_color="white")
civil_content_frame = ctk.CTkFrame(root, fg_color="white")
furniture_content_frame = ctk.CTkFrame(root, fg_color="white")
survey_content_frame = ctk.CTkFrame(root, fg_color="white")
architecture_content_frame = ctk.CTkFrame(root, fg_color="white")
auto_content_frame = ctk.CTkFrame(root, fg_color="white")
factory_content_frame = ctk.CTkFrame(root, fg_color="white")
welding_content_frame = ctk.CTkFrame(root, fg_color="white")
basictech_content_frame = ctk.CTkFrame(root, fg_color="white") # (ช่างเทคนิคพื้นฐาน)
electric_content_frame = ctk.CTkFrame(root, fg_color="white")
aircond_content_frame = ctk.CTkFrame(root, fg_color="white")
it_content_frame = ctk.CTkFrame(root, fg_color="white")
petroleum_content_frame = ctk.CTkFrame(root, fg_color="white")
energy_content_frame = ctk.CTkFrame(root, fg_color="white")
logistics_content_frame = ctk.CTkFrame(root, fg_color="white")
rail_content_frame = ctk.CTkFrame(root, fg_color="white")
mechatronics_content_frame = ctk.CTkFrame(root, fg_color="white")
aviation_content_frame = ctk.CTkFrame(root, fg_color="white")
comtech_content_frame = ctk.CTkFrame(root, fg_color="white")

# --- NEW: รวมเฟรมแผนกทั้งหมดไว้ใน List เพื่อจัดการง่ายขึ้น ---
all_department_frames = [
    electronics_content_frame, construction_content_frame, civil_content_frame,
    furniture_content_frame, survey_content_frame, architecture_content_frame,
    auto_content_frame, factory_content_frame, welding_content_frame,
    basictech_content_frame, electric_content_frame, aircond_content_frame,
    it_content_frame, petroleum_content_frame, energy_content_frame,
    logistics_content_frame, rail_content_frame, mechatronics_content_frame,
    aviation_content_frame, comtech_content_frame
]


# ***************************************************************
# ** 5. อัปเดตฟังก์ชัน `show_frame` (สำคัญมาก) **
# ***************************************************************
def show_frame(frame_to_show):
    """ฟังก์ชันสลับเฟรมที่แสดงบนหน้าจอหลัก (root) และจัดการการแสดงผลของส่วนล่าง"""
    global image_slide_frame, survey_frame, credit_frame, bottom_bar, all_department_frames
    
    # ซ่อนเฟรมเนื้อหาทั้งหมด
    home_content_frame.pack_forget()
    navigation_content_frame.pack_forget()
    
    # --- NEW: ซ่อนเฟรมแผนกทั้งหมด ---
    for frame in all_department_frames:
        frame.pack_forget()
    
    # -------------------------------------------------------------
    # จัดการการแสดงผลของส่วนล่าง (Bottom Widgets)
    # -------------------------------------------------------------
    
    if frame_to_show == home_content_frame:
        # 1. หน้าหลัก: แสดงทุกอย่าง
        if image_slide_frame: image_slide_frame.pack(side="bottom", fill="x", pady=(0, 0))
        if survey_frame: survey_frame.pack(side="bottom", fill="x", pady=(0, 0))
        if credit_frame: credit_frame.pack(side="bottom", fill="x")
        if bottom_bar: bottom_bar.pack(side="bottom", fill="x")
        
    elif frame_to_show in all_department_frames:
        # 2. หน้าแผนก: ซ่อน Image Slide (เพื่อให้มีที่สำหรับแผนผัง)
        if image_slide_frame: image_slide_frame.pack_forget()
        if survey_frame: survey_frame.pack(side="bottom", fill="x", pady=(0, 0))
        if credit_frame: credit_frame.pack(side="bottom", fill="x")
        if bottom_bar: bottom_bar.pack(side="bottom", fill="x")
        
    elif frame_to_show == navigation_content_frame:
        # 3. หน้านำทาง (60 ปี): ซ่อนเกือบหมด
        if image_slide_frame: image_slide_frame.pack_forget()
        if survey_frame: survey_frame.pack_forget()
        if credit_frame: credit_frame.pack_forget()
        if bottom_bar: bottom_bar.pack(side="bottom", fill="x")
             
    # แสดงเฟรมที่ต้องการ
    frame_to_show.pack(side="top", fill="both", expand=True)
             
    # ยก Top Bar และ Mic Frame ขึ้นมาด้านบนสุดเสมอ
    top_bar.lift()
    try:
        if mic_frame is not None:
            if frame_to_show != navigation_content_frame:
                 mic_frame.lift() 
            else:
                 mic_frame.lower(top_bar) 
    except:
        pass

# --- ฟังก์ชันช่วยเหลือในการพิมพ์สถานะ ---
def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

# ***************************************************************
# ** 6. ฟังก์ชันแม่แบบ (Reusable Function) สำหรับสร้างหน้าแผนก **
# ***************************************************************

def create_department_page(
    target_frame: ctk.CTkFrame,
    dept_name: str,
    header_color: str,
    dept_image_path: str,
    map_path: str,
    waypoints: list,
    distance: int,
    time: int
):
    """
    ฟังก์ชันแม่แบบสำหรับสร้าง UI ของหน้าแผนกวิชา
    (ดัดแปลงมาจากโค้ด show_electronics_page() เดิมของคุณ)
    """
    
    # ล้างเนื้อหาเก่าในเฟรมเป้าหมาย
    for widget in target_frame.winfo_children():
        widget.destroy()

    # ตรวจสอบ Waypoints
    if not waypoints or len(waypoints) < 4:
        print_status(f"*** [ERROR] Waypoints สำหรับ {dept_name} ไม่ถูกต้อง ต้องมีอย่างน้อย 2 จุด (4 พิกัด) ***")
        # ใช้พิกัดเริ่มต้นเป็นค่าสำรอง
        WAYPOINTS = [570, 390, 570, 390]
    else:
        WAYPOINTS = waypoints
        
    START_X, START_Y = WAYPOINTS[0], WAYPOINTS[1]
    END_X, END_Y = WAYPOINTS[-2], WAYPOINTS[-1]
    
    # ***************************************************
    # ** สร้างเนื้อหาสำหรับหน้าแผนก (ตามแม่แบบ) **
    # ***************************************************
    
    # 1. Header (ใช้สีตามพารามิเตอร์)
    header_frame = ctk.CTkFrame(target_frame, height=150, fg_color=header_color)
    header_frame.pack(side="top", fill="x")
    
    ctk.CTkLabel(header_frame, 
                 text=dept_name, 
                 font=("Kanit", 36, "bold"),
                 text_color="white").pack(pady=(50, 20), padx=20) 
                 
    # 2. (NEW) กรอบแสดงข้อมูล (ระยะทาง, เวลา)
    info_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
    info_frame.pack(pady=(10, 5))
    
    try:
        footsteps_img = Image.open(FOOTSTEPS_ICON_PATH).resize((30, 30))
        footsteps_ctk_img = ctk.CTkImage(light_image=footsteps_img, dark_image=footsteps_img, size=(30, 30))
        ctk.CTkLabel(info_frame, image=footsteps_ctk_img, text="").pack(side="left", padx=(0, 10))
    except Exception as e:
        print_status(f"ไม่พบไอคอน footsteps: {e}")

    info_text = f"ระยะทางประมาณ {distance} เมตร  |  ใช้เวลาเดิน {time} นาที"
    ctk.CTkLabel(info_frame, 
                 text=info_text, 
                 font=("Kanit", 24, "bold"),
                 text_color="#4B0082").pack(side="left") # Indigo
                 
    # 3. รูปภาพแผนก
    try:
         if os.path.exists(dept_image_path):
             dept_img = Image.open(dept_image_path)
             dept_img_resized = dept_img.resize((DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT), Image.LANCZOS)
             dept_ctk_image = ctk.CTkImage(light_image=dept_img_resized, dark_image=dept_img_resized, size=(DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT))
             
             ctk.CTkLabel(target_frame, 
                          image=dept_ctk_image, 
                          text="").pack(pady=(20, 10))
         else:
             print_status(f"*** [WARNING] ไม่พบรูปภาพแผนก: {dept_image_path} ***")
             ctk.CTkLabel(target_frame, 
                      text="[พื้นที่สำหรับรูปภาพแผนก]", 
                      font=("Kanit", 24)).pack(pady=(20, 10))
    except Exception as e:
         print_status(f"ไม่พบรูปภาพแผนก {dept_name}: {e}")
         ctk.CTkLabel(target_frame, 
                      text="[พื้นที่สำหรับรูปภาพแผนก]", 
                      font=("Kanit", 24)).pack(pady=(20, 10))

    # 4. กรอบสำหรับข้อความนำทาง
    guide_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
    guide_frame.pack(pady=(10, 5))
    ctk.CTkLabel(guide_frame, 
                 text="โปรดเดินตามเส้นทางที่กำหนดในแผนผังนี้ (เส้นประสีน้ำเงิน)", 
                 font=("Kanit", 22, "bold"), 
                 text_color="#8000FF").pack(side="left")

    # 5. แผนผังการเดิน (Map Image) พร้อมเส้นประ
    try:
        map_img = Image.open(map_path)
        map_img_resized = map_img.resize((MAP_DISPLAY_WIDTH, MAP_DISPLAY_HEIGHT), Image.LANCZOS)
        map_tk_img = ImageTk.PhotoImage(map_img_resized) 
        
        map_container_frame = ctk.CTkFrame(
            target_frame, 
            fg_color="white", 
            width=MAP_DISPLAY_WIDTH, 
            height=MAP_DISPLAY_HEIGHT
        )
        map_container_frame.pack(pady=10)
        
        map_canvas = tk.Canvas(
            map_container_frame,
            width=MAP_DISPLAY_WIDTH,
            height=MAP_DISPLAY_HEIGHT,
            bg="white",
            highlightthickness=0,
            bd=0
        )
        map_canvas.pack()
        map_canvas.create_image(0, 0, image=map_tk_img, anchor="nw")
        map_canvas.image = map_tk_img 

        # --- วาดเส้นประ Waypoints ---
        map_canvas.create_line(
            *WAYPOINTS, 
            fill="#0000FF", 
            width=7, 
            dash=(15, 8), 
            smooth=True 
        )
        
        # --- วาดจุดเริ่มต้น (เขียว) ---
        blink_radius = 15 
        map_canvas.create_oval(
            START_X - blink_radius, START_Y - blink_radius, 
            START_X + blink_radius, START_Y + blink_radius, 
            fill="#00C000", outline="white", width=4
        )
        
        # --- วาดจุดเป้าหมาย (แดง) ---
        map_canvas.create_oval(
            END_X - blink_radius, END_Y - blink_radius, 
            END_X + blink_radius, END_Y + blink_radius, 
            fill="#FF0000", outline="white", width=4
        )
        
        # --- ข้อความใต้แผนผัง ---
        ctk.CTkLabel(target_frame, 
                 text=f"เส้นทางนำทาง: จุดเริ่มต้น (เขียว) ไปยัง {dept_name} (แดง)", 
                 font=("Kanit", 18),
                 text_color="#00AA00").pack(pady=(5, 10))
        
    except FileNotFoundError:
        ctk.CTkLabel(target_frame, 
                     text=f"⚠️ ไม่พบรูปภาพแผนผัง '{map_path}' ⚠️", 
                     font=("Kanit", 24), text_color="red").pack(pady=20)
    except Exception as e:
        ctk.CTkLabel(target_frame, 
                     text=f"⚠️ ข้อผิดพลาดในการโหลดรูปภาพ: {e} ⚠️", 
                     font=("Kanit", 24), text_color="red").pack(pady=20)

    # 6. ปุ่มกลับสู่หน้าหลัก
    ctk.CTkButton(target_frame, 
                  text="❮ กลับสู่หน้าหลัก", 
                  command=lambda: show_frame(home_content_frame), 
                  font=("Kanit", 28, "bold"),
                  fg_color="#00C000",
                  hover_color="#008000",
                  width=250,
                  height=70,
                  corner_radius=15).pack(pady=(20, 40))
                  
    # (สำคัญ) ไม่ต้องเรียก show_frame ที่นี่ 
    # ปล่อยให้ฟังก์ชัน wrapper (เช่น show_electronics_page) เป็นคนเรียก

# ***************************************************************
# ** 7. ฟังก์ชัน Wrapper (สำหรับเรียกใช้โดยปุ่ม/เสียง) **
# ***************************************************************
# นี่คือฟังก์ชันที่จะถูกเรียกโดยตรงจาก Event (เช่น การคลิกสไลด์ หรือ คำสั่งเสียง)

def show_electronics_page():
    dept_name = "แผนกวิชาช่างอิเล็กทรอนิกส์"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=electronics_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4], 
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(electronics_content_frame)

def show_construction_page():
    dept_name = "แผนกวิชาช่างก่อสร้าง"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=construction_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(construction_content_frame)

def show_civil_page():
    dept_name = "แผนกวิชาช่างโยธา"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=civil_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(civil_content_frame)

def show_furniture_page():
    dept_name = "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=furniture_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(furniture_content_frame)

def show_survey_page():
    dept_name = "แผนกวิชาช่างสำรวจ"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=survey_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(survey_content_frame)

def show_architecture_page():
    dept_name = "แผนกวิชาสถาปัตยกรรม"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=architecture_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(architecture_content_frame)

def show_auto_page():
    dept_name = "แผนกวิชาช่างยนต์"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=auto_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(auto_content_frame)

def show_factory_page():
    dept_name = "แผนกวิชาช่างกลโรงงาน"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=factory_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(factory_content_frame)

def show_welding_page():
    dept_name = "แผนกวิชาช่างเชื่อมโลหะ"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=welding_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(welding_content_frame)

def show_basictech_page():
    dept_name = "แผนกวิชาช่างเทคนิคพื้นฐาน"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=basictech_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(basictech_content_frame)

def show_electric_page():
    dept_name = "แผนกวิชาช่างไฟฟ้า"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=electric_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(electric_content_frame)

def show_aircond_page():
    dept_name = "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=aircond_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(aircond_content_frame)

def show_it_page():
    dept_name = "แผนกวิชาเทคโนโลยีสารสนเทศ"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=it_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(it_content_frame)

def show_petroleum_page():
    dept_name = "แผนกวิชาเทคโนโลยีปิโตรเลียม"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=petroleum_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(petroleum_content_frame)

def show_energy_page():
    dept_name = "แผนกวิชาเทคนิคพลังงาน"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=energy_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(energy_content_frame)

def show_logistics_page():
    dept_name = "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=logistics_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(logistics_content_frame)

def show_rail_page():
    dept_name = "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=rail_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(rail_content_frame)

def show_mechatronics_page():
    dept_name = "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=mechatronics_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(mechatronics_content_frame)

def show_aviation_page():
    dept_name = "แผนกวิชาแผนกการบิน"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=aviation_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(aviation_content_frame)

def show_comtech_page():
    dept_name = "แผนกวิชาเทคโนโลยีคอมพิวเตอร์"
    info = DEPARTMENT_INFO[dept_name]
    waypoints = DEPARTMENT_WAYPOINTS[dept_name]
    create_department_page(
        target_frame=comtech_content_frame,
        dept_name=dept_name,
        header_color=info[5],
        dept_image_path=info[4],
        map_path=GENERAL_MAP_PATH,
        waypoints=waypoints,
        distance=info[2],
        time=info[3]
    )
    show_frame(comtech_content_frame)


# -----------------------------------------------------------------
# --- ฟังก์ชันควบคุมหน้าต่างนำทางเฉพาะ (60 ปี.jpg) ---
# -----------------------------------------------------------------

def show_navigation_page():
    """
    แสดงเนื้อหานำทางบนหน้าจอหลัก (Full Screen) 
    *** โหลดรูปภาพแผนผังจาก /home/pi/Test_GUI/Tower/1.png ***
    """
    global NAVIGATION_DISPLAY_MAP_PATH, MAX_NAVIGATION_MAP_HEIGHT
    
    for widget in navigation_content_frame.winfo_children():
        widget.destroy()
        
    # ***************************************************
    # ** สร้างเนื้อหาสำหรับหน้าแผนที่นำทาง (Full Screen Content) **
    # ***************************************************

    # 1. ส่วนหัวและปุ่มย้อนกลับ
    back_button_frame = ctk.CTkFrame(navigation_content_frame, fg_color="transparent", height=120)
    back_button_frame.pack(side="top", fill="x", pady=(30, 0), padx=40)
    
    # ปุ่มกลับสู่หน้าหลัก
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
                  
    # หัวข้อใหญ่
    ctk.CTkLabel(navigation_content_frame, 
                 text="🗺️ แผนผังภายในวิทยาลัย 🗺️", 
                 font=("Kanit", 48, "bold"),
                 text_color="#FF4500").pack(pady=(40, 20))
                 
    # --- NEW: พื้นที่สำหรับรูปภาพแผนที่ (ตรงกลาง) ---
    map_image_label = ctk.CTkLabel(navigation_content_frame, text="", fg_color="white")
    map_image_label.pack(pady=(0, 0), padx=20, fill="both", expand=True) 
    
    # โหลดและปรับขนาดรูปภาพ
    try:
        map_path_to_load = NAVIGATION_DISPLAY_MAP_PATH 
        original_map_img = Image.open(map_path_to_load)
        
        print_status(f"--- [NAVIGATION MAP]: โหลดรูปภาพแผนผัง: {map_path_to_load} ---")

        # ฟังก์ชันปรับขนาดและแสดงผล (ปรับปรุงการ resize)
        def resize_and_display_map():
            target_width = map_image_label.winfo_width()
            target_height = map_image_label.winfo_height()
            
            if target_width > 0 and target_height > 0:
                print_status(f"--- [NAVIGATION MAP]: Container size {target_width}x{target_height} ---")
                
                original_width, original_height = original_map_img.size
                
                max_h = min(target_height, MAX_NAVIGATION_MAP_HEIGHT) 
                
                ratio_w = target_width / original_width
                ratio_h = max_h / original_height
                
                final_ratio = min(ratio_w, ratio_h)
                
                new_width = int(original_width * final_ratio)
                new_height = int(original_height * final_ratio)
                
                if new_width <= 0 or new_height <= 0:
                      root.after(100, resize_and_display_map) 
                      return
                      
                print_status(f"--- [NAVIGATION MAP]: Resizing map to {new_width}x{new_height} ---")

                resized_img = original_map_img.resize((new_width, new_height), Image.LANCZOS)
                map_tk_img = ImageTk.PhotoImage(resized_img)
                
                map_image_label.configure(image=map_tk_img, text="")
                map_image_label.image = map_tk_img 
                
                if hasattr(map_image_label, 'image_item_id'):
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
        print_status(f"--- [NAVIGATION MAP ERROR]: ไม่พบรูปภาพแผนที่: {map_path_to_load} ---")
        map_image_label.configure(
            text=f"⚠️ ไม่พบไฟล์รูปภาพแผนที่ '{map_path_to_load}' ⚠️",
            font=("Kanit", 32, "bold"),
            text_color="red",
            fg_color="#FFF0F0"
        )
    except Exception as e:
        print_status(f"--- [NAVIGATION MAP ERROR]: เกิดข้อผิดพลาดในการโหลดรูปภาพ: {e} ---")
        map_image_label.configure(
            text=f"⚠️ ข้อผิดพลาดในการแสดงผลรูปภาพ: {e} ⚠️",
            font=("Kanit", 28),
            text_color="red",
            fg_color="#FFF0F0"
        )
                 
    show_frame(navigation_content_frame) 

# ***************************************************************
# ** 8. อัปเดตฟังก์ชัน Speech Recognition **
# ***************************************************************

# --- NEW: สร้าง Dictionary สำหรับจับคู่ Keyword กับฟังก์ชัน ---
KEYWORD_TO_FUNCTION = {
    tuple(KEYWORDS_ELECTRONICS): show_electronics_page,
    tuple(KEYWORDS_CONSTRUCTION): show_construction_page,
    tuple(KEYWORDS_CIVIL): show_civil_page,
    tuple(KEYWORDS_FURNITURE): show_furniture_page,
    tuple(KEYWORDS_SURVEY): show_survey_page,
    tuple(KEYWORDS_ARCHITECT): show_architecture_page,
    tuple(KEYWORDS_AUTO): show_auto_page,
    tuple(KEYWORDS_FACTORY): show_factory_page,
    tuple(KEYWORDS_WELDING): show_welding_page,
    tuple(KEYWORDS_BASICTECH): show_basictech_page,
    tuple(KEYWORDS_ELECTRIC): show_electric_page,
    tuple(KEYWORDS_AIRCOND): show_aircond_page,
    tuple(KEYWORDS_IT): show_it_page,
    tuple(KEYWORDS_PETROLEUM): show_petroleum_page,
    tuple(KEYWORDS_ENERGY): show_energy_page,
    tuple(KEYWORDS_LOGISTICS): show_logistics_page,
    tuple(KEYWORDS_RAIL): show_rail_page,
    tuple(KEYWORDS_MECHATRONICS): show_mechatronics_page,
    tuple(KEYWORDS_AIRLINE): show_aviation_page,
    tuple(KEYWORDS_COMPUTER_TECH): show_comtech_page
}

def listen_for_speech():
    """ฟังก์ชันหลักในการรับเสียงจากไมค์และแปลงเป็นข้อความ (เวอร์ชันอัปเดต)"""
    global is_listening, KEYWORD_TO_FUNCTION
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
            text_lower = text.lower() # แปลงเป็นตัวเล็กครั้งเดียว
            
            print("\n*** [RECOGNIZED TEXT] ***")
            print(f"ผลลัพธ์: {text}")
            print("***************************\n")
            
            found_command = False
            
            # --- NEW: วนลูปตรวจสอบ Keyword ทั้งหมด ---
            for keywords_tuple, function_to_call in KEYWORD_TO_FUNCTION.items():
                for keyword in keywords_tuple:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' กำลังเรียกฟังก์ชัน {function_to_call.__name__} ---")
                        root.after(0, function_to_call) # เรียกฟังก์ชันที่จับคู่ไว้
                        found_command = True
                        break # ออกจากลูป keyword
                if found_command:
                    break # ออกจากลูปหลัก
            
            if not found_command:
                print_status(f"--- [SYSTEM]: ไม่พบคำสั่งที่ตรงกันสำหรับ: '{text}' ---")
            
        except sr.WaitTimeoutError:
            print_status("--- [MIC ERROR]: ไม่ได้รับเสียงภายใน 7 วินาที ---")
        except sr.UnknownValueError:
            print_status("--- [MIC ERROR]: ไม่สามารถเข้าใจคำพูด (UnknownValueError) ---")
        except sr.RequestError as e:
            print_status(f"--- [MIC ERROR]: ไม่สามารถเชื่อมต่อกับ Google Speech (ตรวจสอบอินเทอร์เน็ต); {e} ---")
        except Exception as e:
            print_status(f"--- [MIC ERROR]: เกิดข้อผิดพลาดในการประมวลผล: {e} ---") 
            
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
        
        # ขอบซ้ายของรูปภาพแรกในรายการ
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


# ***************************************************************
# ** 9. อัปเดตฟังก์ชัน Image Slide (load, place_next, place_previous) **
# ***************************************************************

# --- NEW: สร้าง Dictionary สำหรับจับคู่ Trigger Image กับฟังก์ชัน ---
# (เราดึงข้อมูลนี้มาจาก DEPARTMENT_INFO ที่สร้างไว้ตอนต้น)
TRIGGER_IMAGE_TO_FUNCTION = {
    NAVIGATION_TRIGGER_IMAGE: show_navigation_page
}

# วนลูปเพื่อสร้าง Dictionary อัตโนมัติ
for dept_name, info_tuple in DEPARTMENT_INFO.items():
    trigger_image_filename = info_tuple[0]
    
    # หาฟังก์ชันที่ตรงกับชื่อแผนก (เช่น 'show_electronics_page')
    # เราต้องใช้ globals() เพื่อค้นหาฟังก์ชันจากชื่อ string
    function_name = f"show_{dept_name.split('แผนกวิชา')[-1].replace(' ', '').replace('่', '').replace('้', '').replace('๊', '').replace('๋', '').replace('ิ', '').replace('ี', '').replace('ึ', '').replace('ื', '').replace('ุ', '').replace('ู', '').replace('เ', '').replace('แ', '').replace('ไ', '').replace('ใ', '').replace('โ', '').replace('ำ', '').replace('ฯ', '').replace('(', '').replace(')', '').lower()}_page"
    
    # สร้างชื่อฟังก์ชันแบบ Manual (ปลอดภัยกว่า)
    # นี่คือส่วนที่ต้องทำด้วยมือเล็กน้อยเพื่อให้แน่ใจว่าชื่อตรงกัน
    dept_func_map = {
        "แผนกวิชาช่างอิเล็กทรอนิกส์": show_electronics_page,
        "แผนกวิชาช่างก่อสร้าง": show_construction_page,
        "แผนกวิชาช่างโยธา": show_civil_page,
        "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน": show_furniture_page,
        "แผนกวิชาช่างสำรวจ": show_survey_page,
        "แผนกวิชาสถาปัตยกรรม": show_architecture_page,
        "แผนกวิชาช่างยนต์": show_auto_page,
        "แผนกวิชาช่างกลโรงงาน": show_factory_page,
        "แผนกวิชาช่างเชื่อมโลหะ": show_welding_page,
        "แผนกวิชาช่างเทคนิคพื้นฐาน": show_basictech_page,
        "แผนกวิชาช่างไฟฟ้า": show_electric_page,
        "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ": show_aircond_page,
        "แผนกวิชาเทคโนโลยีสารสนเทศ": show_it_page,
        "แผนกวิชาเทคโนโลยีปิโตรเลียม": show_petroleum_page,
        "แผนกวิชาเทคนิคพลังงาน": show_energy_page,
        "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": show_logistics_page,
        "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง": show_rail_page,
        "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": show_mechatronics_page,
        "แผนกวิชาแผนกการบิน": show_aviation_page,
        "แผนกวิชาเทคโนโลยีคอมพิวเตอร์": show_comtech_page
    }

    if dept_name in dept_func_map:
        # ใช้ชื่อไฟล์รูปภาพเป็น Key และฟังก์ชันเป็น Value
        if trigger_image_filename not in TRIGGER_IMAGE_TO_FUNCTION:
             TRIGGER_IMAGE_TO_FUNCTION[trigger_image_filename] = dept_func_map[dept_name]
        else:
             # กรณีที่หลายแผนกใช้รูปเดียวกัน (เช่น สำรวจ และ สถาปัตย์)
             # เราจะเก็บเป็น list ของฟังก์ชัน (ซับซ้อนไป)
             # หรือ ให้มันเรียกฟังก์ชันแรกที่เจอก็พอ (ง่ายกว่า)
             pass 
    else:
        print_status(f"*** [CONFIG ERROR] ไม่พบฟังก์ชันสำหรับแผนก: {dept_name} ***")

print("--- [SYSTEM] Trigger Images Mapped to Functions: ---")
for img_name, func in TRIGGER_IMAGE_TO_FUNCTION.items():
    print(f"{img_name} -> {func.__name__}")
print("--------------------------------------------------")


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
            
            # --- ปรับขนาดรูปภาพ ---
            if original_height > target_image_height:
                ratio = target_image_height / original_height
                new_width = int(original_width * ratio)
                img = img.resize((new_width, target_image_height), Image.LANCZOS)
            else:
                target_image_height = original_height 
                
            # --- ตรวจสอบความกว้าง (จำกัดความกว้างของ *ตัวรูปภาพ*) ---
            target_image_width_limit = IMAGE_SLIDE_WIDTH_LIMIT - (SLIDE_FRAME_WIDTH * 2)
            if img.width > target_image_width_limit:
                 ratio = target_image_width_limit / img.width
                 new_height = int(img.height * ratio)
                 img = img.resize((target_image_width_limit, new_height), Image.LANCZOS)

            # --- เพิ่มกรอบ (Frame) ให้กับรูปภาพ ---
            img = ImageOps.expand(img, border=SLIDE_FRAME_WIDTH, fill=SLIDE_FRAME_COLOR)
            # ------------------------------------------------

            slide_images.append(img)
            slide_photo_images.append({
                'photo': ImageTk.PhotoImage(img),
                'filename': filename # <-- เราใช้ชื่อไฟล์นี้เป็น Key
            })

            print_status(f"--- [IMAGE SLIDE]: โหลดรูปภาพ (รวมกรอบ): {filename} ({img.width}x{img.height}) ---")

        except Exception as e:
            print_status(f"--- [IMAGE SLIDE ERROR]: ไม่สามารถโหลดรูปภาพ {filename}: {e} ---")

    if not slide_images:
        print_status("--- [IMAGE SLIDE]: ไม่พบรูปภาพที่สามารถโหลดได้ ---")

def place_next_slide(start_immediately_at_right_edge=False):
    """วางรูปภาพสไลด์ถัดไปบน Canvas โดยเว้นช่องไฟ (เวอร์ชันอัปเดต)"""
    global current_slide_index, image_slide_canvas, slide_photo_images, slide_images
    global next_image_x_placement, active_slide_items, SLIDE_GAP, TRIGGER_IMAGE_TO_FUNCTION

    if not slide_photo_images or not image_slide_canvas:
        return

    # 1. กำหนด Index ของรูปภาพถัดไป (เหมือนเดิม)
    if active_slide_items:
        last_slide_index = active_slide_items[-1]['slide_index']
        next_slide_index = (last_slide_index + 1) % len(slide_photo_images)
    else:
        next_slide_index = (current_slide_index + 1) % len(slide_photo_images)
    
    image_data = slide_photo_images[next_slide_index] 
    image_to_place = slide_images[next_slide_index]
    image_width = image_to_place.width
    image_photo = image_data['photo']
    image_filename = image_data['filename'] # <-- ชื่อไฟล์

    # 2. คำนวณตำแหน่ง X (เหมือนเดิม)
    if start_immediately_at_right_edge:
        start_x_center = 1080 + image_width / 2
    else:
        start_x_center = next_image_x_placement + SLIDE_GAP + image_width / 2

    canvas_item_id = image_slide_canvas.create_image(
        start_x_center, IMAGE_SLIDE_HEIGHT // 2, 
        image=image_photo, 
        anchor="center"
    )

    # 3. อัปเดต Global Placement (เหมือนเดิม)
    next_image_x_placement = start_x_center + image_width / 2 
    active_slide_items.append({
        'id': canvas_item_id, 
        'width': image_width, 
        'photo': image_photo, 
        'right_edge': next_image_x_placement,
        'slide_index': next_slide_index 
    })
    current_slide_index = next_slide_index
    
    # 4. --- NEW: Bind event โดยใช้ Dictionary ---
    if image_filename in TRIGGER_IMAGE_TO_FUNCTION:
        # ดึงฟังก์ชันที่ถูกต้องมาจาก Dictionary
        function_to_call = TRIGGER_IMAGE_TO_FUNCTION[image_filename]
        
        # สร้างฟังก์ชัน lambda ที่เรียกฟังก์ชันนั้นๆ
        def handle_click(event, func=function_to_call):
            if not is_dragging: 
                root.after(0, func)
        
        image_slide_canvas.tag_bind(
            canvas_item_id, 
            '<Button-1>', 
            handle_click
        )
    # -----------------------------------------------

def place_previous_slide():
    """วางรูปภาพสไลด์ 'ก่อนหน้า' บน Canvas ทางด้านซ้าย (เวอร์ชันอัปเดต)"""
    global image_slide_canvas, slide_photo_images, slide_images
    global active_slide_items, SLIDE_GAP, TRIGGER_IMAGE_TO_FUNCTION

    if not active_slide_items or not image_slide_canvas or not slide_photo_images:
        return
        
    # 1. คำนวณ Index (เหมือนเดิม)
    current_first_index = active_slide_items[0]['slide_index']
    prev_slide_index = (current_first_index - 1 + len(slide_photo_images)) % len(slide_photo_images)
    if active_slide_items[0]['slide_index'] == prev_slide_index:
        return 
    
    image_data = slide_photo_images[prev_slide_index]
    image_to_place = slide_images[prev_slide_index]
    image_width = image_to_place.width
    image_photo = image_data['photo']
    image_filename = image_data['filename'] # <-- ชื่อไฟล์
    
    # 3. คำนวณตำแหน่ง X (เหมือนเดิม)
    first_item = active_slide_items[0]
    coords = image_slide_canvas.coords(first_item['id'])
    current_x_center = coords[0]
    first_item_left_edge = current_x_center - (first_item['width'] / 2)
    new_x_center = first_item_left_edge - SLIDE_GAP - (image_width / 2)
    
    # 4. สร้าง Item บน Canvas (เหมือนเดิม)
    canvas_item_id = image_slide_canvas.create_image(
        new_x_center, IMAGE_SLIDE_HEIGHT // 2, 
        image=image_photo, 
        anchor="center"
    )

    # 5. เพิ่มเข้า List (เหมือนเดิม)
    new_item = {
        'id': canvas_item_id, 
        'width': image_width, 
        'photo': image_photo, 
        'right_edge': new_x_center + image_width / 2,
        'slide_index': prev_slide_index 
    }
    active_slide_items.insert(0, new_item)

    # 6. --- NEW: Bind event โดยใช้ Dictionary ---
    if image_filename in TRIGGER_IMAGE_TO_FUNCTION:
        function_to_call = TRIGGER_IMAGE_TO_FUNCTION[image_filename]
        
        def handle_click(event, func=function_to_call):
            if not is_dragging: 
                root.after(0, func)
        
        image_slide_canvas.tag_bind(
            canvas_item_id, 
            '<Button-1>', 
            handle_click
        )
    # -----------------------------------------------

    print_status(f"--- [SLIDE CONTROL]: เพิ่มรูปภาพก่อนหน้า Index {prev_slide_index} สำเร็จ ---")


def animate_image_slide():
    """ควบคุมการสไลด์ต่อเนื่องและการจัดการรายการรูปภาพ"""
    global image_slide_canvas, active_slide_items, next_image_x_placement, SLIDE_GAP
    global is_dragging 

    if not image_slide_canvas or not slide_images:
        root.after(25, animate_image_slide)
        return

    # *** MODIFICATION: จะเลื่อนอัตโนมัติก็ต่อเมื่อ is_dragging เป็น False เท่านั้น ***
    if not is_dragging:
        if not active_slide_items:
            # เริ่มต้นการโหลด
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

        # ลบรูปที่ออกนอกจอ (ทางซ้าย)
        if active_slide_items and active_slide_items[0]['right_edge'] < 0:
            item_to_remove = active_slide_items.pop(0)
            image_slide_canvas.delete(item_to_remove['id'])

        # เพิ่มรูปใหม่ (ทางขวา)
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
    text="ความคิดเห็นของท่านมีค่ามากสำหรับเรา\nกรุณาสแกน QR Code เพื่อทำแบบสอบถาม",
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