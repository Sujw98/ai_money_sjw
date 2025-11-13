# 小红书内容生成与发布运营系统

一个基于 LangGraph 多智能体框架构建的财经理财类小红书内容自动化生成与运营系统。

## 🎯 项目目标

通过自动化内容创作和运营策略，积累 1 万粉丝并实现带货变现。

## ✨ 核心特性

- 🤖 **四大智能体协作**：大纲规划、灵感挖掘、内容创作、运营优化
- 🔄 **完整工作流**：从内容规划到发布的全流程自动化
- 💾 **数据持久化**：MySQL 数据库完整记录运营数据
- 🔌 **MCP 集成**：通过 xiaohongshu-mcp 实现小红书操作
- 🧠 **DeepSeek 驱动**：使用 DeepSeek 大模型进行智能创作

## 🚀 快速开始

### 1. 激活虚拟环境

```bash
conda activate xiaohongshu_agent_with_mcp_v1
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
# 编辑 .env 文件，填写 DeepSeek API Key 和 MySQL 配置
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 启动系统

```bash
python main.py
```

## 📖 使用指南

详细使用说明请参考 [SYSTEM_GUIDE.md](SYSTEM_GUIDE.md)

### 基本操作

1. **创建新大纲**：输入资源名称，系统自动生成内容规划
2. **继续处理**：根据大纲 ID 继续生成下一篇内容
3. **查看进度**：查看所有大纲的完成情况

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│             LangGraph 工作流引擎                  │
├─────────────────────────────────────────────────┤
│  大纲规划  →  灵感挖掘  →  内容创作  →  运营优化  │
│      ↓          ↓          ↓          ↓         │
│            MySQL 数据库持久化                     │
├─────────────────────────────────────────────────┤
│              xiaohongshu-mcp                    │
│           (小红书平台操作接口)                     │
└─────────────────────────────────────────────────┘
```

## 📂 项目结构

```
xiaohongshu_agent_with_mcp_v1/
├── src/
│   ├── agents/              # 四大智能体
│   ├── workflows/           # LangGraph 工作流
│   ├── models/              # 数据模型
│   ├── database/            # 数据库管理
│   └── utils/               # 工具类
├── main.py                  # 主入口
├── init_db.py              # 数据库初始化
├── requirements.txt        # 依赖
└── SYSTEM_GUIDE.md        # 详细指南
```

## 🛠️ 技术栈

- **LangGraph**: 多智能体工作流框架
- **LangChain**: 大模型应用开发框架
- **DeepSeek**: 大语言模型
- **SQLAlchemy**: ORM 框架
- **MySQL**: 关系型数据库
- **Pydantic**: 数据验证
- **MCP**: 小红书平台集成

## 📝 开发说明

### 添加新智能体

1. 在 `src/agents/` 创建新的 Agent
2. 在 `src/models/agent_models.py` 定义模型
3. 在 `src/workflows/workflow.py` 添加节点

### 自定义 Prompt

在各个 Agent 类中修改 Prompt 模板即可。

## ⚠️ 注意事项

1. 需要先配置 DeepSeek API Key
2. 需要 MySQL 数据库环境
3. 发布内容需要至少 1 张图片
4. 请遵守小红书平台使用规则

## 📊 数据库表

- `outlines` - 大纲表
- `topics` - 主题表
- `inspirations` - 灵感素材表
- `contents` - 内容表
- `publish_records` - 发布记录表

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目仅供学习交流使用。
