#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档知识图谱结构化抽取脚本

用法:
    # 方式1: 从 LLM JSON 输出生成 Excel（推荐）
    python extract_knowledge_graph.py --json knowledge_nodes.json --template template.xlsx --output output.xlsx

    # 方式2: 提取文档内容供 LLM 处理
    python extract_knowledge_graph.py --source document.docx --extract-text --output document_content.txt

    # 方式3: 仅解析模板
    python extract_knowledge_graph.py --template template.xlsx --dry-run

技术架构:
    文档 → 文本提取(--source --extract-text) → LLM处理 → JSON输出(--json) → Excel生成
    
    正则匹配已被移除，所有语义理解由 LLM 完成。

功能:
    1. 解析 xlsx 模板 A1 单元格的格式规则
    2. 提取 docx/pdf 文档内容供 LLM 处理
    3. 解析 LLM 输出的 JSON 格式知识节点
    4. 自动生成后置关系（前置关系的反向）
    5. 验证格式约束
    6. 输出符合导入规范的 CSV/Excel 文件

关键输出：A-G列(层级) + H-I-J列(三类关系) + 其他属性列
"""

import argparse
import csv
import json
import sys
import io
import os

# 设置控制台输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dataclasses import dataclass, field
from typing import Dict, List

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill
except ImportError:
    print("Error: openpyxl not installed. Run: pip install openpyxl", file=sys.stderr)
    sys.exit(1)

# ==================== 常量定义 ====================

VALID_COGNITIVE_LEVELS = ["记忆", "理解", "应用", "分析", "评价", "创造"]
VALID_CATEGORIES = ["事实性", "概念性", "程序性", "元认知"]
VALID_TAGS = ["重点", "难点", "考点", "课程思政"]

LEVEL_NAMES = {
    1: '一级(课程)', 
    2: '二级(模块)', 
    3: '三级(章节)', 
    4: '四级(主题)', 
    5: '五级(知识点)', 
    6: '六级', 
    7: '七级'
}

LEVEL_TO_COL = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G"}

# ==================== 数据结构定义 ====================

@dataclass
class KnowledgeNode:
    """知识点节点"""
    name: str
    level: int  # 1=A(一级), 2=B(二级), ..., 7=G(七级)
    tags: str = ""
    cognitive_level: str = ""
    category: str = ""
    objective: str = ""
    description: str = ""
    pre_requisites: str = ""  # H列 - 前置知识点
    post_requisites: str = ""  # I列 - 后置知识点  
    related: str = ""          # J列 - 关联知识点
    children: list = field(default_factory=list)

# ==================== 模板解析 ====================

def parse_template(filepath: str) -> dict:
    """解析 xlsx 模板，返回格式规则"""
    wb = load_workbook(filepath)
    ws = wb.active
    
    a1_value = ws['A1'].value or ""
    
    headers = []
    if ws.max_row > 1:
        headers = [ws.cell(row=2, column=i).value for i in range(1, min(16, ws.max_column + 1))]
    
    return {
        "a1_rules": a1_value,
        "headers": headers,
        "max_column": ws.max_column,
        "sheet_name": ws.title
    }

# ==================== 文档内容提取 ====================

def extract_text_from_docx(filepath: str) -> str:
    """从 docx 文档提取纯文本"""
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
        return "\n".join(paragraphs)
    except ImportError:
        print("Error: python-docx not installed. Run: pip install python-docx", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Error parsing docx: {e}", file=sys.stderr)
        return ""

def extract_text_from_pdf(filepath: str) -> str:
    """从 PDF 文档提取纯文本"""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text.strip():
                    text_parts.append(text.strip())
        return "\n\n".join(text_parts)
    except ImportError:
        print("Error: pdfplumber not installed. Run: pip install pdfplumber", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Error parsing PDF: {e}", file=sys.stderr)
        return ""

def extract_document_content(source_path: str) -> str:
    """提取文档内容"""
    if source_path.endswith('.docx'):
        return extract_text_from_docx(source_path)
    elif source_path.endswith('.pdf'):
        return extract_text_from_pdf(source_path)
    else:
        print(f"Error: 不支持的文档格式: {source_path}", file=sys.stderr)
        print("支持的格式: .docx, .pdf", file=sys.stderr)
        return ""

def generate_llm_prompt(document_content: str, template_rules: str = "") -> str:
    """生成供 LLM 处理的 Prompt"""
    prompt = f"""请从以下文档中抽取知识节点，返回 JSON 格式。

