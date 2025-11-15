import customtkinter as ctk
from PIL import Image, ImageTk
import os

# --- Theme / Colors ---
ctk.set_appearance_mode("light")
PURPLE = "#6A1B9A"
LIGHT_PURPLE = "#9C4DCC"
WHITE = "#FFFFFF"
BUTTON_HOVER = "#8E24AA"

# --- App size (portrait) ---
APP_WIDTH = 1080   # width (portrait)
APP_HEIGHT = 1920  # height (portrait)

# --- Department list (ตามที่ผู้ใช้ให้มา) ---
DEPARTMENTS = [
    "แผนกวิชาช่างก่อสร้าง",
    "แผนกวิชาช่างโยธา",
    "แผนกวิชาช่างเครื่องเรือนและตกแต่งภายใน",
    "แผนกวิชาช่างสำรวจ",
    "แผนกวิชาสถาปัตยกรรม",
    "แผนกวิชาช่างยนต์",
    "แผนกวิชาช่างกลโรงงาน",
    "แผนกวิชาช่างเชื่อมโลหะ",
    "แผนกวิชาช่างเทคนิคพื้นฐาน",
    "แผนกวิชาช่างไฟฟ้า",
    "แผนกวิชาช่างอิเล็กทรอนิกส์",
    "แผนกวิชาเครื่องทำความเย็นและปรับอากาศ",
    "แผนกวิชาเทคโนโลยีสารสนเทศ",
    "แผนกวิชาสามัญสัมพันธ์",
    "แผนกวิชาเทคโนโลยีปิโตรเลียม",
    "แผนกวิชาเทคนิคพลังงาน",
    "แผนกวิชาการจัดการโลจิสติกส์ซัพพลายเชน",
    "แผนกวิชาเทคนิคควบคุมระบบขนส่งทางราง",
    "แผนกวิชาเมคคาทรอนิกส์และหุ่นยนต์"
]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HTC Smart Hub")
        # portrait geometry
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

        # Top banner area (purple geometric feel)
        header = ctk.CTkFrame(self, height=180, fg_color=PURPLE)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # optional logo image
        logo_path = "images/logo.png"
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path).resize((140, 140))
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_lbl = ctk.CTkLabel(header, image=self.logo_photo, text="")
                logo_lbl.pack(side="left", padx=40, pady=16)
            except Exception:
                pass

        title_lbl = ctk.CTkLabel(header, text="HTC Smart Hub",
                                 font=ctk.CTkFont(size=36, weight="bold"),
                                 text_color=WHITE)
        title_lbl.pack(side="right", padx=40)

        # Main content frame (white)
        self.container = ctk.CTkFrame(self, fg_color=WHITE)
        self.container.pack(fill="both", expand=True)

        # Dictionary of pages
        self.pages = {}

        # create pages
        for Page in (MainPage, AdminMenuPage, AdminSubPage, DepartmentsMenuPage, DeptDetailPage):
            page = Page(parent=self.container, controller=self)
            self.pages[Page.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        # show main
        self.show_page("MainPage")

    def show_page(self, page_name, **kwargs):
        page = self.pages.get(page_name)
        if not page:
            return
        # if page supports an update with kwargs, call it
        if hasattr(page, "on_show"):
            page.on_show(**kwargs)
        page.tkraise()

# ---------------- Main Page ----------------
class MainPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WHITE)
        self.controller = controller

        # Large content area left: banner & map
        left = ctk.CTkFrame(self, fg_color=WHITE)
        left.place(relx=0.03, rely=0.03, relwidth=0.62, relheight=0.9)

        # Right column for big menu buttons
        right = ctk.CTkFrame(self, fg_color=WHITE)
        right.place(relx=0.68, rely=0.12, relwidth=0.28, relheight=0.75)

        # banner image (optional)
        banner_path = "images/banner.png"
        if os.path.exists(banner_path):
            try:
                banner_img = Image.open(banner_path).resize((int(0.62*APP_WIDTH)-40, 220))
                self.banner_photo = ImageTk.PhotoImage(banner_img)
                ctk.CTkLabel(left, image=self.banner_photo, text="").pack(pady=(10,20))
            except Exception:
                ctk.CTkLabel(left, text="HTC Smart Hub", font=ctk.CTkFont(size=24, weight="bold"), text_color=PURPLE).pack(pady=10)
        else:
            ctk.CTkLabel(left, text="HTC Smart Hub", font=ctk.CTkFont(size=24, weight="bold"), text_color=PURPLE).pack(pady=10)

        # Map area
        map_frame = ctk.CTkFrame(left, fg_color="#F5F5F5", corner_radius=10)
        map_frame.pack(padx=20, pady=10, fill="both", expand=False)
        map_frame.configure(height=780, width= int(0.62*APP_WIDTH)-60)
        map_path = "images/map.png"
        if os.path.exists(map_path):
            try:
                map_img = Image.open(map_path).resize((int(0.62*APP_WIDTH)-100, 720))
                self.map_photo = ImageTk.PhotoImage(map_img)
                ctk.CTkLabel(map_frame, image=self.map_photo, text="").pack(padx=10, pady=10)
            except Exception:
                ctk.CTkLabel(map_frame, text="[ไม่พบรูปแผนที่]", font=ctk.CTkFont(size=20), text_color=PURPLE).pack(pady=60)
        else:
            ctk.CTkLabel(map_frame, text="[ไม่พบรูปแผนที่]", font=ctk.CTkFont(size=20), text_color=PURPLE).pack(pady=60)

        # Right-side big buttons
        btn_style = dict(width=340, height=140, corner_radius=12, font=ctk.CTkFont(size=24, weight="bold"),
                         fg_color=PURPLE, hover_color=BUTTON_HOVER, text_color=WHITE)

        ctk.CTkButton(right, text="ฝ่ายอำนวยการ", command=lambda: controller.show_page("AdminMenuPage"), **btn_style).pack(pady=(20,30))
        ctk.CTkButton(right, text="แผนกวิชา", command=lambda: controller.show_page("DepartmentsMenuPage"), **btn_style).pack(pady=(0,30))

        # Footer purple strip
        footer = ctk.CTkFrame(self, height=60, fg_color=PURPLE)
        footer.place(relx=0, rely=0.95, relwidth=1)

