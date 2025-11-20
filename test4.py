# htc_smart_hub_with_continuous_mic.py
# HTC Smart Hub — full file (lazy-load images + safe background listen)
from cProfile import label
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import time, threading, tempfile, os
import speech_recognition as sr
from gtts import gTTS
import pygame
import sys
import traceback

# ---------- ตั้งค่าธีม ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- ขนาดหน้าจอ ----------
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920

# ---------- เตรียม pygame สำหรับเล่นเสียง ----------
# (ยังคง init ตอนเริ่ม แต่ถ้าเป็นปัญหาช้าให้ย้ายเข้า thread)
try:
    pygame.init()
    pygame.mixer.init()
except Exception as e:
    print("pygame init warning:", e)

# ---------- TTS function (gTTS -> pygame) ----------
tts_lock = threading.Lock()
def speak_tts(text, lang="th"):
    """
    สร้างไฟล์ mp3 ชั่วคราวด้วย gTTS แล้วเล่นด้วย pygame (threaded).
    ใช้ lock เพื่อไม่ให้เสียงทับกัน.
    """
    def _run():
        try:
            with tts_lock:
                tf = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tmp_path = tf.name
                tf.close()
                try:
                    tts = gTTS(text=text, lang=lang)
                    tts.save(tmp_path)
                except Exception as e:
                    print("gTTS save error:", e)
                    try: os.remove(tmp_path)
                    except: pass
                    return

                try:
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                except Exception as e:
                    print("ไม่สามารถเล่นเสียงได้:", e)
                finally:
                    try:
                        os.remove(tmp_path)
                    except:
                        pass
        except Exception as e:
            print("TTS error:", e)

    threading.Thread(target=_run, daemon=True).start()

# ---------- ระบบรู้จำเสียง (Recognizer) ----------
recognizer_main = sr.Recognizer()

