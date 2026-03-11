import re
import random
import urllib3
import time
from typing import List

# 关闭 requests 的 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm  # 进度条可视化
from utils.http_client import http_client
from utils.logger import logger
from config.config import PROXY_SOURCES


class ProxyCrawler:
    """
    免费代理池爬取器（容错降级+反爬增强版）
    核心优化：
    1. 单源失败自动跳过，不影响整体爬取
    2. 进度条可视化，直观显示爬取进度
    3. 动态随机延时，降低被反爬识别概率
    4. 鲁棒的页面解析，兼容空响应/乱码页面
    5. 分级日志输出，爬取状态一目了然
    """

    def __init__(self):
        # 匹配 IP:Port 的正则（增强版，兼容端口前有空格的情况）
        self.proxy_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+\s*:\s*\d+')
        # 动态延时范围（1-3秒随机）
        self.delay_range = (1.0, 3.0)

    def crawl_single_source(self, url: str) -> List[str]:
        """
        爬取单个代理池源（带完整异常处理）
        :param url: 代理池URL
        :return: 代理列表（格式：ip:port）
        """
        proxies = []
        try:
            logger.debug(f"🐢 开始爬取源：{url}")
            resp = http_client.get(url)

            # 容错1：响应为空/None
            if not resp:
                logger.warning(f"⚠️  源 {url} 无响应，跳过")
                return proxies

            # 容错2：响应内容为空
            if not resp.text.strip():
                logger.warning(f"⚠️  源 {url} 响应内容为空，跳过")
                return proxies

            # 鲁棒解析：清理空白字符+统一编码
            page_text = resp.text.strip()
            # 兼容乱码页面，强制转UTF-8
            try:
                page_text = page_text.encode('iso-8859-1').decode('utf-8', errors='ignore')
            except:
                pass

            # 提取代理并标准化格式（去除端口前后空格）
            matches = self.proxy_pattern.findall(page_text)
            # 标准化：比如 "1.2.3.4 : 8080" → "1.2.3.4:8080"
            proxies = [re.sub(r'\s*:\s*', ':', match) for match in matches]
            # 去重
            proxies = list(set(proxies))

            if proxies:
                logger.success(f"✅ 爬取 {url} | 提取到 {len(proxies)} 个有效代理")
            else:
                logger.warning(f"⚠️  源 {url} 未提取到任何代理")

        # 捕获所有异常，确保单源失败不影响整体
        except Exception as e:
            logger.error(f"❌ 源 {url} 爬取失败 | 异常：{str(e)[:80]}")
            proxies = []

        # 动态随机延时（避免固定间隔被反爬）
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)

        return proxies

    def crawl_all_sources(self) -> List[str]:
        """
        爬取所有代理池源（带进度条可视化）
        :return: 合并后的代理列表
        """
        all_proxies = []

        # 容错：代理源列表为空
        if not PROXY_SOURCES:
            logger.error("❌ 代理源列表为空，请检查 config.py 中的 PROXY_SOURCES 配置")
            return all_proxies

        logger.info(f"📡 开始爬取 {len(PROXY_SOURCES)} 个代理源...")

        # 进度条可视化（绿色主题，显示当前爬取的源）
        for source in tqdm(
                PROXY_SOURCES,
                desc="🔍 爬取进度",
                colour="green",
                ncols=80,  # 进度条宽度
                leave=True  # 爬取完成后保留进度条
        ):
            proxies = self.crawl_single_source(source)
            all_proxies.extend(proxies)

        # 全局去重
        all_proxies = list(set(all_proxies))

        # 分级日志提示
        if all_proxies:
            logger.success(f"🎉 所有源爬取完成 | 总计 {len(all_proxies)} 个有效代理（全局去重后）")
        else:
            logger.warning(f"⚠️  所有源爬取完成，但未提取到任何有效代理")

        return all_proxies


# 全局爬取器实例
proxy_crawler = ProxyCrawler()

if __name__ == "__main__":
    # 测试爬取
    logger.info("🚀 开始测试代理爬取器...")
    proxies = proxy_crawler.crawl_all_sources()

    # 友好的测试输出
    if proxies:
        logger.success(f"✅ 测试完成 | 共爬取到 {len(proxies)} 个代理")
        logger.info(f"📌 前5个代理示例：{proxies[:5]}")
    else:
        logger.warning(f"⚠️  测试完成 | 未爬取到任何代理（可能是源不可达/反爬限制）")