# -------------- Admin menu (ฝ่ายอำนวยการ) --------------
class AdminMenuPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WHITE)
        self.controller = controller

        header = ctk.CTkLabel(self, text="ฝ่ายอำนวยการ", font=ctk.CTkFont(size=36, weight="bold"), text_color=PURPLE)
        header.pack(pady=30)

        btn_frame = ctk.CTkFrame(self, fg_color=WHITE)
        btn_frame.pack(pady=20)

        # Buttons for rooms
        rooms = [("ห้องการเงิน", "Finance"), ("ห้องงานทะเบียน", "Registry"), ("ห้องผู้อำนวยการ", "DirectorOffice")]
        for i, (label, key) in enumerate(rooms):
            b = ctk.CTkButton(btn_frame, text=label, width=740, height=120,
                              fg_color=PURPLE, hover_color=BUTTON_HOVER, text_color=WHITE,
                              font=ctk.CTkFont(size=28),
                              command=lambda k=key: controller.show_page("AdminSubPage", room_key=k))
            b.pack(pady=14)

        # Back button
        ctk.CTkButton(self, text="🔙 กลับหน้าหลัก", width=360, height=100,
                      fg_color=PURPLE, hover_color=BUTTON_HOVER, text_color=WHITE,
                      font=ctk.CTkFont(size=22),
                      command=lambda: controller.show_page("MainPage")).pack(side="bottom", pady=40)

