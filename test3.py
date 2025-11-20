import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps 
import tkinter as tk 
import speech_recognition as sr 
import threading 
import time 
import os

# --- กำหนดค่า Path (สมมติว่าไฟล์รูปภาพทั้งหมดอยู่ในโฟลเดอร์นี้) ---
# ต้องกำหนด DEPT_IMAGE_PATH_BASE ให้ตรงกับตำแหน่งไฟล์จริงบนเครื่องที่ใช้งาน
DEPT_IMAGE_PATH_BASE = "/home/pi/Test_GUI/Picture_slide/" 

# --- ตั้งค่า appearance และ theme ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --- สร้างหน้าต่างหลัก ---
root = ctk.CTk()
root.title("HTC Smart Hub")
#root.attributes('-fullscreen', True) # สำหรับโหมด Fullscreen จริง
root.geometry("1080x1920") # ใช้ขนาดมาตรฐานสำหรับหน้าจอสัมผัสแนวตั้ง
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

# --- คำสั่งเสียงทั้งหมด ---
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
    
NAVIGATION_TRIGGER_IMAGE = "60 ปี.jpg" 
NAVIGATION_DISPLAY_MAP_PATH = "/home/pi/Test_GUI/Tower/1.png" # แผนที่หลักสำหรับหน้า Guided Map

# --------------------------------------------------------------------------------------------------
# ** Mappings for Department Images and Video Maps (ตามที่ผู้ใช้ระบุ) **
# --------------------------------------------------------------------------------------------------
# [Image File (for slide/dept page), Video Map File (for dept page map placeholder)]
DEPT_FILE_MAPPING = {
    "แผนกวิชาช่างอิเล็กทรอนิกส์": ("B8.jpg", "z11.mp4"),
    "แผนกวิชาช่างก่อสร้าง": ("B11.jpg", "z4.mp4"),
    "แผนกวิชาช่างโยธา": ("B9.jpg", "z4.mp4"),
    "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน": ("B12.jpg", "z13.mp4"),
    "แผนกวิชาช่างสำรวจ": ("B6.jpg", "z6.mp4"),
    "แผนกวิชาสถาปัตยกรรม": ("B6.jpg", "z6.mp4"), 
    "แผนกวิชาช่างยนต์": ("B15.jpg", "z8.mp4"),
    "แผนกวิชาช่างกลโรงงาน": ("B16.jpg", "z9.mp4"),
    "แผนกวิชาช่างเชื่อมโลหะ": ("B17.jpg", "z7.mp4"),
    "แผนกวิชาช่างเทคนิคพื้นฐาน": ("B1.jpg", "z1.mp4"),
    "แผนกวิชาช่างไฟฟ้า": ("B10.jpg", "z4.mp4"),
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ": ("B2.jpg", "z3.mp4"),
    "แผนกวิชาเทคโนโลยีสารสนเทศ": ("B13.jpg", "z9.mp4"),
    "แผนกวิชาเทคโนโลยีปิโตรเลียม": ("B88.jpg", "z2.mp4"),
    "แผนกวิชาเทคนิคพลังงาน": ("B3.jpg", "z5.mp4"),
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": ("s15.jpeg", "z12.mp4"),
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง": ("B14.jpg", "z.mp4"),
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": ("B3.jpg", "z5.mp4"), 
    "แผนกวิชาแผนกการบิน": ("s15.jpeg", "z12.mp4"), 
    "แผนกวิชาเทคโนโลยีคอมพิวเตอร์": ("w11.jpg", "z10.mp4"),
}
# --------------------------------------------------------------------------------------------------

# Default appearance settings for departments
DEFAULTS = {
    "แผนกวิชาช่างอิเล็กทรอนิกส์": (160, 4, "#87CEFA"), 
    "แผนกวิชาช่างก่อสร้าง": (120, 3, "#FF8C00"), 
    "แผนกวิชาช่างโยธา": (150, 4, "#A52A2A"), 
    "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน": (180, 5, "#D2691E"), 
    "แผนกวิชาช่างสำรวจ": (200, 6, "#556B2F"), 
    "แผนกวิชาสถาปัตยกรรม": (200, 6, "#708090"), 
    "แผนกวิชาช่างยนต์": (100, 3, "#DC143C"), 
    "แผนกวิชาช่างกลโรงงาน": (90, 2, "#4682B4"), 
    "แผนกวิชาช่างเชื่อมโลหะ": (110, 3, "#FF4500"), 
    "แผนกวิชาช่างเทคนิคพื้นฐาน": (130, 3, "#BDB76B"), 
    "แผนกวิชาช่างไฟฟ้า": (140, 4, "#FFD700"), 
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ": (180, 5, "#00BFFF"), 
    "แผนกวิชาเทคโนโลยีสารสนเทศ": (170, 4, "#9370DB"), 
    "แผนกวิชาเทคโนโลยีปิโตรเลียม": (190, 5, "#32CD32"), 
    "แผนกวิชาเทคนิคพลังงาน": (200, 6, "#3CB371"), 
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": (160, 4, "#20B2AA"), 
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง": (210, 6, "#6A5ACD"), 
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": (200, 5, "#BA55D3"), 
    "แผนกวิชาแผนกการบิน": (160, 4, "#4169E1"), 
    "แผนกวิชาเทคโนโลยีคอมพิวเตอร์": (180, 2, "#8A2BE2") 
}

