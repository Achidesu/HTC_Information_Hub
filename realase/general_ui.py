# general_ui.py

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter 
import time
import os

# นำเข้าตัวแปร Global
from config import * # --- ฟังก์ชันช่วยเหลือในการพิมพ์สถานะ (จำเป็นต้องมีในทุกไฟล์) ---
def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

# -----------------------------------------------------------------
# --- ฟังก์ชัน Aura Animation ---
# -----------------------------------------------------------------
def animate_aura():
    """ควบคุมเอฟเฟกต์แสง Aura รอบไมค์"""
    global is_listening, alpha_value, direction, mic_canvas, aura_circles
    
    if not mic_canvas or not root:
        return 
        
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

# -----------------------------------------------------------------
# --- UI Component Creators ---
# -----------------------------------------------------------------

def create_top_bar(master):
    """สร้างแถบด้านบน (Fixed)"""
    top_bar = ctk.CTkFrame(master, height=150, fg_color="#8000FF")
    top_bar.pack(side="top", fill="x")

    try:
        # ⚠️ โปรดเปลี่ยน PATH นี้ให้เป็นที่อยู่รูป logo.png ที่ถูกต้อง ⚠️
        logo_image = Image.open("logo.png").resize((120, 120))
        logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(120,120))
        logo_label = ctk.CTkLabel(top_bar, image=logo_ctk_image, text="")
        logo_label.pack(side="left", padx=(20,10), pady=15)
    except Exception as e:
        print_status(f"ไม่พบไฟล์โลโก้ (logo.png): {e}")

    title_label = ctk.CTkLabel(top_bar, text="HTC Smart Hub", text_color="white", font=("Kanit", 36, "bold"))
    title_label.pack(side="left", padx=10, pady=15)
    
    return top_bar

def create_home_content(master, start_listening_callback):
    """สร้างเนื้อหาหลักของหน้า Home"""
    
    # === ไอคอนไมค์พร้อมเอฟเฟกต์ออร่า ===
    mic_canvas_ref = None
    blinking_dot_ref = None
    try:
        mic_frame = tk.Frame(master, bg="white", width=180, height=180)
        mic_frame.place(x=-25, y=725) # ตำแหน่ง Fixed

        mic_canvas_ref = tk.Canvas(
            mic_frame,
            width=180,
            height=180,
            bg="white",
            highlightthickness=0,
            bd=0
        )
        mic_canvas_ref.pack()
        
        mic_canvas_ref.bind("<Button-1>", start_listening_callback) 
        mic_frame.bind("<Button-1>", start_listening_callback)

        # ⚠️ โปรดเปลี่ยน PATH นี้ให้เป็นที่อยู่รูป microphone.png ที่ถูกต้อง ⚠️
        mic_image = Image.open("/home/pi/Test_GUI/microphone/microphone.png").resize((90, 90))
        mic_photo = ImageTk.PhotoImage(mic_image)
        config.mic_photo_ref = mic_photo # เก็บ Strong Reference

        colors = ["#E0B0FF", "#C77DFF", "#9D4EDD"]
        radii = [80, 60, 40]
        
        global aura_circles
        aura_circles = []

        for i, (color, radius) in enumerate(zip(colors, radii)):
            circle = mic_canvas_ref.create_oval(
                90 - radius, 90 - radius,
                90 + radius, 90 + radius,
                fill="",
                outline=color,
                width=3,
                tags="aura"
            )
            aura_circles.append((circle, radius)) 

        mic_canvas_ref.create_image(90, 90, image=mic_photo, tags="mic")
        mic_canvas_ref.image = mic_photo
        mic_frame.lift()

    except Exception as e:
        print_status(f"ไม่พบรูปไมค์ หรือเกิดข้อผิดพลาดในการสร้างออร่า: {e}")
        mic_frame = None

    # --- รูปแฟนเพจตรงกลาง ---
    try:
        # ⚠️ โปรดเปลี่ยน PATH นี้ให้เป็นที่อยู่รูป FF.png ที่ถูกต้อง ⚠️
        fanpage_image = Image.open("/home/pi/Test_GUI/Facebook/FF.png").resize((950, 400))
        fanpage_ctk_image = ctk.CTkImage(light_image=fanpage_image, dark_image=fanpage_image, size=(950,400))
        fanpage_label = ctk.CTkLabel(master, image=fanpage_ctk_image, text="")
        fanpage_label.pack(pady=(50, 10))
    except Exception as e:
        print_status(f"ไม่พบรูปแฟนเพจ: {e}")

    # --- ข้อความ: แผนผังภายในวิทยาลัย ---
    plan_label = ctk.CTkLabel(master, text="แผนผังภายในวิทยาลัย", font=("Kanit", 32, "bold"))
    plan_label.pack(pady=(0, 20))


    # --- ส่วนแสดงแผนผังพร้อมจุดกระพริบ ---
    map_canvas_widget = tk.Canvas(
        master,
        width=MAP_WIDTH,
        height=MAP_HEIGHT,
        bg="white", 
        highlightthickness=0,
        bd=0
    )
    # ใช้ pack แทน place เพื่อให้จัดเรียงได้ง่ายขึ้นใน frame
    map_canvas_widget.pack(pady=(0, 20)) 

    try:
        # ⚠️ โปรดเปลี่ยน PATH นี้ให้เป็นที่อยู่รูป 1.png ที่ถูกต้อง ⚠️
        map_image_path = "/home/pi/Test_GUI/Tower/1.png" 
        original_map_image = Image.open(map_image_path)

        map_image_resized = original_map_image.resize((MAP_WIDTH, MAP_HEIGHT), Image.LANCZOS)
        map_photo = ImageTk.PhotoImage(map_image_resized) 
        
        map_canvas_widget.create_image(0, 0, image=map_photo, anchor="nw")
        map_canvas_widget.image = map_photo # เก็บ Strong Reference

        blink_x = 375 
        blink_y = 312 
        blink_radius = 10 
        
        blinking_dot_ref = map_canvas_widget.create_oval(
            blink_x - blink_radius, blink_y - blink_radius,
            blink_x + blink_radius, blink_y + blink_radius,
            fill="#FF3333", 
        )

    except Exception as e:
        print_status(f"ไม่พบไฟล์รูปแผนผัง หรือเกิดข้อผิดพลาดในการโหลด: {e}")
        blinking_dot_ref = None 

    return (mic_frame, mic_canvas_ref, blinking_dot_ref)


