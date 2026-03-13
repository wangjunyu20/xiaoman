#!/usr/bin/env python3
"""
多源财经新闻聚合器
整合：财联社、新浪财经、东方财富、AKShare、东财股吧等多个数据源
"""

import sys
import json
import requests
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "industry-research-report" / "scripts"))

# 数据源配置
DATA_SOURCES = {
    "cailianshe": True,  # 财联社电报
    "sina": True,        # 新浪财经
    "eastmoney": True,   # 东方财富新闻
    "guba": True,        # 东财股吧
    "akshare": True,     # AKShare新闻
}

# 行业关键词映射
INDUSTRY_KEYWORDS = {
    "芯片": ["芯片", "半导体", "中芯国际", "北方华创", "韦尔股份", "光刻机", "国产替代", "制程", "制裁"],
    "算力": ["算力", "智算中心", "大模型", "算力租赁", "中科曙光", "浪潮信息", "紫光股份", "智算集群"],
    "AI应用": ["AI应用", "人工智能", "大模型", "AIGC", "科大讯飞", "广联达", "ChatGPT", "文心一言", "Agent"],
    "人形机器人": ["人形机器人", "机器人", "优必选", "特斯拉机器人", "埃斯顿", "汇川技术", "减速器", "执行器"],
    "量子科技": ["量子科技", "量子计算", "量子通信", "国盾量子", "四创电子", "本源量子", "祖冲之号"],
    "脑机接口": ["脑机接口", "Neuralink", "三博脑科", "国际医学", "脑科学", "神经接口"],
    "低空经济": ["低空经济", "eVTOL", "万丰奥威", "中信海直", "适航证", "低空飞行"],
    "光模块": ["光模块", "CPO", "光通信", "中际旭创", "天孚通信", "新易盛", "1.6T", "英伟达"],
    "生物医药": ["生物医药", "创新药", "药明康德", "恒瑞医药", "临床试验", "FDA", "管线"],
    "航空航天": ["航空航天", "军工", "中航沈飞", "航发动力", "卫星", "列装", "军贸"],
    "6G": ["6G", "通信", "中兴通讯", "信维通信", "太赫兹", "标准", "频谱"],
    "卫星互联网": ["卫星互联网", "星链", "低轨卫星", "中国卫星", "北斗星通", "组网"],
    "可控核聚变": ["核聚变", "人造太阳", "ITER", "东方电气", "中国核建", "托卡马克"],
    "消费": ["消费", "复苏", "中国中免", "贵州茅台", "伊利股份", "促销", "政策"],
    "AI医疗": ["AI医疗", "智慧医疗", "卫宁健康", "爱尔眼科", "医疗AI", "智能诊断"],
}

