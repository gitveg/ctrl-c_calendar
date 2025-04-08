import tkinter as tk
from tkinter import ttk
from datetime import datetime,timedelta
import calendar
import os
from tkinter import messagebox
import json
import requests
import re
import audit_log

# 创建主窗口
root = tk.Tk()
root.title("日历程序")
root.geometry("400x700")
root.configure(bg='#FFFACD')  # 设置背景为淡黄色
root.resizable(False, False)  # 固定窗口大小

# 获取当前日期
now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
year = now.year
month = now.month
# 获取当前日期
weekday =  now.weekday()
# 将数字转换为周几的名称
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
weekday_name = days[weekday]
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

# 定义API的URL
API_URL = "http://222.20.126.129:11434/api/generate"

# 模拟的函数来生成请求数据
def http_post_generate(post_data, context):
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "flag": "libcurl",
        "Accept-Encoding": "gzip, deflate, br"
    }

    # 发起POST请求
    response = requests.post(API_URL, headers=headers, data=post_data,timeout=10)
    
    # 如果请求成功，处理返回的数据
    if response.status_code == 200:
        # print(f"code: {response.status_code}")
        response_json = response.json()

        # 打印调试信息
        print(f"AI response: {response_json['response']}")
        # 更新上下文
        context[:] = response_json["context"]  # 更新context
        return response_json['response']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# 主函数
def LLM_func(propt_str):
    # 输入提示词和问题
    hint_for_judge_str="\n上述的信息能够转化为日程信息吗，如果能回复\"Yes\",否则回复\"No\"。"
    hint_str = f"今天是{now_str}\n，{weekday_name}. \
                 分析发给你的信息，回复的具体格式:\"具体时间：具体时间如某年某月某日，几点几分，早上还是晚上\n地点:地点信息\n内容:内容信息\nEND\"。\n \
                 如果信息中仅指明了星期几，则默认是在本周，那你需要根据当天的星期数来计算日期。 \n \
                 如果是线上的将地点替换为会议号或其它相关链接且链接的含义或者内容要写明。\n \
                 如果是一个时间段则具体时间部分显示一段时间,且格式按照xx年xx月xx日-xx年xx月xx日，例如2024年12月23日-2025年1月1日。 \
                 如果有具体的时分，按照如\"11:00\"的格式回复。"
    # hint_of_data=f"现在的时间是{now_str}\n。分析发给你的日程信息，识别其中的年月日若无年或月可省略，回复格式为：\"xx年xx月xx日，比如2021年3月4日\";若无年月日则识别例如\"今天\"\"明天\"\"后天\"的字并直接回复"
    hint_of_data = f"今天是{now_str}\n，{weekday_name}。\
                     分析发给你的日程信息，结合现在的时间，给出日程的年月日，\
                     格式严格为\"xx年xx月xx日\"，比如2021年3月4日\" "
    # 定义上下文
    context = []

    hint_for_judge_str=propt_str+hint_for_judge_str

    # 准备POST请求体的内容
    post_body = {
        "model": "llama3.1",  # 选择的大模型
        "prompt": hint_for_judge_str,  # 转换提示词为UTF-8
        "stream": False,  # 以非流式（不必在意的参数）
        "context": context  # 用于保存对话的上下文
    }

    # 将请求体转为JSON格式
    post_data = json.dumps(post_body, ensure_ascii=False).encode('utf-8')

    # 调用API
    judge=http_post_generate(post_data, context)


    if judge[:3]=="Yes":
    # if 1:
        # 准备POST请求体的内容
        # hint_str+=propt_str
        post_body = {
            "model": "llama3.1",  # 选择的大模型
            "prompt": hint_str,  # 转换提示词为UTF-8
            "stream": False,  # 以非流式（不必在意的参数）
            "context": context  # 用于保存对话的上下文
        }

        # 将请求体转为JSON格式
        post_data = json.dumps(post_body, ensure_ascii=False).encode('utf-8')

        # 调用API
        response=http_post_generate(post_data, context)
        
        print(f"response: {response}")
        print()

        # 获取日期信息，为了保存日程
        post_body = {
            "model": "llama3.1",  # 选择的大模型
            "prompt": hint_of_data,  # 转换提示词为UTF-8
            "stream": False,  # 以非流式（不必在意的参数）
            "context": context  # 用于保存对话的上下文
        }

        # 将请求体转为JSON格式
        post_data = json.dumps(post_body, ensure_ascii=False).encode('utf-8')

        # 调用API
        date=http_post_generate(post_data, context)

        print(f"date: {date}")
        print()
        return 1,response,date
    else:
        print("不是日志信息")
        return 0,0,0

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
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            content = schedule_text.get(1.0, tk.END).strip()
            file.write(content)
        messagebox.showinfo("保存成功", "日程已保存！")
    except Exception as e:
        messagebox.showerror("保存失败", f"保存日程时出错 ：{str(e)}")

# 保存LLM分析的日程信息
def save_LLM_schedule(y,m,d,message):
    filename = f"{schedule_dir}/{y}_{m}_{d}.txt"
    # 判断文件是否存在
    if os.path.exists(filename): #如果文件存在，直接追加
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(message)

    else:   #如果文件不存在，则先创建并输入类似”2024年9月25日的日程：“
        with open(filename, 'w', encoding='utf-8') as file:
            message=f"{y}年{m}月{d}日的日程:\n"+message
            file.write(message)