# ---------- ข้อมูลแผนก (รวมฝ่ายอำนวยการ) ----------
# รูปแบบ tuple: (image_file, map_file, distance_meters, walk_time_minutes)
departments = {
    # ตัวอย่างแผนกต่าง ๆ (แก้เปลี่ยนไฟล์ตามโฟลเดอร์คุณ)
    "แผนกวิชาช่างก่อสร้าง": ("B11.jpg", "s2.gif", 120, 3),
    "แผนกวิชาช่างโยธา": ("B9.jpg", "s2.gif", 150, 4),
    "แผนกวิชาช่างเฟอร์นิเจอร์และตกแต่งภายใน": ("B12.jpg", "s14.gif", 180, 5),
    "แผนกวิชาช่างสำรวจ": ("B6.jpg", "s8.gif", 200, 6),
    "แผนกวิชาสถาปัตยกรรม": ("B6.jpg", "s8.gif", 200, 6),
    "แผนกวิชาช่างยนต์": ("B15.jpg", "s5.gif", 100, 3),
    "แผนกวิชาช่างกลโรงงาน": ("B16.jpg", "s6.gif", 90, 2),
    "แผนกวิชาช่างเชื่อมโลหะ": ("B17.jpg", "s9.gif", 110, 3),
    "แผนกวิชาช่างเทคนิคพื้นฐาน": ("B1.jpg", "s12.gif", 130, 3),
    "แผนกวิชาช่างไฟฟ้า": ("B10.jpg", "s2.gif", 140, 4),
    "แผนกวิชาช่างอิเล็กทรอนิกส์": ("B8.jpg", "s1.gif", 160, 4),
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ": ("B2.jpg", "s10.gif", 180, 5),
    "แผนกวิชาเทคโนโลยีสารสนเทศ": ("B13.jpg", "s6.gif", 170, 4),
    "แผนกวิชาเทคโนโลยีปิโตรเลียม": ("B88.jpg", "s11.gif", 190, 5),
    "แผนกวิชาเทคนิคพลังงาน": ("B3.jpg", "s7.gif", 200, 6),
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": ("s15.jpeg", "s13.gif", 160, 4),
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง": ("B14.jpg", "s4.gif", 210, 6),
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": ("B3.1.jpg", "s7.gif", 200, 5),
    "แผนกวิชาแผนกการบิน": ("s15.jpeg", "s13.gif", 160, 4),
    "แผนกวิชาเทคโนโลยีคอมพิวเตอร์": ("w11.jpg", "w11.jpg", 180, 2),

    # ฝ่าย/ห้องงานอำนวยการ
    "ห้องการเงิน": ("abc.jpg", "o20.gif", 40, 1),
    "ห้องงานทะเบียน": ("ab.jpg", "o18.gif", 40, 1),
    "ห้องงานบุคลากร": ("a1.jpg", "o12.gif", 40, 1),
    "ห้องงานการบัญชี": ("a3.jpg", "o13.gif", 40, 1),
    "ห้องงานวางแผนและงบประมาณ": ("a3.jpg", "o13.gif", 50, 1),
    "ห้องงานรองผู้อำนวยการแผนและความร่วมมือ": ("a4.jpg", "o14.gif", 50, 1),
    "ห้องรองผู้อำนวยการฝ่ายกิจการนักเรียน นักศึกษา": ("a5.jpg", "o15.gif", 50, 1),
    "ห้องรองผู้อำนวยการฝ่ายวิชาการ": ("a6.jpg", "o16.gif", 50, 1),
    "ห้องรองผู้อำนวยการฝ่ายบริหารทรัพยากร": ("a7.jpg", "o17.gif", 50, 1),
    "ห้องงานอาชีวศึกษาระบบทวิภาคี": ("a9.jpg", "o19.gif", 50, 1),
    "ห้องงานพัฒนาหลักสูตร": ("a11.jpg", "o21.gif", 50, 1),
    "งานครูที่ปรึกษา": ("w10.jpg", "l4.gif", 40, 1),
    "งานปกครอง": ("w10.jpg", "l4.gif", 40, 1),
    "งานแนะแนวและการจัดหางาน": ("w9.jpg", "l2.gif", 60, 1),
    "งานกิจการนักเรียน นักศึกษา": ("w4.jpg", "l3.gif", 60, 1),
    "งานวัดและประเมินผล": ("w3.jpg", "l2.gif", 50, 1),
    "ศูนย์ประสานงานบัณฑิตศึกษา วิทยาลัยเทคนิคหาดใหญ่": ("w2.jpg", "l1.gif", 60, 1),
    "สำนักงานอาชีวบัณฑิต วิทยาลัยเทคนิคหาดใหญ่": ("w2.jpg", "l1.gif", 60, 1),
    "ร้านค้าสวัสดิการ": ("w1.jpg", "o1.gif", 210, 3),
    "โรงอาหารใหม่": ("w8.jpg", "o5.gif", 230, 3),
    "โรงอาหารเก่า": ("w7.jpg", "o3.gif", 110, 1),
    "หอประชุม": ("w6.jpg", "o2.gif", 160, 2),
    "ห้องสมุด": ("w5.jpg", "o9.gif", 60, 1),
    "ตึกส้ม": ("w11.jpg", "w11.jpg", 180, 2),
}

