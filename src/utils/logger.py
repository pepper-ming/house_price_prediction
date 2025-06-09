"""
日誌系統模組

提供統一的日誌記錄功能，支援不同級別的日誌輸出。
同時輸出到控制台和檔案，方便除錯和追蹤。
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

class Logger:
    """
    自定義日誌類別
    
    整合 Rich 庫提供更美觀的控制台輸出，
    同時保留傳統的檔案日誌功能。
    """
    
    def __init__(
        self, 
        name: str, 
        log_dir: str = "logs",
        level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True
    ):
        """
        初始化日誌系統
        
        Args:
            name: 日誌名稱（通常使用模組名稱）
            log_dir: 日誌檔案目錄
            level: 日誌級別
            console_output: 是否輸出到控制台
            file_output: 是否輸出到檔案
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 清除現有的處理器，避免重複
        self.logger.handlers = []
        
        # 設定日誌格式
        self.file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 建立日誌目錄
        if file_output:
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(exist_ok=True)
            self._add_file_handler()
        
        # 添加控制台處理器
        if console_output:
            self._add_console_handler()
    
    def _add_file_handler(self) -> None:
        """添加檔案處理器"""
        # 使用日期作為檔名的一部分
        log_filename = f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = self.log_dir / log_filename
        
        file_handler = logging.FileHandler(
            log_filepath, 
            mode='a', 
            encoding='utf-8'
        )
        file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(file_handler)
    
    def _add_console_handler(self) -> None:
        """添加控制台處理器（使用 Rich）"""
        console_handler = RichHandler(
            console=Console(stderr=True),
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_level=True,
            show_path=True
        )
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """記錄除錯訊息"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """記錄一般訊息"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """記錄警告訊息"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """記錄錯誤訊息"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """記錄嚴重錯誤訊息"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """記錄異常訊息（包含堆疊追蹤）"""
        self.logger.exception(message, *args, **kwargs)


def get_logger(
    name: str, 
    level: str = "INFO",
    log_dir: str = "logs"
) -> Logger:
    """
    獲取日誌實例的便利函數
    
    Args:
        name: 日誌名稱
        level: 日誌級別
        log_dir: 日誌目錄
        
    Returns:
        Logger 實例
    """
    return Logger(name, log_dir=log_dir, level=level)


# 建立專案級別的全域日誌
project_logger = get_logger("house_price_prediction")

# 匯出常用函數
def log_info(message: str) -> None:
    """記錄一般訊息的便利函數"""
    project_logger.info(message)

def log_error(message: str) -> None:
    """記錄錯誤訊息的便利函數"""
    project_logger.error(message)

def log_warning(message: str) -> None:
    """記錄警告訊息的便利函數"""
    project_logger.warning(message)