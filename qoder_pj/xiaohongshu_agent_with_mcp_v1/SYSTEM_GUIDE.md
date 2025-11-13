# 小红书内容生成与发布运营系统 - 使用指南

## 系统简介

这是一个基于 LangGraph 多智能体框架构建的财经理财类小红书内容自动化生成与运营系统。系统通过四个核心智能体的协作，实现从内容规划到发布的全流程自动化。

### 核心功能

1. **智能大纲规划**：分析财经理财类资源，制定系列内容规划
2. **灵感挖掘**：从小红书搜索优质内容作为创作参考
3. **原创内容生成**：基于大纲和灵感素材创作高质量原创内容
4. **运营优化**：优化标题和文案，提升传播力和互动率
5. **自动发布**：一键发布到小红书平台
6. **数据持久化**：完整记录运营数据和进度

## 系统架构

### 技术栈

- **LangGraph**：构建多智能体工作流
- **LangChain + DeepSeek**：大语言模型调用
- **MySQL + SQLAlchemy**：数据持久化
- **Pydantic**：数据模型校验
- **MCP (xiaohongshu-mcp)**：小红书平台操作

### 四大智能体

1. **大纲规划智能体 (Outline Agent)**
   - 分析资源内容
   - 制定内容大纲
   - 拆解为系列主题

2. **灵感挖掘智能体 (Inspiration Agent)**
   - 搜索小红书相关内容
   - 筛选优质素材
   - 提供创作参考

3. **内容创作智能体 (Content Agent)**
   - 生成原创内容
   - 结合主题和灵感
   - 确保结构完整

4. **运营优化智能体 (Operation Agent)**
   - 优化标题（标题党风格）
   - 优化文案结构
   - 提升传播力

### 工作流程

```
大纲规划 → 灵感挖掘 → 内容创作 → 运营优化 → 发布 → 保存
```

## 快速开始

### 1. 环境准备

#### 激活虚拟环境

```bash
conda activate xiaohongshu_agent_with_mcp_v1
```

#### 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置

复制 `.env.example` 为 `.env` 并配置：

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=xiaohongshu_agent

# 系统配置
LOG_LEVEL=INFO
MAX_RETRIES=3
```

### 3. 初始化数据库

```bash
python init_db.py
```

重置数据库（删除所有数据）：

```bash
python init_db.py --reset
```

### 4. 启动系统

```bash
python main.py
```

## 使用说明

### 创建新的内容大纲

1. 运行系统后选择 "1. 创建新的内容大纲"
2. 输入资源名称（如：《经济学原理》）
3. 系统会自动：
   - 调用 DeepSeek 分析资源并生成大纲
   - 将大纲拆解为 15-30 个主题
   - 保存到数据库
   - 立即处理第一个主题，生成并发布内容

### 继续处理现有大纲

1. 选择 "2. 继续处理现有大纲"
2. 输入大纲 ID
3. 系统会自动处理下一个待处理主题

### 查看所有大纲

选择 "3. 查看所有大纲" 可查看：
- 大纲 ID
- 资源名称
- 总主题数
- 完成进度
- 创建时间

## 数据库结构

### 表说明

1. **outlines** - 大纲表
   - 存储资源的整体规划
   - 记录总主题数和完成进度

2. **topics** - 主题表
   - 存储具体的内容主题
   - 状态：pending, processing, completed, failed

3. **inspirations** - 灵感素材表
   - 存储从小红书搜索的优质内容
   - 包含点赞、收藏、评论数据

4. **contents** - 内容表
   - 存储原始和优化后的内容
   - 包含标题、正文、标签

5. **publish_records** - 发布记录表
   - 存储发布状态和结果
   - 记录重试次数和错误信息

## MCP 集成说明

### 小红书 MCP 工具

系统集成了 `xiaohongshu-mcp`，提供以下功能：

1. **搜索内容** (`search_feeds`)
   - 根据关键词搜索小红书内容
   - 支持筛选排序

2. **发布内容** (`publish_content`)
   - 发布图文内容到小红书
   - 需要配图（最少1张）

3. **登录管理**
   - `check_login_status` - 检查登录状态
   - `get_login_qrcode` - 获取登录二维码

### 使用 MCP 发布内容

在工作流中，发布节点需要实际调用 MCP 工具：

```python
# 示例：在 publish_node 中调用 MCP
from mcp_xiaohongshu import publish_content

result = publish_content(
    title=optimized_content.title,
    content=optimized_content.content,
    tags=optimized_content.tags,
    images=["path/to/image.jpg"]  # 至少需要1张图片
)
```

## 项目结构

```
xiaohongshu_agent_with_mcp_v1/
├── src/
│   ├── agents/              # 智能体实现
│   │   ├── outline_agent.py
│   │   ├── inspiration_agent.py
│   │   ├── content_agent.py
│   │   └── operation_agent.py
│   ├── workflows/           # 工作流
│   │   ├── state.py
│   │   └── workflow.py
│   ├── models/              # 数据模型
│   │   ├── db_models.py     # 数据库 ORM
│   │   └── agent_models.py  # Agent 模型
│   ├── database/            # 数据库管理
│   │   ├── db_manager.py
│   │   └── dao.py
│   └── utils/               # 工具类
│       ├── config.py
│       ├── logger.py
│       └── publisher.py
├── main.py                  # 主入口
├── init_db.py              # 数据库初始化
├── requirements.txt        # 依赖
├── .env.example           # 配置模板
└── SYSTEM_GUIDE.md        # 本文档
```

## 扩展开发

### 添加新的智能体

1. 在 `src/agents/` 创建新的 Agent 类
2. 在 `src/models/agent_models.py` 定义输入输出模型
3. 在 `src/workflows/workflow.py` 添加新节点

### 自定义 Prompt

所有 Prompt 都在 Agent 类中定义，可根据需求调整：

- `OutlineAgent.outline_prompt` - 大纲生成 Prompt
- `ContentAgent.content_prompt` - 内容创作 Prompt
- `OperationAgent.optimization_prompt` - 优化 Prompt

### 添加新的数据表

1. 在 `src/models/db_models.py` 定义 ORM 模型
2. 在 `src/database/dao.py` 添加 DAO 类
3. 运行 `python init_db.py --reset` 重建数据库

## 常见问题

### Q: 如何添加默认图片？

A: 将图片放到 `assets/default_images/` 目录，系统会自动使用。

### Q: 如何调整内容创作的温度参数？

A: 在各个 Agent 的 `__init__` 方法中修改 `temperature` 参数。

### Q: 如何批量处理多个主题？

A: 可以编写循环脚本，多次调用 `workflow.run(outline_id=xxx)`。

### Q: 如何查看详细日志？

A: 日志文件保存在 `logs/app.log`，可设置 `LOG_LEVEL=DEBUG` 获取更详细信息。

## 注意事项

1. **API 限流**：DeepSeek API 有调用频率限制，建议添加延迟
2. **图片要求**：发布内容至少需要 1 张图片
3. **数据备份**：定期备份 MySQL 数据库
4. **错误重试**：系统会自动重试失败的操作，最多 3 次

## 开发路线图

- [ ] 增加图片自动生成功能
- [ ] 支持视频内容发布
- [ ] 添加定时发布功能
- [ ] 数据分析和可视化
- [ ] 多账号管理
- [ ] 评论自动回复

## 技术支持

如有问题，请检查：
1. 配置文件是否正确
2. 数据库连接是否正常
3. API 密钥是否有效
4. 日志文件中的错误信息

## 许可证

本项目仅供学习交流使用，请遵守小红书平台规则。
