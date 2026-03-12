# 加班餐费报销工具

## 📋 功能说明

自动化工具，用于处理加班餐费报销流程：
- 从 PDF 发票提取开票日期和金额
- 自动计算用餐金额（50 的倍数）
- 填写报销审批表
- 生成发票打印单

## 🚀 使用方法

### 方式 1：直接运行主脚本

```bash
cd /path/to/your/workspace/skills/reimbursement-tool

python3 scripts/main.py "[加班餐报销] 加班事由：支撑部科技司某方案的集中改稿。加班人员：贺林佳、甘俊霖、陈朴、刘畅"
```

### 方式 2：指定路径（可移植）

```bash
python3 scripts/main.py "[加班餐报销] ..." \
    --invoice-dir /path/to/invoices \
    --output-dir /path/to/output
```

### 方式 3：使用环境变量

```bash
export REIMBURSE_INVOICE_DIR=/path/to/invoices
export REIMBURSE_OUTPUT_DIR=/path/to/output

python3 scripts/main.py "[加班餐报销] ..."
```

### 方式 4：分步执行

```bash
cd /path/to/workspace

# 1. 提取发票信息
python3 skills/reimbursement-tool/scripts/extract_invoices.py \
    /path/to/invoices \
    /tmp/invoice_data.json

# 2. 填写报销审批表
python3 skills/reimbursement-tool/scripts/fill_reimbursement.py \
    -i skills/reimbursement-tool/templates/加班餐费报销审批表模板.docx \
    -o /path/to/output/加班餐费报销审批表_已填写.docx \
    -t skills/reimbursement-tool/templates/加班餐费报销审批表.json \
    -n "贺林佳，甘俊霖，陈朴，刘畅" \
    -a 400 \
    -r "支撑部科技司某方案的集中改稿。" \
    -d "2026 年 3 月 11 日"

# 3. 生成发票打印单
python3 skills/reimbursement-tool/scripts/create_invoice_sheet.py \
    -i /path/to/invoices \
    -o /path/to/output/发票打印单.docx \
    -d "2026 年 3 月 11 日" \
    -r "支撑部科技司某方案的集中改稿。"
```

## 📁 文件结构

```
skills/reimbursement-tool/
├── SKILL.md                    # Skill 定义
├── README.md                   # 使用说明
├── scripts/                    # 可执行脚本
│   ├── main.py                 # 主入口
│   ├── extract_invoices.py     # 发票信息提取
│   ├── fill_reimbursement.py   # 填写审批表
│   ├── create_invoice_sheet.py # 生成打印单
│   ├── analyze_docx.py         # 分析 docx 生成模板（开发工具）
│   └── fill_from_template.py   # 通用模板填写工具（开发工具）
├── templates/                  # 模板文件
│   ├── 加班餐费报销审批表模板.docx
│   ├── 加班餐费报销审批表.json
│   └── 加班餐费报销审批表模板_template.json
└── references/                 # 参考资料（可选）
```

## 📥 输入要求

### PDF 发票位置
`/home/lc/.openclaw/workspace/reimbursement/`

### 用户输入格式
```
[加班餐报销] 加班事由：<事由>。加班人员：<姓名 1>、<姓名 2>...
```

### 样例
```
[加班餐报销] 加班事由：支撑部科技司某方案的集中改稿。加班人员：贺林佳、甘俊霖、陈朴、刘畅、李婷、徐若雨、钟鸣、张扬
```

## 📤 输出文件

1. **加班餐费报销审批表_已填写.docx**
   - 用餐时间（从发票提取）
   - 用餐人数（自动计算）
   - 用餐金额（50 的倍数）
   - 加班事由（用户输入）
   - 用餐人员名单（用户输入）

2. **发票打印单.docx**
   - 第一页：发票 PDF 转图片
   - 第二页：用餐时间和加班事由

## 💰 金额计算规则

```python
sum = 所有发票的价税合计

if sum % 50 == 0:
    amount = sum
else:
    amount = (sum // 50 + 1) * 50  # 向上取整
```

**示例：**
- ¥68.10 → ¥100
- ¥320 → ¥350
- ¥380 → ¥400
- ¥400 → ¥400

## 📐 格式要求

### 报销审批表
- 字体：宋体
- 字号：四号（14pt）
- 对齐：居中

### 发票打印单
- 页面：A4
- 页边距：上 4cm
- 第一页：发票图片（占满页面）
- 第二页：用餐信息（四号字，居中）

## 🛠️ 依赖安装

```bash
pip install pdf2image python-docx pillow pdfplumber pdftotext --break-system-packages
```

## ⚠️ 注意事项

1. PDF 发票必须放在 `reimbursement/` 目录
2. 开票日期取第一张发票的日期
3. 姓名支持多种分隔符（`、`，`,`, 空格，中文逗号 `，`）
4. 用餐金额自动向上取整到 50 的倍数

## 🔧 开发工具

### 分析 docx 生成模板

```bash
python3 scripts/analyze_docx.py \
    /path/to/your/template.docx \
    /path/to/output_template.json
```

### 从 JSON 数据填写模板

```bash
python3 scripts/fill_from_template.py \
    -i template.docx \
    -o output.docx \
    -t template_config.json \
    -d data.json
```

## 📝 更新日志

- **2026-03-12**: 规范化目录结构，脚本移至 `scripts/`，模板移至 `templates/`
- **2026-03-12**: 修复姓名解析，支持中文逗号 `，` 分隔符
- **2026-03-11**: 初始版本