DEPARTMENTS_CONFIG = {}
for dept_name, (img_file, video_file) in DEPT_FILE_MAPPING.items():
    size, duration, color = DEFAULTS.get(dept_name, (160, 4, "#87CEFA"))
    # Format: (IMG_FILE_SLIDE, IMG_FILE_DEPT, SIZE, DURATION, FULL_PATH, COLOR)
    DEPARTMENTS_CONFIG[dept_name] = (img_file, img_file, size, duration, os.path.join(DEPT_IMAGE_PATH_BASE, img_file), color)


# ** Waypoints for all 20 departments **
WAYPOINTS_BASE = [545, 500] 
WAYPOINTS_FAR_TOP_LEFT = [545, 500, 350, 400, 200, 250, 100, 150] 
WAYPOINTS_FAR_TOP_RIGHT = [545, 500, 650, 400, 800, 250, 900, 150] 
WAYPOINTS_FAR_BOTTOM_LEFT = [545, 500, 400, 600, 250, 750, 100, 850] 
WAYPOINTS_FAR_BOTTOM_RIGHT = [545, 500, 600, 650, 800, 750, 950, 850] 

WAYPOINTS_DEPARTMENTS = {
    "แผนกวิชาช่างอิเล็กทรอนิกส์": [545, 500, 400, 390, 400, 300, 250, 200, 150, 180], 
    "แผนกวิชาช่างก่อสร้าง": [545, 500, 700, 450, 800, 550, 950, 520, 900, 400], 
    "แผนกวิชาช่างโยธา": WAYPOINTS_FAR_TOP_RIGHT, 
    "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน": [545, 500, 750, 400, 850, 250, 700, 150, 600, 200], 
    "แผนกวิชาช่างสำรวจ": WAYPOINTS_FAR_TOP_RIGHT, 
    "แผนกวิชาสถาปัตยกรรม": WAYPOINTS_FAR_TOP_RIGHT, 
    "แผนกวิชาช่างยนต์": WAYPOINTS_FAR_TOP_LEFT, 
    "แผนกวิชาช่างกลโรงงาน": WAYPOINTS_FAR_TOP_LEFT, 
    "แผนกวิชาช่างเชื่อมโลหะ": WAYPOINTS_FAR_TOP_LEFT, 
    "แผนกวิชาช่างเทคนิคพื้นฐาน": [545, 500, 600, 400, 700, 300, 800, 250], 
    "แผนกวิชาช่างไฟฟ้า": [545, 500, 500, 600, 300, 650, 100, 600, 80, 500], 
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ": WAYPOINTS_FAR_TOP_LEFT, 
    "แผนกวิชาเทคโนโลยีสารสนเทศ": WAYPOINTS_FAR_BOTTOM_RIGHT, 
    "แผนกวิชาเทคโนโลยีปิโตรเลียม": [545, 500, 650, 600, 800, 700, 950, 650, 1000, 750], 
    "แผนกวิชาเทคนิคพลังงาน": WAYPOINTS_FAR_BOTTOM_LEFT, 
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": WAYPOINTS_FAR_BOTTOM_LEFT, 
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง": [545, 500, 450, 250, 300, 150, 100, 200], 
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": WAYPOINTS_FAR_TOP_LEFT, 
    "แผนกวิชาแผนกการบิน": WAYPOINTS_FAR_BOTTOM_LEFT, 
    "แผนกวิชาเทคโนโลยีคอมพิวเตอร์": WAYPOINTS_FAR_BOTTOM_RIGHT, 
}

# *** Global Variables สำหรับ Image Slides ***
IMAGE_SLIDE_FOLDER = DEPT_IMAGE_PATH_BASE 
IMAGE_SLIDE_HEIGHT = 300 
IMAGE_SLIDE_WIDTH_LIMIT = 900 
SLIDE_GAP = 55 
SLIDE_FRAME_WIDTH = 5 
SLIDE_FRAME_COLOR = "black" 
slide_photo_images = [] 
image_slide_canvas = None 
active_slide_items = []
last_x = 0
is_dragging = False

# ** Global UI Components **
home_content_frame = ctk.CTkFrame(root, fg_color="white")
electronics_content_frame = ctk.CTkFrame(root, fg_color="white")
navigation_content_frame = ctk.CTkFrame(root, fg_color="white")
image_slide_frame = None
survey_frame = None
credit_frame = None
bottom_bar = None

