# ProxyAutoSwitcher - 跨平台代理自动切换工具
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)
![Platform: Windows/Linux](https://img.shields.io/badge/Platform-Windows%2FLinux-lightgrey)

## 项目简介（学分项目）
本项目是为《Python 高级编程》/《网络安全》课程设计的**跨平台代理自动切换工具**。
工具支持 Windows/Linux 系统，可自动爬取免费代理池（砧大爷、快代理等）、验证代理可用性，并在 HTTP 请求断链/超时后**自动切换下一个可用代理**，完美解决免费代理不稳定的核心痛点。

### 核心功能亮点
✅ **跨平台兼容**：Windows/Linux 一键创建虚拟环境，代码无需修改即可运行；
✅ **自动爬取代理**：支持多免费代理池源，动态提取 IP:Port；
✅ **智能验证过滤**：剔除超时/失效代理，只保留可用代理；
✅ **断链自动切换**：请求失败后自动重试，自动切换代理，无需手动干预；
✅ **模块化设计**：核心逻辑/配置/工具类分离，便于扩展与维护。

## 快速开始
### 环境要求
- Python 3.8+（推荐 3.10/3.11，兼容性最佳）
- Windows 10+/Linux (Kali/ Ubuntu)
- 网络可正常访问代理池网站

### 安装依赖
已通过 `requirements.txt` 管理所有依赖，创建虚拟环境后会自动安装：
```bash
# 激活虚拟环境（Windows）
D:\proxy_auto_switcher\.venv\Scripts\activate
# 激活虚拟环境（Linux）
source ./venv/bin/activate

# 安装依赖（已内置，无需手动执行）
pip install -r requirements.txt


### 运行程序
```bash
# 入口运行
python main.py


##跨平台打包（生成可执行文件）
```bash
# Windows 打包为 .exe
python build.py --win

# Linux 打包为独立可执行文件
python build.py --linux


### 项目结构
```plaintext
proxy_auto_switcher/
├── core/                  # 核心业务逻辑
│   ├── proxy_crawler.py   # 免费代理池爬取
│   ├── proxy_validator.py # 代理可用性验证
│   └── proxy_switcher.py  # 断链自动切换核心
├── config/                # 配置文件
│   ├── config.py          # 全局配置（目标URL/超时时间）
│   └── proxy_sources.json # 代理池源配置
├── utils/                 # 跨平台工具类
│   ├── os_adapter.py      # 系统适配（Windows/Linux识别）
│   ├── http_client.py     # 通用HTTP请求封装
│   └── logger.py          # 跨平台日志管理
├── tests/                 # 单元测试
│   ├── test_proxy_crawler.py
│   └── test_proxy_validator.py
├── docs/                  # 设计文档/使用说明
│   ├── design.md          # 核心设计思路
│   └── usage_guide.md     # 详细使用指南
├── main.py                # 程序入口
├── build.py               # 跨平台打包脚本
├── requirements.txt       # 生产依赖清单
└── README.md              # 项目说明（本文件）


###设计思路
1. 模块化架构设计
采用「分层模块化」思想，将项目拆分为 核心业务层、配置层、工具层：
core 层：聚焦代理爬取 / 验证 / 切换的核心逻辑，高内聚低耦合；
config 层：集中管理配置，避免硬编码，提升可维护性；
utils 层：封装跨平台适配、HTTP 请求、日志等通用功能，减少代码冗余。
2. 跨平台适配方案
系统识别：通过 platform 库自动识别 Windows/Linux，适配不同路径与命令；
路径处理：使用 os.path 替代硬编码分隔符，兼容多系统；
打包规范：通过 PyInstaller 分别生成 Windows .exe 与 Linux 独立可执行文件。
3. 异常处理机制
针对免费代理的不稳定性，设计了三层异常捕获：
爬取异常：捕获网络请求失败，跳过异常代理源；
验证异常：捕获超时 / 连接重置，剔除失效代理；
请求异常：捕获断链 / 超时，自动切换下一个代理重试。