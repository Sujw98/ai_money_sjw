"""
Agent数据模型 - 定义各个智能体的输入输出模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ========== 大纲规划智能体模型 ==========

class OutlineInput(BaseModel):
    """大纲规划智能体输入"""
    resource_name: str = Field(..., description="资源名称（书籍/课程名）")
    resource_type: str = Field(default="book", description="资源类型")
    outline_id: Optional[int] = Field(None, description="已存在的大纲ID，用于获取下一个主题")


class TopicInfo(BaseModel):
    """主题信息"""
    title: str = Field(..., description="主题标题")
    content: str = Field(..., description="主题详细内容/要点")
    keywords: str = Field(..., description="关键词（用于搜索）")
    order_index: int = Field(..., description="顺序索引")


class OutlineOutput(BaseModel):
    """大纲规划智能体输出"""
    outline_id: int = Field(..., description="大纲ID")
    current_topic: Optional[TopicInfo] = Field(None, description="当前待处理主题")
    has_more: bool = Field(default=True, description="是否还有更多主题")
    total_topics: int = Field(default=0, description="总主题数")


# ========== 灵感挖掘智能体模型 ==========

class InspirationInput(BaseModel):
    """灵感挖掘智能体输入"""
    topic_id: int = Field(..., description="主题ID")
    keywords: str = Field(..., description="搜索关键词")
    top_n: int = Field(default=10, description="获取前N个优质内容")


class XHSNoteInfo(BaseModel):
    """小红书笔记信息"""
    xhs_note_id: str = Field(..., description="小红书笔记ID")
    title: str = Field(..., description="笔记标题")
    content: str = Field(default="", description="笔记内容摘要")
    author: str = Field(default="", description="作者昵称")
    likes: int = Field(default=0, description="点赞数")
    collects: int = Field(default=0, description="收藏数")
    comments: int = Field(default=0, description="评论数")
    url: str = Field(default="", description="笔记链接")


class InspirationOutput(BaseModel):
    """灵感挖掘智能体输出"""
    topic_id: int = Field(..., description="主题ID")
    inspirations: List[XHSNoteInfo] = Field(default_factory=list, description="灵感素材列表")
    total_found: int = Field(default=0, description="找到的总数")


# ========== 内容创作智能体模型 ==========

class ContentGenerationInput(BaseModel):
    """内容创作智能体输入"""
    topic_id: int = Field(..., description="主题ID")
    topic_title: str = Field(..., description="主题标题")
    topic_content: str = Field(..., description="主题详细内容")
    inspirations: List[XHSNoteInfo] = Field(default_factory=list, description="参考的灵感素材")


class GeneratedContent(BaseModel):
    """生成的内容"""
    title: str = Field(..., description="标题")
    content: str = Field(..., description="正文内容")
    tags: List[str] = Field(default_factory=list, description="建议的标签")


class ContentGenerationOutput(BaseModel):
    """内容创作智能体输出"""
    topic_id: int = Field(..., description="主题ID")
    raw_content: GeneratedContent = Field(..., description="原始生成的内容")


# ========== 运营优化智能体模型 ==========

class OperationInput(BaseModel):
    """运营优化智能体输入"""
    topic_id: int = Field(..., description="主题ID")
    raw_title: str = Field(..., description="原始标题")
    raw_content: str = Field(..., description="原始内容")
    raw_tags: List[str] = Field(default_factory=list, description="原始标签")


class OptimizedContent(BaseModel):
    """优化后的内容"""
    title: str = Field(..., description="优化后的标题")
    content: str = Field(..., description="优化后的内容")
    tags: List[str] = Field(default_factory=list, description="优化后的标签")
    optimization_notes: str = Field(default="", description="优化说明")


class OperationOutput(BaseModel):
    """运营优化智能体输出"""
    topic_id: int = Field(..., description="主题ID")
    optimized_content: OptimizedContent = Field(..., description="优化后的内容")


# ========== 发布结果模型 ==========

class PublishResult(BaseModel):
    """发布结果"""
    success: bool = Field(..., description="是否成功")
    note_id: Optional[str] = Field(None, description="小红书笔记ID")
    error_message: Optional[str] = Field(None, description="错误信息")
    publish_time: Optional[str] = Field(None, description="发布时间")
