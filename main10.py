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
    cmd = command.replace("แผนก", "").strip()

    if "กลับ" in cmd or "หน้าหลัก" in cmd:
        show_frame(main_frame, "หน้าหลัก")
        return

    for name, (img, mp, _, _) in departments.items():
        if cmd in name or cmd in shortcuts.get(name, []):
            show_frame(image_pages_department[name], f"แผนก{name}")
            return

    speak("ไม่พบชื่อแผนก")


def listen_continuously():
    r = sr.Recognizer()

    # เตรียมไมค์ครั้งแรก
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)

    while True:
        try:
            with sr.Microphone() as source:
                print("🎤 กำลังฟังเสียงตลอดเวลา…")
                audio = r.listen(source, phrase_time_limit=4)

            command = r.recognize_google(audio, language="th-TH")
            print("ได้ยินว่า:", command)

            handle_voice_command(command)

        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            print("❌ ใช้ Google ไม่ได้")
            continue
        except Exception as e:
            print("Error:", e)
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
        super().__init__(master, *args, **kwargs,text="")
        try:
            self.frames = [ImageTk.PhotoImage(img.copy().resize((900, 600)))
                           for img in ImageSequence.Iterator(Image.open(path))]
            self.delay = 100
            self.idx = 0
            self.after(self.delay, self.animate)
        except Exception as e:
            print(f"ไม่สามารถโหลด GIF: {path} -> {e}")
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
        speak("กรุณาพูดชื่อแผนก หรือพูดว่า กลับหน้าหลัก เพื่อย้อนกลับ")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=7, phrase_time_limit=5)
            command = r.recognize_google(audio, language="th-TH")
            speak(f"ได้ยินว่า {command}")
        except sr.WaitTimeoutError:
            speak("ไม่ได้ยินเสียง กรุณาลองใหม่อีกครั้ง")
            return
        except sr.UnknownValueError:
            speak("ขอโทษค่ะ ไม่เข้าใจเสียง กรุณาพูดอีกครั้ง")
            return
        except sr.RequestError:
            speak("ไม่สามารถเชื่อมต่อระบบรู้จำเสียงได้")
            return

    handle_voice_command(command)


def create_image_page(root, title, img_path, map_path, distance, walk_time, back_to):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")

    try:
        logo_img = Image.open("logo-login.png").resize((90, 90))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(header, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=25, pady=10)
    except:
        pass

    ctk.CTkLabel(header, text=title, text_color="white",
                 font=("Arial Black", 46)).pack(pady=25, padx=50, side="left")

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

    ctk.CTkLabel(content, text="🗺️ แผนที่ตำแหน่งห้อง / แผนก",
                 font=("Arial", 34, "bold"), text_color="#5b00a0").pack(pady=20)

    map_container = ctk.CTkFrame(content, fg_color="white")
    map_container.pack(pady=10)

    if map_path.lower().endswith(".gif"):
        gif = AnimatedGIF(map_container, map_path)
        gif.pack()
    else:
        try:
            map_img = Image.open(map_path).resize((900, 600))
            map_photo = ImageTk.PhotoImage(map_img)
            ctk.CTkLabel(map_container, image=map_photo, text="").pack()
            frame.map_image = map_photo
        except:
            ctk.CTkLabel(map_container, text="(ไม่พบแผนที่)",
                         font=("Arial", 28), text_color="gray").pack(pady=20)

    ctk.CTkLabel(content, text=f"📏 ระยะทาง: {distance} เมตร",
                 font=("Arial", 28), text_color="#333").pack(pady=(20, 5))
    ctk.CTkLabel(content, text=f"⏱️ เวลาเดินโดยประมาณ: {walk_time} นาที",
                 font=("Arial", 28), text_color="#333").pack(pady=(0, 20))

    ctk.CTkButton(frame, text="🎤 พูดกลับหน้าหลักหรือเปลี่ยนแผนก",
                  width=500, height=100, font=("Arial", 28, "bold"),
                  fg_color="#7b2ff7", hover_color="#8f47ff",
                  corner_radius=40,
                  command=lambda: threading.Thread(target=listen_for_command,
                                                   daemon=True).start()).pack(pady=20)

    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")

    ctk.CTkButton(footer, text="↩ กลับ", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white", text_color="#7a1cff",
                  hover_color="#ddd", command=lambda: show_frame(back_to)).pack(side="left", padx=100, pady=15)

    ctk.CTkButton(footer, text="🏠 หน้าหลัก", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white", text_color="#7a1cff",
                  hover_color="#ddd", command=lambda: show_frame(main_frame)).pack(side="right", padx=100, pady=15)

    return frame


def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="#efeaff")
    frame.grid(row=0, column=0, sticky="nsew")

    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")

    try:
        logo_img = Image.open("logo-login.png").resize((120, 120))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(header, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=40, pady=10)
    except:
        pass

    title_label = ctk.CTkLabel(header, text="HTC Smart Hub",
                               text_color="white", font=("Arial Black", 52))
    title_label.pack(pady=20, padx=100, side="left")

    try:
        ff_img = Image.open("FF.png").resize((950, 400))
        ff_photo = ImageTk.PhotoImage(ff_img)
        ff_label = ctk.CTkLabel(frame, image=ff_photo, text="")
        ff_label.image = ff_photo
        ff_label.pack(pady=30)
    except:
        pass

    try:
        gif_anim = AnimatedGIF(frame, "s00.gif")
        gif_anim.pack(pady=10)
    except:
        ctk.CTkLabel(frame, text="(s00.gif)",
                     font=("Arial", 20), text_color="gray").pack(pady=20)

    mic_btn = ctk.CTkButton(frame, text="🎤 สั่งด้วยเสียง (พูดชื่อแผนก)",
                            width=500, height=120, font=("Arial", 36, "bold"),
                            fg_color="#7b2ff7", hover_color="#8f47ff",
                            corner_radius=50,
                            command=lambda: threading.Thread(target=listen_for_command,
                                                             daemon=True).start())
    mic_btn.pack(pady=30)

    ctk.CTkButton(frame, text="🧰 แผนกวิชา", width=400, height=100,
                  font=("Arial", 36, "bold"), fg_color="#712df0",
                  hover_color="#8438f9", corner_radius=40,
                  command=lambda: show_frame(department_frame)).pack(pady=30)

    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")

    ctk.CTkLabel(footer, text="© 2025 HTC Smart Hub",
                 text_color="white", font=("Arial", 22)).pack(pady=15)

    return frame


