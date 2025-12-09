import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps 
import tkinter as tk 
import speech_recognition as sr 
import threading 
import time 
import os 
from tkvideo import tkvideo
from datetime import datetime
import locale

# ตั้งค่า Locale เป็นภาษาไทย
# (ใช้ได้กับระบบปฏิบัติการส่วนใหญ่ที่รองรับ Thai locale)
try:
    # 1. FIX: ลองตั้งค่า locale เป็น th_TH.UTF-8 ก่อน
    locale.setlocale(locale.LC_TIME, 'th_TH.UTF-8')
except locale.Error:
    try:
        # 2. ลองใช้ 'thai' เป็น fallback
        locale.setlocale(locale.LC_TIME, 'thai')
    except locale.Error:
        print("Warning: Could not set locale to Thai.")

# --- ตั้งค่า appearance และ theme ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --- สร้างหน้าต่างหลัก ---
root = ctk.CTk()
root.title("HTC Smart Hub")
# ปรับขนาดหน้าจอให้ใหญ่ขึ้นสำหรับตู้ Kiosk (1080x1920)
# ถ้าเป็นการรันบนคอมพิวเตอร์ทั่วไป อาจจะต้องลดขนาด
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
datetime_label = None # สำหรับแสดงเวลา/วันที่

# ** Navigation Variables **
electronics_window = None 

# ***************************************************************
# ** Global Keyword Lists สำหรับ Speech Recognition **
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
KEYWORDS_BASICTECH = ["ช่างเทคนิคพื้นฐาน", "เทคนิคพื้นฐาน", "พื้นฐานช่าง"]
KEYWORDS_ELECTRIC = ["ช่างไฟฟ้า", "ไฟฟ้า", "ไฟฟ้ากำลัง"]
KEYWORDS_AIRCOND = ["เครื่องทำความเย็น", "ปรับอากาศ", "แอร์", "ระบบความเย็น"]
KEYWORDS_IT = ["เทคโนโลยีสารสนเทศ", "ไอที", "สารสนเทศ", "it", "คอมพิวเตอร์"]
KEYWORDS_PETROLEUM = ["เทคโนโลยีปิโตรเลียม", "ปิโตรเลียม"]
KEYWORDS_ENERGY = ["เทคนิคพลังงาน", "พลังงาน"]
KEYWORDS_LOGISTICS = ["โลจิสติกส์", "ซัพพลายเชน", "logistics"]
KEYWORDS_RAIL = ["ระบบขนส่งทางราง", "ขนส่งทางราง", "ราง", "ระบบราง", "รถไฟ"]
KEYWORDS_MECHATRONICS = ["เมคคาทรอนิกส์", "หุ่นยนต์", "เมคคา", "หุ่นยนต์", "แม็กคา", "แม็คคา", "แมคคา","แมกคา","แม็กคา", "mechatronics"]
KEYWORDS_AIRLINE = ["แผนกการบิน", "การบิน", "aviation"]
KEYWORDS_COMPUTER_TECH = ["เทคโนโลยีคอมพิวเตอร์", "เทคโนโลยีคอม", "คอมพิวเตอร์", "คอมพิว", "ตึกส้ม"]
KEYWORDS_BASIC_SUBJECTS = ["วิชาพื้นฐาน", "พื้นฐาน", "วิชาสามัญ"]
KEYWORDS_SOUTHERN_CENTER = ["ศูนย์ส่งเสริม", "อาชีวศึกษาภาคใต้", "ส่งเสริม"]
KEYWORDS_60YEARS = ["ตึก 60 ปี", "60 ปี"]
KEYWORDS_TUK11 = ["ตึก 11"]

# ***************************************************************
# ** Global Keyword Lists สำหรับ Rooms **
# ***************************************************************
# อ้างอิงจากไฟล์รูปภาพที่ส่งมา และ Path/Videos ที่กำหนดไว้
KEYWORDS_COUNSELING = ["ห้องแนะแนว", "งานแนะแนว"] 
KEYWORDS_CURRICULUM = ["ห้องพัฒนาหลักสูตร", "งานพัฒนาหลักสูตร", "หลักสูตร"]
KEYWORDS_DISCIPLINARY = ["ห้องวินัย", "งานวินัย"]
KEYWORDS_EVALUATION = ["ห้องประเมิน", "งานประเมิน"]
KEYWORDS_EVENT = ["ห้องกิจกรรม", "งานกิจกรรม"]
KEYWORDS_FINANCE = ["ห้องการเงิน", "งานการเงิน"]
KEYWORDS_PRODUCTION = ["ห้องผลิตและพัฒนากำลังคน", "งานผลิตและพัฒนากำลังคน", "กำลังคน"]
KEYWORDS_PUBLIC_RELATIONS = ["ห้องประชาสัมพันธ์", "งานประชาสัมพันธ์", "ประชาสัมพันธ์"]
KEYWORDS_REGISTRATION = ["ห้องทะเบียน", "งานทะเบียน"]
KEYWORDS_PROCUREMENT = ["ห้องพัสดุ", "งานพัสดุ"]
KEYWORDS_ACADEMIC = ["ห้องวิชาการ", "งานวิชาการ"]
KEYWORDS_GOVERNANCE = ["ห้องงานปกครอง", "งานปกครอง"]
KEYWORDS_ASSESSMENT = ["ห้องงานวัดผล", "งานวัดผล", "วัดผล"]
KEYWORDS_GRADUATE = ["งานประสานงานผู้จบ", "งานผู้จบ", "ห้องผู้จบ", "ประสานงานผู้จบ"]
KEYWORDS_DUAL_VOCATIONAL = ["งานทวิภาคี", "ห้องทวิภาคี", "ทวิภาคี"]


# ***************************************************************
# ** NEW: ระยะทางและระยะเวลาเดินทาง (โดยประมาณ) **
# ***************************************************************

# โครงสร้าง: (ระยะทาง (เมตร), เวลา (นาที))
DEFAULT_TRAVEL = (150, 2.5) # ค่าเริ่มต้นสำหรับแผนก/ห้องที่ไม่มีข้อมูล
TRAVEL_INFO = {
    # แผนกวิชา
    "ELECTRONICS": (200, 3),
    "CONSTRUCTION": (350, 5),
    "CIVIL": (300, 4),
    "FURNITURE": (400, 6),
    "SURVEY": (450, 6), # ใช้ร่วมกับ ARCHITECT
    "ARCHITECT": (450, 6),
    "AUTO": (250, 3),
    "FACTORY": (500, 7),
    "WELDING": (300, 4),
    "BASICTECH": (250, 3),
    "ELECTRIC": (180, 2),
    "AIRCOND": (380, 5),
    "IT": (500, 7), # ใช้ร่วมกับ FACTORY
    "PETROLEUM": (550, 8),
    "ENERGY": (600, 8), # ใช้ร่วมกับ MECHATRONICS
    "LOGISTICS": (650, 9), # ใช้ร่วมกับ AIRLINE
    "RAIL": (700, 10),
    "MECHATRONICS": (600, 8),
    "AIRLINE": (650, 9),
    "COMPUTER_TECH": (100, 1),
    "BASIC_SUBJECTS": (150, 2),
    "SOUTHERN_CENTER": (180, 2),
    "60YEARS": (50, 1),
    "TUK11": (650, 9), # ใช้ร่วมกับ AIRLINE/LOGISTICS
    
    # ห้อง/งาน
    "GRADUATE": (120, 1),
    "DUAL_VOCATIONAL": (150, 2),
    "COUNSELING": (100, 1),
    "CURRICULUM": (100, 1),
    "DISCIPLINARY": (150, 2),
    "EVALUATION": (100, 1),
    "EVENT": (120, 1),
    "FINANCE": (80, 1),
    "PRODUCTION": (180, 2),
    "PUBLIC_RELATIONS": (100, 1),
    "REGISTRATION": (80, 1),
    "PROCUREMENT": (120, 1),
    "ACADEMIC": (100, 1),
    "GOVERNANCE": (150, 2),
    "ASSESSMENT": (150, 2),
}


# ***************************************************************
# ** PATHS AND WAYPOINTS **
# ***************************************************************
IMAGE_SLIDE_FOLDER = "Picture_slide" 
ROOM_IMAGE_FOLDER = "room"
ROOM_VIDEO_FOLDER = "room"
IMAGE_SLIDE_HEIGHT = 300 
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
DEPT_IMAGE_WIDTH = 950 
DEPT_IMAGE_HEIGHT = 400 

