#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
import copy

def col_letter_to_index(letter):
    """将列字母转换为索引（A=0, B=1, ...）"""
    index = 0
    for char in letter:
        index = index * 26 + (ord(char) - ord('A') + 1)
    return index - 1

def parse_cell_ref(cell_ref):
    """解析单元格引用，如'B2' -> (col=1, row=1)"""
    col = ''
    row = ''
    for char in cell_ref:
        if char.isalpha():
            col += char
        else:
            row += char
    return (col_letter_to_index(col), int(row) - 1)

def update_cell_value(row_elem, col, value):
    """更新单元格值"""
    # 生成单元格引用（如 B2）
    col_letter = ''
    temp = col + 1
    while temp > 0:
        temp -= 1
        col_letter = chr(temp % 26 + ord('A')) + col_letter
        temp //= 26
    cell_ref = col_letter + str(row_elem.get('r'))
    
    # 查找现有单元格
    for cell in row_elem:
        if cell.tag.endswith('}c') and cell.get('r') == cell_ref:
            # 更新现有单元格
            cell.set('t', 's')  # 设置为共享字符串类型
            # 查找或创建v元素
            v_elem = None
            for child in cell:
                if child.tag.endswith('}v'):
                    v_elem = child
                    break
            if v_elem is None:
                v_elem = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                cell.append(v_elem)
            v_elem.text = str(value)
            return cell_ref, True  # 返回单元格引用和是否是新创建的
    
    # 创建新单元格
    cell = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c')
    cell.set('r', cell_ref)
    cell.set('t', 's')
    cell.set('s', '1')  # 使用样式1
    
    v_elem = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
    v_elem.text = str(value)
    cell.append(v_elem)
    
    row_elem.append(cell)
    return cell_ref, False

