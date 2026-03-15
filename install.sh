#!/bin/bash

echo "==============================================="
echo "   文档知识图谱结构化抽取技能 (V1.0.0)"
echo "==============================================="
echo ""

echo "正在安装技能到 OpenCode 环境..."

mkdir -p ~/.agents/skills/knowledge-graph-extractor/

cp SKILL.md ~/.agents/skills/knowledge-graph-extractor/
cp skill.json ~/.agents/skills/knowledge-graph-extractor/
cp -r scripts/ ~/.agents/skills/knowledge-graph-extractor/
cp -r references/ ~/.agents/skills/knowledge-graph-extractor/
cp -r assets/ ~/.agents/skills/knowledge-graph-extractor/
cp -r examples/ ~/.agents/skills/knowledge-graph-extractor/

echo "✅ 技能文件已复制到 ~/.agents/skills/knowledge-graph-extractor/"
echo ""
echo "💡 使用说明："
echo "   - 运行脚本: python scripts/extract_knowledge_graph.py"
echo "   - 输出格式: 符合 A-G列树状结构，H-I-J列关系格式"
echo "   - 配置模板: assets/template.xlsx"
echo ""
echo "📖 详细文档请查看 SKILL.md 文件"
echo ""
echo "✨ 安装完成！技能已准备就绪。"