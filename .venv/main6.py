import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import threading
import time
import speech_recognition as sr
from gtts import gTTS
import pygame
import os

# ---------- ตั้งค่าธีม ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- ขนาดหน้าจอ ----------
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920

# ---------- ฟังก์ชันเสียง ----------
def speak(text):
    """ให้ AI พูดข้อความ"""
    tts = gTTS(text=text, lang="th")
    filename = "voice.mp3"
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

def listen_command():
    """ฟังคำสั่งเสียงจากไมค์"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("กรุณาพูดชื่อแผนกวิชาที่ต้องการเปิด")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio, language="th-TH")
        print(f"คำสั่งเสียง: {command}")
        return command
    except:
        speak("ขออภัย ไม่ได้ยินกรุณาพูดอีกครั้ง")
        return ""

# ---------- ฟังก์ชันเปิดหน้าจอตามเสียง ----------
def process_voice_command(command):
    for name in departments.keys():
        if name in command:
            speak(f"กำลังเปิดแผนกวิชา {name}")
            show_frame(image_pages_department[name])
            return
    speak("ไม่พบชื่อแผนกที่ระบุ")

# ---------- ฟังก์ชันเปลี่ยนหน้า ----------
def show_frame(frame):
    frame.tkraise()

# ---------- Splash Screen ----------
def splash_screen(root):
    splash = ctk.CTkFrame(root, fg_color="#7a1cff")
    splash.grid(row=0, column=0, sticky="nsew")
    ctk.CTkLabel(splash, text="กำลังโหลดระบบ...", font=("Arial", 36, "bold"), text_color="white").pack(pady=250)
    progress = ctk.CTkProgressBar(splash, width=500, progress_color="#cbb8ff")
    progress.set(0)
    progress.pack(pady=50)

    def loading():
        for i in range(101):
            time.sleep(0.02)
            progress.set(i / 100)
        show_frame(main_frame)
        speak("ยินดีต้อนรับสู่ระบบ HTC Smart Hub")

    threading.Thread(target=loading, daemon=True).start()
    return splash

# ---------- ฟังก์ชันเล่นภาพ GIF ----------
class AnimatedGIF(ctk.CTkLabel):
    def __init__(self, master, path, delay=100):
        im = Image.open(path)
        seq = []
        try:
            for frame in ImageSequence.Iterator(im):
                seq.append(ImageTk.PhotoImage(frame.copy().resize((900, 600))))
        except:
            pass
        self.frames = seq
        self.delay = delay
        self.frame_index = 0
        super().__init__(master, image=self.frames[0])
        self.after(self.delay, self.play)

    def play(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.configure(image=self.frames[self.frame_index])
        self.after(self.delay, self.play)

# ---------- ฟังก์ชันสร้างหน้าแสดงรูป + แผนที่ ----------
def create_image_page(root, title, img_path, map_path, back_to):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(frame, text=title, text_color="#5b00a0", font=("Arial Black", 46)).pack(pady=20)
    content = ctk.CTkScrollableFrame(frame, width=950, height=1200, fg_color="white")
    content.pack(pady=10)

    # รูปหลัก
    try:
        if img_path.endswith(".gif"):
            gif_label = AnimatedGIF(content, img_path)
            gif_label.pack(pady=20)
        else:
            img = Image.open(img_path).resize((900, 600))
            photo = ImageTk.PhotoImage(img)
            ctk.CTkLabel(content, image=photo, text="").pack(pady=20)
            frame.image = photo
    except:
        ctk.CTkLabel(content, text="(ไม่พบรูปภาพหลัก)", font=("Arial", 30), text_color="gray").pack(pady=30)

    # รูปแผนที่
    ctk.CTkLabel(content, text="🗺️ แผนที่แผนก", font=("Arial", 34, "bold"), text_color="#5b00a0").pack(pady=20)
    try:
        if map_path.endswith(".gif"):
            gif_map = AnimatedGIF(content, map_path)
            gif_map.pack(pady=20)
        else:
            map_img = Image.open(map_path).resize((900, 600))
            map_photo = ImageTk.PhotoImage(map_img)
            ctk.CTkLabel(content, image=map_photo, text="").pack(pady=20)
            frame.map_image = map_photo
    except:
        ctk.CTkLabel(content, text="(ไม่พบแผนที่)", font=("Arial", 28), text_color="gray").pack(pady=20)

    # แถบล่าง
    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")
    ctk.CTkButton(footer, text="↩ กลับ", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white", text_color="#7a1cff",
                  command=lambda: show_frame(back_to)).pack(side="left", padx=100, pady=15)
    ctk.CTkButton(footer, text="🏠 หน้าหลัก", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white", text_color="#7a1cff",
                  command=lambda: show_frame(main_frame)).pack(side="right", padx=100, pady=15)
    return frame

# ---------- หน้าเมนูหลัก ----------
def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="#efeaff")
    frame.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(frame, text="HTC Smart Hub", text_color="#7a1cff", font=("Arial Black", 64)).pack(pady=60)
    ctk.CTkLabel(frame, text="🎤 ระบบสั่งงานด้วยเสียง", text_color="#7a1cff", font=("Arial", 32)).pack(pady=10)

    # ปุ่มไมค์
    def mic_button_action():
        threading.Thread(target=lambda: process_voice_command(listen_command()), daemon=True).start()

    ctk.CTkButton(frame, text="🎙️ กดพูดเพื่อสั่งงาน", width=400, height=120,
                  font=("Arial", 36, "bold"), fg_color="#7b2ff7", hover_color="#8f47ff",
                  corner_radius=60, command=mic_button_action).pack(pady=100)

    # Footer
    ctk.CTkFrame(frame, fg_color="#8c52ff", height=80).pack(side="bottom", fill="x")
    return frame

# ---------- แผนกวิชา ----------
departments = {
    "ช่างก่อสร้าง": ("B11.jpg", "G5.gif"),
    "ช่างโยธา": ("B9.jpg", "G5.gif"),
    "ช่างเครื่องเรือนและตกแต่งภายใน": ("B12.jpg", "G20.gif"),
    "ช่างสำรวจ": ("B6.jpg", "G4.gif"),
    "สถาปัตยกรรม": ("B6.jpg", "G4.gif"),
    "ช่างยนต์": ("B16.jpg", "G6.gif"),
    "ช่างกลโรงงาน": ("B16.jpg", "G7.gif"),
    "ช่างเชื่อมโลหะ": ("B17.jpg", "G10.gif"),
    "ช่างเทคนิคพื้นฐาน": ("B1.jpg", "G2.gif"),
    "ช่างไฟฟ้า": ("B10.jpg", "G8.gif"),
    "ช่างอิเล็กทรอนิกส์": ("B8.jpg", "G1.gif"),
    "เครื่องทำความเย็นและปรับอากาศ": ("B2.jpg", "G3.gif"),
    "เทคโนโลยีสารสนเทศ": ("B13.jpg", "G7.gif"),
    "สามัญสัมพันธ์": ("B4.jpg", "G21.gif"),
    "เทคโนโลยีปิโตรเลียม": ("B11.jpg", "G12.gif"),
    "เทคนิคพลังงาน": ("B3.jpg", "G11.gif"),
    "การจัดการโลจิสติกส์ซัพพลายเชน": ("B3.jpg", "E10.png"),
    "เทคนิคควบคุมระบบขนส่งทางราง": ("B14.jpg", "G13.gif"),
    "เมคคาทรอนิกส์และหุ่นยนต์": ("B3.1.jpg", "G11.gif"),
    "เทคนิคพื้นฐาน": ("B1.jpg", "G2.gif")
}

# ---------- สร้างหน้า ----------
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

main_frame = create_main_menu(root)
image_pages_department = {n: create_image_page(root, f"แผนกวิชา {n}", v[0], v[1], main_frame) for n, v in departments.items()}
splash = splash_screen(root)

show_frame(splash)
root.mainloop()