class MultiSourceNewsAggregator:
    """多源新闻聚合器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.cache_dir = Path(__file__).parent.parent / "output" / "news_cache_multi"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 尝试导入akshare
        self.has_akshare = False
        try:
            import akshare as ak
            self.ak = ak
            self.has_akshare = True
        except ImportError:
            pass
    
    def _get_cache(self, key: str) -> Optional[List[Dict]]:
        """获取缓存"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if time.time() - data.get('timestamp', 0) < 3600:  # 1小时缓存
                        return data.get('news', [])
            except:
                pass
        return None
    
    def _set_cache(self, key: str, news: List[Dict]):
        """设置缓存"""
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': time.time(), 'news': news}, f, ensure_ascii=False, indent=2)
    
    def _analyze_impact(self, text: str) -> str:
        """分析新闻影响倾向"""
        text = text.lower()
        positive_words = ['利好', '增长', '突破', '上涨', '涨停', '创新', '签约', '合作', '中标', '订单', '大增', '新高', '超预期', '爆款', '领先', '获批准', '获批']
        negative_words = ['利空', '下跌', '跌停', '亏损', '减持', '处罚', '违规', '召回', '下架', '下滑', '不及预期', '风险', '警示', '大跌', '爆雷', '流出']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            return '利好'
        elif neg_count > pos_count:
            return '利空'
        return '中性'
    
    # ========== 数据源1: 财联社电报 ==========
    def fetch_cailianshe(self, keyword: str, limit: int = 10) -> List[Dict]:
        """抓取财联社电报"""
        cache_key = f"cailianshe_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        keywords_to_match = [keyword] + INDUSTRY_KEYWORDS.get(keyword, [keyword])
        
        try:
            url = "https://www.cls.cn/nodeapi/telegraphList"
            params = {'app': 'CailianpressWeb', 'os': 'web', 'sv': '8.4.6', 'sign': 'default'}
            
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('data', {}).get('roll_data', []):
                    title = item.get('title', '')
                    content = item.get('content', '')
                    all_text = title + content
                    
                    if any(kw in all_text for kw in keywords_to_match):
                        news_list.append({
                            'source': '财联社',
                            'title': title if title else content[:50] + '...',
                            'url': item.get('shareurl', ''),
                            'publish_time': item.get('time', ''),
                            'summary': content[:100] + '...' if len(content) > 100 else content,
                            'impact': self._analyze_impact(all_text)
                        })
                        if len(news_list) >= limit * 2:
                            break
        except Exception as e:
            print(f"  财联社获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    # ========== 数据源2: 新浪财经 ==========
    def fetch_sina(self, keyword: str, limit: int = 10) -> List[Dict]:
        """抓取新浪财经"""
        cache_key = f"sina_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        keywords_to_match = [keyword] + INDUSTRY_KEYWORDS.get(keyword, [keyword])
        
        try:
            url = "https://search.sina.com.cn/"
            params = {'q': keyword, 'c': 'news', 'from': 'channel', 'ie': 'utf-8'}
            
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                # 提取新闻
                pattern = r'<h2><a[^>]*href="([^"]*)"[^>]*>(.*?)</a></h2>'
                matches = re.findall(pattern, resp.text, re.DOTALL)
                
                for url, title in matches[:limit * 2]:
                    title_clean = re.sub(r'<[^>]+>', '', title).strip()
                    if title_clean and any(kw in title_clean for kw in keywords_to_match):
                        news_list.append({
                            'source': '新浪财经',
                            'title': title_clean,
                            'url': url if url.startswith('http') else f"https:{url}",
                            'publish_time': datetime.now().strftime('%Y-%m-%d'),
                            'summary': '',
                            'impact': self._analyze_impact(title_clean)
                        })
                        if len(news_list) >= limit:
                            break
        except Exception as e:
            print(f"  新浪财经获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    # ========== 数据源3: AKShare东方财富新闻 ==========
    def fetch_akshare(self, keyword: str, limit: int = 10) -> List[Dict]:
        """使用AKShare获取东方财富新闻"""
        if not self.has_akshare:
            return []
        
        cache_key = f"akshare_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        keywords_to_match = [keyword] + INDUSTRY_KEYWORDS.get(keyword, [keyword])
        
        try:
            import akshare as ak
            df = ak.stock_news_em()
            
            for _, row in df.head(100).iterrows():
                title = str(row.get('新闻标题', ''))
                content = str(row.get('新闻内容', ''))
                all_text = title + content
                
                if any(kw in all_text for kw in keywords_to_match):
                    news_list.append({
                        'source': str(row.get('文章来源', '东方财富')),
                        'title': title,
                        'url': str(row.get('新闻链接', '')),
                        'publish_time': str(row.get('发布时间', ''))[:16],
                        'summary': content[:80] + '...' if len(content) > 80 else content,
                        'impact': self._analyze_impact(all_text)
                    })
                    if len(news_list) >= limit:
                        break
        except Exception as e:
            print(f"  AKShare获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    # ========== 数据源4: 东方财富股吧 ==========
    def fetch_guba(self, keyword: str, limit: int = 10) -> List[Dict]:
        """抓取东方财富股吧"""
        cache_key = f"guba_{keyword}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached[:limit]
        
        news_list = []
        keywords_to_match = [keyword] + INDUSTRY_KEYWORDS.get(keyword, [keyword])
        
        # 东财板块代码映射
        board_codes = {
            "芯片": "885908", "半导体": "885908",
            "算力": "885871", "人形机器人": "885863",
            "量子科技": "885626", "脑机接口": "885757",
            "低空经济": "885913", "光模块": "873991",
            "生物医药": "885919", "6G": "885914",
            "卫星互联网": "885918", "航空航天": "885735",
            "消费": "885925", "AI应用": "885901",
        }
        
        try:
            board_code = board_codes.get(keyword, '')
            if board_code:
                url = f"https://guba.eastmoney.com/interface/api/getlistbypage"
                params = {'type': '1', 'code': board_code, 'page': '1', 'pageSize': str(limit * 2)}
                
                resp = self.session.get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get('re', []):
                        title = item.get('post_title', '')
                        if any(kw in title for kw in keywords_to_match):
                            news_list.append({
                                'source': '东财股吧',
                                'title': title,
                                'url': f"https://guba.eastmoney.com{item.get('post_url', '')}",
                                'publish_time': item.get('post_publish_time', ''),
                                'summary': item.get('post_content', '')[:60] + '...' if len(item.get('post_content', '')) > 60 else item.get('post_content', ''),
                                'impact': self._analyze_impact(title)
                            })
                            if len(news_list) >= limit:
                                break
        except Exception as e:
            print(f"  东财股吧获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list[:limit]
    
    # ========== 聚合所有数据源 ==========
    def aggregate_news(self, keyword: str, limit_per_source: int = 10) -> List[Dict]:
        """聚合所有数据源的新闻"""
        all_news = []
        
        print(f"  → 财联社...")
        all_news.extend(self.fetch_cailianshe(keyword, limit_per_source))
        time.sleep(0.3)
        
        print(f"  → 新浪财经...")
        all_news.extend(self.fetch_sina(keyword, limit_per_source))
        time.sleep(0.3)
        
        print(f"  → AKShare东方财富...")
        all_news.extend(self.fetch_akshare(keyword, limit_per_source))
        time.sleep(0.3)
        
        print(f"  → 东财股吧...")
        all_news.extend(self.fetch_guba(keyword, limit_per_source))
        
        # 去重（按标题）
        seen_titles = set()
        unique_news = []
        for news in all_news:
            title_key = news['title'][:20]  # 取前20字作为去重key
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        # 按影响排序：利好 > 中性 > 利空
        impact_order = {'利好': 0, '中性': 1, '利空': 2}
        unique_news.sort(key=lambda x: impact_order.get(x.get('impact', '中性'), 1))
        
        return unique_news


# 测试
if __name__ == "__main__":
    aggregator = MultiSourceNewsAggregator()
    
    test_industries = ["光模块", "芯片", "算力", "AI应用"]
    for industry in test_industries:
        print(f"\n{'='*60}")
        print(f"测试行业: {industry}")
        print('='*60)
        news = aggregator.aggregate_news(industry, limit_per_source=3)
        print(f"\n共获取 {len(news)} 条新闻:")
        for i, n in enumerate(news[:5], 1):
            print(f"  {i}. [{n['source']}] {n['title'][:40]}... ({n['impact']})")