# --- PATHS (Dept) ---
AIRCONDI_DEPT_IMAGE_PATH      = "Picture_slide/ทำความเย็น.jpg"
AIRLINE_DEPT_IMAGE_PATH       = "Picture_slide/ตึก11.jpg"
ARCHITECT_DEPT_IMAGE_PATH     = "Picture_slide/สถาปัตยกรรม_สำรวจ.jpg"
AUTO_DEPT_IMAGE_PATH          = "Picture_slide/ช่างยนต์.jpg"
BASIC_TECH_DEPT_IMAGE_PATH    = "Picture_slide/เทคนิคพื้นฐาน.jpg"
CIVIL_DEPT_IMAGE_PATH         = "Picture_slide/โยธา.jpg"
COMPUTER_TECH_DEPT_IMAGE_PATH = "Picture_slide/ตึกส้ม.jpg"
CONSTRUCTION_DEPT_IMAGE_PATH  = "Picture_slide/ก่อสร้าง.jpg"
ELECTRIC_DEPT_IMAGE_PATH      = "Picture_slide/ช่างไฟฟ้า.jpg"
ELECTRONICS_DEPT_IMAGE_PATH   = "Picture_slide/อิเล็กทรอนิกส์.jpg"
ENERGY_DEPT_IMAGE_PATH        = "Picture_slide/แมคคา_พลังงาน.jpg"
FACTORY_DEPT_IMAGE_PATH       = "Picture_slide/สารสนเทศ_กลโรงงาน.jpg"
FURNITURE_DEPT_IMAGE_PATH     = "Picture_slide/ตกแต่งภายใน.jpg"
IT_DEPT_IMAGE_PATH            = "Picture_slide/สารสนเทศ_กลโรงงาน.jpg"
LOGISTICS_DEPT_IMAGE_PATH     = "Picture_slide/ตึก11.jpg"
MECHATRONICS_DEPT_IMAGE_PATH  = "Picture_slide/แมคคา_พลังงาน.jpg"
PETROLEUM_DEPT_IMAGE_PATH     = "Picture_slide/ปิโตรเลียม.jpg"
RAIL_DEPT_IMAGE_PATH          = "Picture_slide/ระบบราง.jpg"
SURVEY_DEPT_IMAGE_PATH        = "Picture_slide/สถาปัตยกรรม_สำรวจ.jpg"
WELDING_DEPT_IMAGE_PATH       = "Picture_slide/ช่างเชื่อมโลหะ.jpg"
SIXTY_YEARS_DEPT_IMAGE_PATH   = os.path.join(IMAGE_SLIDE_FOLDER, "60 ปี.jpg")

# --- WAYPOINT VIDEOS (Dept) ---
WAYPOINT_AIRCONDI_VIDEO        = "Tower/Waypoint_Video/To_AIRCONDI.mp4"
WAYPOINT_AIRLINE_VIDEO         = "Tower/Waypoint_Video/To_AIRLINE.mp4"
WAYPOINT_ARCHITECT_VIDEO       = "Tower/Waypoint_Video/To_ARCHITECT.mp4"
WAYPOINT_AUTO_VIDEO            = "Tower/Waypoint_Video/To_AUTO.mp4"
WAYPOINT_BASIC_TECH_VIDEO      = "Tower/Waypoint_Video/To_BASIC_TECH.mp4"
WAYPOINT_CIVIL_VIDEO           = "Tower/Waypoint_Video/To_CIVIL.mp4"
WAYPOINT_COMPUTER_TECH_VIDEO   = "Tower/Waypoint_Video/To_COMPUTER_TECH.mp4"
WAYPOINT_CONSTRUCTION_VIDEO    = "Tower/Waypoint_Video/To_CONSTRUCTION.mp4"
WAYPOINT_ELECTRIC_VIDEO        = "Tower/Waypoint_Video/To_ELECTRIC.mp4"
WAYPOINT_ELECTRONICS_VIDEO     = "Tower/Waypoint_Video/To_ELECTRONICS.mp4"
WAYPOINT_ENERGY_VIDEO          = "Tower/Waypoint_Video/To_ENERGY.mp4"
WAYPOINT_FACTORY_VIDEO         = "Tower/Waypoint_Video/To_FACTORY.mp4"
WAYPOINT_FURNITURE_VIDEO       = "Tower/Waypoint_Video/To_FURNITURE.mp4"
WAYPOINT_IT_VIDEO              = "Tower/Waypoint_Video/To_IT.mp4"
WAYPOINT_LOGISTICS_VIDEO       = "Tower/Waypoint_Video/To_LOGISTICS.mp4"
WAYPOINT_MECHATRONICS_VIDEO    = "Tower/Waypoint_Video/To_MECHATRONICS.mp4"
WAYPOINT_PETROLEUM_VIDEO       = "Tower/Waypoint_Video/To_PETROLEUM.mp4"
WAYPOINT_RAIL_VIDEO            = "Tower/Waypoint_Video/To_RAIL.mp4"
WAYPOINT_SURVEY_VIDEO          = "Tower/Waypoint_Video/To_SURVEY.mp4"
WAYPOINT_WELDING_VIDEO         = "Tower/Waypoint_Video/To_WELDING.mp4"
WAYPOINT_BASIC_SUBJECTS_VIDEO = "" # No video path provided
WAYPOINT_SOUTHERN_CENTER_VIDEO = "" # No video path provided
WAYPOINT_60YEARS_VIDEO = "" # No video path provided (using blank for now)

# --- ROOM PATHS & VIDEOS ---
def get_room_path(folder, filename):
    # FIX: แก้ Path ให้ใช้ os.path.join เพื่อป้องกันปัญหาเครื่องหมาย \ หรือ /
    return os.path.join(folder, filename)

# ** FIX: ตรวจสอบและแก้ไข Path ของไฟล์วิดีโอ/รูปภาพสำหรับห้องอำนวยการ
#         เนื่องจากก่อนหน้านี้มีการใช้ os.path.join ไม่ถูกต้องในบางส่วน
#         และ Path ที่ใช้ในโค้ดเก่าอาจไม่ตรงกับ Path จริงบนระบบของคุณ 
#         (ใช้ Path เดิมที่กำหนดไว้ในโค้ดต้นฉบับ แต่ยืนยันว่าใช้ os.path.join)

WAYPOINT_GRADUATE_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_GraduateCoordinationCenter.mp4")
GRADUATE_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานประสานงานผู้จบ.jpg")

WAYPOINT_COUNSELING_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_counseling_room.mp4")
COUNSELING_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานแนะแนว.jpg")

WAYPOINT_CURRICULUM_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Curriculumdevelopmentroom.mp4")
CURRICULUM_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานพัฒนาหลักสูตร.jpg")

WAYPOINT_DISCIPLINARY_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_disciplinary_office.mp4")
DISCIPLINARY_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานวินัย_ตึก2.jpg")

WAYPOINT_DUAL_VOCATIONAL_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Dual VocationalEducation_Room.mp4")
DUAL_VOCATIONAL_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานทวิภาคี.jpg")

WAYPOINT_EVALUATION_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_evaluation_room.mp4")
EVALUATION_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานประเมิน.jpg")

WAYPOINT_EVENT_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_eventroom.mp4")
EVENT_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานกิจกรรม.jpg")

WAYPOINT_FINANCE_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Finance room.mp4")
FINANCE_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานการเงิน.jpg")

WAYPOINT_PUBLIC_RELATIONS_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_public_relations_room.mp4")
PUBLIC_RELATIONS_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานประชาสัมพันธ์.jpg")

# FIX: แก้ไขชื่อไฟล์วิดีโอสำหรับห้องทะเบียนให้ถูกต้องตามรูปแบบ Path ที่เคยใช้ในโค้ดเก่า
# ชื่อไฟล์เดิม: To_registeroion.mp4 (อาจสะกดผิด)
# เปลี่ยนเป็น: To_registeroion.mp4 (คงชื่อเดิมไว้ตามที่เคยระบุในโค้ด)
WAYPOINT_REGISTRATION_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_registeroion.mp4")
REGISTRATION_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานทะเบียน.jpg")

