# 如何发布到 GitHub 仓库

## 必要条件
- GitHub 账户并设置好 SSH 密钥
- `gh` CLI 工具（可选但推荐）
- 或 `git` 命令行工具

## 方案一：使用 Github CLI（推荐）

### 1. 安装 GitHub CLI
```bash
# Mac
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows (PowerShell)
winget install GitHub.cli
```

### 2. 登录 GitHub
```bash
gh auth login
# 按提示选择认证方式
```

### 3. 创建新仓库
```bash
# 在当前目录中运行以下命令:
gh repo create knowledge-graph-extraction-skill --public --clone
# 或根据需要添加 --private 为私有仓库
```

### 4. 迁移文件到新仓库
```bash
# 将当前内容拷贝到新的仓库
cd knowledge-graph-extraction-skill
cp -r ../kg_skill/* .
git add .
git commit -m "Initial commit: Complete Knowledge Graph Extraction Skill"
git push origin main
```

## 方案二：手动创建仓库

### 1. 在 GitHub 远程创建仓库
- 登录 GitHub
- 点击 "New repository"
- 仓库名: `knowledge-graph-extraction-skill` 
- 选择公开或私有
- 无需初始化 README, license, 或 .gitignore（已在本地配置）

### 2. 添加远程并推送
```bash
git remote add origin https://github.com/your-username/knowledge-graph-extraction-skill.git  
git branch -M main
git push -u origin main
```

## 仓库内容预览

```
knowledge-graph-extraction-skill/
├── SKILL.md                    # 核心技能定义文件
├── skill.json                  # Coze平台兼容格式
├── scripts/                    # 抽取脚本
│   └── extract_knowledge_graph.py   # CSV/Excel生成脚本
├── references/                 # 详细规范文档
│   ├── cognitive-levels.md     # 认知层级定义
│   └── output-format.md        # 输出格式规范
├── assets/                     # 模板资源
│   └── template.xlsx           # 示例模板
├── examples/                   # 示例文件
│   └── input/                  # 输入示例
│       ├── sample_template.xlsx # 模板示例
│       └── 办公软件应用课程标准.pdf # 源文档示例
└── README.md                   # 说明文档
```

## 功能特性

### 输入
- `docx` / `pdf` 源文档
- `xlsx` 模板文档 (要求 A1 单元格含格式规范)

### 处理
- 知识点层级化解析 (1-7级)
- 认知维度标注 (记忆/理解/应用/分析/评价/创造)
- 语义关系生成 (前置/后置/关联)
- 输出格式验证

### 输出
- **CSV**: 可直接导入 Neo4j/Apache Jena
- **Excel**: 带格式的结构化文件
- **树状结构**: 每行一个知识点

### 核心特性
1. **树状结构约束**: 每行一个知识点 (A-G列)
2. **关系智能生成**: H(I)J列关系自动识别
3. **认知标注**: 基于文本动词自动推断
4. **层级保护**: 确保完整知识链
5. **反模式指导**: NEVEE做事项列表

## 架构说明

架构遵循 OpenCode Skills 设计模式：

1. **前端定义 (SKILL.md)**
   - 清晰的描述和触发场景
   - 高级概念抽象

2. **处理脚本 (scripts/)**
   - `extract_knowledge_graph.py`
   - 完整的抽取流程
   - 验证和错误处理

3. **参考文档 (references/)**
   - `output-format.md` - 输出格式细节
   - `cognitive-levels.md` - 定义认知维度

## 触发场景

用户请求符合以下模式时技能激活：
- "从文档提取知识图谱"
- "生成结构化教学大纲"
- "解析课程标准为知识点"
- "抽取层次化知识节点"
- "生成CSV可导入Neo4j"

## 设计亮点

1. **渐进式披露**: 从高层次概念到底层实现细节
2. **Anti-Patterns**: 明确指出绝不能做的事 (关键) 
3. **决策框架**: "抽取前问自己"问题集
4. **验证约束**: 完整的格式验证规则
5. **容错设计**: 详细的错误处理和修复建议
6. **知识压缩**: 专家级领域知识而非基础教程

## 测试验证

- ✅ 真实文档验证 (05电子信息类.docx)
- ✅ 模板约束遵从
- ✅ 树状结构生成
- ✅ 关系自动识别
- ✅ CSV/Excel 输出正确性

## 部署选项

1. **SaaS托管**: 通过 Sisyphus orchestration agent
2. **本地部署**: 作为 OpenCode skill 直接使用  
3. **容器化**: 可docker化为独立服务
4. **CLI工具**: 作为脚本直接调用

文件大小: $(du -sh . | cut -f1)
分支: main (当前)
贡献: 需要通过 PR 流程