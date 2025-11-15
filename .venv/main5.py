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

# ---------- ฟังก์ชันแสดงภาพ ----------
def create_image_page(root, title, img_path, back_to):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(frame, text=title, font=("Arial Black", 46), text_color="#5b00a0").pack(pady=40)
    
    try:
        img = Image.open(img_path).resize((900, 600))
        photo = ImageTk.PhotoImage(img)
        ctk.CTkLabel(frame, image=photo, text="").pack(pady=20)
        frame.image = photo
    except:
        ctk.CTkLabel(frame, text="(ไม่พบรูปภาพ)", font=("Arial", 30), text_color="gray").pack(pady=50)
    
    ctk.CTkButton(frame, text="↩ กลับ", width=400, height=80,
                  font=("Arial", 28, "bold"), fg_color="#8c52ff", hover_color="#a66cff",
                  command=lambda: show_frame(back_to)).pack(pady=40)
    
    ctk.CTkButton(frame, text="🏠 กลับหน้าหลัก", width=400, height=80,
                  font=("Arial", 28, "bold"), fg_color="#8c52ff", hover_color="#a66cff",
                  command=lambda: show_frame(main_frame)).pack(pady=20)
    return frame


# ---------- สร้างหน้าเมนูหลัก ----------
def create_main_menu(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")

    # ส่วนหัว
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

    title_label = ctk.CTkLabel(header, text="HTC Smart Hub", text_color="white",
                               font=("Arial Black", 52))
    title_label.pack(side="right", padx=60, pady=20)

    # Facebook
    try:
        fb_img = Image.open("FF.png").resize((900, 400))
        fb_photo = ImageTk.PhotoImage(fb_img)
        fb_label = ctk.CTkLabel(frame, image=fb_photo, text="")
        fb_label.image = fb_photo
        fb_label.pack(pady=20)
    except:
        ctk.CTkLabel(frame, text="(รอใส่ภาพ Facebook)", text_color="#7a1cff", font=("Arial", 28)).pack(pady=20)

    # Map
    try:
        map_img = Image.open("Map2.png").resize((900, 500))
        map_photo = ImageTk.PhotoImage(map_img)
        map_label = ctk.CTkLabel(frame, image=map_photo, text="")
        map_label.image = map_photo
        map_label.pack(pady=10)
    except:
        ctk.CTkLabel(frame, text="(รอใส่แผนที่)", text_color="#7a1cff", font=("Arial", 28)).pack(pady=20)

    # ปุ่ม
    btn_office = ctk.CTkButton(frame, text="ฝ่ายอำนวยการ 🏢", width=400, height=100,
                               font=("Arial", 36, "bold"), fg_color="#7b2ff7",
                               hover_color="#8f47ff", command=lambda: show_frame(office_frame))
    btn_office.pack(pady=30)

    btn_department = ctk.CTkButton(frame, text="แผนกวิชา 🧰", width=400, height=100,
                                   font=("Arial", 36, "bold"), fg_color="#712df0",
                                   hover_color="#8438f9", command=lambda: show_frame(department_frame))
    btn_department.pack(pady=30)
    return frame


# ---------- หน้า ฝ่ายอำนวยการ ----------
def create_office_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")
    ctk.CTkLabel(frame, text="ฝ่ายอำนวยการ 🧑‍💼", font=("Arial Black", 48), text_color="#7c02f7").pack(pady=40)

    scroll = ctk.CTkScrollableFrame(frame, width=950, height=1300)
    scroll.pack(pady=20)

    offices = {
        "ห้องการเงิน ": "ab.jpg",
        "ห้องงานทะเบียน ": "abc.jpg",
        "ห้องงานบุคลากร ": "a1.jpg",
        "ห้องงานการบัญชี ": "a3.jpg",
        "ห้องงานวางแผนและงบประมาณ ": "a3.jpg",
        "ห้องงานรองผู้อำนวยการแผนและความร่วมมือ ": "a4.jpg",
        "ห้องรองผู้อำนวยการฝ่ายกิจการนักเรียน นักศึกษา ": "a5.jpg",
        "ห้องรองผู้อำนวยการฝ่ายวิชาการ ": "a6.jpg",
        "ห้องรองผู้อำนวยการฝ่ายบริหารทรัพยากร ": "a7.jpg",
        "ห้องงานอาชีวศึกษาระบบทวิภาคี ": "a9.jpg",
        "ห้องงานพัฒนาหลักสูตร ": "a11.jpg"
    }

    for name, img in offices.items():
        btn = ctk.CTkButton(scroll, text=name, width=700, height=90,
                            font=("Arial", 30, "bold"), fg_color="#7b43ec", hover_color="#9a5cff",
                            command=lambda n=name, i=img: show_frame(image_pages_office[n]))
        btn.pack(pady=10)

    ctk.CTkButton(frame, text="← กลับหน้าหลัก", width=300, height=80,
                  font=("Arial", 28, "bold"), fg_color="#6920f9", hover_color="#7023e4",
                  command=lambda: show_frame(main_frame)).pack(side="bottom", pady=40)
    return frame


# ---------- หน้า แผนกวิชา ----------
def create_department_page(root):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid(row=0, column=0, sticky="nsew")
    ctk.CTkLabel(frame, text="แผนกวิชา 🧰", font=("Arial Black", 48), text_color="#5b00a0").pack(pady=30)

    departments = {
        "ช่างก่อสร้าง": "B11.jpg",
        "ช่างโยธา": "B9.jpg",
        "ช่างเครื่องเรือนและตกแต่งภายใน": "B12.jpg",
        "ช่างสำรวจ": "B6.jpg",
        "สถาปัตยกรรม": "B6.jpg",
        "ช่างกลโรงงาน": "B16.jpg",
        "ช่างเชื่อมโลหะ": "B17.jpg",
        "ช่างเทคนิคพื้นฐาน": "B1.jpg",
        "ช่างไฟฟ้า": "B10.jpg",
        "ช่างอิเล็กทรอนิกส์": "B8.jpg",
        "เครื่องทำความเย็นและปรับอากาศ": "B2.jpg",
        "เทคโนโลยีสารสนเทศ": "B13.jpg",
        "เทคนิคพลังงาน": "B3.jpg",
        "การจัดการโลจิสติกส์ซัพพลายเชน": "B3.jpg",
        "เทคนิคควบคุมระบบขนส่งทางราง": "B14.jpg",
        "เมคคาทรอนิกส์และหุ่นยนต์": "B15.jpg"       
    }

    scroll = ctk.CTkScrollableFrame(frame, width=950, height=1300)
    scroll.pack(pady=20)

    for name, img in departments.items():
        btn = ctk.CTkButton(scroll, text=f"แผนกวิชา{name}", width=700, height=80,
                            font=("Arial", 28, "bold"), fg_color="#7131e2", hover_color="#7b30ea",
                            command=lambda n=name, i=img: show_frame(image_pages_department[n]))
        btn.pack(pady=10)

    ctk.CTkButton(frame, text="← กลับหน้าหลัก", width=300, height=80,
                  font=("Arial", 28, "bold"), fg_color="#6b27f2", hover_color="#7527ea",
                  command=lambda: show_frame(main_frame)).pack(side="bottom", pady=40)
    return frame


# ---------- เริ่มต้นโปรแกรม ----------
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)


