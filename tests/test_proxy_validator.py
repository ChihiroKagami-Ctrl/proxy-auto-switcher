# tests/test_proxy_validator.py
import pytest
from core.proxy_validator import proxy_validator

def test_validate_single_proxy():
    """
    测试单个代理验证（用已知的测试代理）
    """
    # 测试无效代理
    assert proxy_validator.validate_single_proxy("127.0.0.1:8888") is False

def test_validate_proxies():
    """
    测试批量验证
    """
    test_proxies = ["127.0.0.1:8888", "192.168.1.1:8080"]
    available = proxy_validator.validate_proxies(test_proxies)
    assert len(available) == 0