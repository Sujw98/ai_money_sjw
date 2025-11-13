"""
灵感挖掘智能体 - 负责从小红书搜索优质内容作为参考
"""
import logging
from typing import List, Dict, Any
from src.models.agent_models import InspirationInput, InspirationOutput, XHSNoteInfo
from src.database.db_manager import get_db_manager
from src.database.dao import InspirationDAO, TopicDAO

logger = logging.getLogger(__name__)


class InspirationAgent:
    """灵感挖掘智能体"""
    
    def __init__(self):
        """初始化灵感挖掘智能体"""
        logger.info("灵感挖掘智能体初始化完成")
    
    def search_xiaohongshu(self, keywords: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        搜索小红书获取优质内容
        
        注意：这个方法需要在工作流中通过MCP工具调用，这里只是占位
        
        Args:
            keywords: 搜索关键词
            top_n: 获取前N个结果
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        # 此方法将在workflow中通过MCP的search_feeds工具实际调用
        # 这里返回空列表作为占位
        logger.info(f"搜索小红书关键词: {keywords}, top_n: {top_n}")
        return []
    
    def parse_search_results(self, search_results: List[Dict[str, Any]], top_n: int = 10) -> List[XHSNoteInfo]:
        """
        解析搜索结果，提取并排序
        
        Args:
            search_results: MCP返回的搜索结果
            top_n: 取前N个
            
        Returns:
            List[XHSNoteInfo]: 解析后的笔记信息列表
        """
        try:
            notes = []
            
            for item in search_results:
                # 根据MCP返回的数据结构解析
                note = XHSNoteInfo(
                    xhs_note_id=item.get('id', ''),
                    title=item.get('title', ''),
                    content=item.get('desc', '')[:500],  # 限制长度
                    author=item.get('author', {}).get('nickname', ''),
                    likes=item.get('interactInfo', {}).get('likedCount', 0),
                    collects=item.get('interactInfo', {}).get('collectedCount', 0),
                    comments=item.get('interactInfo', {}).get('commentCount', 0),
                    url=f"https://www.xiaohongshu.com/explore/{item.get('id', '')}"
                )
                notes.append(note)
            
            # 按点赞+收藏总数排序
            notes.sort(key=lambda x: x.likes + x.collects, reverse=True)
            
            # 取前N个
            return notes[:top_n]
            
        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")
            return []
    
    def run(self, input_data: InspirationInput, search_results: List[Dict[str, Any]] = None) -> InspirationOutput:
        """
        执行灵感挖掘智能体
        
        Args:
            input_data: 输入数据
            search_results: MCP搜索结果（在workflow中传入）
            
        Returns:
            InspirationOutput: 输出结果
        """
        try:
            logger.info(f"开始挖掘灵感，主题ID: {input_data.topic_id}, 关键词: {input_data.keywords}")
            
            # 如果提供了搜索结果，解析它
            if search_results:
                inspirations = self.parse_search_results(search_results, input_data.top_n)
            else:
                inspirations = []
                logger.warning("未提供搜索结果，灵感列表为空")
            
            # 保存到数据库
            db_manager = get_db_manager()
            with db_manager.get_session() as session:
                if inspirations:
                    # 转换为字典格式
                    inspirations_data = [insp.model_dump() for insp in inspirations]
                    InspirationDAO.batch_create(
                        session=session,
                        topic_id=input_data.topic_id,
                        inspirations_data=inspirations_data
                    )
                    logger.info(f"保存了 {len(inspirations)} 条灵感素材")
            
            return InspirationOutput(
                topic_id=input_data.topic_id,
                inspirations=inspirations,
                total_found=len(inspirations)
            )
            
        except Exception as e:
            logger.error(f"灵感挖掘失败: {e}")
            # 返回空结果而不是抛出异常，让流程继续
            return InspirationOutput(
                topic_id=input_data.topic_id,
                inspirations=[],
                total_found=0
            )
