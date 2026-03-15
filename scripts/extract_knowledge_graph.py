#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档知识图谱结构化抽取脚本

用法:
    python extract_knowledge_graph.py --source document.docx --template template.xlsx --output output.xlsx
    python extract_knowledge_graph.py --source document.pdf --template template.xlsx --output output.csv
    python extract_knowledge_graph.py --template template.xlsx --dry-run  # 仅解析模板

功能:
    1. 解析 xlsx 模板 A1 单元格的格式规则
    2. 从 docx/pdf 提取文本内容
    3. 构建层次化知识节点树 (每行一个知识点)
    4. 自动生成前置/后置/关联关系
    5. 输出符合导入规范的 CSV/Excel 文件

关键输出：A-G列(层级) + H-I-J列(三类关系) + 其他属性列
"""

import argparse
import csv
import subprocess
import sys
import io

# 设置控制台输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill
except ImportError:
    print("Error: openpyxl not installed. Run: pip install openpyxl", file=sys.stderr)
    sys.exit(1)

# ==================== 数据结构定义 ====================

@dataclass
class KnowledgeNode:
    """知识点节点"""
    name: str
    level: int  # 0=A(一级), 1=B(二级), ...
    tags: str = ""
    cognitive_level: str = ""
    category: str = ""
    objective: str = ""
    description: str = ""
    pre_requisites: str = ""  # H列 - 前置知识点
    post_requisites: str = ""  # I列 - 后置知识点  
    related: str = ""          # J列 - 关联知识点
    children: list = field(default_factory=list)

# 韩语动词到认知层级的映射
COGNITIVE_VERB_MAP = {
    # 应用级动词 
    "重点掌握": "应用", "掌握": "应用", "能够": "应用", "会": "应用", 
    "使用": "应用", "操作": "应用", "测量": "应用", "应用": "应用",
    # 理解级动词
    "理解": "理解", "明白": "理解", "解释": "理解", "说明": "理解",
    "阐述": "理解", "区分": "理解", "分类": "理解", "比较": "理解",
    # 记忆级动词
    "了解": "记忆", "知道": "记忆", "说出": "记忆", "认识": "记忆", 
    "识别": "记忆", "回忆": "记忆", "列举": "记忆",
    # 分析级动词
    "分析": "分析", "比较": "分析", "分解": "分析", "识别": "分析",
    # 评价级动词
    "评价": "评价", "判断": "评价", "选择": "评价", "评估": "评价",
    # 创造级动词
    "设计": "创造", "创建": "创造", "制定": "创造", "提出": "创造",
}

# ==================== 认知维度判断 ====================

def get_cognitive_level(verb: str) -> str:
    """根据动词判断认知维度"""
    if not verb:
        return "理解"
    verb_lower = verb.lower()
    
    for keyword, level in COGNITIVE_VERB_MAP.items():
        if keyword in verb_lower:
            return level
    return "理解"

def get_category(topic: str, description: str) -> str:
    """判断知识点分类"""
    proc_keywords = ["操作", "使用", "测量", "实施", "编写", "方法", "步骤", "程序"]
    concept_keywords = ["概念", "定义", "原理", "理论", "组成", "结构", "模型"]
    
    text = f"{topic} {description}".lower()
    for kw in proc_keywords:
        if kw in text:
            return "程序性"
    for kw in concept_keywords:
        if kw in text:
            return "概念性"
    return "概念性"

def get_tags(verb: str) -> str:
    """生成标签"""
    if not verb:
        return ""
    v = verb.lower()
    tags = []
    if "重点掌握" in v:
        tags.extend(["重点", "考点"])
    elif "掌握" in v:
        tags.append("考点")
    return ";".join(tags) if tags else ""

# ==================== 文档解析 ====================

def parse_docx(filepath: str) -> str:
    """解析 docx 文档 - 使用 python-docx"""
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

def parse_pdf(filepath: str) -> str:
    """解析 PDF 文档"""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                text_parts.append(text)
        return "\n".join(text_parts)
    except ImportError:
        print("Error: pdfplumber not installed. Run: pip install pdfplumber", file=sys.stderr)
        return ""

# ==================== 模板解析 ====================

def parse_template(filepath: str) -> dict:
    """解析 xlsx 模板，返回格式规则"""
    wb = load_workbook(filepath)
    ws = wb.active
    
    # 读取 A1 单元格的格式要求
    a1_value = ws['A1'].value or ""
    
    # 读取表头
    headers = []
    if ws.max_row > 1:
        headers = [ws.cell(row=2, column=i).value for i in range(1, min(16, ws.max_column + 1))]
    
    return {
        "a1_rules": a1_value,
        "headers": headers,
        "max_column": ws.max_column,
        "sheet_name": ws.title
    }

# ==================== 知识点树构建 ====================

class KnowledgeTreeBuilder:
    """知识点树构建器"""
    
    def __init__(self, root_name: str = "知识点"):
        self.root = KnowledgeNode(root_name, 0)
        self.all_nodes: Dict[str, KnowledgeNode] = {root_name: self.root}
    
    def add_node(self, name: str, level: int, parent_name: str = None, **kwargs) -> KnowledgeNode:
        """添加知识点节点"""
        node = KnowledgeNode(name, level, **kwargs)
        self.all_nodes[name] = node
        
        if parent_name and parent_name in self.all_nodes:
            self.all_nodes[parent_name].children.append(node)
        elif level > 0:
            # Auto-link to parent: find highest-level ancestor
            max_level = max(n.level for n in self.all_nodes.values()) if self.all_nodes else 0
            potential_parents = [
                n for n in self.all_nodes.values() 
                if n.level < level and n.level >= max_level
            ]
            # Find the closest parent (highest in tree with lower level than our node)
            possible_parents = [n for n in self.all_nodes.values() if n.level == level-1]
            if possible_parents:
                for possible in possible_parents:
                    parent_path = possible.name.replace(' ', '').replace('\u2018', '').replace('\u2019', '').replace('\u201c', '').replace('\u201d', '').lower()
                    node_path = name.replace(' ', '').replace('\u2018', '').replace('\u2019', '').replace('\u201c', '').replace('\u201d', '').lower()
                    if node_path.startswith(parent_path) or parent_path in node_path:
                        possible.children.append(node)
                        break
                else:
                    # If not matched by content, just attach to last found
                    possible_parents[-1].children.append(node)
        
        return node
    
    def set_relations(self, pre_relations: Dict[str, str], related_relations: Dict[str, str]):
        """设置关系"""
        # 设置前詈关系
        for name, pre_list in pre_relations.items():
            if name in self.all_nodes and pre_list:
                self.all_nodes[name].pre_requisites = pre_list
        
        # 设置后置关系（前置的反向）
        post_relations: Dict[str, List[str]] = {}
        for name, pre_str in pre_relations.items():
            if pre_str:
                pre_list = [p.strip() for p in pre_str.split(";") if p.strip()]
                for pre_topic in pre_list:
                    if pre_topic not in post_relations:
                        post_relations[pre_topic] = []
                    post_relations[pre_topic].append(name)
        
        for name, post_list in post_relations.items():
            if name in self.all_nodes:
                self.all_nodes[name].post_requisites = ";".join(post_list)
        
        # 设置关联关系
        for name, related_list in related_relations.items():
            if name in self.all_nodes and related_list:
                self.all_nodes[name].related = related_list
    
    def flatten(self) -> List[Dict]:
        """将树扁平化为行数据"""
        rows = []
        self._flatten(self.root, rows)
        return rows
    
    def _flatten(self, node: KnowledgeNode, rows: List[Dict]):
        """递归扁平化节点"""
        level_to_col = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G"}
        
        # 创建行数据
        row = {col: "" for col in "ABCDEFG"}
        if node.level in level_to_col:
            row[level_to_col[node.level]] = node.name
        
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
        
        # 递归处理子节点
        for child in node.children:
            self._flatten(child, rows)

# ==================== Excel/CSV 生成 ====================

def generate_excel(rows: List[Dict], output_path: str, template_rules: str = ""):
    """生成 Excel 文件"""
    wb = Workbook()
    ws = wb.active
    ws.title = "知识点抽取结果"
    
    # 第1行：使用说明
    instructions = template_rules or """使用说明：
