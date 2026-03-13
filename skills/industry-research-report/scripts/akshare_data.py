#!/usr/bin/env python3
"""
AKShare 数据获取脚本

用于获取A股行情、板块数据等
通过设置正确的请求头来绕过访问限制
"""

import sys
import json
import requests
from datetime import datetime

# 设置全局默认 headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.sina.com.cn",
    "Accept": "*/*",
}

session = requests.Session()
session.headers.update(HEADERS)

def parse_sina_data(content, is_index=False):
    """解析新浪返回的数据"""
    try:
        # 去掉 var hq_str_xxx=" 和 ";
        data = content.split('="')[1]
        data = data.replace('";', '').replace('"', '')
        data = data.strip()
        fields = [f.strip() for f in data.split(',') if f.strip()]
        return fields
    except:
        return []

def get_stock_realtime(symbol="600519"):
    """获取个股实时行情（新浪接口）"""
    try:
        # 转换股票代码
        if symbol.startswith("6"):
            code = f"sh{symbol}"
        elif symbol.startswith(("0", "3")):
            code = f"sz{symbol}"
        else:
            code = f"sh{symbol}"
        
        url = f"https://hq.sinajs.cn/list={code}"
        resp = session.get(url, timeout=10)
        
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}
        
        content = resp.content.decode('gbk', errors='ignore')
        if "var hq_str" not in content:
            return {"error": "No data"}
        
        fields = parse_sina_data(content)
        
        # 新浪股票实时行情字段:
        # 0:名称, 1:开盘, 2:当前, 3:买一价, 4:卖一价, 5:买一量, 6:卖一量,
        # 7:昨收, 8:成交量, 9:成交额, ...
        if len(fields) >= 10:
            close = float(fields[2])
            prev_close = float(fields[7])
            change = close - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0
            
            return {
                "symbol": symbol,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": fields[0],
                "open": float(fields[1]),
                "close": close,
                "prev_close": prev_close,
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "volume": float(fields[8]),
                "amount": float(fields[9]),
                "bid1": float(fields[3]),
                "ask1": float(fields[4])
            }
        return {"raw": fields}
        
    except Exception as e:
        return {"error": str(e)}

def get_index_realtime(index_code="000001"):
    """获取指数行情"""
    try:
        if index_code == "000001":
            code = "s_sh000001"  # 上证指数
        elif index_code == "399001":
            code = "s_sz399001"  # 深证成指
        elif index_code == "399006":
            code = "s_sz399006"  # 创业板指
        else:
            code = f"s_sh{index_code}"
        
        url = f"https://hq.sinajs.cn/list={code}"
        resp = session.get(url, timeout=10)
        
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}
        
        content = resp.content.decode('gbk', errors='ignore')
        if "var hq_str" not in content:
            return {"error": "No data"}
        
        fields = parse_sina_data(content)
        
        # 新浪指数接口字段: 名称,当前,涨跌,涨跌%,成交量,成交额
        if len(fields) >= 5:
            return {
                "index_code": index_code,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": fields[0],
                "close": float(fields[1]),
                "change": float(fields[2]),
                "change_pct": float(fields[3]),
                "volume": float(fields[4]),
                "amount": float(fields[5]) if len(fields) > 5 else 0
            }
        return {"raw": fields}
        
    except Exception as e:
        return {"error": str(e)}

def get_multiple_stocks(symbols):
    """批量获取股票行情"""
    results = []
    for symbol in symbols:
        result = get_stock_realtime(symbol)
        results.append(result)
    return results

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python akshare_data.py stock <代码>   # 个股行情")
        print("  python akshare_data.py index <代码>  # 指数行情")
        print("  python akshare_data.py stocks <代码1> <代码2> ...  # 批量获取")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "stock":
        symbol = sys.argv[2] if len(sys.argv) > 2 else "600519"
        result = get_stock_realtime(symbol)
    elif command == "index":
        index_code = sys.argv[2] if len(sys.argv) > 2 else "000001"
        result = get_index_realtime(index_code)
    elif command == "stocks":
        symbols = sys.argv[2:] if len(sys.argv) > 2 else ["600519", "000001"]
        result = get_multiple_stocks(symbols)
    else:
        result = {"error": f"Unknown command: {command}"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
