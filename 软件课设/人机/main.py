import os
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


def main():
    base_dir = "./ans"  # ans 文件夹路径
    wrong_dir = "./wrong"  # wrong 文件夹路径

    # 获取所有配方文件夹
    ans_folders = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    print(ans_folders)
    if not ans_folders:
        messagebox.showerror("错误", "没有找到任何配方文件夹！")
        return

    # 随机选择一个配方
    selected_folder = random.choice(ans_folders)
    files = [os.path.join(selected_folder, f) for f in os.listdir(selected_folder)]
    result_image = None
    materials = []

    # 区分合成结果和配方材料
    for file in files:
        print(f"检查文件: {file}")
        base_name, ext = os.path.splitext(os.path.basename(file).strip())  # 分离文件名和扩展名
        print(f"文件名（去空格后）: {base_name}, 扩展名: {ext}")

        if base_name == "ans":  # 合成结果文件
            result_image = file
            print("找到合成结果: ans")
        elif base_name.startswith("pic"):  # 配方材料文件
            materials.append(file)
            print(f"找到材料: {file}")
        else:
            print("未匹配此文件")

    if not materials:
        messagebox.showerror("错误", f"配方 {os.path.basename(selected_folder)} 中没有任何材料！")
        return

    if not result_image:
        messagebox.showerror("错误", f"配方 {os.path.basename(selected_folder)} 缺少合成结果文件 ans！")
        return

    # 获取 wrong 文件夹中的图片
    wrong_materials = [os.path.join(wrong_dir, f) for f in os.listdir(wrong_dir) if f.startswith("pic")]
    if not wrong_materials:
        messagebox.showerror("错误", "没有找到任何错误材料！")
        return

    # 随机选择一张错误材料
    wrong_material = random.choice(wrong_materials)

    # 将正确材料和错误材料合并并打乱顺序
    all_materials = materials + [wrong_material]
    random.shuffle(all_materials)

    # 读取简介文本
    description = ""
    rec_file = os.path.join(os.path.dirname(result_image), "rec.txt")
    if os.path.exists(rec_file):
        with open(rec_file, "r", encoding="utf-8") as f:
            description = f.read()

    # 图形界面显示
    show_gui(result_image, all_materials, wrong_material, description)


def show_gui(result_image, all_materials, wrong_material, description):
    def on_click(selected_image):
        if selected_image == wrong_material:
            messagebox.showinfo("结果", "您选错了3次，您已经被锁定，请稍后再试")
        else:
            messagebox.showwarning("结果", "您选错了3次，您已经被锁定，请稍后再试")

    # 创建窗口
    root = tk.Tk()
    root.title("材料选择")
    root.geometry("800x600")

    # 创建整体布局
    frame = tk.Frame(root)
    frame.pack(pady=20)

    # 创建一个框架用于放置合成结果和简介并排
    result_description_frame = tk.Frame(frame)
    result_description_frame.pack(pady=20)

    # 合成结果部分（居中显示）
    result_frame = tk.Frame(result_description_frame)
    result_frame.pack(side=tk.LEFT, padx=20)

    tk.Label(result_frame, text="合成结果：", font=("Arial", 16)).pack(pady=10)
    result_img = Image.open(result_image).resize((200, 200))  # 调整图片大小
    result_img_tk = ImageTk.PhotoImage(result_img)
    result_label = tk.Label(result_frame, image=result_img_tk)
    result_label.image = result_img_tk  # 保存引用，防止被垃圾回收
    result_label.pack(pady=10)

    # 简介部分（右侧显示）
    description_frame = tk.Frame(result_description_frame)
    description_frame.pack(side=tk.LEFT, padx=20)

    tk.Label(description_frame, text="简介：", font=("Arial", 16)).pack(pady=10)
    description_label = tk.Label(description_frame, text=description, wraplength=300, justify="left", font=("Arial", 12))
    description_label.pack(pady=10)

    # 材料部分（横向排列）
    material_frame = tk.Frame(frame)
    material_frame.pack(pady=20)

    for material in all_materials:
        img = Image.open(material).resize((100, 100))  # 调整图片大小
        img_tk = ImageTk.PhotoImage(img)
        btn = tk.Button(material_frame, image=img_tk, command=lambda m=material: on_click(m))
        btn.image = img_tk  # 保存引用，防止被垃圾回收
        btn.pack(side=tk.LEFT, padx=5)

    root.mainloop()


if __name__ == "__main__":
    main()
