"""
系统测试脚本 - 验证各模块功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_config():
    """测试配置加载"""
    print("\n=== 测试配置加载 ===")
    try:
        from src.utils.config import get_settings
        settings = get_settings()
        print(f"✓ 配置加载成功")
        print(f"  - DeepSeek Model: {settings.deepseek_model}")
        print(f"  - MySQL Host: {settings.mysql_host}")
        print(f"  - Database: {settings.mysql_database}")
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False


def test_database():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    try:
        from src.utils.config import get_settings
        from src.database.db_manager import init_db_manager
        
        settings = get_settings()
        db_manager = init_db_manager(settings.database_url)
        
        print(f"✓ 数据库连接成功")
        print(f"  - URL: {settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}")
        
        # 测试会话
        with db_manager.get_session() as session:
            print(f"✓ 数据库会话创建成功")
        
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print(f"  提示: 请确保 MySQL 已启动并且配置正确")
        return False


def test_models():
    """测试数据模型"""
    print("\n=== 测试数据模型 ===")
    try:
        from src.models.agent_models import (
            OutlineInput, TopicInfo, InspirationInput,
            ContentGenerationInput, OperationInput
        )
        
        # 测试创建模型实例
        outline_input = OutlineInput(resource_name="测试资源")
        topic = TopicInfo(
            title="测试主题",
            content="测试内容",
            keywords="关键词1,关键词2",
            order_index=1
        )
        
        print(f"✓ Pydantic 模型创建成功")
        print(f"  - OutlineInput: {outline_input.resource_name}")
        print(f"  - TopicInfo: {topic.title}")
        
        return True
    except Exception as e:
        print(f"✗ 数据模型测试失败: {e}")
        return False


def test_agents():
    """测试智能体初始化"""
    print("\n=== 测试智能体初始化 ===")
    try:
        from src.utils.config import get_settings
        from src.agents.outline_agent import OutlineAgent
        from src.agents.inspiration_agent import InspirationAgent
        from src.agents.content_agent import ContentAgent
        from src.agents.operation_agent import OperationAgent
        
        settings = get_settings()
        
        # 初始化智能体
        outline_agent = OutlineAgent(
            settings.deepseek_api_key,
            settings.deepseek_base_url,
            settings.deepseek_model
        )
        inspiration_agent = InspirationAgent()
        content_agent = ContentAgent(
            settings.deepseek_api_key,
            settings.deepseek_base_url,
            settings.deepseek_model
        )
        operation_agent = OperationAgent(
            settings.deepseek_api_key,
            settings.deepseek_base_url,
            settings.deepseek_model
        )
        
        print(f"✓ 所有智能体初始化成功")
        print(f"  - OutlineAgent ✓")
        print(f"  - InspirationAgent ✓")
        print(f"  - ContentAgent ✓")
        print(f"  - OperationAgent ✓")
        
        return True
    except Exception as e:
        print(f"✗ 智能体初始化失败: {e}")
        return False


def test_workflow():
    """测试工作流初始化"""
    print("\n=== 测试工作流初始化 ===")
    try:
        from src.utils.config import get_settings
        from src.workflows.workflow import ContentWorkflow
        
        settings = get_settings()
        
        workflow = ContentWorkflow(
            settings.deepseek_api_key,
            settings.deepseek_base_url,
            settings.deepseek_model
        )
        
        print(f"✓ 工作流初始化成功")
        print(f"  - 工作流图已编译")
        
        return True
    except Exception as e:
        print(f"✗ 工作流初始化失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("小红书内容生成系统 - 功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("配置加载", test_config()))
    results.append(("数据库连接", test_database()))
    results.append(("数据模型", test_models()))
    results.append(("智能体初始化", test_agents()))
    results.append(("工作流初始化", test_workflow()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "-" * 60)
    print(f"总计: {passed}/{total} 项测试通过")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！系统已就绪。")
        print("\n下一步:")
        print("1. 确保 MySQL 数据库已启动")
        print("2. 运行 'python init_db.py' 初始化数据库")
        print("3. 运行 'python main.py' 启动系统")
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")
        print("\n常见问题:")
        print("1. 检查 .env 文件是否正确配置")
        print("2. 确保已安装所有依赖: pip install -r requirements.txt")
        print("3. 确保 MySQL 数据库已启动并可访问")


if __name__ == "__main__":
    main()
