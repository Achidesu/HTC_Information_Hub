# slide_control.py

from PIL import Image, ImageTk, ImageOps, ImageFilter 
import tkinter as tk 
import os 
import time 

# นำเข้าตัวแปร Global
from config import * # --- ฟังก์ชันช่วยเหลือในการพิมพ์สถานะ ---
def print_status(message):
    """ฟังก์ชันสำหรับพิมพ์ข้อความสถานะใน Terminal พร้อมเวลา"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")


# -----------------------------------------------------------------
# --- ฟังก์ชันควบคุมหน้าต่างนำทางเฉพาะ (60 ปี.jpg) ---
# -----------------------------------------------------------------

def show_navigation_page():
    """แสดงเนื้อหานำทางบนหน้าจอหลัก (Full Screen)"""
    # Import locally เพื่อหลีกเลี่ยง Circular Import
    import main_app 
    show_frame = main_app.show_frame
    
    # ⚠️ โค้ดนี้ถูกตัดออกเพื่อความกระชับ ให้ถือว่ามีการสร้าง Frame ใน main_app แล้ว
    # หากต้องการใช้ฟังก์ชันนี้ ต้องมั่นใจว่า navigation_content_frame ถูกกำหนดค่าใน config.py
    # และมีการสร้าง UI ใน main_app.py
    print_status("--- [NAVIGATION]: แสดงหน้าต่างนำทางเฉพาะ (อาคาร 60 ปี) ---")
    show_frame(navigation_content_frame)


# -----------------------------------------------------------------
# --- ฟังก์ชันสำหรับรูปภาพสไลด์ (Image Marquee) ---
# -----------------------------------------------------------------

def load_slide_images():
    """โหลดรูปภาพทั้งหมดจากโฟลเดอร์ที่กำหนด"""
    global slide_images, slide_photo_images, SLIDE_FRAME_WIDTH, SLIDE_FRAME_COLOR, IMAGE_SLIDE_HEIGHT
    
    slide_images = []
    slide_photo_images = [] 

    if not os.path.exists(IMAGE_SLIDE_FOLDER):
        print_status(f"--- [IMAGE SLIDE ERROR]: ไม่พบโฟลเดอร์: {IMAGE_SLIDE_FOLDER} ---")
        return

    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    image_files = [f for f in os.listdir(IMAGE_SLIDE_FOLDER) if f.lower().endswith(valid_extensions)]
    image_files.sort() 

    if not image_files:
        print_status(f"--- [IMAGE SLIDE]: ไม่พบรูปภาพในโฟลเดอร์: {IMAGE_SLIDE_FOLDER} ---")
        return

    target_image_height = IMAGE_SLIDE_HEIGHT - (SLIDE_FRAME_WIDTH * 2)
    target_image_width_limit = IMAGE_SLIDE_WIDTH_LIMIT - (SLIDE_FRAME_WIDTH * 2)

    for filename in image_files:
        try:
            filepath = os.path.join(IMAGE_SLIDE_FOLDER, filename)
            img = Image.open(filepath)
            
            original_width, original_height = img.size
            
            # ปรับขนาดตามความสูง
            if original_height > target_image_height:
                ratio = target_image_height / original_height
                img = img.resize((int(original_width * ratio), target_image_height), Image.LANCZOS)

            # ตรวจสอบความกว้าง
            if img.width > target_image_width_limit:
                 ratio = target_image_width_limit / img.width
                 img = img.resize((target_image_width_limit, int(img.height * ratio)), Image.LANCZOS)
                 
            # เพิ่มกรอบ (Frame) ให้กับรูปภาพ 
            img = ImageOps.expand(img, border=SLIDE_FRAME_WIDTH, fill=SLIDE_FRAME_COLOR)
            
            slide_images.append(img)
            slide_photo_images.append({
                'photo': ImageTk.PhotoImage(img),
                'filename': filename
            })

            print_status(f"--- [IMAGE SLIDE]: โหลดรูปภาพ (รวมกรอบ): {filename} ({img.width}x{img.height}) ---")

        except Exception as e:
            print_status(f"--- [IMAGE SLIDE ERROR]: ไม่สามารถโหลดรูปภาพ {filename}: {e} ---")

    if not slide_images:
        print_status("--- [IMAGE SLIDE]: ไม่พบรูปภาพที่สามารถโหลดได้ ---")

def handle_navigation_click(event):
    """ฟังก์ชันจัดการการคลิกบนรูปภาพที่ผูกกับ Event"""
    # ใช้ root.after(0, ...) เพื่อให้การนำทางเกิดขึ้นใน Main Thread ของ Tkinter
    if root:
        root.after(0, show_navigation_page)
        print_status("--- [CLICK EVENT]: ทำการนำทางไปยังหน้า 60 ปี แล้ว ---")


def place_next_slide(start_immediately_at_right_edge=False):
    """วางรูปภาพสไลด์ถัดไปบน Canvas โดยเว้นช่องไฟ"""
    global current_slide_index, image_slide_canvas, slide_photo_images, slide_images
    global next_image_x_placement, active_slide_items, SLIDE_GAP, NAVIGATION_TRIGGER_IMAGE

    if not slide_photo_images or not image_slide_canvas:
        return

    current_slide_index = (current_slide_index + 1) % len(slide_photo_images)
    
    image_data = slide_photo_images[current_slide_index] 
    image_to_place = slide_images[current_slide_index]
    
    image_width = image_to_place.width
    image_photo = image_data['photo']
    image_filename = image_data['filename'] 

    if start_immediately_at_right_edge:
        start_x_center = 1080 + image_width / 2
    else:
        start_x_center = next_image_x_placement + SLIDE_GAP + image_width / 2

    canvas_item_id = image_slide_canvas.create_image(
        start_x_center, IMAGE_SLIDE_HEIGHT // 2, 
        image=image_photo, 
        anchor="center"
    )

    # 🌟 การแก้ไขปัญหา Garbage Collection ที่สำคัญที่สุด:
    # ผูก PhotoImage ไว้กับ Canvas item โดยใช้ tag_bind และ setattr 
    # เพื่อให้ Canvas เก็บ Strong Reference ของรูปภาพไว้
    image_slide_canvas.tag_bind(
        canvas_item_id, 
        '<Map>', 
        lambda e, photo=image_photo: setattr(image_slide_canvas, f'_ref_slide_{canvas_item_id}', photo)
    )

    next_image_x_placement = start_x_center + image_width / 2 

    active_slide_items.append({
        'id': canvas_item_id, 
        'width': image_width, 
        'photo': image_photo, 
        'right_edge': next_image_x_placement,
        'slide_index': current_slide_index 
    })
    
    # NEW: ตรวจสอบและผูก Event การคลิกเพื่อนำทาง
    if image_filename == NAVIGATION_TRIGGER_IMAGE:
        image_slide_canvas.tag_bind(
            canvas_item_id, 
            '<Button-1>', 
            handle_navigation_click
        )
        print_status(f"--- [CLICK EVENT]: ผูกคลิกเพื่อนำทางกับรูปภาพ: {image_filename} (ID: {canvas_item_id}) ---")


def animate_image_slide():
    """ควบคุมการสไลด์ต่อเนื่องและการจัดการรายการรูปภาพ"""
    global image_slide_canvas, active_slide_items, next_image_x_placement, SLIDE_GAP
    global is_dragging

    if not image_slide_canvas or not slide_images:
        if root:
            root.after(25, animate_image_slide)
        return

    # หยุดการสไลด์เมื่อมีการลาก (ถ้ามีการใช้งานฟีเจอร์ลากในอนาคต)
    if not is_dragging:
        if not active_slide_items:
            place_next_slide(start_immediately_at_right_edge=True)
            place_next_slide() 

            if not active_slide_items:
                if root:
                    root.after(25, animate_image_slide)
                return

        move_distance = -3 
        
        for item in active_slide_items:
            image_slide_canvas.move(item['id'], move_distance, 0)
            item['right_edge'] += move_distance
            
        next_image_x_placement += move_distance

        # ลบรูปภาพที่เลื่อนออกนอกจอไปแล้ว
        if active_slide_items and active_slide_items[0]['right_edge'] < 0:
            item_to_remove = active_slide_items.pop(0)
            image_slide_canvas.delete(item_to_remove['id'])

            # 🌟 การแก้ไขปัญหา Garbage Collection ที่สำคัญที่สุด:
            # ลบ Strong Reference ที่สร้างไว้เมื่อรูปภาพถูกลบออกจาก Canvas
            ref_name = f'_ref_slide_{item_to_remove["id"]}'
            if hasattr(image_slide_canvas, ref_name):
                delattr(image_slide_canvas, ref_name)
                
        # วางรูปภาพใหม่เมื่อมีช่องว่างเพียงพอ
        if active_slide_items and active_slide_items[-1]['right_edge'] < 1080 + SLIDE_GAP:
            place_next_slide()

    if root:
        root.after(25, animate_image_slide) # 25ms ≈ 40 FPS

# ฟังก์ชัน Drag (placeholder สำหรับการลากในอนาคต)
def start_drag(event):
    global is_dragging, drag_start_x
    is_dragging = True
    drag_start_x = event.x
    
def do_drag(event):
    global drag_start_x, active_slide_items, next_image_x_placement
    if not is_dragging or not image_slide_canvas:
        return
    
    delta_x = event.x - drag_start_x
    drag_start_x = event.x
    
    for item in active_slide_items:
        image_slide_canvas.move(item['id'], delta_x, 0)
        item['right_edge'] += delta_x
        
    next_image_x_placement += delta_x
    
    # เพิ่มรูปภาพใหม่ทางซ้ายหรือขวาตามความเหมาะสม (ต้อง implement place_previous_slide ด้วย)
    # แต่สำหรับการแก้ไขนี้ เราจะเน้นที่การแก้ไข GC ก่อน

def stop_drag(event):
    global is_dragging
    is_dragging = False
    
# *** (หมายเหตุ: โค้ดนี้ใช้สำหรับการเลื่อนแบบอัตโนมัติเท่านั้น) ***