WAYPOINT_PROCUREMENT_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "งานพัสดุ.mp4")
PROCUREMENT_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานพัสดุ.jpg")

WAYPOINT_ACADEMIC_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "งานวิชาการ.mp4")
ACADEMIC_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานวิชาการ.jpg")

WAYPOINT_GOVERNANCE_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "งานปกครอง.mp4")
GOVERNANCE_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานปกครอง.jpg")

WAYPOINT_ASSESSMENT_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "งานวัดผลตึก2-1.mp4") 
ASSESSMENT_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานวัดผลตึก2-1.jpg")

WAYPOINT_PRODUCTION_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Production and Manpower Development Coordination...mp4")
PRODUCTION_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานผลิตและพัฒนากำลังคน.jpg")


# ** Global UI Components **
image_slide_frame = None
survey_frame = None
credit_frame = None
bottom_bar = None
fanpage_ctk_image_global = None 
top_bar = None # ประกาศเป็น Global

# --- ฟังก์ชันช่วยเหลือในการพิมพ์สถานะ ---
def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] [Debug] : {message}")


# ***************************************************************
# ** Timer Inactivity Control Functions **
# ***************************************************************
TIMEOUT_MS = 3 * 60 * 1000  # 3 นาที = 180,000 มิลลิวินาที
inactivity_timer_id = None 
event_key_press_id = None
event_button_1_id = None

def show_main_screen_ui():
    """ฟังก์ชันสำหรับแสดงหน้าจอหลัก (Home Screen)"""
    show_frame(home_content_frame) 
    # **NOTE: ลบการเรียก update_datetime_clock() ที่นี่ออก เพราะมันรันต่อเนื่องอยู่แล้ว**
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
    
    # **NOTE: ลบส่วนนี้ออกเพื่อให้เวลารันต่อเนื่อง**
    # if hasattr(root, '_datetime_after_id') and root._datetime_after_id is not None:
    #     root.after_cancel(root._datetime_after_id)
    #     root._datetime_after_id = None
    
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


def bind_inactivity_reset():
    """ผูก Event การโต้ตอบกับหน้าจอเพื่อรีเซ็ต Timer และเริ่ม Timer ครั้งแรก"""
    global event_key_press_id, event_button_1_id
    
    # ตรวจสอบและยกเลิกการผูก/Timer เก่าก่อนเสมอ เพื่อความสะอาด
    unbind_inactivity_reset() 
    
    # ผูกกับ Event การกดปุ่มใดๆ และการคลิกซ้าย
    event_key_press_id = root.bind('<KeyPress>', reset_inactivity_timer)
    event_button_1_id = root.bind('<Button-1>', reset_inactivity_timer)
    
    # เริ่ม Timer ครั้งแรกทันทีที่เข้าหน้าแผนก
    reset_inactivity_timer()
    print_status("Timer Inactivity 3 นาที เริ่มทำงานแล้ว.")

# ***************************************************************
# ** NEW: Real-Time Date/Time Clock **
# ***************************************************************

def update_datetime_clock():
    """อัปเดตเวลาและวันที่ปัจจุบันแบบ Real-Time บนแถบด้านบน"""
    global datetime_label
    
    # หยุดการ Update เก่า (ถ้ามี)
    if hasattr(root, '_datetime_after_id') and root._datetime_after_id is not None:
        root.after_cancel(root._datetime_after_id)
        
    # **NOTE: ลบเงื่อนไข winfo_ismapped() ออก เพื่อให้รันบน top_bar เสมอ**
    if datetime_label is not None:
        # รูปแบบ: วันที่ 1 มกราคม 2568 เวลา 10:30 น.
        current_dt = datetime.now()
        
        # ปรับปีเป็นพุทธศักราช (ปี ค.ศ. + 543)
        buddhist_year = current_dt.year + 543
        
        # FIX: แก้ปัญหา locale bug โดยการสร้างชื่อเดือน/วันด้วยตัวเอง
        #      เมื่อ locale มีปัญหา (มักเกิดขึ้นใน Windows)
        try:
             # ลองใช้ locale ดึงชื่อวัน/เดือนก่อน
            date_part = current_dt.strftime("วัน %A ที่ %d เดือน %B พ.ศ. %Y").replace(str(current_dt.year), str(buddhist_year)).replace(" 0", " ")
            
        except UnicodeEncodeError:
            # ถ้า locale ล้มเหลว (เกิดบั๊กแสดงตัวอักษรซ้ำๆ) ให้กำหนดชื่อเอง
            thai_months = [
                "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
            ]
            thai_days = [
                "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"
            ]
            day_name = thai_days[current_dt.weekday()]
            month_name = thai_months[current_dt.month - 1]
            
            date_part = f"วัน{day_name} ที่ {current_dt.day} {month_name} พ.ศ. {buddhist_year}"


        time_str = current_dt.strftime("%H:%M:%S")
        
        display_text = f"{date_part}\nเวลา {time_str} น."
        
        datetime_label.configure(text=display_text)
        
        # ตั้งเวลาให้เรียกตัวเองใหม่ใน 1 วินาที (1000ms)
        root._datetime_after_id = root.after(1000, update_datetime_clock)
        
    else:
        # ถ้า datetime_label ยังไม่ถูกสร้าง ให้หยุด Update
        root._datetime_after_id = None


# ***************************************************************
# ** เฟรมสำหรับสลับหน้า (Frame Switching) **
# ***************************************************************
home_content_frame = ctk.CTkFrame(root, fg_color="white")
electronics_content_frame = ctk.CTkFrame(root, fg_color="white")
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
    
    should_show_slides = False
    should_show_survey = False
    should_show_credit = False
    
    if frame_to_show == home_content_frame:
        should_show_slides = True
        should_show_survey = True
        should_show_credit = True
        
    elif frame_to_show == electronics_content_frame:
        should_show_survey = True
        should_show_credit = True
        
    elif frame_to_show == navigation_content_frame:
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


# -----------------------------------------------------------------
# --- NEW/MODIFIED: ฟังก์ชันควบคุมหน้าต่างนำทางแบบมีเส้นทาง (Guided Page) ---
# -----------------------------------------------------------------