# -----------------------------------------------------------------
# --- ฟังก์ชันควบคุมหน้าต่างนำทางแบบมีเส้นทาง (Guided Page) ---
# -----------------------------------------------------------------
def show_frame(frame_to_show):
    """ฟังก์ชันสลับเฟรมที่แสดงบนหน้าจอหลัก (root) และจัดการการแสดงผลของส่วนล่าง"""
    global image_slide_frame, survey_frame, credit_frame, bottom_bar
    
    home_content_frame.pack_forget()
    electronics_content_frame.pack_forget()
    navigation_content_frame.pack_forget()
    
    should_show_slides = (frame_to_show == home_content_frame)
    should_show_survey_credit = (frame_to_show != navigation_content_frame) # ซ่อนทั้งหมดเมื่อเป็น Full Screen Map
    
    if image_slide_frame:
        if should_show_slides:
            image_slide_frame.pack(side="bottom", fill="x", pady=(0, 0))
        else:
            image_slide_frame.pack_forget()

    for widget in [survey_frame, credit_frame]:
        if widget:
            if should_show_survey_credit:
                widget.pack(side="bottom", fill="x", pady=(0, 0) if widget == survey_frame else 0)
            else:
                widget.pack_forget()
            
    if bottom_bar: bottom_bar.pack(side="bottom", fill="x") 
             
    frame_to_show.pack(side="top", fill="both", expand=True)
             
    top_bar.lift()
    try:
        if mic_frame is not None:
            if frame_to_show != navigation_content_frame: 
                 mic_frame.lift() 
            else:
                 mic_frame.lower(top_bar)
    except:
        pass

def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")


def show_guided_page(title, header_bg_color, dept_image_path, waypoints, video_map_file): 
    """
    แสดงเนื้อหาแผนก/กิจกรรมแบบมีเส้นทางนำทาง (Guided Page)
    """
    # ... (โค้ด show_guided_page เหมือนเดิม) ...
    
    MAP_DISPLAY_WIDTH_ELEC = 1152
    MAP_DISPLAY_HEIGHT_ELEC = 648
    DEPT_IMAGE_WIDTH = 950 
    DEPT_IMAGE_HEIGHT = 400 

    # ล้างเนื้อหาเก่า
    for widget in electronics_content_frame.winfo_children():
        widget.destroy() 

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
    
    # 1. Header 
    header_frame = ctk.CTkFrame(electronics_content_frame, height=150, fg_color=header_bg_color)
    header_frame.pack(side="top", fill="x")
    ctk.CTkLabel(header_frame, text=title, font=("Kanit", 36, "bold"), text_color="white").pack(pady=(50, 20), padx=20) 
             
    # 2. รูปภาพแผนก
    try:
         if os.path.exists(dept_image_path):
             dept_img = Image.open(dept_image_path)
             dept_img_resized = dept_img.resize((DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT), Image.LANCZOS)
             dept_ctk_image = ctk.CTkImage(light_image=dept_img_resized, dark_image=dept_img_resized, size=(DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT))
             ctk.CTkLabel(electronics_content_frame, image=dept_ctk_image, text="").pack(pady=(20, 10))
         else:
             ctk.CTkLabel(electronics_content_frame, text=f"[ไม่พบรูปภาพ: {os.path.basename(dept_image_path)}]", font=("Kanit", 24)).pack(pady=(20, 10))
    except Exception as e:
         print_status(f"ไม่พบรูปภาพแผนก: {e}")
         ctk.CTkLabel(electronics_content_frame, text="[พื้นที่สำหรับรูปภาพ]", font=("Kanit", 24)).pack(pady=(20, 10))


    # 3. กรอบสำหรับข้อความนำทาง
    guide_frame = ctk.CTkFrame(electronics_content_frame, fg_color="transparent")
    guide_frame.pack(pady=(10, 5))
    ctk.CTkLabel(guide_frame, 
                 text="โปรดเดินตามเส้นทางที่กำหนดในแผนผังนี้ (เส้นประสีน้ำเงิน)", 
                 font=("Kanit", 22, "bold"), 
                 text_color="#8000FF").pack(side="left")

    # 4. แผนผังการเดิน (Map Image) พร้อมเส้นประ และการแจ้งเตือนเรื่องวิดีโอ
    video_alert = ctk.CTkLabel(electronics_content_frame, 
                             text=f"*** ⚠️ แผนที่เดิมถูกแทนที่ด้วยวิดีโอ '{video_map_file}' (ไม่สามารถเล่นต่อเนื่องได้ในระบบนี้) ⚠️ ***", 
                             font=("Kanit", 18, "bold"), 
                             text_color="#FF0000")
    video_alert.pack(pady=(5, 5))
    
    try:
        map_img = Image.open(NAVIGATION_DISPLAY_MAP_PATH)
        map_img_resized = map_img.resize((MAP_DISPLAY_WIDTH_ELEC, MAP_DISPLAY_HEIGHT_ELEC), Image.LANCZOS)
        map_tk_img = ImageTk.PhotoImage(map_img_resized)
        
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
       
        map_canvas.create_image(0, 0, image=map_tk_img, anchor="nw")
        map_canvas.image = map_tk_img 

        # วาดเส้นประแสดงเส้นทางการเดินแบบหลายจุด (Waypoints)
        map_canvas.create_line(
             *waypoints, 
             fill="blue", 
             width=6, 
             dash=(20, 10), 
             arrow=tk.LAST, 
             arrowshape=(30, 40, 10)
        )
        
        # วาดจุด Start/End
        map_canvas.create_oval(START_X - 15, START_Y - 15, START_X + 15, START_Y + 15, fill="green", outline="white", width=3)
        map_canvas.create_text(START_X, START_Y, text="START", fill="white", font=("Kanit", 10, "bold"))
        map_canvas.create_oval(END_X - 15, END_Y - 15, END_X + 15, END_Y + 15, fill="red", outline="white", width=3)
        map_canvas.create_text(END_X, END_Y, text="END", fill="white", font=("Kanit", 10, "bold"))
        
    except FileNotFoundError:
        ctk.CTkLabel(electronics_content_frame, text=f"⚠️ ไม่พบไฟล์รูปแผนผัง '{NAVIGATION_DISPLAY_MAP_PATH}' ⚠️", font=("Kanit", 24), text_color="red").pack(pady=20)
    except Exception as e:
        ctk.CTkLabel(electronics_content_frame, text=f"⚠️ ข้อผิดพลาดในการโหลดรูปภาพ: {e} ⚠️", font=("Kanit", 24), text_color="red").pack(pady=20)

    # 5. ปุ่มกลับ
    ctk.CTkButton(electronics_content_frame, 
                  text="❮ กลับสู่หน้าหลัก", 
                  command=lambda: show_frame(home_content_frame), 
                  font=("Kanit", 28, "bold"), 
                  fg_color="#00C000", 
                  hover_color="#008000", 
                  width=250, height=70, 
                  corner_radius=15).pack(pady=(20, 40))

    show_frame(electronics_content_frame)

