#!/usr/bin/env python3
"""
雪球数据获取脚本

⚠️ 注意：xueqiu.com 主站 API 需 Playwright，IP 已被封
✅ stock.xueqiu.com 子域名可直接调用

可用功能：
- stock_quote: 股票行情（stock.xueqiu.com）
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def get_token():
    """获取雪球 token"""
    token = os.environ.get('XQ_A_TOKEN', '')
    if not token:
        print("错误: 请设置 XQ_A_TOKEN 环境变量")
        print("export XQ_A_TOKEN='your_token'")
        sys.exit(1)
    return token

def curl_cmd(url, token):
    """执行 curl 命令"""
    cmd = [
        'curl', '-s',
        '-b', f'xq_a_token={token}',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        '-H', 'Referer: https://xueqiu.com/',
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def get_stock_quote(symbol):
    """获取股票行情（可用）"""
    token = get_token()
    url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"
    
    try:
        resp = curl_cmd(url, token)
        data = json.loads(resp)
        
        if data.get('error_code') != 0:
            return {"error": data.get('error_description', 'Unknown error')}
        
        quote = data.get('data', {}).get('quote', {})
        return {
            "symbol": symbol,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": quote.get('name'),
            "current": quote.get('current'),
            "percent": quote.get('percent'),
            "chg": quote.get('chg'),
            "open": quote.get('open'),
            "high": quote.get('high'),
            "low": quote.get('low'),
            "prev_close": quote.get('last_close'),
            "volume": quote.get('volume'),
            "amount": quote.get('amount'),
            "pe_ttm": quote.get('pe_ttm'),
            "pb": quote.get('pb'),
            "market_capital": quote.get('market_capital'),
            "dividend_yield": quote.get('dividend_yield'),
            "exchange": quote.get('exchange')
        }
    except Exception as e:
        return {"error": str(e)}

def get_multiple_quotes(symbols):
    """批量获取股票行情"""
    results = []
    for symbol in symbols:
        result = get_stock_quote(symbol)
        results.append(result)
    return results

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python snowtrace_data.py quote <代码>        # 股票行情")
        print("  python snowtrace_data.py quotes <代码1> <代码2> ...  # 批量行情")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "quote":
        symbol = sys.argv[2] if len(sys.argv) > 2 else "SH600519"
        result = get_stock_quote(symbol)
    elif command == "quotes":
        symbols = sys.argv[2:] if len(sys.argv) > 2 else ["SH600519", "SH000001"]
        result = get_multiple_quotes(symbols)
    else:
        result = {"error": f"Unknown command: {command}"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