def show_guided_page(title, header_bg_color, dept_image_path, waypoint_video, travel_key):
    """
    แสดงเนื้อหาแผนก/กิจกรรมแบบมีเส้นทางนำทาง
    :param title: หัวข้อที่จะแสดงบน Header
    :param header_bg_color: สีพื้นหลังของ Header
    :param dept_image_path: Path รูปภาพที่จะแสดงใต้ Header
    :param waypoint_video: Path ของวิดีโอ Waypoint
    :param travel_key: Key สำหรับดึงข้อมูลระยะทางและเวลาจาก TRAVEL_INFO
    """
    global DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT
    
    # ล้างเนื้อหาเก่า
    for widget in electronics_content_frame.winfo_children():
        widget.destroy()

    # ดึงข้อมูลระยะทาง/เวลา
    distance_m, time_min = TRAVEL_INFO.get(travel_key, DEFAULT_TRAVEL)

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
                 
    # 1.5 แสดงระยะทาง/เวลา (ใต้ Header)
    ctk.CTkLabel(electronics_content_frame,
                 text=f"ระยะทางโดยประมาณ: {distance_m} เมตร | เวลาเดินเท้า: ประมาณ {time_min:.1f} นาที",
                 font=("Kanit", 22, "bold"),
                 text_color="#006400").pack(pady=(10, 5))
                 
    # 2. รูปภาพแผนก (จาก Path ที่กำหนด)
    try:
         if dept_image_path and os.path.exists(dept_image_path):
             dept_img = Image.open(dept_image_path)
             # FIX: เพิ่มการจัดการขนาดรูปภาพ
             dept_img_resized = dept_img.resize((DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT), Image.LANCZOS)
             dept_ctk_image = ctk.CTkImage(light_image=dept_img_resized, dark_image=dept_img_resized, size=(DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT))
             
             ctk.CTkLabel(electronics_content_frame, 
                          image=dept_ctk_image, 
                          text="").pack(pady=(10, 5))
         else:
             ctk.CTkLabel(electronics_content_frame, 
                      text=f"[ไม่พบรูปภาพ: {os.path.basename(dept_image_path) if dept_image_path else 'N/A'}]", 
                      font=("Kanit", 24),
                      text_color="red").pack(pady=(20, 10))
    except Exception as e:
         print_status(f"ไม่พบรูปภาพแผนก: {e}")
         ctk.CTkLabel(electronics_content_frame, 
                      text=f"[พื้นที่สำหรับรูปภาพ: Error - {e}]", 
                      font=("Kanit", 24),
                      text_color="red").pack(pady=(20, 10))


    # 3. กรอบสำหรับข้อความนำทาง
    guide_frame = ctk.CTkFrame(electronics_content_frame, fg_color="transparent")
    guide_frame.pack(pady=(10, 5))
        
    # ข้อความนำทาง (สีม่วงเข้ม)
    ctk.CTkLabel(guide_frame, 
                 text="โปรดเดินตามเส้นทางที่กำหนดในวิดีโอนี้", 
                 font=("Kanit", 22, "bold"), 
                 text_color="#8000FF").pack(side="left")


    # 4. แผนผังการเดิน (Map Image) พร้อมเส้นประ
    map_container_frame = ctk.CTkFrame(
        electronics_content_frame, 
        fg_color="white", 
        width=900,
        height=500
    )
    map_container_frame.pack(pady=10)

    # --- VIDEO FRAME (ใช้ tk.Label) ---
    video_label = tk.Label(map_container_frame, bg="white", borderwidth=0)
    
    VIDEO_PATH = waypoint_video

    # ** FIX: ตรวจสอบ VIDEO_PATH ก่อนเล่น/แสดงข้อความ **
    if VIDEO_PATH and os.path.exists(VIDEO_PATH) and VIDEO_PATH.endswith('.mp4'):
        try:
            video_label.pack(expand=True)
            # ตรวจสอบและควบคุมขนาดให้เหมาะสมกับ Label 900x500
            # Note: The player must be stored as an attribute of the label/frame to prevent garbage collection
            map_container_frame.player = tkvideo(VIDEO_PATH, video_label, loop=1, size=(900, 500))
            map_container_frame.player.play()
            print_status(f"Video loaded: {VIDEO_PATH}")
        except Exception as e:
             # แสดงข้อความ Error หากโหลดวิดีโอไม่ได้
             video_label.pack_forget()
             ctk.CTkLabel(map_container_frame, 
                          text=f"Waypoint Video Error! {VIDEO_PATH}\n[{e}]",
                          font=("Kanit",18),
                          text_color="red").pack(pady=20)
             print_status(f"Video load error! : [ {VIDEO_PATH} ] - {e}")
    else:
        # แสดงข้อความ Not Found
        ctk.CTkLabel(map_container_frame, 
                     text=f"Waypoint Video Not Found! PATH : [ {VIDEO_PATH} ]",
                     font=("Kanit",18),
                     text_color="red").pack(pady=20)
        print_status(f"Video not found! : [ {VIDEO_PATH} ]")

    # =============================================================================
    
    # ข้อความใต้แผนผัง
    ctk.CTkLabel(electronics_content_frame, 
             text=f"เส้นทางนำทาง: จากจุดเริ่มต้น (Kiosk) ไปยัง {title}", 
             font=("Kanit", 18),
             text_color="#00AA00").pack(pady=(5, 10))
    
    # 5. ปุ่มกลับสู่หน้าหลัก
    ctk.CTkButton(electronics_content_frame, 
                  text="❮ กลับสู่หน้าหลัก", 
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

# =============================================================================
# === HOME SCREEN CONTENT (Banner Image + Video) ===
# =============================================================================

# --- 1. BANNER IMAGE (FF.jpg) ---
banner_label = ctk.CTkLabel(home_content_frame, text="")
banner_label.pack(side="top", pady=(20, 10)) 

try:
    BANNER_PATH = "Facebook/FF.png"
    if os.path.exists(BANNER_PATH):
        banner_img = Image.open(BANNER_PATH)
        target_width = 1000
        w_percent = (target_width / float(banner_img.size[0]))
        h_size = int((float(banner_img.size[1]) * float(w_percent)))
        
        banner_img_resized = banner_img.resize((target_width, h_size), Image.LANCZOS)
        banner_ctk_img = ctk.CTkImage(light_image=banner_img_resized, 
                                      dark_image=banner_img_resized, 
                                      size=(target_width, h_size))
        
        banner_label.configure(image=banner_ctk_img)
    else:
        banner_label.configure(text=f"Image not found: {BANNER_PATH}", text_color="red")
except Exception as e:
    print_status(f"Error loading banner image: {e}")

# --- 2. VIDEO FRAME (Below the image) ---
video_container = tk.Frame(home_content_frame, bg="white")
video_container.pack(side="top", expand=True, fill="both", padx=20, pady=(0, 20))

video_label = tk.Label(video_container, bg="white", borderwidth=0)
video_label.pack(expand=True)

try:
    VIDEO_PATH = "Tower/Start_Point/E1.mp4" 

    if os.path.exists(VIDEO_PATH) and VIDEO_PATH.endswith('.mp4'):
        # Store player to prevent garbage collection
        video_container.player = tkvideo(VIDEO_PATH, video_label, loop=1, size=(900, 500))
        video_container.player.play()
        print_status(f"Video loaded: {VIDEO_PATH}")
    else:
        video_label.pack_forget()
        ctk.CTkLabel(video_container, 
                     text=f"Video not found or invalid format: {VIDEO_PATH}", 
                     text_color="red", 
                     font=("Kanit", 24)).pack(expand=True)
except Exception as e:
    print_status(f"Error loading video: {e}")

# =============================================================================

# ***************************************************************
# ** UPDATED: ฟังก์ชัน Wrapper สำหรับแผนกต่างๆ **
# ***************************************************************

def show_electronics_page():
    BLUE_BACKGROUND = "#87CEFA" 
    show_guided_page(title="แผนกวิชาอิเล็กทรอนิกส์", header_bg_color=BLUE_BACKGROUND, 
                     dept_image_path=ELECTRONICS_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_ELECTRONICS_VIDEO, 
                     travel_key="ELECTRONICS")

def show_60_years_page():
    GOLD_BACKGROUND = "#FFD700" 
    show_guided_page(title="60 ปี วิทยาลัยเทคนิคหาดใหญ่", header_bg_color=GOLD_BACKGROUND, 
                     dept_image_path=SIXTY_YEARS_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_60YEARS_VIDEO, 
                     travel_key="60YEARS")

def show_construction_page():
    ORANGE_BACKGROUND = "#FF8C00" 
    show_guided_page(title="แผนกวิชาก่อสร้าง", header_bg_color=ORANGE_BACKGROUND, 
                     dept_image_path=CONSTRUCTION_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_CONSTRUCTION_VIDEO,
                     travel_key="CONSTRUCTION")

def show_electrical_page():
    YELLOW_BACKGROUND = "#FFD100" 
    show_guided_page(title="แผนกวิชาไฟฟ้ากำลัง", header_bg_color=YELLOW_BACKGROUND, 
                     dept_image_path=ELECTRIC_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_ELECTRIC_VIDEO,
                     travel_key="ELECTRIC")

def show_interior_decoration_page():
    BROWN_BACKGROUND = "#A52A2A" 
    show_guided_page(title="แผนกวิชาตกแต่งภายใน", header_bg_color=BROWN_BACKGROUND, 
                     dept_image_path=FURNITURE_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_FURNITURE_VIDEO,
                     travel_key="FURNITURE")

def show_tuk11_page():
    PURPLE_BACKGROUND = "#8A2BE2" 
    show_guided_page(title="ตึก 11 (การบินและโลจิสติกส์)", header_bg_color=PURPLE_BACKGROUND, 
                     dept_image_path=AIRLINE_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_AIRLINE_VIDEO,
                     travel_key="TUK11")

def show_petroleum_page():
    GREEN_BACKGROUND = "#006400" 
    show_guided_page(title="แผนกวิชาปิโตรเลียม", header_bg_color=GREEN_BACKGROUND, 
                     dept_image_path=PETROLEUM_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_PETROLEUM_VIDEO,
                     travel_key="PETROLEUM")
    
def show_technic_mac_page():
    TEAL_BACKGROUND = "#008080" 
    show_guided_page(title="แผนกวิชาช่างยนต์", header_bg_color=TEAL_BACKGROUND,
                     dept_image_path=AUTO_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_AUTO_VIDEO,
                     travel_key="AUTO")

def show_factory_it_page():
    DARK_BLUE_BACKGROUND = "#483D8B" 
    show_guided_page(title="แผนกเครื่องกลโรงงานและสารสนเทศ", header_bg_color=DARK_BLUE_BACKGROUND,
                     dept_image_path=FACTORY_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_FACTORY_VIDEO,
                     travel_key="FACTORY")

def show_mechatronics_energy_page():
    RED_ORANGE_BACKGROUND = "#FF4500"
    show_guided_page(title="แผนกเมคคาทรอนิคและพลังงาน", header_bg_color=RED_ORANGE_BACKGROUND,
                     dept_image_path=MECHATRONICS_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_MECHATRONICS_VIDEO,
                     travel_key="MECHATRONICS")
    
def show_airline_logistics_page():
    PURPLE_BACKGROUND = "#8A2BE2" 
    show_guided_page(title="แผนกการบินและโลจิสติกส์", header_bg_color=PURPLE_BACKGROUND, 
                     dept_image_path=AIRLINE_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_AIRLINE_VIDEO,
                     travel_key="AIRLINE")

def show_rail_page():
    ORANGE_BACKGROUND = "#FF9900" 
    show_guided_page(title="แผนกวิชาระบบราง", header_bg_color=ORANGE_BACKGROUND, 
                     dept_image_path=RAIL_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_RAIL_VIDEO,
                     travel_key="RAIL")

def show_basic_tech_page():
    DARK_YELLOW_BACKGROUND = "#B8860B" 
    show_guided_page(title="แผนกวิชาเทคนิคพื้นฐาน", header_bg_color=DARK_YELLOW_BACKGROUND, 
                     dept_image_path=BASIC_TECH_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_BASIC_TECH_VIDEO,
                     travel_key="BASICTECH")

def show_arch_survey_page():
    BROWN_BACKGROUND = "#8B4513" 
    show_guided_page(title="แผนกสถาปัตยกรรมและช่างสำรวจ", header_bg_color=BROWN_BACKGROUND, 
                     dept_image_path=ARCHITECT_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_ARCHITECT_VIDEO,
                     travel_key="ARCHITECT")

def show_air_condi_page():
    SILVER_BACKGROUND = "#C0C0C0"
    show_guided_page(title="แผนกทำความเย็นและปรับอากาศ", header_bg_color=SILVER_BACKGROUND,
                     dept_image_path=AIRCONDI_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_AIRCONDI_VIDEO,
                     travel_key="AIRCOND")

def show_welding_page():
    BLACK_BACKGROUND = "#222222" 
    show_guided_page(title="แผนกวิชาช่างเชื่อมโลหะ", header_bg_color=BLACK_BACKGROUND, 
                     dept_image_path=WELDING_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_WELDING_VIDEO,
                     travel_key="WELDING")

def show_civil_page():
    GRAY_BACKGROUND = "#708090"
    show_guided_page(title="แผนกวิชาช่างโยธา", header_bg_color=GRAY_BACKGROUND,
                     dept_image_path=CIVIL_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_CIVIL_VIDEO,
                     travel_key="CIVIL")
    
def show_computer_tech_page():
    ORANGE_BACKGROUND = "#FF8C00"
    show_guided_page(title="แผนกคอมพิวเตอร์เทคนิค", header_bg_color=ORANGE_BACKGROUND,
                     dept_image_path=COMPUTER_TECH_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_COMPUTER_TECH_VIDEO,
                     travel_key="COMPUTER_TECH")

def show_basic_subjects_page():
    TEAL_BACKGROUND = "#008080" 
    show_guided_page(title="แผนกวิชาพื้นฐาน (วิชาสามัญ)", header_bg_color=TEAL_BACKGROUND, 
                     dept_image_path="", waypoint_video=WAYPOINT_BASIC_SUBJECTS_VIDEO,
                     travel_key="BASIC_SUBJECTS")

def show_southern_center_page():
    INDIGO_BACKGROUND = "#4B0082" 
    show_guided_page(title="ศูนย์ส่งเสริมและพัฒนาอาชีวศึกษาภาคใต้", header_bg_color=INDIGO_BACKGROUND, 
                     dept_image_path="", waypoint_video=WAYPOINT_SOUTHERN_CENTER_VIDEO,
                     travel_key="SOUTHERN_CENTER")

# ***************************************************************
# ** NEW: ฟังก์ชัน Wrapper สำหรับ Rooms **
# ***************************************************************
ROOM_BACKGROUND_COLOR = "#A9A9A9" 

def show_graduate_page():
    show_guided_page(title="งานประสานงานและส่งเสริมผู้จบ", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=GRADUATE_IMAGE_PATH, waypoint_video=WAYPOINT_GRADUATE_VIDEO,
                     travel_key="GRADUATE")

def show_dual_vocational_page():
    show_guided_page(title="งานทวิภาคี (Dual Vocational Education)", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=DUAL_VOCATIONAL_IMAGE_PATH, waypoint_video=WAYPOINT_DUAL_VOCATIONAL_VIDEO,
                     travel_key="DUAL_VOCATIONAL")

def show_counseling_page():
    show_guided_page(title="ห้องแนะแนว", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=COUNSELING_IMAGE_PATH, waypoint_video=WAYPOINT_COUNSELING_VIDEO,
                     travel_key="COUNSELING")

def show_curriculum_page():
    show_guided_page(title="ห้องพัฒนาหลักสูตร", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=CURRICULUM_IMAGE_PATH, waypoint_video=WAYPOINT_CURRICULUM_VIDEO,
                     travel_key="CURRICULUM")

def show_disciplinary_page():
    show_guided_page(title="ห้องวินัย", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=DISCIPLINARY_IMAGE_PATH, waypoint_video=WAYPOINT_DISCIPLINARY_VIDEO,
                     travel_key="DISCIPLINARY")

def show_evaluation_page():
    show_guided_page(title="ห้องประเมิน", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=EVALUATION_IMAGE_PATH, waypoint_video=WAYPOINT_EVALUATION_VIDEO,
                     travel_key="EVALUATION")

def show_event_page():
    show_guided_page(title="ห้องกิจกรรม", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=EVENT_IMAGE_PATH, waypoint_video=WAYPOINT_EVENT_VIDEO,
                     travel_key="EVENT")

def show_finance_page():
    show_guided_page(title="ห้องการเงิน", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=FINANCE_IMAGE_PATH, waypoint_video=WAYPOINT_FINANCE_VIDEO,
                     travel_key="FINANCE")

def show_production_page():
    show_guided_page(title="ห้องผลิตและพัฒนากำลังคน", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=PRODUCTION_IMAGE_PATH, waypoint_video=WAYPOINT_PRODUCTION_VIDEO,
                     travel_key="PRODUCTION")

def show_public_relations_page():
    show_guided_page(title="ห้องประชาสัมพันธ์", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=PUBLIC_RELATIONS_IMAGE_PATH, waypoint_video=WAYPOINT_PUBLIC_RELATIONS_VIDEO,
                     travel_key="PUBLIC_RELATIONS")

def show_registration_page():
    show_guided_page(title="ห้องทะเบียน", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=REGISTRATION_IMAGE_PATH, waypoint_video=WAYPOINT_REGISTRATION_VIDEO,
                     travel_key="REGISTRATION")

def show_procurement_page():
    show_guided_page(title="ห้องพัสดุ", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=PROCUREMENT_IMAGE_PATH, waypoint_video=WAYPOINT_PROCUREMENT_VIDEO,
                     travel_key="PROCUREMENT")

def show_academic_page():
    show_guided_page(title="ห้องวิชาการ", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=ACADEMIC_IMAGE_PATH, waypoint_video=WAYPOINT_ACADEMIC_VIDEO,
                     travel_key="ACADEMIC")

def show_governance_page():
    show_guided_page(title="ห้องงานปกครอง", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=GOVERNANCE_IMAGE_PATH, waypoint_video=WAYPOINT_GOVERNANCE_VIDEO,
                     travel_key="GOVERNANCE")

def show_assessment_page():
    show_guided_page(title="ห้องงานวัดผล", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=ASSESSMENT_IMAGE_PATH, waypoint_video=WAYPOINT_ASSESSMENT_VIDEO,
                     travel_key="ASSESSMENT")

# ***************************************************************
    
# -----------------------------------------------------------------
# --- ฟังก์ชันควบคุมหน้าต่างนำทางเฉพาะ (Full Screen) ---
# -----------------------------------------------------------------

def show_navigation_page():
    """ฟังก์ชันเดิมสำหรับแสดงแผนผังนำทางแบบ Full Screen"""
    # NEW: หากเข้าหน้า Full Screen Navigation ให้หยุด Timer แผนก
    unbind_inactivity_reset() 
    
    # ... (โค้ดภายในเหมือนเดิม) ...
    for widget in navigation_content_frame.winfo_children():
        widget.destroy()
        
    back_button_frame = ctk.CTkFrame(navigation_content_frame, fg_color="transparent", height=120)
    back_button_frame.pack(side="top", fill="x", pady=(30, 0), padx=40)
    
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
        map_path_to_load = "Tower/1.png" # Assuming this is the full map
        MAX_NAVIGATION_MAP_HEIGHT = 750 
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
        
    current_slide_index = (current_slide_index - 1 + len(slide_images)) % len(slide_images)
    image_info = slide_images[current_slide_index]
    image_photo = slide_photo_images[current_slide_index]
    image_width = image_info['width']
    image_filename = image_info['filename']
    
    return image_photo, image_width, image_filename, current_slide_index


def place_next_slide(start_immediately_at_right_edge=True):
    """สร้างและวางรูปภาพถัดไปลงบน Canvas"""
    global active_slide_items, image_slide_canvas, SLIDE_GAP
    
    image_photo, image_width, _, next_slide_index = get_next_slide()
    
    if image_photo is None:
        return
        
    if start_immediately_at_right_edge and active_slide_items:
        prev_right_edge = active_slide_items[-1]['right_edge']
        new_x_center = prev_right_edge + SLIDE_GAP + (image_width / 2)
    else:
        # เริ่มต้นวางที่ด้านขวาของหน้าจอ (1080)
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

def place_previous_slide():
    """สร้างและวางรูปภาพก่อนหน้าลงบน Canvas ที่ตำแหน่งด้านซ้าย"""
    global active_slide_items, image_slide_canvas, SLIDE_GAP
    
    image_photo, image_width, _, prev_slide_index = get_previous_slide()
    
    if image_photo is None:
        return
        
    # วางรูปภาพใหม่ต่อจากขอบซ้ายของรูปภาพแรก (ที่ active_slide_items[0])
    first_item = active_slide_items[0]
    # left_edge = center - width/2
    first_item_left_edge = first_item['right_edge'] - first_item['width']
    
    # New center = (left_edge) - (SLIDE_GAP) - (width/2)
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
    
    active_slide_items.insert(0, new_item)

# ***************************************************************
# ** Drag & Click Logic **
# ***************************************************************

def start_drag(event):
    """เริ่มต้นการกด (เตรียมลาก)"""
    global last_x, is_dragging
    last_x = event.x
    is_dragging = False 

def do_drag(event):
    """ทำการลาก (เคลื่อนย้าย)"""
    global last_x, image_slide_canvas, active_slide_items, is_dragging
    
    move_distance = event.x - last_x
    
    if abs(move_distance) > 2:
        is_dragging = True
        last_x = event.x
        
        if not active_slide_items:
            return
        
        # เคลื่อนย้ายรูปภาพทั้งหมด
        for item in active_slide_items:
            image_slide_canvas.move(item['id'], move_distance, 0)
            # Update 'right_edge' for tracking
            item['right_edge'] += move_distance 
        
        # ตรวจสอบและโหลดรูปภาพเพิ่มด้านขวา
        if active_slide_items and active_slide_items[-1]['right_edge'] < 1080 + SLIDE_GAP:
            place_next_slide(start_immediately_at_right_edge=True)
            
        # ตรวจสอบและโหลดรูปภาพเพิ่มด้านซ้าย
        first_item = active_slide_items[0]
        first_item_left_edge = first_item['right_edge'] - first_item['width']
        if first_item_left_edge > -100:
            place_previous_slide()
            
        # ลบรูปภาพที่ออกไปจากขอบซ้ายแล้ว
        if active_slide_items and active_slide_items[0]['right_edge'] < 0:
            item_to_remove = active_slide_items.pop(0)
            image_slide_canvas.delete(item_to_remove['id'])


def stop_drag(event):
    """ปล่อยเมาส์ (ใช้สำหรับการตรวจจับ Click)"""
    pass 

# ***************************************************************
# ** NEW: Navigation Mapping (Filename -> Function) **
# ***************************************************************
NAV_MAPPING = {
    # แผนกวิชา
    "60 ปี.jpg": show_60_years_page, 
    "ก่อสร้าง.jpg": show_construction_page, 
    "ช่างไฟฟ้า.jpg": show_electrical_page, 
    "อิเล็กทรอนิกส์.jpg": show_electronics_page, 
    "ปิโตรเลียม.jpg": show_petroleum_page, 
    "ระบบราง.jpg": show_rail_page, 
    "เทคนิคพื้นฐาน.jpg": show_basic_tech_page, 
    "ช่างเชื่อมโลหะ.jpg": show_welding_page, 
    "โยธา.jpg": show_civil_page, 
    "ตกแต่งภายใน.jpg": show_interior_decoration_page, 
    "ตึกส้ม.jpg": show_computer_tech_page, 
    "ทำความเย็น.jpg": show_air_condi_page, 
    "ช่างยนต์.jpg": show_technic_mac_page, 
    "สถาปัตยกรรม_สำรวจ.jpg": show_arch_survey_page, # รวม 2 แผนก
    "สารสนเทศ_กลโรงงาน.jpg": show_factory_it_page, # รวม 2 แผนก
    "แมคคา_พลังงาน.jpg": show_mechatronics_energy_page, # รวม 2 แผนก
    "ตึก11.jpg": show_airline_logistics_page, # รวม 2 แผนก (การบิน/โลจิสติกส์)
    
    # ห้อง/งาน (ส่วนใหญ่เป็น Room_Pictures)
    "งานประสานงานผู้จบ.jpg": show_graduate_page,
    "งานทวิภาคี.jpg": show_dual_vocational_page,
    "งานแนะแนว.jpg": show_counseling_page,
    "งานพัฒนาหลักสูตร.jpg": show_curriculum_page,
    "งานวินัย_ตึก2.jpg": show_disciplinary_page,
    "งานประเมิน.jpg": show_evaluation_page,
    "งานกิจกรรม.jpg": show_event_page,
    "งานการเงิน.jpg": show_finance_page,
    "งานผลิตและพัฒนากำลังคน.jpg": show_production_page,
    "งานประชาสัมพันธ์.jpg": show_public_relations_page,
    "งานทะเบียน.jpg": show_registration_page,
    "งานพัสดุ.jpg": show_procurement_page,
    "งานวิชาการ.jpg": show_academic_page,
    "งานปกครอง.jpg": show_governance_page,
    "งานวัดผลตึก2-1.jpg": show_assessment_page,
}

def on_slide_click(event):
    """ฟังก์ชันจัดการเมื่อมีการปล่อยเมาส์ (Click Release)"""
    global is_dragging, slide_images, active_slide_items
    
    # ถ้าเป็นการลาก (Dragging) ให้จบการทำงาน
    if is_dragging:
        is_dragging = False # รีเซ็ตสถานะ
        return

    # ถ้าไม่ใช่การลาก (คือการคลิก)
    try:
        # ใช้ find_closest เพื่อหา item ที่คลิก
        item_id_list = image_slide_canvas.find_closest(event.x, event.y)
        if not item_id_list: return
        item_id = item_id_list[0] 
        
        # ค้นหาข้อมูลรูปภาพจาก ID
        clicked_item = None
        for item in active_slide_items:
            if item['id'] == item_id:
                clicked_item = item
                break
        
        if clicked_item:
            # ดึงชื่อไฟล์
            slide_index = clicked_item['slide_index']
            filename = slide_images[slide_index]['filename']
            
            # ตรวจสอบใน Mapping และเรียกฟังก์ชัน
            if filename in NAV_MAPPING:
                print_status(f"คลิกรูปภาพ: {filename}")
                # ใช้ root.after(0, ...) เพื่อให้แน่ใจว่าฟังก์ชันนำทางถูกเรียกใน main thread
                root.after(0, NAV_MAPPING[filename])
            else:
                print_status(f"คลิกรูปภาพ: {filename} (ไม่มีฟังก์ชันนำทางใน NAV_MAPPING)")
                
    except Exception as e:
        print_status(f"Click Error: {e}")

# -----------------------------------------------------------------
# --- ฟังก์ชันสำหรับรูปภาพสไลด์ (Image Marquee) ---
# -----------------------------------------------------------------
def load_slide_images():
    """โหลดรูปภาพทั้งหมดจากโฟลเดอร์ที่กำหนด (รวมถึง Room_Pictures)"""
    global slide_images, slide_photo_images, SLIDE_FRAME_WIDTH, SLIDE_FRAME_COLOR, IMAGE_SLIDE_HEIGHT
    slide_images = []
    slide_photo_images = []
    
    # โฟลเดอร์ที่ต้องการโหลดรูปภาพ
    folders_to_load = [IMAGE_SLIDE_FOLDER, ROOM_IMAGE_FOLDER] 
    
    image_list_map = {} # เก็บเพื่อตรวจสอบซ้ำ
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')

    for folder in folders_to_load:
        if not os.path.exists(folder):
            print_status(f"--- [IMAGE SLIDE ERROR]: ไม่พบโฟลเดอร์: {folder} ---")
            continue
            
        image_files = [f for f in os.listdir(folder) if f.lower().endswith(valid_extensions)]
        image_files.sort()
        
        for filename in image_files:
            # ป้องกันการโหลดไฟล์ชื่อซ้ำ (ถ้ามีในทั้งสองโฟลเดอร์)
            if filename in image_list_map: continue 
            
            try:
                filepath = os.path.join(folder, filename)
                img = Image.open(filepath)
                original_width, original_height = img.size
                
                # ... (Resize logic) ...
                target_image_height = IMAGE_SLIDE_HEIGHT - (SLIDE_FRAME_WIDTH * 2)
                
                if original_height > target_image_height:
                    ratio = target_image_height / original_height
                    new_width = int(original_width * ratio)
                    img = img.resize((new_width, target_image_height), Image.LANCZOS)
                else:
                    if original_height < target_image_height:
                        target_image_height = original_height 
                    target_image_width_limit = 900 - (SLIDE_FRAME_WIDTH * 2) 
                    if img.width > target_image_width_limit:
                        ratio = target_image_width_limit / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((target_image_width_limit, new_height), Image.LANCZOS)
                
                # --- เพิ่มกรอบ (Frame) ให้กับรูปภาพ ---
                img = ImageOps.expand(img, border=SLIDE_FRAME_WIDTH, fill=SLIDE_FRAME_COLOR)
                
                slide_images.append({
                    'filename': filename,
                    'width': img.width,
                    'height': img.height
                })
                slide_photo_images.append(ImageTk.PhotoImage(img))
                image_list_map[filename] = True
                
            except Exception as e:
                print_status(f"ไม่สามารถโหลดรูปภาพ {filename}: {e}")
                
    if not slide_images:
        print_status(f"--- [IMAGE SLIDE]: ไม่พบรูปภาพในโฟลเดอร์ที่กำหนด ---")


def animate_image_slide():
    """เคลื่อนย้ายรูปภาพสไลด์ไปทางซ้ายอย่างต่อเนื่อง"""
    global active_slide_items, image_slide_canvas
    
    # ตรวจสอบว่า Canvas ยังอยู่หรือไม่ (ป้องกันข้อผิดพลาดเมื่อปิดโปรแกรม)
    try:
        if not image_slide_canvas.winfo_exists(): return
    except:
        return
        
    # ระยะการเคลื่อนที่ต่อเฟรม
    move_distance = -3
    
    # เคลื่อนย้ายรูปภาพทั้งหมด
    for item in active_slide_items:
        image_slide_canvas.move(item['id'], move_distance, 0)
        item['right_edge'] += move_distance
    
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
    logo_image = Image.open("logo.png").resize((120, 120))
    logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(120,120))
    logo_label = ctk.CTkLabel(top_bar, image=logo_ctk_image, text="")
    logo_label.pack(side="left", padx=(20,10), pady=15)
