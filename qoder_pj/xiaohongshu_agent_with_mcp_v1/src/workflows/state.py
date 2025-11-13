"""
工作流状态定义 - 使用TypedDict定义状态
"""
from typing import TypedDict, List, Optional, Dict, Any
from src.models.agent_models import (
    TopicInfo, XHSNoteInfo, GeneratedContent, OptimizedContent
)


class WorkflowState(TypedDict, total=False):
    """工作流状态"""
    
    # 大纲相关
    outline_id: int  # 大纲ID
    resource_name: str  # 资源名称
    
    # 当前主题
    topic_id: Optional[int]  # 主题ID
    topic_info: Optional[TopicInfo]  # 主题详细信息
    has_more_topics: bool  # 是否还有更多主题
    
    # 灵感素材
    inspirations: List[XHSNoteInfo]  # 灵感素材列表
    search_results: Optional[List[Dict[str, Any]]]  # MCP搜索原始结果
    
    # 内容生成
    raw_content: Optional[GeneratedContent]  # 原始生成的内容
    
    # 内容优化
    optimized_content: Optional[OptimizedContent]  # 优化后的内容
    
    # 发布结果
    publish_success: bool  # 发布是否成功
    publish_note_id: Optional[str]  # 发布后的笔记ID
    publish_error: Optional[str]  # 发布错误信息
    
    # 流程控制
    current_step: str  # 当前步骤
    error_message: Optional[str]  # 错误信息
    retry_count: int  # 重试次数
