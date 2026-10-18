import tkinter as tk
from tkinter import messagebox
import random

# 创建主窗口
root = tk.Tk()
root.title("账号密码登录")
root.geometry("300x200")


# 登录验证函数
def login():
    username = entry_username.get()
    password = entry_password.get()

    # 简单账号密码验证
    if username == "admin" and password == "1234":
        messagebox.showinfo("登录成功", "账号验证成功，进入拼图验证。")
        show_puzzle_verification()  # 触发拼图验证
    else:
        messagebox.showerror("登录失败", "账号或密码错误，请重试。")


# 显示拼图验证窗口
def show_puzzle_verification():
    # 创建新窗口
    puzzle_window = tk.Toplevel(root)
    puzzle_window.title("拼图验证")
    puzzle_window.geometry("400x300")

    # 提示标签
    label_info = tk.Label(puzzle_window, text="请拖动滑块将拼图滑到缺口位置。")
    label_info.pack(pady=10)

    # 创建一个画布来展示拼图
    canvas = tk.Canvas(puzzle_window, width=300, height=200, bg="lightgrey")
    canvas.pack()

    # 随机生成缺口位置
    missing_x = random.randint(80, 200)
    missing_y = 70
    missing_piece = canvas.create_rectangle(
        missing_x, missing_y, missing_x + 50, missing_y + 50, fill="lightgrey", outline="black"
    )

    # 创建完整的拼图
    full_image = canvas.create_rectangle(10, 10, 290, 190, fill="blue", outline="black")

    # 创建滑块
    slider_x = 10  # 滑块初始位置
    slider = canvas.create_rectangle(
        slider_x, missing_y, slider_x + 50, missing_y + 50, fill="darkblue"
    )

    # 滑块移动函数
    def on_slider_move(event):
        # 让滑块跟随鼠标移动
        x = event.x
        if 10 <= x <= 240:  # 限制滑块的移动范围
            canvas.coords(slider, x, missing_y, x + 50, missing_y + 50)

    # 验证函数
    def verify_puzzle():
        # 获取滑块的当前位置
        slider_pos = canvas.coords(slider)
        # 检查滑块是否对齐缺口
        if abs(slider_pos[0] - missing_x) < 5:
            messagebox.showinfo("验证成功", "拼图验证通过！")
            puzzle_window.destroy()
        else:
            messagebox.showwarning("验证失败", "滑块未对齐缺口，请重试。")

    # 鼠标拖动事件绑定到滑块
    canvas.tag_bind(slider, "<B1-Motion>", on_slider_move)

    # 完成验证按钮
    button_verify = tk.Button(puzzle_window, text="完成验证", command=verify_puzzle)
    button_verify.pack(pady=10)


# 创建用户名标签和输入框
label_username = tk.Label(root, text="用户名:")
label_username.pack(pady=10)
entry_username = tk.Entry(root)
entry_username.pack()

# 创建密码标签和输入框
label_password = tk.Label(root, text="密码:")
label_password.pack(pady=10)
entry_password = tk.Entry(root, show="*")
entry_password.pack()

# 创建登录按钮
button_login = tk.Button(root, text="登录", command=login)
button_login.pack(pady=20)

# 运行主循环
root.mainloop()