# ---------- คำย่อ/shortcuts ----------
shortcuts = {
    "แผนกวิชาช่างอิเล็กทรอนิกส์": ["อิเล็ก", "อิเล็กทรอนิกส์", "อีเล็ก"],
    "แผนกวิชาช่างไฟฟ้า": ["ไฟฟ้า"],
    "แผนกวิชาช่างยนต์": ["ยนต์", "ช่างยนต์"],
    "แผนกวิชาเทคโนโลยีสารสนเทศ": ["ไอที", "สารสนเทศ", "เทคโนโลยี"],
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์": ["เมคคา", "หุ่นยนต์"],
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน": ["โลจิสติกส์", "ซัพพลายเชน"],
    "ห้องการเงิน": ["การเงิน"],
    "ห้องงานทะเบียน": ["งานทะเบียน", "ทะเบียน"],
    "ห้องงานบุคลากร": ["งานบุคลากร", "บุคลากร"],
    "ห้องงานการบัญชี": ["งานบัญชี", "การบัญชี", "บัญชี"],
    "ห้องงานวางแผนและงบประมาณ": ["วางแผน", "งบประมาณ", "งานวางแผน"],
    "ห้องงานรองผู้อำนวยการแผนและความร่วมมือ": ["แผนและความร่วมมือ", "งานแผน"],
    "ห้องงานอาชีวศึกษาระบบทวิภาคี": ["ทวิภาคี", "ระบบทวิภาคี"],
    "งานปกครอง": ["ปกครอง"],
    "งานครูที่ปรึกษา": ["ที่ปรึกษา"],
    "งานแนะแนวและการจัดหางาน": ["แนะแนว", "การจัดหางาน", "หางาน"],
    "ร้านค้าสวัสดิการ": ["สหกรณ์", "ร้านค้าสวัสดิการ"],
    "โรงอาหารใหม่": ["โรงอาหารใหม่"],
    "โรงอาหารเก่า": ["โรงอาหารเก่า"],
    "หอประชุม": ["หอประชุม"],
    "ห้องสมุด": ["ห้องสมุด"],
    "ตึกส้ม": ["ตึกส้ม"],
}

# ---------- ป้องกันการพูดซ้ำ ----------
last_announced = {"title": None}
last_announced_lock = threading.Lock()

# ---------- สร้าง mapping สำหรับการค้นหา ----------
_search_variants = {}
for key in list(departments.keys()):
    lower_key = key.lower()
    variants = {lower_key}
    if lower_key.startswith("แผนก"):
        variants.add(lower_key.replace("แผนก", "").strip())
    if lower_key.startswith("ห้อง"):
        variants.add(lower_key.replace("ห้อง", "").strip())
    _search_variants[key] = variants

_shortcut_map = {}
for main, words in shortcuts.items():
    for w in words:
        _shortcut_map[w.lower()] = main

def find_department_by_text(text):
    lowered = text.lower().strip()
    lowered = lowered.replace("แผนก", "").replace("ห้อง", "").strip()

    # shortcuts first
    for sw, main in _shortcut_map.items():
        if sw in lowered:
            return main

    # full/variants
    for main_name, variants in _search_variants.items():
        for v in variants:
            if v and v in lowered:
                return main_name

    # word by word fallback
    words = lowered.split()
    for w in words:
        for main_name, variants in _search_variants.items():
            for v in variants:
                if v and w in v:
                    return main_name
    return None

# ---------- AnimatedGIF helper (lazy-load frames, animate only when started) ----------
class AnimatedGIF(ctk.CTkLabel):
    def __init__(self, master, path, width=900, height=600, delay=80, *args, **kwargs):
        super().__init__(master, *args, **kwargs, text="")
        self.path = path
        self.width = width
        self.height = height
        self.delay = delay
        self.frames = []
        self.idx = 0
        self._animating = False
        self._loading = False
        # show placeholder or first frame if possible lazily
        self._placeholder_text = "(โหลด GIF...)"

    def load_frames(self):
        if self._loading or self.frames:
            return
        self._loading = True
        try:
            pil = Image.open(self.path)
            temp_frames = []
            for img in ImageSequence.Iterator(pil):
                frm = img.copy().resize((self.width, self.height))
                temp_frames.append(ImageTk.PhotoImage(frm))
            self.frames = temp_frames
        except Exception as e:
            print(f"ไม่สามารถโหลด GIF: {self.path} -> {e}")
            self.frames = []
        finally:
            self._loading = False

    def start(self):
        # load frames in background thread to avoid blocking UI
        if self._animating:
            return
        def _start_worker():
            try:
                self.load_frames()
                if not self.frames:
                    # show text if failed
                    def set_text():
                        self.configure(text="(ไม่พบแผนที่ GIF)")
                    self.after(0, set_text)
                    return
                # once frames loaded, begin animate on main thread
                def _begin_anim():
                    self._animating = True
                    self.idx = 0
                    self.configure(image=self.frames[self.idx], text="")
                    self.after(self.delay, self._animate)
                self.after(0, _begin_anim)
            except Exception as e:
                print("AnimatedGIF start error:", e)
        threading.Thread(target=_start_worker, daemon=True).start()

    def _animate(self):
        if not self._animating or not self.frames:
            return
        try:
            self.idx = (self.idx + 1) % len(self.frames)
            self.configure(image=self.frames[self.idx])
        except Exception as e:
            print("AnimatedGIF animate error:", e)
            self._animating = False
            return
        self.after(self.delay, self._animate)

    def stop(self):
        self._animating = False

