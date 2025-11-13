"""
数据访问层 - 封装数据库操作
"""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.db_models import (
    Outline, Topic, Inspiration, Content, PublishRecord,
    TopicStatus, PublishStatus
)

logger = logging.getLogger(__name__)


class OutlineDAO:
    """大纲数据访问对象"""
    
    @staticmethod
    def create(session: Session, resource_name: str, resource_type: str = "book", 
               description: str = None) -> Outline:
        """创建大纲"""
        outline = Outline(
            resource_name=resource_name,
            resource_type=resource_type,
            description=description
        )
        session.add(outline)
        session.flush()
        logger.info(f"创建大纲: {resource_name}")
        return outline
    
    @staticmethod
    def get_by_id(session: Session, outline_id: int) -> Optional[Outline]:
        """根据ID获取大纲"""
        return session.query(Outline).filter(Outline.id == outline_id).first()
    
    @staticmethod
    def get_all(session: Session) -> List[Outline]:
        """获取所有大纲"""
        return session.query(Outline).all()
    
    @staticmethod
    def update_progress(session: Session, outline_id: int, completed_topics: int):
        """更新大纲进度"""
        outline = session.query(Outline).filter(Outline.id == outline_id).first()
        if outline:
            outline.completed_topics = completed_topics
            outline.updated_at = datetime.now()
            session.flush()


class TopicDAO:
    """主题数据访问对象"""
    
    @staticmethod
    def create(session: Session, outline_id: int, topic_title: str, 
               topic_content: str, order_index: int, keywords: str = None) -> Topic:
        """创建主题"""
        topic = Topic(
            outline_id=outline_id,
            topic_title=topic_title,
            topic_content=topic_content,
            order_index=order_index,
            keywords=keywords,
            status=TopicStatus.PENDING
        )
        session.add(topic)
        session.flush()
        logger.info(f"创建主题: {topic_title}")
        return topic
    
    @staticmethod
    def batch_create(session: Session, outline_id: int, topics_data: List[dict]) -> List[Topic]:
        """批量创建主题"""
        topics = []
        for data in topics_data:
            topic = Topic(
                outline_id=outline_id,
                topic_title=data['title'],
                topic_content=data.get('content', ''),
                order_index=data['order_index'],
                keywords=data.get('keywords', ''),
                status=TopicStatus.PENDING
            )
            topics.append(topic)
        session.add_all(topics)
        session.flush()
        logger.info(f"批量创建主题: {len(topics)}个")
        return topics
    
    @staticmethod
    def get_next_pending(session: Session, outline_id: int) -> Optional[Topic]:
        """获取下一个待处理的主题"""
        return session.query(Topic).filter(
            Topic.outline_id == outline_id,
            Topic.status == TopicStatus.PENDING
        ).order_by(Topic.order_index).first()
    
    @staticmethod
    def update_status(session: Session, topic_id: int, status: TopicStatus):
        """更新主题状态"""
        topic = session.query(Topic).filter(Topic.id == topic_id).first()
        if topic:
            topic.status = status
            topic.updated_at = datetime.now()
            session.flush()
            logger.info(f"更新主题状态: topic_id={topic_id}, status={status.value}")
    
    @staticmethod
    def get_by_id(session: Session, topic_id: int) -> Optional[Topic]:
        """根据ID获取主题"""
        return session.query(Topic).filter(Topic.id == topic_id).first()


