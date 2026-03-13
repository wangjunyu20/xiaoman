#!/usr/bin/env python3
"""
报告完整性检验脚本
按SKILL.md数据校验机制执行
"""
import json
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/root/.openclaw/workspace_investment/output/research_reports")
REPORTS_DIR = OUTPUT_DIR / "reports"

def check_report_integrity():
    """检验报告完整性"""
    print("=" * 60)
    print("📋 报告完整性检验")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # 1. 检查首页是否存在
    index_file = OUTPUT_DIR / "index.html"
    if not index_file.exists():
        errors.append("❌ 首页 index.html 不存在")
    else:
        content = index_file.read_text(encoding='utf-8')
        
        # 检查关键元素
        if '查看详情' not in content and 'detail-link' not in content:
            errors.append("❌ 首页缺少跳转到详情页的链接")
        
        if 'href="reports/' not in content:
            errors.append("❌ 首页没有正确链接到reports目录")
        
        # 检查行业数量
        industry_count = content.count('industry-card')
        if industry_count < 15:
            errors.append(f"❌ 首页行业卡片数量不足: {industry_count}/15")
        else:
            print(f"✅ 首页行业卡片数量: {industry_count}")
        
        # 检查新闻资讯
        if 'news-section' not in content:
            warnings.append("⚠️ 首页缺少新闻资讯栏目")
        else:
            # 检查新闻标题链接
            news_links = re.findall(r'<a[^>]*href="(http[^"]*)"[^>]*class="news-title-link"', content)
            if not news_links:
                errors.append("❌ 新闻标题缺少原文链接")
            else:
                print(f"✅ 新闻标题链接数量: {len(news_links)}")
                # 验证链接格式
                invalid_links = [link for link in news_links if not link.startswith('http')]
                if invalid_links:
                    errors.append(f"❌ 发现无效新闻链接: {invalid_links[:3]}")
        
        # 检查模糊词汇
        fuzzy_words = ['近日', '最近', '近期', '日前']
        for word in fuzzy_words:
            if word in content:
                warnings.append(f"⚠️ 发现模糊词汇: '{word}'")
    
    # 2. 检查详情页
    print("\n📄 检查详情页...")
    expected_industries = [
        'consumption', 'semiconductor', 'aerospace', 'biotech', 'low_altitude',
        'computing_infra', 'optical_module', 'satellite', 'embodied_ai', '6g',
        'quantum', 'brain_machine', 'nuclear_fusion', 'ai_app', 'ai_healthcare'
    ]
    
    missing_details = []
    empty_details = []
    
    for industry in expected_industries:
        detail_file = REPORTS_DIR / f"{industry}.html"
        if not detail_file.exists():
            missing_details.append(industry)
        else:
            content = detail_file.read_text(encoding='utf-8')
            # 检查是否为空（少于500字符视为空）
            if len(content) < 500:
                empty_details.append(industry)
            # 检查关键栏目（支持新旧两种模板）
            has_old_structure = '<h2>一、行业概览</h2>' in content
            has_new_structure = '📊 行情与舆情分析' in content and '📋 多步因果推导' in content
            
            if not has_old_structure and not has_new_structure:
                errors.append(f"❌ {industry}.html 缺少行业概览或行情舆情分析")
            
            # 旧模板检查
            if has_old_structure:
                if '<h2>二、本周重大资讯</h2>' not in content:
                    errors.append(f"❌ {industry}.html 缺少'二、本周重大资讯'")
                if '<h2>三、龙头股跟踪</h2>' not in content:
                    errors.append(f"❌ {industry}.html 缺少'三、龙头股跟踪'")
            
            # 新模板检查
            if has_new_structure:
                if '📈 成分股行情' not in content and '成分股行情' not in content:
                    warnings.append(f"⚠️ {industry}.html 可能缺少成分股行情")
                if '⚠️ 风险提示' not in content and '风险提示' not in content:
                    warnings.append(f"⚠️ {industry}.html 可能缺少风险提示")
    
    if missing_details:
        errors.append(f"❌ 缺少详情页: {', '.join(missing_details)}")
    else:
        print(f"✅ 所有15个行业详情页已生成")
    
    if empty_details:
        errors.append(f"❌ 详情页内容为空: {', '.join(empty_details)}")
    
    # 3. 检查返回首页链接
    print("\n🔗 检查详情页返回链接...")
    for detail_file in REPORTS_DIR.glob("*.html"):
        content = detail_file.read_text(encoding='utf-8')
        if 'href="../index.html"' not in content and 'href="../"' not in content:
            errors.append(f"❌ {detail_file.name} 缺少返回首页链接")
        
        # 检查详情页新闻链接
        if 'news-link' not in content and '本周重大资讯' in content:
            warnings.append(f"⚠️ {detail_file.name} 可能缺少新闻链接")
    
    # 4. 检查PDF文件
    print("\n📑 检查PDF报告...")
    import glob
    pdf_files = list(OUTPUT_DIR.glob("行业研究报告_*.pdf"))
    if not pdf_files:
        warnings.append("⚠️ 未找到PDF报告文件（可选）")
    else:
        # 检查最新的PDF
        latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
        pdf_size = latest_pdf.stat().st_size / 1024  # KB
        if pdf_size < 100:
            errors.append(f"❌ PDF文件过小: {pdf_size:.1f}KB，可能内容不完整")
        else:
            print(f"✅ PDF报告已生成: {latest_pdf.name} ({pdf_size:.1f}KB)")
    
    # 5. 汇总结果
    print("\n" + "=" * 60)
    print("📊 检验结果")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print(f"\n⚠️ 发现 {len(warnings)} 个警告:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors and not warnings:
        print("\n✅ 所有检验通过！报告完整。")
        return True
    elif not errors:
        print("\n⚠️ 报告可用，但存在警告。")
        return True
    else:
        print("\n❌ 报告存在错误，需要修复！")
        return False

if __name__ == "__main__":
    success = check_report_integrity()
    exit(0 if success else 1)
