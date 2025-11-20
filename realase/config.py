# config.py

import customtkinter as ctk
import tkinter as tk 

# --- ตั้งค่า appearance และ theme ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ***************************************************************
# ** Global Variables สำหรับควบคุมสถานะและ UI **
# ***************************************************************

# ** Main Window Reference (กำหนดค่าใน main_app) **
root = None 

# ** Frame References (กำหนดค่าใน main_app) **
home_content_frame = None
electronics_content_frame = None
navigation_content_frame = None
top_bar = None

# ** สถานะไมค์/ออร่า **
is_blinking_on = True
blinking_dot = None 
is_listening = False 
mic_canvas = None 
aura_circles = [] 
alpha_value = [0.0] 
direction = [1] 
mic_frame = None 
MAP_WIDTH = 800
MAP_HEIGHT = 400
MAP_Y_POSITION_ON_FRAME = 600

# ** Navigation/Keyword Variables **
KEYWORDS_ELECTRONICS = ["อิเล็กทรอนิกส์", "อิเล็ก", "อีเล็ก", "แผนกอิเล็ก", "อิเล็กทรอนิก"] 

# ** สำหรับการนำทางเฉพาะ **
NAVIGATION_TRIGGER_IMAGE = "60 ปี.jpg" # <--- กำหนดชื่อไฟล์รูปภาพที่ต้องการให้คลิกแล้วนำทาง
MAX_NAVIGATION_MAP_HEIGHT = 750 
# ⚠️ โปรดเปลี่ยน PATH นี้ให้ตรงกับที่อยู่ของแผนที่จริงของคุณ
NAVIGATION_DISPLAY_MAP_PATH = "/home/pi/Test_GUI/Tower/1.png"

# *** Global Variables สำหรับ Image Slides ***
# ⚠️ โปรดเปลี่ยน PATH นี้ให้ตรงกับที่อยู่ของโฟลเดอร์รูปภาพจริงของคุณ
IMAGE_SLIDE_FOLDER = "/home/pi/Test_GUI/Picture_slide" 
IMAGE_SLIDE_HEIGHT = 300 # ความสูง *รวมกรอบ*
IMAGE_SLIDE_WIDTH_LIMIT = 900 # ความกว้างสูงสุด *รวมกรอบ*
SLIDE_GAP = 55 # ช่องว่างระหว่างรูปภาพ
SLIDE_FRAME_WIDTH = 10 # ความหนาของกรอบ (10px)
SLIDE_FRAME_COLOR = "black" # สีของกรอบ

current_slide_index = -1 
slide_images = [] 
slide_photo_images = [] 
image_slide_canvas = None 
active_slide_items = [] 
next_image_x_placement = 1080 
is_dragging = False # สำหรับควบคุมการลาก (ถ้ามี)
drag_start_x = 0