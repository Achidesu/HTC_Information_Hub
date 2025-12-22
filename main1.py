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
import random
import pygame

# จำลองการ import จาก main1 (เพื่อให้โค้ดรันได้โดยไม่มี main1.py)
# NOTE: ค่าเหล่านี้จะถูกกำหนดใหม่ในส่วนของ Path ด้านล่าง
ASSESSMENT_IMAGE_PATH = "" 
GOVERNANCE_IMAGE_PATH = "" 
WAYPOINT_ASSESSMENT_VIDEO = ""
WAYPOINT_GOVERNANCE_VIDEO = ""

from gtts import gTTS
import os

def speak_thai(text):
    """ฟังก์ชันสำหรับสร้างเสียงพูดและเล่นเสียง"""
    def run_speak():
        try:
            tts = gTTS(text=text, lang='th')
            filename = "temp_voice.mp3"
            tts.save(filename)
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload() # คืนไฟล์เพื่อให้ระบบลบได้
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            print(f"Speak Error: {e}")
            
    # รันใน Thread เพื่อไม่ให้ UI ค้าง
    threading.Thread(target=run_speak, daemon=True).start()

# Initialize audio mixer
try:
    pygame.mixer.init()
except:
    print("Audio device not found.")

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
root.attributes("-fullscreen", True)
root.overrideredirect(True)
root.geometry("1080x1920+0+0") 
root.configure(fg_color="white")
root.bind("<Escape>", lambda e: root.destroy())

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
# ** EXPANDED: Global Keyword Lists (คำค้นหาที่ครอบคลุมยิ่งขึ้น) **
# ***************************************************************

# --- คำสั่งทั่วไป (General Commands) ---
# --- คำสั่งทั่วไป (General Commands) ---
KEYWORDS_HOME = [
    "กลับหน้าหลัก", "หน้าหลัก", "กลับหน้าแรก", "หน้าแรก", "เมนูหลัก", "เริ่มต้นใหม่", 
    "home", "main menu", "back", "start over", "กลับ", "ยกเลิก", "รีเซ็ต"
]

# --- แผนกวิชา (Departments) ---
KEYWORDS_ELECTRONICS = [
    "อิเล็กทรอนิกส์", "อิเล็ก", "อีเล็ก", "แผนกอิเล็ก", "ช่างอิเล็ก", "ตึกอิเล็ก", 
    "วงจร", "electronic", "electronics", "circuit","อาคาร4","คาร4","ตึก4"
]
KEYWORDS_CONSTRUCTION = [
    "ช่างก่อสร้าง", "ก่อสร้าง", "ตึกก่อสร้าง", "แผนกก่อสร้าง", "construction", "civil works","อาคาร5","คาร5","ตึก5"
]
KEYWORDS_CIVIL = [
    "ช่างโยธา", "โยธา", "แผนกโยธา", "ตึกโยธา", "civil", "civil engineer","อาคาร5","คาร5","ตึก5"
]
KEYWORDS_FURNITURE = [
    "ช่างเฟอร์นิเจอร์", "ตกแต่งภายใน", "เฟอร์นิเจอร์", "ออกแบบภายใน", "อินทีเรีย", 
    "furniture", "interior", "design", "wood work", "งานไม้",""
]
KEYWORDS_SURVEY = [
    "ช่างสำรวจ", "สำรวจ", "แผนกสำรวจ", "ตึกสำรวจ", "survey", "land survey"
]
KEYWORDS_ARCHITECT = [
    "สถาปัตยกรรม", "สถาปัตย์", "สถาปัต", "แผนกสถาปัตย์", "ตึกสถาปัตย์", "architect", "architecture", "ออกแบบบ้าน"
]
KEYWORDS_AUTO = [
    "ช่างยนต์", "ยนต์", "ยานยนต์", "เครื่องยนต์", "แผนกช่างยนต์", "ตึกช่างยนต์", 
    "ซ่อมรถ", "garage", "auto", "mechanic", "automotive"
]
KEYWORDS_FACTORY = [
    "ช่างกลโรงงาน", "กลโรงงาน", "โรงงาน", "ช่างกล", "แผนกกลโรงงาน", "machine", "factory", "machinist","เครื่องกล","เครื่องกลโรงงาน"
]
KEYWORDS_WELDING = [
    "ช่างเชื่อมโลหะ", "เชื่อมโลหะ", "เชื่อม", "ช่างเชื่อม", "แผนกเชื่อม", "welding", "metal work"
]
KEYWORDS_BASICTECH = [
    "ช่างเทคนิคพื้นฐาน", "เทคนิคพื้นฐาน", "พื้นฐานช่าง", "ตึกพื้นฐาน", "basic tech", "workshop"
]
KEYWORDS_ELECTRIC = [
    "ช่างไฟฟ้า", "ไฟฟ้า", "ไฟฟ้ากำลัง", "ไฟ", "แผนกไฟฟ้า", "ตึกไฟฟ้า", "electric", "electrical", "power""อาคาร5","คาร5","ตึก5"
]
KEYWORDS_AIRCOND = [
    "เครื่องทำความเย็น", "ปรับอากาศ", "แอร์", "ช่างแอร์", "ระบบความเย็น", "ทำความเย็น", 
    "air condition", "refrigeration", "cool"
]
KEYWORDS_IT = [
    "เทคโนโลยีสารสนเทศ", "ไอที", "สารสนเทศ", "ข้อมูล", "it", "information technology", "programmer", "network",
]
KEYWORDS_PETROLEUM = [
    "เทคโนโลยีปิโตรเลียม", "ปิโตรเลียม", "ปิโตร", "น้ำมัน", "แท่นขุดเจาะ", "petroleum", "oil", "gas", "offshore"
]
KEYWORDS_ENERGY = [
    "เทคนิคพลังงาน", "พลังงาน", "ทดแทน", "โซลาร์เซลล์", "energy", "solar", "power plant",
]
KEYWORDS_LOGISTICS = [
    "โลจิสติกส์", "ซัพพลายเชน", "ขนส่ง", "logistics", "shipping", "supply chain","โลจิส",
]
KEYWORDS_RAIL = [
    "ระบบขนส่งทางราง", "ขนส่งทางราง", "ราง", "ระบบราง", "รถไฟ", "ช่างรถไฟ", "rail", "railway", "train"
]
KEYWORDS_MECHATRONICS = [
    "เมคคาทรอนิกส์", "เมคคา", "แม็กคา", "แมคคา", "หุ่นยนต์", "robot", "mechatronics", "automation", "แขนกล"
]
KEYWORDS_AIRLINE = [
    "แผนกการบิน", "การบิน", "ธุรกิจการบิน", "แอร์ไลน์", "สนามบิน", "aviation", "airline", "airport"
]
KEYWORDS_COMPUTER_TECH = [
    "เทคโนโลยีคอมพิวเตอร์", "เทคโนโลยีคอม", "คอมพิวเตอร์", "คอมพิว", "ตึกส้ม", "ช่างคอม", 
    "computer tech", "hardware", "computer","อาคาร7","คาร7","ตึก7","สถาบันการอาชีวศึกษาภาคใต้3","สถาบันอาชีวศึกษา"
]
KEYWORDS_BASIC_SUBJECTS = [
    "วิชาพื้นฐาน", "พื้นฐาน", "วิชาสามัญ", "คณิตศาสตร์", "ภาษาไทย", "ภาษาอังกฤษ", "วิทย์", "สังคม", 
    "math", "science", "english", "thai", "general subjects"
]
KEYWORDS_SOUTHERN_CENTER = [
    "ศูนย์ส่งเสริม", "อาชีวศึกษาภาคใต้", "ส่งเสริม", "ภาคใต้", "southern center"
]
KEYWORDS_60YEARS = [
    "ตึก 60 ปี", "60 ปี", "อาคาร 60 ปี", "อาคารเฉลิมพระเกียรติ", "60th anniversary building"
]
KEYWORDS_TUK11 = [
    "ตึก 11", "อาคาร 11", "ตึกใหม่", "building 11", "ตึกหน้าแผนกอิเล็กทรอนิกส์"
]
# [NEW] เพิ่มอาคาร 10
KEYWORDS_TUK10 = [
    "ตึก 10", "อาคาร 10", "อาคารสิบ", "building 10",
]


# --- ห้อง/งานอำนวยการ (Offices & Rooms) - เพิ่มคำกริยาที่คนชอบใช้ ---
KEYWORDS_COUNSELING = [
    "ห้องแนะแนว", "งานแนะแนว", "แนะแนว", "ปรึกษาปัญหา", "กยศ", "ทุนการศึกษา", "กู้เรียน", "guidance", "scholarship"
] 
KEYWORDS_CURRICULUM = [
    "ห้องพัฒนาหลักสูตร", "งานพัฒนาหลักสูตร", "หลักสูตร", "การเรียนการสอน", "แผนการเรียน", "curriculum"
]
KEYWORDS_DISCIPLINARY = [
    "ห้องวินัย", "งานวินัย", "ฝ่ายปกครอง", "คะแนนความประพฤติ", "ตัดคะแนน", "วินัย", "ทำโทษ", "discipline", "behavior"
]
KEYWORDS_EVALUATION = [
    "ห้องประเมิน", "งานประเมิน", "ประเมินผล", "evaluation"
]
KEYWORDS_EVENT = [
    "ห้องกิจกรรม", "งานกิจกรรม", "กิจกรรม", "เข้าแถว", "ชมรม", "ลูกเสือ", "รด", "activities", "club"
]
KEYWORDS_FINANCE = [
    "ห้องการเงิน", "งานการเงิน", "การเงิน", "จ่ายเงิน", "ชำระเงิน", "ค่าเทอม", "จ่ายค่าเทอม", "ใบเสร็จ", "finance", "tuition"
]
KEYWORDS_PRODUCTION = [
    "ห้องผลิตและพัฒนากำลังคน", "งานผลิต", "พัฒนากำลังคน", "กำลังคน", "manpower"
]
KEYWORDS_PUBLIC_RELATIONS = [
    "ห้องประชาสัมพันธ์", "งานประชาสัมพันธ์", "ประชาสัมพันธ์", "ประกาศ", "ข่าวสาร", "pr", "public relations"
]
KEYWORDS_REGISTRATION = [
    "ห้องทะเบียน", "งานทะเบียน", "ทะเบียน", "ลงทะเบียน", "แก้เกรด", "รีเกรด", "เพิ่มถอน", 
    "ขอใบเกรด", "ใบรับรอง", "transcript", "registration", "grade", "gpa"
]
KEYWORDS_PROCUREMENT = [
    "ห้องพัสดุ", "งานพัสดุ", "พัสดุ", "จัดซื้อ", "เบิกของ", "procurement", "supplies"

]
KEYWORDS_GOVERNANCE = [
    "ห้องงานปกครอง", "งานปกครอง", "ปกครอง", "หัวหน้าตึก", "สารวัตรนักเรียน", "governance"
]
KEYWORDS_ASSESSMENT = [
    "ห้องงานวัดผล", "งานวัดผล", "วัดผล", "สอบแก้ตัว", "สอบซ่อม", "เกรดออก", "assessment", "re-exam"
]
KEYWORDS_GRADUATE = [
    "งานประสานงานผู้จบ", "งานผู้จบ", "ห้องผู้จบ", "คนจบ", "รับวุฒิ", "รับประกาศนียบัตร", "จบการศึกษา", "graduate", "diploma"
]
KEYWORDS_DUAL_VOCATIONAL = [
    "งานทวิภาคี", "ห้องทวิภาคี", "ทวิภาคี", "ฝึกงาน", "ฝึกอาชีพ", "สถานประกอบการ", "internship", "dual vocational"
]

