"""
调试 MCP 服务返回结果
"""
import sys
from pathlib import Path
import requests
import json

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

MCP_BASE_URL = "http://115.190.200.210:18060/mcp"


def debug_search():
    """调试搜索功能"""
    session = requests.Session()
    
    # 第1步：初始化
    print("=== 第1步：初始化 ===")
    response = session.post(
        MCP_BASE_URL,
        json={
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 0
        },
        timeout=30
    )
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 第2步：发送initialized通知 (不带id)
    print("\n=== 第2步：发送initialized通知 ===")
    response = session.post(
        MCP_BASE_URL,
        json={
            "jsonrpc": "2.0",
            "method": "initialized"
        },
        timeout=30
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 第3步：调用工具
    print("\n=== 第3步：调用搜索工具 ===")
    response = session.post(
        MCP_BASE_URL,
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "mcp_xiaohongshu-mcp_search_feeds",
                "arguments": {
                    "keyword": "理财",
                    "filters": {"sort_by": "综合"}
                }
            },
            "id": 1
        },
        timeout=30
    )
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    debug_search()
