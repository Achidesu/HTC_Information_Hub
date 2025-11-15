from tkinter import Tk
import customtkinter as ctk
from PIL import Image, ImageTk

# ---------- ตั้งค่าธีม ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------- ขนาดหน้าจอ ----------
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920


# ---------- ฟังก์ชันเปลี่ยนหน้า ----------
def show_frame(frame):
    frame.tkraise()


# ---------- สร้างหน้าเนื้อหาย่อย ----------
def create_detail_page(root, title_text, back_frame):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    title = ctk.CTkLabel(frame, text=title_text, font=("Arial Black", 48), text_color="#7c02f7")
    title.pack(pady=40)

    ctk.CTkLabel(
        frame,
        text=f"📘 หน้ารายละเอียดของ {title_text}\n\nสามารถเพิ่มข้อมูล ข้อความ หรือรูปภาพเพิ่มเติมภายหลังได้",
        font=("Arial", 32),
        text_color="#3b3b3b"
    ).pack(pady=60)

    back_btn = ctk.CTkButton(
        frame, text="← กลับ", width=300, height=80,
        font=("Arial", 28, "bold"), fg_color="#6920f9", hover_color="#7023e4",
        command=lambda: show_frame(back_frame)
    )
    back_btn.pack(pady=30)

    home_btn = ctk.CTkButton(
        frame, text="🏠 กลับหน้าหลัก", width=300, height=80,
        font=("Arial", 28, "bold"), fg_color="#6920f9", hover_color="#7023e4",
        command=lambda: show_frame(main_frame)
    )
    home_btn.pack(pady=30)

    return frame


# ---------- หน้าเมนูหลัก ----------
def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    header = ctk.CTkFrame(frame, fg_color="#7a1cff", corner_radius=0)
    header.pack(fill="x")

    # โลโก้
    try:
        logo_img = Image.open("logo-login.png").resize((150, 150))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(header, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=40, pady=20)
    except:
        ctk.CTkLabel(header, text="[โลโก้]", text_color="white", font=("Arial", 32)).pack(side="left", padx=40)

    title_label = ctk.CTkLabel(header, text="HTC Smart Hub", text_color="white", font=("Arial Black", 52))
    title_label.pack(side="right", padx=60, pady=20)

    # ส่วน Facebook
    fb_frame = ctk.CTkFrame(frame, fg_color="white", corner_radius=10)
    fb_frame.pack(pady=30)
    try:
        fb_img = Image.open("FF.png").resize((950, 500))
        fb_photo = ImageTk.PhotoImage(fb_img)
        fb_label = ctk.CTkLabel(fb_frame, image=fb_photo, text="")
        fb_label.image = fb_photo
        fb_label.pack(pady=10)
    except:
        ctk.CTkLabel(fb_frame, text="(รอใส่ภาพ Facebook)", text_color="#7a1cff", font=("Arial", 28)).pack(pady=40)

    # ส่วนแผนที่
    map_frame = ctk.CTkFrame(frame, fg_color="white", corner_radius=10)
    map_frame.pack(pady=20)
    try:
        map_img = Image.open("Map.png").resize((950, 600))
        map_photo = ImageTk.PhotoImage(map_img)
        map_label = ctk.CTkLabel(map_frame, image=map_photo, text="")
        map_label.image = map_photo
        map_label.pack(pady=10)
    except:
        ctk.CTkLabel(map_frame, text="(รอใส่แผนที่)", text_color="#7a1cff", font=("Arial", 28)).pack(pady=40)

    # ปุ่มเมนูหลัก
    button_frame = ctk.CTkFrame(frame, fg_color="white")
    button_frame.pack(pady=50)

    btn_office = ctk.CTkButton(
        button_frame, text="ฝ่ายอำนวยการ 🧑‍💼", width=400, height=100,
        font=("Arial", 36, "bold"), fg_color="#6c26f9", hover_color="#6a19e3",
        command=lambda: show_frame(office_frame)
    )
    btn_office.grid(row=0, column=0, padx=20, pady=20)

    btn_department = ctk.CTkButton(
        button_frame, text="แผนกวิชา 🏫", width=400, height=100,
        font=("Arial", 36, "bold"), fg_color="#7738f6", hover_color="#6b1ce2",
        command=lambda: show_frame(department_frame)
    )
    btn_department.grid(row=1, column=0, padx=20, pady=20)

    return frame


# ---------- หน้า ฝ่ายอำนวยการ ----------
def create_office_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    label = ctk.CTkLabel(frame, text="ฝ่ายอำนวยการ 🧑‍💼", font=("Arial Black", 48), text_color="#7c02f7")
    label.pack(pady=50)

    offices = [
        "ห้องการเงิน💸", "ห้องงานทะเบียน📜", "ห้องงานบุคลากร👩‍🏫", "ห้องงานการบัญชี👩‍💼",
        "ห้องงานวางแผนและงบประมาณ💰", "ห้องงานความร่วมมือ🤝",
        "ห้องรองผู้อำนวยการฝ่ายกิจการพัฒนานักเรียน นักศึกษา🧑‍🎓",
        "ห้องรองผู้อำนวยการฝ่ายวิชาการ👨‍💻", "ห้องรองผู้อำนวยการฝ่ายบริหารทรัพยากร👩‍💻",
        "ห้องงานอาชีวศึกษาระบบทวิภาคี👩‍⚖️👨‍🏫", "ห้องงานพัฒนาหลักสูตรการเรียนการสอน📔"
    ]

    scroll = ctk.CTkScrollableFrame(frame, width=950, height=1300, fg_color="#f5f0ff")
    scroll.pack(pady=20)

    for name in offices:
        btn = ctk.CTkButton(
            scroll, text=name, width=700, height=80,
            font=("Arial", 28, "bold"), fg_color="#7131e2", hover_color="#7b30ea",
            command=lambda n=name: show_frame(office_pages[n])
        )
        btn.pack(pady=10)

    back_btn = ctk.CTkButton(
        frame, text="← กลับหน้าหลัก", width=300, height=80,
        font=("Arial", 28, "bold"), fg_color="#6b27f2", hover_color="#7527ea",
        command=lambda: show_frame(main_frame)
    )
    back_btn.pack(side="bottom", pady=60)

    return frame


