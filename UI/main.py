print("程序开始执行...")

print("正在导入 tkinter...")
import tkinter as tk
print("tkinter 导入成功")

print("正在导入 ttk...")
from tkinter import ttk
print("ttk 导入成功")

print("正在导入 datetime...")
from datetime import datetime, timedelta
print("datetime 导入成功")

print("正在导入 calendar...")
import calendar
print("calendar 导入成功")

print("正在导入 os...")
import os
print("os 导入成功")

print("正在导入 messagebox...")
from tkinter import messagebox
print("messagebox 导入成功")

print("正在导入 json...")
import json
print("json 导入成功")

print("正在导入 requests...")
import requests
print("requests 导入成功")

print("正在导入 re...")
import re
print("re 导入成功")

print("正在导入 audit_log...")
import audit_log
print("audit_log 导入成功")

print("正在导入 hashlib...")
import hashlib
print("hashlib 导入成功")

print("正在导入 logging...")
import logging
print("logging 导入成功")

print("正在导入 socket...")
import socket
print("socket 导入成功")

print("正在导入 ssl...")
import ssl
print("ssl 导入成功")

print("正在导入 uuid...")
import uuid
print("uuid 导入成功")

print("正在导入 time...")
import time
print("time 导入成功")

print("正在导入 threading...")
import threading
print("threading 导入成功")

print("正在导入 base64...")
import base64
print("base64 导入成功")

print("正在导入 wraps...")
from functools import wraps
print("wraps 导入成功")

print("所有模块导入完成")

# 设置日志记录
print("正在配置日志...")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='calendar_app.log',
    filemode='a'
)
logger = logging.getLogger('calendar_app')
print("日志配置完成")

# 安全配置
class SecurityConfig:
    MAX_FAILED_ATTEMPTS = 3
    LOCKOUT_TIME = 300  # 5分钟锁定时间
    SESSION_TIMEOUT = 1800  # 30分钟会话超时
    API_TIMEOUT = 15  # API请求超时时间
    
    @staticmethod
    def hash_password(password, salt=None):
        if not salt:
            salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt + key
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        salt = stored_password[:32]
        stored_key = stored_password[32:]
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return new_key == stored_key

# 用户会话管理
class UserSession:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.last_activity = time.time()
        self.failed_attempts = 0
        self.locked_until = 0
    
    def update_activity(self):
        self.last_activity = time.time()
    
    def is_expired(self):
        return (time.time() - self.last_activity) > SecurityConfig.SESSION_TIMEOUT
    
    def is_locked(self):
        return time.time() < self.locked_until
    
    def record_failed_attempt(self):
        self.failed_attempts += 1
        if self.failed_attempts >= SecurityConfig.MAX_FAILED_ATTEMPTS:
            self.locked_until = time.time() + SecurityConfig.LOCKOUT_TIME
            logger.warning(f"Account locked due to multiple failed attempts. Session ID: {self.session_id}")
            return True
        return False

# 创建用户会话
current_session = UserSession()

