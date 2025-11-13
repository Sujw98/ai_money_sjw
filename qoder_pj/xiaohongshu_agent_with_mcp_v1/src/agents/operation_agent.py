"""
运营优化智能体 - 负责优化内容标题和文案
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.models.agent_models import (
    OperationInput, OperationOutput, OptimizedContent
)
from src.database.db_manager import get_db_manager
from src.database.dao import ContentDAO

logger = logging.getLogger(__name__)


class OperationAgent:
    """运营优化智能体"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """
        初始化运营优化智能体
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
        """
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.9  # 更高的创造性用于标题党
        )
        
        # 优化提示模板
        self.optimization_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位资深的小红书运营专家，擅长打造爆款内容。你的任务是优化财经理财类内容，提升传播力和互动率。

优化要点：

1. 标题优化（重中之重）：
   - 使用吸引眼球的"标题党"技巧，但不要夸大失实
   - 加入数字、反转、疑问、痛点等元素
   - 例如："90%的人不知道的理财秘密"、"这样存钱，一年多赚5万！"
   - 控制在20字以内，要有冲击力

2. 内容优化：
   - 开头3行要抓人，直击痛点或抛出惊人观点
   - 适当增加表情符号，但不要过度（每段1-2个）
   - 分段要清晰，多用短句
   - 加入互动引导（如：你学会了吗？点赞收藏不迷路）
   - 强化实用性和可操作性

3. 标签优化：
   - 包含热门财经标签
   - 3-5个标签，平衡热门度和相关性
   - 例如：理财、财商、副业、存钱、投资

请以JSON格式输出：
{{
    "title": "优化后的标题",
    "content": "优化后的内容",
    "tags": ["标签1", "标签2", "标签3"],
    "optimization_notes": "优化说明"
}}"""),
            ("user", """原始标题：{raw_title}

原始内容：
{raw_content}

原始标签：{raw_tags}

请对以上内容进行运营优化。""")
        ])
        
        logger.info("运营优化智能体初始化完成")
    
    def run(self, input_data: OperationInput) -> OperationOutput:
        """
        执行运营优化智能体
        
        Args:
            input_data: 输入数据
            
        Returns:
            OperationOutput: 输出结果
        """
        try:
            logger.info(f"开始优化内容，主题ID: {input_data.topic_id}")
            
            # 调用LLM优化内容
            chain = self.optimization_prompt | self.llm
            response = chain.invoke({
                "raw_title": input_data.raw_title,
                "raw_content": input_data.raw_content,
                "raw_tags": ", ".join(input_data.raw_tags) if input_data.raw_tags else "无"
            })
            
            # 解析响应
            import json
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            optimized_data = json.loads(content.strip())
            
            # 创建优化内容对象
            optimized = OptimizedContent(
                title=optimized_data.get("title", input_data.raw_title),
                content=optimized_data.get("content", input_data.raw_content),
                tags=optimized_data.get("tags", input_data.raw_tags),
                optimization_notes=optimized_data.get("optimization_notes", "")
            )
            
            # 更新数据库
            db_manager = get_db_manager()
            with db_manager.get_session() as session:
                # 根据topic_id查找content
                from src.database.dao import ContentDAO
                content_record = ContentDAO.get_by_topic(session, input_data.topic_id)
                
                if content_record:
                    ContentDAO.update_optimized(
                        session=session,
                        content_id=content_record.id,
                        optimized_title=optimized.title,
                        optimized_content=optimized.content,
                        tags=",".join(optimized.tags) if optimized.tags else ""
                    )
                    logger.info(f"优化内容已保存，主题ID: {input_data.topic_id}")
                else:
                    logger.warning(f"未找到内容记录，主题ID: {input_data.topic_id}")
            
            logger.info(f"内容优化完成。优化说明: {optimized.optimization_notes}")
            
            return OperationOutput(
                topic_id=input_data.topic_id,
                optimized_content=optimized
            )
            
        except Exception as e:
            logger.error(f"内容优化失败: {e}")
            raise
