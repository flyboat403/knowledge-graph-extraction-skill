#!/bin/bash
# OpenCode 文档知识图谱抽取技能安装脚本

set -e  # 任何命令失败时退出

echo "==============================================="
echo "  文档知识图谱抽取技能 (Document Knowledge Graph Extractor)"
echo "  技能版本: 1.0.0"
echo "==============================================="
echo ""

# 检查系统依赖
echo "✓ 检查系统依赖..."
REQUIRED_CMD=("python3" "pip" "git" "pandoc")
MISSING_CMD=()

for cmd in "${REQUIRED_CMD[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        MISSING_CMD+=("$cmd")
    fi
done

if [ ${#MISSING_CMD[@]} -ne 0 ]; then
    echo "❌ 错误: 以下命令未找到: ${MISSING_CMD[*]}"
    echo "  请先安装相应的依赖项"
    exit 1
fi

echo "  所有依赖已找到: Python3, Pip, Git, Pandoc"
echo ""

# 检查 Python 包  
echo "✓ 验证 Python 依赖..."
PYTHON_PKG=("openpyxl" "pandas" "pdfplumber" "python-docx")

MISSING_PYTHONPKG=()
for pkg in "${PYTHON_PKG[@]}"; do
    if python3 -c "import $pkg" &> /dev/null; then
        echo "  - $pkg: 已安装"
    else
        MISSING_PYTHONPKG+=("$pkg")
        echo "  - $pkg: 需要安装"
    fi  
done

if [ ${#MISSING_PYTHONPKG[@]} -ne 0 ]; then
    echo ""
    echo "即将安装缺失的 Python 包: ${MISSING_PYTHONPKG[*]}"
    pip install "${MISSING_PYTHONPKG[@]}"
    echo "✅ Python 依赖安装完成"
fi
echo ""

# 当前工作目录（作为源目录）  
SRC_DIR="."
echo "✓ 准备安装技能文件..."
echo "  源目录: $SRC_DIR"
TARGET_DIR="$HOME/.agents/skills/knowledge-graph-extractor"  
echo "  目标目录: $TARGET_DIR"
echo ""

# 创建目标技能目录
mkdir -p "$TARGET_DIR"

# 复制技能文件到目标位置
echo "✓ 复制技能文件..."

cp "$SRC_DIR/SKILL.md" "$TARGET_DIR/" 2>/dev/null || { 
    # 如果当前目录没有 SKILL.md，则从 /root/kg_skill 目录复制
    cp "/root/kg_skill/SKILL.md" "$TARGET_DIR/" || { echo "错误: 未找到 SKILL.md"; exit 1; }
}

cp "$SRC_DIR/skill.json" "$TARGET_DIR/" 2>/dev/null || { 
    cp "/root/kg_skill/skill.json" "$TARGET_DIR/" || { echo "错误: 未找到 skill.json"; exit 1; }
}

# 复制子目录（如有，否则复制固定位置）
cp -r "$SRC_DIR/scripts/." "$TARGET_DIR/scripts/" 2>/dev/null || {
     mkdir -p "$TARGET_DIR/scripts/" && cp -r "/root/kg_skill/scripts/." "$TARGET_DIR/scripts/" 2>/dev/null
}
cp -r "$SRC_DIR/references/." "$TARGET_DIR/references/" 2>/dev/null || {
     mkdir -p "$TARGET_DIR/references/" && cp -r "/root/kg_skill/references/." "$TARGET_DIR/references/" 2>/dev/null  
}
cp -r "$SRC_DIR/assets/." "$TARGET_DIR/assets/" 2>/dev/null || {
     mkdir -p "$TARGET_DIR/assets/" && cp -r "/root/kg_skill/assets/." "$TARGET_DIR/assets/" 2>/dev/null
}
cp -r "$SRC_DIR/examples/." "$TARGET_DIR/examples/" 2>/dev/null || {
      mkdir -p "$TARGET_DIR/examples/" && cp -r "/root/kg_skill/examples/." "$TARGET_DIR/examples/" 2>/dev/null
}

echo "✅ 技能文件已安装到: $TARGET_DIR"
echo ""

# 验证安装
echo "✓ 验证安装完整性..."

# 检查主要文件是否存在  
check_file() {
    if [ -f "$1" ]; then
        echo "  ✅ $2 存在"
        return 0
    else
        echo "  ❌ $2 不存在"
        return 1
    fi
}

files_check_status=true
check_file "$TARGET_DIR/SKILL.md" "SKILL.md" || files_check_status=false
check_file "$TARGET_DIR/scripts/extract_knowledge_graph.py" "主脚本" || files_check_status=false
check_file "$TARGET_DIR/references/output-format.md" "输出格式规范" || files_check_status=false
check_file "$TARGET_DIR/assets/template.xlsx" "模板文件" || files_check_status=false
echo ""

if [ "$files_check_status" = false ]; then
    echo "❌ 安装未完整完成。请检查上述文件是否正确复制。" 
    exit 1
fi

# 设置执行权限
chmod +x "$TARGET_DIR/scripts/extract_knowledge_graph.py" 2>/dev/null || echo "  注：主脚本可能已有执行权限"
echo "  文件权限已设置: extract_knowledge_graph.py"

# 最终确认信息
echo "==============================================="
echo "✅ 技能安装成功！"
echo ""
echo "💡 现在可以使用知识图谱结构化抽取技能"
echo ""
echo "📁 安装位置: $TARGET_DIR"
echo ""
echo "🔧 使用示例:"
echo "   cd $TARGET_DIR"
echo "   python scripts/extract_knowledge_graph.py \\"
echo "     --source examples/input/sample_document.docx \\"
echo "     --template assets/template.xlsx \\"
echo "     --output output_results.xlsx"
echo ""
echo "📖 使用说明: 请查看 $TARGET_DIR/ QUICKSTART.md"
echo ""  
echo "✨ 技能已准备就绪！知识图谱抽取工具已安装完成。"
echo "==============================================="