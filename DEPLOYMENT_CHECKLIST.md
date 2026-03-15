# 🧪 技能部署验证脚本

这是一个简明的验证脚本，帮助确认知识图谱抽取技能在目标环境中正确部署：

---

## ✅ 部署验证步骤

### 1. 检查技能目录完整性
```bash
# 验证核心文件存在
[[ -f ~/.agents/skills/knowledge-graph-extractor/SKILL.md ]] && echo "✅ SKILL.md 存在"
[[ -f ~/.agents/skills/knowledge-graph-extractor/scripts/extract_knowledge_graph.py ]] && echo "✅ 脚本文件存在"
[[ -f ~/.agents/skills/knowledge-graph-extractor/assets/template.xlsx ]] && echo "✅ 模板文件存在"
[[ -d ~/.agents/skills/knowledge-graph-extractor/references ]] && echo "✅ 参考目录存在"
[[ -d ~/.agents/skills/knowledge-graph-extractor/examples ]] && echo "✅ 示例目录存在"
```

### 2. 检查 Python 依赖
```bash
# 检查必要包
python -c "import openpyxl, pandas, pdfplumber, docx; print('✅ Python 依赖可用')"
```

### 3. 验证脚本可执行性
```bash  
# 检查帮助信息
cd ~/.agents/skills/knowledge-graph-extractor/
python scripts/extract_knowledge_graph.py --help
```

---

## 📋 功能验证清单

- [ ] ✅ 层级结构抽取 (A-G列树状约束)
- [ ] ✅ 认知维度自动标注 (L列 6级: 记忆/理解/应用/分析/评价/创造)  
- [ ] ✅ 知识点分类标注 (M列 4类: 事实性/概念性/程序性/元认知)
- [ ] ✅ 三元关系生成 (H:前置/I:后置/J:关联)
- [ ] ✅ 标签自动生成 (K列: 重点/难点/考点)
- [ ] ✅ CSV/Excel 输出格式
- [ ] ✅ 输出兼容 Neo4j/Jena 导入  
- [ ] ✅ 约束验证 (格式/层级/关系)

---

## 🧠 简明使用验证

快速测试抽取功能：
```bash
# 创建测试文档内容
echo "示例测试文档内容

一级知识：文档处理基础
  二级知识：文本识别技术
    三级知识：OCR基本知识
      为了应用OCR技术，首先需要了解文本识别基础知识

二级知识：结构化分析  
  三层知识：层次化知识节点
  三层知识：认知层级标注" > /tmp/test_doc.txt

# 使用示例文档测试抽取功能（如果存在的话）
cd ~/.agents/skills/knowledge-graph-extractor/
# ls -la examples/  # 检查是否有测试文档
```

如果以上验证皆通过，技能部署成功！🎉  
现在你可以使用知识图谱技能抽取任意文档中的层次化知识点并生成结构化图谱数据了。