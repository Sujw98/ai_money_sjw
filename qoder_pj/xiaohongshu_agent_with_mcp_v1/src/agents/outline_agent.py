"""
大纲规划智能体 - 负责分析资源并制定内容大纲
"""
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.models.agent_models import OutlineInput, OutlineOutput, TopicInfo
from src.database.db_manager import get_db_manager
from src.database.dao import OutlineDAO, TopicDAO
from src.models.db_models import TopicStatus

logger = logging.getLogger(__name__)


class OutlineAgent:
    """大纲规划智能体"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """
        初始化大纲规划智能体
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
        """
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.7
        )
        
        # 创建大纲的提示模板
        self.outline_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的财经理财内容策划专家。你的任务是将财经理财类书籍或课程拆解成适合小红书平台发布的系列图文内容大纲。

要求：
1. 每个主题要独立完整，适合单篇图文呈现
2. 主题要有吸引力，贴近用户实际需求
3. 内容要深入浅出，适合普通用户理解
4. 每个主题包含：标题、详细内容要点、关键词
5. 建议拆解为15-30个主题

请以JSON格式输出，格式如下：
{{
    "total": 主题总数,
    "topics": [
        {{
            "order_index": 顺序,
            "title": "主题标题",
            "content": "详细内容要点",
            "keywords": "关键词1,关键词2,关键词3"
        }},
        ...
    ]
}}"""),
            ("user", "请为《{resource_name}》制定小红书内容大纲。")
        ])
        
        logger.info("大纲规划智能体初始化完成")
    
    def create_outline(self, resource_name: str, resource_type: str = "book") -> int:
        """
        创建新的大纲
        
        Args:
            resource_name: 资源名称
            resource_type: 资源类型
            
        Returns:
            int: 大纲ID
        """
        try:
            logger.info(f"开始为《{resource_name}》创建大纲")
            
            # 调用LLM生成大纲
            chain = self.outline_prompt | self.llm
            response = chain.invoke({"resource_name": resource_name})
            
            # 解析响应
            import json
            content = response.content
            # 提取JSON部分
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            outline_data = json.loads(content.strip())
            
            # 保存到数据库
            db_manager = get_db_manager()
            with db_manager.get_session() as session:
                # 创建大纲记录
                outline = OutlineDAO.create(
                    session=session,
                    resource_name=resource_name,
                    resource_type=resource_type,
                    description=f"《{resource_name}》内容大纲"
                )
                
                # 批量创建主题
                topics_data = outline_data.get("topics", [])
                TopicDAO.batch_create(
                    session=session,
                    outline_id=outline.id,
                    topics_data=topics_data
                )
                
                # 更新大纲的主题总数
                outline.total_topics = len(topics_data)
                session.flush()
                
                logger.info(f"大纲创建成功，ID: {outline.id}, 主题数: {len(topics_data)}")
                return outline.id
                
        except Exception as e:
            logger.error(f"创建大纲失败: {e}")
            raise
    
    def get_next_topic(self, outline_id: int) -> OutlineOutput:
        """
        获取下一个待处理的主题
        
        Args:
            outline_id: 大纲ID
            
        Returns:
            OutlineOutput: 包含下一个主题的输出
        """
        try:
            db_manager = get_db_manager()
            with db_manager.get_session() as session:
                # 获取大纲信息
                outline = OutlineDAO.get_by_id(session, outline_id)
                if not outline:
                    raise ValueError(f"大纲不存在: outline_id={outline_id}")
                
                # 获取下一个待处理主题
                next_topic = TopicDAO.get_next_pending(session, outline_id)
                
                if next_topic:
                    # 更新主题状态为处理中
                    TopicDAO.update_status(session, next_topic.id, TopicStatus.PROCESSING)
                    
                    topic_info = TopicInfo(
                        title=next_topic.topic_title,
                        content=next_topic.topic_content,
                        keywords=next_topic.keywords or "",
                        order_index=next_topic.order_index
                    )
                    
                    logger.info(f"获取到待处理主题: {next_topic.topic_title}")
                    
                    return OutlineOutput(
                        outline_id=outline_id,
                        current_topic=topic_info,
                        has_more=True,
                        total_topics=outline.total_topics
                    )
                else:
                    logger.info(f"大纲 {outline_id} 所有主题已处理完成")
                    return OutlineOutput(
                        outline_id=outline_id,
                        current_topic=None,
                        has_more=False,
                        total_topics=outline.total_topics
                    )
                    
        except Exception as e:
            logger.error(f"获取下一个主题失败: {e}")
            raise
    
    def run(self, input_data: OutlineInput) -> OutlineOutput:
        """
        执行大纲规划智能体
        
        Args:
            input_data: 输入数据
            
        Returns:
            OutlineOutput: 输出结果
        """
        if input_data.outline_id:
            # 如果已有大纲ID，获取下一个主题
            return self.get_next_topic(input_data.outline_id)
        else:
            # 创建新大纲
            outline_id = self.create_outline(
                input_data.resource_name,
                input_data.resource_type
            )
            # 获取第一个主题
            return self.get_next_topic(outline_id)
