# 项目总览

一个基于worldquantbrain平台的量化分析以及通过智能体自动的分析和提交系统。欢迎大家的使用和二次开发，支持用户权限，顾问权限也适用,同时也可以作为其他网站的开发模板。

## 🚀 核心功能

### 能力总览

- **内嵌功能的智能体**：包括对提交alphas的往期数据获取，和可视化分析（平台参数与sharpe对比，每月alphas的数量和平台参数的一些对比）
- **长期记忆系统**：基于chromadb的向量数据库的长期存储和搜索。
- **大量高质量社区帖子数据**：通过对大量高质量社区帖子数据存储在向量数据库，使得智能体对该平台的数据更加敏感，给出高质量模板分析
- **通过循环智能体，不断储存优化表达式，占据一个提交数量**
  ：通过alpha_agent和termination_checker两个智能体通过调用一些工具，不断进行生成 -> 评估，建议 ->再生成的循环。

## 📁 项目结构

```
world_quant_brain/
├── data_community/                 # 社区的帖子数据
│── static/                         # 静态文件，用于web页面的图片展示
│── wqb/                            # 第三方库，自行了解
│── agent.py                        # 协调器
│── alpha_loop.py                   # 循环智能体代码
│── deal_tools.py                   # 封装的数据处理工具
│── memo_tools.py                   # 封装的记忆系统
│── my_fun.py                       # 定义好的功能代码
│── server.py                       # Mcp协议的api文件
│── static_server.py                # 静态地址映射，主要是用于web页面的图片可视化
├── fields.json                     # 平台的数据集集合
│── operators.json                  # 平台的操作符集合
│── big_text.txt                    # 处理后的社区的帖子数据
│── brain_credentials_copy          # worldquantbrain平台的账号密码
│── Deepseek_key                    # DeepSeek的密钥文件
│── test_cat_db.py                  # 查看存储的向量数据库内容
└── README.md                       # 本文件（中文）
lopp_submit/
└── agent.py                        # 提交+分析协调器
```

## 🛠️ 安装

### 前置条件

- Python 3.10 或更高版本

### 安装步骤

- `pip install -r requirements.txt`

## 🚀 快速开始

### 1. 启动静态地址映射

```bash
cd world_quant_brain
python static_server.py
```

执行后将：

- 将静态目录static映射在 `http://localhost:8001`
- 可以在对话中直接显示图片

### 2. 启动mcp.server

```bash
  python server.py
```

执行后将：

- 定义的工具可以通过该 `http://localhost:50001`访问

### 3. 在 Google ADK Web UI 中使用智能体系统

```bash
  adk web
```

执行后将：

- 访问 `http://localhost:8000.`使用该工具

## 🔍 示例使用场景

### 对指定月份提交的alphas分析

```
“请帮我分析7月份的sharpe与其他平台参数的对比可视化”
“获取平台的说有操作符，并结合智能体，对每个操作符给出解释”
“结合记忆智能体，给我一些alpha表达式的模板和灵感”
“帮我将7，8月份的alphas进行对比可视化”
```

## 🛠️ 配置

### 配置

编辑 `brain_credentials_copy` 可自定义：

- 添加好对应的账号密码信息

### 数据库配置

修改 `Deepseek_key` 可：

- Deepseek的API密钥

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支
3. 进行修改
4. 必要时添加测试
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 📞 支持

如有疑问或需要支持：

- 在 GitHub 提交 Issue
- 查阅文档
- 参考示例用法
- 577624834@qq.com

---


**注意**：本项目为个人开发，旨在展示 AI 驱动的研究工作流。生产环境请确保完善安全、验证与异常处理。