# -----------------------------------------------------------------
# ** NEW: Function Generators and Mappings (แก้ไขส่วนนี้) **
# -----------------------------------------------------------------

# NEW: Mapping Department Name to its Handler Function object
DEPT_FUNCTION_MAPPING = {} 

def generate_dept_wrapper(dept_name):
    """Generates the show_..._page function for a given department name."""
    
    if dept_name not in DEPARTMENTS_CONFIG:
        print_status(f"Configuration not found for: {dept_name}")
        return lambda: print_status(f"Error: No config for {dept_name}")

    config_data = DEPARTMENTS_CONFIG[dept_name]
    header_bg_color = config_data[5]
    dept_image_path = config_data[4]
    waypoints = WAYPOINTS_DEPARTMENTS.get(dept_name, WAYPOINTS_BASE)
    # DEPT_FILE_MAPPING[dept_name] is a tuple (img_file, video_file)
    video_map_file = DEPT_FILE_MAPPING[dept_name][1] 

    def show_dept_page():
        print_status(f"--- [SYSTEM]: นำทางไปยังหน้าแผนก: {dept_name} ---")
        show_guided_page(
            title=dept_name,
            header_bg_color=header_bg_color,
            dept_image_path=dept_image_path,
            waypoints=waypoints,
            video_map_file=video_map_file 
        )
        
    # Set a more user-friendly name for debugging/inspection (optional but good)
    show_dept_page.__name__ = f"show_{dept_name.replace('แผนกวิชา', '').replace(' ', '_')}_page"
    
    return show_dept_page

# 1. Create all 20 department wrapper functions and map them to the full department name
for dept_name in DEPT_FILE_MAPPING.keys():
    handler_func = generate_dept_wrapper(dept_name)
    DEPT_FUNCTION_MAPPING[dept_name] = handler_func

# 2. Define the list for Voice Command Mapping
VOICE_COMMAND_MAPPING_LIST = [
    (KEYWORDS_ELECTRONICS, "แผนกวิชาช่างอิเล็กทรอนิกส์"),
    (KEYWORDS_CONSTRUCTION, "แผนกวิชาช่างก่อสร้าง"),
    (KEYWORDS_CIVIL, "แผนกวิชาช่างโยธา"),
    (KEYWORDS_FURNITURE, "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน"),
    (KEYWORDS_SURVEY, "แผนกวิชาช่างสำรวจ"),
    (KEYWORDS_ARCHITECT, "แผนกวิชาสถาปัตยกรรม"),
    (KEYWORDS_AUTO, "แผนกวิชาช่างยนต์"),
    (KEYWORDS_FACTORY, "แผนกวิชาช่างกลโรงงาน"),
    (KEYWORDS_WELDING, "แผนกวิชาช่างเชื่อมโลหะ"),
    (KEYWORDS_BASICTECH, "แผนกวิชาช่างเทคนิคพื้นฐาน"),
    (KEYWORDS_ELECTRIC, "แผนกวิชาช่างไฟฟ้า"),
    (KEYWORDS_AIRCOND, "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ"),
    (KEYWORDS_IT, "แผนกวิชาเทคโนโลยีสารสนเทศ"),
    (KEYWORDS_PETROLEUM, "แผนกวิชาเทคโนโลยีปิโตรเลียม"),
    (KEYWORDS_ENERGY, "แผนกวิชาเทคนิคพลังงาน"),
    (KEYWORDS_LOGISTICS, "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน"),
    (KEYWORDS_RAIL, "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง"),
    (KEYWORDS_MECHATRONICS, "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์"),
    (KEYWORDS_AIRLINE, "แผนกวิชาแผนกการบิน"),
    (KEYWORDS_COMPUTER_TECH, "แผนกวิชาเทคโนโลยีคอมพิวเตอร์"),
]

# 3. Build the final VOICE_COMMAND_MAPPING dynamically
VOICE_COMMAND_MAPPING = {}
for keywords, dept_name in VOICE_COMMAND_MAPPING_LIST:
    if dept_name in DEPT_FUNCTION_MAPPING:
        VOICE_COMMAND_MAPPING[tuple(keywords)] = DEPT_FUNCTION_MAPPING[dept_name]