# ---------- หน้า แผนกวิชา ----------
def create_department_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    label = ctk.CTkLabel(frame, text="แผนกวิชา 🏫", font=("Arial Black", 48), text_color="#5b00a0")
    label.pack(pady=30)

    departments = [
        "ช่างก่อสร้าง", "ช่างโยธา", "ช่างเครื่องเรือนและตกแต่งภายใน", "ช่างสำรวจ", "สถาปัตยกรรม",
        "ช่างยนต์", "ช่างกลโรงงาน", "ช่างเชื่อมโลหะ", "ช่างเทคนิคพื้นฐาน", "ช่างไฟฟ้า",
        "ช่างอิเล็กทรอนิกส์", "เครื่องทำความเย็นและปรับอากาศ", "เทคโนโลยีสารสนเทศ",
        "สามัญสัมพันธ์", "เทคโนโลยีปิโตรเลียม", "เทคนิคพลังงาน", "การจัดการโลจิสติกส์ซัพพลายเชน",
        "เทคนิคควบคุมระบบขนส่งทางราง", "เมคคาทรอนิกส์และหุ่นยนต์"
    ]

    scroll = ctk.CTkScrollableFrame(frame, width=950, height=1300, fg_color="#7b43ec")
    scroll.pack(pady=20)

    for dep in departments:
        btn = ctk.CTkButton(
            scroll, text=f"แผนกวิชา{dep}", width=700, height=80,
            font=("Arial", 28, "bold"), fg_color="#7131e2", hover_color="#7b30ea",
            command=lambda d=dep: show_frame(department_pages[d])
        )
        btn.pack(pady=10)

    back_btn = ctk.CTkButton(
        frame, text="← กลับหน้าหลัก", width=300, height=80,
        font=("Arial", 28, "bold"), fg_color="#6b27f2", hover_color="#7527ea",
        command=lambda: show_frame(main_frame)
    )
    back_btn.pack(side="bottom", pady=60)

    return frame


# ---------- เริ่มต้นโปรแกรม ----------
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.attributes("-fullscreen",True)

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# หน้าแต่ละหมวดหลัก
main_frame = create_main_menu(root)
office_frame = create_office_page(root)
department_frame = create_department_page(root)

# สร้างหน้ารายละเอียดของแต่ละ "ห้อง" ในฝ่ายอำนวยการ
office_pages = {}
office_names = [
    "ห้องการเงิน💸", "ห้องงานทะเบียน📜", "ห้องงานบุคลากร👩‍🏫", "ห้องงานการบัญชี👩‍💼",
    "ห้องงานวางแผนและงบประมาณ💰", "ห้องงานความร่วมมือ🤝",
    "ห้องรองผู้อำนวยการฝ่ายกิจการพัฒนานักเรียน นักศึกษา🧑‍🎓",
    "ห้องรองผู้อำนวยการฝ่ายวิชาการ👨‍💻", "ห้องรองผู้อำนวยการฝ่ายบริหารทรัพยากร👩‍💻",
    "ห้องงานอาชีวศึกษาระบบทวิภาคี👩‍⚖️👨‍🏫", "ห้องงานพัฒนาหลักสูตรการเรียนการสอน📔"
]
for name in office_names:
    office_pages[name] = create_detail_page(root, name, office_frame)

# สร้างหน้ารายละเอียดของแต่ละ "แผนกวิชา"
department_pages = {}
department_names = [
    "ช่างก่อสร้าง", "ช่างโยธา", "ช่างเครื่องเรือนและตกแต่งภายใน", "ช่างสำรวจ", "สถาปัตยกรรม",
    "ช่างยนต์", "ช่างกลโรงงาน", "ช่างเชื่อมโลหะ", "ช่างเทคนิคพื้นฐาน", "ช่างไฟฟ้า",
    "ช่างอิเล็กทรอนิกส์", "เครื่องทำความเย็นและปรับอากาศ", "เทคโนโลยีสารสนเทศ",
    "สามัญสัมพันธ์", "เทคโนโลยีปิโตรเลียม", "เทคนิคพลังงาน", "การจัดการโลจิสติกส์ซัพพลายเชน",
    "เทคนิคควบคุมระบบขนส่งทางราง", "เมคคาทรอนิกส์และหุ่นยนต์"
]
for name in department_names:
    department_pages[name] = create_detail_page(root, f"แผนกวิชา{name}", department_frame)

# เริ่มต้นแสดงหน้าเมนูหลัก
show_frame(main_frame)

root.mainloop()
