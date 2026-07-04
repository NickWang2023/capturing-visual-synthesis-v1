'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: 日志配置模块 - Issue #4 完善错误处理
'''
import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) -> None:
    """
    配置日志系统
    
    Args:
        level: 日志级别
        log_file: 日志文件路径（可选）
        log_format: 日志格式
    """
    # 创建格式器
    formatter = logging.Formatter(log_format)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 文件处理器（可选）
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # 配置根日志器
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的logger
    
    Args:
        name: logger名称
    
    Returns:
        logging.Logger实例
    """
    return logging.getLogger(name)
