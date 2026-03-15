# Environment Setup Instructions

## 系统依赖安装指南

要在本地环境中顺利使用知识图谱抽取技能，需要安装以下依赖：

### Python 环境依赖

```bash
pip install openpyxl pandas pandoc pdfplumber python-docx
```

### 系统工具依赖

```bash  
# Ubuntu/Debian
apt-get update && apt-get install -y pandoc libreoffice unoconv

# CentOS/RHEL/Fedora
yum install -y pandoc libreoffice
# 或者使用 dnf
dnf install -y pandoc libreoffice

# macOS
brew install pandoc --cask  # 使用 Homebrew
```

### 验证依赖

在启动技能前验证环境:

```bash
# 验证 Python 包
python -c "import openpyxl, pandas, pdfplumber, docx; print('✅ Python dependencies OK')"

# 验证 pandoc
pandoc --version
# 输出应为版本信息

# 验证 LibreOffice (用于 docx 转换)
soffice --version  
```

---

## OpenCode 环境配置

### 1. 安装路径配置

技能将安装到:
```bash
~/.agents/skills/knowledge-graph-extractor/
```

### 2. 验证技能注册

安装后使用以下命令验证是否正确注册:

```bash
# 列出所有可用技能
ls -la ~/.agents/skills/ | grep -i graph
# 应能看到 knowledge-graph-extractor 目录
```

### 3. 测试运行验证

```bash
cd ~/.agents/skills/knowledge-graph-extractor/
ls -la scripts/
# 应能看到 extract_knowledge_graph.py 文件
```

---

## 权限设置

确保脚本具有执行权限:

```bash
chmod +x ~/.agents/skills/knowledge-graph-extractor/scripts/extract_knowledge_graph.py
```

或者运行:

```bash  
cd ~/.agents/skills/knowledge-graph-extractor/
find . -name "*.py" -exec chmod +x {} \;
```

---

## 文件路径规范

### 输入/输出路径约定

```bash
输入: 
- 任意目录下的 docx/pdf 文件
  /任意/路径/document.docx

模板:
- 固定模板: assets/template.xlsx

输出:  
- 结果文件: 任意路径/output.[xlsx|csv]
  /output/path/result.xlsx
```

## 错误排查

### 常见错误处理

**错误**: `Command 'pandoc' not found`
- 解决: `apt-get install pandoc` 或 `brew install pandoc`

**错误**: `ModuleNotFoundError: No module named 'openpyxl'`  
- 解决: `pip install openpyxl`

**错误**: `Permission denied: 'scripts/extract_knowledge_graph.py'`
- 解决: `chmod +x scripts/extract_knowledge_graph.py`

**错误**: `Could not read xlsx template A1 cell`
- 解决: 检查 template.xlsx 是否为合法 Excel 格式，A1 单元格必须存在

---

## 环境变量配置 (可选)

为方便识别，推荐设置以下环境变量:

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export KNOWLEDGE_GRAPH_SKILL_PATH="$HOME/.agents/skills/knowledge-graph-extractor"
export PATH="$PATH:$KNOWLEDGE_GRAPH_SKILL_PATH/scripts"
```

重启终端使其生效:
```bash
# for bash
source ~/.bashrc

# for zsh  
source ~/.zshrc
```

然后可直接运行:
```bash
extract_knowledge_graph.py --source doc.docx --template assets/template.xlsx --output output.xlsx
```