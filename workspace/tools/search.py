#!/usr/bin/env python3
"""
SearXNG 本地搜索工具
使用方法: python3 search.py "搜索关键词" [选项]
"""

import requests
import json
import sys
from typing import List, Dict

# 配置
SEARXNG_URL = "http://192.168.50.251:10011"
DEFAULT_ENGINES = "duckduckgo,bing"
DEFAULT_LANGUAGE = "auto"

def search(query: str, engines: str = DEFAULT_ENGINES,
           language: str = DEFAULT_LANGUAGE,
           time_range: str = "", limit: int = 10) -> List[Dict]:
    """
    使用 SearXNG 搜索

    Args:
        query: 搜索关键词
        engines: 搜索引擎（逗号分隔）
        language: 语言（auto/zh/en）
        time_range: 时间范围（day/week/month/year）
        limit: 返回结果数量

    Returns:
        搜索结果列表
    """
    params = {
        'q': query,
        'format': 'json',
        'engines': engines
    }

    if language != "auto":
        params['language'] = language

    if time_range:
        params['time_range'] = time_range

    try:
        response = requests.get(
            f"{SEARXNG_URL}/search",
            params=params,
            timeout=15
        )
        response.raise_for_status()

        data = response.json()
        results = data.get('results', [])

        return results[:limit]

    except requests.exceptions.Timeout:
        print("❌ 搜索超时")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ 搜索失败: {e}")
        return []
    except json.JSONDecodeError:
        print("❌ 响应解析失败")
        return []

def format_results(results: List[Dict], format_type: str = "text") -> str:
    """格式化搜索结果"""

    if not results:
        return "没有找到结果"

    if format_type == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)

    output = []
    for i, r in enumerate(results, 1):
        output.append(f"\n{i}. {r.get('title', 'N/A')}")
        output.append(f"   URL: {r.get('url', 'N/A')}")
        snippet = r.get('content', '')
        if snippet:
            output.append(f"   摘要: {snippet[:150]}...")
        output.append(f"   来源: {r.get('engine', 'N/A')}")

    return "\n".join(output)

def main():
    """命令行入口"""

    # 解析参数
    if len(sys.argv) < 2:
        print("使用方法: python3 search.py \"搜索关键词\" [选项]")
        print("\n选项:")
        print("  --engines=duckduckgo,bing  指定搜索引擎")
        print("  --lang=zh                  指定语言")
        print("  --time=week                时间范围（day/week/month/year）")
        print("  --limit=10                 结果数量")
        print("  --json                     JSON 格式输出")
        print("\n示例:")
        print("  python3 search.py 量化交易")
        print("  python3 search.py python --lang=en --limit=5")
        print("  python3 search.py bitcoin --time=week --json")
        sys.exit(1)

    # 解析查询和选项
    query = sys.argv[1]
    engines = DEFAULT_ENGINES
    language = DEFAULT_LANGUAGE
    time_range = ""
    limit = 10
    format_type = "text"

    for arg in sys.argv[2:]:
        if arg.startswith("--engines="):
            engines = arg.split("=", 1)[1]
        elif arg.startswith("--lang="):
            language = arg.split("=", 1)[1]
        elif arg.startswith("--time="):
            time_range = arg.split("=", 1)[1]
        elif arg.startswith("--limit="):
            limit = int(arg.split("=", 1)[1])
        elif arg == "--json":
            format_type = "json"

    # 执行搜索
    print(f"🔍 搜索: {query}")
    print(f"   引擎: {engines}")
    print(f"   语言: {language}")
    if time_range:
        print(f"   时间: {time_range}")
    print()

    results = search(query, engines, language, time_range, limit)

    # 输出结果
    print(format_results(results, format_type))
    print(f"\n✅ 共找到 {len(results)} 条结果")

if __name__ == "__main__":
    main()