# --- NEW: จุดบริการและงานอำนวยการเพิ่มเติม ---
KEYWORDS_COOP_SHOP = [
    "ร้านค้าสวัสดิการ", "สวัสดิการ", "ร้านค้า", "สหกรณ์", "coop", "shop"
]
KEYWORDS_CANTEEN1 = [
    "โรงอาหาร 1", "โรงอาหารหนึ่ง", "โรงอาหาร1", "แคนทีน 1", "กินข้าว 1","โรงอาหารเก่า"
]
KEYWORDS_CANTEEN2 = [
    "โรงอาหาร 2", "โรงอาหารสอง", "โรงอาหาร2", "แคนทีน 2", "กินข้าว 2","โรงอาหารใหม่"
]
KEYWORDS_BUILDING2 = [
    "อาคาร 2", "ตึก 2", "building 2", 
]
KEYWORDS_BUILDING3 = [
    "อาคาร 3", "ตึก 3", "building 3", 
]
KEYWORDS_LIBRARY = [
    "ห้องสมุด", "อ่านหนังสือ", "ยืมหนังสือ", "library", "book", "reading room", "อาคาร60พรรษามหาราชินี", "อาคาร60พรรษา"
]

KEYWORDS_GYM = [
    "โรงยิม", "ยิม", "ออกกำลังกาย", "gym", "sport hall"
]
KEYWORDS_FUTSAL = [
    "สนามฟุตซอล", "ฟุตซอล", "futsal"
]
KEYWORDS_MEETING_ROOM = [
    "ห้องประชุม", "ประชุม", "meeting room", "หอประชุม"
]
KEYWORDS_CENTRAL_PROCUREMENT = [
    "ห้องพัสดุกลาง", "พัสดุกลาง", "เบิกของกลาง", "central procurement"
]
KEYWORDS_PARKING = [
    "โรงจอดรถ", "ที่จอดรถ", "จอดรถ", "parking lot", "garage"
]
KEYWORDS_FOOTBALL = [
    "สนามฟุตบอล", "ฟุตบอล", "football field"
]
KEYWORDS_TENNIS = [
    "สนามเทนนิส", "เทนนิส", "tennis court"
]
KEYWORDS_FIXIT = [
    "ศูนย์ซ่อมสร้างชุมชน", "ซ่อมสร้างชุมชน", "fixit center", "ซ่อมเครื่องใช้","ศูนย์ซ่อม"
]
KEYWORDS_GENERAL_ADMIN = [
    "งานบริหารทั่วไป", "ธุรการ", "งานทั่วไป", "general admin"
]
KEYWORDS_INFO_DATA = [
    "งานศูนย์ข้อมูลสารสนเทศ", "ศูนย์ข้อมูล", "งานส่งเสริมผลิตผล", "งานประกอบธุรกิจ", "information center", "business promotion"
]
KEYWORDS_ACADEMIC_TOWER = [
    "อาคารวิทยฐานะ", "วิทยฐานะ", "academic tower","สถานีวิทยุ"
]
KEYWORDS_HR = [
    "งานบุคลากร", "บุคลากร", "ฝ่ายบุคคล", "hr", "human resources"
]
KEYWORDS_ACCOUNTING_PLANNING_COOP = [
    "งานการบัญชี", "งานการวางแผน", "งานงบประมาณ", "งานความร่วมมือ", "accounting", "planning", "budget", "cooperation","งานบัญชี","งานวางแผน","งานงบประมาณ"
]
KEYWORDS_PLANNING_COOP_VICE_DIRECTOR = [
    "รองผู้อำนวยการฝ่ายแผนงานและความร่วมมือ", "รองแผนงาน", "รองความร่วมมือ", "vice director planning"
]
KEYWORDS_STUDENT_AFFAIRS_VICE_DIRECTOR = [
    "รองผู้อำนวยการฝ่ายพัฒนากิจการนักเรียน", "รองกิจการนักเรียน", "รองกิจการ", "vice director student affairs"
]
KEYWORDS_ACADEMIC_VICE_DIRECTOR = [
    "รองผู้อำนวยการฝ่ายวิชาการ", "รองวิชาการ", "vice director academic", "วิชาการ", "ห้องวิชาการ", "ฝ่ายวิชาการ"
]
KEYWORDS_RESOURCE_VICE_DIRECTOR = [
    "รองผู้อำนวยการฝ่ายบริหารทรัพยากร", "รองบริหารทรัพยากร", "vice director resource","ทรัพยากร"
]
#.........

# ***************************************************************
# ** NEW: ระยะทางและระยะเวลาเดินทาง (โดยประมาณ) **
# ***************************************************************

# โครงสร้าง: (ระยะทาง (เมตร), เวลา (นาที))
DEFAULT_TRAVEL = (150, 2.5) # ค่าเริ่มต้นสำหรับแผนก/ห้องที่ไม่มีข้อมูล
TRAVEL_INFO = {
    # แผนกวิชา (เดิม)
    "ELECTRONICS": (200, 3),
    "CONSTRUCTION": (350, 5),
    "CIVIL": (300, 4),
    "FURNITURE": (400, 6),
    "SURVEY": (450, 6), 
    "ARCHITECT": (450, 6),
    "AUTO": (250, 3),
    "FACTORY": (500, 7),
    "WELDING": (300, 4),
    "BASICTECH": (250, 3),
    "ELECTRIC": (180, 2),
    "AIRCOND": (380, 5),
    "IT": (500, 7), 
    "PETROLEUM": (550, 8),
    "ENERGY": (600, 8), 
    "LOGISTICS": (650, 9), 
    "RAIL": (700, 10),
    "MECHATRONICS": (600, 8),
    "AIRLINE": (650, 9),
    "COMPUTER_TECH": (100, 1),
    "BASIC_SUBJECTS": (150, 2),
    "SOUTHERN_CENTER": (180, 2),
    "60YEARS": (50, 1),
    "TUK11": (650, 9), 
    # [NEW] อาคาร 10
    "TUK10": (500, 7), 
    
    # ห้อง/งาน (เดิม)
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
    
    # NEW: จุดบริการและงานอำนวยการเพิ่มเติม
    "COOP_SHOP": (200, 3),
    "CANTEEN1": (150, 2),
    "CANTEEN2": (300, 4),
    "BUILDING2": (100, 1),
    "BUILDING3": (250, 3),
    "LIBRARY": (250, 3), 
    "GYM": (400, 5),
    "FUTSAL": (450, 6),
    "MEETING_ROOM": (150, 2),
    "CENTRAL_PROCUREMENT": (220, 3),
    "PARKING": (50, 1),
    "FOOTBALL": (500, 7),
    "TENNIS": (350, 4),
    "FIXIT": (300, 4),
    "GENERAL_ADMIN": (50, 1),
    "INFO_DATA": (100, 1),
    "ACADEMIC_TOWER": (180, 2),
    "HR": (50, 1),
    "ACCOUNTING_PLANNING_COOP": (50, 1),
    "PLANNING_COOP_VICE_DIRECTOR": (50, 1),
    "STUDENT_AFFAIRS_VICE_DIRECTOR": (50, 1),
    "ACADEMIC_VICE_DIRECTOR": (50, 1),
    "RESOURCE_VICE_DIRECTOR": (50, 1),
}


# ***************************************************************
# ** PATHS AND WAYPOINTS **
# ***************************************************************
IMAGE_SLIDE_FOLDER = "Picture_slide" 
ROOM_IMAGE_FOLDER = "room"
ROOM_VIDEO_FOLDER = "room"
ADDON_IMAGE_FOLDER = "AddOn" 
ADDON_VIDEO_FOLDER = "AddOn"
IMAGE_SLIDE_HEIGHT = 200
SLIDE_GAP = 40
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
SIXTY_YEARS_DEPT_IMAGE_PATH   = os.path.join(ADDON_IMAGE_FOLDER, "อาคาร60ปี.jpg")#ยังไม่ลอง
WELDING_DEPT_IMAGE_PATH       = os.path.join(IMAGE_SLIDE_FOLDER, "ช่างเชื่อมโลหะ.jpg")

# --- WAYPOINT VIDEOS (Dept) ---
WAYPOINT_AIRCONDI_VIDEO        = "Tower/Waypoint_Video/To_AIRCONDI.mp4"
WAYPOINT_AIRLINE_VIDEO         = "Tower/Waypoint_Video/To_AIRLINE.mp4"
WAYPOINT_ARCHITECT_VIDEO       = "Tower/Waypoint_Video/To_ARCHITECT.mp4"
WAYPOINT_AUTO_VIDEO            = "Tower/Waypoint_Video/To_AUTO.mp4"
WAYPOINT_BASIC_TECH_VIDEO      = "Tower/Waypoint_Video/To_BASIC.mp4"
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
WAYPOINT_BASIC_SUBJECTS_VIDEO = "" 
WAYPOINT_SOUTHERN_CENTER_VIDEO = "" 
WAYPOINT_60YEARS_VIDEO = os.path.join(ADDON_VIDEO_FOLDER, "To_60yearold_building.mp4")
# [NEW] อาคาร 10
WAYPOINT_TUK10_VIDEO = os.path.join(ADDON_VIDEO_FOLDER,"To_Building_10.mp4")
TUK10_IMAGE_PATH     = os.path.join(ADDON_IMAGE_FOLDER, "อาคาร10.jpg") 

# --- ROOM PATHS & VIDEOS ---
def get_room_path(folder, filename):
    return os.path.join(folder, filename)

# [NEW] ฟังก์ชันสำหรับดึง Path จากโฟลเดอร์ AddOn
def get_addon_path(folder, filename):
    return os.path.join(folder, filename)

# GRADUATE - งานประสานงานและส่งเสริมผู้จบ 
WAYPOINT_GRADUATE_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_GraduateCoordinationCenter.mp4")
GRADUATE_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "ศูนย์ประสานงานบัณฑิตศึกษา.jpg") 

# COUNSELING - ห้องแนะแนว 
WAYPOINT_COUNSELING_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_counseling_room.mp4")
COUNSELING_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานแนะแนวและการจัดหางาน.jpg") 

# CURRICULUM - ห้องพัฒนาหลักสูตร 
WAYPOINT_CURRICULUM_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Curriculumdevelopmentroom.mp4")
CURRICULUM_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "ห้องงานพัฒนาหลักสูตร.jpg") 

# DISCIPLINARY - ห้องวินัย / งานปกครอง 
WAYPOINT_DISCIPLINARY_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_disciplinary_office.mp4")
DISCIPLINARY_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานปกครองและงานครูที่ปรึกษา.jpg") 

# DUAL_VOCATIONAL - งานทวิภาคี 
WAYPOINT_DUAL_VOCATIONAL_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Dual VocationalEducation_Room.mp4")
DUAL_VOCATIONAL_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "ห้องงานอาชีวศึกษาระบบทวิภาคี.jpg") 

# EVALUATION - ห้องประเมิน
WAYPOINT_EVALUATION_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_evaluation_room.mp4")
EVALUATION_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานวัดผลและประเมินผล.jpg") 

# EVENT - ห้องกิจกรรม / งานพัฒนากิจการนักเรียน 
WAYPOINT_EVENT_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_eventroom.mp4")  
EVENT_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "กิจกรรมนักเรียน.jpg")

# FINANCE - ห้องการเงิน 
WAYPOINT_FINANCE_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Finance room.mp4")
FINANCE_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานการเงิน.jpg") 

# PUBLIC_RELATIONS - ห้องประชาสัมพันธ์ 
WAYPOINT_PUBLIC_RELATIONS_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_public_relations_room.mp4")
PUBLIC_RELATIONS_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "ประชาสัมพันธ์.jpg") 

# REGISTRATION - ห้องทะเบียน 
WAYPOINT_REGISTRATION_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_registeroion.mp4")
REGISTRATION_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานทะเบียน.jpg") 

# PROCUREMENT - ห้องพัสดุ
WAYPOINT_PROCUREMENT_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Procurement.mp4") 
PROCUREMENT_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานพัสดุ.jpg") 

# ACADEMIC - ห้องวิชาการ
WAYPOINT_ACADEMIC_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_Academic.mp4") 
ACADEMIC_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานวิชาการ.jpg") 

