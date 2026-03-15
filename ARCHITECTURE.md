# 项目结构解析

## 📁 完整目录结构

```
knowledge-graph-extraction-skill/
├── SKILL.md                    # 🎯 核心技能定义 (含 name+description)
├── skill.json                  # 🔄 Coze 平台兼容格式
├── scripts/
│   └── extract_knowledge_graph.py   # 🤖 知识抽取处理引擎  
├── references/
│   ├── output-format.md        # 📋 输出格式规范 (核心)
│   └── cognitive-levels.md     # 🧠 认知层级定义 (核心) 
├── assets/
│   └── template.xlsx           # 📎 输出模板文件
├── examples/
│   ├── input/                  # 📥 输入示例文档
│   │   ├── sample_template.xlsx
│   │   └── 办公软件应用课程标准.pdf
│   └── output/                 # 📤 输出示例数据  
│       ├── sample_extraction_result.csv
│       └── sample_extraction_result.xlsx
├── README.md                   # 📖 项目总体说明
├── QUICKSTART.md               # ⚡ 快速入门手册 (新手必备)
├── BEST_PRACTICES.md          # 🏆 最佳实践指南 (推荐)  
├── USAGE.md                   # 💡 使用说明卡片 (快速查阅)
├── CARD.md                    # 📇 简明使用卡片 (极简) 
├── CHEATSHEET.md              # 📝 速查参考 (详细操作)
├── QUICK_REF.md               # 🧭 速览指南 (综合)
├── ENVIRONMENT_SETUP.md       # 🔧 环境搭建指南 (部署)
├── FAQ.md                     # ❓ 常见问题解答 (排错)
└── INSTALL.sh                 # 🚀 自动安装脚本
```

---

## 🎯 核心组件详情

### 1. 主要组件

| 文件 | 用途 | 关键功能 |
|------|------|----------|  
| **SKILL.md** | 🧠 核心定义 | 描述触发条件、工作流程和技能规范 |
| **skill.json** | 🔄 平台标准 | Coze平台适配格式 |
| **extract_knowledge_graph.py** | 🤖 核心引擎 | 解析/抽取/生成逻辑处理程序 | 

### 2. 参考组件  

| 文件/目录 | 内容 | 作用 |
|----------|------|-----|
| **output-format.md** | 输出列规范 (A-O列) | 约束 H-I-J 关系生成规则 |
| **cognitive-levels.md** | 认知层级映射 | 动词→层级自动转化规则 |
| **template.xlsx** | 输出格式模板 | A1含格式要求的Excel模板 |
| **examples/** | 输入/输出示例 | 验证和调试参考样本 |

### 3. 文档组件

| 文件 | 覆盖范围 | 目标读者 |
|------|----------|----------|
| **QUICKSTART.md** | 一行命令上手 | 初学者入门 |
| **BEST_PRACTICES.md** | 高级优化技巧 | 进阶用户 |
| **USAGE.md** | 核心功能摘要 | 日常查阅 |
| **FAQ.md** | 问题解答 | 故障排查 |

---

## 🔗 关系映射

### 内容关系流
```
SKILL.md → 知识图谱抽取技能定义总览 (触发 → 流程 → 约束)

scripts/extract_knowledge_graph.py 
         → 实现 SKILL.md 中的抽取功能
         → 依赖 assets/template.xlsx 进行格式输出  
         → 使用 references/*.md 中的规则

references/ 
├── output-format.md → A-G列树约束 + H-I-J关系规范  
└── cognitive-levels.md → L列认知标注规则

examples/
├── input/ → 流程输入参考  
└── output/ → 实际输出样例
```

---

## 🧩 装载与调用流程

```
1. OpenCode 检查 SKILL.md 
   → 基于 description 判断触发时机
2. 加载提取核心功能定义  
3. 依赖 references/ 提供详尽规范信息
4. 执行 scripts/ 中的处理逻辑
5. 输出至 assets/ 模板格式
```

---

## 🏗️ 设计模式遵循

按照 OpenCode Skills 最佳实践设计：

| 模式 | 组件 | 实现方式 |
|------|------|----------|  
| **核心定义** | SKILL.md | Frontmatter (name+description) + 主体功能 |
| **参考分离** | references/ | 规范约束与主逻辑分离 |
| **资源分层** | assets/examples/ | 模板资源与示例资源归类 |
| **脚本独立** | scripts/ | 核心逻辑用 Python 脚本实现 |
| **渐进披露** | 各文档 | 按需加载详尽信息 |