---
trigger: model_decision
description: python编程语言开发的项目必须执行该规则
---

# Python 项目开发规范

## 虚拟环境管理

### 创建虚拟环境
在开始任何 Python 项目编程前，必须先创建独立的虚拟环境：

conda create -n {项目名} python=3.13.7

**说明：**
- 虚拟环境名称使用项目名称
- Python 版本固定使用 3.13.7

### 激活虚拟环境
**重要：这是必须执行的步骤**

在进行任何编程调试工作前，或者开启终端后执行命令前，必须先激活虚拟环境：

conda activate {项目名}

### 最佳实践
1. 每个项目使用独立的虚拟环境，避免依赖冲突
2. 激活虚拟环境后再安装依赖包
3. 在虚拟环境中进行所有的开发、测试和调试工作
4. 使用 `pip freeze > requirements.txt` 记录项目依赖

### 示例工作流程
# 1. 创建虚拟环境
conda create -n my_project python=3.13.7

# 2. 激活虚拟环境（开启终端后执行命令前必须执行）
conda activate my_project

# 3. 安装依赖（必须先激活虚拟环境）
pip install -r requirements.txt

# 4. 开始编程和调试
python main.py
