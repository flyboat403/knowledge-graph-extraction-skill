# 最佳实践：文档知识图谱抽取

## 🎯 核心目标
从教育/技术文档自动化生成**结构化知识图谱**，满足树状层级(A-G列) + 三类关系(H-I-J列)的标准化输出，直接兼容Neo4j/Jena等图谱工具导入。

---

## 📝 输入文档准备最佳实践

### 1. 文档格式优化

**推荐格式**：Word `.docx` 文档 (优于 PDF)

#### 正确结构（推荐）：
```markdown
# 一级标题：电子信息类职业技能考试
## 二级标题：专业知识(应知)  
### 三级标题：电工技术基础与技能
#### 四级标题：安全用电常识
##### 五级标题：触电的种类和形式
###### 六级标题：接触触电的类型
#######
```

**vs. 避免手动编号：**
```
❌ 错误： 
1. 电工技术基础  
  1.1 安全用电常识
    1.1.1 触电种类  
      1.1.1.1 接触触电
```

### 2. 关键词标准化

在文档中使用**认知动词**引导知识点层级：

| 认知等级 | 动词模板 | 文档示例 |
|----------|----------|----------|
| **记忆** | "了解..." "知道...的定义" | 了解电阻的定义和单位 |
| **理解** | "理解..." "掌握...的含义" | 理解欧姆定律的物理内涵 |
| **应用** | "掌握..." "能够...使用" | 掌握万用表测量方法 |
| **分析** | "分析...的原理" "比较...差异" | 分析电路故障的常见原因 |
| **评价** | "评价...优劣" "判断...合理性" | 评价不同设计方案的优势 |
| **创造** | "设计...方案" "创建...系统" | 设计电路保护系统方案 |

---

## ⚙️ 模板设计最佳实践

### A1单元格约束定义（模板核心）

```csv
使用说明：
1. A1-G1列对应知识点层级，每行只填写一个知识点
2. H1-J1列填入前置/后置/关联知识点（多知识点用英文分号;隔开）
3. K1-O1保留为标签/认知/分类信息
4. 每行仅一知识点（树状结构），保证导入兼容性
```

### 模板列头标准：
```
A: 一级知识点
B: 二级知识点  
C: 三级知识点
D: 四级知识点
E: 五级知识点
F: 六级知识点
G: 七级知识点
H: 前置知识点  # 例如: 电阻基础知识;电流基本概念
I: 后置知识点  # 自动生成（前置的反向关系）  
J: 关联知识点  # 例如: 电压;功率;频率
K: 标签        # 例如: 考点;重点;难点
L: 认知维度    # 仅一项: 记忆/理解/应用/分析/评价/创造
M: 知识分类    # 仅一项: 亊实性/概念性/程序性/元认知  
N: 教学目标    # 自定义描述文本
O: 知识点说明  # 详细说明文本
```

---

## 🏗️ 知识结构设计

### 层级分配策略

| 层级 | 代表内容 | 文档位置 | 典型特征 |
|------|----------|----------|----------|
| **A** | 主领域 | 文档标题 | 学科/课程/专项 |
| **B** | 模块/单元 | 章名 | 独立功能区 |  
| **C** | 知识主题 | 节名 | 零碎子模块 |
| **D** | 抽象概念 | 小节名 | 通用知识点 |
| **E** | 具体知识 | 段落要点 | 实体概念 |
| **F** | 细化节点 | 静态描述 | 要点细分 |
| **G** | 原子内容 | 非结构化细节 | 可选节点 |

示例：
```
A: 电子信息类职业技能考试
B: 专业知识(应知)  
C: 电工技术基础与技能
D: 安全用电常识
E: 触电的种类和形式
F: 接触触电的类型
G: (可选) 单项类型详解
```

---

## 🧠 认知标注最佳实践

### 动词优先级处理规则

```python
# 识别顺序从前往后
if 任何词汇 in 认知词典:
    return 高优先级认知

认知词典 = {
    "创造": ["设计", "构建", "开发", "创建", "规划"],
    "评价": ["评估", "判断", "评价", "鉴别", "分析优劣"],  
    "分析": ["分析", "比较", "辨析", "解析", "对比"],
    "应用": ["应用", "操作", "执行", "掌握", "使用", "能够", "会"],
    "理解": ["理解", "解释", "说明", "阐述", "熟悉"],
    "记忆": ["记住", "知道", "了解", "认识", "说出", "识记"]
}
```