# 处理日期信息
def parse_date(message):
    # 获取今天的日期
    today = datetime.now().date()
    if(message=="今天"):
        return today.year,today.month,today.day
    elif message=="明天":
        tomorrow = today + timedelta(days=1)
        return tomorrow.year,tomorrow.month,tomorrow.day+1
    elif message=="后天":
        hou_tian = today + timedelta(days=2)
        return hou_tian.year,hou_tian.month,hou_tian.day+1
    
    # 获取当前年份
    current_year = datetime.now().year

    # 使用正则表达式提取年、月、日
    # 1. 完整的 "年-月-日" 格式
    match_full = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', message)

    if match_full:
        # 如果匹配到年份、月份、日期
        year = int(match_full.group(1))  # 提取年
        month = int(match_full.group(2))  # 提取月
        day = int(match_full.group(3))  # 提取日
        return year,month,day
    # 2. 只有 "月-日" 格式
    elif re.match(r'(\d{1,2})月(\d{1,2})日', message):
        match_month_day = re.match(r'(\d{1,2})月(\d{1,2})日', message)
        year = current_year  # 如果没有年份，则使用当前年份
        month = int(match_month_day.group(1))  # 提取月
        day = int(match_month_day.group(2))  # 提取日
        return year,month,day
    # 3. 只有 "月" 格式
    elif re.match(r'(\d{1,2})月', message):
        match_month = re.match(r'(\d{1,2})月', message)
        year = current_year  # 如果没有年份，则使用当前年份
        month = int(match_month.group(1))  # 提取月
        day = 1  # 如果没有日期，则默认设置为 1 号
        return year,month,day
    # 3. 只有 "日" 格式
    elif re.match(r'(\d{1,2})日', message):
        match_day = re.match(r'(\d{1,2})日', message)
        year = current_year  # 如果没有年份，则使用当前年份
        month = 1  # 默认为1
        day = int(match_day.group(2))
        return year,month,day
    else:
        # 如果没有有效的日期格式
        # print("日期格式不正确")
        year = month = day = None
        return year,month,day

# 粘贴复制内容到日程
# 粘贴的逻辑是LLM分析剪贴板内容是否为行程内容，是的话调用这个函数
# 修改了一下逻辑，该功能主要是用来让用户能够通过AI来提取剪贴板中的日程信息
def paste_content_to_calendar():
    response = messagebox.askyesno("提示", "是否要读取复制内容至日历")
    if(response):
        try:
            clipboard_content = root.clipboard_get()
            flag,LLM_response,date=LLM_func(clipboard_content)   #flag为1表示是日志信息，0表示不是日志信息
            if flag==1:
                response=messagebox.askyesno("AI分析的日程信息是否合理",LLM_response[:-3])
                if response==1: #如果用户认为合理则记录一个日程文件中
                    pattern = r"(\b\d{1,2}:\d{2}\b)"  # 提取时间
                    match = re.search(pattern, LLM_response)
                    time=""
                    if match:
                        time=match.group(0)

                    pattern = r"地点[:：]?\s*(.*?)\s*内容[:：]?\s*(.*)" # 提取地点和内容
                    match = re.search(pattern, LLM_response)
                    print(match)
                    location=""
                    content=""
                    if match:
                        # 提取地点和内容
                        location = match.group(1).strip()  # 去除前后空格
                        content = match.group(2).strip()  # 去除前后空格

                    # 正则表达式匹配“xx年xx月xx日-xx年xx月xx日”
                    pattern = r"(\d{4})年(\d{1,2})月(\d{1,2})日-(\d{4})年(\d{1,2})月(\d{1,2})日"
                    # 使用re.search()进行匹配
                    match = re.search(pattern, LLM_response)
                    print(match)
                    if match:
                        # 提取开始和结束日期
                        start_year = int(match.group(1))  # 将开始年份转为整数
                        start_month = int(match.group(2))  # 将开始月份转为整数
                        start_day = int(match.group(3))  # 将开始日期转为整数

                        end_year = int(match.group(4))  # 将结束年份转为整数
                        end_month = int(match.group(5))  # 将结束月份转为整数
                        end_day = int(match.group(6))  # 将结束日期转为整数

                        # 循环将日程记录到时间段中
                        for y in range(start_year,end_year+1):
                            for m in range(start_month,end_month+1):
                                for d in range(start_day,end_day+1):
                                    save_content=f"具体时间：{time}\n地点：{location}\n内容：{content}"
                                    save_LLM_schedule(y,m,d,save_content)
                    else:
                        y,m,d=parse_date(date)
                        if y!=None and m!=None and d!=None:
                            print(f"{y}.{m}.{d}")
                            save_LLM_schedule(y,m,d,LLM_response[:-3])
                # else: #用户可以对内容进行一定的修改再保存

                # schedule_text.insert(tk.END, LLM_response[:-3])
            else:
                messagebox.showerror("错误","剪贴板中不包含日程信息")
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
paste_btn = tk.Button(root, text="粘贴复制内容给AI分析", command=paste_content_to_calendar, relief='groove', bg='#FFEB99', activebackground='#FFD700', font=("Arial", 10))
paste_btn.pack(pady=5)

# 初始化日历
update_calendar(year, month)

# 运行主循环
root.mainloop()
