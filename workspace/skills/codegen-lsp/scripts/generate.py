#!/usr/bin/env python3
"""
Codegen-LSP - 多语言类型代码生成器
支持 Python、Dotnet (C#)、SQL Server
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader, Template


class TypeMapper:
    """类型映射器"""
    
    PYTHON_TYPES = {
        'integer': 'int',
        'string': 'str',
        'decimal': 'Decimal',
        'datetime': 'datetime',
        'boolean': 'bool',
        'guid': 'UUID',
        'binary': 'bytes'
    }
    
    DOTNET_TYPES = {
        'integer': 'int',
        'string': 'string',
        'decimal': 'decimal',
        'datetime': 'DateTime',
        'boolean': 'bool',
        'guid': 'Guid',
        'binary': 'byte[]'
    }
    
    SQL_TYPES = {
        'integer': 'INT',
        'string': 'NVARCHAR',
        'decimal': 'DECIMAL',
        'datetime': 'DATETIME2',
        'boolean': 'BIT',
        'guid': 'UNIQUEIDENTIFIER',
        'binary': 'VARBINARY'
    }
    
    @classmethod
    def to_python(cls, type_name: str) -> str:
        return cls.PYTHON_TYPES.get(type_name, 'Any')
    
    @classmethod
    def to_dotnet(cls, type_name: str) -> str:
        return cls.DOTNET_TYPES.get(type_name, 'object')
    
    @classmethod
    def to_sql(cls, type_name: str, max_length: Optional[int] = None, 
               precision: Optional[int] = None, scale: Optional[int] = None) -> str:
        base_type = cls.SQL_TYPES.get(type_name, 'NVARCHAR')
        
        if type_name == 'string':
            if max_length:
                return f'NVARCHAR({max_length})' if max_length != -1 else 'NVARCHAR(MAX)'
            return 'NVARCHAR(255)'
        elif type_name == 'decimal':
            p = precision or 18
            s = scale or 2
            return f'DECIMAL({p},{s})'
        elif type_name == 'binary':
            if max_length:
                return f'VARBINARY({max_length})' if max_length != -1 else 'VARBINARY(MAX)'
            return 'VARBINARY(MAX)'
        
        return base_type


class SpecValidator:
    """规范验证器"""
    
    REQUIRED_FIELDS = ['namespace', 'types']
    
    @classmethod
    def validate(cls, spec: Dict) -> List[str]:
        """验证规范，返回错误列表"""
        errors = []
        
        # 检查必需字段
        for field in cls.REQUIRED_FIELDS:
            if field not in spec:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查类型定义
        if 'types' in spec:
            for i, type_def in enumerate(spec['types']):
                if 'name' not in type_def:
                    errors.append(f"类型 {i} 缺少 name 字段")
                if 'properties' not in type_def:
                    errors.append(f"类型 {type_def.get('name', i)} 缺少 properties 字段")
                
                # 检查属性
                for j, prop in enumerate(type_def.get('properties', [])):
                    if 'name' not in prop:
                        errors.append(f"类型 {type_def.get('name', i)} 的属性 {j} 缺少 name 字段")
                    if 'type' not in prop:
                        errors.append(f"类型 {type_def.get('name', i)} 的属性 {prop.get('name', j)} 缺少 type 字段")
        
        return errors


class CodeGenerator:
    """代码生成器"""
    
    def __init__(self, template_dir: Optional[str] = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / 'templates'
        
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.type_mapper = TypeMapper()
    
    def generate_python(self, spec: Dict) -> Dict[str, str]:
        """生成 Python 代码"""
        files = {}
        
        # 准备模板数据
        for type_def in spec['types']:
            type_def['python_properties'] = self._prepare_python_properties(type_def['properties'])
        
        # 生成类文件
        template = self.env.get_template('python/class.jinja2')
        for type_def in spec['types']:
            content = template.render(
                type_def=type_def,
                namespace=spec['namespace']
            )
            files[f"{type_def['name'].lower()}.py"] = content
        
        # 生成 __init__.py
        init_template = self.env.get_template('python/init.jinja2')
        init_content = init_template.render(types=spec['types'])
        files['__init__.py'] = init_content
        
        return files
    
    def generate_dotnet(self, spec: Dict) -> Dict[str, str]:
        """生成 Dotnet 代码"""
        files = {}
        
        # 准备模板数据
        for type_def in spec['types']:
            type_def['dotnet_properties'] = self._prepare_dotnet_properties(type_def['properties'])
        
        # 生成类文件
        template = self.env.get_template('dotnet/class.jinja2')
        for type_def in spec['types']:
            content = template.render(
                type_def=type_def,
                namespace=spec['namespace']
            )
            files[f"{type_def['name']}.cs"] = content
        
        return files
    
    def generate_sqlserver(self, spec: Dict) -> Dict[str, str]:
        """生成 SQL Server 代码"""
        files = {}
        
        # 准备模板数据
        for type_def in spec['types']:
            type_def['sql_columns'] = self._prepare_sql_columns(type_def)
        
        # 生成表文件
        table_template = self.env.get_template('sqlserver/table.jinja2')
        tables_content = table_template.render(
            types=spec['types'],
            database=spec.get('database', 'MyDatabase')
        )
        files['tables.sql'] = tables_content
        
        # 生成存储过程
        procedure_template = self.env.get_template('sqlserver/procedure.jinja2')
        procedures_content = procedure_template.render(types=spec['types'])
        files['procedures.sql'] = procedures_content
        
        return files
    
    def _prepare_python_properties(self, properties: List[Dict]) -> List[Dict]:
        """准备 Python 属性"""
        result = []
        for prop in properties:
            python_prop = {
                'name': self._to_snake_case(prop['name']),
                'type': self.type_mapper.to_python(prop['type']),
                'description': prop.get('description', ''),
                'required': prop.get('required', True),
                'default': prop.get('default'),
                'enum': prop.get('enum', [])
            }
            result.append(python_prop)
        return result
    
    def _prepare_dotnet_properties(self, properties: List[Dict]) -> List[Dict]:
        """准备 Dotnet 属性"""
        result = []
        for prop in properties:
            dotnet_prop = {
                'name': self._to_pascal_case(prop['name']),
                'type': self.type_mapper.to_dotnet(prop['type']),
                'description': prop.get('description', ''),
                'required': prop.get('required', True),
                'primary_key': prop.get('primary_key', False),
                'foreign_key': prop.get('foreign_key'),
                'max_length': prop.get('max_length'),
                'enum': prop.get('enum', [])
            }
            result.append(dotnet_prop)
        return result
    
    def _prepare_sql_columns(self, type_def: Dict) -> List[Dict]:
        """准备 SQL 列"""
        result = []
        for prop in type_def.get('properties', []):
            sql_col = {
                'name': prop['name'],
                'type': self.type_mapper.to_sql(
                    prop['type'],
                    prop.get('max_length'),
                    prop.get('precision'),
                    prop.get('scale')
                ),
                'primary_key': prop.get('primary_key', False),
                'required': prop.get('required', True),
                'foreign_key': prop.get('foreign_key'),
                'default': prop.get('default'),
                'identity': prop.get('identity', False)
            }
            result.append(sql_col)
        return result
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """转换为 snake_case"""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)
    
    @staticmethod
    def _to_pascal_case(name: str) -> str:
        """转换为 PascalCase"""
        parts = name.split('_')
        return ''.join(word.capitalize() for word in parts)


def load_spec(spec_file: str) -> Dict:
    """加载规范文件"""
    with open(spec_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_files(files: Dict[str, str], output_dir: str, dry_run: bool = False):
    """写入文件"""
    output_path = Path(output_dir)
    
    for filename, content in files.items():
        file_path = output_path / filename
        
        if dry_run:
            print(f"\n=== {file_path} ===")
            print(content)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 生成: {file_path}")


def main():
    parser = argparse.ArgumentParser(description='多语言类型代码生成器')
    parser.add_argument('--input', '-i', required=True, help='输入规范文件路径')
    parser.add_argument('--language', '-l', choices=['python', 'dotnet', 'sqlserver', 'all'], 
                       default='all', help='目标语言')
    parser.add_argument('--output', '-o', required=True, help='输出目录')
    parser.add_argument('--namespace', '-n', help='命名空间（覆盖规范）')
    parser.add_argument('--dry-run', action='store_true', help='只预览，不写入文件')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')
    
    args = parser.parse_args()
    
    # 加载规范
    print(f"📖 加载规范: {args.input}")
    spec = load_spec(args.input)
    
    # 覆盖命名空间
    if args.namespace:
        spec['namespace'] = args.namespace
    
    # 验证规范
    print("🔍 验证规范...")
    errors = SpecValidator.validate(spec)
    if errors:
        print("❌ 规范验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    if args.verbose:
        print(f"  命名空间: {spec['namespace']}")
        print(f"  类型数量: {len(spec['types'])}")
        for type_def in spec['types']:
            print(f"    - {type_def['name']}: {len(type_def['properties'])} 个属性")
    
    # 生成代码
    generator = CodeGenerator()
    
    languages = ['python', 'dotnet', 'sqlserver'] if args.language == 'all' else [args.language]
    
    for lang in languages:
        print(f"\n🔨 生成 {lang.upper()} 代码...")
        
        output_dir = Path(args.output) / lang
        
        if lang == 'python':
            files = generator.generate_python(spec)
        elif lang == 'dotnet':
            files = generator.generate_dotnet(spec)
        elif lang == 'sqlserver':
            files = generator.generate_sqlserver(spec)
        
        write_files(files, str(output_dir), args.dry_run)
    
    print(f"\n✅ 完成！共生成 {len(languages)} 种语言的代码")


if __name__ == '__main__':
    main()
