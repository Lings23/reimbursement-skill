# 加班餐费报销工具 - 安装指南

## 📋 系统要求

- Python 3.8+
- poppler-utils（PDF 转图片工具）

---

## 🔧 安装步骤

### 步骤 1: 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils python3-pip
```

**macOS:**
```bash
brew install poppler
```

**CentOS/RHEL:**
```bash
sudo yum install -y poppler-utils
```

**验证安装:**
```bash
pdftotext -v
```

---

### 步骤 2: 安装 Python 依赖

```bash
cd skills/reimbursement-tool
pip install -r requirements.txt
```

**或者使用虚拟环境:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

### 步骤 3: 验证安装

```bash
# 检查脚本是否可运行
python3 scripts/main.py --help

# 应该显示用法信息
```

---

### 步骤 4: 创建发票目录

```bash
# 在 workspace 根目录创建发票目录
mkdir -p ../../reimbursement
```

---

### 步骤 5: 测试运行

```bash
# 放入测试发票 PDF 到 reimbursement/ 目录
# 然后运行：
python3 scripts/main.py "[加班餐报销] 加班事由：测试 加班人员：张三"

# 检查输出文件
ls -lh ../../*.docx
```

---

## ⚙️ 配置

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `REIMBURSE_INVOICE_DIR` | 发票 PDF 目录 | `<workspace>/reimbursement/` |
| `REIMBURSE_OUTPUT_DIR` | 输出文件目录 | `<workspace>/` |

### 命令行参数

```bash
python3 scripts/main.py "[加班餐报销] ..." \
    --invoice-dir /path/to/invoices \
    --output-dir /path/to/output \
    --input-file input.txt
```

---

## 🐛 常见问题

### 1. `pdftotext: command not found`

**解决:** 安装 poppler-utils（见步骤 1）

### 2. `ModuleNotFoundError: No module named 'docx'`

**解决:** 
```bash
pip install -r requirements.txt
```

### 3. 中文文件名乱码

**解决:** 确保系统 locale 设置为 UTF-8
```bash
locale -a  # 查看支持的 locale
export LANG=zh_CN.UTF-8
```

### 4. PDF 无法提取文字

**原因:** 扫描件或图片型 PDF

**解决:** 使用 OCR 工具预处理 PDF，或联系开票方获取电子版

---

## 📦 卸载

```bash
# 删除技能目录
rm -rf skills/reimbursement-tool

# 删除 Python 包（如果安装了）
pip uninstall reimbursement-skill
```

---

## 📄 许可证

MIT License - 见 LICENSE 文件