def animate_blinking_dot():
    """ควบคุมจุดกระพริบบนแผนผัง"""
    global is_blinking_on 
    global blinking_dot 
    
    if not blinking_dot or not root:
        if root:
            root.after(400, animate_blinking_dot)
        return

    map_canvas_widget = root.nametowidget(blinking_dot).master # หา Canvas จาก Item ID

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

def create_fixed_bottom_widgets(master, start_drag_cmd, do_drag_cmd, stop_drag_cmd):
    """สร้าง UI ส่วนล่างทั้งหมด (Fixed)"""

    # --- 1. ส่วนแสดงรูปภาพสไลด์ (Image Marquee) ---
    image_slide_frame = ctk.CTkFrame(master, height=IMAGE_SLIDE_HEIGHT, fg_color="#F0F0F0", corner_radius=0) 
    image_slide_frame.pack(side="bottom", fill="x", pady=(0, 0)) 

    image_slide_canvas = tk.Canvas(
        image_slide_frame,
        height=IMAGE_SLIDE_HEIGHT,
        bg="#F0F0F0", 
        highlightthickness=0,
        bd=0,
    )
    image_slide_canvas.pack(fill="both", expand=True)

    # ผูก Drag Events (สำหรับอนาคต)
    image_slide_canvas.bind("<Button-1>", start_drag_cmd)
    image_slide_canvas.bind("<B1-Motion>", do_drag_cmd)
    image_slide_canvas.bind("<ButtonRelease-1>", stop_drag_cmd)


    # --- 2. ช่องแบบสอบถามความพึงพอใจ ---
    survey_frame = ctk.CTkFrame(master, height=180, fg_color="#F5F0FF", corner_radius=0)
    survey_frame.pack(side="bottom", fill="x", pady=(0, 0)) 

    inner_survey_frame = ctk.CTkFrame(survey_frame, fg_color="transparent")
    inner_survey_frame.pack(fill="both", expand=True, padx=40, pady=25)

    survey_text_frame = ctk.CTkFrame(inner_survey_frame, fg_color="transparent")
    survey_text_frame.pack(side="left", fill="both", expand=True)

    title_container = ctk.CTkFrame(survey_text_frame, fg_color="transparent")
    title_container.pack(anchor="w")

    try:
        # ⚠️ โปรดเปลี่ยน PATH นี้ให้เป็นที่อยู่รูป star.png ที่ถูกต้อง ⚠️
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
        # ⚠️ โปรดเปลี่ยน PATH นี้ให้เป็นที่อยู่รูป qrcode.png ที่ถูกต้อง ⚠️
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


    # --- 3. ข้อความเลื่อนด้านล่าง (Text Marquee) ---
    credit_frame = ctk.CTkFrame(master, height=55, fg_color="#D6B0FF")
    credit_frame.pack(side="bottom", fill="x") 

    canvas_marquee = tk.Canvas(
        credit_frame,
        height=55,
        bg="#D6B0FF",
        highlightthickness=0,
        bd=0,
    )
    canvas_marquee.pack(fill="both", expand=True)

    credit_text = "จัดทำโดย นักศึกษา แผนกภาควิชาเทคโนโลยีคอมพิวเตอร์"

    try:
        marquee_font = ("Kanit", 26, "bold")
    except:
        marquee_font = ("Arial", 26, "bold")

    text_id = canvas_marquee.create_text(
        1080, 28,
        text=credit_text,
        fill="black",
        font=marquee_font,
        anchor="w"
    )

    def scroll_text():
        canvas_marquee.move(text_id, -2, 0)
        x = canvas_marquee.coords(text_id)[0]

        try:
            bbox = canvas_marquee.bbox(text_id)
            if bbox:
                text_width = bbox[2] - bbox[0]
            else:
                text_width = 1080 
        except:
            text_width = 1080

        if x < -text_width:
            canvas_marquee.coords(text_id, 1080, 28)

        if root:
            root.after(16, scroll_text)

    if root:
        root.after(16, scroll_text)


    # --- 4. แถบล่างอีกชั้น (Bottom Bar - ล่างสุดของหน้าจอ) ---
    bottom_bar = ctk.CTkFrame(master, height=45, fg_color="#A070FF")
    bottom_bar.pack(side="bottom", fill="x") 

    bottom_label = ctk.CTkLabel(
        bottom_bar,
        text="© 2025 HatYai Technical College",
        font=("Arial", 20, "bold"),
        text_color="white"
    )
    bottom_label.pack(pady=5)
    
    return image_slide_canvas

