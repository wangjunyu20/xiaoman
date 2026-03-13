#!/usr/bin/env python3
"""
财联社新闻抓取模块

功能：
- 抓取财联社电报实时新闻
- 按关键词筛选行业相关新闻
- 返回结构化新闻数据（含标题、链接、时间、摘要）

使用免签名API:
https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&os=web&sv=8.4.6&rn=50
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# 默认缓存配置
DEFAULT_CACHE_DIR = Path("./news_cache")
DEFAULT_CACHE_TTL = 1800  # 30分钟

# 行业关键词映射
INDUSTRY_KEYWORDS = {
    "光模块": ["光模块", "CPO", "光通信", "中际旭创", "天孚通信", "新易盛"],
    "人形机器人": ["人形机器人", "机器人", "具身智能", "优必选", "特斯拉机器人"],
    "量子科技": ["量子科技", "量子计算", "量子通信", "国盾量子"],
    "AI应用": ["AI应用", "人工智能", "大模型", "AIGC", "ChatGPT"],
    "脑机接口": ["脑机接口", "Neuralink", "脑科学"],
    "可控核聚变": ["核聚变", "人造太阳", "ITER", "托卡马克"],
    "AI+医疗": ["AI医疗", "智慧医疗", "医疗AI"],
    "消费": ["消费", "零售", "茅台", "中国中免"],
    "集成电路": ["集成电路", "半导体", "芯片", "中芯国际"],
    "低空经济": ["低空经济", "无人机", "飞行汽车", "eVTOL"],
    "算力": ["算力", "智算", "数据中心", "服务器"],
}


class CailiansheNewsFetcher:
    """财联社新闻抓取器"""
    
    def __init__(self, cache_dir: Optional[Path] = None, cache_ttl: int = DEFAULT_CACHE_TTL):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.cls.cn/',
        })
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_ttl = cache_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache(self, key: str) -> Optional[List[Dict]]:
        """获取缓存数据"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if time.time() - data.get('timestamp', 0) < self.cache_ttl:
                        return data.get('news', [])
            except:
                pass
        return None
    
    def _set_cache(self, key: str, news: List[Dict]):
        """设置缓存数据"""
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': time.time(),
                'news': news
            }, f, ensure_ascii=False, indent=2)
    
    def fetch_telegraph(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        抓取财联社电报，并按关键词筛选
        
        Args:
            keyword: 搜索关键词
            limit: 返回新闻数量上限
            
        Returns:
            List[Dict]: 新闻列表，每条包含title, url, publish_time, summary, impact
        """
        cache_key = f"cls_telegraph_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        try:
            url = "https://www.cls.cn/nodeapi/telegraphList"
            params = {
                'app': 'CailianpressWeb',
                'os': 'web',
                'sv': '8.4.6',
                'rn': '50',
                'last_time': '0'
            }
            
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                telegraph_data = data.get('data', {}).get('roll_data', [])
                
                # 关键词匹配
                keywords_to_match = [keyword] + INDUSTRY_KEYWORDS.get(keyword, [keyword])
                
                for item in telegraph_data:
                    content = item.get('content', '')
                    brief = item.get('brief', '')
                    
                    # 检查是否包含关键词
                    all_text = content + brief
                    if any(kw in all_text for kw in keywords_to_match):
                        news_list.append({
                            'source': '财联社',
                            'title': brief or (content[:80] + '...' if len(content) > 80 else content),
                            'url': f"https://www.cls.cn/telegraph/{item.get('id', '')}",
                            'publish_time': datetime.fromtimestamp(item.get('ctime', 0)).strftime('%Y-%m-%d %H:%M'),
                            'summary': content[:100] + '...' if len(content) > 100 else content,
                            'impact': self._analyze_impact(content)
                        })
                        
                        if len(news_list) >= limit:
                            break
        except Exception as e:
            print(f"财联社抓取失败: {e}")
        
        time.sleep(0.3)
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    def _analyze_impact(self, text: str) -> str:
        """分析新闻对股价的影响倾向"""
        text = text.lower()
        positive_words = ['利好', '增长', '突破', '上涨', '涨停', '创新', '签约', '合作', '中标', '订单', '超预期', '爆款', '领先', '大增', '新高']
        negative_words = ['利空', '下跌', '跌停', '亏损', '减持', '处罚', '违规', '召回', '下架', '下滑', '不及预期', '风险', '警示', '大跌', '爆雷']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            return '利好'
        elif neg_count > pos_count:
            return '利空'
        return '中性'


def fetch_cailianshe_news(keyword: str, limit: int = 5) -> List[Dict]:
    """
    便捷函数：抓取财联社新闻
    
    Args:
        keyword: 搜索关键词
        limit: 返回新闻数量上限
        
    Returns:
        List[Dict]: 新闻列表
        
    Example:
        >>> news = fetch_cailianshe_news("光模块", 3)
        >>> for item in news:
        ...     print(f"{item['title']} - {item['url']}")
    """
    fetcher = CailiansheNewsFetcher()
    return fetcher.fetch_telegraph(keyword, limit)


if __name__ == "__main__":
    # 测试
    import sys
    
    keyword = sys.argv[1] if len(sys.argv) > 1 else "光模块"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    print(f"抓取财联社新闻: 关键词={keyword}, 数量={limit}")
    print("-" * 60)
    
    news = fetch_cailianshe_news(keyword, limit)
    
    for i, item in enumerate(news, 1):
        print(f"\n{i}. {item['title']}")
        print(f"   来源: {item['source']}")
        print(f"   时间: {item['publish_time']}")
        print(f"   影响: {item['impact']}")
        print(f"   链接: {item['url']}")
        print(f"   摘要: {item['summary']}")
