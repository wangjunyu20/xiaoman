#!/usr/bin/env python3
"""
多源财经新闻抓取模块（实用版）

使用策略：
1. AKShare stock_news_em - 获取最新财经新闻（全市场），然后按关键词筛选
2. 使用百度/新浪财经的行业资讯页面
3. 东方财富股吧热帖

支持行业：光模块、人形机器人、量子科技、AI应用、可控核聚变、脑机接口、AI+医疗
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

# 缓存配置
CACHE_DIR = Path("/root/.openclaw/workspace_investment/output/news_cache")
CACHE_TTL = 1800  # 缓存30分钟

# 行业关键词映射
INDUSTRY_KEYWORDS = {
    "光模块": ["光模块", "CPO", "光通信", "中际旭创", "天孚通信", "新易盛", "光迅科技", "剑桥科技"],
    "人形机器人": ["人形机器人", "机器人", "优必选", "特斯拉机器人", "埃斯顿", "中大力德", "减速器", "伺服电机"],
    "量子科技": ["量子科技", "量子计算", "量子通信", "国盾量子", "四创电子", "本源量子", "祖冲之号"],
    "AI应用": ["AI应用", "人工智能", "大模型", "AIGC", "科大讯飞", "广联达", "ChatGPT", "文心一言"],
    "可控核聚变": ["核聚变", "人造太阳", "ITER", "东方电气", "中国核建", "托卡马克", "等离子体"],
    "脑机接口": ["脑机接口", "Neuralink", "三博脑科", "国际医学", "脑科学", "神经接口"],
    "AI+医疗": ["AI医疗", "智慧医疗", "医疗AI", "卫宁健康", "爱尔眼科", "医疗信息化", "智能诊断"]
}

# 东财板块代码映射
EASTMONEY_BOARD_CODES = {
    "光模块": "873991",
    "人形机器人": "885863",
    "量子科技": "885626",
    "AI应用": "885901",
    "可控核聚变": "885814",
    "脑机接口": "885757",
    "AI+医疗": "887791"
}

class NewsFetcher:
    """新闻抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # 尝试导入akshare
        self.has_akshare = False
        try:
            import akshare as ak
            self.ak = ak
            self.has_akshare = True
            print("✅ AKShare 已加载")
        except ImportError:
            print("⚠️ AKShare 未安装")
    
    def _get_cache(self, key: str) -> Optional[List[Dict]]:
        """获取缓存数据"""
        cache_file = CACHE_DIR / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if time.time() - data.get('timestamp', 0) < CACHE_TTL:
                        return data.get('news', [])
            except:
                pass
        return None
    
    def _set_cache(self, key: str, news: List[Dict]):
        """设置缓存数据"""
        cache_file = CACHE_DIR / f"{key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': time.time(),
                'news': news
            }, f, ensure_ascii=False, indent=2)
    
    def fetch_em_news_baidu(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        通过百度搜索获取东方财富相关新闻
        使用百度site搜索
        """
        cache_key = f"baidu_em_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        try:
            # 使用百度搜索site:eastmoney.com
            url = "https://www.baidu.com/s"
            params = {
                'wd': f'{keyword} site:eastmoney.com',
                'rn': limit * 2
            }
            
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                # 解析搜索结果
                # 提取标题和链接
                pattern = r'<a[^>]*href="([^"]*eastmoney\.com[^"]*)"[^>]*>([^<]+)</a>'
                matches = re.findall(pattern, resp.text, re.IGNORECASE)
                
                for url, title in matches[:limit]:
                    # 清理HTML标签和空白
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    if title and len(title) > 10:
                        news_list.append({
                            'source': '东方财富',
                            'title': title,
                            'url': url,
                            'publish_time': datetime.now().strftime('%Y-%m-%d'),
                            'summary': '',
                            'impact': self._analyze_impact(title)
                        })
        except Exception as e:
            print(f"  百度-东财搜索失败: {e}")
        
        time.sleep(0.5)
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    def fetch_sina_finance_search(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        新浪财经搜索
        """
        cache_key = f"sina_search_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        try:
            # 新浪财经搜索
            url = "https://search.sina.com.cn/"
            params = {
                'q': keyword,
                'c': 'news',
                'from': 'channel',
                'ie': 'utf-8'
            }
            
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                # 提取新闻标题和链接
                pattern = r'<h2><a[^>]*href="([^"]*)"[^>]*>(.*?)</a></h2>'
                matches = re.findall(pattern, resp.text, re.DOTALL)
                
                for url, title in matches[:limit]:
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    if title:
                        news_list.append({
                            'source': '新浪财经',
                            'title': title,
                            'url': url if url.startswith('http') else f"https:{url}",
                            'publish_time': datetime.now().strftime('%Y-%m-%d'),
                            'summary': '',
                            'impact': self._analyze_impact(title)
                        })
        except Exception as e:
            print(f"  新浪财经搜索失败: {e}")
        
        time.sleep(0.3)
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    def fetch_eastmoney_guba(self, board_name: str, limit: int = 5) -> List[Dict]:
        """
        抓取东方财富股吧热帖
        """
        cache_key = f"guba_{board_name}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        try:
            board_code = EASTMONEY_BOARD_CODES.get(board_name, '')
            if not board_code:
                return news_list
            
            # 东财股吧API - 获取热帖
            url = "https://guba.eastmoney.com/api/taobaoliststoken"
            params = {
                'type': '1',
                'code': board_code,
                'page': '1',
                'pageSize': str(limit * 2)
            }
            
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('re', []):
                    title = item.get('post_title', '')
                    if title:
                        news_list.append({
                            'source': '东财股吧',
                            'title': title,
                            'url': f"https://guba.eastmoney.com{item.get('post_url', '')}",
                            'publish_time': item.get('post_publish_time', ''),
                            'summary': item.get('post_content', '')[:50] + '...' if len(item.get('post_content', '')) > 50 else item.get('post_content', ''),
                            'impact': self._analyze_impact(title)
                        })
        except Exception as e:
            print(f"  东财股吧抓取失败: {e}")
        
        time.sleep(0.3)
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    def fetch_akshare_news(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        使用AKShare获取东方财富财经新闻，然后筛选
        """
        if not self.has_akshare:
            return []
        
        cache_key = f"akshare_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        try:
            df = self.ak.stock_news_em()
            keywords_to_match = [keyword] + INDUSTRY_KEYWORDS.get(keyword, [keyword])
            
            for _, row in df.head(50).iterrows():
                title = str(row.get('新闻标题', ''))
                content = str(row.get('新闻内容', ''))
                news_keyword = str(row.get('关键词', ''))
                
                # 检查是否包含关键词
                all_text = title + content + news_keyword
                if any(kw in all_text for kw in keywords_to_match):
                    news_list.append({
                        'source': str(row.get('文章来源', '东方财富')),
                        'title': title,
                        'url': str(row.get('新闻链接', '')),
                        'publish_time': str(row.get('发布时间', ''))[:16],
                        'summary': content[:50] + '...' if len(content) > 50 else content,
                        'impact': self._analyze_impact(title + content)
                    })
                    
                    if len(news_list) >= limit:
                        break
        except Exception as e:
            print(f"  AKShare新闻获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    def _analyze_impact(self, text: str) -> str:
        """
        分析新闻对股价的影响倾向
        """
        text = text.lower()
        positive_words = ['利好', '增长', '突破', '上涨', '涨停', '创新', '签约', '合作', '中标', '订单', '增长', '超预期', '爆款', '领先', '大增', '新高']
        negative_words = ['利空', '下跌', '跌停', '亏损', '减持', '处罚', '违规', '召回', '下架', '下滑', '不及预期', '风险', '警示', '大跌', '爆雷']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            return '利好'
        elif neg_count > pos_count:
            return '利空'
        return '中性'
    
    def fetch_cailianshe_telegraph(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        抓取财联社电报，并按关键词筛选
        使用免签名API: /nodeapi/telegraphList
        """
        cache_key = f"cailianshe_telegraph_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        try:
            # 财联社电报API（无需签名）
            url = "https://www.cls.cn/nodeapi/telegraphList"
            params = {
                'app': 'CailianpressWeb',
                'os': 'web',
                'sv': '8.4.6',
                'rn': '50',  # 获取50条
                'last_time': '0'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.cls.cn/',
            }
            
            resp = self.session.get(url, params=params, headers=headers, timeout=10)
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
                            'title': brief or content[:80] + '...' if len(content) > 80 else content,
                            'url': f"https://www.cls.cn/telegraph/{item.get('id', '')}",
                            'publish_time': datetime.fromtimestamp(item.get('ctime', 0)).strftime('%Y-%m-%d %H:%M'),
                            'summary': content[:100] + '...' if len(content) > 100 else content,
                            'impact': self._analyze_impact(content)
                        })
                        
                        if len(news_list) >= limit:
                            break
        except Exception as e:
            print(f"  财联社电报抓取失败: {e}")
        
        time.sleep(0.3)
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    def fetch_cailianshe_news(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        抓取财联社新闻（优先使用电报API）
        """
        return self.fetch_cailianshe_telegraph(keyword, limit)
    
    def fetch_industry_news(self, industry: str, limit_per_source: int = 3) -> Dict[str, List[Dict]]:
        """
        获取某个行业的多源新闻
        
        Args:
            industry: 行业名称
            limit_per_source: 每个来源获取的新闻数量
        
        Returns:
            Dict: {'source_name': [news_list]}
        """
        keywords = INDUSTRY_KEYWORDS.get(industry, [industry])
        primary_keyword = keywords[0] if keywords else industry
        
        print(f"\n🔄 正在获取 [{industry}] 行业新闻...")
        
        news_by_source = {}
        
        # 1. AKShare 东财新闻
        print(f"  → 东财新闻(AKShare)...")
        ak_news = self.fetch_akshare_news(primary_keyword, limit_per_source)
        if ak_news:
            news_by_source['东方财富'] = ak_news
        
        # 2. 东财股吧
        print(f"  → 东财股吧...")
        guba_news = self.fetch_eastmoney_guba(industry, limit_per_source)
        if guba_news:
            news_by_source['东财股吧'] = guba_news
        
        # 3. 新浪财经
        print(f"  → 新浪财经...")
        sina_news = self.fetch_sina_finance_search(primary_keyword, limit_per_source)
        if sina_news:
            news_by_source['新浪财经'] = sina_news
        
        # 4. 财联社电报
        print(f"  → 财联社...")
        cls_news = self.fetch_cailianshe_telegraph(primary_keyword, limit_per_source)
        if cls_news:
            news_by_source['财联社'] = cls_news
        
        # 统计
        total = sum(len(news) for news in news_by_source.values())
        print(f"✅ 共获取 {total} 条新闻")
        
        return news_by_source
    
    def fetch_all_industries(self, industries: List[str] = None) -> Dict[str, Dict[str, List[Dict]]]:
        """
        获取所有行业的新闻
        
        Args:
            industries: 行业列表，默认为全部
        
        Returns:
            Dict: {industry: {source: [news_list]}}
        """
        if industries is None:
            industries = list(INDUSTRY_KEYWORDS.keys())
        
        all_news = {}
        for industry in industries:
            all_news[industry] = self.fetch_industry_news(industry)
            time.sleep(0.5)  # 行业间间隔
        
        return all_news


def test_fetcher():
    """测试新闻抓取器"""
    fetcher = NewsFetcher()
    
    # 测试单个行业
    print("=" * 60)
    print("测试：获取光模块行业新闻")
    print("=" * 60)
    
    news = fetcher.fetch_industry_news("光模块", limit_per_source=2)
    
    print("\n" + "=" * 60)
    print("抓取结果汇总")
    print("=" * 60)
    
    total = 0
    for source, items in news.items():
        print(f"\n📰 {source} ({len(items)}条):")
        total += len(items)
        for item in items:
            title = item['title'][:40] + '...' if len(item['title']) > 40 else item['title']
            print(f"  • {title} [{item['impact']}]")
    
    print(f"\n总计: {total} 条新闻")
    return news


if __name__ == "__main__":
    test_fetcher()
