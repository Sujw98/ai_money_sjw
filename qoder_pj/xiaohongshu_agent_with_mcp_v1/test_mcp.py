"""
测试 MCP 服务连接
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.utils.mcp_helper import check_login_status, search_feeds, get_login_qrcode

logger = setup_logger("test_mcp", "INFO")


def test_mcp_connection():
    """测试MCP服务连接"""
    print("=" * 60)
    print("测试 MCP 服务连接")
    print("=" * 60)
    
    # 1. 测试登录状态检查
    print("\n1. 测试登录状态检查...")
    is_logged_in = check_login_status()
    print(f"   登录状态: {'已登录' if is_logged_in else '未登录'}")
    
    # 2. 测试搜索功能
    print("\n2. 测试搜索功能...")
    results = search_feeds("理财", {"sort_by": "综合"})
    print(f"   搜索到 {len(results)} 条结果")
    if results:
        print(f"   第一条结果: {results[0] if len(results) > 0 else 'N/A'}")
    
    # 3. 测试获取登录二维码
    print("\n3. 测试获取登录二维码...")
    qrcode = get_login_qrcode()
    print(f"   二维码获取: {'成功' if qrcode else '失败'}")
    
    print("\n" + "=" * 60)
    print("MCP 服务测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_mcp_connection()
