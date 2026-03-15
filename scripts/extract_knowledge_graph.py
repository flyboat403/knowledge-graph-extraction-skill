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

关键输出：A-G列(层级) + H-I-J列(三类关系) + 其他属性列
"""

import argparse
import csv
import subprocess
import sys
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
    """解析 docx 文档"""
    try:
        result = subprocess.run(
            ["pandoc", filepath, "-t", "markdown"], 
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"pandoc warning: {result.stderr}", file=sys.stderr)
        return result.stdout
    except FileNotFoundError:
        print("Error: pandoc not installed. Run: apt-get install pandoc", file=sys.stderr)
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
            potential_parents = [
                n for n in self.all_nodes.values() 
                if n.level < level and n.level >= max(n.level for n in self.all_nodes.values()) if self.all_nodes else 0
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
            self._flatten_node(child, rows)

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

def generate_csv(rows: List[Dict], output_path: str):
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
    
    # 3. 构建知识点树（这里需要根据实际文档内容实现）
    print("步骤3: 构建知识点树...")
    print("  (注意: 这里需要根据实际文档内容实现具体抽取逻辑)")
    
    # 4. 使用示例数据创建知识树
    builder = KnowledgeTreeBuilder("知识点")
    
    # 示例层级关系
    level1 = builder.add_node("电子信息类职业技能考试", 0)
    level2_1 = builder.add_node("专业知识(应知)", 1, "电子信息类职业技能考试")
    level2_2 = builder.add_node("技能操作(应会)", 1, "电子信息类职业技能考试")
    
    # 示例电工知识点层级（部分）
    dian_gong = builder.add_node("电工技术基础与技能", 2, "专业知识(应知)")
    an_quan_yong_dian = builder.add_node("安全用电常识", 3, "电工技术基础与技能")
    builder.add_node("触电种类和形式", 4, "安全用电常识", cognitive_level=get_cognitive_level("掌握"))
    builder.add_node("安全用电的技术措施和制度措施", 4, "安全用电常识", cognitive_level=get_cognitive_level("重点掌握"))
    builder.add_node("触电的急救方法", 4, "安全用电常识", cognitive_level=get_cognitive_level("了解"))
    
    dian_lu_ji_chu = builder.add_node("电路基础", 3, "电工技术基础与技能")
    builder.add_node("电路组成及三种状态", 4, "电路基础", cognitive_level=get_cognitive_level("理解"))
    builder.add_node("常用元器件图形符号", 4, "电路基础", cognitive_level=get_cognitive_level("掌握"))
    
    # 示例电子知识点层级
    dian_zi = builder.add_node("电子技术基础与技能", 2, "专业知识(应知)")
    ban_dao_ti = builder.add_node("半导体的主要特性", 3, "电子技术基础与技能")
    builder.add_node("半导体的概念、特性", 4, "半导体的主要特性", cognitive_level=get_cognitive_level("了解"))
    builder.add_node("P型、N型半导体", 4, "半导体的主要特性", cognitive_level=get_cognitive_level("了解"))
    builder.add_node("PN结的特性", 4, "半导体的主要特性", cognitive_level=get_cognitive_level("掌握"))
    
    # 示例单片机知识点层级
    dan_pian_ji = builder.add_node("单片机原理及应用", 2, "专业知识(应知)")
    dan_pian_ji_gai_shu = builder.add_node("单片机概述", 3, "单片机原理及应用")
    builder.add_node("单片机的发展与分类", 4, "单片机概述", cognitive_level=get_cognitive_level("了解"))
    
    # 示例技能操作知识点
    dian_gong_ji_neng = builder.add_node("电工技术基础与技能", 2, "技能操作(应会)")
    builder.add_node("安全用电常识与操作规范", 3, "电工技术基础与技能", cognitive_level="应用", category="程序性")
    
    dian_zi_ji_neng = builder.add_node("电子技术基础与技能", 2, "技能操作(应会)")
    builder.add_node("常用电子元器件的识别、选用与测试", 3, "电子技术基础与技能", cognitive_level="应用", category="程序性")
    
    dan_pian_ji_ji_neng = builder.add_node("单片机原理及应用", 2, "技能操作(应会)")
    builder.add_node("STC51单片机最小系统程序设计", 3, "单片机原理及应用", cognitive_level="应用", category="程序性")
    
    # 设置示例关系
    pre_relations = {
        "安全用电的技术措施和制度措施": "触电种类和形式",
        "电路组成及三种状态": "安全用电常识",
        "常用元器件图形符号": "电路组成及三种状态",
        "P型、N型半导体": "半导体的概念、特性",
        "PN结的特性": "P型、N型半导体",
    }
    related_relations = {
        "触电种类和形式": "安全用电的技术措施和制度措施",
        "电路组成及三种状态": "常用元器件图形符号",
        "P型、N型半导体": "PN结的特性"
    }
    builder.set_relations(pre_relations, related_relations)
    
    # 5. 生成输出
    print("步骤4: 生成输出文件...")
    rows = builder.flatten()
    
    if args.output.endswith('.csv'):
        generate_csv(rows, args.output)
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