def create_department_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(frame, text="แผนกวิชา 🧰",
                 font=("Arial Black", 48), text_color="#5b00a0").pack(pady=30)

    scroll = ctk.CTkScrollableFrame(frame, width=950, height=1300)
    scroll.pack(pady=20)

    for name in departments.keys():
        btn = ctk.CTkButton(scroll, text=f"แผนก{name}",
                            width=700, height=80, font=("Arial", 28, "bold"),
                            fg_color="#7131e2", hover_color="#7b30ea",
                            corner_radius=40,
                            command=lambda n=name: show_frame(image_pages_department[n],
                                                              f"แผนก{n}"))
        btn.pack(pady=10)

    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")

    ctk.CTkButton(footer, text="↩ กลับ", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white",
                  text_color="#7a1cff", hover_color="#ddd",
                  command=lambda: show_frame(main_frame)).pack(pady=20)

    return frame


# ---------- ข้อมูลแผนก ----------
departments = {
    "ช่างก่อสร้าง": ("B11.jpg", "s2.gif", 120, 3),
    "ช่างโยธา": ("B9.jpg", "s2.gif", 150, 4),
    "ช่างเฟอร์นิเจอร์และตกแต่งภายใน": ("B12.jpg", "s14.gif", 180, 5),
    "ช่างสำรวจ": ("B6.jpg", "s8.gif", 200, 6),
    "สถาปัตยกรรม": ("B6.jpg", "s8.gif", 200, 6),
    "ช่างยนต์": ("B15.jpg", "s5.gif", 100, 3),
    "ช่างกลโรงงาน": ("B16.jpg", "s6.gif", 90, 2),
    "ช่างเชื่อมโลหะ": ("B17.jpg", "s9.gif", 110, 3),
    "ช่างเทคนิคพื้นฐาน": ("B1.jpg", "s12.gif", 130, 3),
    "ช่างไฟฟ้า": ("B10.jpg", "s2.gif", 140, 4),
    "ช่างอิเล็กทรอนิกส์": ("B8.jpg", "s1.gif", 160, 4),
    "เครื่องทำความเย็นและปรับอากาศ": ("B2.jpg", "s10.gif", 180, 5),
    "เทคโนโลยีสารสนเทศ": ("B13.jpg", "s6.gif", 170, 4),
    "เทคโนโลยีปิโตรเลียม": ("B88.jpg", "s11.gif", 190, 5),
    "เทคนิคพลังงาน": ("B3.jpg", "s7.gif", 200, 6),
    "การจัดการโลจิสติกส์ซัพพลายเชน": ("s15.jpeg", "s13.gif", 160, 4),
    "เทคนิคควบคุมระบบขนส่งทางราง": ("B14.jpg", "s4.gif", 210, 6),
    "เมคคาทรอนิกส์และหุ่นยนต์": ("B3.1.jpg", "s7.gif", 200, 5),
    "แผนกการบิน": ("s15.jpeg", "s13.gif", 160, 4),
}

# ---------- คำย่อ ----------
shortcuts = {
    "ช่างอิเล็กทรอนิกส์": ["อิเล็ก", "อิเล็กทรอนิกส์"],
    "ช่างไฟฟ้า": ["ไฟฟ้า"],
    "ช่างยนต์": ["ยนต์", "ช่างยนต์"],
    "เทคโนโลยีสารสนเทศ": ["ไอที", "สารสนเทศ", "เทคโนโลยี"],
    "เมคคาทรอนิกส์และหุ่นยนต์": ["เมคคา", "หุ่นยนต์", "แม็กคา", "แม็คคา", "แมคคา","แมกคา","แม็กคา"],
    "การจัดการโลจิสติกส์ซัพพลายเชน": ["โลจิสติกส์", "ซัพพลายเชน"],
    "ช่างกลโรงงาน": ["กล", "กลโรงงาน"],
    "ช่างเชื่อมโลหะ": ["เชื่อม", "โลหะ"],
    "ช่างก่อสร้าง": ["ก่อสร้าง"],
    "สถาปัตยกรรม": ["สถาปัตย์"],
    "แผนกการบิน": ["การบิน"],
}


# ========================================================================
#                       เริ่มต้นโปรแกรม
# ========================================================================

root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


main_frame = create_main_menu(root)
department_frame = create_department_page(root)
image_pages_department = {
    n: create_image_page(root, f"แผนก{n}", v[0], v[1], v[2], v[3], department_frame)
    for n, v in departments.items()
}

splash = splash_screen(root)

show_frame(splash)


# ---------- เริ่มไมค์ฟังตลอดเวลา ----------
threading.Thread(target=listen_continuously, daemon=True).start()

root.mainloop()
