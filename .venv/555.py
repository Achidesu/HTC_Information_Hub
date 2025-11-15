import customtkinter as ctk
from PIL import Image, ImageTk
from itertools import count

# ---------- ตั้งค่าธีม ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- ขนาดหน้าจอ ----------
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920

# ---------- ฟังก์ชันเปลี่ยนหน้า ----------
def show_frame(frame):
    frame.tkraise()

# ---------- ฟังก์ชันเล่น GIF ----------
def play_gif(label, gif_path):
    try:
        gif = Image.open(gif_path)
    except Exception as e:
        print(f"ไม่สามารถเปิด {gif_path}: {e}")
        return

    frames = []
    try:
        for i in count(0):
            frames.append(ImageTk.PhotoImage(gif.copy().convert("RGBA").resize((900, 600))))
            gif.seek(i + 1)
    except EOFError:
        pass

    def update(idx=0):
        if not frames:
            return
        label.configure(image=frames[idx])
        label.image = frames[idx]
        label.after(100, update, (idx + 1) % len(frames))
    label.after(0, update)

# ---------- Splash Screen ----------
def splash_screen(root, next_frame):
    splash = ctk.CTkFrame(root, fg_color="#7a1cff")
    splash.grid(row=0, column=0, sticky="nsew")

    # โลโก้
    try:
        logo_img = Image.open("logo-login.png").resize((300, 300))
        logo_photo = ImageTk.PhotoImage(logo_img)
        label_logo = ctk.CTkLabel(splash, image=logo_photo, text="")
        label_logo.image = logo_photo
        label_logo.pack(pady=100)
    except:
        ctk.CTkLabel(splash, text="HTC", font=("Arial Black", 80), text_color="white").pack(pady=150)

    ctk.CTkLabel(splash, text="กำลังโหลดระบบ...", font=("Arial", 36, "bold"), text_color="white").pack(pady=20)

    progress = ctk.CTkProgressBar(splash, width=500, progress_color="#cbb8ff")
    progress.set(0)
    progress.pack(pady=50)

    # โหลด progress ด้วย after
    def loading(i=0):
        if i > 100:
            show_frame(next_frame)
            return
        progress.set(i / 100)
        root.after(20, lambda: loading(i + 1))
    root.after(100, lambda: loading())

    return splash

# ---------- ฟังก์ชันสร้างหน้าแสดงรูป + แผนที่ ----------
def create_image_page(root, title, img_path, map_path, back_to):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    # ===== ส่วนหัว =====
    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")
    try:
        logo_img = Image.open("logo-login.png").resize((80, 80))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(header, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=30, pady=10)
    except:
        pass
    ctk.CTkLabel(header, text=title, text_color="white", font=("Arial Black", 46)).pack(pady=25)

    content = ctk.CTkScrollableFrame(frame, width=950, height=1200, fg_color="white")
    content.pack(pady=10)

    # ===== รูปหลัก =====
    try:
        img = Image.open(img_path).resize((900, 600))
        photo = ImageTk.PhotoImage(img)
        ctk.CTkLabel(content, image=photo, text="").pack(pady=20)
        frame.image = photo
    except:
        ctk.CTkLabel(content, text="(ไม่พบรูปภาพหลัก)", font=("Arial", 30), text_color="gray").pack(pady=30)

    # ===== แผนที่แบบ GIF =====
    ctk.CTkLabel(content, text="🗺️ แผนที่ตำแหน่งห้อง / แผนก", font=("Arial", 34, "bold"), text_color="#5b00a0").pack(pady=20)
    try:
        map_label = ctk.CTkLabel(content, text="")
        map_label.pack(pady=20)
        play_gif(map_label, map_path)
    except:
        ctk.CTkLabel(content, text="(ไม่พบแผนที่)", font=("Arial", 28), text_color="gray").pack(pady=20)

    # ===== แถบล่าง =====
    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")
    ctk.CTkButton(footer, text="↩ กลับ", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white", text_color="#7a1cff",
                  hover_color="#ddd", command=lambda: show_frame(back_to)).pack(side="left", padx=100, pady=15)
    ctk.CTkButton(footer, text="🏠 หน้าหลัก", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white", text_color="#7a1cff",
                  hover_color="#ddd", command=lambda: show_frame(main_frame)).pack(side="right", padx=100, pady=15)

    return frame

# ---------- ส่วนเมนูหลัก ----------
def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="#efeaff")
    frame.grid(row=0, column=0, sticky="nsew")

    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")
    try:
        logo_img = Image.open("logo-login.png").resize((150, 150))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(header, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=40, pady=20)
    except:
        ctk.CTkLabel(header, text="[โลโก้]", text_color="white", font=("Arial", 32)).pack(side="left", padx=40)
    ctk.CTkLabel(header, text="HTC Smart Hub", text_color="white", font=("Arial Black", 52)).pack(side="right", padx=60, pady=20)

    # ตัวอย่างภาพ FF.png
    try:
        ff_img = Image.open("FF.png").resize((950, 400))
        ff_photo = ImageTk.PhotoImage(ff_img)
        ff_label = ctk.CTkLabel(frame, image=ff_photo, text="")
        ff_label.image = ff_photo
        ff_label.pack(pady=30)
    except:
        ctk.CTkLabel(frame, text="(รอใส่ภาพ FF.png)", text_color="#7a1cff", font=("Arial", 28)).pack(pady=20)

    # ตัวอย่างแผนที่ Map2.png
    try:
        Map2_img = Image.open("Map2.png").resize((700, 400))
        Map2_photo = ImageTk.PhotoImage(Map2_img)
        Map2_label = ctk.CTkLabel(frame, image=Map2_photo, text="")
        Map2_label.image = Map2_photo
        Map2_label.pack(pady=30)
    except:
        ctk.CTkLabel(frame, text="(รอใส่ภาพ Map2.png)", text_color="#7a1cff", font=("Arial", 28)).pack(pady=20)

    return frame

# ---------- ตัวอย่างข้อมูล Office / Department ----------
offices = {
    "ห้องการเงิน": ("abc.jpg", "G14.gif"),
    "ห้องงานทะเบียน": ("ab.jpg", "G15.gif"),
}

departments = {
    "ช่างก่อสร้าง": ("B11.jpg", "G5.gif"),
    "ช่างโยธา": ("B9.jpg", "G5.gif"),
}

# ---------- เริ่มต้นระบบ ----------
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# ---------- สร้างหน้าหลัก ----------
main_frame = create_main_menu(root)

# ---------- สร้าง splash screen ----------
splash = splash_screen(root, main_frame)

# ---------- แสดง splash screen ก่อน main menu ----------
show_frame(splash)
root.mainloop()