## 文档内容
{document_content}

## 输出格式
```json
[
  {{
    "name": "知识点名称",
    "level": 1-7,
    "cognitive_level": "记忆/理解/应用/分析/评价/创造",
    "category": "事实性/概念性/程序性/元认知",
    "pre_requisites": ["前置知识点"],
    "related": ["关联知识点"],
    "tags": "重点;考点",
    "description": "知识点说明"
  }}
]
```

## 层级定义
- level 1: 课程/学科名称
- level 2: 模块/单元
- level 3: 章节/部分
- level 4: 知识主题
- level 5: 具体知识点
- level 6-7: 知识点细分

## 抽取原则
1. 识别有独立学习价值的知识点
2. 生成前置关系（学习依赖）
3. 生成关联关系（相关概念）
4. 过滤非知识内容（考试说明、行政信息）
"""
    return prompt

# ==================== JSON 解析（LLM 输出） ====================

def parse_llm_json(filepath: str) -> List[KnowledgeNode]:
    """解析 LLM 输出的 JSON 文件，转换为 KnowledgeNode 列表"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("JSON 根元素必须是数组")
    
    nodes = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"警告: 第 {i+1} 个元素不是对象，跳过", file=sys.stderr)
            continue
        
        name = item.get('name', '')
        if not name:
            print(f"警告: 第 {i+1} 个知识点缺少 name 字段，跳过", file=sys.stderr)
            continue
        
        # 处理前置和关联关系（支持数组或字符串）
        pre_req = item.get('pre_requisites', [])
        if isinstance(pre_req, list):
            pre_req = ';'.join(str(p).strip() for p in pre_req if p)
        else:
            pre_req = str(pre_req).strip() if pre_req else ''
        
        related = item.get('related', [])
        if isinstance(related, list):
            related = ';'.join(str(r).strip() for r in related if r)
        else:
            related = str(related).strip() if related else ''
        
        node = KnowledgeNode(
            name=name,
            level=item.get('level', 5),
            tags=item.get('tags', ''),
            cognitive_level=item.get('cognitive_level', '理解'),
            category=item.get('category', '概念性'),
            objective=item.get('objective', ''),
            description=item.get('description', ''),
            pre_requisites=pre_req,
            related=related,
        )
        nodes.append(node)
    
    return nodes

# ==================== 关系生成 ====================

def generate_post_relations(nodes: List[KnowledgeNode]) -> None:
    """生成后置关系（前置关系的反向）"""
    name_to_node: Dict[str, KnowledgeNode] = {n.name: n for n in nodes}
    post_relations: Dict[str, List[str]] = {}
    
    for node in nodes:
        if node.pre_requisites:
            pre_list = [p.strip() for p in node.pre_requisites.split(';') if p.strip()]
            for pre_name in pre_list:
                if pre_name not in post_relations:
                    post_relations[pre_name] = []
                if node.name not in post_relations[pre_name]:
                    post_relations[pre_name].append(node.name)
    
    for node in nodes:
        if node.name in post_relations:
            node.post_requisites = ';'.join(post_relations[node.name])

def validate_relations(nodes: List[KnowledgeNode]) -> List[str]:
    """验证关系约束"""
    errors = []
    all_names = {n.name for n in nodes}
    
    for node in nodes:
        # 检查前置关系
        if node.pre_requisites:
            for pre in node.pre_requisites.split(';'):
                pre = pre.strip()
                if pre and pre not in all_names:
                    errors.append(f"节点 '{node.name}' 的前置知识点 '{pre}' 不存在")
        
        # 检查关联关系
        if node.related:
            for rel in node.related.split(';'):
                rel = rel.strip()
                if rel and rel not in all_names:
                    errors.append(f"节点 '{node.name}' 的关联知识点 '{rel}' 不存在")
    
    return errors

