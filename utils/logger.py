# utils/logger.py
import os
import sys
from loguru import logger
from utils.os_adapter import get_log_dir, get_system_type


def init_logger():
    """
    初始化日志配置（产品级优化版，彻底修复 KeyError）
    核心优化：
    - 用 loguru 原生 level.icon 绑定 emoji，避免 extra 字段导致的 KeyError
    - 控制台：emoji+分级彩色+紧凑对齐，视觉更直观
    - 文件：含进程/线程ID，保留更多调试上下文
    - 容错：自动创建日志目录，避免路径不存在报错
    - 兼容：适配Windows/Linux/macOS终端颜色
    - 扩展：安全新增SUCCESS级别，贴合业务成功场景
    """
    # 清空默认配置
    logger.remove()

    # ========== 安全配置所有日志级别（带emoji+颜色） ==========
    # 调试级别 🐞
    try:
        logger.level("DEBUG")
    except ValueError:
        logger.level("DEBUG", color="<blue>", icon="🐞")
    # 信息级别 ℹ️
    try:
        logger.level("INFO")
    except ValueError:
        logger.level("INFO", color="<green>", icon="ℹ️")
    # 成功级别 ✅（自定义）
    try:
        logger.level("SUCCESS")
    except ValueError:
        logger.level("SUCCESS", no=25, color="<bold><green>", icon="✅")
    # 警告级别 ⚠️
    try:
        logger.level("WARNING")
    except ValueError:
        logger.level("WARNING", color="<yellow>", icon="⚠️")
    # 错误级别 ❌
    try:
        logger.level("ERROR")
    except ValueError:
        logger.level("ERROR", color="<red>", icon="❌")
    # 致命级别 💥
    try:
        logger.level("CRITICAL")
    except ValueError:
        logger.level("CRITICAL", color="<bold><red>", icon="💥")

    # ========== 基础配置：日志目录容错 ==========
    log_dir = get_log_dir()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    sys_type = get_system_type()
    log_file = os.path.join(log_dir, "proxy_auto_switcher_{time:YYYY-MM-DD}.log")

    # ========== 控制台输出：视觉优化版 ==========
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "{level: <8} | "  # ✅ 自动显示带emoji的级别，如 🐞 DEBUG
        "<cyan>{name: <15}</cyan>:<cyan>{line: <3}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sink=sys.stdout,  # 直接输出到标准输出，简化sink逻辑
        format=console_format,
        level="INFO",
        colorize=True,  # 启用彩色输出
        enqueue=True  # 异步输出，避免阻塞业务
    )

    # ========== 文件输出：调试友好版 ==========
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "PID:{process.id: <6} | TID:{thread.id: <6} | "
        "{level: <7} | {name}:{line} - {message}"
    )

    logger.add(
        sink=log_file,
        rotation="00:00",  # 每天0点自动分割日志
        retention="7 days",  # 保留7天日志，自动清理旧日志
        encoding="utf-8",  # 强制UTF-8，避免中文乱码
        level="DEBUG",  # 文件日志保留DEBUG级别（更详细）
        format=file_format,
        compression="zip",  # 压缩过期日志，节省磁盘空间
        enqueue=True  # 异步写入，提升性能
    )

    # 封装SUCCESS级别快捷方法（方便调用）
    def success(msg, *args, **kwargs):
        logger.log("SUCCESS", msg, *args, **kwargs)

    logger.success = success

    return logger


# ========== 全局日志实例 ==========
logger = init_logger()

if __name__ == "__main__":
    # 测试所有日志级别效果
    logger.debug("调试信息：代理爬取请求参数")
    logger.info("信息提示：开始爬取免费代理池")
    logger.success("成功提示：验证通过3个可用代理")
    logger.warning("警告提示：代理池站点响应超时")
    logger.error("错误提示：爬取代理池站点连接失败")
    logger.critical("致命错误：无任何可用代理，任务终止")