# 安全装饰器 - 记录敏感操作
def audit_operation(operation_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Performing {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Successfully completed {operation_name}")
                # 记录审计日志
                audit_log.log_operation(operation_name, "SUCCESS")
                return result
            except Exception as e:
                logger.error(f"Error in {operation_name}: {str(e)}")
                audit_log.log_operation(operation_name, "FAILURE", str(e))
                raise
        return wrapper
    return decorator

# 安全装饰器 - 检查会话是否过期
def check_session_expiry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_session.is_expired():
            logger.warning("Session expired")
            messagebox.showwarning("安全警告", "会话已过期，请重新登录")
            return None
        current_session.update_activity()
        return func(*args, **kwargs)
    return wrapper

# 创建主窗口
print("正在创建主窗口...")
try:
    root = tk.Tk()
    print("Tk()创建成功")
    root.title("日历程序")
    print("设置标题成功")
    root.geometry("400x700")
    print("设置窗口大小成功")
    root.configure(bg='#F0F8FF')  # 设置背景为爱丽丝蓝
    print("设置背景颜色成功")
    root.resizable(False, False)  # 固定窗口大小
    print("设置窗口大小固定成功")
except Exception as e:
    print(f"创建主窗口时出错: {str(e)}")
    raise

# 设置应用图标
try:
    root.iconbitmap("calendar_icon.ico")
except Exception as e:
    print(f"无法加载应用图标: {str(e)}")
    logger.warning("无法加载应用图标")

# 获取当前日期
now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
year = now.year
month = now.month
# 获取当前日期
weekday = now.weekday()
# 将数字转换为周几的名称
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
weekday_name = days[weekday]
selected_day = now.day  # 默认选中今天

# 自定义字体
title_font = ("Helvetica", 14, "bold")
bold_font = ("Helvetica", 12, "bold")
normal_font = ("Helvetica", 10)

# 日程存储路径
schedule_dir = "schedules"
if not os.path.exists(schedule_dir):
    os.makedirs(schedule_dir)
    logger.info(f"Created schedule directory: {schedule_dir}")

# 创建一个样式对象
style = ttk.Style()
style.configure("TButton", font=normal_font, background="#E6E6FA")
style.configure("TLabel", font=normal_font, background="#F0F8FF")
style.configure("Title.TLabel", font=title_font, background="#F0F8FF")

# 显示当前日期标签
header_frame = tk.Frame(root, bg='#F0F8FF', pady=10)
header_frame.pack(fill=tk.X)

app_title = tk.Label(header_frame, text="智能日历助手", font=title_font, bg='#F0F8FF', fg='#4169E1')
app_title.pack()

current_date_label = tk.Label(header_frame, text=f"今天是{year}年{month}月{selected_day}日", font=bold_font, bg='#F0F8FF', fg='#000080')
current_date_label.pack(pady=5)

# 定义API的URL
API_URL = "http://222.20.126.129:11434/api/generate"

# 安全的API请求函数
@audit_operation("API请求")
def secure_api_request(url, headers, data, timeout=SecurityConfig.API_TIMEOUT):
    try:
        # 创建一个安全的SSL上下文
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # 发起POST请求
        response = requests.post(url, headers=headers, data=data, timeout=timeout)
        
        # 检查响应状态码
        if response.status_code == 200:
            return response
        else:
            logger.error(f"API请求失败: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求异常: {str(e)}")
        return None

# 模拟的函数来生成请求数据
def http_post_generate(post_data, context):
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "flag": "libcurl",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "CalendarApp/1.0",
        "X-Request-ID": str(uuid.uuid4())
    }

    # 发起POST请求
    response = secure_api_request(API_URL, headers, post_data, timeout=SecurityConfig.API_TIMEOUT)
    
    # 如果请求成功，处理返回的数据
    if response and response.status_code == 200:
        try:
            response_json = response.json()
            logger.info(f"AI response received successfully")
            # 打印调试信息
            print(f"AI response: {response_json['response']}")
            # 更新上下文
            context[:] = response_json["context"]  # 更新context
            return response_json['response']
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            messagebox.showerror("错误", "无法解析API响应")
            return None
    else:
        error_msg = "API请求失败" if not response else f"错误: {response.status_code}"
        logger.error(error_msg)
        messagebox.showerror("API错误", error_msg)
        return None

# 主函数
@check_session_expiry
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

    # 验证输入内容，防止注入攻击
    sanitized_prompt = re.sub(r'[<>]', '', propt_str)
    if sanitized_prompt != propt_str:
        logger.warning("检测到潜在的注入尝试")
        messagebox.showwarning("安全警告", "检测到不安全的输入内容")
        return 0, 0, 0

    hint_for_judge_str = sanitized_prompt + hint_for_judge_str

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
    judge = http_post_generate(post_data, context)
    
    if not judge:
        return 0, 0, 0

    if judge[:3] == "Yes":
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
        response = http_post_generate(post_data, context)
        
        if not response:
            return 0, 0, 0
            
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
        date = http_post_generate(post_data, context)
        
        if not date:
            return 0, 0, 0

        print(f"date: {date}")
        print()
        return 1, response, date
    else:
        logger.info("输入内容不是日程信息")
        print("不是日志信息")
        return 0, 0, 0

# 创建一个函数来更新日历
@check_session_expiry
def update_calendar(year, month):
    """
    更新日历显示，并重新绘制日历框。
    """
    for widget in cal_frame.winfo_children():
        widget.destroy()

    # 添加月份标题
    month_names = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
    month_label = tk.Label(cal_frame, text=f"{year}年 {month_names[month-1]}", font=bold_font, bg='#F0F8FF', fg='#4169E1')
    month_label.grid(row=0, column=0, columnspan=7, pady=5)

    cal = calendar.monthcalendar(year, month)
    days = ['一', '二', '三', '四', '五', '六', '日']
    
    # 添加星期标题
    for i, day in enumerate(days):
        lbl = tk.Label(cal_frame, text=day, padx=10, pady=5, bg='#F0F8FF', fg='#4169E1', font=bold_font)
        lbl.grid(row=1, column=i)

    # 获取今天的日期，用于高亮显示
    today = datetime.now().date()
    
    # 添加日期按钮
    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            if day == 0:
                lbl = tk.Label(cal_frame, text='', padx=10, pady=5, bg='#F0F8FF')
            else:
                # 检查是否有日程
                has_schedule = os.path.exists(f"{schedule_dir}/{year}_{month}_{day}.txt")
                
                # 设置按钮样式
                if today.year == year and today.month == month and today.day == day:
                    # 今天的日期
                    bg_color = '#FF6347'  # 红色
                    fg_color = 'white'
                elif has_schedule:
                    # 有日程的日期
                    bg_color = '#4682B4'  # 钢蓝色
                    fg_color = 'white'
                else:
                    # 普通日期
                    bg_color = '#E6E6FA'  # 淡紫色
                    fg_color = 'black'
                
                lbl = tk.Button(cal_frame, text=day, padx=5, pady=5, width=4, font=normal_font,
                                command=lambda d=day: select_day(d),
                                relief='groove', bg=bg_color, fg=fg_color, activebackground='#FFD700')
            lbl.grid(row=r + 2, column=c)

# 切换到前一个月
@check_session_expiry
def prev_month():
    global year, month
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    update_calendar(year, month)
    logger.info(f"切换到上一个月: {year}年{month}月")

# 切换到下一个月
@check_session_expiry
def next_month():
    global year, month
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    update_calendar(year, month)
    logger.info(f"切换到下一个月: {year}年{month}月")

# 切换到前一年
@check_session_expiry
def prev_year():
    global year
    year -= 1
    update_calendar(year, month)
    logger.info(f"切换到上一年: {year}年")

# 切换到下一年
@check_session_expiry
def next_year():
    global year
    year += 1
    update_calendar(year, month)
    logger.info(f"切换到下一年: {year}年")

# 更新选中日期并显示日程
@check_session_expiry
def select_day(day):
    global selected_day
    selected_day = day
    current_date_label.config(text=f"{year}年{month}月{selected_day}日")
    show_schedule(day)
    logger.info(f"选择日期: {year}年{month}月{day}日")

# 显示并加载日程
@check_session_expiry
def show_schedule(day):
    schedule_text.delete(1.0, tk.END)
    filename = f"{schedule_dir}/{year}_{month}_{day}.txt"
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
                schedule_text.insert(tk.END, content)
            logger.info(f"加载日程: {filename}")
        except Exception as e:
            logger.error(f"读取日程文件错误: {str(e)}")
            messagebox.showerror("错误", f"无法读取日程文件: {str(e)}")
    else:
        schedule_text.insert(tk.END, f"{year}年{month}月{day}日的日程：\n")

# 保存当前日期的日程
@audit_operation("保存日程")
@check_session_expiry
def save_schedule():
    filename = f"{schedule_dir}/{year}_{month}_{selected_day}.txt"
    try:
        content = schedule_text.get(1.0, tk.END).strip()
        
        # 检查内容是否包含潜在的恶意代码
        if re.search(r'<script|<iframe|javascript:|eval\(', content, re.IGNORECASE):
            logger.warning(f"检测到潜在的恶意内容")
            messagebox.showwarning("安全警告", "检测到潜在的恶意内容，请检查您的输入")
            return
            
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        messagebox.showinfo("保存成功", "日程已保存！")
        logger.info(f"日程保存成功: {filename}")
        
        # 更新日历显示，以反映有日程的日期
        update_calendar(year, month)
    except Exception as e:
        logger.error(f"保存日程错误: {str(e)}")
        messagebox.showerror("保存失败", f"保存日程时出错 ：{str(e)}")

# 保存LLM分析的日程信息
@audit_operation("AI分析日程保存")
@check_session_expiry
def save_LLM_schedule(y, m, d, message):
    filename = f"{schedule_dir}/{y}_{m}_{d}.txt"
    try:
        # 检查内容是否包含潜在的恶意代码
        if re.search(r'<script|<iframe|javascript:|eval\(', message, re.IGNORECASE):
            logger.warning(f"检测到潜在的恶意内容")
            messagebox.showwarning("安全警告", "检测到潜在的恶意内容，请检查AI生成的内容")
            return
            
        # 判断文件是否存在
        if os.path.exists(filename): #如果文件存在，直接追加
            with open(filename, 'a', encoding='utf-8') as file:
                file.write("\n" + message)
            logger.info(f"AI日程追加成功: {filename}")
        else:   #如果文件不存在，则先创建并输入类似"2024年9月25日的日程："
            with open(filename, 'w', encoding='utf-8') as file:
                message = f"{y}年{m}月{d}日的日程:\n" + message
                file.write(message)
            logger.info(f"AI日程创建成功: {filename}")
            
        # 如果当前显示的是这个日期，则刷新显示
        if y == year and m == month and d == selected_day:
            show_schedule(d)
            
        # 更新日历显示，以反映有日程的日期
        if y == year and m == month:
            update_calendar(year, month)
    except Exception as e:
        logger.error(f"保存AI日程错误: {str(e)}")
        messagebox.showerror("保存失败", f"保存AI日程时出错: {str(e)}")

# 处理日期信息
def parse_date(message):
    # 获取今天的日期
    today = datetime.now().date()
    if(message=="今天"):
        return today.year, today.month, today.day
    elif message=="明天":
        tomorrow = today + timedelta(days=1)
        return tomorrow.year, tomorrow.month, tomorrow.day
    elif message=="后天":
        hou_tian = today + timedelta(days=2)
        return hou_tian.year, hou_tian.month, hou_tian.day
    
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
        return year, month, day
    # 2. 只有 "月-日" 格式
    elif re.match(r'(\d{1,2})月(\d{1,2})日', message):
        match_month_day = re.match(r'(\d{1,2})月(\d{1,2})日', message)
        year = current_year  # 如果没有年份，则使用当前年份
        month = int(match_month_day.group(1))  # 提取月
        day = int(match_month_day.group(2))  # 提取日
        return year, month, day
    # 3. 只有 "月" 格式
    elif re.match(r'(\d{1,2})月', message):
        match_month = re.match(r'(\d{1,2})月', message)
        year = current_year  # 如果没有年份，则使用当前年份
        month = int(match_month.group(1))  # 提取月
        day = 1  # 如果没有日期，则默认设置为 1 号
        return year, month, day
    # 3. 只有 "日" 格式
    elif re.match(r'(\d{1,2})日', message):
        match_day = re.match(r'(\d{1,2})日', message)
        year = current_year  # 如果没有年份，则使用当前年份
        month = datetime.now().month  # 使用当前月份
        day = int(match_day.group(1))
        return year, month, day
    else:
        # 如果没有有效的日期格式
        logger.warning(f"无效的日期格式: {message}")
        year = month = day = None
        return year, month, day

# 粘贴复制内容到日程
# 粘贴的逻辑是LLM分析剪贴板内容是否为行程内容，是的话调用这个函数
# 修改了一下逻辑，该功能主要是用来让用户能够通过AI来提取剪贴板中的日程信息
@audit_operation("AI分析剪贴板")
@check_session_expiry
def paste_content_to_calendar():
    response = messagebox.askyesno("提示", "是否要读取复制内容至日历")
    if(response):
        try:
            # 获取剪贴板内容
            clipboard_content = root.clipboard_get()
            
            # 检查剪贴板内容长度
            if len(clipboard_content) > 5000:
                logger.warning("剪贴板内容过长")
                messagebox.showwarning("警告", "剪贴板内容过长，请减少内容后重试")
                return
                
            # 检查剪贴板内容是否包含潜在的恶意代码
            if re.search(r'<script|<iframe|javascript:|eval\(', clipboard_content, re.IGNORECASE):
                logger.warning("检测到剪贴板中的潜在恶意内容")
                messagebox.showwarning("安全警告", "检测到剪贴板中的潜在恶意内容")
                return
                
            # 显示加载提示
            loading_label = tk.Label(root, text="AI正在分析中...", font=bold_font, bg='#F0F8FF', fg='#4169E1')
            loading_label.pack(pady=5)
            root.update()
            
            # 调用AI分析
            flag, LLM_response, date = LLM_func(clipboard_content)
            
            # 移除加载提示
            loading_label.destroy()
            
            if flag == 1:
                response = messagebox.askyesno("AI分析的日程信息是否合理", LLM_response[:-3])
                if response == 1: #如果用户认为合理则记录一个日程文件中
                    pattern = r"(\b\d{1,2}:\d{2}\b)"  # 提取时间
                    match = re.search(pattern, LLM_response)
                    time = ""
                    if match:
                        time = match.group(0)

                    pattern = r"地点[:：]?\s*(.*?)\s*内容[:：]?\s*(.*)" # 提取地点和内容
                    match = re.search(pattern, LLM_response)
                    print(match)
                    location = ""
                    content = ""
                    if match:
                        # 提取地点和内容
                        location = match.group(1).strip()  # 去除前后空格
                        content = match.group(2).strip()  # 去除前后空格

                    # 正则表达式匹配"xx年xx月xx日-xx年xx月xx日"
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

                        # 创建开始和结束日期对象
                        start_date = datetime(start_year, start_month, start_day)
                        end_date = datetime(end_year, end_month, end_day)
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
print("开始运行主循环...")
root.mainloop()
print("主循环结束")
