import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk 
# ----------------------------------------
# ฟังก์ชันสร้างหน้าจอแสดงผล (1920x1080)
# ----------------------------------------
class DisplayWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Display Window (1920x1080)")
        self.geometry("1080x1920")  # แนวตั้ง
        self.configure(bg="white")
        self.resizable(False, False)

        # พื้นที่สำหรับเนื้อหา
        self.content_label = tk.Label(self, text="📱 หน้าจอแสดงผล", font=("Arial", 28, "bold"), bg="white")
        self.content_label.pack(pady=100)

    def show_content(self, page_name):
        """เปลี่ยนเนื้อหาตามเมนูที่เลือก"""
        for widget in self.winfo_children():
            widget.destroy()  # ล้างของเดิม

        tk.Label(self, text=page_name, font=("Arial", 36, "bold"), fg="#4b0082", bg="white").pack(pady=50)

        if page_name == "Map":
            tk.Label(self, text="📍 แผนที่ วิทยาลัยเทคนิคหาดใหญ่", font=("Arial", 24), bg="white").pack()
        elif page_name == "ผู้อำนวยการ":
            tk.Label(self, text="👨‍🏫 นายสมศักดิ์ ไชยโสดา\nผู้อำนวยการวิทยาลัยเทคนิคหาดใหญ่",
                     font=("Arial", 22), bg="white").pack()
        elif page_name == "ติดต่อเรา":
            tk.Label(self, text="📞 เบอร์ติดต่อ: 074-212300\n✉️ Email: info@htc.ac.th",
                     font=("Arial", 22), bg="white").pack()
        else:
            tk.Label(self, text="หน้าว่าง", font=("Arial", 24), bg="white").pack()


# ----------------------------------------
# ฟังก์ชันสร้างหน้าจอเมนู (1280x800)
# ----------------------------------------
class MenuWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Menu (1280x800)")
        self.geometry("1280x800")
        self.configure(bg="#dcd6f7")
        self.resizable(False, False)

        # สร้างหน้าจอแสดงผล
        self.display_window = DisplayWindow()

        # หัวข้อ
        tk.Label(self, text="📘 วิทยาลัยเทคนิคหาดใหญ่", font=("Arial", 28, "bold"),
                 bg="#9b59b6", fg="white").pack(fill="x")

        # ปุ่มเมนู
        button_frame = tk.Frame(self, bg="#dcd6f7")
        button_frame.pack(expand=True)

        btn_map = tk.Button(button_frame, text="🗺️  MAP", font=("Arial", 20, "bold"),
                            bg="#8f2fb4", fg="white", width=20, height=2,
                            command=lambda: self.display_window.show_content("Map"))
        btn_map.pack(pady=20)

        btn_director = tk.Button(button_frame, text="👨‍💼  ผู้อำนวยการ", font=("Arial", 20, "bold"),
                                 bg="#8e44ad", fg="white", width=20, height=2,
                                 command=lambda: self.display_window.show_content("ผู้อำนวยการ"))
        btn_director.pack(pady=20)

        btn_contact = tk.Button(button_frame, text="📞  ติดต่อเรา", font=("Arial", 20, "bold"),
                                bg="#7d3c98", fg="white", width=20, height=2,
                                command=lambda: self.display_window.show_content("ติดต่อเรา"))
        btn_contact.pack(pady=20)

        # ปุ่มออกจากโปรแกรม
        tk.Button(self, text="❌ ออกจากระบบ", font=("Arial", 14),
                  bg="#6c3483", fg="white", command=self.quit).pack(side="bottom", pady=10)


# ----------------------------------------
# เริ่มโปรแกรม
# ----------------------------------------
if __name__ == "__main__":
    app = MenuWindow()
    app.mainloop()
    