except Exception as e:
    print_status(f"ไม่พบไฟล์โลโก้ (logo.png): {e}")
# ข้อความบนแถบ
title_label = ctk.CTkLabel(top_bar, text="HTC Smart Hub", text_color="white", font=("Kanit", 36, "bold"))
title_label.pack(side="left", padx=10, pady=15)

# ***************************************************************
# ** NEW LOCATION: Real-Time Date/Time Clock Placeholder (Right of Top Bar) **
# ***************************************************************
datetime_label = ctk.CTkLabel(
    top_bar, 
    text="กำลังโหลดเวลา...", 
    font=("Kanit", 20, "bold"), 
    text_color="white", # เปลี่ยนเป็นสีขาวเพื่อให้เห็นชัดบนแถบสีม่วง
    justify="right"
)
# วางให้อยู่มุมขวาบนของ top_bar
datetime_label.pack(side="right", padx=20, pady=(15, 0))


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
    qr_image = Image.open("QR/qrcode.png").resize((140, 140))
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
image_slide_canvas.bind("<ButtonRelease-1>", on_slide_click)


# ***************************************************************
# ** Speech Recognition Functions (ทำงานใน Thread แยก) **
# ***************************************************************

def listen_for_speech():
    """ฟังก์ชันหลักในการรับเสียงจากไมค์และแปลงเป็นข้อความ พร้อมแก้ปัญหาค้าง"""
    global is_listening
    r = sr.Recognizer()
    LANGUAGE = "th-TH" 

    is_listening = True 
    print_status("--- [MIC STATUS]: โปรดพูดตอนนี้ (Listening...) ---")
    
    try: 
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.8) 
            
            try:
                # ลด Timeout ลงเล็กน้อยเพื่อให้ไม่ค้างนานเกินไป
                audio = r.listen(source, timeout=5, phrase_time_limit=10) 
                print_status("--- [MIC STATUS]: ได้รับเสียงแล้ว กำลังประมวลผล... ---")
                
                text = r.recognize_google(audio, language=LANGUAGE) 
                
                print("\n*** [RECOGNIZED TEXT] ***")
                print(f"ผลลัพธ์: {text}")
                print("***************************\n")
                
                text_lower = text.lower()
                
                # =================================================================
                # --- MODIFIED: ตรวจสอบคำสั่งทั้งหมด (ครอบคลุมแผนกและห้องใหม่) ---
                # =================================================================
                
                # 0. ตรวจสอบคำสั่งกลับหน้าหลัก
                for keyword in ["กลับหน้าหลัก", "กลับบ้าน", "หน้าแรก", "ไปหน้าหลัก"]:
                    if keyword in text_lower:
                        print_status(f"--- [SYSTEM]: ตรวจพบคำสั่ง: '{keyword}' นำทางกลับหน้าหลัก ---")
                        root.after(0, go_to_main_screen)
                        return
                        
                # --- แผนกวิชา ---
                if any(k in text_lower for k in KEYWORDS_ELECTRONICS): root.after(0, show_electronics_page); return
                if any(k in text_lower for k in KEYWORDS_CONSTRUCTION): root.after(0, show_construction_page); return 
                if any(k in text_lower for k in KEYWORDS_60YEARS): root.after(0, show_60_years_page); return
                if any(k in text_lower for k in KEYWORDS_ELECTRIC): root.after(0, show_electrical_page); return
                if any(k in text_lower for k in KEYWORDS_FURNITURE): root.after(0, show_interior_decoration_page); return
                if any(k in text_lower for k in KEYWORDS_PETROLEUM): root.after(0, show_petroleum_page); return
                if any(k in text_lower for k in KEYWORDS_RAIL): root.after(0, show_rail_page); return
                if any(k in text_lower for k in KEYWORDS_BASICTECH): root.after(0, show_basic_tech_page); return
                # สถาปัตยกรรม/ช่างสำรวจ
                if any(k in text_lower for k in KEYWORDS_ARCHITECT + KEYWORDS_SURVEY): root.after(0, show_arch_survey_page); return
                # กลโรงงาน (รวมสารสนเทศ/IT)
                if any(k in text_lower for k in KEYWORDS_FACTORY + KEYWORDS_IT): root.after(0, show_factory_it_page); return
                # แมคคาทรอนิค/พลังงาน
                if any(k in text_lower for k in KEYWORDS_MECHATRONICS + KEYWORDS_ENERGY): root.after(0, show_mechatronics_energy_page); return
                # การบิน/โลจิสติกส์/ตึก 11
                if any(k in text_lower for k in KEYWORDS_AIRLINE + KEYWORDS_LOGISTICS + KEYWORDS_TUK11): root.after(0, show_airline_logistics_page); return
                if any(k in text_lower for k in KEYWORDS_AUTO): root.after(0, show_technic_mac_page); return
                if any(k in text_lower for k in KEYWORDS_WELDING): root.after(0, show_welding_page); return
                if any(k in text_lower for k in KEYWORDS_AIRCOND): root.after(0, show_air_condi_page); return
                if any(k in text_lower for k in KEYWORDS_CIVIL): root.after(0, show_civil_page); return
                if any(k in text_lower for k in KEYWORDS_COMPUTER_TECH): root.after(0, show_computer_tech_page); return
                if any(k in text_lower for k in KEYWORDS_BASIC_SUBJECTS): root.after(0, show_basic_subjects_page); return
                if any(k in text_lower for k in KEYWORDS_SOUTHERN_CENTER): root.after(0, show_southern_center_page); return
                    
                # --- ห้อง/งาน (UPDATED) ---
                if any(k in text_lower for k in KEYWORDS_GRADUATE): root.after(0, show_graduate_page); return
                if any(k in text_lower for k in KEYWORDS_DUAL_VOCATIONAL): root.after(0, show_dual_vocational_page); return
                if any(k in text_lower for k in KEYWORDS_COUNSELING): root.after(0, show_counseling_page); return
                if any(k in text_lower for k in KEYWORDS_CURRICULUM): root.after(0, show_curriculum_page); return
                if any(k in text_lower for k in KEYWORDS_DISCIPLINARY): root.after(0, show_disciplinary_page); return
                if any(k in text_lower for k in KEYWORDS_EVALUATION): root.after(0, show_evaluation_page); return
                if any(k in text_lower for k in KEYWORDS_EVENT): root.after(0, show_event_page); return
                if any(k in text_lower for k in KEYWORDS_FINANCE): root.after(0, show_finance_page); return
                if any(k in text_lower for k in KEYWORDS_PRODUCTION): root.after(0, show_production_page); return
                if any(k in text_lower for k in KEYWORDS_PUBLIC_RELATIONS): root.after(0, show_public_relations_page); return
                if any(k in text_lower for k in KEYWORDS_REGISTRATION): root.after(0, show_registration_page); return
                if any(k in text_lower for k in KEYWORDS_PROCUREMENT): root.after(0, show_procurement_page); return
                if any(k in text_lower for k in KEYWORDS_ACADEMIC): root.after(0, show_academic_page); return
                if any(k in text_lower for k in KEYWORDS_GOVERNANCE): root.after(0, show_governance_page); return
                if any(k in text_lower for k in KEYWORDS_ASSESSMENT): root.after(0, show_assessment_page); return

            
            except sr.WaitTimeoutError:
                print_status("--- [MIC ERROR]: ไม่ได้รับเสียงภายใน 5 วินาที ---")
            except sr.UnknownValueError:
                print_status("--- [MIC ERROR]: ไม่สามารถเข้าใจคำพูด (UnknownValueError) ---")
            except sr.RequestError as e:
                print_status(f"--- [MIC ERROR]: ไม่สามารถเชื่อมต่อกับ Google Speech (ตรวจสอบอินเทอร์เน็ต); {e} ---")
            except Exception as e:
                print_status(f"--- [MIC ERROR]: เกิดข้อผิดพลาดในการประมวลผล: {e} ---") 
            
    finally:
        is_listening = False
        print_status("--- [MIC STATUS]: การฟังเสร็จสิ้น (IDLE) ---")


        