# GOVERNANCE - ห้องงานปกครอง 
WAYPOINT_GOVERNANCE_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_disciplinary_office.mp4")
GOVERNANCE_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานปกครองและงานครูที่ปรึกษา.jpg")

# ASSESSMENT - ห้องงานวัดผล 
WAYPOINT_ASSESSMENT_VIDEO = get_room_path(ROOM_VIDEO_FOLDER, "To_evaluation_room.mp4")
ASSESSMENT_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "งานวัดผล.webp") 

# PRODUCTION - ห้องผลิตและพัฒนากำลังคน 
WAYPOINT_PRODUCTION_VIDEO = get_room_path(ROOM_VIDEO_FOLDER,"To_Production_Manpower.mp4" ) 
PRODUCTION_IMAGE_PATH     = get_room_path(ROOM_IMAGE_FOLDER, "ศูนย์ประสานงานผลิตและพัฒนากำลังคน.jpg") 


# --- NEW: PATHS สำหรับจุดบริการใหม่ (ปรับปรุงให้ใช้ชื่อไฟล์ที่เสถียร) ---

# ร้านค้าสวัสดิการ
WAYPOINT_COOP_SHOP_VIDEO            = get_addon_path(ADDON_VIDEO_FOLDER, "To_Coop_Shop.mp4") 
COOP_SHOP_IMAGE_PATH                = get_addon_path(ADDON_IMAGE_FOLDER, "ร้านค้าสวัสดิการ.jpg") 

# โรงอาหาร 1
WAYPOINT_CANTEEN1_VIDEO             = get_addon_path(ADDON_VIDEO_FOLDER, "To_Canteen_1.mp4") 
CANTEEN1_IMAGE_PATH                 = get_addon_path(ADDON_IMAGE_FOLDER, "โรงอาหาร1.jpg") 

# โรงอาหาร 2
WAYPOINT_CANTEEN2_VIDEO             = get_addon_path(ADDON_VIDEO_FOLDER, "To_Canteen_2.mp4") 
CANTEEN2_IMAGE_PATH                 = get_addon_path(ADDON_IMAGE_FOLDER, "โรงอาหาร2.jpg") 

# อาคาร 2
WAYPOINT_BUILDING2_VIDEO            = get_addon_path(ADDON_VIDEO_FOLDER, "To_Building_2.mp4") 
BUILDING2_IMAGE_PATH                = get_addon_path(ADDON_IMAGE_FOLDER, "อาคาร2.jpg") 

# อาคาร 3
WAYPOINT_BUILDING3_VIDEO            = get_addon_path(ADDON_VIDEO_FOLDER, "To_Building_3.mp4") 
BUILDING3_IMAGE_PATH                = get_addon_path(ADDON_IMAGE_FOLDER, "อาคาร3.jpg") 

# ห้องสมุด 
WAYPOINT_LIBRARY_VIDEO              = get_addon_path(ADDON_VIDEO_FOLDER, "To_Library.mp4")
LIBRARY_IMAGE_PATH                  = get_addon_path(ADDON_IMAGE_FOLDER, "ห้องสมุด.jpg") 

# โรงยิม
WAYPOINT_GYM_VIDEO                  = get_addon_path(ADDON_VIDEO_FOLDER, "To_Gym.mp4")
GYM_IMAGE_PATH                      = get_addon_path(ADDON_IMAGE_FOLDER, "โรงยิม.jpg") 

# สนามฟุตซอล
WAYPOINT_FUTSAL_VIDEO               = get_addon_path(ADDON_VIDEO_FOLDER, "To_Futsal_Court.mp4")
FUTSAL_IMAGE_PATH                   = get_addon_path(ADDON_IMAGE_FOLDER, "สนามฟุตซอล.jpg") 

# ห้องประชุม 
WAYPOINT_MEETING_ROOM_VIDEO         = get_addon_path(ADDON_VIDEO_FOLDER, "To_Auditorium.mp4")
MEETING_ROOM_IMAGE_PATH             = get_addon_path(ADDON_IMAGE_FOLDER, "ห้องประชุม.jpg") 

# ห้องพัสดุกลาง
WAYPOINT_CENTRAL_PROCUREMENT_VIDEO  = get_addon_path(ADDON_VIDEO_FOLDER, "To_Central_Procurement.mp4") 
CENTRAL_PROCUREMENT_IMAGE_PATH      = get_addon_path(ADDON_IMAGE_FOLDER, "ห้องพัสดุกลาง.jpg") 

# โรงจอดรถ
WAYPOINT_PARKING_VIDEO              = get_addon_path(ADDON_VIDEO_FOLDER, "To_Parking_Lot.mp4") 
PARKING_IMAGE_PATH                  = get_addon_path(ADDON_IMAGE_FOLDER, "โรงจอดรถ.jpg") 

# สนามฟุตบอล
WAYPOINT_FOOTBALL_VIDEO             = get_addon_path(ADDON_VIDEO_FOLDER, "To_Football_Field.mp4")
FOOTBALL_IMAGE_PATH                 = get_addon_path(ADDON_IMAGE_FOLDER, "สนามฟุตบอล.jpg") 

# สนามเทนนิส
WAYPOINT_TENNIS_VIDEO               = get_addon_path(ADDON_VIDEO_FOLDER, "To_Tennis_Court.mp4")
TENNIS_IMAGE_PATH                   = get_addon_path(ADDON_IMAGE_FOLDER, "สนามเทนนิส.jpg") 

# ศูนย์ซ่อมสร้างชุมชน และ Fixit center
WAYPOINT_FIXIT_VIDEO                = get_addon_path(ADDON_VIDEO_FOLDER, "To_Fixit_Center.mp4") 
FIXIT_IMAGE_PATH                    = get_addon_path(ADDON_IMAGE_FOLDER, "ศูนย์ซ่อมสร้างชุมชนและFixitcenter.jpg") 

# งานบริหารทั่วไป
WAYPOINT_GENERAL_ADMIN_VIDEO        = get_addon_path(ADDON_VIDEO_FOLDER, "To_General_Administration.mp4")
GENERAL_ADMIN_IMAGE_PATH            = get_addon_path(ADDON_IMAGE_FOLDER, "งานบริหารทั่วไป.jpg") 

# งานศูนย์ข้อมูลสารสนเทศและงานส่งเสริมผลิตผลการและประกอบธุรกิจ
WAYPOINT_INFO_DATA_VIDEO            = get_addon_path(ADDON_VIDEO_FOLDER, "To_Info_Data.mp4") 
INFO_DATA_IMAGE_PATH                = get_addon_path(ADDON_IMAGE_FOLDER, "ศูนย์ข้อมูลสารสนเทศ.jpg")  #ยังไม่ลอง

# อาคารวิทยฐานะ
WAYPOINT_ACADEMIC_TOWER_VIDEO       = get_addon_path(ADDON_VIDEO_FOLDER, "To_Academic_Tower.mp4") 
ACADEMIC_TOWER_IMAGE_PATH           = get_addon_path(ADDON_IMAGE_FOLDER, "อาคารวิทยฐานะ.jpg") 

# งานบุคลากร (ตึกอำนวยการชั้น 2)
WAYPOINT_HR_VIDEO                   = get_addon_path(ADDON_VIDEO_FOLDER, "To_HR.mp4") 
HR_IMAGE_PATH                       = get_addon_path(ADDON_IMAGE_FOLDER, "งานบุคลากร.jpg") 

# งานการบัญชี / งานการวางแผนและงบประมาณ / งานความร่วมมือ (ตึกอำนวยการชั้น 2)
WAYPOINT_ACCOUNTING_PLANNING_COOP_VIDEO = get_addon_path(ADDON_VIDEO_FOLDER, "To_Accounting_Planning.mp4") 
ACCOUNTING_PLANNING_COOP_IMAGE_PATH = get_addon_path(ADDON_IMAGE_FOLDER, "งานการบัญชี_งานการวางแผนและงบประมาณ_งานความร่วมมือ.jpg") 

# รองผู้อำนวยการฝ่ายแผนงานและความร่วมมือ (ตึกอำนวยการชั้น 2)
WAYPOINT_PLANNING_COOP_VICE_DIRECTOR_VIDEO = get_addon_path(ADDON_VIDEO_FOLDER, "To_Deputy_Director_Planning.mp4") 
PLANNING_COOP_VICE_DIRECTOR_IMAGE_PATH = get_addon_path(ADDON_IMAGE_FOLDER, "รองผู้อำนวยการฝ่ายแผนงานและความร่วมมือ.jpg") #ยังไม่ลอง

# รองผู้อำนวยการฝ่ายพัฒนากิจการนักเรียน นักศึกษา (ตึกอำนวยการชั้น 2)
WAYPOINT_STUDENT_AFFAIRS_VICE_DIRECTOR_VIDEO = get_addon_path(ADDON_VIDEO_FOLDER, "To_Deputy_Director_Student_Affairs.mp4") 
STUDENT_AFFAIRS_VICE_DIRECTOR_IMAGE_PATH = get_addon_path(ADDON_IMAGE_FOLDER, "รองผู้อำนวยการฝ่ายพัฒนากิจการนักเรียน นักศึกษา.jpg") #ยังไม่ลอง

# รองผู้อำนวยการฝ่ายวิชาการ (ตึกอำนวยการชั้น 2)
WAYPOINT_ACADEMIC_VICE_DIRECTOR_VIDEO = get_addon_path(ADDON_VIDEO_FOLDER, "To_Deputy_Director_Academic_Affairs.mp4") 
ACADEMIC_VICE_DIRECTOR_IMAGE_PATH = get_addon_path(ADDON_IMAGE_FOLDER, "รองผู้อำนวยการฝ่ายวิชาการ.jpg") #ยังไม่ลอง

# รองผู้อำนวยการฝ่ายบริหารทรัพยากร (ตึกอำนวยการชั้น 2)
WAYPOINT_RESOURCE_VICE_DIRECTOR_VIDEO = get_addon_path(ADDON_VIDEO_FOLDER, "To_Deputy_Director_Resource_Management.mp4") 
RESOURCE_VICE_DIRECTOR_IMAGE_PATH = get_addon_path(ADDON_IMAGE_FOLDER, "รองผู้อำนวยการฝ่ายบริหารทรัพยากร.jpg")
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
        
    if datetime_label is not None:
        current_dt = datetime.now()
        
        # ปรับปีเป็นพุทธศักราช (ปี ค.ศ. + 543)
        buddhist_year = current_dt.year + 543
        
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
        # ในหน้าแผนก/ห้องย่อย (Guided Page) จะแสดง Survey และ Credit Bar
        should_show_survey = True
        should_show_credit = True
        
    elif frame_to_show == navigation_content_frame:
        # ในหน้าแผนผัง (Full Map) จะไม่แสดง Slide/Survey/Credit Bar
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


def load_home_video():
    try:
        VIDEO_PATH = "Tower/Start_Point/E1_1.mp4" 

        if os.path.exists(VIDEO_PATH) and VIDEO_PATH.endswith('.mp4'):
            # Store player to prevent garbage collection
            video_container.player = tkvideo(VIDEO_PATH, video_label, loop=1, size=(900, 500))
            video_container.player.play()
            print_status(f"Home Video loaded: {VIDEO_PATH}")
        else:
            video_label.pack_forget()
            ctk.CTkLabel(video_container, 
                         text=f"Video not found: {VIDEO_PATH}", 
                         text_color="red", 
                         font=("Kanit", 24)).pack(expand=True)
    except Exception as e:
        print_status(f"Error loading home video: {e}")


# -----------------------------------------------------------------
# --- NEW/MODIFIED: ฟังก์ชันควบคุมหน้าต่างนำทางแบบมีเส้นทาง (Guided Page) ---
# -----------------------------------------------------------------