# ---------- ฟังก์ชันสร้างหน้าแผนก (lazy load image/map) ----------
def create_image_page(root, title, img_path, map_path, distance, walk_time):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")
    frame._loaded = False
    frame._img_path = img_path
    frame._map_path = map_path

    # header
    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")
    try:
        logo_img_obj = Image.open("33.png").resize((90, 90))
        logo_ctkimg = ctk.CTkImage(light_image=logo_img_obj, dark_image=logo_img_obj, size=(90,90))
        logo_label = ctk.CTkLabel(header, image=logo_ctkimg, text="")
        logo_label.image = logo_ctkimg
        logo_label.pack(side="left", padx=20, pady=8)
    except Exception:
        pass

    ctk.CTkLabel(header, text=title, text_color="white", font=("Arial Black", 36)).pack(padx=20, pady=12, side="left")

    # content
    content = ctk.CTkFrame(frame, fg_color="white")
    content.pack(pady=10, fill="both", expand=True)

    # placeholder labels (image & map) - actual images loaded on demand
    frame._img_label = ctk.CTkLabel(content, text="(กำลังโหลดรูปภาพ)", font=("Arial", 18), text_color="gray")
    frame._img_label.pack(pady=10)

    ctk.CTkLabel(content, text="🗺️ แผนที่ตำแหน่งห้อง / แผนก", font=("Arial", 24, "bold"), text_color="#5b00a0").pack(pady=8)

    frame._map_container = ctk.CTkFrame(content, fg_color="white")
    frame._map_container.pack(pady=6)

    # distance/time
    ctk.CTkLabel(content, text=f"📏 ระยะทาง: {distance} เมตร", font=("Arial", 20), text_color="#333").pack(pady=(16,4))
    ctk.CTkLabel(content, text=f"⏱️ เวลาเดินโดยประมาณ: {walk_time} นาที", font=("Arial", 20), text_color="#333").pack(pady=(0,16))

    # footer
    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")

    return frame

def ensure_page_loaded(frame, map_width=900, map_height=600, img_width=900, img_height=600):
    """
    โหลดรูปและ GIF เมื่อหน้าเพจถูกแสดงครั้งแรก (lazy load)
    """
    if getattr(frame, "_loaded", False):
        return
    frame._loaded = True

    # load main image
    try:
        p = frame._img_path
        if p and os.path.exists(p):
            img_obj = Image.open(p).resize((img_width, img_height))
            photo = ctk.CTkImage(light_image=img_obj, dark_image=img_obj, size=(img_width,img_height))
            frame._img_label.configure(image=photo, text="")
            frame._img_label.image = photo
        else:
            frame._img_label.configure(text="(ไม่พบรูปภาพหลัก)", image=None)
    except Exception as e:
        print("load main image error:", e)
        frame._img_label.configure(text="(ไม่พบรูปภาพหลัก)", image=None)

    # load map (gif or static)
    map_p = frame._map_path
    try:
        if map_p and map_p.lower().endswith(".gif") and os.path.exists(map_p):
            # use AnimatedGIF and start it
            gif_widget = AnimatedGIF(frame._map_container, map_p, width=map_width, height=map_height, delay=80)
            gif_widget.pack()
            gif_widget.start()
            frame._map_widget = gif_widget
        else:
            if map_p and os.path.exists(map_p):
                map_img_obj = Image.open(map_p).resize((map_width, map_height))
                map_photo = ctk.CTkImage(light_image=map_img_obj, dark_image=map_img_obj, size=(map_width,map_height))
                map_lbl = ctk.CTkLabel(frame._map_container, image=map_photo, text="")
                map_lbl.image = map_photo
                map_lbl.pack()
                frame._map_widget = map_lbl
            else:
                label = ctk.CTkLabel(frame._map_container, text="(ไม่พบแผนที่)", font=("Arial", 18), text_color="gray")
                label.pack()
                frame._map_widget = label
    except Exception as e:
        print("load map error:", e)
        label = ctk.CTkLabel(frame._map_container, text="(ไม่พบแผนที่)", font=("Arial", 18), text_color="gray")
        label.pack()
        frame._map_widget = label