root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

main_frame = create_main_menu(root)
office_frame = create_office_page(root)
department_frame = create_department_page(root)

# ---------- สร้างหน้ารูปภาพย่อยทั้งหมด ----------
image_pages_office = {}
image_pages_department = {}

# สร้างหน้า "ฝ่ายอำนวยการ"
offices = {
   "ห้องการเงิน 💸": "ab.jpg",
        "ห้องงานทะเบียน ": "abc.jpg",
        "ห้องงานบุคลากร ": "a1.jpg",
        "ห้องงานการบัญชี ": "a3.jpg",
        "ห้องงานวางแผนและงบประมาณ ": "a3.jpg",
        "ห้องงานรองผู้อำนวยการแผนและความร่วมมือ ": "a4.jpg",
        "ห้องรองผู้อำนวยการฝ่ายกิจการนักเรียน นักศึกษา ": "a5.jpg",
        "ห้องรองผู้อำนวยการฝ่ายวิชาการ ": "a6.jpg",
        "ห้องรองผู้อำนวยการฝ่ายบริหารทรัพยากร ": "a7.jpg",
        "ห้องงานอาชีวศึกษาระบบทวิภาคี ": "a9.jpg",
        "ห้องงานพัฒนาหลักสูตร ": "a11.jpg"
}
for name, img in offices.items():
    image_pages_office[name] = create_image_page(root, name, img, office_frame)

# สร้างหน้า "แผนกวิชา"
departments = {
     "ช่างก่อสร้าง": "B11.jpg",
        "ช่างโยธา": "B9.jpg",
        "ช่างเครื่องเรือนและตกแต่งภายใน": "B12.jpg",
        "ช่างสำรวจ": "B6.jpg",
        "สถาปัตยกรรม": "B6.jpg",
        "ช่างกลโรงงาน": "B16.jpg",
        "ช่างเชื่อมโลหะ": "B17.jpg",
        "ช่างเทคนิคพื้นฐาน": "B1.jpg",
        "ช่างไฟฟ้า": "B10.jpg",
        "ช่างอิเล็กทรอนิกส์": "B8.jpg",
        "เครื่องทำความเย็นและปรับอากาศ": "B2.jpg",
        "เทคโนโลยีสารสนเทศ": "B13.jpg",
        "เทคนิคพลังงาน": "B3.jpg",
        "การจัดการโลจิสติกส์ซัพพลายเชน": "B3.jpg",
        "เทคนิคควบคุมระบบขนส่งทางราง": "B14.jpg",
        "เมคคาทรอนิกส์และหุ่นยนต์": "B15.jpg"
}
for name, img in departments.items():
    image_pages_department[name] = create_image_page(root, f"แผนกวิชา{name}", img, department_frame)

show_frame(main_frame)
root.mainloop()
