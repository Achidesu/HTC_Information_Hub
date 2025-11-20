import customtkinter as ctk
from PIL import Image, ImageTk
import cv2

# --- ตั้งค่า appearance และ theme ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --- สร้างหน้าต่างหลัก ---
root = ctk.CTk()
root.title("HTC Smart Hub")
root.geometry("1080x1920")
root.configure(fg_color="white")

# --- แถบด้านบนสีม่วง ---
top_bar = ctk.CTkFrame(root, height=150, fg_color="#8000FF")
top_bar.pack(side="top", fill="x")

# โลโก้
try:
    logo_image = Image.open("logo.png").resize((120, 120))
    logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(120,120))
    logo_label = ctk.CTkLabel(top_bar, image=logo_ctk_image, text="")
    logo_label.pack(side="left", padx=(20,10), pady=15)
except Exception as e:
    print("ไม่พบไฟล์โลโก้:", e)

# ข้อความบนแถบ
title_label = ctk.CTkLabel(top_bar, text="HTC Smart Hub", text_color="white", font=("Arial", 36, "bold"))
title_label.pack(side="left", padx=10, pady=15)

# --- รูปแฟนเพจตรงกลาง ---
try:
    fanpage_image = Image.open("/home/pi/Test_GUI/Facebook/FF.png").resize((950, 400))
    fanpage_ctk_image = ctk.CTkImage(light_image=fanpage_image, dark_image=fanpage_image, size=(950,400))
    fanpage_label = ctk.CTkLabel(root, image=fanpage_ctk_image, text="")
    fanpage_label.pack(pady=(50, 10))
except Exception as e:
    print("ไม่พบไฟล์แฟนเพจ:", e)

# --- ข้อความ: แผนผังภายในวิทยาลัย (ใต้แฟนเพจ) ---
plan_label = ctk.CTkLabel(root, text="แผนผังภายในวิทยาลัย", font=("Arial", 32, "bold"))
plan_label.pack(pady=(0, 20))

# --- วิดีโอ MP4 ---
video_path = "/home/pi/Test_GUI/Tower/E1.mp4"
cap = cv2.VideoCapture(video_path)
map_label = ctk.CTkLabel(root)
map_label.pack(pady=(0, 20))

def play_video():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame).resize((800,400))
        tk_image = ImageTk.PhotoImage(pil_image)
        map_label.configure(image=tk_image)
        map_label.image = tk_image
        root.after(30, play_video)  # ~33fps
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        root.after(30, play_video)

play_video()  # เริ่มเล่นวิดีโอ

# --- ข้อความเลื่อนด้านล่างสุด พร้อม background สีม่วงสวย ---
credit_frame = ctk.CTkFrame(root, height=50, fg_color="#C8A2C8")  # สีม่วงอ่อนสวย
credit_frame.pack(side="bottom", fill="x")

credit_text = "จัดทำโดย นักศึกษา ภาควิชาเทคโนโลยีคอมพิวเตอร์    "

credit_label = ctk.CTkLabel(
    credit_frame,
    text=credit_text,
    font=("Arial", 24, "bold"),
    text_color="black"
)
credit_label.place(x=-500, y=10)   # เริ่มนอกจอด้านซ้าย

scroll_x = -500  # จุดเริ่มต้น

def scroll_text():
    global scroll_x
    scroll_x += 3  # ความเร็วเลื่อน 1–10
    credit_label.place(x=scroll_x, y=10)

    # ถ้าเลื่อนไปเกินขวาสุดแล้ววนกลับซ้ายใหม่
    if scroll_x > 1100:  
        scroll_x = -len(credit_text) * 12  

    root.after(30, scroll_text)  # 30ms คือความเร็วเฟรม animation

scroll_text()

