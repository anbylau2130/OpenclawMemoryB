#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
import io

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

def get_shared_string_map(z):
    """获取所有共享字符串，返回字符串到索引的映射"""
    with z.open('xl/sharedStrings.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
        string_map = {}
        idx = 0
        for si in root.iter():
            if si.tag.endswith('}si'):
                t = si.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                if t is not None and t.text:
                    string_map[t.text] = idx
                else:
                    string_map[''] = idx
                idx += 1
        return string_map

def update_shared_strings(tree, new_strings):
    """更新共享字符串表，返回新字符串的索引"""
    root = tree.getroot()
    ns = {'sst': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    # 获取当前所有字符串
    string_map = {}
    idx = 0
    for si in root.findall('sst:si', ns):
        t = si.find('sst:t', ns)
        if t is not None and t.text:
            string_map[t.text] = idx
        idx += 1
    
    # 添加新字符串
    new_indices = {}
    for new_string in new_strings:
        if new_string not in string_map:
            # 创建新的si元素
            si = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si')
            t = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
            t.text = new_string
            si.append(t)
            root.append(si)
            string_map[new_string] = idx
            idx += 1
        
        new_indices[new_string] = string_map[new_string]
    
    # 更新count属性
    root.set('count', str(idx))
    root.set('uniqueCount', str(idx))
    
    return new_indices

def update_sheet(tree, updates):
    """更新工作表单元格"""
    root = tree.getroot()
    
    # 找到sheetData
    sheet_data = root.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData')
    
    for row_num, col, value_idx in updates:
        # 查找对应的行
        row_elem = None
        for r in sheet_data.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            if r.get('r') == str(row_num):
                row_elem = r
                break
        
        if row_elem is None:
            # 创建新行
            row_elem = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')
            row_elem.set('r', str(row_num))
            sheet_data.append(row_elem)
        
        # 查找对应的单元格
        cell_ref = ''
        temp = col + 1
        while temp > 0:
            temp -= 1
            cell_ref = chr(temp % 26 + ord('A')) + cell_ref
            temp //= 26
        cell_ref += str(row_num)
        
        cell_elem = None
        for c in row_elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            if c.get('r') == cell_ref:
                cell_elem = c
                break
        
        if cell_elem is None:
            # 创建新单元格
            cell_elem = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c')
            cell_elem.set('r', cell_ref)
            cell_elem.set('t', 's')  # 共享字符串类型
            cell_elem.set('s', '1')  # 使用样式
            row_elem.append(cell_elem)
        
        # 设置单元格值
        v_elem = cell_elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
        if v_elem is None:
            v_elem = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            cell_elem.append(v_elem)
        v_elem.text = str(value_idx)
        
        print(f"  {cell_ref}: 索引={value_idx}")

try:
    # 打开原始文件
    input_file = '/root/.openclaw/media/inbound/923dcee7-788e-4d49-9bbd-d0d2e751803f.xlsx'
    output_file = '/root/.openclaw/media/inbound/崔晓洋岗位说明书_已填写.xlsx'
    
    with zipfile.ZipFile(input_file, 'r') as z:
        # 读取共享字符串表
        with z.open('xl/sharedStrings.xml') as f:
            shared_tree = ET.parse(f)
        
        # 读取工作表1
        with z.open('xl/worksheets/sheet1.xml') as f:
            sheet_tree = ET.parse(f)
        
        # 准备新字符串
        print("准备新字符串...")
        new_strings = [
            "崔晓洋",  # 岗位名称
            "副经理",  # 岗位职级
            "FY-IT-001",  # 岗位编号
            "财务部-信息组",  # 所属部门
            "财务总监",  # 直接上级岗位名称
            "无",  # 直接下属岗位名称
            "0",  # 直接下属人数
            "1人",  # 团队规模
            "负责公司ERP系统的开发、维护与优化，推动财务信息化建设，提升数据处理和分析效率，为公司决策提供数据支持。",  # 岗位设置目的
            "1. ERP系统开发与维护：负责公司ERP系统的功能开发、代码维护和性能优化。\n2. 财务信息化建设：推动财务业务流程信息化，开发财务相关的应用系统。\n3. 数据报表开发：设计和开发各类数据报表，满足财务分析和决策需求。\n4. 系统故障处理：及时响应和处理系统运行中的问题，确保系统稳定运行。\n5. 技术支持与培训：为财务部门提供技术支持和系统使用培训。",  # 岗位工作职责及内容
            "本科及以上学历，计算机相关专业",  # 学历及专业
            "25-35岁",  # 年龄要求
            "公司总部",  # 工作地点
            "1. 熟练掌握至少一种编程语言（如Java、Python、C#等）\n2. 熟悉数据库设计和优化，熟练使用SQL\n3. 了解ERP系统原理，有ERP系统开发经验优先\n4. 熟悉财务业务流程者优先",  # 知识技能要求
            "1. 3年以上相关工作经验\n2. 有ERP系统开发或财务信息化项目经验优先\n3. 具备良好的沟通能力和问题解决能力",  # 经验能力要求
        ]
        
        for s in new_strings:
            print(f"  - {s[:60]}...")
        
        # 更新共享字符串
        print("\n更新共享字符串...")
        string_indices = update_shared_strings(shared_tree, new_strings)
        print(f"  共享字符串总数: {len(string_indices)}")
        
        # 更新工作表
        print("\n更新工作表单元格...")
        updates = [
            (5, 2, string_indices["崔晓洋"]),    # C5: 岗位名称
            (5, 7, string_indices["副经理"]),    # H5: 岗位职级
            (5, 9, string_indices["FY-IT-001"]),    # J5: 岗位编号
            (6, 2, string_indices["财务部-信息组"]),    # C6: 所属部门
            (6, 7, string_indices["财务总监"]),    # H6: 直接上级岗位名称
            (6, 9, string_indices["1人"]),    # J6: 团队规模
            (7, 2, string_indices["负责公司ERP系统的开发、维护与优化，推动财务信息化建设，提升数据处理和分析效率，为公司决策提供数据支持。"]),    # C7: 岗位设置目的
            (8, 2, string_indices["1. ERP系统开发与维护：负责公司ERP系统的功能开发、代码维护和性能优化。\n2. 财务信息化建设：推动财务业务流程信息化，开发财务相关的应用系统。\n3. 数据报表开发：设计和开发各类数据报表，满足财务分析和决策需求。\n4. 系统故障处理：及时响应和处理系统运行中的问题，确保系统稳定运行。\n5. 技术支持与培训：为财务部门提供技术支持和系统使用培训。"]),    # C8: 岗位工作职责及内容
            (11, 2, string_indices["本科及以上学历，计算机相关专业"]),  # C11: 学历及专业
            (12, 2, string_indices["25-35岁"]),  # C12: 年龄要求
            (13, 2, string_indices["公司总部"]),  # C13: 工作地点
            (14, 2, string_indices["1. 熟练掌握至少一种编程语言（如Java、Python、C#等）\n2. 熟悉数据库设计和优化，熟练使用SQL\n3. 了解ERP系统原理，有ERP系统开发经验优先\n4. 熟悉财务业务流程者优先"]),  # C14: 知识技能要求
            (15, 2, string_indices["1. 3年以上相关工作经验\n2. 有ERP系统开发或财务信息化项目经验优先\n3. 具备良好的沟通能力和问题解决能力"]),  # C15: 经验能力要求
        ]
        
        update_sheet(sheet_tree, updates)
        
        # 创建新的zip文件
        print("\n生成新文件...")
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as z_out:
            # 复制所有文件（除了我们修改的文件）
            for filename in z.namelist():
                if filename not in ['xl/sharedStrings.xml', 'xl/worksheets/sheet1.xml']:
                    z_out.writestr(filename, z.read(filename))
            
            # 写入修改后的文件
            z_out.writestr('xl/sharedStrings.xml', ET.tostring(shared_tree.getroot(), encoding='UTF-8', xml_declaration=True))
            z_out.writestr('xl/worksheets/sheet1.xml', ET.tostring(sheet_tree.getroot(), encoding='UTF-8', xml_declaration=True))
        
        print(f"\n✓ 岗位说明书已生成: {output_file}")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
