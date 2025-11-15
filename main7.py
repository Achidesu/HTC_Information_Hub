import tkinter as tk
from tkinter import font

class HTCSmartHub:
    def __init__(self, root):
        self.root = root
        self.root.title("HTC Smart Hub")
        self.root.geometry("1080x1920")
        self.root.configure(bg='#8B008B')
        
        # หน้าต่างๆ
        self.main_frame = None
        self.admin_frame = None
        self.department_frame = None
        
        self.show_main_menu()
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_back_button(self, command):
        btn = tk.Button(
            self.root,
            text="← กลับสู่หน้าหลัก",
            font=("TH Sarabun New", 24, "bold"),
            bg='#FF1493',
            fg='white',
            activebackground='#C71585',
            activeforeground='white',
            relief=tk.FLAT,
            command=command,
            cursor='hand2'
        )
        btn.pack(pady=20, padx=40, anchor='nw')
        return btn
    
    def show_main_menu(self):
        self.clear_screen()
        
        # Header
        header = tk.Frame(self.root, bg='#8B008B', height=200)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="HTC Smart Hub",
            font=("TH Sarabun New", 48, "bold"),
            bg='#8B008B',
            fg='white'
        )
        title.pack(pady=30)
        
        
        # Main buttons
        button_frame = tk.Frame(self.root, bg='#8B008B')
        button_frame.pack(expand=True, pady=40)
        
        btn_admin = tk.Button(
            button_frame,
            text="ฝ่ายอำนวยการ",
            font=("TH Sarabun New", 36, "bold"),
            bg='#FF1493',
            fg='white',
            activebackground='#C71585',
            activeforeground='white',
            width=20,
            height=3,
            relief=tk.FLAT,
            command=self.show_admin_menu,
            cursor='hand2'
        )
        btn_admin.pack(pady=20)
        
        btn_dept = tk.Button(
            button_frame,
            text="แผนกวิชา",
            font=("TH Sarabun New", 36, "bold"),
            bg='#FF1493',
            fg='white',
            activebackground='#C71585',
            activeforeground='white',
            width=20,
            height=3,
            relief=tk.FLAT,
            command=self.show_department_menu,
            cursor='hand2'
        )
        btn_dept.pack(pady=20)
    
    def show_admin_menu(self):
        self.clear_screen()
        self.create_back_button(self.show_main_menu)
        
        title = tk.Label(
            self.root,
            text="ฝ่ายอำนวยการ",
            font=("TH Sarabun New", 42, "bold"),
            bg='#8B008B',
            fg='white'
        )
        title.pack(pady=30)
        
        button_frame = tk.Frame(self.root, bg='#8B008B')
        button_frame.pack(expand=True)
        
        rooms = [
            ("ห้องการเงิน", lambda: self.show_room_detail("ห้องการเงิน")),
            ("ห้องงานทะเบียน", lambda: self.show_room_detail("ห้องงานทะเบียน"))
        ]
        
        for room_name, command in rooms:
            btn = tk.Button(
                button_frame,
                text=room_name,
                font=("TH Sarabun New", 32, "bold"),
                bg='#FF1493',
                fg='white',
                activebackground='#C71585',
                activeforeground='white',
                width=25,
                height=3,
                relief=tk.FLAT,
                command=command,
                cursor='hand2'
            )
            btn.pack(pady=15, padx=40)
    
    def show_department_menu(self):
        self.clear_screen()
        self.create_back_button(self.show_main_menu)
        
        title = tk.Label(
            self.root,
            text="แผนกวิชา",
            font=("TH Sarabun New", 42, "bold"),
            bg='#8B008B',
            fg='white'
        )
        title.pack(pady=20)
        
        # Canvas และ Scrollbar
        canvas = tk.Canvas(self.root, bg='#8B008B', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#8B008B')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((540, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        departments = [
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
        
        for dept in departments:
            btn = tk.Button(
                scrollable_frame,
                text=dept,
                font=("TH Sarabun New", 28, "bold"),
                bg='#FF1493',
                fg='white',
                activebackground='#C71585',
                activeforeground='white',
                width=35,
                height=2,
                relief=tk.FLAT,
                command=lambda d=dept: self.show_room_detail(d),
                cursor='hand2'
            )
            btn.pack(pady=10, padx=40)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def show_room_detail(self, name):
        self.clear_screen()
        self.create_back_button(self.show_main_menu)
        
        title = tk.Label(
            self.root,
            text=name,
            font=("TH Sarabun New", 42, "bold"),
            bg='#8B008B',
            fg='white'
        )
        title.pack(pady=50)
        
        content_frame = tk.Frame(self.root, bg='white', width=900, height=1200)
        content_frame.pack(expand=True, pady=20)
        
        content_label = tk.Label(
            content_frame,
            text=f"ข้อมูลของ {name}\n\n(สามารถเพิ่มเนื้อหาที่นี่)",
            font=("TH Sarabun New", 28),
            bg='white',
            fg='#333333',
            justify=tk.LEFT,
            wraplength=850
        )
        content_label.pack(pady=50, padx=50)

if __name__ == "__main__":
    root = tk.Tk()
    app = HTCSmartHub(root)
    root.mainloop()