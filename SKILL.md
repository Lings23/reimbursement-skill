---
name: reimbursement-tool
description: 加班餐费报销自动化工具。当用户输入以 [加班餐报销] 开头时触发，自动读取发票 PDF、填写报销审批表、生成发票打印单。
version: 1.0.0
author: lc
license: MIT
---

# 加班餐费报销工具

## 📦 移植指南

### 快速移植

```bash
# 1. 复制到目标 OpenClaw workspace
cp -r skills/reimbursement-tool /path/to/new/workspace/skills/

# 2. 安装系统依赖
# Ubuntu/Debian:
sudo apt-get install -y poppler-utils

# macOS:
brew install poppler

# 3. 安装 Python 依赖
cd /path/to/new/workspace/skills/reimbursement-tool
pip install -r requirements.txt

# 4. 创建发票目录
mkdir -p /path/to/new/workspace/reimbursement

# 5. 测试
python3 scripts/main.py "[加班餐报销] 加班事由：测试 加班人员：张三"
```

### 目录结构要求

```
<workspace>/
├── skills/
│   └── reimbursement-tool/    # 此技能目录
└── reimbursement/              # 发票 PDF 目录（可选位置）
```

### 配置方式

**方式 1: 默认路径**
- 发票目录：`<workspace>/reimbursement/`
- 输出目录：`<workspace>/`

**方式 2: 环境变量**
```bash
export REIMBURSE_INVOICE_DIR=/path/to/invoices
export REIMBURSE_OUTPUT_DIR=/path/to/output
```

**方式 3: 命令行参数**
```bash
python3 scripts/main.py "[加班餐报销] ..." \
    --invoice-dir /path/to/invoices \
    --output-dir /path/to/output
```

---

## 触发条件

用户输入以 `[加班餐报销]` 开头

## 输入格式

```
[加班餐报销] 加班事由：<事由>。加班人员：<姓名 1>、<姓名 2>...
```

### 样例

```
[加班餐报销] 加班事由：支撑部科技司某方案的集中改稿。加班人员：贺林佳、甘俊霖、陈朴、刘畅、李婷、徐若雨、钟鸣、张扬
```

## 目录结构

```
skills/reimbursement-tool/
├── SKILL.md              # 技能定义（本文件）
├── README.md             # 详细文档
├── scripts/              # 可执行脚本
│   ├── extract_invoices.py      # 从 PDF 提取发票信息
│   ├── fill_reimbursement.py    # 填写报销审批表
│   ├── create_invoice_sheet.py  # 生成发票打印单
│   ├── main.py                  # 主入口脚本
│   ├── analyze_docx.py          # 分析 docx 生成模板（开发工具）
│   └── fill_from_template.py    # 通用模板填写工具（开发工具）
├── templates/            # 模板文件
│   ├── 加班餐费报销审批表模板.docx
│   ├── 加班餐费报销审批表.json
│   └── 加班餐费报销审批表模板_template.json
└── references/           # 参考资料（可选）
```

## 可移植配置

本技能支持完全可移植，通过以下方式配置路径：

### 环境变量

```bash
export REIMBURSE_INVOICE_DIR=/path/to/invoices   # 发票 PDF 目录
export REIMBURSE_OUTPUT_DIR=/path/to/output      # 输出文件目录
```

### 命令行参数

```bash
python3 scripts/main.py "[加班餐报销] ..." \
    --invoice-dir /path/to/invoices \
    --output-dir /path/to/output
```

### 默认行为

- 发票目录：`<workspace>/reimbursement/`
- 输出目录：`<workspace>/`（技能目录的上级）

## 工作流程

### 1. 解析用户输入

从用户输入中提取：
- **加班事由**：`加班事由：` 之后、`加班人员：` 之前的内容
- **加班人员**：`加班人员：` 之后的姓名列表（支持 `、`，`,`, ` ` 分隔）

### 2. 读取发票 PDF

读取 `/home/lc/.openclaw/workspace/reimbursement/` 目录下的所有 PDF 文件：

```bash
python3 skills/reimbursement-tool/scripts/extract_invoices.py \
    /home/lc/.openclaw/workspace/reimbursement \
    /tmp/invoice_data.json
```

提取每张发票的：
- **发票号码**
- **开票日期**
- **价税合计（小写）**

### 3. 计算用餐金额

```python
# 对所有价税合计求和
sum = sum(所有发票的价税合计)

# 向上取整到 50 的倍数
if sum % 50 == 0:
    amount = sum
else:
    amount = (sum // 50 + 1) * 50
```

### 4. 填写报销审批表

使用模板 `templates/加班餐费报销审批表.json` 填写：

```bash
python3 skills/reimbursement-tool/scripts/fill_reimbursement.py \
    --input skills/reimbursement-tool/templates/加班餐费报销审批表模板.docx \
    --output /home/lc/.openclaw/workspace/加班餐费报销审批表_已填写.docx \
    --template skills/reimbursement-tool/templates/加班餐费报销审批表.json \
    --names "<姓名列表>" \
    --amount <计算后的金额> \
    --reason "<加班事由>" \
    --date "<开票日期>"
```

**填写格式要求：**
- 字体：宋体
- 字号：四号
- 对齐：居中

### 5. 生成发票打印单

创建 `发票打印单.docx`：

```bash
python3 skills/reimbursement-tool/scripts/create_invoice_sheet.py \
    --input-dir /home/lc/.openclaw/workspace/reimbursement \
    --output /home/lc/.openclaw/workspace/发票打印单.docx \
    --date "<开票日期>" \
    --reason "<加班事由>"
```

**格式要求：**
- 页面：A4
- 页边距：上 4cm，左右下 2.54cm（默认）
- 第一页：PDF 转图片，尽可能占满页面但不超出一页
- 第二页：中间位置填写用餐时间和加班事由，字号四号

## 输出文件

1. `加班餐费报销审批表_已填写.docx` - 填写完整的报销审批表
2. `发票打印单.docx` - 发票图片 + 用餐信息

## 依赖

```bash
pip install pdf2image python-docx pillow pdfplumber pdftotext --break-system-packages
```

## 注意事项

1. PDF 发票必须放在 `/home/lc/.openclaw/workspace/reimbursement/` 目录
2. 开票日期取第一张发票的日期（或最新日期）
3. 用餐金额必须是 50 的倍数（向上取整）
4. 姓名列表支持多种分隔符（`、`，`,`, ` `，中文逗号 `，`）

## 开发工具

- `scripts/analyze_docx.py` - 分析 docx 文档结构，自动生成模板 JSON
- `scripts/fill_from_template.py` - 通用模板填写工具，支持从 JSON 数据文件加载