def show_guided_page(title, header_bg_color, dept_image_path, waypoint_video, travel_key):
    """
    [UPDATED] ปรับปรุงสัดส่วน: ขยายวิดีโอแผนที่ให้ใหญ่ขึ้น และขยับรูปภาพด้านล่างลงมา
    """
    global DEPT_IMAGE_WIDTH, DEPT_IMAGE_HEIGHT
    
    for widget in electronics_content_frame.winfo_children():
        widget.destroy()

    distance_m, time_min = TRAVEL_INFO.get(travel_key, DEFAULT_TRAVEL)

    # --- ส่วนคอนเทนเนอร์หลัก ---
    content_container = ctk.CTkFrame(electronics_content_frame, fg_color="white")
    content_container.pack(side="top", fill="both", expand=True)

    # --- Header ---
    header_frame = ctk.CTkFrame(content_container, height=120, fg_color=header_bg_color)
    header_frame.pack(side="top", fill="x")
    
    ctk.CTkLabel(header_frame, text=title, font=("Kanit", 42, "bold"), text_color="white").pack(pady=(20, 10))
    
    # แสดงข้อมูลระยะทางและเวลา
    ctk.CTkLabel(content_container, 
                 text=f"📍 ระยะทาง: {distance_m} เมตร  |  ⏱️ เวลาเดินประมาณ: {time_min:.1f} นาที",
                 font=("Kanit", 24, "bold"), 
                 text_color="#006400").pack(pady=(10, 5))

    # --- 1. ส่วนวิดีโอนำทาง (ขยายเพิ่มขนาด) ---
    ctk.CTkLabel(content_container, text="🎬 วิดีโอนำทางไปยังจุดหมาย", font=("Kanit", 22, "bold"), text_color="#8000FF").pack()

    map_container_frame = ctk.CTkFrame(content_container, fg_color="white")
    map_container_frame.pack(pady=5, padx=20, fill="x") 

    video_label_guide = tk.Label(map_container_frame, bg="white", borderwidth=0)
    video_label_guide.pack(expand=True)
    
    if waypoint_video and os.path.exists(waypoint_video):
        try:
            # ขยายขนาดวิดีโอแผนที่ให้ใหญ่ขึ้นเป็น 900x500 เพื่อความชัดเจน
            map_container_frame.player = tkvideo(waypoint_video, video_label_guide, loop=1, size=(900, 500))
            map_container_frame.player.play()
        except Exception as e:
             print_status(f"Video Error: {e}")

    # --- 2. ส่วนรูปภาพสถานที่ (ขยับระยะห่างลงมา) ---
    # เพิ่ม pady ด้านบน (40) เพื่อขยับรูปภาพลงมาให้ไม่เบียดกับวิดีโอ
    ctk.CTkLabel(content_container, text="📸 ภาพประกอบสถานที่", font=("Kanit", 20, "bold"), text_color="#B418A9").pack(pady=(40, 0))

    try:
         if dept_image_path and os.path.exists(dept_image_path):
             dept_img = Image.open(dept_image_path)
             
             # คำนวณเพื่อรักษา Aspect Ratio ไม่ให้รูปยืด
             original_width, original_height = dept_img.size
             target_width = 750 # ปรับขนาดรูปให้พอดีกับวิดีโอที่ขยายขึ้น
             target_height = int((target_width / original_width) * original_height)
             
             # ควบคุมความสูงไม่ให้เกินหน้าจอ
             if target_height > 320:
                 target_height = 320
                 target_width = int((target_height / original_height) * original_width)

             dept_img_resized = dept_img.resize((target_width, target_height), Image.LANCZOS)
             dept_ctk_image = ctk.CTkImage(light_image=dept_img_resized, size=(target_width, target_height))
             ctk.CTkLabel(content_container, image=dept_ctk_image, text="").pack(pady=(10, 20))
    except Exception as e:
         print_status(f"Image Error: {e}")

    # --- ส่วนล่าง: ปุ่มกลับหน้าหลัก ---
    button_footer = ctk.CTkFrame(electronics_content_frame, fg_color="white")
    button_footer.pack(side="bottom", fill="x", pady=20)
    ctk.CTkButton(button_footer, text="❮ กลับสู่หน้าหลัก", command=go_to_main_screen, 
                  font=("Kanit", 28, "bold"), fg_color="#00C000", width=250, height=70, corner_radius=15).pack()

    voice_text = f"ระบบกำลังนำทางไปยัง {title} ระยะทาง {distance_m} เมตร ใช้เวลาเดินประมาณ {time_min} นาที"
    speak_thai(voice_text)
    show_frame(electronics_content_frame) 
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

# =============================================================================

# ***************************************************************
# ** UPDATED: ฟังก์ชัน Wrapper สำหรับแผนกต่างๆ (เดิม) **
# ***************************************************************

def show_electronics_page():
    BLUE_BACKGROUND = "#87CEFA" 
    show_guided_page(title="แผนกวิชาอิเล็กทรอนิกส์", header_bg_color=BLUE_BACKGROUND, 
                     dept_image_path=ELECTRONICS_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_ELECTRONICS_VIDEO, 
                     travel_key="ELECTRONICS")

