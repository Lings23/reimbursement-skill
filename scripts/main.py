#!/usr/bin/env python3
"""
加班餐费报销工具 - 主入口

触发条件：用户输入以 [加班餐报销] 开头
"""

import re
import sys
import subprocess
import os
from pathlib import Path


# 获取脚本所在目录和 workspace 根目录
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent  # reimbursement-skill

# 尝试推导 workspace 根目录
# 情况 1: skill 在 workspace/skills/reimbursement-tool/ 下
if SKILL_DIR.parent.name == 'skills':
    WORKSPACE = SKILL_DIR.parent.parent
# 情况 2: skill 直接在 workspace/reimbursement-skill/ 下
elif SKILL_DIR.parent.name == 'workspace' or (SKILL_DIR.parent / '.git').exists():
    WORKSPACE = SKILL_DIR.parent
else:
    # 默认：向上两级
    WORKSPACE = SKILL_DIR.parent.parent

# 默认配置（可通过环境变量覆盖）
INVOICE_DIR = Path(os.environ.get('REIMBURSE_INVOICE_DIR', WORKSPACE / 'reimbursement'))
OUTPUT_DIR = Path(os.environ.get('REIMBURSE_OUTPUT_DIR', WORKSPACE))


def parse_input(user_input):
    """解析用户输入"""
    # 提取加班事由
    reason_match = re.search(r'加班事由[:：]\s*(.+?)[。.]', user_input)
    reason = reason_match.group(1).strip() if reason_match else ''
    
    # 提取加班人员
    names_match = re.search(r'加班人员[:：]\s*(.+)', user_input)
    names_str = names_match.group(1).strip() if names_match else ''
    
    # 解析姓名列表（支持中文逗号、顿号、英文逗号、空格）
    names_str = names_str.replace('，', ',').replace('、', ',').replace(' ', ',')
    names = [n.strip() for n in names_str.split(',') if n.strip()]
    
    return reason, names


def run_script(script_name, args):
    """运行脚本"""
    script_path = SCRIPT_DIR / script_name
    cmd = [sys.executable, str(script_path)] + args
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description='加班餐费报销工具')
    parser.add_argument('input', nargs='?', help='用户输入字符串或输入文件路径')
    parser.add_argument('--invoice-dir', '-i', type=Path, default=INVOICE_DIR,
                        help=f'发票 PDF 目录 (默认：{INVOICE_DIR})')
    parser.add_argument('--output-dir', '-o', type=Path, default=OUTPUT_DIR,
                        help=f'输出文件目录 (默认：{OUTPUT_DIR})')
    parser.add_argument('--input-file', '-f', type=Path, help='从文件读取输入')
    
    args = parser.parse_args()
    
    # 获取用户输入
    if args.input_file:
        user_input = args.input_file.read_text(encoding='utf-8').strip()
    elif args.input:
        user_input = args.input
    else:
        print("用法：python main.py \"[加班餐报销] 加班事由：xxx 加班人员：xxx\"")
        print("   或：python main.py -f input.txt")
        print("   或：python main.py --invoice-dir /path/to/invoices --output-dir /path/to/output")
        sys.exit(1)
    
    if not user_input.startswith('[加班餐报销]'):
        print("❌ 输入必须以 [加班餐报销] 开头")
        sys.exit(1)
    
    print("=" * 60)
    print("加班餐费报销工具")
    print("=" * 60)
    print(f"工作区：{WORKSPACE}")
    print(f"发票目录：{args.invoice_dir}")
    print(f"输出目录：{args.output_dir}")
    
    # 1. 解析输入
    print("\n【1. 解析用户输入】")
    reason, names = parse_input(user_input)
    print(f"  加班事由：{reason}")
    print(f"  加班人员：{names} ({len(names)}人)")
    
    if not names:
        print("❌ 未找到加班人员名单")
        sys.exit(1)
    
    # 2. 提取发票信息
    print("\n【2. 提取发票信息】")
    invoice_data = '/tmp/invoice_data.json'
    
    if not run_script('extract_invoices.py', [str(args.invoice_dir), invoice_data]):
        print("⚠️ 发票提取失败，继续执行...")
    
    # 读取发票数据
    import json
    try:
        with open(invoice_data, 'r', encoding='utf-8') as f:
            invoices = json.load(f)
        
        # 计算金额
        total = sum(inv.get('价税合计（小写）', 0) for inv in invoices)
        if total % 50 == 0:
            amount = int(total)
        else:
            amount = (int(total) // 50 + 1) * 50
        
        # 获取日期
        date = invoices[0].get('开票日期', '') if invoices else ''
        
        print(f"  开票日期：{date}")
        print(f"  原始合计：{total:.2f}")
        print(f"  用餐金额：{amount} 元 (50 的倍数)")
    except Exception as e:
        print(f"⚠️ 读取发票数据失败：{e}")
        amount = 50 * len(names)  # 默认每人 50 元
        date = ''
    
    # 3. 填写报销审批表
    print("\n【3. 填写报销审批表】")
    
    success = run_script('fill_reimbursement.py', [
        '-i', str(SKILL_DIR / 'templates/加班餐费报销审批表模板.docx'),
        '-o', str(args.output_dir / '加班餐费报销审批表_已填写.docx'),
        '-t', str(SKILL_DIR / 'templates/加班餐费报销审批表.json'),
        '-n', ','.join(names),
        '-a', str(amount),
        '-r', reason,
        '-d', date
    ])
    
    if success:
        print("  ✓ 报销审批表已生成")
    
    # 4. 生成发票打印单
    print("\n【4. 生成发票打印单】")
    success = run_script('create_invoice_sheet.py', [
        '-i', str(args.invoice_dir),
        '-o', str(args.output_dir / '发票打印单.docx'),
        '-d', date,
        '-r', reason
    ])
    
    if success:
        print("  ✓ 发票打印单已生成")
    
    # 完成
    print("\n" + "=" * 60)
    print("✅ 报销处理完成！")
    print("=" * 60)
    print(f"\n输出文件：")
    print(f"  1. {args.output_dir / '加班餐费报销审批表_已填写.docx'}")
    print(f"  2. {args.output_dir / '发票打印单.docx'}")


if __name__ == '__main__':
    main()
