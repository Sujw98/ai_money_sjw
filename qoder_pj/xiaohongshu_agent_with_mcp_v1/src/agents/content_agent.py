"""
内容创作智能体 - 负责生成原创内容
"""
import logging
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.models.agent_models import (
    ContentGenerationInput, ContentGenerationOutput,
    GeneratedContent, XHSNoteInfo
)
from src.database.db_manager import get_db_manager
from src.database.dao import ContentDAO

logger = logging.getLogger(__name__)


class ContentAgent:
    """内容创作智能体"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """
        初始化内容创作智能体
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
        """
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.8  # 提高创造性
        )
        
        # 内容创作提示模板
        self.content_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的财经理财内容创作者，擅长在小红书平台创作深入浅出、通俗易懂的财经知识内容。

创作要求：
1. 内容要原创，结合主题要点和参考素材创作，但不能抄袭
2. 语言要生动活泼，贴近年轻用户，多用比喻和案例
3. 结构清晰：开头吸引人→核心知识点→实用建议→总结
4. 长度控制在800-1500字
5. 要有干货，让用户学到实用知识
6. 避免过于专业的术语，要通俗化表达

请以JSON格式输出：
{{
    "title": "内容标题（20字以内）",
    "content": "正文内容（包含表情符号增加活泼感）",
    "tags": ["标签1", "标签2", "标签3"]
}}"""),
            ("user", """主题标题：{topic_title}

主题要点：
{topic_content}

参考素材（优质小红书内容）：
{inspirations}

请基于以上信息创作一篇小红书图文内容。""")
        ])
        
        logger.info("内容创作智能体初始化完成")
    
    def format_inspirations(self, inspirations: List[XHSNoteInfo]) -> str:
        """
        格式化灵感素材为文本
        
        Args:
            inspirations: 灵感素材列表
            
        Returns:
            str: 格式化后的文本
        """
        if not inspirations:
            return "暂无参考素材"
        
        result = []
        for i, insp in enumerate(inspirations[:5], 1):  # 只用前5个
            result.append(f"{i}. 《{insp.title}》")
            result.append(f"   点赞: {insp.likes}, 收藏: {insp.collects}")
            if insp.content:
                result.append(f"   内容摘要: {insp.content[:200]}...")
            result.append("")
        
        return "\n".join(result)
    
    def run(self, input_data: ContentGenerationInput) -> ContentGenerationOutput:
        """
        执行内容创作智能体
        
        Args:
            input_data: 输入数据
            
        Returns:
            ContentGenerationOutput: 输出结果
        """
        try:
            logger.info(f"开始创作内容，主题: {input_data.topic_title}")
            
            # 格式化灵感素材
            inspirations_text = self.format_inspirations(input_data.inspirations)
            
            # 调用LLM生成内容
            chain = self.content_prompt | self.llm
            response = chain.invoke({
                "topic_title": input_data.topic_title,
                "topic_content": input_data.topic_content,
                "inspirations": inspirations_text
            })
            
            # 解析响应
            import json
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            content_data = json.loads(content.strip())
            
            # 创建生成内容对象
            generated = GeneratedContent(
                title=content_data.get("title", input_data.topic_title),
                content=content_data.get("content", ""),
                tags=content_data.get("tags", [])
            )
            
            # 保存到数据库
            db_manager = get_db_manager()
            with db_manager.get_session() as session:
                ContentDAO.create(
                    session=session,
                    topic_id=input_data.topic_id,
                    raw_title=generated.title,
                    raw_content=generated.content,
                    tags=",".join(generated.tags) if generated.tags else ""
                )
                logger.info(f"内容已保存到数据库，主题ID: {input_data.topic_id}")
            
            return ContentGenerationOutput(
                topic_id=input_data.topic_id,
                raw_content=generated
            )
            
        except Exception as e:
            logger.error(f"内容创作失败: {e}")
            raise
