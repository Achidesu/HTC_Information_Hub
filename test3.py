import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import time, threading
import speech_recognition as sr
import pyttsx3
import pygame

# ---------- ตั้งค่าธีม ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- ขนาดหน้าจอ ----------
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920

# ---------- ตั้งค่าเสียง ----------
pygame.mixer.init()
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)
tts_lock = threading.Lock()


def speak(text):
    def run():
        with tts_lock:
            tts_engine.say(text)
            tts_engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()


# ========================================================================
#      ระบบไมค์เปิดตลอดเวลา (Continuous Listening)
# ========================================================================

def handle_voice_command(command):
    cmd = command.replace("แผนก", "").replace("วิชา", "").strip()

    if "กลับ" in cmd or "หน้าหลัก" in cmd:
        show_frame(main_frame, "หน้าหลัก")
        return

    for name, (img, mp, dist, walk_time) in departments.items():
        if cmd in name or cmd in shortcuts.get(name, []):
            show_frame(image_pages_department[name], f"แผนก{name}")

            speak(f"แผนก{name} อยู่ห่างจากที่นี่ {dist} เมตร ใช้เวลาเดินประมาณ {walk_time} นาที")
            return

    speak("ไม่พบชื่อแผนกที่คุณพูดค่ะ")


def listen_continuously():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)

    while True:
        try:
            with sr.Microphone() as source:
                audio = r.listen(source, phrase_time_limit=4)

            command = r.recognize_google(audio, language="th-TH")
            handle_voice_command(command)

        except:
            continue


# ========================================================================
#                 ระบบฟังก์ชัน UI ต่างๆ เดิมทั้งหมด
# ========================================================================

def show_frame(frame, title=None):
    frame.tkraise()
    if title:
        speak(f"เปิดหน้า {title}")


def splash_screen(root):
    splash = ctk.CTkFrame(root, fg_color="#7a1cff")
    splash.grid(row=0, column=0, sticky="nsew")

    try:
        logo_img = Image.open("logo-login.png").resize((300, 300))
        logo_photo = ImageTk.PhotoImage(logo_img)
        label_logo = ctk.CTkLabel(splash, image=logo_photo, text="")
        label_logo.image = logo_photo
        label_logo.pack(pady=100)
    except:
        ctk.CTkLabel(splash, text="HTC", font=("Arial Black", 80), text_color="white").pack(pady=150)

    ctk.CTkLabel(splash, text="กำลังโหลดระบบ...", font=("Arial", 36, "bold"),
                 text_color="white").pack(pady=20)
    progress = ctk.CTkProgressBar(splash, width=500, progress_color="#cbb8ff")
    progress.set(0)
    progress.pack(pady=50)

    def loading():
        for i in range(101):
            time.sleep(0.02)
            progress.set(i / 100)
        show_frame(main_frame)

    threading.Thread(target=loading, daemon=True).start()
    return splash


class AnimatedGIF(ctk.CTkLabel):
    def __init__(self, master, path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        try:
            self.frames = [ImageTk.PhotoImage(img.copy().resize((900, 600)))
                           for img in ImageSequence.Iterator(Image.open(path))]
            self.delay = 100
            self.idx = 0
            self.after(self.delay, self.animate)
        except:
            self.frames = []

    def animate(self):
        if not self.frames:
            return
        self.configure(image=self.frames[self.idx])
        self.idx = (self.idx + 1) % len(self.frames)
        self.after(self.delay, self.animate)


def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("กรุณาพูดชื่อแผนกวิชาหรือฝ่ายอำนวยที่ท่านต้องการ")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=7, phrase_time_limit=5)
            command = r.recognize_google(audio, language="th-TH")
        except:
            speak("กรุณาพูดใหม่อีกครั้งค่ะ")
            return

    handle_voice_command(command)


def create_image_page(root, title, img_path, map_path, distance, walk_time, back_to):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")

    ctk.CTkLabel(header, text=title, text_color="white",
                 font=("Arial Black", 46)).pack(pady=25)

    content = ctk.CTkFrame(frame, fg_color="white")
    content.pack(pady=10)

    try:
        img = Image.open(img_path).resize((900, 600))
        photo = ImageTk.PhotoImage(img)
        ctk.CTkLabel(content, image=photo, text="").pack(pady=20)
        frame.image = photo
    except:
        ctk.CTkLabel(content, text="(ไม่พบรูปภาพหลัก)",
                     font=("Arial", 30), text_color="gray").pack(pady=30)

    try:
        if map_path.lower().endswith(".gif"):
            gif = AnimatedGIF(content, map_path)
            gif.pack()
        else:
            map_img = Image.open(map_path).resize((900, 600))
            map_photo = ImageTk.PhotoImage(map_img)
            ctk.CTkLabel(content, image=map_photo, text="").pack()
            frame.map_image = map_photo
    except:
        ctk.CTkLabel(content, text="(ไม่พบแผนที่)",
                     font=("Arial", 28), text_color="gray").pack(pady=20)

    ctk.CTkLabel(content, text=f"📏 ระยะทาง: {distance} เมตร",
                 font=("Arial", 28)).pack(pady=(20, 5))

    ctk.CTkLabel(content, text=f"⏱️ เวลาเดินประมาณ: {walk_time} นาที",
                 font=("Arial", 28)).pack(pady=(0, 20))

    return frame


def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="#efeaff")
    frame.grid(row=0, column=0, sticky="nsew")

    return frame


# ---------- ข้อมูลแผนก ----------
departments = {
    "ช่างก่อสร้าง": ("B11.jpg", "s2.gif", 120, 3),
    "ช่างโยธา": ("B9.jpg", "s2.gif", 150, 4),
    "เทคโนโลยีสารสนเทศ": ("B13.jpg", "s6.gif", 170, 4),
}

# ---------- คำย่อ ----------
shortcuts = {
    "เทคโนโลยีสารสนเทศ": ["ไอที", "สารสนเทศ"],
    "ช่างก่อสร้าง": ["ก่อสร้าง"],
    "ช่างโยธา": ["โยธา"],
}


# ========================================================================
#                       เริ่มต้นโปรแกรม (ส่วนสำคัญ)
# ========================================================================

root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

main_frame = create_main_menu(root)

image_pages_department = {
    n: create_image_page(root, f"แผนก{n}", v[0], v[1], v[2], v[3], main_frame)
    for n, v in departments.items()
}

splash = splash_screen(root)
show_frame(splash)

threading.Thread(target=listen_continuously, daemon=True).start()

root.mainloop()
