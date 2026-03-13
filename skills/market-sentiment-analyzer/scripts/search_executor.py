#!/usr/bin/env python3
"""
搜索执行器 - 实现严格的搜索深度与规则
调用OpenClaw MCP kimi_search工具
"""

import subprocess
import json
import time
from typing import List, Dict
from datetime import datetime

class SearchExecutor:
    """搜索执行器 - 严格遵循SEARCH_DEPTH_RULES"""
    
    def __init__(self, depth_level: int = 3):
        self.depth_level = depth_level
        self.search_log = []
        self.results = {
            "D1_实时新闻": [],
            "D2_分析解读": [],
            "D3_政策动态": [],
            "D4_国际形势": [],
            "D5_资本市场": []
        }
        
        # 根据深度级别设置搜索条数
        self.min_counts = {
            1: {"D1": 5, "D2": 5, "D3": 0, "D4": 0, "D5": 0},   # Quick Scan
            2: {"D1": 10, "D2": 10, "D3": 5, "D4": 5, "D5": 5},  # Standard
            3: {"D1": 20, "D2": 20, "D3": 10, "D4": 10, "D5": 10}, # Deep Dive
            4: {"D1": 50, "D2": 50, "D3": 30, "D4": 30, "D5": 30}  # Panoramic
        }.get(depth_level, {"D1": 20, "D2": 20, "D3": 10, "D4": 10, "D5": 10})
    
    def _call_kimi_search(self, query: str, limit: int = 10) -> List[Dict]:
        """调用kimi_search MCP工具"""
        try:
            # 使用openclaw命令调用MCP工具
            cmd = f"openclaw tools kimi_search '{query}' --limit {limit} 2>&1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            # 解析输出
            output = result.stdout + result.stderr
            
            # 尝试从输出中提取JSON
            try:
                # 查找JSON数组
                start = output.find('[')
                end = output.rfind(']')
                if start != -1 and end != -1:
                    json_str = output[start:end+1]
                    return json.loads(json_str)
            except:
                pass
            
            # 如果解析失败，返回空列表
            return []
        except Exception as e:
            print(f"    搜索失败: {e}")
            return []
    
    def execute_5d_search(self, industry: str) -> Dict:
        """
        执行5维强制覆盖搜索
        严格遵循SEARCH_DEPTH_RULES
        """
        print(f"\n🔍 启动5维深度搜索 (Level {self.depth_level})")
        print("=" * 60)
        start_time = datetime.now()
        
        # D1: 实时新闻
        print("\n【D1】实时新闻搜索...")
        queries_d1 = [
            f"{industry} 最新消息 今日",
            f"{industry} 今日行情 实时",
            f"{industry} 最新动态 2026"
        ]
        for query in queries_d1:
            results = self._call_kimi_search(query, limit=10)
            self.results["D1_实时新闻"].extend(results)
            print(f"  - '{query}': {len(results)}条")
            time.sleep(1)  # 避免请求过快
        print(f"  D1总计: {len(self.results['D1_实时新闻'])}条 (要求≥{self.min_counts['D1']})")
        
        # D2: 分析解读
        print("\n【D2】分析解读搜索...")
        queries_d2 = [
            f"{industry} 分析 研报",
            f"{industry} 投资分析 2026",
            f"{industry} 行业研究 券商"
        ]
        for query in queries_d2:
            results = self._call_kimi_search(query, limit=10)
            self.results["D2_分析解读"].extend(results)
            print(f"  - '{query}': {len(results)}条")
            time.sleep(1)
        print(f"  D2总计: {len(self.results['D2_分析解读'])}条 (要求≥{self.min_counts['D2']})")
        
        # D3: 政策动态
        print("\n【D3】政策动态搜索...")
        queries_d3 = [
            f"{industry} 政策 监管",
            f"AI 人工智能 政策 美国 中国",
            f"光模块 CPO 产业政策 补贴"
        ]
        for query in queries_d3:
            results = self._call_kimi_search(query, limit=8)
            self.results["D3_政策动态"].extend(results)
            print(f"  - '{query}': {len(results)}条")
            time.sleep(1)
        print(f"  D3总计: {len(self.results['D3_政策动态'])}条 (要求≥{self.min_counts['D3']})")
        
        # D4: 国际形势
        print("\n【D4】国际形势搜索...")
        queries_d4 = [
            "中东 伊朗 霍尔木兹海峡 地缘政治 2026",
            "石油 能源危机 油价 2026",
            "美联储 美元 货币政策 2026"
        ]
        for query in queries_d4:
            results = self._call_kimi_search(query, limit=8)
            self.results["D4_国际形势"].extend(results)
            print(f"  - '{query}': {len(results)}条")
            time.sleep(1)
        print(f"  D4总计: {len(self.results['D4_国际形势'])}条 (要求≥{self.min_counts['D4']})")
        
        # D5: 资本市场
        print("\n【D5】资本市场搜索...")
        queries_d5 = [
            f"{industry} 主力资金 资金流向",
            f"{industry} 机构 北向资金",
            f"AI板块 资金流出 减仓 2026"
        ]
        for query in queries_d5:
            results = self._call_kimi_search(query, limit=8)
            self.results["D5_资本市场"].extend(results)
            print(f"  - '{query}': {len(results)}条")
            time.sleep(1)
        print(f"  D5总计: {len(self.results['D5_资本市场'])}条 (要求≥{self.min_counts['D5']})")
        
        # 计算搜索质量
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        coverage = self._calculate_coverage()
        
        print("\n" + "=" * 60)
        print(f"✅ 5维搜索完成！用时: {duration:.1f}分钟")
        print(f"📊 覆盖度: {coverage['completed']}/{coverage['total']} 维度")
        print(f"📈 整体完成率: {coverage['rate']:.0%}")
        print("=" * 60)
        
        return {
            "results": self.results,
            "coverage": coverage,
            "duration_minutes": duration,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_coverage(self) -> Dict:
        """计算搜索覆盖度"""
        total = 5
        completed = 0
        
        for dim, min_count in self.min_counts.items():
            dim_key = {
                "D1": "D1_实时新闻",
                "D2": "D2_分析解读",
                "D3": "D3_政策动态",
                "D4": "D4_国际形势",
                "D5": "D5_资本市场"
            }.get(dim, dim)
            
            if len(self.results.get(dim_key, [])) >= min_count:
                completed += 1
        
        return {
            "total": total,
            "completed": completed,
            "rate": completed / total
        }
    
    def validate_critical_info(self, info: str) -> Dict:
        """
        验证关键信息（3源交叉验证）
        """
        print(f"\n🔍 验证关键信息: '{info}'")
        
        sources = []
        for dim_name, dim_results in self.results.items():
            for item in dim_results:
                title = item.get("title", "")
                if info in title or info in item.get("snippet", ""):
                    sources.append({
                        "dimension": dim_name,
                        "title": title,
                        "source": item.get("source", "未知")
                    })
        
        # 去重
        unique_sources = []
        seen = set()
        for s in sources:
            key = s["title"][:30]
            if key not in seen:
                seen.add(key)
                unique_sources.append(s)
        
        validation_status = "✅ 已验证" if len(unique_sources) >= 3 else \
                          "⚠️ 待验证" if len(unique_sources) >= 1 else "❌ 无法验证"
        
        print(f"  找到{len(unique_sources)}个独立来源")
        for s in unique_sources[:3]:
            print(f"    - [{s['dimension']}] {s['title'][:40]}...")
        
        return {
            "info": info,
            "source_count": len(unique_sources),
            "sources": unique_sources[:5],
            "validation_status": validation_status
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='5维深度搜索执行器')
    parser.add_argument('--industry', '-i', required=True, help='行业名称')
    parser.add_argument('--depth', '-d', type=int, default=3, help='搜索深度(1-4)')
    parser.add_argument('--output', '-o', help='输出文件')
    
    args = parser.parse_args()
    
    executor = SearchExecutor(depth_level=args.depth)
    result = executor.execute_5d_search(args.industry)
    
    # 验证示例
    executor.validate_critical_info("伊朗")
    executor.validate_critical_info("霍尔木兹")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 搜索结果保存: {args.output}")