# ---------- หน้าเมนูหลัก ----------
def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="#efeaff")
    frame.grid(row=0, column=0, sticky="nsew")

    # header bar
    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")
    try:
        logo_img_obj = Image.open("33.png").resize((120, 120))
        logo_ctkimg = ctk.CTkImage(light_image=logo_img_obj, dark_image=logo_img_obj, size=(120,120))
        logo_label = ctk.CTkLabel(header, image=logo_ctkimg, text="")
        logo_label.image = logo_ctkimg
        logo_label.pack(side="left", padx=20, pady=8)
    except Exception:
        pass

    ctk.CTkLabel(header, text="HTC Smart Hub", text_color="white", font=("Arial Black", 40)).pack(side="left", padx=16, pady=12)

    # large banner (optional)
    try:
        ff_img_obj = Image.open("FF.png").resize((950, 400))
        ff_ctk = ctk.CTkImage(light_image=ff_img_obj, dark_image=ff_img_obj, size=(950,400))
        ff_label = ctk.CTkLabel(frame, image=ff_ctk, text="")
        ff_label.image = ff_ctk
        ff_label.pack(pady=30)
    except Exception:
        pass

    # animated hero (optional)
    try:
        hero = AnimatedGIF(frame, "s00.gif", width=1000, height=420, delay=80)
        hero.pack(pady=20)
        # start hero animation later when main menu shown
        frame._hero_widget = hero
    except Exception as e:
        print("s00.gif load error:", e)
        ctk.CTkLabel(frame, text="(ไม่พบไฟล์ s00.gif)", font=("Arial", 20), text_color="gray").pack(pady=20)

    # ---------- ไมค์ลอยด้านซ้าย ----------
    float_frame = ctk.CTkFrame(frame, fg_color="#7b2ff7", corner_radius=18)
    float_frame.place(relx=0.02, rely=0.45, anchor="w")

    mic_float_btn = ctk.CTkButton(float_frame, text="🎤", width=80, height=80, font=("Arial", 36, "bold"),
                                  fg_color="white", text_color="#7b2ff7", hover_color="#eee",
                                  corner_radius=40, command=lambda: threading.Thread(target=single_listen_and_process, daemon=True).start())
    mic_float_btn.pack(pady=(10,6))

    # ข้อความชวนพูด
    mic_hint = ctk.CTkLabel(float_frame, text="กรุณาพูดแผนกวิชาหรือ\nฝ่ายอำนวยที่ท่านต้องการ", font=("Arial", 14), text_color="white", justify="center")
    mic_hint.pack()

    # bottom footers (2 layers)
    footer_top = ctk.CTkFrame(frame, fg_color="#6b3fe8", corner_radius=0, height=50)
    footer_top.pack(side="bottom", fill="x")
    footer_label_top = ctk.CTkLabel(footer_top, text="ออกแบบ-เขียน โดย ช่างเทคโนโลยีคอมพิวเตอร์", text_color="white", font=("Arial", 18))
    footer_label_top.pack(pady=8)

    footer_bottom = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0, height=48)
    footer_bottom.pack(side="bottom", fill="x")

    marquee_text = "  ออกแบบ-เขียน โดย ช่างเทคโนโลยีคอมพิวเตอร์  "
    marquee_var = {"text": marquee_text}
    marquee_label = ctk.CTkLabel(footer_bottom, text=marquee_text, text_color="white", font=("Arial", 20))
    marquee_label.pack(pady=6)

    def marquee_shift():
        s = marquee_var["text"]
        s = s[1:] + s[0]
        marquee_var["text"] = s
        marquee_label.configure(text=s)
        footer_bottom.after(180, marquee_shift)

    footer_bottom.after(180, marquee_shift)

    return frame

