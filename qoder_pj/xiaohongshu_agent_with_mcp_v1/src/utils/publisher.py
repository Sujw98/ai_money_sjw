"""
发布器 - 负责将内容发布到小红书
"""
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class XiaohongshuPublisher:
    """小红书发布器"""
    
    def __init__(self):
        """初始化发布器"""
        self.default_images_path = Path("assets/default_images")
        self.default_images_path.mkdir(parents=True, exist_ok=True)
        logger.info("小红书发布器初始化完成")
    
    def publish_content(
        self,
        title: str,
        content: str,
        tags: list = None,
        images: list = None
    ) -> Dict[str, Any]:
        """
        发布内容到小红书
        
        Args:
            title: 标题
            content: 正文内容
            tags: 话题标签列表
            images: 图片路径列表
            
        Returns:
            Dict: 发布结果，包含success, note_id, error_message等字段
        """
        try:
            logger.info(f"开始发布内容: {title}")
            
            # 准备标签
            if tags is None:
                tags = []
            
            # 准备图片
            if images is None or len(images) == 0:
                # 如果没有提供图片，使用默认图片
                images = self._get_default_images()
            
            # 这里应该调用MCP的publish_content方法
            # 由于MCP在运行时才可用，这里先做占位处理
            # 实际发布逻辑会在workflow中通过MCP工具调用
            
            result = {
                "success": True,
                "note_id": None,  # 实际发布后会有笔记ID
                "title": title,
                "content": content,
                "tags": tags,
                "images": images,
                "error_message": None
            }
            
            logger.info(f"内容发布准备完成: {title}")
            return result
            
        except Exception as e:
            logger.error(f"发布内容失败: {e}")
            return {
                "success": False,
                "note_id": None,
                "error_message": str(e)
            }
    
    def _get_default_images(self) -> list:
        """
        获取默认图片路径
        
        Returns:
            list: 默认图片路径列表
        """
        # 查找默认图片目录中的图片
        default_images = []
        if self.default_images_path.exists():
            for ext in ['*.jpg', '*.jpeg', '*.png']:
                default_images.extend(list(self.default_images_path.glob(ext)))
        
        # 如果有默认图片，随机选择一张
        if default_images:
            # 这里可以优化为随机选择或根据内容选择合适的图片
            return [str(default_images[0].absolute())]
        
        logger.warning("未找到默认图片，发布可能需要手动添加图片")
        return []
    
    def add_default_image(self, image_path: str):
        """
        添加默认图片到默认图片库
        
        Args:
            image_path: 图片路径
        """
        import shutil
        source = Path(image_path)
        if source.exists():
            target = self.default_images_path / source.name
            shutil.copy(source, target)
            logger.info(f"添加默认图片: {source.name}")
        else:
            logger.warning(f"图片文件不存在: {image_path}")


# 全局发布器实例
_publisher: Optional[XiaohongshuPublisher] = None


def get_publisher() -> XiaohongshuPublisher:
    """
    获取发布器实例（单例模式）
    
    Returns:
        XiaohongshuPublisher: 发布器实例
    """
    global _publisher
    if _publisher is None:
        _publisher = XiaohongshuPublisher()
    return _publisher
