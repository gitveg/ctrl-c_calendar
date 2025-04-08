# audit_log.py
import logging
from datetime import datetime

print("audit_log.py 开始执行...")

# 设置日志记录器
try:
    logging.basicConfig(filename="audit_log.txt", level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    print("日志配置成功")
except Exception as e:
    print(f"日志配置失败: {str(e)}")
    raise

def log_operation(operation_name, status, details=None):
    """记录操作到审计日志"""
    try:
        message = f"Operation: {operation_name} - Status: {status}"
        if details:
            message += f" - Details: {details}"
        logging.info(message)
        print(f"操作已记录: {message}")
    except Exception as e:
        print(f"记录操作失败: {str(e)}")