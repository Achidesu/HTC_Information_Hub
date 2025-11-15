# htc_smart_hub_google_tts.py
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import time, threading
import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile

# ---------- ตั้งค่าธีม ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- ขนาดหน้าจอ ----------
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920

# ---------- ตั้งค่าเสียง Google TTS ----------
pygame.mixer.init()

def speak(text):
    """ใช้ Google TTS พูดข้อความ"""
    def run():
        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tf:
                tts = gTTS(text=text, lang="th")
                tts.save(tf.name)
                pygame.mixer.music.load(tf.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
        except Exception as e:
            print("TTS Error:", e)
    threading.Thread(target=run, daemon=True).start()

# ========================================================================
# ข้อมูลแผนกและ shortcuts
# ========================================================================
departments = {
    "ช่างก่อสร้าง": ("B11.jpg", "s2.gif", 120, 3),
    "ช่างโยธา": ("B9.jpg", "s2.gif", 150, 4),
    "ช่างเฟอร์นิเจอร์และตกแต่งภายใน": ("B12.jpg", "s14.gif", 180, 5),
    "ช่างสำรวจ": ("B6.jpg", "s8.gif", 200, 6),
}
shortcuts = {
    "ช่างก่อสร้าง": ["ก่อสร้าง"],
    "ช่างโยธา": ["โยธา"],
    "ช่างเฟอร์นิเจอร์และตกแต่งภายใน": ["เฟอร์นิเจอร์", "ตกแต่ง"],
    "ช่างสำรวจ": ["สำรวจ"],
}

# ========================================================================
# ระบบไมค์เปิดตลอดเวลา
# ========================================================================
def handle_voice_command(command):
    cmd = command.replace("แผนก", "").strip()
    if "กลับ" in cmd or "หน้าหลัก" in cmd:
        show_frame(main_frame, "หน้าหลัก")
        return
    for name in departments.keys():
        if cmd in name or cmd in shortcuts.get(name, []):
            show_frame(image_pages_department[name], f"แผนก{name}")
            return
    speak("ไม่พบชื่อแผนก")

def listen_continuously():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
    while True:
        try:
            with sr.Microphone() as source:
                audio = r.listen(source, phrase_time_limit=4)
            command = r.recognize_google(audio, language="th-TH")
            handle_voice_command(command)
        except:
            continue

def listen_once():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.7)
        try:
            audio = r.listen(source, timeout=7, phrase_time_limit=5)
            command = r.recognize_google(audio, language="th-TH")
            handle_voice_command(command)
        except:
            speak("ไม่ได้ยินเสียง กรุณาลองใหม่อีกครั้ง")

