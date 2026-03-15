# 文档知识图谱结构化抽取技能

从文档中抽取层次化知识节点，输出可导入知识图谱系统的结构化数据。

## 功能特性

- **层次化抽取**：从 docx/pdf 中提取 6+ 级知识点层级
- **认知标注**：自动标注认知层级（记忆/理解/应用/分析/评价/创造） 
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

## 技术约束

- **树状结构**：每行只能填写一个知识点 (A-G列单一填充)
- **层级递进**：A列(一级) 至 G列(七级)  
- **认知维度**：记忆/理解/应用/分析/评价/创造 (单选值)
- **知识分类**：亊实性/概念性/程序性/元认知 (单选值)
- **关系互斥**：任两点可仅有一类关系 (前置/后置/关联)

### 关系生成机制

- **H列（前置）**：学习当前知识点前要掌握
- **I列（后置）**：学习当前知识点后可继续学
- **J列（关联）**：相关但非依赖的知识点

## 使用方式

### 命令行运行
```bash
python scripts/extract_knowledge_graph.py \
  --source document.docx \
  --template assets/template.xlsx \
  --output output.xlsx
```

### 参数说明
- `source`：输入文档路径  
- `template`：格式模板路径
- `output`：输出文件路径

## 安装使用

```bash
# 安装技能
opencode skills install https://github.com/flyboat403/knowledge-graph-extraction-skill.git

## 或克隆到手动安装
mkdir -p ~/.agents/skills/knowledge-graph-extractor/
cp SKILL.md ~/.agents/skills/knowledge-graph-extractor/
cp -r scripts/ ~/.agents/skills/knowledge-graph-extractor/
cp -r assets/ ~/.agents/skills/knowledge-graph-extractor/
cp -r references/ ~/.agents/skills/knowledge-graph-extractor/
cp -r examples/ ~/.agents/skills/knowledge-graph-extractor/
```

## 目录结构

```
knowledge-graph-extraction-skill/
├── SKILL.md                    # 核心技能定义 (含 name+description)
├── skill.json                  # Coze 平台兼容格式  
├── scripts/
│   └── extract_knowledge_graph.py   # 抽取引擎
├── references/
│   ├── output-format.md         # 输出格式规范
│   └── cognitive-levels.md      # 认知层级定义
├── assets/
│   └── template.xlsx            # 模板文件
├── examples/
│   └── 示例输入输出文件
├── README.md                  # 项目说明 (即本文件)
├── QUICKSTART.md              # 快速入门
├── BEST_PRACTICES.md          # 最佳实践
├── FAQ.md                     # 常见问题  
└── RELEASE_NOTES.md           # 发布说明
```

## 应用场景

- **教育领域**：从课程标准/考试大纲抽取知识图谱
- **技能培训**：自动化知识结构化分析
- **知识管理**：文档知识转变为结构化知识库
- **图谱构建**：为 Neo4j/Apache Jena 准备数据

### 教育示例
输入文档："四川省普通高校招生职业技能考试大纲.pdf"  
输出格式：A1单元格含格式约束的Excel文件
- **树状结构**: A列(课程)→B列(模块)→C列(章节)→D列(主题)→E列(知识点)
- **关系抽取**: 学习依赖/相关关联关系（H-I-J列）
- **认知标注**: 记忆/理解/应用/分析/评价/创造（L列）
- **分类标注**: 事实性/概念性/程序性/元认知（M列）

输出文件可直接导入知识图谱工具，构建学科知识体系图谱。

---

## 完整文档

详细使用说明请参考：

- [**快速入门**](QUICKSTART.md) - 一行命令开始使用
- [**最佳实践**](BEST_PRACTICES.md) - 优化输出结果
- [**FAQ**](FAQ.md) - 问题解答与解决方法
- [**使用技巧**](CHEATSHEET.md) - 快速参考卡片
- [**安装指南**](ENVIRONMENT_SETUP.md) - 环境配置说明

---

**Powered by OpenCode & Sisyphus**  
**Author**: flyboat403