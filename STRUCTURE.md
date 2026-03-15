# 项目结构说明

## 目录结构概览

```
knowledge-graph-extraction-skill/
├── SKILL.md                    # 核心技能定义文件 (OpenCode格式)
├── skill.json                  # Coze平台兼容格式 (skill.json)
├── README.md                   # 项目说明
├── MANUAL.md                   # 快速使用手册
├── QUICKSTART.md               # 快速入门指南  
├── BEST_PRACTICES.md           # 最佳实践指南
├── RELEASE_NOTES.md            # 发布说明
├── install.sh                  # 安装脚本
├── scripts/
│   └── extract_knowledge_graph.py   # 主抽取引擎
├── references/
│   ├── output-format.md         # 输出格式详细规范
│   └── cognitive-levels.md      # 认知层级定义指南
├── assets/
│   └── template.xlsx            # 输出格式模板
├── examples/
│   ├── input/                  # 输入示例数据
│   │   ├── sample_template.xlsx # 模板示例  
│   │   └── 办公软件应用课程标准.pdf # 输入文档示例
│   └── output/                 # 输出示例数据  
│       ├── sample_extraction_result.csv    # CSV格式示例
│       └── sample_extraction_result.xlsx   # Excel格式示例
└── PUBLISH_GUIDE.md            # 发布到GitHub指南
```

## 核心文件说明

### 主定义文件
- **SKILL.md**: 采用 OpenCode 标准的技能定义，含完整 name+description frontmatter
- **skill.json**: Coze 平台兼容的技能描述格式

### 核心执行脚本
- **scripts/extract_knowledge_graph.py**: 文档解析+知识抽取+关系生成主引擎

### 配置与模板
- **assets/template.xlsx**: 输出文件的 Excel 模板 (A1 单元格含格式约束)

### 参考文档  
- **references/output-format.md**: 详细说明 A-O 列格式约束及层级关系
- **references/cognitive-levels.md**: 动词-认知层级映射规则

### 示例数据
- **examples/input/**: 输入文档和模板示例
- **examples/output/**: 生成的抽取结果示例 (CSV/Excel 格式)

---

## 安装与部署

### 1. 自动安装
```
# 现有脚本安装
bash install.sh
```

### 2. 手动安装到 OpenCode
```bash
# 复制到 OpenCode 的技能目录
cp -r /path/to/knowledge-graph-extraction-skill ~/.agents/skills/knowledge-graph-extractor/
```

### 3. 验证安装
```bash
# 检查技能是否可用
# 通常会出现在 OpenCode 的技能列表中
```

---

## 工作流程

输入 → [SKILL] → 输出

1. **输入**: `docx`/`pdf` 文档 + `xlsx` 模板
2. **处理**: 
   - 模板 A1 格式识别
   - 文档层次解析
   - 知识节点抽取及分层  
   - 语义关系自动识别
   - 认知维度和知识分类标注
3. **输出**: 
   - CSV 文件 (可导入 Neo4j/Jena)
   - Excel 文件 (可视化的树状结果)

---

## 使用方式

### 直接运行脚本
```bash
python scripts/extract_knowledge_graph.py \
  --source document.docx \
  --template template.xlsx \
  --output output.xlsx
```

输出格式 (A-O列):
- A-G列: 知识点层级关系 (树状结构, 每行一个知识点)
- H-J列: 前置/后置/关联关系 
- K-O列: 标签/认知维度/分类/目标/说明

---

## 与其他技能的区别

| 技能 | 用途 | 特色功能 |
|------|------|----------|
| **本技能** | 文档知识图谱结构化抽取 | 专注树状层级+认知关系+可导入图谱格式 |
| docx | 简单Word文档处理 | 针对Word文档基础操作 |
| xlsx | Excel表格处理 | 针对表格格式的数据处理 | 
| pdf | PDF文档处理 | 针对PDF格式的数据提取 |

本技能独特之处在于：
- 生成知识图谱导入格式 (A-G树+H-J关系)
- 自动认知层级标注 (6维布鲁姆分类)
- 完整前置/后置/关聝关系识别