def show_60_years_page():
    GOLD_BACKGROUND = "#FFD700" 
    show_guided_page(title="อาคาร 60 ปี ", header_bg_color=GOLD_BACKGROUND, 
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
    show_guided_page(title="แผนกวิชาเฟอร์นิเจอร์และเครื่องตกแต่งภายใน", header_bg_color=BROWN_BACKGROUND, 
                     dept_image_path=FURNITURE_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_FURNITURE_VIDEO,
                     travel_key="FURNITURE")
# [NEW] อาคาร 11 (เดิม)
def show_tuk11_page():
    PURPLE_BACKGROUND = "#8A2BE2" 
    show_guided_page(title="อาคาร 11", header_bg_color=PURPLE_BACKGROUND, 
                     dept_image_path=AIRLINE_DEPT_IMAGE_PATH, waypoint_video=WAYPOINT_AIRLINE_VIDEO,
                     travel_key="TUK11")
# [NEW] อาคาร 10
def show_tuk10_page():
    LIGHT_ORANGE_BACKGROUND = "#FFB6C1" # Light Coral
    show_guided_page(title="อาคาร 10", header_bg_color=LIGHT_ORANGE_BACKGROUND, 
                     dept_image_path=TUK10_IMAGE_PATH, waypoint_video=WAYPOINT_TUK10_VIDEO,
                     travel_key="TUK10")
                     
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
    show_guided_page(title="แผนกเทคโนโลยีคอมพิวเตอร์", header_bg_color=ORANGE_BACKGROUND,
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
# ** UPDATED: ฟังก์ชัน Wrapper สำหรับ Rooms (เดิม + ใหม่) **
# ***************************************************************
ROOM_BACKGROUND_COLOR = "#A9A9A9" 
POI_BACKGROUND_COLOR = "#808000" # Olive

# --- Rooms (เดิม) ---
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

def show_governance_page():
    show_guided_page(title="ห้องงานปกครอง", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=GOVERNANCE_IMAGE_PATH, waypoint_video=WAYPOINT_GOVERNANCE_VIDEO,
                     travel_key="GOVERNANCE")

def show_assessment_page():
    show_guided_page(title="ห้องงานวัดผล", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=ASSESSMENT_IMAGE_PATH, waypoint_video=WAYPOINT_ASSESSMENT_VIDEO,
                     travel_key="ASSESSMENT")
                     
# --- NEW: จุดบริการทั่วไป (POI) ---
def show_coop_shop_page():
    show_guided_page(title="ร้านค้าสวัสดิการ", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=COOP_SHOP_IMAGE_PATH, waypoint_video=WAYPOINT_COOP_SHOP_VIDEO,
                     travel_key="COOP_SHOP")

def show_canteen1_page():
    show_guided_page(title="โรงอาหาร 1", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=CANTEEN1_IMAGE_PATH, waypoint_video=WAYPOINT_CANTEEN1_VIDEO,
                     travel_key="CANTEEN1")

def show_canteen2_page():
    show_guided_page(title="โรงอาหาร 2", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=CANTEEN2_IMAGE_PATH, waypoint_video=WAYPOINT_CANTEEN2_VIDEO,
                     travel_key="CANTEEN2")

def show_building2_page():
    show_guided_page(title="อาคาร 2", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=BUILDING2_IMAGE_PATH, waypoint_video=WAYPOINT_BUILDING2_VIDEO,
                     travel_key="BUILDING2")

def show_building3_page():
    show_guided_page(title="อาคาร 3", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=BUILDING3_IMAGE_PATH, waypoint_video=WAYPOINT_BUILDING3_VIDEO,
                     travel_key="BUILDING3")

def show_library_page():
    show_guided_page(title="ห้องสมุด ", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=LIBRARY_IMAGE_PATH, waypoint_video=WAYPOINT_LIBRARY_VIDEO,
                     travel_key="LIBRARY")

def show_gym_page():
    show_guided_page(title="โรงยิม", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=GYM_IMAGE_PATH, waypoint_video=WAYPOINT_GYM_VIDEO,
                     travel_key="GYM")

def show_futsal_page():
    show_guided_page(title="สนามฟุตซอล", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=FUTSAL_IMAGE_PATH, waypoint_video=WAYPOINT_FUTSAL_VIDEO,
                     travel_key="FUTSAL")

def show_meeting_room_page():
    show_guided_page(title="ห้องประชุม", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=MEETING_ROOM_IMAGE_PATH, waypoint_video=WAYPOINT_MEETING_ROOM_VIDEO,
                     travel_key="MEETING_ROOM")

def show_central_procurement_page():
    show_guided_page(title="ห้องพัสดุกลาง", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=CENTRAL_PROCUREMENT_IMAGE_PATH, waypoint_video=WAYPOINT_CENTRAL_PROCUREMENT_VIDEO,
                     travel_key="CENTRAL_PROCUREMENT")

def show_parking_page():
    show_guided_page(title="โรงจอดรถ", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=PARKING_IMAGE_PATH, waypoint_video=WAYPOINT_PARKING_VIDEO,
                     travel_key="PARKING")

def show_football_page():
    show_guided_page(title="สนามฟุตบอล", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=FOOTBALL_IMAGE_PATH, waypoint_video=WAYPOINT_FOOTBALL_VIDEO,
                     travel_key="FOOTBALL")

def show_tennis_page():
    show_guided_page(title="สนามเทนนิส", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=TENNIS_IMAGE_PATH, waypoint_video=WAYPOINT_TENNIS_VIDEO,
                     travel_key="TENNIS")

def show_fixit_page():
    show_guided_page(title="ศูนย์ซ่อมสร้างชุมชน และ Fixit center", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=FIXIT_IMAGE_PATH, waypoint_video=WAYPOINT_FIXIT_VIDEO,
                     travel_key="FIXIT")

def show_general_admin_page():
    show_guided_page(title="งานบริหารทั่วไป", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=GENERAL_ADMIN_IMAGE_PATH, waypoint_video=WAYPOINT_GENERAL_ADMIN_VIDEO,
                     travel_key="GENERAL_ADMIN")

def show_info_data_page():
    show_guided_page(title="งานศูนย์ข้อมูลสารสนเทศและงานส่งเสริมผลิตผลการและประกอบธุรกิจ", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=INFO_DATA_IMAGE_PATH, waypoint_video=WAYPOINT_INFO_DATA_VIDEO,
                     travel_key="INFO_DATA")

def show_academic_tower_page():
    show_guided_page(title="อาคารวิทยฐานะ", header_bg_color=POI_BACKGROUND_COLOR, 
                     dept_image_path=ACADEMIC_TOWER_IMAGE_PATH, waypoint_video=WAYPOINT_ACADEMIC_TOWER_VIDEO,
                     travel_key="ACADEMIC_TOWER")

def show_hr_page():
    show_guided_page(title="งานบุคลากร (ตึกอำนวยการชั้น 2)", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=HR_IMAGE_PATH, waypoint_video=WAYPOINT_HR_VIDEO,
                     travel_key="HR")

def show_accounting_planning_coop_page():
    show_guided_page(title="งานการบัญชี / งานการวางแผนและงบประมาณ / งานความร่วมมือ (ตึกอำนวยการชั้น 2)", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=ACCOUNTING_PLANNING_COOP_IMAGE_PATH, waypoint_video=WAYPOINT_ACCOUNTING_PLANNING_COOP_VIDEO,
                     travel_key="ACCOUNTING_PLANNING_COOP")

def show_planning_coop_vice_director_page():
    show_guided_page(title="รองผู้อำนวยการฝ่ายแผนงานและความร่วมมือ (ตึกอำนวยการชั้น 2)", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=PLANNING_COOP_VICE_DIRECTOR_IMAGE_PATH, waypoint_video=WAYPOINT_PLANNING_COOP_VICE_DIRECTOR_VIDEO,
                     travel_key="PLANNING_COOP_VICE_DIRECTOR")

def show_student_affairs_vice_director_page():
    show_guided_page(title="รองผู้อำนวยการฝ่ายพัฒนากิจการนักเรียน นักศึกษา (ตึกอำนวยการชั้น 2)", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=STUDENT_AFFAIRS_VICE_DIRECTOR_IMAGE_PATH, waypoint_video=WAYPOINT_STUDENT_AFFAIRS_VICE_DIRECTOR_VIDEO,
                     travel_key="STUDENT_AFFAIRS_VICE_DIRECTOR")

def show_academic_vice_director_page():
    show_guided_page(title="รองผู้อำนวยการฝ่ายวิชาการ (ตึกอำนวยการชั้น 2)", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=ACADEMIC_VICE_DIRECTOR_IMAGE_PATH, waypoint_video=WAYPOINT_ACADEMIC_VICE_DIRECTOR_VIDEO,
                     travel_key="ACADEMIC_VICE_DIRECTOR")

def show_resource_vice_director_page():
    show_guided_page(title="รองผู้อำนวยการฝ่ายบริหารทรัพยากร (ตึกอำนวยการชั้น 2)", header_bg_color=ROOM_BACKGROUND_COLOR, 
                     dept_image_path=RESOURCE_VICE_DIRECTOR_IMAGE_PATH, waypoint_video=WAYPOINT_RESOURCE_VICE_DIRECTOR_VIDEO,
                     travel_key="RESOURCE_VICE_DIRECTOR")

# ***************************************************************
# ===============================================================
# ** Interactive Map: Popup & Click Handling (Full 1-31) **
# ===============================================================

 # ฟังก์ชันปุ่มนำทาง (เรียกใช้ฟังก์ชันเดิมในระบบ)
 # 
 # 
current_popup = None  # ตัวแปร Global สำหรับเก็บ Popup ที่กำลังแสดงอยู่

dcurrent_popup = None  # ตัวแปร Global สำหรับเก็บเฟรมปัจจุบัน

current_popup = None  # ตัวแปร Global สำหรับเก็บเฟรมปัจจุบัน

current_popup = None  # ตัวแปร Global สำหรับเก็บเฟรมปัจจุบัน

current_popup = None
popup_timer_id = None

# --- ตัวแปร Global สำหรับจัดการ Popup และเวลานับถอยหลัง ---
# --- ตัวแปร Global สำหรับจัดการ Popup และเวลานับถอยหลัง ---
current_popup = None
popup_timer_id = None

# --- 1. ปรับปรุงฟังก์ชันปิด (ให้รองรับการเช็ค widget เพื่อไม่ให้ปิดตอนกำลังลาก) ---
# --- 1. ปรับปรุงฟังก์ชันปิด (ให้รองรับการเช็ค widget เพื่อไม่ให้ปิดตอนกำลังลาก) ---
def close_building_popup(event=None):
    """ฟังก์ชันสำหรับปิด Popup และยกเลิกเวลานับถอยหลัง"""
    global current_popup, popup_timer_id
    if current_popup is not None:
        try:
            # ถ้าเป็นการคลิกจาก Event (เช่น คลิกพื้นที่ว่าง)
            if event and hasattr(event, "widget"):
                # ตรวจสอบว่า widget ที่คลิกเป็นส่วนหนึ่งของ popup หรือไม่
                # ถ้าคลิกโดนตัว popup หรือลูกๆ ของมัน ไม่ต้องปิด (เพื่อให้ลากได้)
                clicked_w = event.widget
                if clicked_w == current_popup or str(clicked_w).startswith(str(current_popup)):
                    return
                
            current_popup.destroy()
            current_popup = None
            if popup_timer_id is not None:
                root.after_cancel(popup_timer_id)
                popup_timer_id = None
        except:
            pass

# --- 2. ฟังก์ชันช่วยสำหรับการลาก (Drag and Drop) ---
def start_popup_drag(event):
    current_popup._drag_start_x = event.x
    current_popup._drag_start_y = event.y

def do_popup_drag(event):
    x = current_popup.winfo_x() - current_popup._drag_start_x + event.x
    y = current_popup.winfo_y() - current_popup._drag_start_y + event.y
    current_popup.place(x=x, y=y)

# --- 3. ฟังก์ชันสร้าง Popup แบบขยายขนาด, มีปุ่มปิดสีแดง และลากได้ ---
def show_building_popup(name, travel_key, x, y):
    """ฟังก์ชันสร้างเฟรมข้อมูลอาคาร (ลากได้ + ปุ่มปิดวงกลมสีแดงชัดเจน)"""
    global current_popup, popup_timer_id
    
    close_building_popup() 

    popup_width = 380 
    # ตั้งค่าเริ่มต้นตำแหน่งที่แสดง (แสดงใกล้ๆ จุดที่คลิกหรือตำแหน่งที่เหมาะสม)
    x_pos = 650 
    y_pos = 1000 

    popup = ctk.CTkFrame(home_content_frame, corner_radius=25, fg_color="white", 
                         border_width=4, border_color="#8000FF", width=popup_width)
    popup.place(x=x_pos, y=y_pos)
    current_popup = popup 

    # --- ทำให้เฟรมลากได้ ---
    popup.bind("<Button-1>", start_popup_drag)
    popup.bind("<B1-Motion>", do_popup_drag)

    # --- ปุ่มกากบาทปิด (วงกลมสีแดงเด่นชัด) ---
    btn_close = ctk.CTkButton(popup, 
                              text="✕", 
                              width=45, 
                              height=45, 
                              corner_radius=22, 
                              fg_color="#FF0000", 
                              text_color="white", 
                              hover_color="#CC0000", 
                              font=("Arial", 22, "bold"),
                              command=close_building_popup)
    btn_close.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")

    # --- ส่วนแสดงชื่อสถานที่ ---
    ctk_name = ctk.CTkLabel(popup, text=name, font=("Kanit", 22, "bold"), 
                            text_color="#8000FF", wraplength=300)
    ctk_name.pack(pady=(65, 10), padx=30)
    # ทำให้ Label ลากได้ด้วย
    ctk_name.bind("<Button-1>", start_popup_drag)
    ctk_name.bind("<B1-Motion>", do_popup_drag)

    # --- ส่วนข้อมูลระยะทางและปุ่มนำทาง ---
    if travel_key == "REGISTRATION":
        ctk.CTkLabel(popup, text="📍 คุณอยู่ที่นี่\n(จุดตั้งตู้ HTC Smart Hub)", 
                     font=("Kanit", 18), text_color="#006400").pack(pady=20, padx=30)
    else:
        distance_m, time_min = TRAVEL_INFO.get(travel_key, DEFAULT_TRAVEL)
        info_text = f"📏 ระยะทาง: {distance_m} เมตร\n⏱️ เวลาเดิน: {time_min} นาที"
        
        info_label = ctk.CTkLabel(popup, text=info_text, font=("Kanit", 18), text_color="#333333")
        info_label.pack(pady=10, padx=30)
        info_label.bind("<Button-1>", start_popup_drag)
        info_label.bind("<B1-Motion>", do_popup_drag)
        

        def navigate_and_close():
            # ดึงฟังก์ชันนำทางจาก Mapping เดิมที่คุณมี
            nav_func = {
                "ELECTRIC": show_electrical_page, "ARCHITECT": show_arch_survey_page,
                "FACTORY": show_factory_it_page, "RAIL": show_rail_page,
                "AUTO": show_technic_mac_page, "WELDING": show_welding_page,
                "MECHATRONICS": show_mechatronics_energy_page, "PETROLEUM": show_petroleum_page,
                "BASICTECH": show_basic_tech_page, "AIRCOND": show_air_condi_page,
                "ELECTRONICS": show_electronics_page, "FURNITURE": show_interior_decoration_page,
                "AIRLINE": show_airline_logistics_page, "COMPUTER_TECH": show_computer_tech_page,
                "COOP_SHOP": show_coop_shop_page, "CANTEEN2": show_canteen2_page,
                "CANTEEN1": show_canteen1_page, "BUILDING2": show_building2_page,
                "BUILDING3": show_building3_page, "LIBRARY": show_library_page,
                "GYM": show_gym_page, "SOUTHERN_CENTER": show_southern_center_page,
                "GENERAL_ADMIN": show_general_admin_page, "FUTSAL": show_futsal_page,
                "MEETING_ROOM": show_meeting_room_page, "ACADEMIC_TOWER": show_academic_tower_page,
                "PARKING": show_parking_page, "FOOTBALL": show_football_page,
                "TENNIS": show_tennis_page, "FIXIT": show_fixit_page
            }.get(travel_key)
            
            close_building_popup()
            if nav_func: nav_func()

      # ปรับขนาดปุ่มให้น้อยลง (จากเดิม width 280 -> 240, height 55 -> 45)
        btn_nav = ctk.CTkButton(popup, 
                                text="🚀 เริ่มการนำทาง", 
                                height=45,          # ลดความสูงปุ่ม
                                width=210,          # ลดความกว้างปุ่ม
                                fg_color="#8000FF", 
                                hover_color="#5B0094",
                                font=("Kanit", 18, "bold"), # ลดขนาดฟอนต์ลงเล็กน้อยจาก 20 -> 18
                                corner_radius=12,   # ปรับความโค้งให้รับกับขนาดปุ่มที่เล็กลง
                                command=navigate_and_close)
        
        # ปรับ pady (ระยะห่าง) ให้ปุ่มอยู่ตำแหน่งที่พอดีกับขอบล่างของเฟรม
        btn_nav.pack(side="bottom", pady=(0, 35))
    # รีเซ็ต Timer ทุกครั้งที่ขยับหรือคลิก (ถ้าต้องการให้มันเปิดค้างไว้นานขึ้น)
    popup_timer_id = root.after(60000, close_building_popup) # เพิ่มเป็น 1 นาที

# --- แก้ไขพิกัดและชื่อสถานที่ให้ตรงตามเมนูใหม่ ---
def on_map_click(event):
    x, y = event.x, event.y
    r = 25 

    # อ้างอิงชื่อตามไฟล์ menu.jpg ที่คุณส่งมา
    if abs(x - 428) < r and abs(y - 364) < r: 
        show_building_popup("อาคารอำนวยการ", "REGISTRATION", x, y) # 1
    elif abs(x - 648) < r and abs(y - 258) < r: 
        show_building_popup("แผนกวิชาช่างไฟฟ้า / ก่อสร้าง / โยธา", "ELECTRIC", x, y) # 2
    elif abs(x - 647) < r and abs(y - 426) < r: 
        show_building_popup("แผนกวิชาช่างสำรวจ / สถาปัตยกรรม", "ARCHITECT", x, y) # 3
    elif abs(x - 647) < r and abs(y - 125) < r: 
        show_building_popup("แผนกวิชาช่างกลโรงงาน / เทคโนโลยีสารสนเทศ", "FACTORY", x, y) # 4
    elif abs(x - 571) < r and abs(y - 130) < r: 
        show_building_popup("แผนกเทคนิคควบคุมและซ่อมบำรุงขนส่งทางราง", "RAIL", x, y) # 5
    elif abs(x - 586) < r and abs(y - 56) < r: 
        show_building_popup("แผนกวิชาช่างยนต์", "AUTO", x, y) # 6
    elif abs(x - 513) < r and abs(y - 174) < r: 
        show_building_popup("แผนกวิชาช่างเชื่อมโลหะ", "WELDING", x, y) # 7
    elif abs(x - 518) < r and abs(y - 340) < r: 
        show_building_popup("แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์ / เทคนิคพลังงาน", "MECHATRONICS", x, y) # 8
    elif abs(x - 437) < r and abs(y - 55) < r: 
        show_building_popup("แผนกวิชาเทคโนโลยีเครื่องมือวัดและควบคุมปิโตรเลียม", "PETROLEUM", x, y) # 9
    elif abs(x - 574) < r and abs(y - 246) < r: 
        show_building_popup("แผนกวิชาช่างเทคนิคพื้นฐาน", "BASICTECH", x, y) # 10
    elif abs(x - 551) < r and abs(y - 313) < r: 
        show_building_popup("แผนกวิชาเครื่องทำความเย็นและปรับอากาศ", "AIRCOND", x, y) # 11
    elif abs(x - 650) < r and abs(y - 366) < r: 
        show_building_popup("แผนกวิชาช่างอิเล็กทรอนิกส์", "ELECTRONICS", x, y) # 12
    elif abs(x - 573) < r and abs(y - 193) < r: 
        show_building_popup("แผนกวิชาเฟอร์นิเจอร์และตกแต่งภายใน", "FURNITURE", x, y) # 13
    elif abs(x - 580) < r and abs(y - 349) < r: 
        show_building_popup("แผนกวิชาช่างโลจิสติกส์และซัพพลายเชน / ธุรกิจการบิน", "AIRLINE", x, y) # 14
    elif abs(x - 535) < r and abs(y - 426) < r: 
        show_building_popup("แผนกวิชาเทคโนโลยีคอมพิวเตอร์", "COMPUTER_TECH", x, y) # 15
    elif abs(x - 649) < r and abs(y - 461) < r: 
        show_building_popup("ร้านค้าสวัสดิการ", "COOP_SHOP", x, y) # 16
    elif abs(x - 450) < r and abs(y - 124) < r: 
        show_building_popup("โรงอาหาร 2", "CANTEEN2", x, y) # 17
    elif abs(x - 353) < r and abs(y - 171) < r: 
        show_building_popup("โรงอาหาร 1", "CANTEEN1", x, y) # 18
    elif abs(x - 490) < r and abs(y - 358) < r: 
        show_building_popup("อาคาร 2 อาคารเรียน", "BUILDING2", x, y) # 19
    elif abs(x - 549) < r and abs(y - 383) < r: 
        show_building_popup("อาคาร 3 อาคารเรียน", "BUILDING3", x, y) # 20
    elif abs(x - 443) < r and abs(y - 292) < r: 
        show_building_popup("ห้องสมุด", "LIBRARY", x, y) # 21
    elif abs(x - 318) < r and abs(y - 212) < r: 
        show_building_popup("โรงยิม", "GYM", x, y) # 22
    elif abs(x - 338) < r and abs(y - 102) < r: 
        show_building_popup("ศูนย์ส่งเสริมและพัฒนาอาชีวะ", "SOUTHERN_CENTER", x, y) # 23
    elif abs(x - 449) < r and abs(y - 403) < r: 
        show_building_popup("งานบริหารทั่วไป", "GENERAL_ADMIN", x, y) # 24
    elif abs(x - 454) < r and abs(y - 208) < r: 
        show_building_popup("สนามฟุตซอล", "25", x, y) # 25 (ตรวจสอบชื่อใน menu.jpg อีกครั้ง)
    elif abs(x - 398) < r and abs(y - 200) < r: 
        show_building_popup("หอประชุม", "MEETING_ROOM", x, y) # 26
    elif abs(x - 492) < r and abs(y - 288) < r: 
        show_building_popup("อาคารวิทยฐานะ", "ACADEMIC_TOWER", x, y) # 27
    elif abs(x - 336) < r and abs(y - 421) < r: 
        show_building_popup("โรงจอดรถ", "PARKING", x, y) # 28
    elif abs(x - 291) < r and abs(y - 336) < r: 
        show_building_popup("สนามฟุตบอล", "FOOTBALL", x, y) # 29
    elif abs(x - 388) < r and abs(y - 51) < r: 
        show_building_popup("สนามเทนนิส", "TENNIS", x, y) # 30
    elif abs(x - 616) < r and abs(y - 481) < r: 
        show_building_popup("ศูนย์ซ่อมสร้างชุมชนและ FIXIT CENTER", "FIXIT", x, y) # 31

# ผูกเหตุการณ์คลิกพื้นที่ว่างในหน้าหลักเพื่อปิด Popup
home_content_frame.bind("<Button-1>", close_building_popup, add="+")
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
# ** Drag & Click Logic (ใช้สำหรับ Image Slide) **
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
    # แผนกวิชา (เดิม)
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
    "สถาปัตยกรรม_สำรวจ.jpg": show_arch_survey_page, 
    "สารสนเทศ_กลโรงงาน.jpg": show_factory_it_page, 
    "แมคคา_พลังงาน.jpg": show_mechatronics_energy_page, 
    "ตึก11.jpg": show_tuk11_page, 
    "อาคาร10.jpg": show_tuk10_page, 
    
    # ห้อง/งาน (ใช้สำหรับ Voice Search)
    "ศูนย์ประสานงานบัณฑิตศึกษา.jpg": show_graduate_page,
    "ห้องงานอาชีวศึกษาระบบทวิภาคี.jpg": show_dual_vocational_page,
    "งานแนะแนวและการจัดหางาน.jpg": show_counseling_page,
    "ห้องงานพัฒนาหลักสูตร.jpg": show_curriculum_page,
    "งานปกครองและงานครูที่ปรึกษา.jpg": show_disciplinary_page,
    "งานวัดผลและประเมินผล.jpg": show_evaluation_page,
    "กิจกรรมนักเรียน.jpg": show_event_page,
    "งานการเงิน.jpg": show_finance_page,
    "ศูนย์ประสานงานผลิตและพัฒนากำลังคน.jpg": show_production_page,
    "ประชาสัมพันธ์.jpg": show_public_relations_page,
    "งานทะเบียน.jpg": show_registration_page,
    
    
    # NEW: จุดบริการเพิ่มเติม (ตรวจสอบว่าชื่อไฟล์ตรงกับในโฟลเดอร์ room)
    "ร้านค้าสวัสดิการ.jpg": show_coop_shop_page, 
    "โรงอาหาร1.jpg": show_canteen1_page,
    "โรงอาหาร2.jpg": show_canteen2_page,
    "อาคาร2.jpg": show_building2_page,
    "อาคาร3.jpg": show_building3_page,
    "ห้องสมุด.jpg": show_library_page,
    "โรงยิม.jpg": show_gym_page,
    "สนามฟุตซอล.jpg": show_futsal_page,
    "ห้องประชุม.jpg": show_meeting_room_page, 
    "ห้องพัสดุกลาง.jpg": show_central_procurement_page, 
    "โรงจอดรถ.jpg": show_parking_page,
    "สนามฟุตบอล.jpg": show_football_page,
    "สนามเทนนิส.jpg": show_tennis_page,
    "ศูนย์ซ่อมสร้างชุมชนและ Fixit center.jpg": show_fixit_page,
    "งานบริหารทั่วไป.jpg": show_general_admin_page,
    "งานศูนย์ข้อมูลสารสนเทศและงานส่งเสริมผลิตผลการ.jpg": show_info_data_page,
    "อาคารวิทยฐานะ.jpg": show_academic_tower_page,
    "งานบุคลากร.jpg": show_hr_page,
    "งานการบัญชี_งานการวางแผนและงบประมาณ_งานความร่วมมือ.jpg": show_accounting_planning_coop_page,
    "รองผู้อำนวยการฝ่ายแผนงานและความร่วมมือ.jpg": show_planning_coop_vice_director_page,
    "รองผู้อำนวยการฝ่ายพัฒนากิจการนักเรียน นักศึกษา.jpg": show_student_affairs_vice_director_page, 
    "รองผู้อำนวยการฝ่ายวิชาการ.jpg": show_academic_vice_director_page,
    "รองผู้อำนวยการฝ่ายบริหารทรัพยากร.jpg": show_resource_vice_director_page,
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

# ***************************************************************
# ** [OPTIMIZED] ฟังก์ชันสำหรับรูปภาพสไลด์ (Performance Tuned) **
# ***************************************************************
def load_slide_images():
    """
    [OPTIMIZED] โหลดรูปภาพเรียงตามชื่อไฟล์ (Sort) และใช้โหมด Resize แบบเร็ว (BILINEAR)
    เหมาะสำหรับ Raspberry Pi 4
    """
    global slide_images, slide_photo_images, SLIDE_FRAME_WIDTH, SLIDE_FRAME_COLOR, IMAGE_SLIDE_HEIGHT
    slide_images = []
    slide_photo_images = []
    
    folders_to_load = [IMAGE_SLIDE_FOLDER] 
    
    # NOTE: รายการไฟล์ที่ได้รับอนุญาตให้แสดงบนแถบเลื่อน (เฉพาะแผนกวิชาเดิม + อาคาร 10/11)
    allowed_dept_files = [
        "60 ปี.jpg", "ก่อสร้าง.jpg", "ช่างไฟฟ้า.jpg", "อิเล็กทรอนิกส์.jpg", 
        "ปิโตรเลียม.jpg", "ระบบราง.jpg", "เทคนิคพื้นฐาน.jpg", "ช่างเชื่อมโลหะ.jpg", 
        "โยธา.jpg", "ตกแต่งภายใน.jpg", "ตึกส้ม.jpg", "ทำความเย็น.jpg", 
        "ช่างยนต์.jpg", "สถาปัตยกรรม_สำรวจ.jpg", "สารสนเทศ_กลโรงงาน.jpg", 
        "แมคคา_พลังงาน.jpg", "ตึก11.jpg", "อาคาร10.jpg" # [NEW] เพิ่มอาคาร 10
    ]
    
    image_list_map = {} 
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')

    for folder in folders_to_load:
        if not os.path.exists(folder):
            print_status(f"--- [IMAGE SLIDE ERROR]: ไม่พบโฟลเดอร์: {folder} ---")
            continue
            
        image_files = [f for f in os.listdir(folder) if f.lower().endswith(valid_extensions)]
        
        # 1. เรียงตามชื่อไฟล์ (A-Z) เพื่อให้ลำดับคงที่และวนลูปถูกต้อง
        image_files.sort() 
        
        for filename in image_files:
            if filename not in allowed_dept_files:
                continue # กรองเฉพาะไฟล์ที่อยู่ใน allowed_dept_files เท่านั้น
            
            if filename in image_list_map: continue 
            
            try:
                filepath = os.path.join(folder, filename)
                img = Image.open(filepath)
                original_width, original_height = img.size
                
                # Resize logic
                target_image_height = IMAGE_SLIDE_HEIGHT - (SLIDE_FRAME_WIDTH * 2)
                
                # 2. OPTIMIZATION: ใช้ Image.BILINEAR แทน LANCZOS (เร็วกว่า 3 เท่า)
                if original_height > target_image_height:
                    ratio = target_image_height / original_height
                    new_width = int(original_width * ratio)
                    img = img.resize((new_width, target_image_height), Image.BILINEAR)
                else:
                    if original_height < target_image_height:
                        target_image_height = original_height 
                    target_image_width_limit = 900 - (SLIDE_FRAME_WIDTH * 2) 
                    if img.width > target_image_width_limit:
                        ratio = target_image_width_limit / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((target_image_width_limit, new_height), Image.BILINEAR)
                
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
    """เคลื่อนย้ายรูปภาพสไลด์ไปทางซ้าย (Reduced FPS for Performance)"""
    global active_slide_items, image_slide_canvas
    
    try:
        if not image_slide_canvas.winfo_exists(): return
    except:
        return
        
    # 3. OPTIMIZATION: เพิ่มระยะเคลื่อนที่ต่อครั้ง (จาก -3 เป็น -6)
    move_distance = -6 
    
    for item in active_slide_items:
        image_slide_canvas.move(item['id'], move_distance, 0)
        item['right_edge'] += move_distance
    
    if active_slide_items and active_slide_items[0]['right_edge'] < 0:
        item_to_remove = active_slide_items.pop(0)
        image_slide_canvas.delete(item_to_remove['id'])
    
    if active_slide_items and active_slide_items[-1]['right_edge'] < 1080 + SLIDE_GAP:
        place_next_slide()
    
    # 4. OPTIMIZATION: เพิ่มเวลา Delay เป็น 50ms (20 FPS) จากเดิม 25ms
    root.after(50, animate_image_slide)

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
# ** Real-Time Date/Time Clock Placeholder (Right of Top Bar) **
# ***************************************************************
datetime_label = ctk.CTkLabel(
    top_bar, 
    text="กำลังโหลดเวลา...", 
    font=("Kanit", 20, "bold"), 
    text_color="white", 
    justify="right"
)
# วางให้อยู่มุมขวาบนของ top_bar
datetime_label.pack(side="right", padx=20, pady=(15, 0))


# ***************************************************************
# ** ส่วนของ UI ด้านล่าง (Fixed Bottom Widgets - ต้อง Pack ก่อนส่วนกลาง) **
# *******************************************************************

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

# ***************************************************************
# ** Fixed: Credit Text Marquee (Moving Text) **
# ***************************************************************

# --- 3. ข้อความเลื่อนด้านล่าง (Text Marquee) ---
credit_frame = ctk.CTkFrame(root, height=40, fg_color="#5B0094", corner_radius=0)
credit_frame.pack(side="bottom", fill="x")

# Create the label
credit_text_content = "จัดทำโดยนักศึกษาเทคโนโลยีคอมพิวเตอร์"
credit_label = ctk.CTkLabel(
    credit_frame, 
    text=credit_text_content, 
    font=("Kanit", 24, "bold"), 
    text_color="white"
)

# Initial placement (Starts off-screen to the right)
credit_label.place(x=1080, y=5) 

def animate_credit_marquee():
    """Function to move text from Right to Left loop"""
    try:
        # Check if label exists to prevent errors on close
        if not credit_label.winfo_exists(): return
    except: return
    
    # Settings
    speed = 2  # Higher number = Faster
    screen_width = root.winfo_width() # Get current screen width
    text_width = credit_label.winfo_reqwidth() # Get text width
    current_x = credit_label.winfo_x()
    
    # Calculate new position
    new_x = current_x - speed
    
    # If text moves completely off the left side, reset to right side
    if new_x < -(text_width + 50):
        new_x = screen_width
        
    # Apply new position
    credit_label.place(x=new_x, y=5) # y=5 centers it in the 40px frame
    
    # Loop every 20ms
    root.after(20, animate_credit_marquee)

# Start the animation immediately
animate_credit_marquee()

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
# ** IMPROVED: Speech Recognition (Faster & More Sensitive) **
# ***************************************************************

# Global variable to control Aura color
mic_status = "IDLE" # Options: IDLE, CALIBRATING, LISTENING, PROCESSING

# NOTE: ลบฟังก์ชัน Text-to-Speech ออกทั้งหมดตามคำขอ

def listen_for_speech():
    """ฟังก์ชันรับเสียงที่ปรับปรุงให้ทำงานไวขึ้นและแม่นยำขึ้น"""
    global is_listening, mic_status
    r = sr.Recognizer()
    LANGUAGE = "th-TH" 

    is_listening = True 
    mic_status = "CALIBRATING" # Update status for animation
    print_status("--- [MIC]: Calibrating noise... (Wait) ---")
    
    try: 
        with sr.Microphone() as source:
            # 1. FASTER CALIBRATION: ลดเวลาปรับเสียงรบกวนเหลือ 0.1 วินาที (จากเดิม 0.8)
            r.adjust_for_ambient_noise(source, duration=0.1) 
            
            # 2. SET STATUS TO LISTENING: เปลี่ยนสี Aura เป็นเขียวทันทีที่พร้อม
            mic_status = "LISTENING"
            print_status("--- [MIC]: พูดได้เลย! (Listening...) ---")
            
            try:
                # 3. OPTIMIZED LISTENING:
                # timeout=5: ถ้าไม่พูดภายใน 5 วิ ให้ตัดจบ (ไม่ต้องรอนาน)
                # phrase_time_limit=5: ให้เวลาพูดคำสั่งสั้นๆ ไม่เกิน 5 วิ
                audio = r.listen(source, timeout=5, phrase_time_limit=5) 
                
                mic_status = "PROCESSING" # เปลี่ยนสถานะเป็นกำลังประมวลผล
                print_status("--- [MIC]: กำลังประมวลผล... ---")
                
                text = r.recognize_google(audio, language=LANGUAGE) 
                
                print(f"\n*** [RESULT]: '{text}' ***\n")
                
                text_lower = text.lower()
                
                # --- COMMAND MAPPING ---
                
                # 0. ตรวจสอบคำสั่งกลับหน้าหลัก
                if any(k in text_lower for k in KEYWORDS_HOME):
                    print_status(f"--- [SYSTEM]: ตรวจพบคำสั่งกลับหน้าหลัก ---")
                    root.after(0, go_to_main_screen)
                    return

                # --- แผนกวิชา (เดิม) ---
                if any(k in text_lower for k in KEYWORDS_ELECTRONICS): root.after(0, show_electronics_page); return
                if any(k in text_lower for k in KEYWORDS_CONSTRUCTION): root.after(0, show_construction_page); return 
                if any(k in text_lower for k in KEYWORDS_60YEARS): root.after(0, show_60_years_page); return
                if any(k in text_lower for k in KEYWORDS_TUK11): root.after(0, show_tuk11_page); return 
                if any(k in text_lower for k in KEYWORDS_TUK10): root.after(0, show_tuk10_page); return 
                if any(k in text_lower for k in KEYWORDS_ELECTRIC): root.after(0, show_electrical_page); return
                if any(k in text_lower for k in KEYWORDS_FURNITURE): root.after(0, show_interior_decoration_page); return
                if any(k in text_lower for k in KEYWORDS_PETROLEUM): root.after(0, show_petroleum_page); return
                if any(k in text_lower for k in KEYWORDS_RAIL): root.after(0, show_rail_page); return
                if any(k in text_lower for k in KEYWORDS_BASICTECH): root.after(0, show_basic_tech_page); return
                if any(k in text_lower for k in KEYWORDS_ARCHITECT + KEYWORDS_SURVEY): root.after(0, show_arch_survey_page); return
                if any(k in text_lower for k in KEYWORDS_FACTORY + KEYWORDS_IT): root.after(0, show_factory_it_page); return
                if any(k in text_lower for k in KEYWORDS_MECHATRONICS + KEYWORDS_ENERGY): root.after(0, show_mechatronics_energy_page); return
                if any(k in text_lower for k in KEYWORDS_AIRLINE + KEYWORDS_LOGISTICS): root.after(0, show_airline_logistics_page); return 
                if any(k in text_lower for k in KEYWORDS_AUTO): root.after(0, show_technic_mac_page); return
                if any(k in text_lower for k in KEYWORDS_WELDING): root.after(0, show_welding_page); return
                if any(k in text_lower for k in KEYWORDS_AIRCOND): root.after(0, show_air_condi_page); return
                if any(k in text_lower for k in KEYWORDS_CIVIL): root.after(0, show_civil_page); return
                if any(k in text_lower for k in KEYWORDS_COMPUTER_TECH): root.after(0, show_computer_tech_page); return
                if any(k in text_lower for k in KEYWORDS_BASIC_SUBJECTS): root.after(0, show_basic_subjects_page); return
                if any(k in text_lower for k in KEYWORDS_SOUTHERN_CENTER): root.after(0, show_southern_center_page); return
                
                # --- ห้อง/งาน (เดิม) ---
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
                if any(k in text_lower for k in KEYWORDS_GOVERNANCE): root.after(0, show_governance_page); return
                if any(k in text_lower for k in KEYWORDS_ASSESSMENT): root.after(0, show_assessment_page); return
                
                # --- NEW: จุดบริการและงานอำนวยการเพิ่มเติม ---
                if any(k in text_lower for k in KEYWORDS_COOP_SHOP): root.after(0, show_coop_shop_page); return
                if any(k in text_lower for k in KEYWORDS_CANTEEN1): root.after(0, show_canteen1_page); return
                if any(k in text_lower for k in KEYWORDS_CANTEEN2): root.after(0, show_canteen2_page); return
                if any(k in text_lower for k in KEYWORDS_BUILDING2): root.after(0, show_building2_page); return
                if any(k in text_lower for k in KEYWORDS_BUILDING3): root.after(0, show_building3_page); return
                if any(k in text_lower for k in KEYWORDS_LIBRARY): root.after(0, show_library_page); return
                if any(k in text_lower for k in KEYWORDS_GYM): root.after(0, show_gym_page); return
                if any(k in text_lower for k in KEYWORDS_FUTSAL): root.after(0, show_futsal_page); return
                if any(k in text_lower for k in KEYWORDS_MEETING_ROOM): root.after(0, show_meeting_room_page); return
                if any(k in text_lower for k in KEYWORDS_CENTRAL_PROCUREMENT): root.after(0, show_central_procurement_page); return
                if any(k in text_lower for k in KEYWORDS_PARKING): root.after(0, show_parking_page); return
                if any(k in text_lower for k in KEYWORDS_FOOTBALL): root.after(0, show_football_page); return
                if any(k in text_lower for k in KEYWORDS_TENNIS): root.after(0, show_tennis_page); return
                if any(k in text_lower for k in KEYWORDS_FIXIT): root.after(0, show_fixit_page); return
                if any(k in text_lower for k in KEYWORDS_GENERAL_ADMIN): root.after(0, show_general_admin_page); return
                if any(k in text_lower for k in KEYWORDS_INFO_DATA): root.after(0, show_info_data_page); return
                if any(k in text_lower for k in KEYWORDS_ACADEMIC_TOWER): root.after(0, show_academic_tower_page); return
                if any(k in text_lower for k in KEYWORDS_HR): root.after(0, show_hr_page); return
                if any(k in text_lower for k in KEYWORDS_ACCOUNTING_PLANNING_COOP): root.after(0, show_accounting_planning_coop_page); return
                if any(k in text_lower for k in KEYWORDS_PLANNING_COOP_VICE_DIRECTOR): root.after(0, show_planning_coop_vice_director_page); return
                if any(k in text_lower for k in KEYWORDS_STUDENT_AFFAIRS_VICE_DIRECTOR): root.after(0, show_student_affairs_vice_director_page); return
                if any(k in text_lower for k in KEYWORDS_ACADEMIC_VICE_DIRECTOR): root.after(0, show_academic_vice_director_page); return
                if any(k in text_lower for k in KEYWORDS_RESOURCE_VICE_DIRECTOR): root.after(0, show_resource_vice_director_page); return

                # ถ้าไม่ตรงกับเงื่อนไขใดๆ
                print_status(f"--- [MIC]: ไม่พบคำสั่งสำหรับ '{text}' ---")


            except sr.UnknownValueError:
                print_status("--- [MIC]: ฟังไม่เข้าใจ (ลองใหม่อีกครั้ง) ---")
                speak_thai("กรุณาพูดใหม่อีกครั้ง")
            except sr.WaitTimeoutError:
                print_status("--- [MIC]: หมดเวลา (ไม่ได้พูด) ---")
            except sr.UnknownValueError:
                print_status("--- [MIC]: ฟังไม่เข้าใจ (ลองใหม่อีกครั้ง) ---")
            except sr.RequestError:
                print_status("--- [MIC]: อินเทอร์เน็ตมีปัญหา ---")
            except Exception as e:
                print_status(f"--- [MIC ERROR]: {e} ---")
            
    finally:
        is_listening = False
        mic_status = "IDLE"

        
# def start_listening_thread(event=None):
   # """Start the listening process in a separate thread to prevent freezing"""
    #global is_listening
   # if not is_listening:
        # NEW: หยุด Timer Inactivity ชั่วคราวเมื่อเริ่มฟัง
       # unbind_inactivity_reset()
      #  Thread_Mic = threading.Thread(target=listen_for_speech)
     #   Thread_Mic.start()
   # else:
      #  print_status("--- [SYSTEM]: ระบบกำลังฟังอยู่... ---")  (โค้ดเก่า)

def start_listening_thread(event=None):
    global is_listening
    if not is_listening:
        # --- เพิ่มบรรทัดนี้ ---
        speak_thai("กรุณาพูดชื่อแผนกหรือจุดอำนวยการที่ท่านต้องการ")
        # ------------------
        unbind_inactivity_reset()
        Thread_Mic = threading.Thread(target=listen_for_speech)
        Thread_Mic.start()
    else:
        print_status("--- [SYSTEM]: ระบบกำลังฟังอยู่... ---")
# ***************************************************************
# ** FIXED: Microphone UI (Text BELOW logo) **
# ***************************************************************

try:
    # --- 1. Create Status Notification Label (MOVED BELOW) ---
    mic_text_label = ctk.CTkLabel(
        root, 
        text="กดเพื่อสั่งงานด้วยเสียง", 
        font=("Kanit", 22, "bold"), 
        text_color="gray"
    )
    # Center x=110 (Mic x=20 + half width 90), y=925 (Below mic)
    mic_text_label.place(x=110, y=925, anchor="center") 

    # --- 2. Create the Mic Frame ---
    mic_frame = tk.Frame(root, bg="white", width=180, height=180)
    mic_frame.place(x=20, y=725) 

    # --- 3. Create Canvas ---
    mic_canvas = tk.Canvas(
        mic_frame,
        width=180,
        height=180,
        bg="white",
        highlightthickness=0,
        bd=0
    )
    mic_canvas.pack()
    
    # --- 4. Bind Click Events ---
    mic_canvas.bind("<Button-1>", start_listening_thread) 
    mic_frame.bind("<Button-1>", start_listening_thread)

    # --- 5. Load Image Safely ---
    MIC_IMAGE_PATH = "microphone/microphone.png" 
    
    if os.path.exists(MIC_IMAGE_PATH):
        mic_image = Image.open(MIC_IMAGE_PATH).resize((90, 90))
        mic_photo = ImageTk.PhotoImage(mic_image)
    else:
        print_status(f"Warning: Microphone image not found at {MIC_IMAGE_PATH}")
        mic_image = Image.new('RGBA', (90, 90), (200, 200, 200, 0))
        mic_photo = ImageTk.PhotoImage(mic_image)

    # --- 6. Create Aura Circles ---
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

    # --- 7. Place Microphone Icon ---
    mic_canvas.create_image(90, 90, image=mic_photo, tags="mic")
    mic_canvas.image = mic_photo 

    # --- 8. Aura Animation & Text Update Function ---
    def animate_aura():
        global is_listening, alpha_value, direction, mic_canvas, aura_circles, mic_status
        
        try:
            if not mic_canvas.winfo_exists(): return
        except: return

        # === UPDATE TEXT & COLOR BASED ON STATUS ===
        if mic_status == "LISTENING":
            # State: Listening
            base_color_hex = ["#00FF00", "#32CD32", "#008000"] # Green
            speed = 5.0
            border_width = 6
            mic_text_label.configure(text="พูดได้เลย!", text_color="#00AA00")
            
        elif mic_status == "PROCESSING" or mic_status == "CALIBRATING":
            # State: Processing or Calibrating
            base_color_hex = ["#FFD700", "#FFA500", "#FF4500"] # Orange
            speed = 3.0
            border_width = 4
            if mic_status == "PROCESSING":
                mic_text_label.configure(text="กำลังประมวลผล...", text_color="#FF8C00")
            else:
                mic_text_label.configure(text="...", text_color="gray")
            
        else:
            # State: Idle
            base_color_hex = ["#E0B0FF", "#C77DFF", "#9D4EDD"] # Purple
            speed = 1.5
            border_width = 3
            mic_text_label.configure(text="กดเพื่อสั่งงานด้วยเสียง", text_color="gray")
        
        # === AURA PULSE ANIMATION ===
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
            
            colors_animated.append(f"#{r_final:02x}{g_final:02x}{b_final:02x}")

        for i, circle in enumerate(aura_circles):
            mic_canvas.itemconfig(circle, outline=colors_animated[i], width=border_width)

        root.after(50, animate_aura)

    # Start Animation
    animate_aura()
    mic_frame.lift()

except Exception as e:
    print_status(f"Error creating Microphone UI: {e}")
    
# ***************************************************************
# ** Initialization and Main Loop **
# ***************************************************************

# เริ่มต้นโหลดรูปภาพสไลด์ (เฉพาะแผนกวิชา)
load_slide_images()

# เริ่มต้นแสดงสไลด์ชุดแรก
if slide_images:
    # เพิ่มการเช็คว่ามีรูปภาพของอาคาร 10 และ ตึก 11 ใน slide_images หรือไม่
    has_tuk10 = any(d['filename'] == "อาคาร10.jpg" for d in slide_images)
    has_tuk11 = any(d['filename'] == "ตึก11.jpg" for d in slide_images)
    
    # ถ้าไม่มีรูปภาพอาคาร 10/11 ในโฟลเดอร์ ก็จะไม่แสดงในสไลด์
    if has_tuk10:
        print_status("อาคาร 10 ถูกเพิ่มในสไลด์แล้ว")
    if has_tuk11:
        print_status("ตึก 11 ถูกเพิ่มในสไลด์แล้ว")

    for i in range(min(5, len(slide_images))): # สร้าง 5 สไลด์แรกเพื่อครอบหน้าจอ
        place_next_slide(start_immediately_at_right_edge=False)

# เริ่มต้น Animation Marquee
animate_image_slide()

root.after(500, load_home_video)
# แสดงเฟรมเริ่มต้น (Home)
show_frame(home_content_frame)
root.after(500, load_home_video)
def load_home_video():
    try:
        # เปลี่ยน Path เป็น Tower/E.1
        VIDEO_PATH = "Tower/E.1" 
        
        # ตรวจสอบว่ามีไฟล์วิดีโอหรือไม่
        if os.path.exists(VIDEO_PATH):
            video_container.player = tkvideo(VIDEO_PATH, video_label, loop=1, size=(900, 500))
            video_container.player.play()
            print_status(f"Home Video loaded: {VIDEO_PATH}")
        else:
            # ลองเติม .mp4 กรณีไฟล์ไม่มีนามสกุล
            alt_path = VIDEO_PATH + ".mp4"
            if os.path.exists(alt_path):
                 video_container.player = tkvideo(alt_path, video_label, loop=1, size=(900, 500))
                 video_container.player.play()
            else:
                 video_label.pack_forget()
                 ctk.CTkLabel(video_container, text=f"Video not found: {VIDEO_PATH}", text_color="red").pack()
    except Exception as e:
        print_status(f"Error loading home video: {e}")
# เพิ่มบรรทัดนี้เพื่อเปิดระบบสัมผัสแผนที่
video_label.bind("<Button-1>", on_map_click)

# ===============================================================
# ** UPDATED SIDE MENU: รายชื่ออาคาร (Horizontal, Draggable, Large Frame) **
# ===============================================================

i# ===============================================================
# ** UPDATED: รายชื่ออาคาร (Draggable Frame & Draggable Button) **
# ===============================================================

is_list_open = False
list_frame_container = None

def toggle_building_list():
    global is_list_open, list_frame_container
    if is_list_open:
        if list_frame_container:
            list_frame_container.place_forget()
        is_list_open = False
    else:
        show_building_list_frame()
        is_list_open = True

# --- ฟังก์ชันสำหรับการลาก (ใช้ได้ทั้งปุ่มและเฟรม) ---
def start_drag(event, widget):
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

def do_drag(event, widget):
    x = widget.winfo_x() - widget._drag_start_x + event.x
    y = widget.winfo_y() - widget._drag_start_y + event.y
    widget.place(x=x, y=y, relx=0, rely=0, anchor="nw")

def show_building_list_frame():
    global list_frame_container
    if list_frame_container:
        list_frame_container.destroy()

    # 1. สร้างเฟรมหลัก
    list_frame_container = ctk.CTkFrame(home_content_frame, corner_radius=25, 
                                        fg_color="white", border_width=4, border_color="#8000FF")
    
    # วางไว้กลางจอในตอนแรก
    list_frame_container.place(relx=0.5, rely=0.5, anchor="center")

    # --- ทำให้เฟรมลากได้ ---
    list_frame_container.bind("<Button-1>", lambda e: start_drag(e, list_frame_container))
    list_frame_container.bind("<B1-Motion>", lambda e: do_drag(e, list_frame_container))

    # 2. ปุ่มกากบาทปิด
    btn_close = ctk.CTkButton(list_frame_container, text="✕", width=50, height=50, 
                              fg_color="#FF0000", text_color="white", font=("Arial", 24, "bold"),
                              command=toggle_building_list)
    btn_close.place(relx=1.0, rely=0.0, x=-15, y=15, anchor="ne")

    # 3. การโหลดรูปภาพ menu.jpg
    img_list_path = os.path.join("Tower", "menu.jpg")
    try:
        if os.path.exists(img_list_path):
            raw_img = Image.open(img_list_path)
            display_w = 800 
            ratio = display_w / float(raw_img.size[0])
            display_h = int(float(raw_img.size[1]) * ratio)
            
            resized_img = raw_img.resize((display_w, display_h), Image.LANCZOS)
            list_img = ctk.CTkImage(light_image=resized_img, dark_image=resized_img, size=(display_w, display_h))
            
            label_img = ctk.CTkLabel(list_frame_container, image=list_img, text="")
            label_img.image = list_img 
            label_img.pack(pady=(80, 40), padx=40)
            
            # ทำให้ตัวรูปภาพลากได้ด้วย (กรณีเมาส์คลิกโดนรูปแทนที่จะเป็นขอบเฟรม)
            label_img.bind("<Button-1>", lambda e: start_drag(e, list_frame_container))
            label_img.bind("<B1-Motion>", lambda e: do_drag(e, list_frame_container))
        else:
            err_label = ctk.CTkLabel(list_frame_container, text=f"ไม่พบไฟล์: {img_list_path}", text_color="red")
            err_label.pack(pady=100, padx=50)
    except Exception as e:
        print(f"Error: {e}")

# --- 4. สร้างปุ่มเมนูแนวนอนที่ลากได้ ---
btn_side_menu = ctk.CTkButton(
    home_content_frame, text="รายชื่ออาคาร", font=("Kanit", 22, "bold"),
    fg_color="#8000FF", text_color="white", width=160, height=60, corner_radius=15,
    command=toggle_building_list
)
btn_side_menu.place(relx=1.0, rely=0.5, anchor="e", x=-20)

# ผูกเหตุการณ์การลากให้ปุ่ม
btn_side_menu.bind("<Button-1>", lambda e: start_drag(e, btn_side_menu))
btn_side_menu.bind("<B1-Motion>", lambda e: do_drag(e, btn_side_menu))
# ===============================================================



update_datetime_clock()
# Main Loop
root.mainloop()
#อัพเดทใหม่ 2.0