"""
小红书内容生成与发布运营系统 - 主入口
"""
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_settings
from src.utils.logger import setup_logger
from src.database.db_manager import init_db_manager
from src.workflows.workflow import ContentWorkflow


def main():
    """主函数"""
    # 初始化日志
    logger = setup_logger("xiaohongshu_agent", "INFO", "logs/app.log")
    logger.info("=" * 60)
    logger.info("小红书内容生成与发布运营系统启动")
    logger.info("=" * 60)
    
    try:
        # 加载配置
        logger.info("加载配置...")
        settings = get_settings()
        
        # 初始化数据库
        logger.info("初始化数据库连接...")
        db_manager = init_db_manager(settings.database_url)
        
        # 初始化工作流
        logger.info("初始化工作流...")
        workflow = ContentWorkflow(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model
        )
        
        logger.info("系统初始化完成！")
        logger.info("")
        
        # 交互式菜单
        while True:
            print("\n" + "=" * 60)
            print("小红书内容生成与发布运营系统")
            print("=" * 60)
            print("1. 创建新的内容大纲")
            print("2. 继续处理现有大纲")
            print("3. 查看所有大纲")
            print("4. 退出系统")
            print("=" * 60)
            
            choice = input("\n请选择操作 (1-4): ").strip()
            
            if choice == "1":
                create_new_outline(workflow)
            elif choice == "2":
                continue_existing_outline(workflow)
            elif choice == "3":
                view_all_outlines()
            elif choice == "4":
                logger.info("系统退出")
                print("\n再见！👋")
                break
            else:
                print("无效的选择，请重新输入")
        
    except KeyboardInterrupt:
        logger.info("用户中断系统")
        print("\n\n系统已停止")
    except Exception as e:
        logger.error(f"系统运行错误: {e}", exc_info=True)
        print(f"\n错误: {e}")
    finally:
        # 清理资源
        try:
            db_manager = init_db_manager(settings.database_url)
            db_manager.close()
        except:
            pass


def create_new_outline(workflow: ContentWorkflow):
    """创建新的内容大纲"""
    print("\n" + "-" * 60)
    print("创建新的内容大纲")
    print("-" * 60)
    
    resource_name = input("请输入资源名称（如：经济学原理）: ").strip()
    
    if not resource_name:
        print("资源名称不能为空")
        return
    
    print(f"\n开始为《{resource_name}》创建大纲并生成第一篇内容...")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    try:
        result = workflow.run(resource_name=resource_name)
        
        if result.get("success"):
            print(f"\n✅ 内容生成成功！")
            print(f"   大纲ID: {result.get('outline_id')}")
            print(f"   主题ID: {result.get('topic_id')}")
            print(f"   还有更多主题: {'是' if result.get('has_more_topics') else '否'}")
        else:
            print(f"\n❌ 内容生成失败: {result.get('error_message')}")
            
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")


def continue_existing_outline(workflow: ContentWorkflow):
    """继续处理现有大纲"""
    print("\n" + "-" * 60)
    print("继续处理现有大纲")
    print("-" * 60)
    
    outline_id = input("请输入大纲ID: ").strip()
    
    if not outline_id or not outline_id.isdigit():
        print("无效的大纲ID")
        return
    
    outline_id = int(outline_id)
    
    print(f"\n开始处理大纲 {outline_id} 的下一个主题...")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    try:
        result = workflow.run(outline_id=outline_id)
        
        if result.get("success"):
            print(f"\n✅ 内容生成成功！")
            print(f"   主题ID: {result.get('topic_id')}")
            print(f"   还有更多主题: {'是' if result.get('has_more_topics') else '否'}")
        else:
            print(f"\n❌ 内容生成失败: {result.get('error_message')}")
            
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")


def view_all_outlines():
    """查看所有大纲"""
    print("\n" + "-" * 60)
    print("所有大纲列表")
    print("-" * 60)
    
    try:
        from src.database.db_manager import get_db_manager
        from src.database.dao import OutlineDAO
        
        db_manager = get_db_manager()
        with db_manager.get_session() as session:
            outlines = OutlineDAO.get_all(session)
            
            if not outlines:
                print("暂无大纲记录")
                return
            
            for outline in outlines:
                print(f"\nID: {outline.id}")
                print(f"资源名称: {outline.resource_name}")
                print(f"总主题数: {outline.total_topics}")
                print(f"已完成: {outline.completed_topics}")
                print(f"进度: {outline.completed_topics}/{outline.total_topics} ({outline.completed_topics*100//outline.total_topics if outline.total_topics > 0 else 0}%)")
                print(f"创建时间: {outline.created_at}")
                print("-" * 60)
                
    except Exception as e:
        print(f"\n❌ 查询出错: {e}")


if __name__ == "__main__":
    main()