### 上下文判断增强

**上下文增强**: 通过上下文关键词提升识别准确度：

```
✅ 理解优先场景：
- "要求学生[理解]原理" > 一般"理解概念"
- "掌握[基本]操作" > "掌握复杂技能"
  
✅ 应用优先场景：  
- "[能够]独立完成" > "理解过程"
- "会[使用]工具" > "知道名称"
```

---

## 🔗 关系抽取高级策略

### 智能关系识别

1. **逻辑关联**: 顺序性、依赖性、相似性
   - `"A的实现依赖B"` → B为A前置
   - `"A与B密切相关"` → A与B关联
   - `"基于A进行B"` → A为B前置

2. **结构关联**: 直接层级相邻
   - 同级概念 → 关联关系  
   - 父子级 → 前置/后置关系

3. **术语关联**: 同义/反义/扩展词
   识别 `"模拟电路"` 与 `"数字电路"` 的对比关系

### 关系生成模板

```python
class 关系识别器:
    def _识别前置关系(self, 当前节点, 候选列表):
        # 先修-后修逻辑
        return [c for c in 候选 if  
                self.是先修需求(c, 当前节点)]
    
    def _生成后置关系(self, 前置映射):
        # 反向映射
        return {child: parent for parent, children 
                in 前置映射.items() for child in children}
    
    def _识别关联关系(self, 当前节点, 候选列表):
        # 同类/对比/补充性知识
        return [c for c in 候选 if 
                self.相关不前置(c, 当前节点)]
```

---

## 📊 输出验证最佳实践

### 格式验证脚本

```python
def 验证树状结构(df):
    """验证每行A-G列仅含一个知识点"""
    errors = []
    for idx, row in df.iterrows():
        count = sum(1 for col in 'ABCDEFG' if row[col])
        if count != 1:
            errors.append(f"行{idx}: {count}个知识点")
    return errors

def 验证认知约束(df):
    """验证认知维度符合标准"""
    valid_levels = {"记忆", "理解", "应用", "分析", "评价", "创造"}
    return set(df[df.L!=None].L.unique()).issubset(set(valid_levels))

def 验证关系格式(df):
    """验证关系使用英文分号"""
    errors = []
    for col in 'HIJ':  # 关系列
        for idx, val in enumerate(df[col]):
            if val and '；' in val:  # 中文分号
                errors.append(f"{col}列第{idx}行使用中文分号")
    return errors
```

### 质量评估标准

| 指标 | 理想值 | 验证方法 |
|------|--------|----------|
| 层次完整性 | >6级 | 统计A-G列层级分布 |
| 关系数密度 | 0.3-0.5 | 关联数量/节点数量比率 |
| 节点关联率 | >0.7 | 有关系连接的节点比率 |
| 认知准确率 | >85% | 与专家标注对比 |

---

## 🚀 高效使用模式

### 模式1：批量文档处理

```bash
# 批量处理多文档
find . -name "*.docx" | while read docfile; do  
  python scripts/extract_knowledge_graph.py \
    --source "$docfile" \
    --template assets/template.xlsx \
    --output "output_${docfile%.*}.xlsx"
done
```

### 模式2：增量知识图谱构建

```python
from openpyxl import load_workbook
import pandas as pd

# 合并多个抽取结果
def 合并结果(all_files):
    df_combined = []
    for f in all_files:
        df = pd.read_excel(f)  
        df_combined.append(df)
    
    # 确保A-O列完整
    result = pd.concat(df_combined, ignore_index=True)
    return result.fillna('')

# 使用示例 - 将多本书籍的结果合并
merged_df = 合并结果(['电工基础.xlsx', '电子技术.xlsx', '单片机.xlsx'])
merged_df.to_excel('完整知识图谱.xlsx', index=False)
```

### 模式3：导入工具准备验证

