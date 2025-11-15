import customtkinter as ctk
from PIL import Image, ImageTk
import time
import threading

# ---------- ตั้งค่าธีม ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- ขนาดหน้าจอ ----------
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920

# ---------- ฟังก์ชันเปลี่ยนหน้า ----------
def show_frame(frame):
    frame.tkraise()


# ---------- Splash Screen ----------
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

    ctk.CTkLabel(splash, text="กำลังโหลดระบบ...", font=("Arial", 36, "bold"), text_color="white").pack(pady=20)
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

    # รูปหลัก
    try:
        img = Image.open(img_path).resize((900, 600))
        photo = ImageTk.PhotoImage(img)
        ctk.CTkLabel(content, image=photo, text="").pack(pady=20)
        frame.image = photo
    except:
        ctk.CTkLabel(content, text="(ไม่พบรูปภาพหลัก)", font=("Arial", 30), text_color="gray").pack(pady=30)

    # รูปแผนที่
    ctk.CTkLabel(content, text="🗺️ แผนที่ตำแหน่งห้อง / แผนก", font=("Arial", 34, "bold"), text_color="#5b00a0").pack(pady=20)
    try:
        map_img = Image.open(map_path).resize((900, 600))
        map_photo = ImageTk.PhotoImage(map_img)
        ctk.CTkLabel(content, image=map_photo, text="").pack(pady=20)
        frame.map_image = map_photo
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

    # Header
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

    # ภาพ FF.png
    try:
        ff_img = Image.open("FF.png").resize((950, 400))
        ff_photo = ImageTk.PhotoImage(ff_img)
        ff_label = ctk.CTkLabel(frame, image=ff_photo, text="")
        ff_label.image = ff_photo
        ff_label.pack(pady=30)
    except:
        ctk.CTkLabel(frame, text="(รอใส่ภาพ FF.png)", text_color="#7a1cff", font=("Arial", 28)).pack(pady=20)
    try:
        Map2_img = Image.open("Map2.png").resize((700, 400))
        Map2_photo = ImageTk.PhotoImage(Map2_img)
        Map2_label = ctk.CTkLabel(frame, image=Map2_photo, text="")
        Map2_label.image = Map2_photo
        Map2_label.pack(pady=30)
    except:
        ctk.CTkLabel(frame, text="(รอใส่ภาพ Map2.png)", text_color="#7a1cff", font=("Arial", 28)).pack(pady=20)

    # ปุ่มเมนู
    ctk.CTkButton(frame, text="ฝ่ายอำนวยการ 🏢", width=400, height=100,
                  font=("Arial", 36, "bold"), fg_color="#7b2ff7", hover_color="#8f47ff",
                  corner_radius=40, command=lambda: show_frame(office_frame)).pack(pady=30)
    ctk.CTkButton(frame, text="แผนกวิชา 🧰", width=400, height=100,
                  font=("Arial", 36, "bold"), fg_color="#712df0", hover_color="#8438f9",
                  corner_radius=40, command=lambda: show_frame(department_frame)).pack(pady=30)

    # Footer ชิดล่าง
    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")
    ctk.CTkLabel(footer, text="© 2025 HTC Smart Hub", text_color="white", font=("Arial", 22)).pack(pady=15)
    return frame


# ---------- หน้า “ฝ่ายอำนวยการ” ----------
def create_office_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")
    ctk.CTkLabel(frame, text="ฝ่ายอำนวยการ 🧑‍💼", font=("Arial Black", 48), text_color="#7c02f7").pack(pady=40)

    scroll = ctk.CTkScrollableFrame(frame, width=950, height=1300)
    scroll.pack(pady=20)

    for name in offices.keys():
        btn = ctk.CTkButton(scroll, text=name, width=700, height=90,
                            font=("Arial", 30, "bold"), fg_color="#7b43ec", hover_color="#9a5cff",
                            corner_radius=40, command=lambda n=name: show_frame(image_pages_office[n]))
        btn.pack(pady=10)

    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")
    ctk.CTkButton(footer, text="↩ กลับ", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white", text_color="#7a1cff",
                  hover_color="#ddd", command=lambda: show_frame(main_frame)).pack(pady=20)
    return frame