def show_60_years_page():
    """ฟังก์ชัน Wrapper สำหรับการแสดงหน้า 60 ปี"""
    GOLD_BACKGROUND = "#FFD700" 
    waypoints = WAYPOINTS_DEPARTMENTS.get("แผนกวิชาช่างอิเล็กทรอนิกส์", WAYPOINTS_BASE) # ใช้ Waypoints Default
    
    show_guided_page(
        title="60 ปี วิทยาลัยเทคนิคหาดใหญ่",
        header_bg_color=GOLD_BACKGROUND,
        dept_image_path=os.path.join(IMAGE_SLIDE_FOLDER, NAVIGATION_TRIGGER_IMAGE), 
        waypoints=waypoints,
        video_map_file="No Video Map"
    )

def show_navigation_page():
    """ ฟังก์ชันเดิมสำหรับแสดงแผนผังนำทางแบบ Full Screen """
    # ... (โค้ด show_navigation_page เหมือนเดิม) ...
    MAX_NAVIGATION_MAP_HEIGHT = 750 
    for widget in navigation_content_frame.winfo_children():
        widget.destroy()
    back_button_frame = ctk.CTkFrame(navigation_content_frame, fg_color="transparent", height=120)
    back_button_frame.pack(side="top", fill="x", pady=(30, 0), padx=40)
    ctk.CTkButton(back_button_frame, text="❮ กลับสู่หน้าหลัก", command=lambda: show_frame(home_content_frame), font=("Kanit", 28, "bold"), fg_color="#FF4500", hover_color="#CC3700", width=250, height=70, corner_radius=15).pack(side="left")

    try:
        map_img = Image.open(NAVIGATION_DISPLAY_MAP_PATH)
        scale_ratio = 1080 / map_img.width
        new_width = 1080
        new_height = int(map_img.height * scale_ratio)

        if new_height > MAX_NAVIGATION_MAP_HEIGHT:
            new_height = MAX_NAVIGATION_MAP_HEIGHT
            scale_ratio = new_height / map_img.height
            new_width = int(map_img.width * scale_ratio)
        
        map_img_resized = map_img.resize((new_width, new_height), Image.LANCZOS)
        map_photo = ImageTk.PhotoImage(map_img_resized)
        
        map_canvas_widget = tk.Canvas(navigation_content_frame, 
                                      width=new_width, 
                                      height=new_height, 
                                      bg="white", 
                                      highlightthickness=0, bd=0)
        map_canvas_widget.pack(pady=20)
        
        map_canvas_widget.create_image(0, 0, image=map_photo, anchor="nw")
        map_canvas_widget.image = map_photo 
        
    except Exception as e:
        ctk.CTkLabel(navigation_content_frame, text=f"⚠️ ไม่พบไฟล์รูปแผนผัง '{NAVIGATION_DISPLAY_MAP_PATH}' หรือเกิดข้อผิดพลาดในการโหลด: {e} ⚠️", font=("Kanit", 24), text_color="red").pack(pady=20)

    show_frame(navigation_content_frame)

# -----------------------------------------------------------------
# --- ฟังก์ชัน Speech Recognition และ MIC Animation ---
# -----------------------------------------------------------------
def reset_mic_icon():
    """รีเซ็ตไอคอนไมค์เป็นสถานะปกติ"""
    global is_listening
    is_listening = False
    if mic_canvas:
        for circle in aura_circles:
            mic_canvas.delete(circle)
        aura_circles.clear()
        mic_canvas.create_image(90, 90, image=mic_photo)

def animate_listening():
    """สร้างเอฟเฟกต์ออร่าเมื่อกำลังฟัง"""
    global alpha_value, direction
    
    if not is_listening:
        return

    alpha_value[0] += direction[0] * 0.05
    if alpha_value[0] >= 1.0 or alpha_value[0] <= 0.0:
        direction[0] *= -1 
        
    if len(aura_circles) < 3: 
        radius = 45 + int(alpha_value[0] * 30)
        colors = ["#E0B0FF", "#C77DFF", "#9D4EDD"]
        color_index = len(aura_circles) % len(colors)
        fill_color = colors[color_index]
        
        circle = mic_canvas.create_oval(90 - radius, 90 - radius, 90 + radius, 90 + radius,
                                        outline=fill_color, width=3)
        aura_circles.append(circle)
        
    if len(aura_circles) > 3:
        mic_canvas.delete(aura_circles.pop(0))

    mic_canvas.tag_raise(mic_canvas.find_all()[-1])
    
    root.after(100, animate_listening)

def start_listening_thread(event=None):
    """เริ่มกระบวนการฟังเสียงในเธรดแยก"""
    global is_listening
    if is_listening:
        print_status("--- [MIC]: กำลังรอการประมวลผลคำสั่งเดิม... ---")
        return
    
    print_status("--- [MIC]: เริ่มกระบวนการฟัง... ---")
    is_listening = True
    reset_mic_icon()
    animate_listening()
    
    threading.Thread(target=listen_and_process, daemon=True).start()

