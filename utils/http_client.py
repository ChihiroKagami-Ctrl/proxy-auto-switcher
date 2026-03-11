import time
import random
import requests
from typing import Optional, Dict
from requests.exceptions import (
    RequestException,
    ConnectTimeout,
    ConnectionError,
    SSLError,
    ReadTimeout
)
from utils.logger import logger
from config.config import TIMEOUT

# ========== 反爬核心配置 ==========
USER_AGENT_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]

ACCEPT_ENCODING_POOL = [
    "gzip, deflate, br",
    "gzip, deflate",
    "deflate, br",
    "gzip"
]

COOKIE_TEMPLATES = [
    "BAIDUID=1234567890ABCDEF:FG=1; BIDUPSID=1234567890ABCDEF; PSTM=1690000000; BD_UPN=123456;",
    "Hm_lvt_123456=1690000000; Hm_lpvt_123456=1690000000; _ga=GA1.2.1234567890.1690000000;",
    "sessionid=abc123def456ghi789; csrftoken=1234567890abcdef1234567890abcdef;"
]

class HttpClient:
    """
    通用HTTP客户端（极致反爬版）
    """

    def __init__(self, timeout: int = 30, retry_times: int = 3, retry_delay_range: tuple = (1.0, 3.0)):
        self.timeout = timeout if TIMEOUT is not None else timeout
        self.retry_times = retry_times
        self.retry_delay_min, self.retry_delay_max = retry_delay_range

    def _generate_random_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": random.choice(USER_AGENT_POOL),
            "Referer": random.choice(["https://www.baidu.com", "https://www.google.com", "https://www.qq.com"]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice([
                "zh-CN,zh;q=0.9,en;q=0.8",
                "zh-CN,zh;q=0.8,en;q=0.7",
                "en-US,en;q=0.9,zh-CN;q=0.8"
            ]),
            "Accept-Encoding": random.choice(ACCEPT_ENCODING_POOL),
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "close",
            "X-Requested-With": random.choice(["XMLHttpRequest", "XMLHttpRequest, MSXML2"]),
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1"
        }
        if random.random() > 0.5:
            headers["Cookie"] = random.choice(COOKIE_TEMPLATES)
        headers = dict(random.sample(list(headers.items()), len(headers)))
        return headers

    def get(self, url: str, proxy: Optional[str] = None, allow_redirects: bool = False) -> Optional[requests.Response]:
        proxies = None
        if proxy:
            proxy = proxy if proxy.startswith(("http://", "https://")) else f"http://{proxy}"
            proxies = {"http": proxy, "https": proxy}

        for attempt in range(1, self.retry_times + 1):
            headers = self._generate_random_headers()
            try:
                logger.debug(f"第 {attempt}/{self.retry_times} 次请求 | URL：{url} | 代理：{proxy or '无'} | UA：{headers['User-Agent'][:50]}...")
                resp = requests.get(
                    url=url,
                    headers=headers,
                    proxies=proxies,
                    timeout=self.timeout,
                    allow_redirects=allow_redirects,
                    verify=False,
                    stream=False,
                    auth=None
                )
                # ✅ 修复：先判断 resp.encoding 是否存在，再调用 .lower()
                if resp.encoding and resp.encoding.lower() in ["iso-8859-1", "latin-1", "ascii"]:
                    resp.encoding = resp.apparent_encoding or "utf-8"
                else:
                    resp.encoding = resp.apparent_encoding or "utf-8"

                logger.debug(f"请求成功 | 状态码：{resp.status_code} | URL：{url}")
                return resp

            except ConnectTimeout:
                logger.warning(f"第 {attempt} 次失败 | {url} | 原因：连接超时（站点不可达/被墙）")
            except ReadTimeout:
                logger.warning(f"第 {attempt} 次失败 | {url} | 原因：读取超时（站点响应慢）")
            except ConnectionError:
                logger.warning(f"第 {attempt} 次失败 | {url} | 原因：连接错误（站点不可达/被墙）")
            except SSLError:
                logger.warning(f"第 {attempt} 次失败 | {url} | 原因：SSL证书错误（免费代理常见）")
            except RequestException as e:
                logger.warning(f"第 {attempt} 次失败 | {url} | 原因：{str(e)[:80]}")

            if attempt < self.retry_times:
                delay = random.uniform(self.retry_delay_min, self.retry_delay_max)
                logger.debug(f"等待 {delay:.2f} 秒后重试...")
                time.sleep(delay)

        logger.error(f"重试 {self.retry_times} 次彻底失败 | URL：{url} | 代理：{proxy or '无'}")
        return None

http_client = HttpClient()

if __name__ == "__main__":
    logger.info("开始测试极致反爬HTTP客户端...")
    resp = http_client.get("http://ip.cn")
    if resp:
        logger.success(f"测试成功 | 响应内容：{resp.text[:200]}")
    else:
        logger.error("测试失败：无法访问ip.cn（大概率是网络/站点问题，非代码问题）")