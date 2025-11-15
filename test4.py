# htc_smart_hub_with_continuous_mic.py
from cProfile import label
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import time, threading, tempfile, os
import speech_recognition as sr
from gtts import gTTS
import pygame

# ---------- ตั้งค่าธีม ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- ขนาดหน้าจอ ----------
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920

# ---------- เตรียม pygame สำหรับเล่นเสียง ----------
pygame.init()
pygame.mixer.init()

# ---------- Main Page (หน้าหลัก) ----------


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
                tts = gTTS(text=text, lang=lang)
                tts.save(tmp_path)

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

# ---------- คำย่อ/shortcuts ----------
shortcuts = {
    "ช่างอิเล็กทรอนิกส์": ["อิเล็ก", "อิเล็กทรอนิกส์"],
    "ช่างไฟฟ้า": ["ไฟฟ้า"],
    "ช่างยนต์": ["ยนต์", "ช่างยนต์"],
    "เทคโนโลยีสารสนเทศ": ["ไอที", "สารสนเทศ", "เทคโนโลยี"],
    "เมคคาทรอนิกส์และหุ่นยนต์": ["เมคคา", "หุ่นยนต์"],
    "การจัดการโลจิสติกส์ซัพพลายเชน": ["โลจิสติกส์", "ซัพพลายเชน"],
    "ช่างกลโรงงาน": ["กล", "กลโรงงาน"],
    "ช่างเชื่อมโลหะ": ["เชื่อม", "โลหะ"],
    "ช่างก่อสร้าง": ["ก่อสร้าง"],
    "สถาปัตยกรรม": ["สถาปัตย์"],
    "แผนกการบิน": ["การบิน"],
}

# ---------- ฟังก์ชันเปิดหน้า และพูดชื่อแผนกเมื่อเป็น page แผนก ----------
def show_frame(frame, title=None):
    frame.tkraise()
    # ถ้าเป็นหน้าแผนก ให้พูดชื่อ+ระยะ+เวลา (พูดครั้งเดียวเมื่อเปิดหน้า)
    if title and title.startswith("แผนก"):
        name = title.replace("แผนก", "")
        # ป้องกันกรณีชื่อไม่อยู่ใน dictionary
        info = departments.get(name)
        if info:
            distance = info[2]
            walk_time = info[3]
            speak_tts(f"แผนก {name} ระยะทาง {distance} เมตร เวลาเดินประมาณ {walk_time} นาที")
        else:
            speak_tts(title)
    elif title:
        speak_tts(title)

# ---------- Splash Screen ----------
def splash_screen(root):
    splash = ctk.CTkFrame(root, fg_color="#7a1cff")
    splash.grid(row=0, column=0, sticky="nsew")
    try:
        logo_img = Image.open("logo-login.png").resize((300, 300))
        logo_photo = ImageTk.PhotoImage(logo_img)
        label_logo = ctk.CTkLabel(splash, image=logo_photo, text="")
        label_logo.image = logo_photo
        label_logo.pack(pady=120)
    except:
        ctk.CTkLabel(splash, text="HTC Smart Hub", font=("Arial Black", 60), text_color="white").pack(pady=150)

    ctk.CTkLabel(splash, text="กำลังโหลดระบบ...", font=("Arial", 28, "bold"), text_color="white").pack(pady=10)
    progress = ctk.CTkProgressBar(splash, width=500, progress_color="#cbb8ff")
    progress.set(0)
    progress.pack(pady=20)

    def loading():
        for i in range(101):
            time.sleep(0.01)
            progress.set(i / 100)
        show_frame(main_frame, "หน้าหลัก")

    threading.Thread(target=loading, daemon=True).start()
    return splash

# ---------- Animated GIF helper ----------
class AnimatedGIF(ctk.CTkLabel):
    def __init__(self, master, path, width=900, height=600, delay=100, *args, **kwargs):
        super().__init__(master, *args, **kwargs, text="")
        self.path = path
        self.width = width
        self.height = height
        self.delay = delay
        self.frames = []
        try:
            for img in ImageSequence.Iterator(Image.open(path)):
                frm = img.copy().resize((self.width, self.height))
                self.frames.append(ImageTk.PhotoImage(frm))
        except Exception as e:
            print(f"ไม่สามารถโหลด GIF: {path} -> {e}")
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

