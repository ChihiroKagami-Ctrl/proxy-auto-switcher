from typing import Optional, List
from itertools import cycle
from tqdm import tqdm
from utils.http_client import http_client
from utils.logger import logger
from config.config import TARGET_URL, MAX_RETRY


class ProxySwitcher:
    """
    代理自动切换器（负载均衡+自动重试+可视化版）
    核心优化：
    1. 负载均衡：轮询/随机选择代理，避免单点过载
    2. 自动重试：请求失败时自动切换下一个代理，直到成功或耗尽所有代理
    3. 状态管理：记录代理使用状态（成功/失败次数），便于后续优化
    4. 优雅降级：无可用代理时给出友好提示，不崩溃
    5. 可视化：请求过程进度条+分级日志，直观展示切换流程
    """

    def __init__(self, max_retry: int = None):
        self.max_retry = max_retry or MAX_RETRY  # 最大重试次数（=可用代理数）
        self.available_proxies: List[str] = []  # 可用代理池
        self.proxy_stats: dict = {}  # 代理状态统计：{proxy: {"success": 0, "fail": 0}}
        self.proxy_cycle: Optional[cycle] = None  # 轮询代理迭代器

    def update_proxies(self, proxies: List[str]):
        """
        更新可用代理池（外部注入验证后的代理）
        :param proxies: 可用代理列表
        """
        self.available_proxies = proxies
        # 初始化轮询迭代器
        if proxies:
            self.proxy_cycle = cycle(proxies)
            # 初始化状态统计
            for proxy in proxies:
                if proxy not in self.proxy_stats:
                    self.proxy_stats[proxy] = {"success": 0, "fail": 0}
            logger.success(f"✅ 代理池更新完成 | 可用代理数：{len(proxies)}")
        else:
            self.proxy_cycle = None
            logger.warning("⚠️  可用代理池为空，无法发起请求")

    def _get_next_proxy(self) -> Optional[str]:
        """
        获取下一个代理（轮询策略，负载均衡）
        :return: 代理地址 / None（无可用代理）
        """
        if not self.proxy_cycle:
            return None
        return next(self.proxy_cycle)

    def _record_proxy_result(self, proxy: str, success: bool):
        """
        记录代理使用结果（成功/失败次数）
        :param proxy: 代理地址
        :param success: 是否成功
        """
        if proxy in self.proxy_stats:
            if success:
                self.proxy_stats[proxy]["success"] += 1
            else:
                self.proxy_stats[proxy]["fail"] += 1

    def auto_switch_request(self, url: str = None, **kwargs) -> Optional[object]:
        """
        自动切换代理发起请求（核心方法）
        :param url: 目标URL（默认从配置读取）
        :param kwargs: 额外请求参数
        :return: Response对象 / None（所有代理都失败）
        """
        url = url or TARGET_URL
        if not self.available_proxies:
            logger.error("❌ 无可用代理，无法发起请求")
            return None

        total_proxies = len(self.available_proxies)
        max_attempts = min(self.max_retry, total_proxies)
        logger.info(f"🚀 开始自动切换请求 | 目标URL：{url} | 最大尝试次数：{max_attempts}")

        # 进度条可视化
        for attempt in tqdm(
            range(1, max_attempts + 1),
            desc="🔄 自动切换代理",
            colour="cyan",
            ncols=80
        ):
            proxy = self._get_next_proxy()
            if not proxy:
                logger.error("❌ 代理池已耗尽，请求失败")
                break

            logger.info(f"🔄 第 {attempt}/{max_attempts} 次尝试 | 使用代理：{proxy}")
            try:
                resp = http_client.get(
                    url,
                    proxy=proxy,
                    allow_redirects=True,
                    timeout=15,
                    **kwargs
                )
                if resp and resp.status_code in (200, 302, 403):
                    self._record_proxy_result(proxy, success=True)
                    logger.success(f"✅ 请求成功！| 代理：{proxy} | 状态码：{resp.status_code}")
                    return resp
                else:
                    self._record_proxy_result(proxy, success=False)
                    logger.warning(f"⚠️  代理 {proxy} 请求失败 | 状态码：{resp.status_code if resp else '无响应'}")
            except Exception as e:
                self._record_proxy_result(proxy, success=False)
                logger.error(f"❌ 代理 {proxy} 请求异常 | 异常：{str(e)[:80]}")

        logger.error(f"💥 所有代理尝试失败，请求终止")
        return None

    def get_proxy_stats(self) -> dict:
        """获取代理使用统计（便于调试/优化）"""
        return self.proxy_stats


# 全局切换器实例
proxy_switcher = ProxySwitcher()

if __name__ == "__main__":
    # 测试自动切换（用模拟可用代理）
    test_proxies = [
        "110.242.13.13:8888",
        "123.169.15.99:8090",
        "47.98.57.102:80"
    ]
    logger.info("🚀 开始测试代理自动切换器...")
    proxy_switcher.update_proxies(test_proxies)
    resp = proxy_switcher.auto_switch_request()
    if resp:
        logger.success(f"✅ 测试完成 | 响应状态码：{resp.status_code}")
    else:
        logger.warning("⚠️  测试完成 | 所有代理请求失败")
    # 打印代理统计
    logger.info(f"📊 代理使用统计：{proxy_switcher.get_proxy_stats()}")