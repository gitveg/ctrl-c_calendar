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

# 全局变量
year = datetime.now().year
month = datetime.now().month
selected_day = datetime.now().day
schedule_dir = "schedules"

# 自定义颜色
COLORS = {
    'primary': '#4A90E2',
    'secondary': '#50E3C2',
    'success': '#7ED321',
    'danger': '#FF4D4F',
    'warning': '#F5A623',
    'background': '#F8F9FA',
    'card': '#FFFFFF',
    'text': '#2C3E50',
    'text_light': '#7F8C8D',
    'border': '#E0E0E0',
    'hover': '#F0F7FF',
    'today': '#4A90E2',
    'schedule': '#7ED321',
    'weekend': '#FF4D4F'
}

# 自定义字体
title_font = ("Microsoft YaHei UI", 20, "bold")
bold_font = ("Microsoft YaHei UI", 14, "bold")
normal_font = ("Microsoft YaHei UI", 12)

# 安全配置
class SecurityConfig:
    MAX_LOGIN_ATTEMPTS = 3
    SESSION_TIMEOUT = 1800  # 30分钟
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    ALLOWED_FILE_TYPES = ['.txt']
    MAX_CONTENT_LENGTH = 10000  # 字符数
    API_TIMEOUT = 15  # API请求超时时间（秒）

# 用户会话管理
class UserSession:
    def __init__(self):
        self.last_activity = datetime.now()
        self.login_attempts = 0
        self.is_locked = False
    
    def update_activity(self):
        self.last_activity = datetime.now()

    def check_expiry(self):
        return (datetime.now() - self.last_activity).total_seconds() > SecurityConfig.SESSION_TIMEOUT

    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
            self.is_locked = True

    def reset(self):
        self.last_activity = datetime.now()
        self.login_attempts = 0
        self.is_locked = False

# 创建用户会话实例
user_session = UserSession()

# 安全装饰器
def audit_operation(operation_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Performing {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Successfully completed {operation_name}")
                audit_log.log_operation(operation_name, "SUCCESS")
                return result
            except Exception as e:
                logger.error(f"Error in {operation_name}: {str(e)}")
                audit_log.log_operation(operation_name, "FAILURE", str(e))
                raise
        return wrapper
    return decorator

def check_session_expiry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if user_session.check_expiry():
            logger.warning("Session expired")
            messagebox.showwarning("安全警告", "会话已过期，请重新登录")
            return None
        user_session.update_activity()
        return func(*args, **kwargs)
    return wrapper

# API相关函数
@audit_operation("API请求")
def secure_api_request(url, headers, data, timeout=SecurityConfig.API_TIMEOUT):
    try:
        # 创建SSL上下文
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # 执行请求
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=timeout,
            verify=False
        )
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求错误: {str(e)}")
        raise

def http_post_generate(post_data, context):
    try:
        print("准备发送HTTP POST请求...")
        # 处理不同类型的数据
        if context == "分析日程":
            url = "http://222.20.126.129:11434/api/generate"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama2",
                "prompt": post_data,
                "stream": False
            }
            
        else:
            logger.error("未知的请求上下文")
            raise ValueError("未知的请求上下文")
            
        print("发送请求...")
        print(f"URL: {url}")
        print(f"数据: {data}")
        
        response = secure_api_request(url, headers, data)
        print("请求成功")
        return response
    except Exception as e:
        logger.error(f"HTTP POST请求失败: {str(e)}")
        print(f"请求失败: {str(e)}")
        raise

