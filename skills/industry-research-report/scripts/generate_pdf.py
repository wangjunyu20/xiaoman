#!/usr/bin/env python3
"""
生成带目录的PDF报告
包含首页 + 所有15个行业详情页
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/root/.openclaw/workspace_investment/output/research_reports")
REPORTS_DIR = OUTPUT_DIR / "reports"

def generate_pdf():
    """使用Playwright生成PDF"""
    
    today = datetime.now().strftime("%Y%m%d")
    pdf_path = OUTPUT_DIR / f"行业研究报告_{today}.pdf"
    
    # 创建合并的HTML文件（带目录）
    merged_html = create_merged_html()
    merged_path = OUTPUT_DIR / "merged_for_pdf.html"
    merged_path.write_text(merged_html, encoding='utf-8')
    
    # 使用Playwright生成PDF
    script = f'''
import asyncio
from playwright.async_api import async_playwright

async def generate_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('file://{merged_path}')
        await page.wait_for_load_state('networkidle')
        
        # 生成PDF，带目录书签
        await page.pdf(
            path='{pdf_path}',
            format='A4',
            print_background=True,
            margin={{
                'top': '40px',
                'bottom': '40px',
                'left': '40px',
                'right': '40px'
            }},
            display_header_footer=True,
            header_template='<div style="font-size:9px; margin-left:40px; color:#666;">热点行业研究报告</div>',
            footer_template='<div style="font-size:9px; margin-left:40px; color:#666;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
        )
        
        await browser.close()
        print(f"✅ PDF生成完成: {pdf_path}")

asyncio.run(generate_pdf())
'''
    
    # 写入并执行
    script_path = OUTPUT_DIR / "_generate_pdf_script.py"
    script_path.write_text(script, encoding='utf-8')
    
    result = subprocess.run(
        ["python3", str(script_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ PDF生成失败: {result.stderr}")
        return None
    
    # 清理临时文件
    script_path.unlink()
    
    return pdf_path


def create_merged_html():
    """创建合并的HTML（首页+所有详情页+目录）"""
    
    today = datetime.now().strftime("%Y年%m月%d日")
    
    # 读取首页内容
    index_html = (OUTPUT_DIR / "index.html").read_text(encoding='utf-8')
    
    # 提取首页主体内容（去掉head和body标签，只保留内容）
    index_body = extract_body_content(index_html)
    
    # 定义15个行业
    industries = [
        {"name": "消费", "file": "consumption"},
        {"name": "集成电路", "file": "semiconductor"},
        {"name": "航空航天", "file": "aerospace"},
        {"name": "生物医药", "file": "biotech"},
        {"name": "低空经济", "file": "low_altitude"},
        {"name": "算力基础设施", "file": "computing_infra"},
        {"name": "光模块", "file": "optical_module"},
        {"name": "卫星互联网", "file": "satellite"},
        {"name": "具身智能/人形机器人", "file": "embodied_ai"},
        {"name": "6G", "file": "6g"},
        {"name": "量子科技", "file": "quantum"},
        {"name": "脑机接口", "file": "brain_machine"},
        {"name": "可控核聚变", "file": "nuclear_fusion"},
        {"name": "AI应用", "file": "ai_app"},
        {"name": "AI+医疗", "file": "ai_healthcare"},
    ]
    
    # 生成目录
    toc_html = generate_toc(industries)
    
    # 读取所有详情页
    details_html = []
    for ind in industries:
        detail_file = REPORTS_DIR / f"{ind['file']}.html"
        if detail_file.exists():
            content = detail_file.read_text(encoding='utf-8')
            body = extract_body_content(content)
            # 添加锚点
            details_html.append(f'<div class="page-break" id="{ind["file"]}"></div>')
            details_html.append(body)
    
    # 合并HTML
    merged = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>热点行业研究报告 - {today}</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 100%;
        }}
        
        /* 目录样式 */
        .toc {{
            page-break-after: always;
            padding: 40px 20px;
        }}
        
        .toc h1 {{
            font-size: 24px;
            text-align: center;
            margin-bottom: 40px;
            color: #1a1a1a;
        }}
        
        .toc-list {{
            list-style: none;
            padding: 0;
            max-width: 500px;
            margin: 0 auto;
        }}
        
        .toc-list li {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px dotted #ccc;
            font-size: 14px;
        }}
        
        .toc-list a {{
            color: #333;
            text-decoration: none;
        }}
        
        .toc-list a:hover {{
            color: #0066cc;
        }}
        
        /* 分页 */
        .page-break {{
            page-break-before: always;
        }}
        
        /* 适配打印 */
        @media print {{
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
        
        /* 继承原有样式 */
        {extract_styles(index_html)}
    </style>
</head>
<body>
    <!-- 目录页 -->
    <div class="toc">
        <h1>📊 热点行业研究报告<br><small>{today}</small></h1>
        {toc_html}
    </div>
    
    <!-- 首页概览 -->
    <div class="page-break" id="overview"></div>
    {index_body}
    
    <!-- 各行业详情 -->
    {''.join(details_html)}
    
</body>
</html>'''
    
    return merged


def generate_toc(industries):
    """生成目录HTML"""
    items = [
        '<li><a href="#overview">一、行业概览（首页）</a></li>'
    ]
    
    for i, ind in enumerate(industries, 2):
        items.append(f'<li><a href="#{ind["file"]}">{i}、{ind["name"]}</a></li>')
    
    return f'<ol class="toc-list">{ "".join(items) }</ol>'


def extract_body_content(html):
    """提取body内容"""
    import re
    
    # 找到body标签
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        return body_match.group(1)
    
    # 如果没找到body，返回整个内容
    return html


def extract_styles(html):
    """提取style标签内容"""
    import re
    
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    return '\n'.join(styles)


if __name__ == "__main__":
    pdf_path = generate_pdf()
    if pdf_path:
        print(f"✅ PDF报告已生成: {pdf_path}")
    else:
        print("❌ PDF生成失败")
        exit(1)
