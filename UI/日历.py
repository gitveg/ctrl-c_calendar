import tkinter as tk
from tkinter import ttk
from datetime import datetime
import calendar
import os
from tkinter import messagebox

# 创建主窗口
root = tk.Tk()
root.title("日历程序")
root.geometry("400x700")
root.configure(bg='#FFFACD')  # 设置背景为淡黄色
root.resizable(False, False)  # 固定窗口大小

# 获取当前日期
now = datetime.now()
year = now.year
month = now.month
selected_day = now.day  # 默认选中今天

# 自定义字体
bold_font = ("Arial", 12, "bold")

# 日程存储路径
schedule_dir = "schedules"
if not os.path.exists(schedule_dir):
    os.makedirs(schedule_dir)

# 显示当前日期标签
current_date_label = tk.Label(root, text=f"今天是{year}年{month}月{selected_day}日", font=bold_font, bg='#FFFACD')
current_date_label.pack(pady=10)

# 创建一个函数来更新日历
def update_calendar(year, month):
    """
    更新日历显示，并重新绘制日历框。
    """
    for widget in cal_frame.winfo_children():
        widget.destroy()

    cal = calendar.monthcalendar(year, month)
    days = ['一', '二', '三', '四', '五', '六', '日']
    for day in days:
        lbl = tk.Label(cal_frame, text=day, padx=10, pady=5, bg='#FFFACD', font=("Arial", 10))
        lbl.grid(row=0, column=days.index(day))

    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            if day == 0:
                lbl = tk.Label(cal_frame, text='', padx=10, pady=5, bg='#FFFACD')  # 移除空白处的阴影，背景设置为淡黄色
            else:
                lbl = tk.Button(cal_frame, text=day, padx=5, pady=5, width=4, font=("Arial", 10),
                                command=lambda d=day: select_day(d),
                                relief='groove', bg='#FFEB99', activebackground='#FFD700')
            lbl.grid(row=r + 1, column=c)

# 切换到前一个月
def prev_month():
    global year, month
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    update_calendar(year, month)

# 切换到下一个月
def next_month():
    global year, month
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    update_calendar(year, month)

# 切换到前一年
def prev_year():
    global year
    year -= 1
    update_calendar(year, month)

# 切换到下一年
def next_year():
    global year
    year += 1
    update_calendar(year, month)

# 更新选中日期并显示日程
def select_day(day):
    global selected_day
    selected_day = day
    current_date_label.config(text=f"{year}年{month}月{selected_day}日")
    show_schedule(day)

# 显示并加载日程
def show_schedule(day):
    schedule_text.delete(1.0, tk.END)
    filename = f"{schedule_dir}/{year}_{month}_{day}.txt"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            schedule_text.insert(tk.END, content)
    else:
        schedule_text.insert(tk.END, f"{year}年{month}月{day}日的日程：\n")

# 保存当前日期的日程
def save_schedule():
    filename = f"{schedule_dir}/{year}_{month}_{selected_day}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        content = schedule_text.get(1.0, tk.END).strip()
        file.write(content)

# 粘贴复制内容到日程
# 粘贴的逻辑是LLM分析剪贴板内容是否为行程内容，是的话调用这个函数
def paste_content_to_calendar():
    response = messagebox.askyesno("提示", "是否要读取复制内容至日历")
    try:
        clipboard_content = root.clipboard_get()
        schedule_text.insert(tk.END, clipboard_content)
    except tk.TclError:
        messagebox.showerror("错误", "剪贴板中没有内容")

# 日历框架
cal_frame = tk.Frame(root, bg='#FFFACD')  # 日历框架背景设置为淡黄色
cal_frame.pack()

# 创建按钮框架
btn_frame = tk.Frame(root, bg='#FFFACD')  # 按钮框架背景设置为淡黄色
btn_frame.pack(pady=10)

# 创建年份和月份切换的按钮框架
year_btn_frame = tk.Frame(root, bg='#FFFACD')
year_btn_frame.pack(pady=5)

# 前一年和下一年按钮
prev_year_btn = tk.Button(year_btn_frame, text="上一年", command=prev_year, relief='groove', bg='#FFEB99', activebackground='#FFD700', font=("Arial", 10))
prev_year_btn.pack(side='left', padx=10)

next_year_btn = tk.Button(year_btn_frame, text="下一年", command=next_year, relief='groove', bg='#FFEB99', activebackground='#FFD700', font=("Arial", 10))
next_year_btn.pack(side='left', padx=10)

# 前一个月和下一个月按钮
prev_btn = tk.Button(btn_frame, text="前一个月", command=prev_month, relief='groove', bg='#FFEB99', activebackground='#FFD700', font=("Arial", 10))
prev_btn.pack(side='left', padx=10)

next_btn = tk.Button(btn_frame, text="后一个月", command=next_month, relief='groove', bg='#FFEB99', activebackground='#FFD700', font=("Arial", 10))
next_btn.pack(side='left', padx=10)

# 默认显示当前日期的日程
schedule_label = tk.Label(root, text="日程表", font=bold_font, bg='#FFFACD')
schedule_label.pack()

# 创建文本框用于显示选中的日期日程
schedule_text = tk.Text(root, height=8, width=50, font=("Arial", 10), wrap='word', padx=10, pady=10)
schedule_text.pack(pady=5)
show_schedule(selected_day)  # 默认显示今天的日程

# 保存按钮（去除阴影效果）
save_btn = tk.Button(root, text="保存日程", command=save_schedule, relief='groove', bg='#FFEB99', activebackground='#FFD700', font=("Arial", 10))
save_btn.pack(pady=5)

# 粘贴复制内容按钮
paste_btn = tk.Button(root, text="粘贴复制内容", command=paste_content_to_calendar, relief='groove', bg='#FFEB99', activebackground='#FFD700', font=("Arial", 10))
paste_btn.pack(pady=5)

# 初始化日历
update_calendar(year, month)

# 运行主循环
root.mainloop()