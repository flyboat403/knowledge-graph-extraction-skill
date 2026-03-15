#!/usr/bin/env python3
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
"""

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill


@dataclass
class KnowledgeNode:
    name: str
    level: int
    tags: str = ""
    cognitive_level: str = ""
    category: str = ""
    objective: str = ""
    description: str = ""
    pre_requisites: str = ""
    post_requisites: str = ""
    related: str = ""
    children: List = field(default_factory=list)


COGNITIVE_VERB_MAP = {
    "重点掌握": "应用", "掌握": "应用", "能够": "应用",
    "理解": "理解", "说明": "理解", "解释": "理解",
    "了解": "记忆", "知道": "记忆",
    "分析": "分析", "比较": "分析",
    "评价": "评价", "判断": "评价",
    "设计": "创造", "规划": "创造",
}


def get_cognitive_level(verb: str) -> str:
    if not verb:
        return "理解"
    v = verb.lower()
    for kw, level in COGNITIVE_VERB_MAP.items():
        if kw in v:
            return level
    return "理解"


def get_category(topic: str, desc: str) -> str:
    text = f"{topic} {desc}".lower()
    for kw in ["操作", "使用", "测量", "配置", "编写"]:
        if kw in text:
            return "程序性"
    for kw in ["概念", "原理", "定义", "结构", "模型"]:
        if kw in text:
            return "概念性"
    return "概念性"


def get_tags(verb: str) -> str:
    if not verb:
        return ""
    v = verb.lower()
    return "重点;考点" if "重点掌握" in v else "考点" if "掌握" in v else ""


def parse_docx(filepath: str) -> str:
    result = subprocess.run(["pandoc", filepath, "-t", "markdown"], capture_output=True, text=True, timeout=60)
    return result.stdout if result.returncode == 0 else ""


def parse_pdf(filepath: str) -> str:
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except ImportError:
        print("Error: pip install pdfplumber", file=sys.stderr)
        sys.exit(1)


def parse_template(filepath: str) -> Dict:
    wb = load_workbook(filepath)
    ws = wb.active
    return {
        "a1_rules": ws['A1'].value or "",
        "headers": [ws.cell(row=2, column=i).value for i in range(1, 16)],
        "max_column": ws.max_column,
    }


class KnowledgeTreeBuilder:
    def __init__(self, root_name: str = "知识点"):
        self.root = KnowledgeNode(root_name, 0)
        self.all_nodes: Dict[str, KnowledgeNode] = {root_name: self.root}
    
    def add_node(self, name: str, level: int, parent_name: str = None, **kwargs) -> KnowledgeNode:
        node = KnowledgeNode(name, level, **kwargs)
        self.all_nodes[name] = node
        if parent_name and parent_name in self.all_nodes:
            self.all_nodes[parent_name].children.append(node)
        return node
    
    def set_relations(self, pre_relations: Dict[str, str], related_relations: Dict[str, str]):
        for name, pre_list in pre_relations.items():
            if name in self.all_nodes:
                self.all_nodes[name].pre_requisites = pre_list
        
        post: Dict[str, List[str]] = {}
        for name, pre_list in pre_relations.items():
            for p in pre_list.split(";"):
                p = p.strip()
                if p:
                    post.setdefault(p, []).append(name)
        for name, pl in post.items():
            if name in self.all_nodes:
                self.all_nodes[name].post_requisites = ";".join(pl)
        
        for name, rel in related_relations.items():
            if name in self.all_nodes:
                self.all_nodes[name].related = rel
    
    def flatten(self) -> List[Dict]:
        rows = []
        self._flatten(self.root, rows)
        return rows
    
    def _flatten(self, node: KnowledgeNode, rows: List[Dict]):
        col = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G"}
        row = {c: "" for c in "ABCDEFG"}
        if node.level in col:
            row[col[node.level]] = node.name
        row.update({
            "H": node.pre_requisites, "I": node.post_requisites, "J": node.related,
            "K": node.tags, "L": node.cognitive_level, "M": node.category,
            "N": node.objective, "O": node.description
        })
        rows.append(row)
        for c in node.children:
            self._flatten(c, rows)


INSTRUCTIONS = """使用说明：
1. A列至G列对应知识点的层级关系，区间内每行只能填写一个知识点
2. H列至J列填写对应知识点的前置、后置和关联知识点，多个知识点之间用英文分号";"隔开
3. 任意两个知识点之间只能存在一种关系（前置、后置或关联），新导入的关系将覆盖旧关系，关系设置总数上限为2000个
4. 固定标签包括：重点、难点、考点、课程思政，可根据需要自定义标签，多个标签之间用英文分号";"隔开
5. 认知维度包括：记忆、理解、应用、分析、评价、创造，每个知识点只能填入一个认知维度
6. 知识点分类包括：事实性、概念性、程序性、元认知，每个知识点只能填入一个分类
7. 知识点说明仅支持输入文本，暂不支持图片、公式等
8. 请不要删除此行，也不要删除模板中的任何列"""


def generate_excel(rows: List[Dict], output_path: str, rules: str = ""):
    wb = Workbook()
    ws = wb.active
    ws.title = "知识点抽取结果"
    
    ws['A1'] = rules or INSTRUCTIONS
    ws.merge_cells('A1:O1')
    ws['A1'].alignment = Alignment(wrap_text=True, vertical='top')
    
    headers = ['一级知识点','二级知识点','三级知识点','四级知识点','五级知识点','六级知识点','七级知识点',
               '前置知识点','后置知识点','关联知识点','标签','认知维度','分类','教学目标','知识点说明']
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=2, column=i, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        c.alignment = Alignment(horizontal='center')
    
    for w, v in [('A',25),('B',20),('C',25),('D',25),('E',25),('F',15),('G',15),
                 ('H',35),('I',35),('J',35),('K',15),('L',12),('M',12),('N',35),('O',40)]:
        ws.column_dimensions[w].width = v
    
    for ri, r in enumerate(rows, 3):
        for ci, k in enumerate(['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'], 1):
            ws.cell(row=ri, column=ci, value=r.get(k, ""))
    
    wb.save(output_path)


def generate_csv(rows: List[Dict], output_path: str):
    headers = ['一级知识点','二级知识点','三级知识点','四级知识点','五级知识点','六级知识点','七级知识点',
               '前置知识点','后置知识点','关联知识点','标签','认知维度','分类','教学目标','知识点说明']
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in rows:
            w.writerow([r.get(k, "") for k in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O']])


def main():
    p = argparse.ArgumentParser(description='文档知识图谱结构化抽取')
    p.add_argument('--source', help='源文档 (docx/pdf)')
    p.add_argument('--template', required=True, help='xlsx模板')
    p.add_argument('--output', help='输出文件 (xlsx/csv)')
    p.add_argument('--dry-run', action='store_true', help='仅解析模板')
    args = p.parse_args()
    
    print("=" * 60)
    print("步骤1: 解析模板...")
    template = parse_template(args.template)
    print(f"  列数: {template['max_column']}, A1规则: {len(template['a1_rules'])}字符")
    
    if args.dry_run:
        return
    
    if not args.source or not args.output:
        print("Error: 需要 --source 和 --output", file=sys.stderr)
        sys.exit(1)
    
    print("步骤2: 解析源文档...")
    content = parse_docx(args.source) if args.source.endswith('.docx') else parse_pdf(args.source)
    print(f"  内容: {len(content)} 字符")
    
    print("步骤3: 构建知识点树...")
    builder = KnowledgeTreeBuilder("知识点")
    # 用户根据文档内容添加节点
    
    print("步骤4: 生成输出...")
    rows = builder.flatten()
    generate_csv(rows, args.output) if args.output.endswith('.csv') else generate_excel(rows, args.output, template['a1_rules'])
    print(f"  输出: {args.output}")
    
    print(f"\n完成! 知识点: {len(rows)}")


if __name__ == "__main__":
    main()