#!/usr/bin/env python3
"""
雪球观点抓取器
- 抓取大V用户对行业板块的点评
- 提取观点、情绪、逻辑
"""

import requests
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# 雪球API配置
XUEQIU_API = "https://xueqiu.com/query/v1/symbol/search/status"
XUEQIU_USER_API = "https://xueqiu.com/query/v1/status/user_timeline"

# 需要配置Cookie（从浏览器登录后获取）
# 格式：xq_a_token=xxx; xq_r_token=xxx
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://xueqiu.com/',
    'X-Requested-With': 'XMLHttpRequest',
}

# 行业关键词映射
INDUSTRY_KEYWORDS = {
    '消费': ['消费', '白酒', '茅台', '中免', '伊利', '食品饮料', '零售'],
    '人形机器人': ['机器人', '特斯拉', 'optimus', '埃斯顿', '汇川', '减速器', '电机'],
    '光模块': ['光模块', 'CPO', '中际旭创', '天孚通信', '新易盛', '800G', '1.6T'],
    '算力': ['算力', '服务器', '中科曙光', '浪潮', '寒武纪', 'AI芯片'],
    '低空经济': ['低空经济', '飞行汽车', '无人机', '万丰奥威', '中信海直'],
    '量子科技': ['量子', '国盾量子', '量子计算', '量子通信'],
    '脑机接口': ['脑机接口', '脑科学', 'Neuralink', '三博脑科'],
    'AI应用': ['AI应用', '大模型', 'ChatGPT', '文心一言', '通义千问'],
    'AI医疗': ['AI医疗', '智慧医疗', '医疗AI', '润达医疗'],
    '6G': ['6G', '通信', '中兴通讯', '烽火通信'],
    '卫星互联网': ['卫星', '星链', '中国卫通', '北斗', '商业航天'],
    '可控核聚变': ['核聚变', '核电', '人造太阳', 'iter'],
    '集成电路': ['芯片', '半导体', '中芯国际', '北方华创', '国产替代'],
    '生物医药': ['医药', '创新药', '恒瑞医药', '药明康德', 'CXO'],
    '航空航天': ['航天', '航空', '中航沈飞', '航发动力', '军工'],
}

# 默认关注的大V列表（用户可配置）
DEFAULT_FOLLOWING = [
    # 需要用户配置雪球用户ID
    # 格式：{"name": "投资老曹", "id": "12345678"},
]

class XueqiuOpinionFetcher:
    """雪球观点抓取器"""
    
    def __init__(self, cookie=None):
        self.headers = DEFAULT_HEADERS.copy()
        if cookie:
            self.headers['Cookie'] = cookie
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_user_timeline(self, user_id, count=10):
        """抓取用户最新发帖"""
        url = f"https://xueqiu.com/statuses/original/timeline.json"
        params = {
            'user_id': user_id,
            'page': 1,
            'count': count
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('statuses', [])
            else:
                print(f"  ⚠️  获取用户{user_id}时间线失败: {resp.status_code}")
                return []
        except Exception as e:
            print(f"  ⚠️  请求异常: {e}")
            return []
    
    def fetch_stock_discussion(self, symbol, count=20):
        """抓取股票讨论区帖子"""
        url = XUEQIU_API
        params = {
            'symbol': symbol,
            'page': 1,
            'size': count
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('list', [])
            else:
                print(f"  ⚠️  获取{symbol}讨论失败: {resp.status_code}")
                return []
        except Exception as e:
            print(f"  ⚠️  请求异常: {e}")
            return []
    
    def extract_opinions(self, posts, industry_keywords):
        """从帖子中提取观点"""
        opinions = []
        
        for post in posts:
            text = post.get('text', '')
            # 去除HTML标签
            text = re.sub(r'<[^>]+>', '', text)
            
            # 检查是否包含行业关键词
            if any(kw in text for kw in industry_keywords):
                user = post.get('user', {})
                opinion = {
                    'source': '雪球',
                    'author': user.get('screen_name', '匿名'),
                    'user_id': user.get('id'),
                    'text': text[:200] + '...' if len(text) > 200 else text,
                    'time': post.get('created_at'),
                    'like_count': post.get('like_count', 0),
                    'comment_count': post.get('comment_count', 0),
                }
                
                # 简单情绪判断
                if any(w in text for w in ['看好', '买入', '机会', '上涨', '利好']):
                    opinion['sentiment'] = '看涨'
                elif any(w in text for w in ['看空', '卖出', '风险', '下跌', '利空']):
                    opinion['sentiment'] = '看跌'
                else:
                    opinion['sentiment'] = '中性'
                
                opinions.append(opinion)
        
        # 按点赞数排序，取前5条
        opinions.sort(key=lambda x: x['like_count'], reverse=True)
        return opinions[:5]
    
    def fetch_industry_opinions(self, industry, following_list=None):
        """抓取行业相关观点"""
        keywords = INDUSTRY_KEYWORDS.get(industry, [industry])
        all_opinions = []
        
        print(f"\n🔍 抓取[{industry}]相关观点...")
        print(f"  关键词: {', '.join(keywords[:3])}...")
        
        # 1. 从关注的大V抓取
        following = following_list or DEFAULT_FOLLOWING
        for user in following:
            print(f"  → 抓取 {user['name']} 的帖子...")
            posts = self.fetch_user_timeline(user['id'], count=10)
            opinions = self.extract_opinions(posts, keywords)
            for op in opinions:
                op['author_type'] = '关注大V'
            all_opinions.extend(opinions)
        
        # 2. 从龙头股讨论区抓取
        # 这里需要映射行业到龙头股代码
        print(f"  → 从讨论区抓取...")
        # 简化为直接搜索帖子
        
        print(f"  ✅ 共收集 {len(all_opinions)} 条观点")
        return all_opinions


def main():
    """测试抓取"""
    # 需要用户提供Cookie
    cookie = None  # 从浏览器获取
    
    fetcher = XueqiuOpinionFetcher(cookie=cookie)
    
    # 抓取消费板块观点
    opinions = fetcher.fetch_industry_opinions('消费')
    
    print("\n" + "="*60)
    print("📊 抓取结果")
    print("="*60)
    for i, op in enumerate(opinions[:5], 1):
        print(f"\n{i}. [{op['sentiment']}] {op['author']} ({op['source']})")
        print(f"   {op['text'][:100]}...")
        print(f"   👍 {op['like_count']}  💬 {op['comment_count']}")


if __name__ == '__main__':
    main()
