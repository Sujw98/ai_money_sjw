"""
数据库ORM模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class TopicStatus(enum.Enum):
    """主题状态枚举"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class PublishStatus(enum.Enum):
    """发布状态枚举"""
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    PENDING = "pending"  # 待发布


class Outline(Base):
    """大纲表 - 存储资源的整体规划"""
    __tablename__ = 'outlines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_name = Column(String(255), nullable=False, comment='资源名称（书籍/课程名）')
    resource_type = Column(String(50), default='book', comment='资源类型')
    total_topics = Column(Integer, default=0, comment='总主题数量')
    completed_topics = Column(Integer, default=0, comment='已完成主题数')
    description = Column(Text, comment='大纲描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联关系
    topics = relationship("Topic", back_populates="outline", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Outline(id={self.id}, resource_name='{self.resource_name}', total_topics={self.total_topics})>"


class Topic(Base):
    """主题表 - 存储具体的内容主题"""
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    outline_id = Column(Integer, ForeignKey('outlines.id'), nullable=False, comment='所属大纲ID')
    topic_title = Column(String(255), nullable=False, comment='主题标题')
    topic_content = Column(Text, comment='主题详细内容/要点')
    order_index = Column(Integer, nullable=False, comment='顺序索引')
    status = Column(Enum(TopicStatus), default=TopicStatus.PENDING, comment='处理状态')
    keywords = Column(String(500), comment='关键词（用于搜索）')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联关系
    outline = relationship("Outline", back_populates="topics")
    inspirations = relationship("Inspiration", back_populates="topic", cascade="all, delete-orphan")
    contents = relationship("Content", back_populates="topic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Topic(id={self.id}, title='{self.topic_title}', status={self.status.value})>"


class Inspiration(Base):
    """灵感素材表 - 存储从小红书搜索的优质内容"""
    __tablename__ = 'inspirations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False, comment='所属主题ID')
    xhs_note_id = Column(String(100), comment='小红书笔记ID')
    title = Column(String(500), comment='笔记标题')
    content = Column(Text, comment='笔记内容摘要')
    author = Column(String(100), comment='作者昵称')
    likes = Column(Integer, default=0, comment='点赞数')
    collects = Column(Integer, default=0, comment='收藏数')
    comments = Column(Integer, default=0, comment='评论数')
    url = Column(String(500), comment='笔记链接')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 关联关系
    topic = relationship("Topic", back_populates="inspirations")
    
    def __repr__(self):
        return f"<Inspiration(id={self.id}, xhs_note_id='{self.xhs_note_id}', likes={self.likes})>"


class Content(Base):
    """内容表 - 存储生成和优化后的内容"""
    __tablename__ = 'contents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False, comment='所属主题ID')
    raw_title = Column(String(500), comment='原始标题')
    raw_content = Column(Text, comment='原始内容')
    optimized_title = Column(String(500), comment='优化后标题')
    optimized_content = Column(Text, comment='优化后内容')
    tags = Column(String(500), comment='标签（逗号分隔）')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联关系
    topic = relationship("Topic", back_populates="contents")
    publish_records = relationship("PublishRecord", back_populates="content", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Content(id={self.id}, topic_id={self.topic_id}, optimized_title='{self.optimized_title}')>"


class PublishRecord(Base):
    """发布记录表 - 存储内容发布情况"""
    __tablename__ = 'publish_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey('contents.id'), nullable=False, comment='内容ID')
    xhs_note_id = Column(String(100), comment='小红书笔记ID')
    publish_time = Column(DateTime, comment='发布时间')
    status = Column(Enum(PublishStatus), default=PublishStatus.PENDING, comment='发布状态')
    error_message = Column(Text, comment='错误信息')
    retry_count = Column(Integer, default=0, comment='重试次数')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 关联关系
    content = relationship("Content", back_populates="publish_records")
    
    def __repr__(self):
        return f"<PublishRecord(id={self.id}, content_id={self.content_id}, status={self.status.value})>"