class InspirationDAO:
    """灵感素材数据访问对象"""
    
    @staticmethod
    def create(session: Session, topic_id: int, xhs_note_id: str, title: str,
               content: str = None, author: str = None, likes: int = 0,
               collects: int = 0, comments: int = 0, url: str = None) -> Inspiration:
        """创建灵感素材"""
        inspiration = Inspiration(
            topic_id=topic_id,
            xhs_note_id=xhs_note_id,
            title=title,
            content=content,
            author=author,
            likes=likes,
            collects=collects,
            comments=comments,
            url=url
        )
        session.add(inspiration)
        session.flush()
        return inspiration
    
    @staticmethod
    def batch_create(session: Session, topic_id: int, inspirations_data: List[dict]) -> List[Inspiration]:
        """批量创建灵感素材"""
        inspirations = []
        for data in inspirations_data:
            inspiration = Inspiration(
                topic_id=topic_id,
                xhs_note_id=data.get('xhs_note_id', ''),
                title=data.get('title', ''),
                content=data.get('content', ''),
                author=data.get('author', ''),
                likes=data.get('likes', 0),
                collects=data.get('collects', 0),
                comments=data.get('comments', 0),
                url=data.get('url', '')
            )
            inspirations.append(inspiration)
        session.add_all(inspirations)
        session.flush()
        logger.info(f"批量创建灵感素材: {len(inspirations)}个")
        return inspirations
    
    @staticmethod
    def get_by_topic(session: Session, topic_id: int) -> List[Inspiration]:
        """获取主题的所有灵感素材"""
        return session.query(Inspiration).filter(
            Inspiration.topic_id == topic_id
        ).order_by(Inspiration.likes.desc()).all()


class ContentDAO:
    """内容数据访问对象"""
    
    @staticmethod
    def create(session: Session, topic_id: int, raw_title: str, raw_content: str,
               optimized_title: str = None, optimized_content: str = None,
               tags: str = None) -> Content:
        """创建内容"""
        content = Content(
            topic_id=topic_id,
            raw_title=raw_title,
            raw_content=raw_content,
            optimized_title=optimized_title,
            optimized_content=optimized_content,
            tags=tags
        )
        session.add(content)
        session.flush()
        logger.info(f"创建内容: topic_id={topic_id}")
        return content
    
    @staticmethod
    def update_optimized(session: Session, content_id: int, 
                        optimized_title: str, optimized_content: str, tags: str = None):
        """更新优化后的内容"""
        content = session.query(Content).filter(Content.id == content_id).first()
        if content:
            content.optimized_title = optimized_title
            content.optimized_content = optimized_content
            content.tags = tags
            content.updated_at = datetime.now()
            session.flush()
            logger.info(f"更新优化内容: content_id={content_id}")
    
    @staticmethod
    def get_by_id(session: Session, content_id: int) -> Optional[Content]:
        """根据ID获取内容"""
        return session.query(Content).filter(Content.id == content_id).first()
    
    @staticmethod
    def get_by_topic(session: Session, topic_id: int) -> Optional[Content]:
        """根据主题ID获取内容"""
        return session.query(Content).filter(Content.topic_id == topic_id).first()


class PublishRecordDAO:
    """发布记录数据访问对象"""
    
    @staticmethod
    def create(session: Session, content_id: int, xhs_note_id: str = None,
               status: PublishStatus = PublishStatus.PENDING) -> PublishRecord:
        """创建发布记录"""
        record = PublishRecord(
            content_id=content_id,
            xhs_note_id=xhs_note_id,
            status=status,
            publish_time=datetime.now() if status == PublishStatus.SUCCESS else None
        )
        session.add(record)
        session.flush()
        logger.info(f"创建发布记录: content_id={content_id}")
        return record
    
    @staticmethod
    def update_status(session: Session, record_id: int, status: PublishStatus,
                     xhs_note_id: str = None, error_message: str = None):
        """更新发布状态"""
        record = session.query(PublishRecord).filter(PublishRecord.id == record_id).first()
        if record:
            record.status = status
            if xhs_note_id:
                record.xhs_note_id = xhs_note_id
            if error_message:
                record.error_message = error_message
            if status == PublishStatus.SUCCESS:
                record.publish_time = datetime.now()
            elif status == PublishStatus.FAILED:
                record.retry_count += 1
            session.flush()
            logger.info(f"更新发布状态: record_id={record_id}, status={status.value}")
    
    @staticmethod
    def get_by_content(session: Session, content_id: int) -> Optional[PublishRecord]:
        """根据内容ID获取发布记录"""
        return session.query(PublishRecord).filter(
            PublishRecord.content_id == content_id
        ).order_by(PublishRecord.created_at.desc()).first()