def listen_and_process():
    """ฟังก์ชันหลักสำหรับรับเสียงและประมวลผลคำสั่ง"""
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source)
    except Exception as e:
        print_status(f"--- [MIC ERROR]: ไม่สามารถเข้าถึงไมโครโฟน: {e} ---")
        root.after(0, reset_mic_icon)
        return

    try:
        with mic as source:
            print_status("--- [MIC]: กำลังรอคำสั่งเสียง (จำกัด 7 วินาที)... ---")
            audio = r.listen(source, timeout=7)
    except sr.WaitTimeoutError:
        print_status("--- [MIC ERROR]: ไม่ได้รับเสียงภายใน 7 วินาที ---")
        root.after(0, reset_mic_icon)
        return
    except Exception as e:
        print_status(f"--- [MIC ERROR]: เกิดข้อผิดพลาดในการฟัง: {e} ---")
        root.after(0, reset_mic_icon)
        return
        
    try:
        text = r.recognize_google(audio, language="th-TH")
        handle_speech_command(text)
    except sr.UnknownValueError:
        print_status("--- [MIC ERROR]: ไม่สามารถเข้าใจคำพูด (UnknownValueError) ---")
    except sr.RequestError as e:
        print_status(f"--- [MIC ERROR]: ไม่สามารถเชื่อมต่อกับ Google Speech; Error: {e} ---")
    finally:
        root.after(0, reset_mic_icon)
        
def handle_speech_command(text):
    """ฟังก์ชันสำหรับประมวลผลคำสั่งเสียงเพื่อนำทาง"""
    global is_listening
    text_lower = text.lower().replace(" ", "")
    print_status(f"--- [MIC] ได้ยิน: '{text}' (ตรวจสอบ: '{text_lower}') ---")

    # 1. ตรวจสอบคำสั่ง "กลับ"
    if "กลับ" in text_lower or "home" in text_lower:
        print_status("--- [SYSTEM]: ตรวจพบคำสั่ง: 'กลับ' นำทางกลับสู่หน้าหลัก ---")
        root.after(0, lambda: show_frame(home_content_frame))
        return
        
    # 2. ตรวจสอบคำสั่งสำหรับแผนกทั้งหมด (ใช้ Mapping ที่สร้างใหม่)
    for keywords, handler_func in VOICE_COMMAND_MAPPING.items():
        for keyword in keywords:
            if keyword in text_lower: 
                print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางไปยังหน้าแผนก: {handler_func.__name__} ---")
                root.after(0, handler_func)
                return

    # หากไม่พบคำสั่งใด ๆ
    print_status("--- [SYSTEM]: ตรวจไม่พบคำสั่งนำทางที่ตรงกัน ---")


# -------------------------------------------------------------------
# --- Image Slides (แถบเลื่อนด้านล่าง) ---
# -------------------------------------------------------------------

def load_slide_images():
    """โหลดและปรับขนาดรูปภาพทั้งหมดในโฟลเดอร์สำหรับแถบเลื่อน"""
    global slide_photo_images

    slide_photo_images = []
    
    valid_extensions = ('.jpg', '.jpeg', '.png')
    
    # กรองเฉพาะไฟล์ที่อยู่ใน DEPT_FILE_MAPPING เพื่อแสดงเฉพาะแผนกที่กำหนด
    image_files_to_load = [v[0] for v in DEPT_FILE_MAPPING.values()]
    
    # เพิ่มรูป 60 ปี.jpg (Navigation Trigger)
    image_files_to_load.append(NAVIGATION_TRIGGER_IMAGE)
    
    # กรองและจัดเรียงไฟล์ที่มีอยู่จริง
    # ใช้ for loop แทน list comprehension เพื่อให้สามารถโหลดไฟล์ซ้ำได้หากมีการกำหนดไฟล์ซ้ำใน DEPT_FILE_MAPPING 
    # (เช่น B6.jpg สำหรับช่างสำรวจและสถาปัตยกรรม)
    for img_file in image_files_to_load:
        filepath = os.path.join(IMAGE_SLIDE_FOLDER, img_file)
        if os.path.exists(filepath) and img_file.lower().endswith(valid_extensions):
            
            try:
                img = Image.open(filepath)
                original_width, original_height = img.size

                target_image_height = IMAGE_SLIDE_HEIGHT - (SLIDE_FRAME_WIDTH * 2)
                
                # Resize based on height
                if original_height != target_image_height:
                    ratio = target_image_height / original_height
                    new_width = int(original_width * ratio)
                    img = img.resize((new_width, target_image_height), Image.LANCZOS)

                # Limit width (if needed)
                target_image_width_limit = IMAGE_SLIDE_WIDTH_LIMIT - (SLIDE_FRAME_WIDTH * 2)
                if img.width > target_image_width_limit:
                    ratio = target_image_width_limit / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((target_image_width_limit, new_height), Image.LANCZOS)

                # Add border
                img = ImageOps.expand(img, border=SLIDE_FRAME_WIDTH, fill=SLIDE_FRAME_COLOR) 
                
                slide_photo_images.append({
                    'photo': ImageTk.PhotoImage(img),
                    'filename': img_file,
                    'original_dept_name': next((k for k, v in DEPT_FILE_MAPPING.items() if v[0] == img_file), None) # ห้ามใช้ None
                })
                print_status(f"--- [IMAGE SLIDE]: โหลดรูปภาพ: {img_file} ({img.width}x{img.height}) ---")
            except Exception as e:
                print_status(f"--- [IMAGE SLIDE ERROR]: ไม่สามารถโหลดรูปภาพ {img_file}: {e} ---")

    if not slide_photo_images: 
        print_status(f"--- [IMAGE SLIDE]: ไม่พบรูปภาพที่กำหนดในโฟลเดอร์: {IMAGE_SLIDE_FOLDER} ---")
        return


