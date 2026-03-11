# utils/os_adapter.py
import os
import platform


def get_system_type() -> str:
    """
    获取当前系统类型
    返回：Windows/Linux/MacOS
    """
    sys_name = platform.system()
    if sys_name == "Windows":
        return "Windows"
    elif sys_name == "Linux":
        return "Linux"
    elif sys_name == "Darwin":
        return "MacOS"
    else:
        raise ValueError(f"不支持的系统类型：{sys_name}")


def get_project_root() -> str:
    """
    获取项目根目录（跨平台）
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_path(filename: str) -> str:
    """
    获取配置文件路径（跨平台）
    :param filename: 配置文件名（如 proxy_sources.json）
    """
    root = get_project_root()
    return os.path.join(root, "config", filename)


def get_log_dir() -> str:
    r"""
    获取日志目录（跨平台）
    Windows: C:\Users\用户名\proxy_tool\logs
    Linux: ~/proxy_tool/logs
    """
    sys_type = get_system_type()
    if sys_type == "Windows":
        # 路径用 r 前缀，避免 \ 被当成转义符
        log_dir = os.path.join(os.environ["USERPROFILE"], r"proxy_tool\logs")
    else:
        log_dir = os.path.join(os.environ["HOME"], r"proxy_tool/logs")

    # 自动创建目录
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


if __name__ == "__main__":
    # 测试代码
    print(f"系统类型：{get_system_type()}")
    print(f"项目根目录：{get_project_root()}")
    print(f"日志目录：{get_log_dir()}")