# 部署验证清单 (Deployment Checklist)

## ✅ 技能部署验证

### 1. 目录结构验证
```bash
# 检查目录层级
ls -la ~/.agents/skills/knowledge-graph-extractor/
# 应能看到:
# - SKILL.md
# - scripts/extract_knowledge_graph.py
# - assets/template.xlsx
# - references/
# - examples/
```

### 2. 文件完整性验证  
```bash
# 核心文件检查
ls -la ~/.agents/skills/knowledge-graph-extractor/SKILL.md
ls -la ~/.agents/skills/knowledge-graph-extractor/scripts/extract_knowledge_graph.py
ls -la ~/.agents/skills/knowledge-graph-extractor/assets/template.xlsx
```

### 3. 脚本可执行验证
```bash
# 测试脚本帮助命令
cd ~/.agents/skills/knowledge-graph-extractor/
python scripts/extract_knowledge_graph.py --help
```

### 4. 依赖环境验证
```bash
# Python 依赖测试
python -c "import openpyxl, pandas, pdfplumber, docx; print('✅ 依赖可用')" 

# 系统命令测试
pandoc --version 2>/dev/null && echo "✅ pandoc 可用" || echo "⚠️ pandoc 未安装"
```

---

## 🧪 功能测试验证

### 输出格式验证
```bash
# 验证每行是否只有一个知识点 (A-G列)
python -c "
import pandas as pd
import sys
df = pd.read_csv(sys.argv[1]) if len(sys.argv) > 1 else exit(1)
invalid_rows = []
for _, row in df.iterrows():  
  count = sum(1 for col in 'ABCDEFG' if row[col] and str(row[col]).strip())
  if count != 1:
    invalid_rows.append(_)
print(f'树状结构验证: {len(invalid_rows)==0}', end='')
if invalid_rows:
  print(f', 发现 {len(invalid_rows)} 个错误行: {invalid_rows[:5]}')
else:
  print(' ✅ 通过')
"
```