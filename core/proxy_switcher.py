# core/proxy_switcher.py
import random
import time
from utils.http_client import http_client
from utils.logger import logger
from core.proxy_crawler import proxy_crawler
from core.proxy_validator import proxy_validator
from config.config import MAX_RETRY, TARGET_URL


class ProxySwitcher:
    """
    断链自动切换核心逻辑
    """

    def __init__(self):
        self.available_proxies = []  # 可用代理池
        self.max_retry = MAX_RETRY
        self.target_url = TARGET_URL

    def refresh_available_proxies(self):
        """
        刷新可用代理池（爬取+验证）
        """
        logger.info("开始刷新可用代理池...")
        # 1. 爬取代理
        raw_proxies = proxy_crawler.crawl_all_sources()
        if not raw_proxies:
            logger.error("爬取代理失败，可用代理池为空")
            return

        # 2. 验证代理
        self.available_proxies = proxy_validator.validate_proxies(raw_proxies)

    def auto_switch_request(self) -> dict | None:
        """
        自动切换代理发起请求
        :return: 响应信息（status_code/headers） / None
        """
        # 先刷新可用代理池
        if not self.available_proxies:
            self.refresh_available_proxies()
        if not self.available_proxies:
            logger.error("无可用代理，无法发起请求")
            return None

        retry_count = 0
        while retry_count < self.max_retry:
            # 随机选一个代理
            proxy = random.choice(self.available_proxies)
            proxy_url = f"http://{proxy}"
            retry_count += 1

            logger.info(f"第 {retry_count} 次尝试 | 使用代理：{proxy}")

            # 发起请求
            resp = http_client.get(self.target_url, proxy=proxy_url)
            if resp:
                logger.success(f"请求成功！代理：{proxy} | 状态码：{resp.status_code}")
                return {
                    "status_code": resp.status_code,
                    "proxy": proxy,
                    "headers": dict(resp.headers)
                }
            else:
                logger.warning(f"请求失败 | 代理：{proxy} | 重试次数：{retry_count}/{self.max_retry}")
                # 移除失效代理
                if proxy in self.available_proxies:
                    self.available_proxies.remove(proxy)
                # 代理池为空时刷新
                if not self.available_proxies:
                    self.refresh_available_proxies()
                time.sleep(1)  # 间隔1秒重试

        logger.error(f"达到最大重试次数（{self.max_retry}），请求失败")
        return None


# 全局切换器实例
proxy_switcher = ProxySwitcher()

if __name__ == "__main__":
    # 测试自动切换
    result = proxy_switcher.auto_switch_request()
    if result:
        print(f"请求结果：{result}")