# -------------- Admin subpage (ตัวอย่างเนื้อหาห้อง) --------------
class AdminSubPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WHITE)
        self.controller = controller
        self.title_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=34, weight="bold"), text_color=PURPLE)
        self.title_label.pack(pady=30)

        self.content = ctk.CTkLabel(self, text="", wraplength=900, justify="left", font=ctk.CTkFont(size=20))
        self.content.pack(pady=30, padx=40)

        ctk.CTkButton(self, text="🔙 ย้อนกลับ", width=300, height=80,
                      fg_color=PURPLE, hover_color=BUTTON_HOVER, text_color=WHITE,
                      font=ctk.CTkFont(size=20),
                      command=lambda: controller.show_page("AdminMenuPage")).pack(side="bottom", pady=30)

    def on_show(self, room_key=None):
        # room_key: "Finance", "Registry", "DirectorOffice"
        if room_key == "Finance":
            self.title_label.configure(text="ห้องการเงิน")
            self.content.configure(text="ข้อมูล: ติดต่อฝ่ายการเงิน\nหมายเลขภายใน: 101\nเวลาทำการ: 08:30-16:30\n(รายละเอียดเพิ่มเติม...)")
        elif room_key == "Registry":
            self.title_label.configure(text="ห้องงานทะเบียน")
            self.content.configure(text="ข้อมูล: งานทะเบียนนักเรียน\nหมายเลขภายใน: 102\nเวลาทำการ: 08:30-16:30\n(รายละเอียดเพิ่มเติม...)")
        elif room_key == "DirectorOffice":
            self.title_label.configure(text="ห้องผู้อำนวยการ")
            self.content.configure(text="ข้อมูล: สำนักงานผู้อำนวยการ\nติดต่อเพื่อนัดหมาย หัวหน้า...\n(รายละเอียดเพิ่มเติม...)")
        else:
            self.title_label.configure(text="รายละเอียด")
            self.content.configure(text="ข้อมูลเพิ่มเติม...")

# -------------- Departments menu --------------
class DepartmentsMenuPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WHITE)
        self.controller = controller

        header = ctk.CTkLabel(self, text="แผนกวิชา", font=ctk.CTkFont(size=36, weight="bold"), text_color=PURPLE)
        header.pack(pady=20)

        # Scrollable frame for many department buttons
        scroll = ctk.CTkScrollableFrame(self, width=960)
        scroll.pack(pady=10, padx=40, fill="both", expand=True)

        for dept in DEPARTMENTS:
            b = ctk.CTkButton(scroll, text=dept, width=900, height=110,
                              fg_color=PURPLE, hover_color=BUTTON_HOVER, text_color=WHITE,
                              font=ctk.CTkFont(size=20),
                              command=lambda d=dept: controller.show_page("DeptDetailPage", dept_name=d))
            b.pack(pady=8)

        ctk.CTkButton(self, text="🔙 กลับหน้าหลัก", width=360, height=90,
                      fg_color=PURPLE, hover_color=BUTTON_HOVER, text_color=WHITE,
                      font=ctk.CTkFont(size=20),
                      command=lambda: controller.show_page("MainPage")).pack(side="bottom", pady=20)

# -------------- Department detail page --------------
class DeptDetailPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WHITE)
        self.controller = controller
        self.title = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=34, weight="bold"), text_color=PURPLE)
        self.title.pack(pady=30)
        self.info = ctk.CTkLabel(self, text="", wraplength=920, justify="left", font=ctk.CTkFont(size=20))
        self.info.pack(pady=20, padx=30)

        # Sample area for an image or tools
        self.tools_frame = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=10)
        self.tools_frame.pack(pady=10, padx=30, fill="both", expand=False)
        self.tools_frame.configure(height=700)

        self.tools_label = ctk.CTkLabel(self.tools_frame, text="(แสดงภาพหรือข้อมูลแผนกเพิ่มเติมได้ที่นี่)", font=ctk.CTkFont(size=18))
        self.tools_label.pack(pady=40)

        ctk.CTkButton(self, text="🔙 กลับหน้าก่อนหน้า", width=300, height=80,
                      fg_color=PURPLE, hover_color=BUTTON_HOVER, text_color=WHITE,
                      font=ctk.CTkFont(size=20),
                      command=lambda: controller.show_page("DepartmentsMenuPage")).pack(side="bottom", pady=30)

    def on_show(self, dept_name=None):
        if not dept_name:
            dept_name = "แผนกวิชา"
        self.title.configure(text=dept_name)
        # Example placeholder content; you can replace with real data per-department
        info_text = f"รายละเอียดของ {dept_name}\n\n- ห้องปฏิบัติการ / เวิร์กช็อป\n- อาจารย์ผู้รับผิดชอบ: (ชื่อ)\n- เวลาเปิดทำการ: 08:30 - 16:30\n- อุปกรณ์ที่ใช้: ...\n(เพิ่มรายละเอียดที่ต้องการได้)"
        self.info.configure(text=info_text)
        # (ถ้าต้องการโหลดรูปเฉพาะแผนก ให้ตรวจสอบไฟล์ images/{dept_name}.png แล้วโหลดแสดงใน tools_frame)

# ---------------- Run app ----------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
