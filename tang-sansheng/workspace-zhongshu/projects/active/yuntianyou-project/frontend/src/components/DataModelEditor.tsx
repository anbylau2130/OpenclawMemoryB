import React, { useState } from 'react';
import { Card, Button, Form, Input, Select, Space, Table, Modal, message, Tabs } from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  SaveOutlined,
  CodeOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = Input;

/**
 * 数据模型编辑器 - 低代码平台核心组件
 */
const DataModelEditor: React.FC = () => {
  const [modelName, setModelName] = useState('');
  const [modelDescription, setModelDescription] = useState('');
  const [fields, setFields] = useState<any[]>([]);
  const [generatedCode, setGeneratedCode] = useState('');
  const [codeModalVisible, setCodeModalVisible] = useState(false);

  // 数据类型定义（对应金蝶云苍穹的字段类型）
  const dataTypes = [
    { label: '文本', value: 'string' },
    { label: '整数', value: 'int' },
    { label: '小数', value: 'decimal' },
    { label: '布尔', value: 'bool' },
    { label: '日期', value: 'DateTime' },
    { label: '时间', value: 'TimeSpan' },
    { label: '日期时间', value: 'DateTime' },
    { label: 'GUID', value: 'Guid' },
    { label: '长文本', value: 'text' },
    { label: 'JSON', value: 'json' },
    { label: '二进制', value: 'byte[]' },
  ];

  // 添加字段
  const addField = () => {
    const newField = {
      id: `field_${Date.now()}`,
      name: `Field${fields.length + 1}`,
      displayName: `字段${fields.length + 1}`,
      type: 'string',
      length: 255,
      nullable: true,
      primaryKey: false,
      autoIncrement: false,
      defaultValue: '',
      comment: '',
    };
    setFields([...fields, newField]);
    message.success('字段添加成功');
  };

  // 更新字段
  const updateField = (id: string, key: string, value: any) => {
    setFields(fields.map(f => f.id === id ? { ...f, [key]: value } : f));
  };

  // 删除字段
  const deleteField = (id: string) => {
    setFields(fields.filter(f => f.id !== id));
    message.success('字段删除成功');
  };

  // 生成代码
  const generateCode = () => {
    if (!modelName) {
      message.error('请输入模型名称');
      return;
    }

    // 生成C#实体类代码
    const csharpCode = generateCSharpEntity();
    setGeneratedCode(csharpCode);
    setCodeModalVisible(true);
  };

  // 生成C#实体类
  const generateCSharpEntity = () => {
    const className = modelName.replace(/\s+/g, '');
    
    let code = `using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace YunTianYou.Domain.Entities;

/// <summary>
/// ${modelDescription || modelName}
/// </summary>
[Table("${className.toLowerCase()}s")]
public class ${className} : BaseEntity
{
`;

    fields.forEach(field => {
      code += `    /// <summary>\n`;
      code += `    /// ${field.displayName}\n`;
      code += `    /// </summary>\n`;
      
      if (field.primaryKey) {
        code += `    [Key]\n`;
        code += `    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]\n`;
      } else {
        if (field.type === 'string' || field.type === 'text') {
          code += `    [StringLength(${field.length})]\n`;
        }
        if (field.required) {
          code += `    [Required]\n`;
        }
      }
      
      code += `    public ${field.nullable && !field.primaryKey ? 'virtual ' : ''}${getFieldType(field)} ${field.name} { get; set; }\n\n`;
    });

    code += `}

// 自动生成时间: ${new Date().toLocaleString('zh-CN')}
// 生成工具: 云天佑低代码平台
`;

    return code;
  };

  // 获取字段类型
  const getFieldType = (field: any) => {
    if (field.nullable && !field.primaryKey) {
      switch (field.type) {
        case 'string':
        case 'text':
          return 'string';
        case 'int':
          return 'int?';
        case 'decimal':
          return 'decimal?';
        case 'bool':
          return 'bool?';
        case 'DateTime':
          return 'DateTime?';
        case 'Guid':
          return 'Guid?';
        default:
          return field.type + '?';
      }
    }
    return field.type;
  };

  // 保存数据模型
  const saveModel = async () => {
    if (!modelName) {
      message.error('请输入模型名称');
      return;
    }

    const modelData = {
      name: modelName,
      description: modelDescription,
      fields: fields,
    };

    try {
      // 调用API保存模型
      message.success('数据模型保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '字段名',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <Input
          value={text}
          onChange={(e) => updateField(record.id, 'name', e.target.value)}
        />
      ),
    },
    {
      title: '显示名',
      dataIndex: 'displayName',
      key: 'displayName',
      render: (text: string, record: any) => (
        <Input
          value={text}
          onChange={(e) => updateField(record.id, 'displayName', e.target.value)}
        />
      ),
    },
    {
      title: '数据类型',
      dataIndex: 'type',
      key: 'type',
      render: (text: string, record: any) => (
        <Select
          value={text}
          onChange={(value) => updateField(record.id, 'type', value)}
          style={{ width: 120 }}
        >
          {dataTypes.map(type => (
            <Option key={type.value} value={type.value}>{type.label}</Option>
          ))}
        </Select>
      ),
    },
    {
      title: '长度',
      dataIndex: 'length',
      key: 'length',
      render: (text: number, record: any) => (
        <Input
          type="number"
          value={text}
          onChange={(e) => updateField(record.id, 'length', parseInt(e.target.value))}
          style={{ width: 80 }}
        />
      ),
    },
    {
      title: '可空',
      dataIndex: 'nullable',
      key: 'nullable',
      render: (checked: boolean, record: any) => (
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => updateField(record.id, 'nullable', e.target.checked)}
        />
      ),
    },
    {
      title: '主键',
      dataIndex: 'primaryKey',
      key: 'primaryKey',
      render: (checked: boolean, record: any) => (
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => updateField(record.id, 'primaryKey', e.target.checked)}
        />
      ),
    },
    {
      title: '说明',
      dataIndex: 'comment',
      key: 'comment',
      render: (text: string, record: any) => (
        <Input
          value={text}
          onChange={(e) => updateField(record.id, 'comment', e.target.value)}
        />
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Button
          type="link"
          danger
          icon={<DeleteOutlined />}
          onClick={() => deleteField(record.id)}
        >
          删除
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card title={
        <Space>
          <DatabaseOutlined />
          <span>数据模型编辑器</span>
        </Space>
      }>
        <Form layout="vertical">
          <Form.Item label="模型名称">
            <Input
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              placeholder="请输入模型名称（如：User, Product）"
            />
          </Form.Item>

          <Form.Item label="模型描述">
            <TextArea
              value={modelDescription}
              onChange={(e) => setModelDescription(e.target.value)}
              rows={3}
              placeholder="请输入模型描述"
            />
          </Form.Item>
        </Form>

        <div style={{ marginBottom: '16px' }}>
          <Space>
            <Button type="primary" icon={<PlusOutlined />} onClick={addField}>
              添加字段
            </Button>
            <Button icon={<SaveOutlined />} onClick={saveModel}>
              保存模型
            </Button>
            <Button icon={<CodeOutlined />} onClick={generateCode}>
              生成代码
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={fields}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>

      {/* 代码预览模态框 */}
      <Modal
        title="生成的C#代码"
        open={codeModalVisible}
        onCancel={() => setCodeModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setCodeModalVisible(false)}>
            关闭
          </Button>,
          <Button key="copy" type="primary" onClick={() => {
            navigator.clipboard.writeText(generatedCode);
            message.success('代码已复制到剪贴板');
          }}>
            复制代码
          </Button>,
        ]}
      >
        <pre style={{ 
          background: '#f5f5f5', 
          padding: '16px', 
          borderRadius: '4px',
          maxHeight: '500px',
          overflow: 'auto'
        }}>
          {generatedCode}
        </pre>
      </Modal>
    </div>
  );
};

export default DataModelEditor;