# 日历功能函数
@check_session_expiry
def LLM_func(propt_str):
    # 输入提示词和问题
    try:
        print("分析文本是否包含日程信息...")
        full_prompt = f"""
请分析以下文本是否包含日程信息。
如果包含日程信息，请提取出日期、时间、地点、事项等信息，并以JSON格式返回。
如果文本不包含日程信息，请返回"false"。

文本内容：{propt_str}
"""
        response = http_post_generate(full_prompt, "分析日程")
        print("获取响应结果")
        print(response)
        
        if isinstance(response, dict) and 'response' in response:
            result = response['response'].strip()
            print(f"收到结果: {result}")
            
            # 检查是否为false
            if result.lower() == 'false':
                return False, None, None
                
            # 尝试解析JSON
            try:
                # 提取JSON部分
                json_match = re.search(r'({.+})', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    
                    # 提取信息
                    content = ""
                    if 'date' in data:
                        date = data['date']
                    else:
                        date = None
                        
                    if 'time' in data:
                        content += f"时间: {data['time']}\n"
                    if 'location' in data:
                        content += f"地点: {data['location']}\n"
                    if 'event' in data:
                        content += f"事项: {data['event']}\n"
                    if 'description' in data:
                        content += f"描述: {data['description']}\n"
                    if 'content' in data:
                        content += f"{data['content']}\n"
                        
                    return True, content, date
                else:
                    # 如果无法提取JSON，将整个结果作为内容返回
                    return True, result, None
            except json.JSONDecodeError as e:
                logger.error(f"解析JSON错误: {str(e)}")
                print(f"解析JSON错误: {str(e)}")
                # 如果无法解析为JSON，将整个结果作为内容返回
                if result.lower() != 'false':
                    return True, result, None
                return False, None, None
        
        return False, None, None
    except Exception as e:
        logger.error(f"LLM功能错误: {str(e)}")
        print(f"LLM功能错误: {str(e)}")
        messagebox.showerror("错误", f"分析失败: {str(e)}")
        return False, None, None

def parse_date(message):
    # 获取今天的日期
    today = datetime.now()
    current_year = today.year
    current_month = today.month
    current_day = today.day
    
    # 尝试提取年月日信息
    year_pattern = r'(\d{4})年'
    month_pattern = r'(\d{1,2})月'
    day_pattern = r'(\d{1,2})日'
    date_pattern = r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
    
    # 提取年月日
    year_match = re.search(year_pattern, message)
    month_match = re.search(month_pattern, message)
    day_match = re.search(day_pattern, message)
    date_match = re.search(date_pattern, message)
    
    year = None
    month = None
    day = None
    
    # 优先使用完整日期格式
    if date_match:
        year = int(date_match.group(1))
        month = int(date_match.group(2))
        day = int(date_match.group(3))
    else:
        # 单独提取年月日
        if year_match:
            year = int(year_match.group(1))
        else:
            year = current_year
            
        if month_match:
            month = int(month_match.group(1))
        else:
            month = current_month
            
        if day_match:
            day = int(day_match.group(1))
        else:
            day = current_day
    
    # 确保日期有效
    try:
        if month < 1 or month > 12:
            month = current_month
        
        max_days = calendar.monthrange(year, month)[1]
        if day < 1 or day > max_days:
            day = min(current_day, max_days)
            
        return year, month, day
    except Exception as e:
        logger.error(f"解析日期错误: {str(e)}")
        return current_year, current_month, current_day

@audit_operation("AI分析日程保存")
@check_session_expiry
def save_LLM_schedule(y, m, d, message):
    try:
        # 创建日程目录
        os.makedirs(schedule_dir, exist_ok=True)
        
        # 构建文件名
        filename = f"{schedule_dir}/{y}_{m}_{d}.txt"
        
        # 安全检查
        if len(message) > SecurityConfig.MAX_CONTENT_LENGTH:
            logger.warning(f"内容超出最大长度限制: {len(message)} > {SecurityConfig.MAX_CONTENT_LENGTH}")
            messagebox.showwarning("安全警告", "内容过长，已被截断")
            message = message[:SecurityConfig.MAX_CONTENT_LENGTH]
            
        # 检测潜在恶意内容
        if re.search(r'<script|<iframe|javascript:|eval\(', message, re.IGNORECASE):
            logger.warning(f"检测到潜在的恶意内容")
            messagebox.showwarning("安全警告", "检测到潜在的恶意内容，请检查您的输入")
            return
            
        # 保存文件
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(message)
            
        logger.info(f"成功保存日程: {filename}")
        return True
    except Exception as e:
        logger.error(f"保存日程错误: {str(e)}")
        messagebox.showerror("错误", f"保存日程时出错: {str(e)}")
        return False

# 日历操作函数
@check_session_expiry
def prev_month():
    global year, month
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    update_calendar(year, month)

@check_session_expiry
def next_month():
    global year, month
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    update_calendar(year, month)

@check_session_expiry
def prev_year():
    global year
    year -= 1
    update_calendar(year, month)

@check_session_expiry
def next_year():
    global year
    year += 1
    update_calendar(year, month)

@check_session_expiry
def select_day(day):
    global selected_day
    selected_day = day
    current_date_label.config(text=f"{year}年{month}月{selected_day}日")
    show_schedule()

@check_session_expiry
def show_schedule(day=None):
    """显示选中日期的日程"""
    global selected_day
    
    if day is not None:
        selected_day = day
    
    if selected_day:
        try:
            with open(os.path.join(schedule_dir, f"{year}_{month}_{selected_day}.txt"), 'r', encoding='utf-8') as f:
                content = f.read()
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, content)
        except FileNotFoundError:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, "无日程安排")
    else:
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "请选择日期")

