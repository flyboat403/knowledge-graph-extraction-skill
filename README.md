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

## 安装使用

### 使用 OpenCode CLI
```bash
# 安装技能
opencode skills install https://github.com/flyboat403/knowledge-graph-extraction-skill.git
```

### 直接运行脚本
```bash
python scripts/extract_knowledge_graph.py \
  --source document.docx \
  --template assets/template.xlsx \
  --output output.xlsx
```

## 目录结构

```
knowledge-graph-extraction-skill/
├── SKILL.md                    # 核心定义文件
├── scripts/
│   └── extract_knowledge_graph.py   # 抽取脚本
├── references/
│   ├── output-format.md        # 输出格式规范
│   └── cognitive-levels.md     # 认知层级定义
├── assets/
│   └── template.xlsx           # 模板文件
├── examples/
│   ├── input/                  # 输入示例
│   └── output/                 # 输出示例
└── README.md                   # 本文件
```

## 使用场景

- 从课程标准抽取知识点构建知识图谱
- 教育领域的结构化教学数据分析
- 自动知识图谱构建与导入
- 教学内容的层级化梳理

## 技术约束

- **树状结构**：每行只能填写一个知识点
- **层级关系**：A列(一级) 至 G列(七级)  
- **认知维度**：记忆/理解/应用/分析/评价/创造
- **知识分类**：事实性/概念性/程序性/元认知
- **关系类型**：前置/后置/关联（三类互斥）

## 质量保障

项目经过充分测试，包括：
- 真实文档抽取验证
- 格式约束验证  
- 关系完整性验证
- 标准化输出验证

---
**Powered by Sisyphus & OpenCode**  