# 文档知识图谱结构化抽取技能

从文档中抽取层次化知识节点，输出可导入知识图谱系统的结构化数据。

## 功能特性

- **层次化抽取**：从 docx/pdf 中提取 6+ 级知识点层级
- **认知标注**：自动识别认知层级（记忆/理解/应用/分析/评价/创造） 
- **关系生成**：自动生成前置/后置/关联关系
- **格式支持**：输出 CSV/Excel 兼容 Neo4j/Jena 导入
- **反模式指导**：详尽的防错指南

## 输入要求

- **源文档**：`docx` 或 `pdf` 格式
- **模板**：`xlsx` 格式，A1单元格包含格式规则

## 输出格式

- **层级结构**：A-G 列为层级（每行一知识点）  
- **关系数据**：H-I-J 列（前置/后置/关联）
- **标签分类**：K-O 列（标签/认知/分类/目标/说明）

## 技术实现

### 数据结构规范

系统严格按照以下标准输出数据：

| 列 | 说明 | 业务含义 |
|---|------|----------|
| A-G 列 | 知识点层级结构 | 一级课程→七级具体知识点的树状结构，每行为知识点 |
| H 列 | 前置知识点 | 学习当前知识前需掌握的知识点 |
| I 列 | 后置知识点 | 学完当前知识后可继续学习的知识点 |
| J 列 | 关联知识点 | 与当前知识点相关但非前置/后置的知识点 |
| K 列 | 标签 | 固定标签(重点/难点/考点/课程思政)和自定义标签 |
| L 列 | 认知维度 | 教育维度(记忆/理解/应用/分析/评价/创造) |
| M 列 | 知识分类 | 概念类型(事实性/概念性/程序性/元认知) |
| N-O 列 | 教学目标/知识点说明 | 教学用途和内容说明 |

### 关系生成机制

知识关系基于语义理解而非简单的关键词匹配：

- **前置关系**：如 "电阻知识点" → "欧姆定律" 
- **后置关系**：根据前置关系自动反向生成
- **关联关系**：如 "电压概念" ⮂ "电流概念" (并列但相关)

## 使用方式

### 1. 命令行运行
```bash
python scripts/extract_knowledge_graph.py \
  --source document.docx \
  --template assets/template.xlsx \
  --output output.xlsx
```

### 2. Coze 平台安装
在 Coze 中直接搜索并安装：
- Skill ID: `knowledge_graph_extraction_skill`
- 或从 URL: `https://github.com/flyboat403/knowledge-graph-extraction-skill`

## 目录结构

```
knowledge-graph-extraction-skill/
├── SKILL.md                      # 核心技能定义 (含 name+description)
├── skill.json                    # Coze 平台兼容格式
├── scripts/
│   └── extract_knowledge_graph.py   # 抽取处理引擎
├── references/
│   ├── output-format.md         # 输出格式规范
│   └── cognitive-levels.md      # 认知层级定义
├── assets/
│   └── template.xlsx             # 示例模板文件
├── examples/
│   └── sample_template.xlsx      # 输入示例文件
└── README.md                    # 说明文档
```

## 应用场景

- **教育领域**：从课程标准抽取知识点构建知识图谱
- **研究领域**：教育领域的结构化教学数据分析
- **企业培训**：自动知识图谱构建与导入
- **课程开发**：教学内容的层级化梳理

## 技术约束

- **树状结构**：每行只能填写一个知识点 (A-G列单一填充)
- **层级递进**：A列(一级) → G列(七级) 完整路径  
- **认知维度**：记忆/理解/应用/分析/评价/创造 (单选值)
- **知识分类**：事实性/概念性/程序性/元认知 (单选值)
- **关系互斥**：任两点可仅有一类关系 (前置/后置/关联)

## 质量保障

项目经过充分测试，包括：
- 真实文档抽取验证 (04计算机类.docx, 05电子信息类.docx)
- 格式约束验证 (树状结构/认知标注/关系生成)
- 输出兼容性验证 (Neo4j/Jena导入验证)
- 反模式防护验证 (格式错误预防)

---

## 安装

```bash
# 使用 OpenCode CLI
opencode skills add https://github.com/flyboat403/knowledge-graph-extraction-skill.git

# 或手动安装
git clone https://github.com/flyboat403/knowledge-graph-extraction-skill.git
cd knowledge-graph-extraction-skill
# 遵循 SKILL.md 中的使用指南
```

**Powered by Sisyphus & OpenCode**