@audit_operation("保存日程")
@check_session_expiry
def save_schedule(content):
    filename = f"{schedule_dir}/{year}_{month}_{selected_day}.txt"
    try:
        if re.search(r'<script|<iframe|javascript:|eval\(', content, re.IGNORECASE):
            logger.warning(f"检测到潜在的恶意内容")
            messagebox.showwarning("安全警告", "检测到潜在的恶意内容，请检查您的输入")
            return
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        messagebox.showinfo("保存成功", "日程已保存！")
        update_calendar(year, month)
    except Exception as e:
        logger.error(f"保存日程错误: {str(e)}")
        messagebox.showerror("保存失败", f"保存日程时出错 ：{str(e)}")

# 剪贴板相关函数
@audit_operation("AI分析剪贴板")
@check_session_expiry
def paste_content_to_calendar():
    try:
        # 获取剪贴板内容
        content = root.clipboard_get()
        if not content:
            messagebox.showinfo("提示", "剪贴板为空")
            return
            
        print(f"获取剪贴板内容: {content[:50]}...")
        
        # 调用LLM分析
        is_schedule, response, date = LLM_func(content)
        
        if is_schedule:
            print("识别为日程信息")
            # 解析日期
            y, m, d = parse_date(date if date else content)
            
            # 清空预览区域
            ai_preview_text.delete(1.0, tk.END)
            
            # 显示预览内容
            preview_content = f"识别日期：{y}年{m}月{d}日\n\n"
            preview_content += f"识别内容：\n{response}\n\n"
            preview_content += "请检查识别结果，确认无误后点击下方按钮保存。"
            
            ai_preview_text.insert(tk.END, preview_content)
            
            # 切换到AI识别标签页
            right_notebook.select(ai_frame)
        else:
            print("非日程信息")
            messagebox.showinfo("提示", "剪贴板内容不是有效的日程信息")
    except Exception as e:
        logger.error(f"粘贴内容出错: {str(e)}")
        messagebox.showerror("错误", f"粘贴内容时出错: {str(e)}")

def save_ai_result():
    try:
        # 获取预览内容
        preview_content = ai_preview_text.get(1.0, tk.END).strip()
        if not preview_content:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
            
        # 提取日期
        date_match = re.search(r'识别日期：(\d{4})年(\d{1,2})月(\d{1,2})日', preview_content)
        if not date_match:
            messagebox.showwarning("警告", "无法提取日期信息")
            return
            
        y = int(date_match.group(1))
        m = int(date_match.group(2))
        d = int(date_match.group(3))
        
        # 提取内容
        content_match = re.search(r'识别内容：\n(.*?)(?:\n\n请检查识别结果|$)', preview_content, re.DOTALL)
        if not content_match:
            messagebox.showwarning("警告", "无法提取内容信息")
            return
            
        content = content_match.group(1).strip()
        
        # 保存日程
        if save_LLM_schedule(y, m, d, content):
            # 更新日历显示
            if y == year and m == month:
                update_calendar(year, month)
                if d == selected_day:
                    show_schedule()
            
            # 切换到日程编辑标签页
            right_notebook.select(edit_frame)
            messagebox.showinfo("成功", "日程已保存！")
    except Exception as e:
        logger.error(f"保存AI识别结果出错: {str(e)}")
        messagebox.showerror("错误", f"保存AI识别结果时出错: {str(e)}")

@audit_operation("AI格式化日程")
@check_session_expiry
def format_schedule(content):
    try:
        if not content.strip():
            messagebox.showwarning("警告", "请输入要格式化的内容")
            return
            
        # 调用LLM分析
        is_schedule, response, date = LLM_func(content)
        
        if is_schedule:
            # 解析日期
            y, m, d = parse_date(date if date else content)
            
            # 清空预览区域
            ai_preview_text.delete(1.0, tk.END)
            
            # 显示预览内容
            preview_content = f"识别日期：{y}年{m}月{d}日\n\n"
            preview_content += f"格式化内容：\n{response}\n\n"
            preview_content += "请检查格式化结果，确认无误后点击下方按钮保存。"
            
            ai_preview_text.insert(tk.END, preview_content)
            
            # 切换到AI识别标签页
            right_notebook.select(ai_frame)
        else:
            messagebox.showinfo("提示", "输入内容不是有效的日程信息")
    except Exception as e:
        logger.error(f"格式化日程出错: {str(e)}")
        messagebox.showerror("错误", f"格式化日程时出错: {str(e)}")