1. A列至G列对应知识点的层级关系，区间内每行只能填写一个知识点
2. H列至J列填写对应知识点的前置、后置和关联知识点，多个知识点之间用英文分号";"隔开
3. 任意两个知识点之间只能存在一种关系（前提、后置或关联），新导入的关系将覆盖旧关系，关系设置总数上限为2000个
4. 固定标签包括：重点、难点、考点、课程思政，可根据需要自定义标签，多个标签之间用英文分号";"隔开
5. 认知维度包括：记忆、理解、应用、分析、评价、创造，每个知识点只能填入一个认知维度
6. 知识点分类包括：亊实性、概念性、程序性、元认知，每个知识点只能填入一个分类
7. 知识点说明仅支持输入文本，暂不支持图片、公式等
8. 请不要删除此行，也不偠删除模版中的任何列"""
    
    ws['A1'] = instructions
    ws.merge_cells('A1:O1')
    ws['A1'].alignment = Alignment(wrap_text=True, vertical='top')
    
    # 表头
    headers = ['一级知识点', '二级知识点', '三级知识点', '四级知识点', '五级知识点',
               '六级知识点', '七级知识点', '前置知识点', '后置知识点', '关联知识点',
               '标签', '认知维度', '分类', '教学目标', '知识点说明']
    
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col_idx, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # 列宽
    col_widths = {
        'A': 25, 'B': 20, 'C': 25, 'D': 25, 'E': 25, 'F': 15, 'G': 15,
        'H': 35, 'I': 35, 'J': 35, 'K': 15, 'L': 12, 'M': 12, 'N': 35, 'O': 40
    }
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width
    
    # 数据
    for row_idx, row_data in enumerate(rows, 3):
        for col_idx, key in enumerate(['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'], 1):
            ws.cell(row=row_idx, column=col_idx, value=row_data.get(key) or "")
    
    wb.save(output_path)
    print(f"Excel 文件已保存: {output_path}")

def generate_csv(rows: List[Dict], output_path: str, template_rules: str = ""):
    """生成 CSV 文件"""
    headers = ['一级知识点', '二级知识点', '三级知识点', '四级知识点', '五级知识点',
               '六级知识点', '七级知识点', '前置知识点', '后置知识点', '关联知识点',
               '标签', '认知维度', '分类', '教学目标', '知识点说明']
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row_data in rows:
            writer.writerow([
                row_data.get('A', ''), row_data.get('B', ''), row_data.get('C', ''), 
                row_data.get('D', ''), row_data.get('E', ''), row_data.get('F', ''), 
                row_data.get('G', ''), row_data.get('H', ''), row_data.get('I', ''), 
                row_data.get('J', ''), row_data.get('K', ''), row_data.get('L', ''), 
                row_data.get('M', ''), row_data.get('N', ''), row_data.get('O', '')
            ])
    
    print(f"CSV 文件已保存: {output_path}")

# ==================== 验证 ====================

def validate_rows(rows: List[Dict]) -> List[str]:
    """验证行数据是否符合约束"""
    errors = []
    
    for i, row in enumerate(rows, 3):
        # 验证 A-G 列：每行只能有一个知识点
        level_vals = [row.get(col, "") for col in 'ABCDEFG']
        non_empty_count = sum(1 for val in level_vals if val)
        if non_empty_count != 1:
            errors.append(f"行 {i}: 每行应只有1个知识点，实际{non_empty_count}个")
        
        # 验证认知维度（单选）
        cognitive = row.get('L', '')
        if cognitive and cognitive not in ["记忆", "理解", "应用", "分析", "评价", "创造"]:
            errors.append(f"行 {i}: L列(认知维度)值无效: {cognitive}")
        
        # 验证分类（单选）
        category = row.get('M', '')
        if category and category not in ["事实性", "概念性", "程序性", "元认知"]:
            errors.append(f"行 {i}: M列(分类)值无效: {category}")
    
    return errors

# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description='文档知识图谱结构化抽取')
    parser.add_argument('--source', help='源文档路径 (docx/pdf)')
    parser.add_argument('--template', required=True, help='xlsx 模板路径')
    parser.add_argument('--output', help='输出文件路径 (xlsx/csv)')
    parser.add_argument('--dry-run', action='store_true', help='仅解析模板，不生成输出')
    args = parser.parse_args()
    
    # 1. 解析模板
    print("步骤1: 解析模板...")
    template = parse_template(args.template)
    print(f"  模板列数: {template['max_column']}")
    print()
    
    if args.dry_run:
        print("Dry run 完成。")
        return
    
    if not args.source or not args.output:
        print("错误: 需要指定 --source 和 --output 参数", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # 2. 解析源文档
    print("步骤2: 解析源文档...")
    if args.source.endswith('.docx'):
        content = parse_docx(args.source)
    elif args.source.endswith('.pdf'):
        content = parse_pdf(args.source)
    else:
        print(f"错误: 不支持的文档格式: {args.source}", file=sys.stderr)
        sys.exit(1)
    print(f"  内容长度: {len(content)} 字符")
    print()
    
    # 3. 构建知识点树
    print("步骤3: 构建知识点树...")
    
    # 根据文档内容自动识别专业类别并构建知识树
    # Extract subject from filename or content
    import re
    import os
    
    subject = os.path.basename(args.source).split('.')[0]
    if '土木水利' in subject:
        builder = KnowledgeTreeBuilder("土木水利类专业知识")
        root_name = "土木水利类专业知识"
    elif '纺织服装' in subject:
        builder = KnowledgeTreeBuilder("纺织服装类专业知识")
        root_name = "纺织服装类专业知识"
    else:
        builder = KnowledgeTreeBuilder("专业知识")
        root_name = "专业知识"
    
    print(f"  已初始化知识树构建器: {root_name}")
    
    # 4. 解析并添加知识点
    print("步骤4: 解析文档内容...")
    
    # 解析文档结构 - 识别层级关系
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # 识别知识点层级
    knowledge_nodes = []  # (level, identifier, name, attrs)
    current_chapters = {}  # {level: name}
    
    # Track current parent at each level
    parent_stack = {root_name: 0}
    
    for line in lines:
        # Skip non-content lines
        if line in ['(2023年版)', '— 2—', '— 3—', '— 4—', '— 5—', '— 6—', '第 2页']:
            continue
        
        # Skip pure percentages and non-knowledge lines
        if '%' in line and len(line) < 30 and ('占' in line or '约占' in line):
            continue
        if '约占' in line and len(line) < 40:
            continue
        if any(skip in line for skip in ['选择题', '判断题', '综合题', '试卷结构']):
            continue
            
        # Match 一、二、三、 Chinese numerals with 、 (but only for major sections)
        # Skip common non-knowledge headings
        chinese_num_match = re.match(r'^([一二三四五六七八九十]+)[、]\s*(.+)$', line)
        if chinese_num_match:
            roman = chinese_num_match.group(1)
            name = chinese_num_match.group(2).strip()
            # Skip common administrative headings
            if name in ['考试性质', '考试依据', '考试方式', '考试范围和要求']:
                continue
            if name and len(name) > 1:
                roman_map = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
                level = 1  # 一、 topics are 一级 (A列)
                current_chapters[level] = name
                knowledge_nodes.append((level, roman, name, {}))
                continue
        
        # Match 【xxx】 brackets - major sections (level 1 -> A)
        bracket_match = re.match(r'【(.+)】', line)
        if bracket_match:
            name = bracket_match.group(1).strip()
            if name and len(name) > 1:
                current_chapters[1] = name
                knowledge_nodes.append((1, name, name, {}))
                continue
        
        # Match (一)、(二)、(三) - Chinese roman numerals in parentheses (level 2 -> B)
        chapter_match = re.match(r'^\(([一二三四五六七八九十]+)\)[，。、\s]*(.+)$', line)
        if chapter_match:
            roman = chapter_match.group(1)
            name = chapter_match.group(2).strip()
            if name and len(name) > 1:
                roman_map = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
                # This is level 2 (B列)
                level = 2
                current_chapters[level] = name
                knowledge_nodes.append((level, roman, name, {}))
                continue
        
        # Match 1.、2.、3. pattern - main topics (level 2 -> B)
        num_match = re.match(r'^(\d+)[.、]\s*(.+)$', line)
        if num_match:
            num = num_match.group(1)
            name = num_match.group(2).strip()
            # Skip if contains special patterns or is too short
            if '%' in name or '约占' in name or '约' in name or len(name) < 3:
                continue
            if name:
                level = 2  # 1. topics are 二级 (B列)
                current_chapters[level] = name
                knowledge_nodes.append((level, num, name, {}))
                continue
        
        # Match (1)、(2)、(3) - sub topics (level 3 -> C)
        sub_match = re.match(r'^\((\d+)\)[，。、\s]*(.+)$', line)
        if sub_match:
            num = sub_match.group(1)
            name = sub_match.group(2).strip()
            if name and len(name) > 2:
                level = 3  # (1) topics are 三级 (C列)
                # Check if this line contains cognitive verbs
                attrs = {}
                for verb in ["重点掌握", "掌握", "理解", "了解", "应用", "分析", "评价", "创造"]:
                    if verb in name:
                        attrs["cognitive_level"] = get_cognitive_level(verb)
                        attrs["tags"] = get_tags(verb)
                        attrs["category"] = get_category(name, name)
                        break
                knowledge_nodes.append((level, num, name, attrs))
                continue
        
        # If line contains cognitive verbs but wasn't matched by patterns above
        # This might be D-level knowledge items (四级知识点)
        if len(line) > 10:
            attrs = {}
            has_cognitive_verb = False
            for verb in ["重点掌握", "掌握", "理解", "了解", "应用", "分析", "评价", "创造"]:
                if verb in line:
                    attrs["cognitive_level"] = get_cognitive_level(verb)
                    attrs["tags"] = get_tags(verb)
                    attrs["category"] = get_category(line, line)
                    has_cognitive_verb = True
                    break
            
            if has_cognitive_verb:
                # Try to find appropriate level based on context
                if len(knowledge_nodes) > 0:
                    last_level = knowledge_nodes[-1][0]
                    if last_level == 3:  # Last was C-level, this is D-level
                        level = 4  # D列
                    elif last_level == 2:  # Last was B-level, this might be C-level continuation
                        level = 3  # C列
                    else:
                        level = last_level + 1 if last_level < 7 else 7
                else:
                    level = 3  # Default to C-level
                
                knowledge_nodes.append((level, "", line, attrs))
    
    # Build knowledge tree - map levels to A-G columns
    # Level 1 -> A, Level 2 -> B, etc.
    level_to_col = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G'}
    
    # Debug: print first 10 nodes being added
    print(f"  前10个节点:")
    for i, (level, num, name, attrs) in enumerate(knowledge_nodes[:10]):
        print(f"    {i+1}: 层级{level} '{name[:50]}...' 属性: {attrs}")
    
    for level, num, name, attrs in knowledge_nodes:
        # Find parent - look for the most recent node at a lower level
        parent_name = None
        parent_level = -1
        for p_name, p_level in sorted(parent_stack.items(), key=lambda x: x[1], reverse=True):
            if p_level < level:
                parent_level = p_level
                parent_name = p_name
                break
        
        # Add node
        builder.add_node(name, level, parent_name, **attrs)
        
        # Update parent stack - keep only the latest at each level
        # Remove any nodes at same or higher level
        for lvl in list(parent_stack.keys()):
            if parent_stack[lvl] >= level:
                del parent_stack[lvl]
        parent_stack[name] = level
    
    print(f"  已解析 {len(knowledge_nodes)} 个知识点节点")
    
    # 5. 自动生成关系（基于层级）
    print("步骤5: 生成知识点关系...")
    
    # 根据父子关系自动生成前置关系
    pre_relations = {}
    rows_temp = builder.flatten()
    
    # 简单的前置关系：同一父节点的子节点之间，后一个的前置是前一个
    parent_children = {}
    for row in rows_temp:
        for col in 'ABCDEFG':
            if row.get(col):
                node_name = row[col]
                # 找父级
                for parent_col in 'ABCDEFG':
                    parent_val = row.get(parent_col, '')
                    if parent_val and parent_val != node_name:
                        if parent_val not in parent_children:
                            parent_children[parent_val] = []
                        if node_name not in parent_children[parent_val]:
                            parent_children[parent_val].append(node_name)
    
    # 生成前置关系
    for parent, children in parent_children.items():
        if len(children) > 1:
            # Sort children to maintain order (based on parsing order)
            for i, child in enumerate(children):
                if i > 0:
                    pre_relations[child] = children[i-1]
    
    builder.set_relations(pre_relations, {})
    print(f"  已生成 {len(pre_relations)} 个前置关系")
    
    # 6. 生成输出
    print("步骤6: 生成输出文件...")
    rows = builder.flatten()
    
    # 同时生成 CSV 备份
    csv_path = args.output.replace('.xlsx', '.csv') if args.output.endswith('.xlsx') else args.output
    if not args.output.endswith('.csv'):
        print(f"  步骤6.1: 生成 CSV 备份文件...")
        generate_csv(rows, csv_path, template['a1_rules'])
        print(f"  CSV 备份文件已保存: {csv_path}")
    
    if args.output.endswith('.csv'):
        generate_csv(rows, args.output, template['a1_rules'])
    else:
        generate_excel(rows, args.output, template['a1_rules'])
    
    # 6. 验证与输出统计
    print("步骤5: 输出验证...")
    errors = validate_rows(rows)
    if errors:
        print(f"  ❌ 发现 {len(errors)} 个错误:")
        for i, err in enumerate(errors[:5], 1):
            print(f"     {i}. {err}")
        if len(errors) > 5:
            print(f"     ... 还有 {len(errors)-5} 个错误")
    else:
        print("  ✅ 验证通过")
    
    print()
    print("=" * 60)
    print("抽取结果概要")
    print("=" * 60)
    
    h_count = sum(1 for r in rows if r.get('H'))
    i_count = sum(1 for r in rows if r.get('I'))
    j_count = sum(1 for r in rows if r.get('J'))
    
    print(f"""
知识点统计:
  - 节点总数: {len(rows)} 条
  - 层级深度: 5 级（部分示例）

关系统计:
  - 前置关系(H列): {h_count} 条
  - 后置关系(I列): {i_count} 条
  - 关联关系(J列): {j_count} 条

格式验证:
  - 树状结构(每行一个知识点): {all(sum(1 for c in 'ABCDEFG' if r.get(c)) == 1 for r in rows)}
  - 认知维度合规: {all(r.get('L', '') in ["记忆", "理解", "应用", "分析", "评价", "创造"] or not r.get('L') for r in rows)}
  - 知识点分类合规: {all(r.get('M', '') in ["事实性", "概念性", "程序性", "元认知"] or not r.get('M') for r in rows)}

文件输出:
  - 输出路径: {args.output}
""")

if __name__ == "__main__":
    main()