def create_electronics_page_content(master, show_frame_cmd, home_frame):
    """สร้างเนื้อหาสำหรับหน้าแผนกอิเล็กทรอนิกส์"""
    header_frame = ctk.CTkFrame(master, height=150, fg_color="#A070FF")
    header_frame.pack(side="top", fill="x")
    
    ctk.CTkLabel(header_frame, 
                 text="แผนกวิชาอิเล็กทรอนิกส์", 
                 font=("Kanit", 36, "bold"),
                 text_color="white").pack(pady=40, padx=20)

    ctk.CTkLabel(master, 
                 text="ข้อมูล แผนผัง และรายละเอียดที่เกี่ยวข้อง", 
                 font=("Kanit", 28)).pack(pady=(60, 20))
    
    # ⚠️ Placeholder
    ctk.CTkLabel(master, 
                 text="(พื้นที่สำหรับใส่รูปภาพแผนผังเฉพาะแผนกอิเล็กทรอนิกส์)", 
                 font=("Kanit", 22),
                 text_color="#666666").pack(pady=100)

    ctk.CTkButton(master, 
                  text="❮ กลับสู่หน้าหลัก", 
                  command=lambda: show_frame_cmd(home_frame), 
                  font=("Kanit", 24),
                  fg_color="#8000FF",
                  hover_color="#6A0DAD",
                  width=250,
                  height=60).pack(pady=40)

def create_navigation_page_content(master, show_frame_cmd, home_frame):
    """สร้างเนื้อหาสำหรับหน้านำทางเฉพาะ"""
    header_frame = ctk.CTkFrame(master, height=150, fg_color="#FF4500")
    header_frame.pack(side="top", fill="x")
    
    ctk.CTkLabel(header_frame, 
                 text="นำทางไปยังอาคาร 60 ปี", 
                 font=("Kanit", 36, "bold"),
                 text_color="white").pack(pady=40, padx=20)

    ctk.CTkLabel(master, 
                 text="พื้นที่สำหรับแสดงแผนที่/ระยะทาง จากจุดปัจจุบัน", 
                 font=("Kanit", 28)).pack(pady=(60, 20))
    
    # ⚠️ Placeholder
    ctk.CTkLabel(master, 
                 text="[สถานะ]: กำลังวัดระยะทางไปยังอาคาร 60 ปี...\n(จะแสดงผลลัพธ์การวัดระยะทางที่นี่)", 
                 font=("Kanit", 22),
                 text_color="#666666").pack(pady=100)

    ctk.CTkButton(master, 
                  text="❮ กลับสู่หน้าหลัก", 
                  command=lambda: show_frame_cmd(home_frame), 
                  font=("Kanit", 24),
                  fg_color="#FF4500",
                  hover_color="#CC3700",
                  width=250,
                  height=60).pack(pady=40)