@check_session_expiry
def update_calendar(year, month):
    for widget in cal_frame.winfo_children():
        widget.destroy()

    month_names = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
    month_label = tk.Label(cal_frame, text=f"{year}年 {month_names[month-1]}", 
                          font=bold_font, bg=COLORS['card'], fg=COLORS['text'])
    month_label.grid(row=0, column=0, columnspan=7, pady=15)

    cal = calendar.monthcalendar(year, month)
    days = ['一', '二', '三', '四', '五', '六', '日']
    
    for i, day in enumerate(days):
        lbl = tk.Label(cal_frame, text=day, padx=15, pady=10, 
                      bg=COLORS['background'], fg=COLORS['text_light'], font=bold_font)
        lbl.grid(row=1, column=i, sticky='ew')

    today = datetime.now().date()
    
    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            if day == 0:
                lbl = tk.Label(cal_frame, text='', padx=15, pady=10, bg=COLORS['card'])
            else:
                has_schedule = os.path.exists(f"{schedule_dir}/{year}_{month}_{day}.txt")
                
                if today.year == year and today.month == month and today.day == day:
                    bg_color = COLORS['today']
                    fg_color = 'white'
                elif has_schedule:
                    bg_color = COLORS['schedule']
                    fg_color = 'white'
                elif c >= 5:  # 周末
                    bg_color = COLORS['background']
                    fg_color = COLORS['weekend']
                else:
                    bg_color = COLORS['background']
                    fg_color = COLORS['text']
                
                lbl = tk.Button(cal_frame, text=day, padx=15, pady=10, width=4,
                              command=lambda d=day: select_day(d),
                              font=normal_font, bg=bg_color, fg=fg_color,
                              activebackground=COLORS['hover'], relief='flat',
                              cursor='hand2')
            lbl.grid(row=r + 2, column=c, padx=2, pady=2, sticky='ew')

    for i in range(7):
        cal_frame.grid_columnconfigure(i, weight=1)

# 创建主窗口
print("正在创建主窗口...")
try:
    root = tk.Tk()
    print("Tk()创建成功")
    root.title("智能日历助手")
    root.geometry("1200x800")  # 增大窗口尺寸
    root.configure(bg=COLORS['background'])  # 使用更柔和的背景色
    root.resizable(True, True)  # 允许调整窗口大小
    print("设置窗口大小成功")
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
weekday = now.weekday()
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
weekday_name = days[weekday]
selected_day = now.day

# 创建主框架
main_frame = tk.Frame(root, bg=COLORS['background'])
main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

# 创建顶部标题栏
header_frame = tk.Frame(main_frame, bg=COLORS['card'], bd=0, relief='flat')
header_frame.pack(fill=tk.X, pady=(0, 20))

app_title = tk.Label(header_frame, text="智能日历助手", font=title_font, 
                    bg=COLORS['card'], fg=COLORS['text'])
app_title.pack(side=tk.LEFT, padx=20, pady=20)

current_date_label = tk.Label(header_frame, 
                            text=f"今天是{year}年{month}月{selected_day}日 {weekday_name}", 
                            font=bold_font, bg=COLORS['card'], fg=COLORS['text_light'])
current_date_label.pack(side=tk.RIGHT, padx=20, pady=20)

# 创建内容区域
content_frame = tk.Frame(main_frame, bg=COLORS['background'])
content_frame.pack(fill=tk.BOTH, expand=True)

# 创建左侧日历区域
left_frame = tk.Frame(content_frame, bg=COLORS['card'], bd=0, relief='flat')
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

# 创建日历控制按钮框架
control_frame = tk.Frame(left_frame, bg=COLORS['card'])
control_frame.pack(fill=tk.X, pady=20, padx=20)

# 年份控制按钮
year_btn_frame = tk.Frame(control_frame, bg=COLORS['card'])
year_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

prev_year_btn = tk.Button(year_btn_frame, text="◀ 上一年", command=prev_year, 
                         font=normal_font, bg=COLORS['primary'], fg='white', 
                         activebackground=COLORS['primary'], relief='flat',
                         padx=20, pady=8, cursor='hand2')
prev_year_btn.pack(side=tk.LEFT, padx=5)

year_label = tk.Label(year_btn_frame, text=f"{year}年", font=bold_font,
                     bg=COLORS['card'], fg=COLORS['text'])
year_label.pack(side=tk.LEFT, expand=True)

next_year_btn = tk.Button(year_btn_frame, text="下一年 ▶", command=next_year,
                         font=normal_font, bg=COLORS['primary'], fg='white',
                         activebackground=COLORS['primary'], relief='flat',
                         padx=20, pady=8, cursor='hand2')