# ---------- หน้า “แผนกวิชา” ----------
def create_department_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")
    ctk.CTkLabel(frame, text="แผนกวิชา 🧰", font=("Arial Black", 48), text_color="#5b00a0").pack(pady=30)

    scroll = ctk.CTkScrollableFrame(frame, width=950, height=1300)
    scroll.pack(pady=20)

    for name in departments.keys():
        btn = ctk.CTkButton(scroll, text=f"แผนกวิชา{name}", width=700, height=80,
                            font=("Arial", 28, "bold"), fg_color="#7131e2", hover_color="#7b30ea",
                            corner_radius=40, command=lambda n=name: show_frame(image_pages_department[n]))
        btn.pack(pady=10)

    footer = ctk.CTkFrame(frame, fg_color="#8c52ff", corner_radius=0)
    footer.pack(side="bottom", fill="x")
    ctk.CTkButton(footer, text="↩ กลับ", width=300, height=70,
                  font=("Arial", 28, "bold"), fg_color="white", text_color="#7a1cff",
                  hover_color="#ddd", command=lambda: show_frame(main_frame)).pack(pady=20)
    return frame


# ---------- เริ่มต้น ----------
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


# ✅ ฝ่ายอำนวยการ
offices = {
    "ห้องการเงิน": ("abc.jpg", "M4.png"),
    "ห้องงานทะเบียน": ("ab.jpg", "M6.png"),
    "ห้องงานบุคลากร": ("a1.jpg", "M2.png"),
    "ห้องงานการบัญชี": ("a3.jpg", "M3.png"),
    "ห้องงานอาชีวศึกษาระบบทวิภาคี": ("a9.jpg", "M5.png"),
    "ห้องงานพัฒนาหลักสูตร": ("a11.jpg", "M1.png"),
    "ห้องงานวางแผนและงบประมาณ": ("a3.jpg", "M3.png"),
    "ห้องงานรองผู้อำนวยการแผนและความร่วมมือ": ("a4.jpg", "M1.png"),
    "ห้องรองผู้อำนวยการฝ่ายกิจการนักเรียน นักศึกษา": ("a5.jpg", "M4.png"),
    "ห้องรองผู้อำนวยการฝ่ายวิชาการ": ("a6.jpg", "M4.png"),
    "ห้องรองผู้อำนวยการฝ่ายบริหารทรัพยากร": ("a7.jpg", "M5.png"),
}

# ✅ แผนกวิชา
departments = {
    "ช่างก่อสร้าง": ("B11.jpg", "E3.png"),
    "ช่างโยธา": ("B9.jpg", "E3.png"),
    "ช่างเครื่องเรือนและตกแต่งภายใน": ("B12.jpg", "E12.png"),
    "ช่างสำรวจ": ("B6.jpg", "E2.png"),
    "สถาปัตยกรรม": ("B6.jpg", "E2.png"),
    "ช่างยนต์": ("B16.jpg", "m55.png"),
    "ช่างกลโรงงาน": ("B16.jpg", "E5.png"),
    "ช่างเชื่อมโลหะ": ("B17.jpg", "E8.png"),
    "ช่างเทคนิคพื้นฐาน": ("B1.jpg", "E15.png"),
    "ช่างไฟฟ้า": ("B10.jpg", "E6.png"),
    "ช่างอิเล็กทรอนิกส์": ("B8.jpg", "E1.png"),
    "เครื่องทำความเย็นและปรับอากาศ": ("B2.jpg", "E14.png"),
    "เทคโนโลยีสารสนเทศ": ("B13.jpg", "E5.png"),
    "สามัญสัมพันธ์": ("B4.jpg", "E33.png"),
    "เทคโนโลยีปิโตรเลียม": ("B11.jpg", "E11.png"),
    "เทคนิคพลังงาน": ("B3.jpg", "E10.png"),
    "การจัดการโลจิสติกส์ซัพพลายเชน": ("B3.jpg", "E10.png"),
    "เทคนิคควบคุมระบบขนส่งทางราง": ("B14.jpg", "E13.png"),
    "เมคคาทรอนิกส์และหุ่นยนต์": ("B3.1.jpg", "E10.png"),
}

# ---------- สร้างหน้า ----------
main_frame = create_main_menu(root)
office_frame = create_office_page(root)
department_frame = create_department_page(root)
image_pages_office = {n: create_image_page(root, n, v[0], v[1], office_frame) for n, v in offices.items()}
image_pages_department = {n: create_image_page(root, f"แผนกวิชา{n}", v[0], v[1], department_frame) for n, v in departments.items()}
splash = splash_screen(root)

show_frame(splash)
root.mainloop()