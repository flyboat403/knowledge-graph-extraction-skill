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
REQUIRED_CMD=("python3" "pip" "git")
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

echo "  所有依赖已找到: Python3, Pip, Git"
echo ""

# 检查 Python 包状态
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

# 确定脚本执行目录（根据当前工作区域）
SRC_DIR="/root/kg_skill"  # 假设在技能开发目录运行
if [ ! -d "$SRC_DIR" ]; then
    SRC_DIR="."  # 否则使用当前目录
fi

echo "✓ 准备安装技能文件..."
echo "  源目录: $SRC_DIR"
TARGET_DIR="$HOME/.agents/skills/knowledge-graph-extractor"
echo "  目标目录: $TARGET_DIR"
echo ""

# 创建目标技能目录
mkdir -p "$TARGET_DIR"

# 复制技能文件到目标位置
echo "✓ 复制技能文件..."
cp "$SRC_DIR/SKILL.md" "$TARGET_DIR/" 2>/dev/null || { echo "错误: 未找到 SKILL.md"; exit 1; }
cp "$SRC_DIR/skill.json" "$TARGET_DIR/" 2>/dev/null || { echo "错误: 未找到 skill.json"; exit 1; }

# 复制子目录
cp -r "$SRC_DIR/scripts/." "$TARGET_DIR/scripts/" 2>/dev/null || mkdir -p "$TARGET_DIR/scripts/"
cp -r "$SRC_DIR/references/." "$TARGET_DIR/references/" 2>/dev/null || mkdir -p "$TARGET_DIR/references/"
cp -r "$SRC_DIR/assets/." "$TARGET_DIR/assets/" 2>/dev/null || mkdir -p "$TARGET_DIR/assets/"
cp -r "$SRC_DIR/examples/." "$TARGET_DIR/examples/" 2>/dev/null || mkdir -p "$TARGET_DIR/examples/"

echo "✅ 技能文件安装到: $TARGET_DIR"
echo ""

# 验证安装
echo "✓ 验证安装完整性..."
CHECK_FILES=(
    "$TARGET_DIR/SKILL.md"
    "$TARGET_DIR/skill.json"
    "$TARGET_DIR/scripts/extract_knowledge_graph.py"
    "$TARGET_DIR/references/output-format.md"
    "$TARGET_DIR/references/cognitive-levels.md"
    "$TARGET_DIR/assets/template.xlsx"
    "$TARGET_DIR/examples/input/placeholder.txt"
    "$TARGET_DIR/examples/output/OUTPUT_EXAMPLES.md"
)

ALL_GOOD=true
for file in "${CHECK_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file 存在"
    else
        echo "  ❌ $file 不存在"
        ALL_GOOD=false
    fi
done
echo ""

if [ "$ALL_GOOD" = false ]; then
    echo "❌ 安装未完整完成。请检查上述文件是否正确复制。"
    exit 1
fi

# 最终确认信息
echo "==============================================="
echo "✅ 技能安装成功！"
echo ""
echo "💡 现在可以使用知识图谱抽取技能"
echo ""
echo "📁 安装位置: $TARGET_DIR"
echo ""
echo "🔧 运行示例:"
echo "   cd $TARGET_DIR"
echo "   python scripts/extract_knowledge_graph.py \\"
echo "     --source examples/input/doc.pdf \\"
echo "     --template assets/template.xlsx \\"
echo "     --output output_results.xlsx"
echo ""
echo "📖 使用说明: 请查看 $TARGET_DIR/SKILL.md"
echo ""
echo "✨ 就绪！知识图谱结构化抽取技能已准备就绪。"
echo "==============================================="