next_year_btn.pack(side=tk.RIGHT, padx=5)

# 月份控制按钮
month_btn_frame = tk.Frame(control_frame, bg=COLORS['card'])
month_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

prev_month_btn = tk.Button(month_btn_frame, text="◀ 上月", command=prev_month,
                          font=normal_font, bg=COLORS['primary'], fg='white',
                          activebackground=COLORS['primary'], relief='flat',
                          padx=20, pady=8, cursor='hand2')
prev_month_btn.pack(side=tk.LEFT, padx=5)

month_label = tk.Label(month_btn_frame, text=f"{month}月", font=bold_font,
                      bg=COLORS['card'], fg=COLORS['text'])
month_label.pack(side=tk.LEFT, expand=True)

next_month_btn = tk.Button(month_btn_frame, text="下月 ▶", command=next_month,
                          font=normal_font, bg=COLORS['primary'], fg='white',
                          activebackground=COLORS['primary'], relief='flat',
                          padx=20, pady=8, cursor='hand2')
next_month_btn.pack(side=tk.RIGHT, padx=5)

# 日历框架
cal_frame = tk.Frame(left_frame, bg=COLORS['card'])
cal_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# 创建右侧日程区域
right_frame = tk.Frame(content_frame, bg=COLORS['card'], padx=20, pady=20)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# 创建标签页
notebook = ttk.Notebook(right_frame)
notebook.pack(fill=tk.BOTH, expand=True)

# 日程编辑标签页
edit_frame = tk.Frame(notebook, bg=COLORS['card'])
notebook.add(edit_frame, text="日程编辑")

# 创建标题标签
schedule_title = tk.Label(edit_frame, text="日程内容", font=bold_font,
                        bg=COLORS['card'], fg=COLORS['text'])
schedule_title.pack(padx=20, pady=10)

# 创建文本区域 - 减小高度
text_area = tk.Text(edit_frame, wrap=tk.WORD, height=8, font=normal_font,
                   bg='white', fg=COLORS['text'], relief='flat',
                   padx=10, pady=10)
text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# 创建按钮框架
button_frame = tk.Frame(edit_frame, bg=COLORS['card'])
button_frame.pack(fill=tk.X, padx=20, pady=10)

# 保存按钮 - 增加高度和可见性
save_btn = tk.Button(button_frame, text="保存日程", 
                    command=lambda: save_schedule(text_area.get(1.0, tk.END)),
                    font=bold_font, bg=COLORS['success'], fg='white',
                    activebackground=COLORS['success'], relief='raised',
                    width=15, height=2, padx=20, pady=10, cursor='hand2')
save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

# AI格式化按钮 - 增加高度和可见性
format_btn = tk.Button(button_frame, text="AI格式化", 
                      command=lambda: format_schedule(text_area.get(1.0, tk.END)),
                      font=bold_font, bg=COLORS['secondary'], fg='white',
                      activebackground=COLORS['secondary'], relief='raised',
                      width=15, height=2, padx=20, pady=10, cursor='hand2')
format_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)

# AI识别标签页
ai_frame = tk.Frame(notebook, bg=COLORS['card'])
notebook.add(ai_frame, text="AI智能识别")

# 创建AI识别按钮 - 增加高度和可见性
ai_btn = tk.Button(ai_frame, text="识别剪贴板内容", 
                  command=paste_content_to_calendar,
                  font=bold_font, bg=COLORS['primary'], fg='white',
                  activebackground=COLORS['primary'], relief='raised',
                  width=20, height=2, padx=20, pady=10, cursor='hand2')
ai_btn.pack(padx=20, pady=20)

# 创建预览区域 - 减小高度
preview_label = tk.Label(ai_frame, text="识别结果预览", font=bold_font,
                        bg=COLORS['card'], fg=COLORS['text'])
preview_label.pack(padx=20, pady=10)

preview_text = tk.Text(ai_frame, wrap=tk.WORD, height=8, font=normal_font,
                      bg='white', fg=COLORS['text'], relief='flat',
                      padx=10, pady=10)
preview_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# 创建保存识别结果按钮 - 增加高度和可见性
save_ai_btn = tk.Button(ai_frame, text="保存识别结果", 
                       command=save_ai_result,
                       font=bold_font, bg=COLORS['success'], fg='white',
                       activebackground=COLORS['success'], relief='raised',
                       width=20, height=2, padx=20, pady=10, cursor='hand2')
save_ai_btn.pack(padx=20, pady=20)

# 初始化日历显示
update_calendar(year, month)

# 启动主循环
root.mainloop()