def add_shared_string(z, new_string):
    """添加新的共享字符串，返回索引"""
    with z.open('xl/sharedStrings.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
        # 查找是否已存在该字符串
        idx = 0
        for si in root.iter():
            if si.tag.endswith('}si'):
                t = si.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                if t is not None and t.text == new_string:
                    return idx, False  # 已存在
                idx += 1
        
        # 不存在，添加新字符串
        si = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si')
        t = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
        t.text = new_string
        si.append(t)
        root.append(si)
        
        # 更新count和uniqueCount属性
        count = int(root.get('count', 0)) + 1
        unique_count = int(root.get('uniqueCount', 0)) + 1
        root.set('count', str(count))
        root.set('uniqueCount', str(unique_count))
        
        # 返回新字符串的索引
        return idx, True  # 新创建

try:
    # 打开原始文件
    input_file = '/root/.openclaw/media/inbound/923dcee7-788e-4d49-9bbd-d0d2e751803f.xlsx'
    output_file = '/root/.openclaw/media/inbound/崔晓洋岗位说明书_已填写.xlsx'
    
    with zipfile.ZipFile(input_file, 'r') as z:
        # 读取共享字符串表
        with z.open('xl/sharedStrings.xml') as f:
            shared_tree = ET.parse(f)
            shared_root = shared_tree.getroot()
        
        # 读取工作表1
        with z.open('xl/worksheets/sheet1.xml') as f:
            sheet_tree = ET.parse(f)
            sheet_root = sheet_tree.getroot()
        
        # 添加新的共享字符串
        print("添加共享字符串...")
        
        # 基本情况
        new_strings = [
            "崔晓洋",  # 岗位名称
            "副经理",  # 岗位职级
            "FY-IT-001",  # 岗位编号
            "财务部-信息组",  # 所属部门
            "财务总监",  # 直接上级岗位名称
            "无",  # 直接下属岗位名称
            "0",  # 直接下属人数
            "1人",  # 团队规模
        ]
        
        # 主要工作职责及目标描述
        new_strings.extend([
            "负责公司ERP系统的开发、维护与优化，推动财务信息化建设，提升数据处理和分析效率，为公司决策提供数据支持。",  # 岗位设置目的
            "1. ERP系统开发与维护：负责公司ERP系统的功能开发、代码维护和性能优化。\n2. 财务信息化建设：推动财务业务流程信息化，开发财务相关的应用系统。\n3. 数据报表开发：设计和开发各类数据报表，满足财务分析和决策需求。\n4. 系统故障处理：及时响应和处理系统运行中的问题，确保系统稳定运行。\n5. 技术支持与培训：为财务部门提供技术支持和系统使用培训。",  # 岗位工作职责及内容
        ])
        
        # 专业力要求
        new_strings.extend([
            "本科及以上学历，计算机相关专业",  # 学历及专业
            "25-35岁",  # 年龄要求
            "公司总部",  # 工作地点
            "1. 熟练掌握至少一种编程语言（如Java、Python、C#等）\n2. 熟悉数据库设计和优化，熟练使用SQL\n3. 了解ERP系统原理，有ERP系统开发经验优先\n4. 熟悉财务业务流程者优先",  # 知识技能要求
            "1. 3年以上相关工作经验\n2. 有ERP系统开发或财务信息化项目经验优先\n3. 具备良好的沟通能力和问题解决能力",  # 经验能力要求
        ])
        
        string_indices = {}
        for i, new_string in enumerate(new_strings):
            idx, is_new = add_shared_string(z, new_string)
            string_indices[i] = idx
            if is_new:
                print(f"  新增: {new_string[:50]}...")
            else:
                print(f"  已存在: {new_string[:50]}...")
        
        # 更新工作表数据
        print("\n更新工作表数据...")
        
        # 定位到需要更新的行和列
        # 根据模板，填充位置如下：
        # C5: 岗位名称 (row=5, col=2)
        # H5: 岗位职级 (row=5, col=7)
        # J5: 岗位编号 (row=5, col=9)
        # C6: 所属部门 (row=6, col=2)
        # H6: 直接上级岗位名称 (row=6, col=7)
        # J6: 团队规模 (row=6, col=9)
        # C7: 岗位设置目的 (row=7, col=2)
        # C8: 岗位工作职责及内容 (row=8, col=2)
        # C9: 专业力要求标题 (row=9, col=2)
        # C11: 学历及专业 (row=11, col=2)
        # C12: 年龄要求 (row=12, col=2)
        # C13: 工作地点 (row=13, col=2)
        # C14: 知识技能要求 (row=14, col=2)
        # C15: 经验能力要求 (row=15, col=2)
        
        updates = [
            (5, 2, string_indices[0]),    # C5: 岗位名称
            (5, 7, string_indices[1]),    # H5: 岗位职级
            (5, 9, string_indices[2]),    # J5: 岗位编号
            (6, 2, string_indices[3]),    # C6: 所属部门
            (6, 7, string_indices[4]),    # H6: 直接上级岗位名称
            (6, 9, string_indices[7]),    # J6: 团队规模
            (7, 2, string_indices[8]),    # C7: 岗位设置目的
            (8, 2, string_indices[9]),    # C8: 岗位工作职责及内容
            (11, 2, string_indices[10]),  # C11: 学历及专业
            (12, 2, string_indices[11]),  # C12: 年龄要求
            (13, 2, string_indices[12]),  # C13: 工作地点
            (14, 2, string_indices[13]),  # C14: 知识技能要求
            (15, 2, string_indices[14]),  # C15: 经验能力要求
        ]
        
        for row_num, col, value_idx in updates:
            # 查找对应的行
            row_elem = None
            for r in sheet_root.iter():
                if r.tag.endswith('}row') and r.get('r') == str(row_num):
                    row_elem = r
                    break
            
            if row_elem is not None:
                cell_ref, is_new = update_cell_value(row_elem, col, value_idx)
                print(f"  更新 {cell_ref}: 索引={value_idx}, 新单元格={is_new}")
        
        # 创建新的zip文件
        print("\n生成新文件...")
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as z_out:
            # 复制所有文件（除了我们修改的文件）
            for filename in z.namelist():
                if filename not in ['xl/sharedStrings.xml', 'xl/worksheets/sheet1.xml']:
                    z_out.writestr(filename, z.read(filename))
            
            # 写入修改后的文件
            z_out.writestr('xl/sharedStrings.xml', ET.tostring(shared_root, encoding='UTF-8', xml_declaration=True))
            z_out.writestr('xl/worksheets/sheet1.xml', ET.tostring(sheet_root, encoding='UTF-8', xml_declaration=True))
        
        print(f"\n✓ 岗位说明书已生成: {output_file}")
        
        # 打印填写的内容摘要
        print("\n填写内容摘要:")
        print("✓ 岗位名称: 崔晓洋")
        print("✓ 岗位职级: 副经理")
        print("✓ 所属部门: 财务部-信息组")
        print("✓ 岗位设置目的: 已填写")
        print("✓ 岗位工作职责及内容: 已填写")
        print("✓ 学历及专业: 已填写")
        print("✓ 年龄要求: 已填写")
        print("✓ 工作地点: 已填写")
        print("✓ 知识技能要求: 已填写")
        print("✓ 经验能力要求: 已填写")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
