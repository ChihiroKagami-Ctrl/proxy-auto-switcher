# config/config.py
import os
import json
from utils.os_adapter import get_config_path, get_system_type
from utils.logger import logger

# 基础配置（可通过.env覆盖，优先读取环境变量）
TIMEOUT = int(os.getenv("TIMEOUT", 15))  # 请求超时时间（秒）
MAX_RETRY = int(os.getenv("MAX_RETRY", 10))  # 最大重试次数
TARGET_URL = os.getenv("TARGET_URL", "http://hjc.sdedu.net/?by=history&from=kkframene")  # 目标站点

def load_proxy_sources() -> list:
    """
    加载代理池源配置
    """
    try:
        with open(get_config_path("proxy_sources.json"), "r", encoding="utf-8") as f:
            sources = json.load(f)
        logger.info(f"加载代理池源成功，共{len(sources)}个源")
        return sources
    except FileNotFoundError:
        logger.error("proxy_sources.json配置文件不存在，使用默认源")
        # 默认代理池源
        return [
            "https://www.zdaye.com/free/",
            "https://www.kuaidaili.com/free/"
        ]

# 加载代理池源
PROXY_SOURCES = load_proxy_sources()

if __name__ == "__main__":
    # 测试配置加载
    print(f"超时时间：{TIMEOUT}")
    print(f"最大重试：{MAX_RETRY}")
    print(f"目标URL：{TARGET_URL}")
    print(f"代理池源：{PROXY_SOURCES}")