# 💡 使用说明

## 🚀 快速开始
```bash
# 安装到 OpenCode:
opencode skills add knowledge-graph-extractor

# 或克隆安装:
git clone https://github.com/flyboat403/knowledge-graph-extraction-skill.git ~/.agents/skills/knowledge-graph-extractor
```

## 📁 目录结构
```
ROOT/
├── SKILL.md                            #  skill核心定义  
├── scripts/
│   └── extract_knowledge_graph.py     # 抽取引擎
├── assets/
│   └── template.xlsx                  # 输出模板
├── references/                        # 格式规范文档
│   ├── output-format.md
│   └── cognitive-levels.md            
├── examples/                          # 示例数据  
│   ├── input/
│   └── output/
├── README.md                          # 项目说明  
├── QUICKSTART.md                      # 快速入门
└── BEST_PRACTICES.md                  # 最佳实践
```

## 📤 输出格式 (A-O列)

| 列 | 含义 | 约束 | 示例 |
|----|------|------|------|
| **A-G列** | 知识点层级 | 每行仅1非空 | 树状结构，一级→七级 |
| **H列** | 前置知识 | 英文`分号`分隔 | `电阻知识;电流知识` |
| **I列** | 后置知识 | H列自动反向 | `欧姆定律;电位知识` |
| **J列** | 关联知识 | 英文`分号`分隔 | `电压概念;功率概念` |
| **K列** | 标签 | 分号分隔 | `重点;考点;难点` |
| **L列** | 认知维度 | 单选值 | `记忆/理解/应用/分析/评价/创造` |
| **M列** | 知识分类 | 単选值 | `'亊实性/概念性/程序性/元认知` |
| **N-O列** | 教学目标/说明 | 自由文本 | 教学目的说明 |

## ⚠️ 关键约束  

- ✅ 每行只填写**一个知识点**(A-G列) 
- ✅ 关系分隔符使用英文分号`;`
- ✅ L/M列为**单选值**  
- ✅ 保留所有模板列(A-O)
- ✅ 前后关系对称(确保一致性)
- ✅ 输出可导入Neo4j/Jena

## 🔧 核心功能命令

```bash
cd ~/.agents/skills/knowledge-graph-extractor/

# 基本抽取
python scripts/extract_knowledge_graph.py \
  --source input_document.docx \
  --template assets/template.xlsx \
  --output result.xlsx

# 验证关系结构  
python -c "
import pandas as pd; 
df = pd.read_csv('result.csv');
for i,row in df.iterrows(): 
   if sum(1 for c in 'ABCDEFG' if row.get(c,'')) != 1: 
      print(f'格式错误@行{i+3}')
"  
```

## 🧠 认知层级标注

| 动词类型 | 维度 | 教育能力 |
|----------|------|----------|
| **知道/了解/记忆** | 记忆 | 识别、回忆 |
| **理解/阐明/解释** | 理解 | 诠释、举例 |  
| **掌握/运用/使用** | 应用 | 在新情境中应用 |
| **分析/比较/辨别** | 分析 | 拆解、剖析关系 |
| **评价/判断/选择** | 评价 | 做出判断、论证 |
| **设计/规划/构建** | 创造 | 创新、产生新方案 |  

## 🔁 关系分类说明

- **H(前置)**: 学习当前前需先掌握 (如A→B, 则A是B的前置) 
- **I(后置)**: 自动生成前置关系的反向（H的逆）  
- **J(关联)**: 相关但不构成依赖 (如C↔D, 并列概念/相似对比)

## 🎓 应用场景

- **课程标准分析**: 抽取教学大纲中的知识点层级
- **考试内容整理**: 为考试大纲构建知识图谱 
- **培训内容组织**: 技能点关系分析与路径规划
- **教育资源整理**: 为教学系统结构化内容组织  

---

**Powered by Sisyphus & OpenCode** 