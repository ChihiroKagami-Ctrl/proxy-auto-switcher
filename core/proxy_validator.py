import time
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from utils.http_client import http_client
from utils.logger import logger
from config.config import TARGET_URL

# 兼容旧配置：如果 config 里没定义，就用默认值
try:
    from config.config import VALIDATION_BATCH_SIZE, MAX_WORKERS
except ImportError:
    VALIDATION_BATCH_SIZE = 10
    MAX_WORKERS = 5

class ProxyValidator:
    """
    代理可用性验证器（并发+可视化+容错版）
    核心优化：
    1. 多线程并发验证，大幅提升验证速度
    2. 进度条可视化，直观显示验证进度
    3. 超时控制+重试机制，应对临时网络波动
    4. 完整异常处理，单代理验证失败不影响整体
    5. 分级日志，验证状态一目了然
    """

    def __init__(self, test_url: Optional[str] = None, max_retries: int = 2):
        self.test_url = test_url or TARGET_URL
        self.max_retries = max_retries  # 单个代理验证重试次数
        self.timeout = 10  # 验证超时时间（秒）

    def validate_single_proxy(self, proxy: str) -> bool:
        """
        验证单个代理（带重试）
        :param proxy: 代理（格式：ip:port）
        :return: True/False
        """
        proxy_url = f"http://{proxy}"
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = http_client.get(
                    self.test_url,
                    proxy=proxy_url,
                    allow_redirects=True,
                    timeout=self.timeout
                )
                # 状态码200/302/403都算通（403是站点拦截，但代理本身可用）
                if resp and resp.status_code in (200, 302, 403):
                    logger.debug(f"✅ 代理可用：{proxy}（第{attempt}次尝试）")
                    return True
                else:
                    logger.debug(f"⚠️  代理失效：{proxy}（第{attempt}次尝试）")
            except Exception as e:
                logger.debug(f"❌ 代理验证异常：{proxy} | 尝试{attempt}次 | 异常：{str(e)[:50]}")
                time.sleep(0.5)  # 重试前短暂延时
        return False

    def validate_proxies(self, proxies: List[str], batch_size: int = None) -> List[str]:
        """
        批量验证代理（并发+进度条）
        :param proxies: 待验证代理列表
        :param batch_size: 每批验证数量（默认从配置读取）
        :return: 可用代理列表
        """
        if not proxies:
            logger.warning("⚠️  待验证代理列表为空，直接返回空列表")
            return []

        batch_size = batch_size or VALIDATION_BATCH_SIZE
        available_proxies = []
        total = len(proxies)

        logger.info(f"🔍 开始验证 {total} 个代理 | 并发数：{MAX_WORKERS} | 批次大小：{batch_size}")

        # 分批次验证，避免并发过高被封
        for i in range(0, total, batch_size):
            batch = proxies[i:i + batch_size]
            batch_num = i // batch_size + 1
            logger.info(f"📦 验证第 {batch_num} 批代理 | 共 {len(batch)} 个")

            # 多线程并发验证
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_proxy = {
                    executor.submit(self.validate_single_proxy, proxy): proxy
                    for proxy in batch
                }

                # 进度条可视化
                for future in tqdm(
                    as_completed(future_to_proxy),
                    total=len(batch),
                    desc=f"🔍 验证第{batch_num}批",
                    colour="blue",
                    ncols=80
                ):
                    proxy = future_to_proxy[future]
                    try:
                        if future.result():
                            available_proxies.append(proxy)
                    except Exception as e:
                        logger.error(f"❌ 代理 {proxy} 验证异常 | 异常：{str(e)[:80]}")

            # 批次间延时，避免高频请求
            time.sleep(1)

        logger.success(f"🎉 代理验证完成 | 可用代理：{len(available_proxies)}/{total}")
        return available_proxies


# 全局验证器实例
proxy_validator = ProxyValidator()

if __name__ == "__main__":
    # 测试验证（用测试代理列表）
    test_proxies = [
        "110.242.13.13:8888",
        "123.169.15.99:8090",
        "8.8.8.8:80",  # 无效代理
        "47.98.57.102:80"
    ]
    logger.info("🚀 开始测试代理验证器...")
    available = proxy_validator.validate_proxies(test_proxies)
    logger.success(f"✅ 测试完成 | 可用代理：{available}")