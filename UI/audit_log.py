# audit_log.py
import sys
import logging

# 设置日志记录器
logging.basicConfig(filename="audit_log.txt", level=logging.INFO)

def audit_hook(event, args):
    # 记录所有敏感事件
    logging.info(f"Audit event: {event}, args: {args}")
    
    # 可选：打印控制台（调试时）
    print(f"[Audit] {event} | {args}")

# 添加到 audit 系统
sys.addaudithook(audit_hook)