def draw_slides_on_canvas():
    """วาดรูปภาพที่โหลดไว้ทั้งหมดลงบน Canvas และผูกการทำงาน (FIXED)"""
    global image_slide_canvas, active_slide_items, next_image_x_placement

    if not image_slide_canvas or not slide_photo_images:
        return

    image_slide_canvas.delete("all")
    active_slide_items = []
    
    current_x = SLIDE_GAP
    
    # ใช้ DEPT_FILE_MAPPING เพื่อสร้างแผนที่ย้อนกลับ (filename -> dept_name)
    dept_name_map = {}
    for dept_name, (img_file, _) in DEPT_FILE_MAPPING.items():
        # หากมีหลายแผนกใช้รูปเดียวกัน จะเก็บเฉพาะแผนกแรกที่พบ
        if img_file not in dept_name_map:
            dept_name_map[img_file] = dept_name
            
    # วาดรูปภาพทั้งหมด
    for i, slide_data in enumerate(slide_photo_images):
        photo = slide_data['photo']
        filename = slide_data['filename']
        img_width = photo.width()
        img_height = photo.height()
        
        y_pos = IMAGE_SLIDE_HEIGHT // 2
        canvas_item_id = image_slide_canvas.create_image(current_x, y_pos, image=photo, anchor="w")
        active_slide_items.append(canvas_item_id)
        
        # -------------------------------------------------------------------
        # ** FIXED: BIND CLICK HANDLERS **
        # -------------------------------------------------------------------
        
        # 1. ตรวจสอบว่าเป็นรูปภาพแผนกหรือไม่
        dept_name_from_file = dept_name_map.get(filename)

        if dept_name_from_file:
            # ใช้ DEPT_FUNCTION_MAPPING เพื่อค้นหา Handler (FIXED)
            dept_handler = DEPT_FUNCTION_MAPPING.get(dept_name_from_file) 
            
            if dept_handler:
                # ใช้ default argument 'handler=dept_handler' เพื่อ Lock ค่า function handler ใน closure
                def handle_dept_click(event, handler=dept_handler):
                    if not is_dragging:
                        root.after(0, handler)
                
                image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_dept_click)
                print_status(f"--- [SLIDE]: ผูกฟังก์ชันเข้ากับรูปภาพ '{filename}' ({dept_name_from_file}) สำเร็จ ---")
            else:
                 print_status(f"--- [SLIDE ERROR]: ไม่พบฟังก์ชัน handler สำหรับ '{dept_name_from_file}' ---")
                 

        # 2. Handle 60 ปี.jpg
        elif filename == NAVIGATION_TRIGGER_IMAGE:
            def handle_60_years_click(event):
                if not is_dragging:
                    root.after(0, show_60_years_page)
            image_slide_canvas.tag_bind(canvas_item_id, '<Button-1>', handle_60_years_click)
            print_status(f"--- [SLIDE]: ผูกฟังก์ชัน 'show_60_years_page' เข้ากับรูปภาพ '{filename}' สำเร็จ ---")
        
        else:
             print_status(f"--- [SLIDE]: ไม่มีการผูกฟังก์ชันคลิกสำหรับรูปภาพ '{filename}' ---")
             
        # อัปเดตตำแหน่ง x สำหรับรูปภาพถัดไป
        current_x += img_width + SLIDE_GAP

    # กำหนดขนาดของ scroll region
    image_slide_canvas.config(scrollregion=(0, 0, current_x, IMAGE_SLIDE_HEIGHT))
    next_image_x_placement = current_x 

def handle_mouse_down(event):
    """เริ่มลาก (Drag)"""
    global last_x, is_dragging
    last_x = event.x
    is_dragging = False 
    image_slide_canvas.scan_mark(event.x, event.y)

def handle_mouse_move(event):
    """กำลังลาก (Dragging)"""
    global is_dragging
    if abs(event.x - last_x) > 5: 
        is_dragging = True
    image_slide_canvas.scan_dragto(event.x, event.y, gain=1)

def handle_mouse_up(event):
    """สิ้นสุดการลาก (Release)"""
    global is_dragging
    pass

# -------------------------------------------------------------------
# --- UI Initialization (การสร้าง UI) ---
# -------------------------------------------------------------------

# --- 1. Top Bar ---
top_bar = ctk.CTkFrame(root, height=80, fg_color="#0066CC")
top_bar.pack(side="top", fill="x")

try:
    logo_img = Image.open("/home/pi/Test_GUI/icons/33.png").resize((50, 50))
    logo_ctk_image = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(50, 50))
    logo_label = ctk.CTkLabel(top_bar, image=logo_ctk_image, text="")
    logo_label.pack(side="left", padx=10, pady=15)
except Exception as e:
    print_status(f"ไม่พบไฟล์โลโก้ (33.png): {e}")

title_label = ctk.CTkLabel(top_bar, text="HTC Smart Hub", text_color="white", font=("Kanit", 36, "bold"))
title_label.pack(side="left", padx=10, pady=15)

