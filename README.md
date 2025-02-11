# AEsir Deep Research Agent 🧠

---

## 简介 📖

参考 https://github.com/dzhng/deep-research 中的方法，用python实现了一遍deep research agent。通过自然语言提问，Agent 能够：

1.  **自动生成 SERP 查询**:  根据用户提出的研究主题，智能生成一系列相关的搜索引擎查询。
2.  **深度网络爬取**:  利用 `firecrawl` 库进行高效的网络爬取，获取丰富的网页内容。
3.  **知识提取与学习**:  借助 LLM 模型 (如 `gpt-4o`)，从爬取结果中提取关键信息和知识点。
4.  **报告撰写**:  将研究成果整理成结构清晰、内容详实的 Markdown 格式报告。

## 使用 🛠️

### 1. 环境准备

确保安装了 Python 3.12 或更高版本。

### 2. 克隆项目

首先，将项目代码克隆到本地：

```bash
git clone [您的项目仓库地址]
cd [项目目录名]
```
### 3. 安装python包
使用 pip 安装项目所需的 Python 依赖：
```bash
pip install -r requirements.txt
```
---
## 使用指南 🚀

### 1. 配置参数
在 main.py 中，需要配置以下参数：
- `llm_api_key`: llm 的 API 密钥，需要在[OpenAI官网](https://www.google.com/url?sa=E&source=gmail&q=https://www.openai.com)或其他llm官网获得
- `llm_base_url`: llm API 的URL
- `firecrawl_api_key`: firecrawl 的 API 密钥,需要在[Firecrawl官网](https://www.firecrawl.dev/)获得
- `research_query`: 需要进行研究的主题。

  
### 2. 运行
运行 main.py 开始进行research：
```bash
python main.py
```
---
## 结构 📂
```
deep-research-agent/
├── main.py                      # 主程序入口文件
├── Agent/                       # Agent 核心模块
│   ├── config.py                # 参数管理
│   ├── dfs_research.py          # 迭代research实现
│   ├── app_utils/               # api工具模块
│   │   ├── firecrawl_app.py     # Firecrawl API 封装
│   │   ├── llm_app.py           # LLM API 封装和 Prompt 定义
│   ├── utils/                   # 其他工具
│   │   ├── log.py               # 配置log
├── requirements.txt             # 项目依赖列表
├── README.md                    # README 文件
└── app.log                      # 日志文件 (程序运行时自动生成)
```