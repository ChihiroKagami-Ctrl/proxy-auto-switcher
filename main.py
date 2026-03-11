# main.py
import sys
import os

# 🔥 修复模块导入路径（核心！确保能找到utils/core/config）
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.banner import show_banner
from utils.logger import logger
from core.proxy_switcher import proxy_switcher
from config.config import TARGET_URL


def main():
    """
    代理自动切换工具 - 主入口
    核心流程：显示标题 → 初始化切换器 → 自动切换代理请求 → 输出结果
    """
    # 1. 显示精美ASCII标题（提升工具质感）
    show_banner()

    # 2. 初始化提示（专业级日志）
    logger.info("🚀 跨平台代理自动切换工具启动")
    logger.info(f"🎯 目标请求地址：{TARGET_URL}")
    logger.info(f"🔄 最大重试次数：{proxy_switcher.max_retry}")
    logger.info("=" * 60)

    # 3. 核心逻辑：自动切换代理发起请求
    try:
        logger.info("📡 开始执行代理自动切换请求...")
        result = proxy_switcher.auto_switch_request()

        # 4. 结果处理（分级提示）
        if result:
            logger.success("🎉 请求任务执行成功！")
            logger.info(f"✅ 成功代理：{result['proxy']}")
            logger.info(f"📊 响应状态码：{result['status_code']}")
            logger.debug(f"📜 响应头：{result['headers']}")  # 调试级信息，不刷屏
        else:
            logger.error("❌ 请求任务执行失败（所有代理尝试完毕）")

    # 5. 异常处理（优雅降级）
    except KeyboardInterrupt:
        logger.info("\n👋 用户主动终止工具运行")
    except Exception as e:
        logger.critical(f"💥 工具执行异常：{str(e)}", exc_info=True)  # 打印完整异常栈，便于调试

    # 6. 结束提示
    logger.info("=" * 60)
    logger.info("🏁 代理自动切换工具执行结束")


if __name__ == "__main__":
    # 直接运行主函数
    main()