# ---------- ฟังก์ชันการประมวลผลคำสั่งเสียง (จาก continuous listener) ----------
def process_command_text(text):
    txt = text.lower().replace("แผนก", "").strip()
    # คำสั่ง 'กลับ' หรือ 'หน้าหลัก'
    if "กลับ" in txt or "หน้าหลัก" in txt:
        root.after(0, lambda: show_frame(main_frame, "หน้าหลัก"))
        return

    # หาแผนกตามชื่อหรือ shortcuts
    for name in departments.keys():
        if name in txt:
            # เปิดหน้า (บน main thread)
            root.after(0, lambda n=name: show_frame(image_pages_department[n], f"แผนก{n}"))
            return
        for s in shortcuts.get(name, []):
            if s in txt:
                root.after(0, lambda n=name: show_frame(image_pages_department[n], f"แผนก{n}"))
                return

    # ถ้าไม่พบ
    speak_tts("ไม่พบชื่อแผนกที่กล่าว กรุณาพูดใหม่")

# ---------- Continuous listening thread (background) ----------
def listen_continuously():
    r = sr.Recognizer()
    # adjust once
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
    except Exception as e:
        print("ไมโครโฟนไม่พร้อมหรือไม่พบอุปกรณ์:", e)

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
                # ไม่เข้าใจ -> ข้าม
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
            speak_tts("กรุณาพูดชื่อแผนกที่ท่านต้องการ")
            r.adjust_for_ambient_noise(source, duration=0.7)
            audio = r.listen(source, timeout=7, phrase_time_limit=5)
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

# ---------- สร้างหน้าแผนก (ไม่มีปุ่ม) ----------
def create_image_page(root, title, img_path, map_path, distance, walk_time, back_to):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    # header
    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")
    try:
        logo_img = Image.open("logo-login.png").resize((90, 90))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(header, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=20, pady=8)
    except:
        pass

    ctk.CTkLabel(header, text=title, text_color="white", font=("Arial Black", 40)).pack(padx=20, pady=12, side="left")

    # content
    content = ctk.CTkFrame(frame, fg_color="white")
    content.pack(pady=10)

    # main image
    try:
        img = Image.open(img_path).resize((900, 600))
        photo = ImageTk.PhotoImage(img)
        img_lbl = ctk.CTkLabel(content, image=photo, text="")
        img_lbl.image = photo
        img_lbl.pack(pady=10)
    except:
        ctk.CTkLabel(content, text="(ไม่พบรูปภาพหลัก)", font=("Arial", 24), text_color="gray").pack(pady=10)

    # map title
    ctk.CTkLabel(content, text="🗺️ แผนที่ตำแหน่งห้อง / แผนก", font=("Arial", 28, "bold"), text_color="#5b00a0").pack(pady=8)

    # map
    map_container = ctk.CTkFrame(content, fg_color="white")
    map_container.pack(pady=6)
    if str(map_path).lower().endswith(".gif"):
        gif = AnimatedGIF(map_container, map_path, width=900, height=600, delay=80)
        gif.pack()
    else:
        try:
            map_img = Image.open(map_path).resize((900, 600))
            map_photo = ImageTk.PhotoImage(map_img)
            map_lbl = ctk.CTkLabel(map_container, image=map_photo, text="")
            map_lbl.image = map_photo
            map_lbl.pack()
        except:
            ctk.CTkLabel(map_container, text="(ไม่พบแผนที่)", font=("Arial", 20), text_color="gray").pack(pady=10)

    # distance/time (แสดงเป็นข้อความด้านล่างแผนที่)
    ctk.CTkLabel(content, text=f"📏 ระยะทาง: {distance} เมตร", font=("Arial", 24), text_color="#333").pack(pady=(16,4))
    ctk.CTkLabel(content, text=f"⏱️ เวลาเดินโดยประมาณ: {walk_time} นาที", font=("Arial", 24), text_color="#333").pack(pady=(0,16))

    # footer (สองแถวด้านล่างจะถูกสร้างที่หน้า main; แต่ยังคง footer เล็ก ๆ เงียบ ๆ ไว้)
    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")
    # ไม่มีปุ่ม — ผู้ใช้ใช้เสียงคำสั่ง "กลับ" เพื่อกลับหน้าหลัก

    return frame

