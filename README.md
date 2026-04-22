# 文档知识图谱结构化抽取

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

从 PDF/Word 文档中自动提取层次化知识节点，标注认知层级与语义关系，输出可直接导入知识图谱系统的结构化文件。

## ✨ 功能特性

- **📚 层次化知识抽取** - 支持最多 7 级知识节点层次结构
- **🧠 认知层级标注** - 基于布鲁姆分类法（记忆/理解/应用/分析/评价/创造）
- **🔗 语义关系识别** - 自动识别前置、后置、关联关系
- **🎯 教学目标生成** - LLM 自动生成具体可衡量的教学目标
- **📊 多格式输出** - 支持 Excel 和 CSV 格式
- **✅ 格式验证** - 自动验证树状结构完整性和数据规范性

## 🏗️ 技术架构

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   文档解析    │───→│  LLM 语义抽取 │───→│   格式验证    │───→│  Excel 生成  │
│   (脚本)     │    │   (LLM)      │    │   (脚本)     │    │   (脚本)     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
      │                    │                   │                   │
      ▼                    ▼                   ▼                   ▼
  提取纯文本          语义理解+推理        验证格式约束         生成标准输出
  解析模板           生成节点+关系        修复格式错误
```

## 📦 安装

### 依赖项

```bash
pip install openpyxl python-docx pdfplumber
```

### 克隆仓库

```bash
git clone https://github.com/flyboat403/knowledge-graph-extraction-skill.git
cd knowledge-graph-extraction-skill
```

## 🚀 快速开始

### 步骤 1: 提取文档内容

```bash
python scripts/extract_knowledge_graph.py \
  --source document.docx \
  --extract-text \
  --output document_content.txt
```

### 步骤 2: LLM 知识抽取

将文档内容传递给 LLM（使用 `prompts/extraction_prompt.md` 中的 Prompt 模板），获取 JSON 格式的知识节点。

### 步骤 3: 生成 Excel 文件

```bash
python scripts/extract_knowledge_graph.py \
  --json knowledge_nodes.json \
  --template template.xlsx \
  --output output.xlsx
```

## 📋 输出格式

### 列结构

| 列范围 | 用途 | 说明 |
|--------|------|------|
| A-G 列 | 知识点层级 | 每行一个知识点，列位置表示层级 |
| H 列 | 前置知识点 | 学习当前知识点前需先掌握的知识 |
| I 列 | 后置知识点 | 学习当前知识点后可学习的知识 |
| J 列 | 关联知识点 | 相关但不构成前置/后置关系的知识 |
| K 列 | 标签 | 重点/难点/考点/课程思政 |
| L 列 | 认知维度 | 记忆/理解/应用/分析/评价/创造 |
| M 列 | 知识分类 | 事实性/概念性/程序性/元认知 |
| N 列 | 教学目标 | 学习后应达成的能力或理解 |
| O 列 | 知识点说明 | 简要描述 |

### 层级定义

| Level | 对应列 | 典型内容 | 示例 |
|-------|--------|----------|------|
| 1 | A 列 | 课程/学科名称 | 土木水利类职业技能考试 |
| 2 | B 列 | 模块/单元 | 专业知识(应知) |
| 3 | C 列 | 章节/部分 | 土木工程力学 |
| 4 | D 列 | 知识主题 | 力和受力图 |
| 5 | E 列 | 具体知识点 | 约束与约束反力 |
| 6 | F 列 | 知识点细分 | 接触触电的类型 |
| 7 | G 列 | 原子内容 | 单相触电的具体特征 |

### 教学目标生成规则

| 层级 | 是否需要教学目标 | 原因 |
|------|-----------------|------|
| Level 1-3 | ❌ 不需要 | 结构容器，非具体学习内容 |
| Level 4-7 | ✅ **必填** | 学生实际学习的内容 |

**教学目标句式模板：**

| 认知层级 | 推荐句式 | 示例 |
|----------|---------|------|
| 记忆 | 能够说出/列举... | "能够说出电阻的单位及换算关系" |
| 理解 | 能够解释/说明... | "能够解释欧姆定律的物理意义" |
| 应用 | 能够使用/操作... | "能够使用万用表测量电阻值" |
| 分析 | 能够分析/比较... | "能够分析串联与并联电路的区别" |
| 评价 | 能够选择/判断... | "能够选择合适的电阻类型" |
| 创造 | 能够设计/创建... | "能够设计符合要求的简单电路" |

## 📁 项目结构

```
knowledge-graph-extraction-skill/
├── README.md                    # 项目说明文档
├── SKILL.md                     # 技能详细文档
├── skill.json                   # 技能元数据
├── scripts/
│   └── extract_knowledge_graph.py   # 主脚本
├── prompts/
│   ├── extraction_prompt.md     # 知识抽取 Prompt 模板
│   └── relation_prompt.md       # 关系推理 Prompt 模板
├── references/
│   ├── output-format.md         # 输出格式规范
│   └── cognitive-levels.md      # 认知层级定义
└── examples/
    ├── template-knowledge-graph.xlsx          # 知识图谱 Excel 模板
    └── example-curriculum-office-software.pdf # 示例课程标准文档
```

## 🔧 命令行参数

```bash
python scripts/extract_knowledge_graph.py [OPTIONS]

选项:
  --json FILE       LLM 输出的 JSON 文件路径
  --source FILE     源文档路径 (docx/pdf)
  --extract-text    提取文档文本供 LLM 处理
  --template FILE   xlsx 模板路径
  --output FILE     输出文件路径
  --dry-run         仅解析模板，不生成输出
```

## 📊 示例输出

```json
[
  {
    "name": "土木工程力学",
    "level": 3,
    "cognitive_level": "应用",
    "category": "概念性",
    "pre_requisites": [],
    "related": ["土木工程材料", "土木工程测量"],
    "tags": "重点",
    "objective": "",
    "description": "土木工程力学基础知识"
  },
  {
    "name": "力和受力图",
    "level": 4,
    "cognitive_level": "理解",
    "category": "概念性",
    "pre_requisites": [],
    "related": ["平面力系的合成与平衡"],
    "tags": "重点",
    "objective": "能够理解力及力系的概念与性质，掌握约束反力的画法和受力图的绘制方法",
    "description": "力学基础概念与受力分析"
  }
]
```

## ✅ 格式验证

脚本自动验证以下约束：

- ✅ 每行只有一个知识点（A-G 列）
- ✅ 树状结构完整性（无断层）
- ✅ 认知维度为单选值
- ✅ 知识点分类为单选值
- ✅ 分隔符使用英文分号 `;`
- ✅ Level 4-7 节点有教学目标

## 🚫 Anti-Patterns（禁止）

| 错误 | 正确 |
|------|------|
| 一行填写多个知识点 | 每行只填一个知识点 |
| 使用中文分号 `；` | 使用英文分号 `;` |
| 认知维度填多个值 | 认知维度为单选 |
| 层级跳跃（A→C） | 层级连续（A→B→C） |

## 🔗 兼容性

**支持导入平台：**
- Neo4j
- Apache Jena
- 超星知识图谱
- 泛雅平台

**支持文档格式：**
- `.docx` (Microsoft Word)
- `.pdf` (PDF 文档)

## 📖 参考资料

- [布鲁姆教育目标分类法](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)
- [Neo4j 图数据库](https://neo4j.com/)
- [Apache Jena](https://jena.apache.org/)

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ for knowledge graph extraction**