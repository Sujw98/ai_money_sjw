"""
LangGraph工作流 - 编排多智能体协作流程
"""
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from src.workflows.state import WorkflowState
from src.agents.outline_agent import OutlineAgent
from src.agents.inspiration_agent import InspirationAgent
from src.agents.content_agent import ContentAgent
from src.agents.operation_agent import OperationAgent
from src.models.agent_models import (
    OutlineInput, InspirationInput, ContentGenerationInput, OperationInput
)
from src.database.db_manager import get_db_manager
from src.database.dao import TopicDAO, PublishRecordDAO
from src.models.db_models import TopicStatus, PublishStatus
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentWorkflow:
    """内容生成与发布工作流"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """
        初始化工作流
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
            model: 模型名称
        """
        # 初始化各个智能体
        self.outline_agent = OutlineAgent(api_key, base_url, model)
        self.inspiration_agent = InspirationAgent()
        self.content_agent = ContentAgent(api_key, base_url, model)
        self.operation_agent = OperationAgent(api_key, base_url, model)
        
        # 构建工作流图
        self.workflow = self._build_workflow()
        
        logger.info("内容工作流初始化完成")
    
    def _build_workflow(self) -> StateGraph:
        """构建工作流图"""
        workflow = StateGraph(WorkflowState)
        
        # 添加节点
        workflow.add_node("outline", self.outline_node)
        workflow.add_node("inspiration", self.inspiration_node)
        workflow.add_node("content", self.content_node)
        workflow.add_node("operation", self.operation_node)
        workflow.add_node("publish", self.publish_node)
        workflow.add_node("save", self.save_node)
        
        # 设置入口
        workflow.set_entry_point("outline")
        
        # 添加边
        workflow.add_edge("outline", "inspiration")
        workflow.add_edge("inspiration", "content")
        workflow.add_edge("content", "operation")
        workflow.add_edge("operation", "publish")
        workflow.add_edge("publish", "save")
        workflow.add_edge("save", END)
        
        return workflow.compile()
    
    def outline_node(self, state: WorkflowState) -> WorkflowState:
        """大纲规划节点 - 获取下一个主题"""
        try:
            logger.info("=== 执行大纲规划节点 ===")
            
            outline_input = OutlineInput(
                resource_name=state.get("resource_name", ""),
                outline_id=state.get("outline_id")
            )
            
            output = self.outline_agent.run(outline_input)
            
            state["outline_id"] = output.outline_id
            state["topic_info"] = output.current_topic
            state["has_more_topics"] = output.has_more
            
            if output.current_topic:
                state["topic_id"] = state.get("topic_id")  # 从数据库获取
                # 需要通过数据库查询获取实际的topic_id
                db_manager = get_db_manager()
                with db_manager.get_session() as session:
                    topic = TopicDAO.get_next_pending(session, output.outline_id)
                    if topic:
                        state["topic_id"] = topic.id
                
                logger.info(f"获取到主题: {output.current_topic.title}")
            else:
                logger.info("没有更多待处理主题")
                state["topic_id"] = None
            
            state["current_step"] = "outline_completed"
            return state
            
        except Exception as e:
            logger.error(f"大纲规划节点执行失败: {e}")
            state["error_message"] = str(e)
            state["current_step"] = "outline_failed"
            return state
    
    def inspiration_node(self, state: WorkflowState) -> WorkflowState:
        """灵感挖掘节点 - 搜索小红书优质内容"""
        try:
            logger.info("=== 执行灵感挖掘节点 ===")
            
            if not state.get("topic_id"):
                logger.warning("没有主题ID，跳过灵感挖掘")
                state["inspirations"] = []
                return state
            
            topic_info = state.get("topic_info")
            if not topic_info:
                logger.warning("没有主题信息，跳过灵感挖掘")
                state["inspirations"] = []
                return state
            
            inspiration_input = InspirationInput(
                topic_id=state["topic_id"],
                keywords=topic_info.keywords,
                top_n=10
            )
            
            # 注意：这里需要传入MCP搜索结果
            # 实际使用时，应该先调用MCP的search_feeds，然后将结果传入
            search_results = state.get("search_results", [])
            
            output = self.inspiration_agent.run(inspiration_input, search_results)
            
            state["inspirations"] = output.inspirations
            logger.info(f"找到 {len(output.inspirations)} 条灵感素材")
            
            state["current_step"] = "inspiration_completed"
            return state
            
        except Exception as e:
            logger.error(f"灵感挖掘节点执行失败: {e}")
            state["error_message"] = str(e)
            state["inspirations"] = []
            state["current_step"] = "inspiration_failed"
            return state
    
    def content_node(self, state: WorkflowState) -> WorkflowState:
        """内容创作节点 - 生成原创内容"""
        try:
            logger.info("=== 执行内容创作节点 ===")
            
            topic_info = state.get("topic_info")
            if not topic_info or not state.get("topic_id"):
                raise ValueError("缺少主题信息")
            
            content_input = ContentGenerationInput(
                topic_id=state["topic_id"],
                topic_title=topic_info.title,
                topic_content=topic_info.content,
                inspirations=state.get("inspirations", [])
            )
            
            output = self.content_agent.run(content_input)
            
            state["raw_content"] = output.raw_content
            logger.info(f"内容创作完成: {output.raw_content.title}")
            
            state["current_step"] = "content_completed"
            return state
            
        except Exception as e:
            logger.error(f"内容创作节点执行失败: {e}")
            state["error_message"] = str(e)
            state["current_step"] = "content_failed"
            return state
    
    def operation_node(self, state: WorkflowState) -> WorkflowState:
        """运营优化节点 - 优化标题和内容"""
        try:
            logger.info("=== 执行运营优化节点 ===")
            
            raw_content = state.get("raw_content")
            if not raw_content or not state.get("topic_id"):
                raise ValueError("缺少原始内容")
            
            operation_input = OperationInput(
                topic_id=state["topic_id"],
                raw_title=raw_content.title,
                raw_content=raw_content.content,
                raw_tags=raw_content.tags
            )
            
            output = self.operation_agent.run(operation_input)
            
            state["optimized_content"] = output.optimized_content
            logger.info(f"内容优化完成: {output.optimized_content.title}")
            logger.info(f"优化说明: {output.optimized_content.optimization_notes}")
            
            state["current_step"] = "operation_completed"
            return state
            
        except Exception as e:
            logger.error(f"运营优化节点执行失败: {e}")
            state["error_message"] = str(e)
            state["current_step"] = "operation_failed"
            return state
    
    def publish_node(self, state: WorkflowState) -> WorkflowState:
        """发布节点 - 发布到小红书"""
        try:
            logger.info("=== 执行发布节点 ===")
            
            optimized_content = state.get("optimized_content")
            if not optimized_content:
                raise ValueError("缺少优化后的内容")
            
            # 这里需要实际调用MCP的publish_content
            # 暂时标记为待发布
            logger.info(f"准备发布内容: {optimized_content.title}")
            logger.info(f"标签: {', '.join(optimized_content.tags)}")
            
            # 实际发布逻辑应该在这里通过MCP工具调用
            # 这里先模拟成功
            state["publish_success"] = True
            state["publish_note_id"] = None  # 实际发布后会有
            state["publish_error"] = None
            
            state["current_step"] = "publish_completed"
            return state
            
        except Exception as e:
            logger.error(f"发布节点执行失败: {e}")
            state["error_message"] = str(e)
            state["publish_success"] = False
            state["publish_error"] = str(e)
            state["current_step"] = "publish_failed"
            return state
    
    def save_node(self, state: WorkflowState) -> WorkflowState:
        """保存节点 - 更新数据库状态"""
        try:
            logger.info("=== 执行保存节点 ===")
            
            db_manager = get_db_manager()
            with db_manager.get_session() as session:
                topic_id = state.get("topic_id")
                
                if topic_id:
                    # 更新主题状态
                    if state.get("publish_success"):
                        TopicDAO.update_status(session, topic_id, TopicStatus.COMPLETED)
                        logger.info(f"主题 {topic_id} 标记为已完成")
                        
                        # 创建发布记录
                        from src.database.dao import ContentDAO
                        content = ContentDAO.get_by_topic(session, topic_id)
                        if content:
                            PublishRecordDAO.create(
                                session=session,
                                content_id=content.id,
                                xhs_note_id=state.get("publish_note_id"),
                                status=PublishStatus.SUCCESS if state.get("publish_success") else PublishStatus.FAILED
                            )
                    else:
                        TopicDAO.update_status(session, topic_id, TopicStatus.FAILED)
                        logger.warning(f"主题 {topic_id} 标记为失败")
                    
                    # 更新大纲进度
                    from src.database.dao import OutlineDAO
                    outline_id = state.get("outline_id")
                    if outline_id:
                        outline = OutlineDAO.get_by_id(session, outline_id)
                        if outline:
                            completed = sum(1 for t in outline.topics if t.status == TopicStatus.COMPLETED)
                            OutlineDAO.update_progress(session, outline_id, completed)
            
            state["current_step"] = "save_completed"
            logger.info("工作流执行完成")
            return state
            
        except Exception as e:
            logger.error(f"保存节点执行失败: {e}")
            state["error_message"] = str(e)
            state["current_step"] = "save_failed"
            return state
    
    def run(self, resource_name: str = None, outline_id: int = None) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            resource_name: 资源名称（创建新大纲时使用）
            outline_id: 大纲ID（继续现有大纲时使用）
            
        Returns:
            Dict: 执行结果
        """
        try:
            # 初始化状态
            initial_state: WorkflowState = {
                "resource_name": resource_name or "",
                "outline_id": outline_id,
                "has_more_topics": True,
                "inspirations": [],
                "publish_success": False,
                "current_step": "starting",
                "retry_count": 0
            }
            
            logger.info("开始执行工作流")
            
            # 执行工作流
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get("publish_success", False),
                "outline_id": final_state.get("outline_id"),
                "topic_id": final_state.get("topic_id"),
                "has_more_topics": final_state.get("has_more_topics", False),
                "error_message": final_state.get("error_message")
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