# ========================================================================
# Animated GIF
# ========================================================================
class AnimatedGIF(ctk.CTkLabel):
    def __init__(self, master, path, width=900, height=600, delay=100, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.width = width
        self.height = height
        self.delay = delay
        self.frames = []
        try:
            for img in ImageSequence.Iterator(Image.open(path)):
                frm = img.copy().resize((self.width, self.height))
                self.frames.append(ImageTk.PhotoImage(frm))
        except:
            self.frames = []
        self.idx = 0
        if self.frames:
            self.after(self.delay, self._animate)
    def _animate(self):
        if not self.frames:
            return
        self.configure(image=self.frames[self.idx])
        self.idx = (self.idx + 1) % len(self.frames)
        self.after(self.delay, self._animate)

# ========================================================================
# ฟังก์ชันช่วย
# ========================================================================
def show_frame(frame, title=None):
    frame.tkraise()
    if title:
        speak(f"เปิดหน้า {title}")

# ---------- สร้างหน้าแสดงรูป/แผนที่แผนก ----------
def create_image_page(root, title, img_path, map_path, distance, walk_time):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    # Header พร้อมโลโก้ซ้ายบน
    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")
    try:
        logo_img = Image.open("logo-login.png").resize((90, 90))
        logo_photo = ImageTk.PhotoImage(logo_img)
        ctk.CTkLabel(header, image=logo_photo, text="").pack(side="left", padx=25, pady=10)
    except:
        ctk.CTkLabel(header, text="HTC", font=("Arial Black",52), text_color="white").pack(side="left", padx=25)
    ctk.CTkLabel(header, text=title, font=("Arial Black",46), text_color="white").pack(side="left", padx=50, pady=25)

    # Content รูปหลัก
    content = ctk.CTkFrame(frame, fg_color="white")
    content.pack(pady=10)
    try:
        img = Image.open(img_path).resize((900,600))
        photo = ImageTk.PhotoImage(img)
        ctk.CTkLabel(content, image=photo, text="").pack(pady=20)
        frame.image = photo
    except:
        ctk.CTkLabel(content, text="(ไม่พบรูปภาพหลัก)", font=("Arial",30), text_color="gray").pack(pady=30)

    # แผนที่/GIF
    map_container = ctk.CTkFrame(content, fg_color="white")
    map_container.pack(pady=10)
    if map_path.lower().endswith(".gif"):
        gif = AnimatedGIF(map_container, map_path, width=900, height=600, delay=80)
        gif.pack()
    else:
        try:
            map_img = Image.open(map_path).resize((900,600))
            map_photo = ImageTk.PhotoImage(map_img)
            ctk.CTkLabel(map_container, image=map_photo, text="").pack()
            frame.map_image = map_photo
        except:
            ctk.CTkLabel(map_container, text="(ไม่พบแผนที่)", font=("Arial",28), text_color="gray").pack(pady=20)

    # ระยะทาง/เวลาเดิน
    ctk.CTkLabel(content, text=f"📏 ระยะทาง: {distance} เมตร", font=("Arial",28), text_color="#333").pack(pady=(20,5))
    ctk.CTkLabel(content, text=f"⏱️ เวลาเดินโดยประมาณ: {walk_time} นาที", font=("Arial",28), text_color="#333").pack(pady=(0,20))

    # พูดชื่อแผนก + ระยะทาง + เวลาเดิน
    speak(f"แผนก {title} ระยะทาง {distance} เมตร ใช้เวลาเดิน {walk_time} นาที")

    return frame

# ---------- หน้าแรก Main Menu ----------
def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="#efeaff")
    frame.grid(row=0, column=0, sticky="nsew")

    # Header พร้อมโลโก้
    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")
    try:
        logo_img = Image.open("logo-login.png").resize((120, 120))
        logo_photo = ImageTk.PhotoImage(logo_img)
        ctk.CTkLabel(header, image=logo_photo, text="").pack(side="left", padx=40, pady=10)
    except:
        ctk.CTkLabel(header, text="HTC", font=("Arial Black",52), text_color="white").pack(side="left", padx=40)

    ctk.CTkLabel(header, text="HTC Smart Hub", font=("Arial Black",52), text_color="white").pack(side="left", padx=100, pady=20)

    # ปุ่มไมค์ลอย
    float_frame = ctk.CTkFrame(frame, fg_color="#7b2ff7", corner_radius=18, width=220, height=180)
    float_frame.place(relx=0.01, rely=0.4, anchor="w")
    try:
        mic_img = Image.open("mic1.png").resize((120,120))
        mic_photo = ImageTk.PhotoImage(mic_img)
        mic_label = ctk.CTkLabel(float_frame, image=mic_photo, text="")
        mic_label.image = mic_photo
        mic_label.pack(pady=(8,4))
    except:
        mic_label = ctk.CTkLabel(float_frame, text="🎤", font=("Arial",36))
        mic_label.pack(pady=(8,4))
    ctk.CTkLabel(float_frame, text="กรุณาพูด\nแผนกที่ท่านต้องการ", font=("Arial",16), text_color="white", justify="center").pack()
    float_frame.bind("<Button-1>", lambda e: threading.Thread(target=listen_once, daemon=True).start())
    mic_label.bind("<Button-1>", lambda e: threading.Thread(target=listen_once, daemon=True).start())

    return frame

# ---------- หน้าแผนก ----------
def create_department_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")
    ctk.CTkLabel(frame, text="แผนกวิชา 🧰", font=("Arial Black",48), text_color="#5b00a0").pack(pady=30)

    scroll = ctk.CTkScrollableFrame(frame, width=950, height=800)
    scroll.pack(pady=20)
    for name in departments.keys():
        btn = ctk.CTkButton(scroll, text=f"แผนก{name}", width=700, height=80, font=("Arial",28,"bold"),
                            fg_color="#7131e2", hover_color="#7b30ea", corner_radius=40,
                            command=lambda n=name: show_frame(image_pages_department[n], f"แผนก{n}"))
        btn.pack(pady=10)
    return frame

# ========================================================================
# เริ่มโปรแกรม
# ========================================================================
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)

# สร้าง frames
main_frame = create_main_menu(root)
department_frame = create_department_page(root)
image_pages_department = {
    n: create_image_page(root, n, v[0], v[1], v[2], v[3])
    for n,v in departments.items()
}

main_frame.tkraise()

# Start continuous listening
threading.Thread(target=listen_continuously, daemon=True).start()

root.mainloop()