def start_listening_thread(event=None):
    """Start the listening process in a separate thread to prevent freezing"""
    global is_listening
    if not is_listening:
        # NEW: หยุด Timer Inactivity ชั่วคราวเมื่อเริ่มฟัง
        unbind_inactivity_reset()
        Thread_Mic = threading.Thread(target=listen_for_speech)
        Thread_Mic.start()
    else:
        print_status("--- [SYSTEM]: ระบบกำลังฟังอยู่... ---")


try:
    # 1. Create the Frame
    mic_frame = tk.Frame(root, bg="white", width=180, height=180)
    # วางไว้ที่ตำแหน่งที่เหมาะสม (725 คือตำแหน่งที่ไม่ทับกับส่วนกลาง)
    mic_frame.place(x=20, y=725) 

    # 2. Create Canvas
    mic_canvas = tk.Canvas(
        mic_frame,
        width=180,
        height=180,
        bg="white",
        highlightthickness=0,
        bd=0
    )
    mic_canvas.pack()
    
    # 3. Bind Click Events
    mic_canvas.bind("<Button-1>", start_listening_thread) 
    mic_frame.bind("<Button-1>", start_listening_thread)

    # 4. Load Image Safely
    MIC_IMAGE_PATH = "microphone/microphone.png" 
    
    if os.path.exists(MIC_IMAGE_PATH):
        mic_image = Image.open(MIC_IMAGE_PATH).resize((90, 90))
        mic_photo = ImageTk.PhotoImage(mic_image)
    else:
        print_status(f"Warning: Microphone image not found at {MIC_IMAGE_PATH}")
        mic_image = Image.new('RGBA', (90, 90), (200, 200, 200, 0))
        mic_photo = ImageTk.PhotoImage(mic_image)

    # 5. Create Aura Circles
    aura_circles = []
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
        aura_circles.append(circle) 

    # 6. Place Microphone Icon in Center
    mic_canvas.create_image(90, 90, image=mic_photo, tags="mic")
    mic_canvas.image = mic_photo 

    # 7. Aura Animation Function
    def animate_aura():
        global is_listening, alpha_value, direction, mic_canvas, aura_circles
        
        try:
            if not mic_canvas.winfo_exists(): return
        except: return

        if is_listening:
            base_color_hex = ["#FFD700", "#FFA500", "#FF4500"] 
            speed = 4.0
            border_width = 5
        else:
            base_color_hex = ["#E0B0FF", "#C77DFF", "#9D4EDD"] 
            speed = 1.5
            border_width = 3
        
        # Update Alpha/Pulse
        alpha_value[0] += direction[0] * speed
        if alpha_value[0] >= 100:
            alpha_value[0] = 100
            direction[0] = -1
        elif alpha_value[0] <= 0:
            alpha_value[0] = 0
            direction[0] = 1

        intensity = alpha_value[0] / 100.0
        
        # Calculate colors
        colors_animated = []
        for hex_color in base_color_hex:
            r_base = int(hex_color[1:3], 16)
            g_base = int(hex_color[3:5], 16)
            b_base = int(hex_color[5:7], 16)
            
            # Pulse logic
            r_final = int(r_base * (0.6 + 0.4 * intensity)) 
            g_final = int(g_base * (0.6 + 0.4 * intensity))
            b_final = int(b_base * (0.6 + 0.4 * intensity))
            
            colors_animated.append(f"#{r_final:02x}{g_final:02x}{b_final:02x}")

        # Update Canvas
        for i, circle in enumerate(aura_circles):
            mic_canvas.itemconfig(circle, outline=colors_animated[i], width=border_width)

        root.after(20, animate_aura)

    # Start Animation
    animate_aura()
    mic_frame.lift()

except Exception as e:
    print_status(f"Error creating Microphone UI: {e}")

# ***************************************************************
# ** Initialization and Main Loop **
# ***************************************************************

# เริ่มต้นโหลดรูปภาพสไลด์ (รวมถึง Room_Pictures)
load_slide_images()

# เริ่มต้นแสดงสไลด์ชุดแรก
if slide_images:
    for i in range(min(5, len(slide_images))): # สร้าง 5 สไลด์แรกเพื่อครอบหน้าจอ
        place_next_slide(start_immediately_at_right_edge=False)

# เริ่มต้น Animation Marquee
animate_image_slide()


# แสดงเฟรมเริ่มต้น (Home)
show_frame(home_content_frame)

# NEW: เริ่มต้นนาฬิกา
update_datetime_clock() 

# Main Loop
root.mainloop()