#!/usr/bin/env python3
"""
从 PDF 发票中提取开票日期和价税合计
"""

import subprocess
import json
import re
import sys
import glob
from pathlib import Path


def extract_text_from_pdf(pdf_path):
    """使用 pdftotext 提取 PDF 文本"""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', pdf_path, '-'],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout
    except Exception as e:
        print(f"⚠️ 无法读取 PDF {pdf_path}: {e}")
        return ""


def parse_invoice(text):
    """从发票文本中提取关键信息"""
    info = {
        '发票号码': '',
        '开票日期': '',
        '价税合计（小写）': '',
        '价税合计（大写）': ''
    }
    
    # 发票号码（支持中文冒号和英文冒号）
    for pattern in [r'发票号码：\s*([0-9]{10,20})', r'发票号码:\s*([0-9]{10,20})']:
        match = re.search(pattern, text)
        if match:
            info['发票号码'] = match.group(1)
            break
    
    # 开票日期（兼容特殊 Unicode 字符和空格）
    # ⽉ U+2F49 (康熙部首), 月 U+6708 (普通汉字)
    # ⽇ U+2F47 (康熙部首), 日 U+65E5 (普通汉字)
    for pattern in [r'开票日期：\s*([0-9]{4}\s*年\s*[0-9]+\s*[⽉月]\s*[0-9]+\s*[⽇日])', 
                    r'开票日期:\s*([0-9]{4}\s*年\s*[0-9]+\s*[⽉月]\s*[0-9]+\s*[⽇日])']:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            # 标准化日期格式
            date_str = date_str.replace('⽉', '月').replace('⽇', '日').replace(' ', '')
            info['开票日期'] = date_str
            break
    
    # 价税合计（小写）- 查找 ¥ 符号后的数字
    match = re.search(r'（小写）[¥￥]?\s*([0-9,]+\.?[0-9]*)', text)
    if match:
        amount = match.group(1).replace(',', '')
        info['价税合计（小写）'] = float(amount)
    
    # 价税合计（大写）
    match = re.search(r'（大写）\s*([零壹贰叁肆伍陆柒捌玖拾佰仟万亿圆整]+)', text)
    if match:
        info['价税合计（大写）'] = match.group(1)
    
    return info


def process_directory(input_dir, output_file=None):
    """处理目录中的所有 PDF 文件"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ 目录不存在：{input_dir}")
        return []
    
    # 使用 glob 避免中文文件名编码问题
    pdf_files = [Path(f) for f in glob.glob(str(input_path / '*.pdf'))]
    
    if not pdf_files:
        print(f"⚠️ 目录中没有 PDF 文件：{input_dir}")
        return []
    
    print(f"找到 {len(pdf_files)} 个 PDF 文件")
    
    invoices = []
    for pdf_path in pdf_files:
        print(f"\n处理：{pdf_path.name}")
        text = extract_text_from_pdf(str(pdf_path))
        info = parse_invoice(text)
        info['pdf_file'] = pdf_path.name
        
        if info['发票号码'] or info['开票日期']:
            invoices.append(info)
            print(f"  ✓ 发票号码：{info['发票号码']}")
            print(f"  ✓ 开票日期：{info['开票日期']}")
            print(f"  ✓ 价税合计：{info['价税合计（小写）']}")
        else:
            print(f"  ⚠️ 未能提取到有效信息")
    
    # 保存结果
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(invoices, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 结果已保存：{output_file}")
    
    return invoices


def calculate_amount(invoices):
    """计算总金额并向上取整到 50 的倍数"""
    total = sum(inv.get('价税合计（小写）', 0) for inv in invoices)
    
    if total == 0:
        return 0, 0
    
    # 向上取整到 50 的倍数
    if total % 50 == 0:
        rounded = int(total)
    else:
        rounded = (int(total) // 50 + 1) * 50
    
    print(f"\n💰 金额计算：")
    print(f"  原始合计：{total:.2f}")
    print(f"  取整后：{rounded} (50 的倍数)")
    
    return total, rounded


def get_latest_date(invoices):
    """获取最新的开票日期"""
    dates = [inv['开票日期'] for inv in invoices if inv.get('开票日期')]
    if not dates:
        return ''
    # 返回第一个（或可以按日期排序后返回最新的）
    return dates[0]


if __name__ == '__main__':
    import os
    
    # 支持环境变量或命令行参数
    default_invoice_dir = os.environ.get('REIMBURSE_INVOICE_DIR', 
                                         Path(__file__).parent.parent.parent.parent / 'reimbursement')
    
    input_dir = sys.argv[1] if len(sys.argv) > 1 else str(default_invoice_dir)
    output_file = sys.argv[2] if len(sys.argv) > 2 else '/tmp/invoice_data.json'
    
    invoices = process_directory(input_dir, output_file)
    
    if invoices:
        total, rounded = calculate_amount(invoices)
        date = get_latest_date(invoices)
        
        print(f"\n📅 开票日期：{date}")
        print(f"💵 用餐金额（取整后）：{rounded} 元")