# ==================== 层级树构建 ====================

def build_knowledge_tree(nodes: List[KnowledgeNode]) -> List[KnowledgeNode]:
    """根据层级构建知识树，建立父子关系
    
    要求：输入的节点必须按深度优先顺序排列（由 LLM Prompt 保证）
    
    算法原理：
    1. level_stack 记录每个层级当前的"活跃"父节点
    2. 遇到新节点时，清理栈中层级 >= 当前层级的节点
    3. 新节点的父节点 = level_stack[level - 1]
    4. 将当前节点压入其层级的栈
    
    示例执行过程（深度优先顺序）：
      节点                level_stack           父节点
      ────────────────────────────────────────────────────
      课程(level1)        {1: 课程}             None → root
      模块A(level2)       {1: 课程, 2: 模块A}   课程
      章节A1(level3)      {1: 课程, 2: 模块A, 3: 章节A1}  模块A
      主题A1a(level4)     {..., 4: 主题A1a}     章节A1
      主题A1b(level4)     {..., 4: 主题A1b}     章节A1 (清理level4后重新添加)
      章节A2(level3)      {..., 3: 章节A2}      模块A (清理level3,4后)
      模块B(level2)       {1: 课程, 2: 模块B}   课程 (清理level2,3,4后)
    """
    level_stack: Dict[int, KnowledgeNode] = {}
    root_nodes = []
    
    for node in nodes:
        # 清理栈中层级 >= 当前层级的节点
        for l in list(level_stack.keys()):
            if l >= node.level:
                del level_stack[l]
        
        # 父节点是当前层级-1的栈顶节点
        parent = level_stack.get(node.level - 1)
        
        if parent:
            parent.children.append(node)
        else:
            root_nodes.append(node)
        
        # 将当前节点压入其层级的栈
        level_stack[node.level] = node
    
    return root_nodes

# ==================== 扁平化输出 ====================

def flatten_nodes(nodes: List[KnowledgeNode]) -> List[Dict]:
    """将知识节点列表扁平化为 Excel 行数据"""
    rows = []
    
    for node in nodes:
        row = {col: "" for col in "ABCDEFG"}
        if node.level in LEVEL_TO_COL:
            row[LEVEL_TO_COL[node.level]] = node.name
        
        row.update({
            "H": node.pre_requisites,
            "I": node.post_requisites, 
            "J": node.related,
            "K": node.tags,
            "L": node.cognitive_level,
            "M": node.category,
            "N": node.objective,
            "O": node.description
        })
        
        rows.append(row)
        
        if node.children:
            rows.extend(flatten_nodes(node.children))
    
    return rows

# ==================== Excel/CSV 生成 ====================

def generate_excel(rows: List[Dict], output_path: str, template_rules: str = ""):
    """生成 Excel 文件"""
    wb = Workbook()
    ws = wb.active
    ws.title = "知识点抽取结果"
    
    instructions = template_rules or """使用说明：
1. A列至G列对应知识点的层级关系，区间内每行只能填写一个知识点
2. H列至J列填写对应知识点的前置、后置和关联知识点，多个知识点之间用英文分号";"隔开
3. 任意两个知识点之间只能存在一种关系（前提、后置或关联）
4. 固定标签包括：重点、难点、考点、课程思政
5. 认知维度包括：记忆、理解、应用、分析、评价、创造
6. 知识点分类包括：事实性、概念性、程序性、元认知"""
    
    ws['A1'] = instructions
    ws.merge_cells('A1:O1')
    ws['A1'].alignment = Alignment(wrap_text=True, vertical='top')
    
    headers = ['一级知识点', '二级知识点', '三级知识点', '四级知识点', '五级知识点',
               '六级知识点', '七级知识点', '前置知识点', '后置知识点', '关联知识点',
               '标签', '认知维度', '分类', '教学目标', '知识点说明']
    
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col_idx, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    col_widths = {'A': 25, 'B': 20, 'C': 25, 'D': 25, 'E': 25, 'F': 15, 'G': 15,
                  'H': 35, 'I': 35, 'J': 35, 'K': 15, 'L': 12, 'M': 12, 'N': 35, 'O': 40}
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width
    
    for row_idx, row_data in enumerate(rows, 3):
        for col_idx, key in enumerate(['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'], 1):
            ws.cell(row=row_idx, column=col_idx, value=row_data.get(key) or "")
    
    wb.save(output_path)
    print(f"✅ Excel 文件已保存: {output_path}")