# ---------- หน้าแผนก (รายการ) ----------
def create_department_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(frame, text="รายการแผนก (สั่งด้วยเสียง)", font=("Arial Black", 30), text_color="#5b00a0").pack(pady=30)

    list_frame = ctk.CTkFrame(frame, fg_color="white")
    list_frame.pack(pady=10, fill="both", expand=True)
    for name in departments.keys():
        ctk.CTkLabel(list_frame, text=f"• {name}", font=("Arial", 20), text_color="#333").pack(anchor="w", padx=20, pady=6)

    footer_top = ctk.CTkFrame(frame, fg_color="#6b3fe8", corner_radius=0, height=50)
    footer_top.pack(side="bottom", fill="x")
    ctk.CTkLabel(footer_top, text="ออกแบบ-เขียน โดย ช่างเทคโนโลยีคอมพิวเตอร์", text_color="white", font=("Arial", 18)).pack(pady=8)
    footer_bottom = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0, height=48)
    footer_bottom.pack(side="bottom", fill="x")
    marquee_label = ctk.CTkLabel(footer_bottom, text="  ออกแบบ-เขียน โดย ช่างเทคโนโลยีคอมพิวเตอร์  ", text_color="white", font=("Arial", 20))
    marquee_label.pack(pady=6)
    def marquee_shift2():
        s = marquee_label.cget("text")
        s = s[1:] + s[0]
        marquee_label.configure(text=s)
        footer_bottom.after(180, marquee_shift2)
    footer_bottom.after(180, marquee_shift2)

    return frame

# ========================================================================
# ฟังก์ชันเปิดหน้า และพูดชื่อแผนกเมื่อเป็น page แผนก/ห้อง
# ========================================================================
def show_frame(frame, title=None):
    # ยกเลเยอร์
    try:
        frame.tkraise()
    except Exception as e:
        print("show_frame warning:", e)

    # ถ้ามี hero GIF บนหน้าหลัก ให้เริ่มเมื่อแสดง
    try:
        if hasattr(frame, "_hero_widget"):
            frame._hero_widget.start()
    except Exception:
        pass

    # ถ้าเป็นหน้าแผนกจริง ๆ ให้ lazy-load รูปของหน้า
    try:
        if getattr(frame, "_img_path", None) is not None:
            ensure_page_loaded(frame)
    except Exception as e:
        print("ensure_page_loaded error:", e)

    if not title:
        return

    with last_announced_lock:
        if last_announced["title"] == title:
            return
        last_announced["title"] = title

    # พูดชื่อง่าย ๆ
    if title.startswith("แผนก"):
        name = title.replace("แผนก", "").strip()
        info = departments.get(f"แผนก{name}") or departments.get(name) or departments.get(f"แผนก{name.strip()}")
        if info:
            distance = info[2]; walk_time = info[3]
            speak_tts(f"แผนก {name} ระยะทาง {distance} เมตร เวลาเดินประมาณ {walk_time} นาที")
        else:
            speak_tts(title)
    elif title.startswith("ห้อง"):
        name = title.strip()
        info = departments.get(name) or departments.get(name.replace("ห้อง", "").strip())
        if info:
            distance = info[2]; walk_time = info[3]
            speak_tts(f"{name} ระยะทาง {distance} เมตร เวลาเดินประมาณ {walk_time} นาที")
        else:
            speak_tts(title)
    else:
        speak_tts(title)

