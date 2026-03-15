# 部署说明 (Deployment Guide)

## 🚀 快速部署

### 选项1：直接安装 (推荐)
```bash
# 1. 克隆到 OpenCode 技能目录
mkdir -p ~/.agents/skills/
git clone https://github.com/flyboat403/knowledge-graph-extraction-skill.git ~/.agents/skills/knowledge-graph-extractor

# 2. 验证安装
test -f ~/.agents/skills/knowledge-graph-extractor/SKILL.md && echo "✅ 安装成功" || echo "❌ 安装失败"
```

### 选项2：使用脚本安装
```bash
# 运行安装脚本 (来自仓库根目录)
bash INSTALL.sh
```

---

## 🧩 完整组件部署

### 1. 核心文件结构
确保以下目录结构完整部署到 `~/.agents/skills/knowledge-graph-extractor/`:

```bash
knowledge-graph-extractor/
├── SKILL.md                    # 核心技能定义
├── skill.json                  # Coze 兼容格式
├── scripts/
│   └── extract_knowledge_graph.py   # 抽取主引擎
├── references/
│   ├── output-format.md        # 输出格式规范
│   └── cognitive-levels.md     # 认知层级定义
├── assets/
│   └── template.xlsx           # Excel输出模板
├── examples/
│   ├── input/                  # 输入示例  
│   └── output/                 # 输出示例
└── README.md                   # 使用说明
```

### 2. 验证部署完整性
```bash
# 检查必要文件是否存在
for file in SKILL.md scripts/extract_knowledge_graph.py assets/template.xlsx; do
  if [[ -f "$HOME/.agents/skills/knowledge-graph-extractor/$file" ]]; then
    echo "✅ $file - 已存在"
  else
    echo "❌ $file - 缺失"
  fi
done
```

### 3. 依赖环境检查
```bash
# 验证必要命令和工具
missing_deps=()
for cmd in "python3" "pandoc"; do
  if ! command -v "$cmd" &> /dev/null; then
    missing_deps+=("$cmd") 
  fi
done

if [ ${#missing_deps[@]} -gt 0 ]; then
  echo "⚠️ 缺失依赖: ${missing_deps[*]}"
  echo "请运行: apt-get install pandoc"  # 针对 ubuntu
else
  echo "✅ 依赖检查通过"
fi

# 验证 Python 库
pip list | grep -E "(openpyxl|pandas|pdfplumber|python-docx)" | wc -l
# 输出应该是 4 (四个包都存在)
```

---

## ⚙️ 环境参数配置

### Python 依赖安装
```bash
pip install openpyxl pandas pdfplumber python-docx
```

### 可选配置 (用于 docx 解析增强)
```bash
# Ubuntu
sudo apt-get update && sudo apt-get install -y pandoc libreoffice

# CentOS/Fedora  
sudo yum install -y pandoc libreoffice

# macOS
brew install pandoc --cask
```

---

## 🧪 安装验证测试

### 1. 基础功能测试
```bash
cd ~/.agents/skills/knowledge-graph-extractor

# 检查脚本是否可执行
python3 scripts/extract_knowledge_graph.py --help
```

### 2. 示例抽取测试
```bash
# 使用本仓库测试文件
python3 scripts/extract_knowledge_graph.py \
  --source examples/input/办公软件应用课程标准.pdf \
  --template assets/template.xlsx \
  --output test_extraction.xlsx \
  --dry-run
```

### 3. 输出格式验证
```bash
# 检查生成的文件格式是否正确
file test_extraction.xlsx
# 输出应显示 Excel 文件类型
```

---

## 🔄 更新技能版本

```bash
# 重新拉取最新版本
cd ~/.agents/skills/knowledge-graph-extractor
git pull origin main

# 验证更新后的文件
ls -la
```

---

## 🧯 故障排查

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|  
| 脚本无权限执行 | 缺失执行权限 | `chmod +x scripts/extract_knowledge_graph.py` |
| 找不到 pandoc 命令 | 未安装 pandoc | `apt-get install pandoc` |
| xlsx 模板无法读取 | 模板损坏或格式不符 | 检查 `assets/template.xlsx` 存在性 |
| 无法导入 | 前置依赖包缺失 | `pip install openpyxl pandas pdfplumber` |
| SKILL.md 格式错误 | frontmatter 缺失或错误 | 验证首3行包含正确的YAML frontmatter |

---

## 📤 卸载技能

```bash
# 删除技能目录
rm -rf ~/.agents/skills/knowledge-graph-extractor
```