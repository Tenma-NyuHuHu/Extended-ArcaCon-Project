import os
import configparser
import tkinter as tk
from sungDuckCon import create_gif_with_text
from cutFor200x200 import ImageCropper
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont

# def create_gif_from_folder():
#     # 1. 폴더 선택창 띄우기
#     root = tk.Tk()
#     root.withdraw() # 메인 창 숨기기
#     target_folder = filedialog.askdirectory(title="이미지와 config.txt가 있는 폴더를 선택하세요")
    
#     if not target_folder:
#         print("작업이 취소되었습니다.")
#         return

#     config_path = os.path.join(target_folder, "config.txt")
    
#     # 2. config.txt 존재 여부 확인
#     if not os.path.exists(config_path):
#         messagebox.showerror("에러", f"'{target_folder}' 내에 config.txt가 없습니다.")
#         return
    
#     create_gif_with_text(target_folder)

def create_cutwindow_and_gif():
    # 1. 폴더 선택창 띄우기
    root = tk.Tk()
    root.withdraw() # 메인 창 숨기기
    target_folder = filedialog.askdirectory(title="이미지와, config.txt와 uncropeds가 있는 폴더를 선택하세요")
    
    if not target_folder:
        print("작업이 취소되었습니다.")
        return

    uncropeds_path = os.path.join(target_folder, "uncropeds")
    
    if not os.path.exists(uncropeds_path):
        messagebox.showerror("에러", f"'{target_folder}' 내에 uncropeds가 없습니다.")
        return
    
    config_path = os.path.join(target_folder, "config.txt")
    
    if not os.path.exists(config_path):
        messagebox.showerror("에러", f"'{target_folder}' 내에 config.txt가 없습니다.")
        return
    

    image_files = [os.path.join(uncropeds_path, f) for f in os.listdir(uncropeds_path) if f.endswith(('.png', '.jpg', '.jpeg', '.webp', '.PNG'))]

    for img_p in image_files:
        cropper = ImageCropper(img_p, target_folder)
        status = cropper.run()
        if status == "quit":
            break
    
    create_gif_with_text(target_folder)
        

    


if __name__ == "__main__":
    create_cutwindow_and_gif()
    # create_cutwindow()