# --- 4. Bottom Bar (ล่างสุด) ---
bottom_bar = ctk.CTkFrame(root, height=45, fg_color="#A070FF")
bottom_bar.pack(side="bottom", fill="x")
bottom_label = ctk.CTkLabel(
    bottom_bar, text="© 2025 HatYai Technical College", font=("Arial", 20, "bold"), text_color="white"
)
bottom_label.pack(pady=5)

# --- 3. Credit / Marquee ---
credit_frame = ctk.CTkFrame(root, height=55, fg_color="#D6B0FF")
credit_frame.pack(side="bottom", fill="x")
canvas = tk.Canvas(
    credit_frame, height=55, bg="#D6B0FF", highlightthickness=0, bd=0,
)
canvas.pack(fill="both", expand=True)
credit_text = "จัดทำโดย นักศึกษา แผนกภาควิชาเทคโนโลยีคอมพิวเตอร์"
try:
    marquee_font = ("Kanit", 26, "bold")
except:
    marquee_font = ("Arial", 26, "bold")
text_id = canvas.create_text(
    1080, 28, text=credit_text, fill="#333333", font=marquee_font, anchor="w"
)
def marquee_animation():
    """ฟังก์ชันสำหรับเลื่อนข้อความ"""
    canvas.move(text_id, -2, 0)
    x1, y1, x2, y2 = canvas.bbox(text_id)
    if x2 < 0:
        text_width = x2 - x1
        canvas.move(text_id, 1080 + text_width, 0)
    root.after(30, marquee_animation)

marquee_animation()

# --- 2. Image Slides ---
image_slide_frame = ctk.CTkFrame(root, height=IMAGE_SLIDE_HEIGHT + 10, fg_color="white") 
image_slide_frame.pack(side="bottom", fill="x")

load_slide_images()

image_slide_canvas = tk.Canvas(
    image_slide_frame, 
    height=IMAGE_SLIDE_HEIGHT, 
    bg="white", 
    highlightthickness=0, bd=0
)
image_slide_canvas.pack(fill="x", padx=10, pady=(5, 5))

draw_slides_on_canvas()

image_slide_canvas.bind("<ButtonPress-1>", handle_mouse_down)
image_slide_canvas.bind("<B1-Motion>", handle_mouse_move)
image_slide_canvas.bind("<ButtonRelease-1>", handle_mouse_up)


# --- 5. Survey Button ---
survey_frame = ctk.CTkFrame(root, height=100, fg_color="white")
survey_frame.pack(side="bottom", fill="x", pady=(0, 0))
survey_button = ctk.CTkButton(
    survey_frame,
    text="แบบสอบถามความพึงพอใจ 📝",
    font=("Kanit", 24, "bold"),
    fg_color="#3399FF",
    hover_color="#0077CC",
    width=350,
    height=60,
    corner_radius=10,
    command=lambda: print_status("--- [SYSTEM]: เปิดหน้าแบบสอบถาม (ไม่ทำงานในโค้ดนี้) ---")
)
survey_button.pack(pady=(15, 20))


# ***************************************************************
# ** UI กลาง (Home Content) **
# ***************************************************************
home_content_frame.pack(side="top", fill="both", expand=True)
home_content_frame.pack_propagate(False)

home_label = ctk.CTkLabel(home_content_frame, 
                          text="ยินดีต้อนรับสู่ HTC Smart Hub", 
                          font=("Kanit", 48, "bold"), 
                          text_color="#0066CC")
home_label.pack(pady=(100, 20))

sub_label = ctk.CTkLabel(home_content_frame, 
                         text="กรุณาแตะปุ่มไมค์เพื่อสั่งการด้วยเสียง หรือแตะรูปภาพด้านล่างเพื่อเลือกแผนกวิชา", 
                         font=("Kanit", 28), 
                         text_color="#333333")
sub_label.pack(pady=(0, 50))

map_nav_button = ctk.CTkButton(home_content_frame, 
                              text="ดูแผนที่นำทางแบบเต็มจอ", 
                              command=show_navigation_page, 
                              font=("Kanit", 28, "bold"), 
                              fg_color="#CC0066", 
                              hover_color="#AA0044", 
                              width=300, 
                              height=80, 
                              corner_radius=15)
map_nav_button.pack(pady=(20, 40))


# === ไอคอนไมค์ ===
try:
    mic_frame = tk.Frame(root, bg="white", width=180, height=180)
    mic_frame.place(x=-25, y=725)
    mic_canvas = tk.Canvas(
        mic_frame, width=180, height=180, bg="white", highlightthickness=0, bd=0
    )
    mic_canvas.pack()
    mic_canvas.bind("<Button-1>", start_listening_thread)
    mic_frame.bind("<Button-1>", start_listening_thread)
    
    mic_image = Image.open("/home/pi/Test_GUI/microphone/microphone.png").resize((90, 90))
    mic_photo = ImageTk.PhotoImage(mic_image)
    
    reset_mic_icon() 
except Exception as e:
    print_status(f"--- [MIC UI ERROR]: ไม่สามารถสร้างไอคอนไมค์: {e} ---")


# ***************************************************************
# ** เริ่มต้นการทำงาน **
# ***************************************************************
if __name__ == "__main__":
    root.mainloop()