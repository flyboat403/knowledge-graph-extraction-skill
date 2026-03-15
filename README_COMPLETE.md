# 文档知识图谱结构化抽取技能

从 Word/PDF 文档中自动化抽取层次化知识节点，生成适用于知识图谱系统导出的结构化数据。

[![OpenCode Skill](https://img.shields.io/badge/OpenCode-Skill-blue?logo=skill)](https://opencode.ai/) 
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-yellow)](RELEASE_NOTES.md)

## 🚀 快速开始

### 技能调用
```bash
# 使用安装好的技能
cd ~/.agents/skills/knowledge-graph-extractor/
python scripts/extract_knowledge_graph.py \
  --source input_document.docx \
  --template assets/template.xlsx \
  --output output_graph.xlsx
```

### 输入输出
- **源文档**: `.docx` 或 `.pdf` (结构化文档，最佳为Word标题样式)  
- **模板**: `.xlsx` (格式约束模板，A1单元格含规范)
- **输出**: `.xlsx`/.`csv` (兼容 Neo4j/Jena 格式)

---

## 🌟 核心功能

| 功能特性 | 说明 | 优势 |
|----------|------|------|
| **层次化抽取** | 从文档中抽取 7+级知识点层级(A-G列树结构) | 支持精细化知识结构分析 |
| **认知标注** | 识别布鲁姆层级(记忆/理解/应用/分析/评价/创造) | 自动进行教育目标分级 |
| **关系识别** | 生成前置/后置/关联三类知识点关系 | 构建完整知识依赖图 |
| **格式约束** | 每行1知识点，符合导入标准 | 100%兼容图谱工具导入 |

---

## 📊 输出示例  

抽取结果遵循 A-O 列标准格式：

| A | B | C | D | E | H | I | J | K | L | M |
|--|-- |--|--|--|--|--|--|--|--|--|
| 电子信息技术 | 专业知识 | 电工技术基础 | 安全用电常识 | 触电种类 |电阻/电流概念| 安全措施/急救 |关联知识...|考点/重点|理解|概念性|

> **关键约束**: 每行 A-G 列只能填写**一个**知识点（树状结构）

---

## 🎓 适用场景

### 教育领域
- **课程标准解析**: 抽取教学知识点层级
- **考试大纲分析**: 构建考试知识点图谱  
- **教材内容组织**: 层次化知识内容梳理
- **学习路径规划**: 前置依赖关系识别

### 知识管理
- **企业培训**: 技能点层级与关系分析
- **产品文档**: 功能模块结构化整理  
- **知识图谱构建**: 从文档自动生成图谱数据

---

## 🛠️ 技术规范

### 树状结构规则  
- 每行 (A-G列) 有且仅有1个知识点 (确保树结构正确) ✅
- H-J列 用英文分号`;`分隔多项关系 ✅  
- L/M列 只填入单选值 (认知/分类) ✅
- 输出文件 直接兼容知识图谱工具导入 ✅

### 认知层级说明

| 维度 | 标识词 | 示例 |
|------|--------|------|
| **记忆** | "说出" "了解" "记住" | 说出电阻的单位 |
| **理解** | "理解" "解释" "阐述" | 解释欧姆定律原理 |
| **应用** | "掌握" "运用" "会使用" | 运用万用表测量电压 |
| **分析** | "分析" "比较" "分解" | 分析电路故障原因 |
| **评价** | "评价" "判断" "选择" | 评价不同电路方案 |
| **创造** | "设计" "构建" "规划" | 设计电源控制电路 |

---

## 📁 目录结构

```
knowledge-graph-extractor/
├── SKILL.md                    # OpenCode技能定义  
├── scripts/
│   └── extract_knowledge_graph.py   # 抽取主程序
├── references/    
│   ├── output-format.md        # 输出格式规范
│   └── cognitive-levels.md     # 认知层级定义
├── assets/
│   └── template.xlsx           # 输出模板
├── examples/
│   └── 输入/输出示例文件
├── docs/ 
│   ├── QUICKSTART.md           # 快速入门
│   ├── BEST_PRACTICES.md       # 最佳实践  
│   ├── FAQ.md                 # 问题解答
│   └── CHEATSHEET.md          # 使用卡片
└── README.md                 # 本文档
```

---

## 📈 性能指标

| 指标 | 规范 |
|------|------|
| 层级深度 | ≥ 7 级 (A-G列) |
| 节点数量 | 无限制 |
| 关系数量 | ≤ 2000 条 (受导入系统限制) |
| 认知准确率 | > 85% (基于动词判断) |
| 模板兼容性 | 100% (A1规则自动识别) |

---

## 👨‍🏫 最佳实践

1. **文档准备**: 使用 Word 标题样式而非手工编号
2. **认知标注**: 文档中使用明确动词 ("要求掌握" → 应用)  
3. **模板定制**: 根据导入工具需求微调 A1 格式说明
4. **关系标识**: 使用明确术语标示知识关联("基于"\| "依赖"\| "后接")

---

## ⚡ 部署

### 安装到 OpenCode
```bash 
# 方法1: 直接下载到技能目录
mkdir -p ~/.agents/skills/knowledge-graph-extractor/
cd ~/.agents/skills/knowledge-graph-extractor/
# 下载本仓库文件到此目录...

# 方法2: 使用OpenCode CLI
opencode skills add https://github.com/flyboat403/knowledge-graph-extraction-skill.git
```

---

## 📚 学习资源

- **入门**: [QUICKSTART.md](QUICKSTART.md)
- **最佳实践**: [BEST_PRACTICES.md](BEST_PRACTICES.md) 
- **问题解答**: [FAQ.md](FAQ.md)
- **参考规范**: [references/](references/) 
- **示例数据**: [examples/](examples/)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进此技能！

---

**💡 提示**: 这是第一个专门用于从教育文档构建知识图谱的 OpenCode 自动化技能，将复杂的知识结构化任务转变为简单的文档处理！
