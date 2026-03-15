# 文档知识图谱抽取技能 - 使用速查卡
## Document Knowledge Graph Extraction Skill - Quick Reference Card

| **属性** | **值** | **备注** |
|----------|--------|----------|
| 📌 **功能** | 从docx/pdf抽取层次化知识节点 | 7+级知识层级结构 |
| 📥 **输入** | `source.docx/pdf + template.xlsx` | 模版A1单元格含格式要求 |
| 📤 **输出** | `output.xlsx/csv (A-O列)` | 符合图谱导入标准 |
| 🧠 **认知** | 记忆→理解→应用→分析→评价→创造 | 自动识别标注 |
| 🔗 **关系** | 前置(H) / 后置(I) / 关联(J) | 三类语义关系 |

---

### 🔧 快速命令
```bash
# 执行抽取
python scripts/extract_knowledge_graph.py \
  --source document.docx \
  --template assets/template.xlsx \
  --output result.xlsx

# 验证格式  
python -c "
import pandas as pd
df = pd.read_csv('result.csv')  
for i, r in df.iterrows():
  if sum(1 for c in 'ABCDEFG' if r[c]) != 1: 
    print(f'树状格式错误 行{i+2}')
"
```

### 🧩 必须遵守的约束
- **树状结构**: 每行A-G列仅一个知识点 ✅
- **关系分隔符**: 多项用英文`;`分隔 (`知识点A;知识点B`) ✅
- **认知单选**: L列仅填1个值 (`记忆/理解/应用...`) ✅  
- **分类单选**: M列仅填1个值 (`事实性/概念性...`) ✅
- **保留列完整**: 不删除A-O任一列 ✅

### 👨‍🏫 应用场景示例
**教学**: 从《课程标准》抽知识点 → 构建学科知识图谱

**培训**: 从技能大纲构建 → 知识依赖网络