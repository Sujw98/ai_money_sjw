"""  
MCP 辅助模块 - 封装小红书MCP调用
注意：直接调用MCP服务，不需要初始化
"""
import logging
import requests
import json
from typing import List, Dict, Any, Optional
from src.utils.config import get_settings

logger = logging.getLogger(__name__)

# MCP 服务配置
MCP_BASE_URL = get_settings().xiaohongshu_mcp_url
# MCP_BASE_URL = "http://115.190.200.210:18060/mcp"
MCP_TIMEOUT = 30  # 超时时间（秒）


def _call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """直接调用MCP工具"""
    try:
        response = requests.post(
            MCP_BASE_URL,
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": hash(tool_name) % 10000
            },
            timeout=MCP_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                logger.error(f"MCP调用错误: {result['error']}")
                return None
            return result
        else:
            logger.error(f"MCP调用失败: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"MCP调用异常: {e}")
        return None


def check_login_status() -> bool:
    """
    检查小红书登录状态
    
    Returns:
        bool: 是否已登录
    """
    try:
        logger.info("调用MCP检查登录状态")
        result = _call_mcp_tool(
            "mcp_xiaohongshu-mcp_check_login_status",
            {"random_string": "check"}
        )
        
        if result:
            logger.info(f"登录状态检查结果: {result}")
            return True
        return False
            
    except Exception as e:
        logger.error(f"检查登录状态失败: {e}")
        return False


def search_feeds(keyword: str, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """
    搜索小红书内容
    
    Args:
        keyword: 搜索关键词
        filters: 筛选条件，如 {"sort_by": "综合", "note_type": "不限"}
        
    Returns:
        List[Dict]: 搜索结果列表
    """
    try:
        if filters is None:
            filters = {}
        
        logger.info(f"调用MCP搜索小红书，关键词: {keyword}")
        
        result = _call_mcp_tool(
            "mcp_xiaohongshu-mcp_search_feeds",
            {"keyword": keyword, "filters": filters}
        )
        
        if result:
            # 解析MCP返回的结果
            content = result.get('result', {}).get('content', [])
            if isinstance(content, list) and len(content) > 0:
                # 尝试解析第一个内容项中的文本
                import json
                try:
                    feeds_data = json.loads(content[0].get('text', '[]'))
                    logger.info(f"搜索成功，获取到 {len(feeds_data)} 条结果")
                    return feeds_data if isinstance(feeds_data, list) else []
                except:
                    return content
        return []
            
    except Exception as e:
        logger.error(f"搜索小红书内容失败: {e}")
        return []


def publish_content(
    title: str,
    content: str,
    images: List[str],
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    发布内容到小红书
    
    Args:
        title: 标题（最多20个中文字）
        content: 正文内容
        images: 图片路径列表（至少1张）
        tags: 话题标签列表
        
    Returns:
        Dict: 发布结果，包含 success, note_id, error_message
    """
    try:
        if not images or len(images) == 0:
            return {
                "success": False,
                "note_id": None,
                "error_message": "至少需要1张图片"
            }
        
        if tags is None:
            tags = []
        
        logger.info(f"调用MCP发布内容: {title}")
        logger.info(f"图片数量: {len(images)}，标签: {', '.join(tags)}")
        
        result = _call_mcp_tool(
            "mcp_xiaohongshu-mcp_publish_content",
            {
                "title": title,
                "content": content,
                "images": images,
                "tags": tags
            }
        )
        
        if result:
            logger.info(f"发布结果: {result}")
            
            # 解析返回结果
            result_data = result.get('result', {})
            content_list = result_data.get('content', [])
            
            # 尝试从返回中提取note_id
            note_id = None
            if content_list and len(content_list) > 0:
                import json
                try:
                    publish_result = json.loads(content_list[0].get('text', '{}'))
                    note_id = publish_result.get('note_id')
                except:
                    pass
            
            return {
                "success": True,
                "note_id": note_id,
                "error_message": None
            }
        else:
            return {
                "success": False,
                "note_id": None,
                "error_message": "MCP调用失败"
            }
            
    except Exception as e:
        logger.error(f"发布内容失败: {e}")
        return {
            "success": False,
            "note_id": None,
            "error_message": str(e)
        }


def get_login_qrcode() -> Optional[str]:
    """
    获取登录二维码
    
    Returns:
        str: Base64编码的二维码图片，或None
    """
    try:
        logger.info("调用MCP获取登录二维码")
        
        result = _call_mcp_tool(
            "mcp_xiaohongshu-mcp_get_login_qrcode",
            {"random_string": "qrcode"}
        )
        
        if result:
            logger.info("二维码获取成功")
            
            # 解析返回结果
            content = result.get('result', {}).get('content', [])
            if content and len(content) > 0:
                import json
                try:
                    qr_data = json.loads(content[0].get('text', '{}'))
                    return qr_data.get('qrcode_base64')
                except:
                    return content[0].get('text')
        return None
            
    except Exception as e:
        logger.error(f"获取登录二维码失败: {e}")
        return None
