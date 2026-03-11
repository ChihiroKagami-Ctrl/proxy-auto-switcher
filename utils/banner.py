# utils/banner.py
import os  # 👈 必须加上！
import sys  # 👈 加上，用于判断系统类型（跨平台清屏）
import time
from colorama import init, Fore, Style

# 初始化 colorama（兼容 Windows 终端彩色）
init(autoreset=True)


def show_banner():
    """显示精美项目标题（ASCII 艺术+彩色）"""
    # ASCII 艺术标题：ProxyAutoSwitcher（代理自动切换器）
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}===============================================================
   _____         _     _                     _        _        
  |  __ \\       | |   | |                   | |      | |       
  | |__) |__  __| | __| | ___  _ __   __ _  | |_ __ _| |_ ___  
  |  ___/ _ \\/ _` |/ _` |/ _ \\| '_ \\ / _` | | __/ _` | __/ _ \\ 
  | |  |  __/ (_| | (_| | (_) | | | | (_| | | || (_| | ||  __/ 
  |_|   \\___|\\__,_|\\__,_|\\___/|_| |_|\\__, |  \\__\\__,_|\\__\\___| 
                                      __/ |                    
                                     |___/                     
{Fore.GREEN}{Style.BRIGHT}                      跨平台代理自动切换器 v1.0
{Fore.YELLOW}===============================================================
{Fore.WHITE}📌 功能：免费代理爬取 → 智能验证 → 失效自动切换
{Fore.WHITE}🔧 特性：反爬优化 | 异常处理 | 跨平台兼容 | 日志追踪
{Fore.WHITE}⚠️  说明：免费代理池稳定性有限，建议用于学习测试
{Fore.CYAN}{Style.BRIGHT}===============================================================
    """
    # ✅ 跨平台清空终端（Windows 用 cls，Linux/macOS 用 clear）
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

    # 打印标题
    print(banner)
    # 延迟0.5秒，让用户看清标题
    time.sleep(0.5)