```python
# 为 Neo4j 准备 CSV 数据
def 为neo4j准备(df):
    # 过滤有效行（有A-G列数据的行）
    df_valid = df[df[['A','B','C','D','E','F','G']].any(axis=1)]
    
    # 打平层级（每个知识点单独一行）  
    nodes = []
    for _, row in df_valid.iterrows():
        for level, col in enumerate('ABCDEFG', 1):
            if row[col]:
                nodes.append({
                    'name': row[col],
                    'level': level,
                    'cognitive': row['L'],
                    'category': row['M']
                })
    
    # 生成关系 CSV
    relations = []
    for _, row in df_valid.iterrows():  
        if row['H']:  # 前置关系
            for pre_topic in row['H'].split(';'):
                relations.append({
                    'start_node': pre_topic.strip(),
                    'end_node': row['A'] or row['B'] or row['C'] or row['D'] or row['E'] or row['F'] or row['G'], 
                    'relation_type': 'pre_requisite'
                })
        if row['J']:  # 关联关系
            for rel_topic in row['J'].split(';'):  
                relations.append({
                    'start_node': row['A'] or row['B'] or row['C'] or row['D'] or row['E'] or row['F'] or row['G'],
                    'end_node': rel_topic.strip(),
                    'relation_type': 'associated_with'
                })
                
    return pd.DataFrame(nodes), pd.DataFrame(relations)
```

---

## ✅ 完整验证清单

- [ ] **树状结构**：每行A-G列仅1个知识点（验证 `sum(1 for c in 'ABCDEFG' if $c_row) == 1`)
- [ ] **关系分隔符**：H-I-J列使用英文分号`;`（而非中文`；`）  
- [ ] **单选约束**：L列(M列)为预定义选项（认知/分类）中的单选
- [ ] **列完整性**：A-O列模板结构未删除（保证导入兼容）
- [ ] **关系唯一性**：任意两知识点仅存在一种关系类型
- [ ] **导入验证**：输出文件可正常导入知识图谱工具
- [ ] **层级深度**：抽取层级≥期望深度（建议≥6级）  
- [ ] **标注准确率**：认知/分类标注准确性>80%

---

## 🛡️ 防错检查

### 频发错误防错指南

| 错误类型 | 检查项 | 补救措應 |  
|----------|--------|----------|
| **格式冲突** | 一行多知识点(树约束) | 重跑抽取脚本或手动拆分行 |
| **认知误标** | 应用/理解认知层级混淆 | 检查源文档中的认知动词 |
| **关系重复** | 两知识点多重关系 | 保留主要原因，删減次要关系 |
| **层数跳跃** | 非连续层级结构 | 检查源文档层级是否连续 |

### 质量验证脚本

```bash
echo "=== 最终验证报告 ==="

# 树状结构验证
python -c "
import pandas as pd;
df = pd.read_csv('output.csv');
tree_errors = [];
for i, row in df.iterrows():
  count = sum(1 for c in 'ABCDEFG' if row.get(c, '')); 
  if count != 1: tree_errors.append(f'行{i+3}格式错: {count}节点')
if tree_errors: 
  print('❌ 树状结构错误:')
  for e in tree_errors[:5]: print(f'  {e}')
  if len(tree_errors) > 5: print(f'  ... 还有{len(tree_errors)-5}个')
else: print('✅ 树状结构验证通过')
"

# 认知维度验证
python -c "
import pandas as pd;
df = pd.read_csv('output.csv');
valid_levels = {'记忆', '理解', '应用', '分析', '评价', '创造'};
invalid_levels = {level for level in df.L.dropna() if level not in valid_levels};
print(f'✅ 认知维度检验:' + '通过' if not invalid_levels else f'发现问题: {invalid_levels}')
"

# 关系格式验证  
python -c "
import pandas as pd;
df = pd.read_csv('output.csv');
rel_errors = [];
for col in 'HIJ':
  for _, row in df.iterrows():
    if row.get(col, None) and ('；' in str(row[col]) or '，' in str(row[col])):
      rel_errors.append(f'{col}列含中文符号')
if rel_errors: 
  print(f'❌ 关系列格式错: {len(set(rel_errors))}个')
else: print('✅ 关系列格式验证通过')
"
```

---

## 🔄 迭代改进策略

### 持续调优指标

1. **抽取覆盖率** = 有效知识点数 / 源文档知识点总计
2. **关系准确率** = 正确关系数 / 关系总数
3. **认知标注准确率** = (记忆+理解+应用)占比与预期偏差
4. **模板兼容性** = 输出导入一次成功/运行总次数

### 性能优化建议

- 使用 Word 标题样式而非手工编号提升抽取准度
- 将大文档拆分为多个中等大小文档处理
- 建立认知动词词典定期更新（基于错误分析）
- 设计自动评估脚本持续监控质量

---

这一套最佳实践确保了从文档到知识图谱的成功转换，通过标准化输入、优化流程设计和严格验证输出，实现高质量、一致性、可验证的知识图谱抽取效果。