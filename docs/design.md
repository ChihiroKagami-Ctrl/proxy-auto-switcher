# 项目设计思路
## 1. 核心需求
设计跨平台代理自动切换工具，解决免费代理不稳定、断链后手动更换的问题。

## 2. 模块划分
### 2.1 core 模块
- proxy_crawler.py：爬取免费代理池，提取 IP:端口
- proxy_validator.py：验证代理可用性
- proxy_switcher.py：断链自动切换核心逻辑

### 2.2 utils 模块
- os_adapter.py：抹平 Windows/Linux 系统差异
- http_client.py：封装 HTTP 请求，统一异常处理

## 3. 跨平台适配方案
- 路径处理：使用 os.path 替代硬编码分隔符
- 系统识别：通过 platform.system() 区分 Windows/Linux
- 打包方案：pyinstaller 分别打包为 .exe 和 Linux 可执行文件