# ---------- ฟังก์ชันประมวลผลคำสั่งเสียง ----------
def process_command_text(text):
    if not text or not text.strip():
        return
    lowered = text.lower()
    print("process_command_text got:", lowered)

    # กลับ / หน้าหลัก
    if "กลับ" in lowered or "หน้าหลัก" in lowered:
        with last_announced_lock:
            last_announced["title"] = None
        root.after(0, lambda: show_frame(main_frame, "หน้าหลัก"))
        return

    # หาแผนก
    found = find_department_by_text(lowered)
    if found:
        title = found if found.startswith("ห้อง") else (found if found.startswith("แผนก") else f"แผนก{found}")
        # call on main thread
        if found in image_pages_department:
            root.after(0, lambda n=found, t=title: show_frame(image_pages_department[n], t))
        else:
            speak_tts("ไม่พบชื่อแผนกหรือห้องที่กล่าว กรุณาพูดใหม่")
        return

    # ไม่พบ
    speak_tts("ไม่พบชื่อแผนกหรือห้องที่กล่าว กรุณาพูดใหม่")

# ---------- Continuous listening thread (background) ----------
def listen_continuously_thread():
    r = sr.Recognizer()
    # ปรับเสียงรอบข้างตอนเริ่มใน thread (อาจช้า ถ้ามีปัญหาให้ลด duration)
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
    except Exception as e:
        print("ไมโครโฟนไม่พร้อมหรือไม่พบอุปกรณ์ (background):", e)

    while True:
        try:
            with sr.Microphone() as source:
                print("🎤 (Background) กำลังฟังเสียงตลอดเวลา…")
                audio = r.listen(source, phrase_time_limit=4)
            try:
                text = r.recognize_google(audio, language="th-TH")
                print("BG heard:", text)
                process_command_text(text)
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print("RequestError (background):", e)
                time.sleep(1)
                continue
        except Exception as e:
            print("Error listening background:", e)
            time.sleep(0.5)
            continue

# ---------- single listen (on floating mic press) ----------
def single_listen_and_process():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            speak_tts("กรุณาพูดแผนกวิชาหรือฝ่ายอำนวยที่ท่านต้องการ")
            r.adjust_for_ambient_noise(source, duration=0.6)
            audio = r.listen(source, timeout=7, phrase_time_limit=6)
        try:
            text = r.recognize_google(audio, language="th-TH")
            print("Single heard:", text)
            process_command_text(text)
        except sr.UnknownValueError:
            speak_tts("ขอโทษ ไม่เข้าใจ กรุณาพูดใหม่")
        except sr.RequestError:
            speak_tts("ไม่สามารถเชื่อมต่อระบบรู้จำเสียงได้")
    except Exception as e:
        print("single listen error:", e)
        speak_tts("มีข้อผิดพลาดการใช้ไมโครโฟน")

# ========================================================================
# Start application (ไม่มีหน้า splash) — สร้าง GUI ก่อนแล้วค่อยเริ่ม thread ฟังเสียง
# ========================================================================
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# create frames
main_frame = create_main_menu(root)
department_frame = create_department_page(root)

# สร้างหน้า image pages (แต่ยังไม่โหลดรูป/แผนที่จนกว่าจะเปิด)
image_pages_department = {}
for n, v in departments.items():
    title = n if n.startswith("ห้อง") else (n if n.startswith("แผนก") else f"แผนก{n}")
    img_file, map_file, dist, wtime = v
    image_pages_department[n] = create_image_page(root, title, img_file, map_file, dist, wtime)

# แสดงหน้าหลักทันที (ไม่มี splash)
root.after(100, lambda: show_frame(main_frame, "หน้าหลัก"))

# เริ่ม thread ฟังเสียงหลัง GUI ขึ้น (เลื่อน 1 วิ เพื่อให้ UI แสดงก่อน)
def start_background_listening_delayed():
    threading.Thread(target=listen_continuously_thread, daemon=True).start()

root.after(1000, start_background_listening_delayed)

# ถ้าต้องการ ให้เริ่มแอนิเมชัน hero บนหน้าหลักเมื่อ GUI แสดง
def start_hero_if_any():
    try:
        if hasattr(main_frame, "_hero_widget"):
            main_frame._hero_widget.start()
    except Exception:
        pass

root.after(500, start_hero_if_any)

# run
try:
    root.mainloop()
except Exception:
    traceback.print_exc()
    try:
        root.destroy()
    except:
        pass
    sys.exit(1)
