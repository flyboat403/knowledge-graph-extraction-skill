# OpenCode 文档知识图谱抽取技能验证

## ✅ 快速验证检查表

### 1. 文件结构检查
```bash
# 检查技能目录
ls -la ~/.agents/skills/knowledge-graph-extractor/
# 预期输出：
# SKILL.md, scripts/, assets/, references/, examples/
```

### 2. 核心文件验证
```bash
for file in SKILL.md "scripts/extract_knowledge_graph.py" "assets/template.xlsx"; do
  if [ -f ~/.agents/skills/knowledge-graph-extractor/$file ]; then
    echo "✅ $file 存在"
  else  
    echo "❌ $file 缺失"
  fi
done
```

### 3. 依赖验证
```bash
# Python 依赖
python -c "import openpyxl, pandas, pdfplumber, docx" && echo "✅ Python依赖完整" || echo "❌ Python依赖缺失"

# 系统命令
command -v pandoc > /dev/null && echo "✅ pandoc 可用" || echo "⚠️ pandoc 未安装"
```

---

## 🧪 功能测试 (可选)

### 运行测试抽取
```bash
# 进入技能目录
cd ~/.agents/skills/knowledge-graph-extractor/

# 查看帮助信息
python scripts/extract_knowledge_graph.py --help
```

### 验证输出格式  
```bash
# 简单格式验证脚本
python -c "
import pandas as pd
import sys
if len(sys.argv) < 2: exit(1)
df = pd.read_csv(sys.argv[1])
invalid = [i for _, r in df.iterrows() if sum(1 for c in 'ABCDEFG' if pd.notna(r[c]) and r[c]) != 1]
print(f'Tree structure test: {\"✅ Pass\" if len(df) == 0 or len(invalid) == 0 else f\"❌ {len(invalid)} errors\"}')
" test_output.csv  # 替换为具体测试结果文件
```

---

## 📊 技能特性验证

| 特性 | 检查方法 | 通过标准 |
|------|----------|----------|
| **树状结构** | 每行 A-G 列仅1个节点 | 所有行 sum(A1-G1)==1 |
| **认知维度** | L列仅填预定义值 | 值属于 {记忆/理解/应用/分析/评价/创造} |
| **知识分类** | M列仅填预定义值 | 值属于 {事实性/概念性/程序性/元认知} |
| **分隔符** | H/I/J列多值 | 用英文分号`;`分隔 |
| **关系完整性** | H-I列双向性 | A前置→B 则 B后置→A |

---

**验证完成标志**：以上检查全部通过，技能部署成功！ 
**开始使用**：可在 OpenCode 环境中正常调用此技能