# 文档知识图谱结构化抽取技能

自动化从 Word/PDF 文档抽取层次化知识节点，生成符合知识图谱系统导入要求的结构化数据。

## 🎯 功能特性

### 核心能力
- **层次化抽取**：从 docx/pdf 抽取 7 级以上知识点层级结构
- **认知标注**：自动识别认知层级（记忆→理解→应用→分析→评价→创造）
- **关系生成**：自动生成前置/后置/关联三元关系
- **标准输出**：生成符合 Neo4j/Jena 格式的 CSV/Excel 文件
- **反模式防护**：内置详尽的防错指南和验证约束

### 技术约束
- **树状结构**：每行只填写一个知识点（A-G列区间）
- **关系约束**：H-I-J列关系用英文分号";"隔开  
- **单一选择**：认知维度和分类为单选值
- **完整保留**：模板列结构不可删除

## 📁 目录结构

```
knowledge-graph-extraction-skill/
├── SKILL.md                    # 核心技能定义文件
├── skill.json                  # Coze平台兼容格式
├── scripts/
│   └── extract_knowledge_graph.py   # 核心抽取引擎
├── references/
│   ├── output-format.md        # 输出格式规范
│   └── cognitive-levels.md     # 认知层级定义
├── assets/
│   └── template.xlsx           # 输出模板文件
├── examples/
│   ├── input/                  # 输入示例文档
│   │   ├── 办公软件应用课程标准.pdf
│   │   └── sample_template.xlsx
│   └── output/                 # 输出示例文件
│       ├── sample_extraction_result.csv
│       └── sample_extraction_result.xlsx
├── README.md                   # 项目说明 (此文件)
├── QUICKSTART.md               # 快速入门指南
├── BEST_PRACTICES.md           # 最佳实践指南
└── RELEASE_NOTES.md            # 发布说明
```

## 🚀 快速开始

### 安装
```bash
# 克隆仓库
git clone https://github.com/flyboat403/knowledge-graph-extraction-skill.git

# 或集成到 OpenCode 环境
# 放置 SKILL.md 及相关文件到 ~/.agents/skills/knowledge-graph-extractor/
```

### 使用
```bash
# 直接运行脚本
python scripts/extract_knowledge_graph.py \
  --source 课程标准.docx \
  --template assets/template.xlsx \
  --output output_result.xlsx
```

## 📋 输入输出规范

### 输入要求
- **源文档**：`docx` 或 `pdf` 格式
- **模板文件**：`xlsx` 格式，A1 单元格包含格式规范

### 输出格式 (A-O列)
| 列 | 含义 | 说明 |
|----|------|------|
| A-G | 知识点层级 | 树状结构（每行一个知识点） |
| H | 前置知识点 | 学习当前知识前需掌握 |
| I | 后置知识点 | 学完当前知识后可学习 |
| J | 关联知识点 | 与其他知识点的关联 |
| K | 标签 | 重点/难点/课程思政 等 |
| L | 认知维度 | 记忆/理解/应用/分析/评价/创造 |
| M | 知识分类 | 事实性/概念性/程序性/元认知 |
| N-O | 教学目标/知识点说明 | 其他教学属性 |

## 🎓 应用场景

- **教育领域**：从课程标准、教学大纲提取知识点构建知识图谱
- **技能培训**：自动化生成技能操作规范的层次化结构  
- **知识管理**：将文档知识转变为结构化知识库
- **图谱构建**：为 Neo4j/Apache Jena 等图谱工具准备数据

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助完善这个技能。

## 📄 许可证

MIT License

---

**Made with ❤️ for the OpenCode Community**