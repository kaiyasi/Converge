"""
結構化日誌系統
- 支援日誌輪替
- 分級輸出 (console, file, error)
- 敏感資訊遮罩
- 上下文日誌
"""
import logging
import os
import re
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional
import json


class SensitiveDataFilter(logging.Filter):
    """過濾敏感資訊"""

    SENSITIVE_PATTERNS = [
        (r'token["\']?\s*:\s*["\']?([^"\'}\s]+)', r'token: ***MASKED***'),
        (r'api[_-]?key["\']?\s*:\s*["\']?([^"\'}\s]+)', r'api_key: ***MASKED***'),
        (r'secret["\']?\s*:\s*["\']?([^"\'}\s]+)', r'secret: ***MASKED***'),
        (r'password["\']?\s*:\s*["\']?([^"\'}\s]+)', r'password: ***MASKED***'),
        (r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', r'Bearer ***MASKED***'),
        (r'[A-Za-z0-9]{24}\.[A-Za-z0-9]{6}\.[A-Za-z0-9_-]{27}', r'***DISCORD_TOKEN***'),  # Discord Token
    ]

    def filter(self, record):
        """遮罩敏感資訊"""
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
            record.msg = msg
        return True


class ContextFilter(logging.Filter):
    """添加上下文資訊"""

    def __init__(self):
        super().__init__()
        self.context = {}

    def set_context(self, **kwargs):
        """設定上下文"""
        self.context.update(kwargs)

    def clear_context(self):
        """清除上下文"""
        self.context.clear()

    def filter(self, record):
        """添加上下文到日誌記錄"""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


class JSONFormatter(logging.Formatter):
    """JSON 格式日誌"""

    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # 添加異常資訊
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # 添加額外字段
        for key in ['user_id', 'message_id', 'group_id', 'channel_id']:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """彩色控制台輸出"""

    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 綠色
        'WARNING': '\033[33m',   # 黃色
        'ERROR': '\033[31m',     # 紅色
        'CRITICAL': '\033[1;31m', # 粗體紅色
    }
    RESET = '\033[0m'

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_dir: str = 'logs',
    log_level: str = 'INFO',
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    設定日誌系統

    Args:
        log_dir: 日誌目錄
        log_level: 日誌級別
        enable_console: 啟用控制台輸出
        enable_file: 啟用檔案輸出
        enable_json: 啟用 JSON 格式日誌
        max_bytes: 單個日誌檔案最大大小
        backup_count: 備份檔案數量

    Returns:
        配置好的 logger
    """
    # 創建日誌目錄
    if enable_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 取得 root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # 清除現有 handlers
    logger.handlers.clear()

    # 添加過濾器
    sensitive_filter = SensitiveDataFilter()
    context_filter = ContextFilter()

    # 控制台輸出
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(sensitive_filter)
        console_handler.addFilter(context_filter)
        logger.addHandler(console_handler)

    # 一般日誌檔案
    if enable_file:
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'bot.log'),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(sensitive_filter)
        file_handler.addFilter(context_filter)
        logger.addHandler(file_handler)

    # 錯誤日誌檔案
    if enable_file:
        error_handler = RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s\n'
            'Exception: %(exc_info)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        error_handler.addFilter(sensitive_filter)
        error_handler.addFilter(context_filter)
        logger.addHandler(error_handler)

    # JSON 日誌檔案
    if enable_json and enable_file:
        json_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, 'bot.json.log'),
            when='midnight',
            interval=1,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_formatter = JSONFormatter()
        json_handler.setFormatter(json_formatter)
        json_handler.addFilter(sensitive_filter)
        json_handler.addFilter(context_filter)
        logger.addHandler(json_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    獲取指定名稱的 logger

    Args:
        name: logger 名稱

    Returns:
        logger 實例
    """
    return logging.getLogger(name)


# 全域 context filter (用於設定上下文)
_context_filter = ContextFilter()


def set_log_context(**kwargs):
    """設定日誌上下文"""
    _context_filter.set_context(**kwargs)


def clear_log_context():
    """清除日誌上下文"""
    _context_filter.clear_context()


# 使用範例
if __name__ == '__main__':
    # 設定日誌
    setup_logging(log_level='DEBUG', enable_json=True)

    # 取得 logger
    logger = get_logger(__name__)

    # 測試日誌
    logger.debug('這是 DEBUG 訊息')
    logger.info('這是 INFO 訊息')
    logger.warning('這是 WARNING 訊息')
    logger.error('這是 ERROR 訊息')

    # 測試敏感資訊遮罩
    logger.info('Token: abc123xyz, API Key: secret_key_here')

    # 測試上下文
    set_log_context(user_id='U123456', message_id='M789')
    logger.info('帶有上下文的訊息')
    clear_log_context()

    # 測試異常
    try:
        raise ValueError('測試異常')
    except Exception as e:
        logger.exception('捕獲異常')
