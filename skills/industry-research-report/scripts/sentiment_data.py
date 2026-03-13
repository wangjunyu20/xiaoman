#!/usr/bin/env python3
"""
舆情数据获取脚本（东方财富股吧）

从东方财富股吧获取热门帖子和评论
"""

import sys
import json
import subprocess
from datetime import datetime

def fetch_url(url):
    """获取网页内容"""
    cmd = [
        'curl', '-s',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def get_guba_posts(stock_code, limit=10):
    """获取股吧热门帖子"""
    # A股用 list, 港股用 list,hk
    if stock_code.startswith(('0', '3', '6')):
        url = f"https://guba.eastmoney.com/list,{stock_code}.html"
    else:
        url = f"https://guba.eastmoney.com/list,hk{stock_code}.html"
    
    try:
        # 使用 extract_content_from_websites 工具
        from extract_content_from_websites import extract_content_from_websites
        
        result = extract_content_from_websites([{
            "url": url,
            "prompt": f"提取{stock_code}股吧热门帖子标题、评论数、阅读数，按热度排序取前{limit}条"
        }])
        
        # 解析结果
        content = result[0]["result"]
        return {
            "stock_code": stock_code,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "东方财富股吧",
            "posts": content[:2000]  # 限制长度
        }
    except Exception as e:
        return {"error": str(e)}

def get_industry_sentiment(industry_name):
    """获取行业舆情（通过行业指数代码）"""
    # 行业板块映射
    industry_map = {
        "人形机器人": "885863",  # 机器人概念
        "量子科技": "885626",    # 量子技术
        "AI应用": "885901",      # 人工智能
        "可控核聚变": "885814",  # 核能
        "光模块": "873991",      # 光通信
    }
    
    code = industry_map.get(industry_name, "")
    if not code:
        return {"error": f"未知行业: {industry_name}"}
    
    url = f"https://guba.eastmoney.com/list,{code}.html"
    
    try:
        from extract_content_from_websites import extract_content_from_websites
        
        result = extract_content_from_websites([{
            "url": url,
            "prompt": f"提取{industry_name}板块热门帖子标题和评论数"
        }])
        
        return {
            "industry": industry_name,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "posts": result[0]["result"][:2000]
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python sentiment_data.py guba <股票代码>    # 股吧帖子")
        print("  python sentiment_data.py industry <行业名>   # 行业舆情")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "guba":
        stock_code = sys.argv[2] if len(sys.argv) > 2 else "600519"
        result = get_guba_posts(stock_code)
    elif command == "industry":
        industry = sys.argv[2] if len(sys.argv) > 2 else "AI应用"
        result = get_industry_sentiment(industry)
    else:
        result = {"error": f"未知命令: {command}"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
