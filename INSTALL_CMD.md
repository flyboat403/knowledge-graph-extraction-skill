```bash
#!/bin/sh
# 一键安装文档知识图谱抽取技能
# 用法: bash install_skill.sh [目标目录]

SKILL_DIR="${1:-$HOME/.agents/skills/knowledge-graph-extractor}"

echo "Installing knowledge graph extraction skill to: $SKILL_DIR"

# 创建目录
mkdir -p "$SKILL_DIR"
mkdir -p "$SKILL_DIR/scripts" 
mkdir -p "$SKILL_DIR/references"
mkdir -p "$SKILL_DIR/assets"
mkdir -p "$SKILL_DIR/examples"

# 检查依赖
for dep in python3 pandoc; do
  if ! command -v $dep >/dev/null 2>&1; then
    echo "Error: $dep is required but not installed" >&2
    exit 1
  fi
done

# 复制文件 (从当前项目目录)
[[ -f SKILL.md ]] && cp SKILL.md "$SKILL_DIR/"
[[ -f skill.json ]] && cp skill.json "$SKILL_DIR/"
[[ -f scripts/extract_knowledge_graph.py ]] && cp scripts/extract_knowledge_graph.py "$SKILL_DIR/scripts/"
[[ -f references/output-format.md ]] && cp references/output-format.md "$SKILL_DIR/references/"
[[ -f references/cognitive-levels.md ]] && cp references/cognitive-levels.md "$SKILL_DIR/references/"
[[ -f assets/template.xlsx ]] && cp assets/template.xlsx "$SKILL_DIR/assets/"
[[ -f examples/input/README.md ]] && cp examples/input/README.md "$SKILL_DIR/examples/"
[[ -f README.md ]] && cp README.md "$SKILL_DIR/"

# 设置权限
chmod +x "$SKILL_DIR/scripts/extract_knowledge_graph.py" 2>/dev/null

# 验证安装
if [[ -f "$SKILL_DIR/SKILL.md" ]] && [[ -f "$SKILL_DIR/scripts/extract_knowledge_graph.py" ]]; then
  echo "✅ Installation successful!"
  echo "💡 Usage: cd $SKILL_DIR && python scripts/extract_knowledge_graph.py --source doc.docx --template assets/template.xlsx --output output.xlsx"
else
  echo "❌ Installation failed!" >&2  
  exit 1
fi
```