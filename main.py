import tkinter as tk
from tkinter import font as tkfont

class HTCSmartHub:
    def __init__(self, root):
        self.root = root
        self.root.title("HTC Smart Hub")
        self.root.geometry("1080x1920")
        self.root.configure(bg='white')
        
        # Define colors
        self.purple = "#A70DE4"
        self.light_purple = "#AE18EA"
        self.white = "#FFFFFF"
        
        # Create main container
        self.container = tk.Frame(root, bg='white')
        self.container.pack(fill='both', expand=True)
        
        # Show home page
        self.show_home()
    
    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def create_header(self, title="HTC Smart Hub"):
        header = tk.Frame(self.container, bg=self.purple, height=150)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=title, font=("Arial", 36, "bold"), 
                              bg=self.purple, fg='white')
        title_label.pack(expand=True)
    
    def create_footer(self):
        footer = tk.Frame(self.container, bg=self.purple, height=100)
        footer.pack(side='bottom', fill='x')
        footer.pack_propagate(False)
    
    def create_back_button(self, command):
        back_btn = tk.Button(self.container, text="← กลับสู่หน้าหลัก", 
                            font=("Arial", 24), bg=self.light_purple, fg='white',
                            command=command, relief='flat', padx=30, pady=15,
                            cursor='hand2')
        back_btn.pack(pady=20)
    
    def create_menu_button(self, parent, text, command, row, col):
        btn = tk.Button(parent, text=text, font=("Arial", 28, "bold"),
                       bg=self.purple, fg='white', command=command,
                       relief='flat', padx=40, pady=60, cursor='hand2',
                       activebackground=self.light_purple)
        btn.grid(row=row, column=col, padx=30, pady=30, sticky='nsew')
    
    def show_home(self):
        self.clear_frame()
        self.create_header("HTC Smart Hub")
        
        # Main content area
        content = tk.Frame(self.container, bg='white')
        content.pack(fill='both', expand=True, pady=50)
        
        # Configure grid
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        # Create main menu buttons
        self.create_menu_button(content, "ฝ่ายอำนวยการ", self.show_admin, 0, 0)
        self.create_menu_button(content, "แผนกวิชา", self.show_departments, 0, 1)
        
        self.create_footer()
    
    def show_admin(self):
        self.clear_frame()
        self.create_header("ฝ่ายอำนวยการ")
        
        self.create_back_button(self.show_home)
        
        content = tk.Frame(self.container, bg='white')
        content.pack(fill='both', expand=True, pady=30)
        
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        # Admin offices
        self.create_menu_button(content, "ห้องการเงิน", 
                               lambda: self.show_room("ห้องการเงิน"), 0, 0)
        self.create_menu_button(content, "ห้องงานทะเบียน", 
                               lambda: self.show_room("ห้องงานทะเบียน"), 0, 1)
        
        self.create_footer()
    
    def show_room(self, room_name):
        self.clear_frame()
        self.create_header(room_name)
        
        self.create_back_button(self.show_admin)
        
        content = tk.Frame(self.container, bg='white')
        content.pack(fill='both', expand=True)
        
        info_label = tk.Label(content, text=f"ข้อมูล{room_name}", 
                             font=("Arial", 32), bg='white', fg=self.purple)
        info_label.pack(expand=True)
        
        self.create_footer()
    
    def show_departments(self):
        self.clear_frame()
        self.create_header("แผนกวิชา")
        
        self.create_back_button(self.show_home)
        
        # Scrollable content
        canvas = tk.Canvas(self.container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.container, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
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
        
        for i, dept in enumerate(departments):
            btn = tk.Button(scrollable_frame, text=dept, font=("Arial", 24),
                           bg=self.purple, fg='white',
                           command=lambda d=dept: self.show_department_detail(d),
                           relief='flat', padx=30, pady=25, cursor='hand2',
                           activebackground=self.light_purple)
            btn.pack(fill='x', padx=40, pady=10)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.create_footer()
    
    def show_department_detail(self, dept_name):
        self.clear_frame()
        self.create_header(dept_name)
        
        self.create_back_button(self.show_departments)
        
        content = tk.Frame(self.container, bg='white')
        content.pack(fill='both', expand=True)
        
        info_label = tk.Label(content, text=f"ข้อมูล{dept_name}", 
                             font=("Arial", 32), bg='white', fg=self.purple)
        info_label.pack(expand=True)
        
        self.create_footer()

if __name__ == "__main__":
    root = tk.Tk()
    app = HTCSmartHub(root)
    root.mainloop()