def generate_csv(rows: List[Dict], output_path: str):
    """生成 CSV 文件"""
    headers = ['一级知识点', '二级知识点', '三级知识点', '四级知识点', '五级知识点',
               '六级知识点', '七级知识点', '前置知识点', '后置知识点', '关联知识点',
               '标签', '认知维度', '分类', '教学目标', '知识点说明']
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row_data in rows:
            writer.writerow([row_data.get(c, '') for c in 'ABCDEFGHIJKLMNO'])
    
    print(f"✅ CSV 文件已保存: {output_path}")

# ==================== 验证 ====================

def validate_rows(rows: List[Dict]) -> List[str]:
    """验证行数据是否符合约束"""
    errors = []
    
    for i, row in enumerate(rows, 3):
        level_vals = [row.get(col, "") for col in 'ABCDEFG']
        non_empty_count = sum(1 for val in level_vals if val)
        if non_empty_count != 1:
            errors.append(f"行 {i}: 每行应只有1个知识点，实际{non_empty_count}个")
        
        cognitive = row.get('L', '')
        if cognitive and cognitive not in VALID_COGNITIVE_LEVELS:
            errors.append(f"行 {i}: 认知维度无效: {cognitive}")
        
        category = row.get('M', '')
        if category and category not in VALID_CATEGORIES:
            errors.append(f"行 {i}: 分类无效: {category}")
        
        for col in 'HIJ':
            val = row.get(col, '')
            if val and '；' in val:
                errors.append(f"行 {i}: {col}列使用中文分号")
    
    return errors

# ==================== 统计输出 ====================

def print_statistics(nodes: List[KnowledgeNode], rows: List[Dict], output_path: str, csv_path: str):
    """输出统计信息"""
    level_dist = {}
    for node in nodes:
        level_dist[node.level] = level_dist.get(node.level, 0) + 1
    
    h_count = sum(1 for n in nodes if n.pre_requisites)
    i_count = sum(1 for n in nodes if n.post_requisites)
    j_count = sum(1 for n in nodes if n.related)
    
    print(f"""
{'=' * 60}
抽取结果概要
{'=' * 60}

知识点统计:
  - 节点总数: {len(nodes)} 条
  - 层级分布: {', '.join([f'{LEVEL_NAMES.get(l, l)}: {c}' for l, c in sorted(level_dist.items())])}

关系统计:
  - 前置关系(H列): {h_count} 条
  - 后置关系(I列): {i_count} 条
  - 关联关系(J列): {j_count} 条

格式验证:
  - 树状结构: {'✅ 通过' if all(sum(1 for c in 'ABCDEFG' if r.get(c)) == 1 for r in rows) else '❌ 失败'}
  - 认知维度: {'✅ 通过' if all(r.get('L', '') in VALID_COGNITIVE_LEVELS or not r.get('L') for r in rows) else '❌ 失败'}
  - 知识点分类: {'✅ 通过' if all(r.get('M', '') in VALID_CATEGORIES or not r.get('M') for r in rows) else '❌ 失败'}

文件输出:
  - Excel路径: {output_path}
  - CSV备份: {csv_path}
""")

# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(
        description='文档知识图谱结构化抽取',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从 LLM JSON 生成 Excel（推荐）
  %(prog)s --json nodes.json --template template.xlsx --output output.xlsx
  
  # 提取文档内容供 LLM 处理
  %(prog)s --source document.docx --extract-text --output content.txt
  
  # 仅解析模板
  %(prog)s --template template.xlsx --dry-run