# ---------- หน้าเมนูหลัก (ลบปุ่มทั้งหมด ยกเว้น ไมค์ลอยซ้าย) ----------
def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="#efeaff")
    frame.grid(row=0, column=0, sticky="nsew")

    # header bar
    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")
    try:
        logo_img = Image.open("logo-login.png").resize((120, 120))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(header, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=20, pady=8)
    except:
        pass
    ctk.CTkLabel(header, text="HTC Smart Hub", text_color="white", font=("Arial Black", 40)).pack(side="left", padx=16, pady=12)
    try:
        ff_img = Image.open("FF.png").resize((950, 400))
        ff_photo = ImageTk.PhotoImage(ff_img)
        ff_label = ctk.CTkLabel(frame, image=ff_photo, text="")
        ff_label.image = ff_photo
        ff_label.pack(pady=30)
    except:
        pass
    # s00.gif ขนาดกลาง/ใหญ่
    try:
        gif_anim = AnimatedGIF(frame, "s00.gif", width=1000, height=420, delay=80)
        gif_anim.pack(pady=20)
    except Exception as e:
        print("s00.gif load error:", e)
        ctk.CTkLabel(frame, text="(ไม่พบไฟล์ s00.gif)", font=("Arial", 20), text_color="gray").pack(pady=20)

    # ---------- ไมค์ลอยด้านซ้าย ---------- (ตามที่ขอ)
    float_w = 260
    float_h = 180
    float_frame = ctk.CTkFrame(frame, fg_color="#7b2ff7", corner_radius=18)
    # left side: relx small, anchor west
    float_frame.place(relx=0.02, rely=0.45, anchor="w")

    mic_float_btn = ctk.CTkButton(float_frame, text="🎤", width=80, height=80, font=("Arial", 36, "bold"),
                                  fg_color="white", text_color="#7b2ff7", hover_color="#eee",
                                  corner_radius=40, command=lambda: threading.Thread(target=single_listen_and_process, daemon=True).start())
    mic_float_btn.pack(pady=(10,6))

    mic_hint = ctk.CTkLabel(float_frame, text="กรุณาพูดชื่อ\nแผนกวิชาที่ท่านต้องการ", font=("Arial", 14), text_color="white", justify="center")
    mic_hint.pack()

    # ---------- แถบล่าง 2 ชั้น (stacked footers) ----------
    footer_top = ctk.CTkFrame(frame, fg_color="#6b3fe8", corner_radius=0, height=50)
    footer_top.pack(side="bottom", fill="x")
    footer_label_top = ctk.CTkLabel(footer_top, text="ออกแบบ-เขียน โดย ช่างเทคโนโลยีคอมพิวเตอร์", text_color="white", font=("Arial", 18))
    footer_label_top.pack(pady=8)

    footer_bottom = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0, height=48)
    footer_bottom.pack(side="bottom", fill="x")

    # marquee (running text) in bottom footer
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

    # note: ไม่มีปุ่มเมนู — การนำทางทั้งหมดทำผ่านเสียง (continuous) หรือปุ่มไมค์ลอย

    return frame

# ---------- หน้าแผนก (รายการ) ---------- (ไม่มีปุ่มกด)
def create_department_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(frame, text="รายการแผนก (สั่งด้วยเสียง)", font=("Arial Black", 30), text_color="#5b00a0").pack(pady=30)

    # แสดงรายการเป็น label เท่านั้น (ไม่ใช่ปุ่ม)
    list_frame = ctk.CTkFrame(frame, fg_color="white")
    list_frame.pack(pady=10)
    for name in departments.keys():
        ctk.CTkLabel(list_frame, text=f"• {name}", font=("Arial", 22), text_color="#333").pack(anchor="w", padx=20, pady=6)

    # footer (สองชั้นเหมือนหน้าแรก)
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
# Start application
# ========================================================================

root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# ---------- ปุ่มไมค์ลอย ----------
float_w = 180
float_h = 180

float_frame = ctk.CTkFrame(root, width=float_w, height=float_h)
float_frame.place(relx=0.02, rely=0.45, anchor="w")
# โหลดรูป mic
mic_icon = ctk.CTkImage(
    light_image=Image.open("mic1.png"),
    dark_image=Image.open("mic1.png"),
    size=(32, 32)
)
# create frames
main_frame = create_main_menu(root)
department_frame = create_department_page(root)
image_pages_department = {
    n: create_image_page(root, f"แผนก{n}", v[0], v[1], v[2], v[3], department_frame)
    for n, v in departments.items()
}

splash = splash_screen(root)
show_frame(splash)

# start continuous background listening (daemon thread)
threading.Thread(target=listen_continuously, daemon=True).start()

root.mainloop()