""")
    parser.add_argument('--json', help='LLM 输出的 JSON 文件路径')
    parser.add_argument('--source', help='源文档路径 (docx/pdf)')
    parser.add_argument('--extract-text', action='store_true', help='提取文档文本供 LLM 处理')
    parser.add_argument('--template', help='xlsx 模板路径')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--dry-run', action='store_true', help='仅解析模板')
    args = parser.parse_args()
    
    # 模式1: 提取文档文本
    if args.source and args.extract_text:
        print("步骤1: 提取文档内容...")
        content = extract_document_content(args.source)
        
        if not content:
            print("错误: 无法提取文档内容", file=sys.stderr)
            sys.exit(1)
        
        print(f"  内容长度: {len(content)} 字符")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 文档内容已保存: {args.output}")
            print("\n下一步: 请将文档内容传递给 LLM 进行知识抽取，然后使用 --json 参数生成 Excel")
        else:
            print("\n" + "=" * 60)
            print("文档内容:")
            print("=" * 60)
            print(content)
        
        return
    
    # 模式2: 解析模板 (dry-run)
    if args.dry_run:
        if not args.template:
            print("错误: dry-run 模式需要 --template 参数", file=sys.stderr)
            sys.exit(1)
        
        print("解析模板...")
        template = parse_template(args.template)
        print(f"  模板列数: {template['max_column']}")
        print(f"  Sheet名称: {template['sheet_name']}")
        print(f"  A1规则: {template['a1_rules'][:100]}..." if len(template['a1_rules']) > 100 else f"  A1规则: {template['a1_rules']}")
        print("\n✅ 模板解析完成")
        return
    
    # 模式3: 从 JSON 生成 Excel
    if not args.json:
        print("错误: 需要指定 --json 参数", file=sys.stderr)
        print("提示: 使用 --source --extract-text 提取文档内容，然后交给 LLM 处理", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    if not args.template or not args.output:
        print("错误: 需要 --template 和 --output 参数", file=sys.stderr)
        sys.exit(1)
    
    # 步骤1: 解析模板
    print("步骤1: 解析模板...")
    template = parse_template(args.template)
    print(f"  模板列数: {template['max_column']}")
    
    # 步骤2: 解析 JSON
    print("步骤2: 解析 LLM JSON 输出...")
    nodes = parse_llm_json(args.json)
    print(f"  已加载 {len(nodes)} 个知识节点")
    
    # 步骤3: 生成关系
    print("步骤3: 生成知识点关系...")
    generate_post_relations(nodes)
    
    relation_errors = validate_relations(nodes)
    if relation_errors:
        print(f"  ⚠️ 关系验证警告 ({len(relation_errors)} 条):")
        for err in relation_errors[:3]:
            print(f"    - {err}")
        if len(relation_errors) > 3:
            print(f"    - ... 还有 {len(relation_errors) - 3} 条")
    
    # 步骤4: 构建层级树
    print("步骤4: 构建层级结构...")
    root_nodes = build_knowledge_tree(nodes)
    rows = flatten_nodes(root_nodes)
    
    # 步骤5: 生成输出
    print("步骤5: 生成输出文件...")
    csv_path = args.output.replace('.xlsx', '.csv') if args.output.endswith('.xlsx') else args.output + '.csv'
    
    generate_csv(rows, csv_path)
    if args.output.endswith('.xlsx'):
        generate_excel(rows, args.output, template['a1_rules'])
    
    # 步骤6: 验证
    print("步骤6: 输出验证...")
    errors = validate_rows(rows)
    if errors:
        print(f"  ❌ 发现 {len(errors)} 个错误:")
        for i, err in enumerate(errors[:5], 1):
            print(f"     {i}. {err}")
    else:
        print("  ✅ 验证通过")
    
    # 输出统计
    print_statistics(nodes, rows, args.output, csv_path)

if __name__ == "__main__":
    main()
