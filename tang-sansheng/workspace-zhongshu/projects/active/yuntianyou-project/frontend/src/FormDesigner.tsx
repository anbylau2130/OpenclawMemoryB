import React, { useState } from 'react';
import { Layout, Menu, Card, Button, Form, Input, Select, message, Space } from 'antd';
import {
  FormOutlined,
  AppstoreAddOutlined,
  DatabaseOutlined,
  SettingOutlined,
  SaveOutlined,
  EyeOutlined,
} from '@ant-design/icons';

const { Header, Content, Sider } = Layout;
const { Option } = Select;

/**
 * 低代码表单设计器 - 核心组件
 */
const FormDesigner: React.FC = () => {
  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [fields, setFields] = useState<any[]>([]);
  const [selectedField, setSelectedField] = useState<any>(null);

  // 字段类型定义
  const fieldTypes = [
    { label: '单行文本', value: 'text' },
    { label: '多行文本', value: 'textarea' },
    { label: '数字', value: 'number' },
    { label: '日期', value: 'date' },
    { label: '日期时间', value: 'datetime' },
    { label: '下拉选择', value: 'select' },
    { label: '多选框', value: 'checkbox' },
    { label: '单选框', value: 'radio' },
    { label: '文件上传', value: 'file' },
    { label: '图片上传', value: 'image' },
    { label: '邮箱', value: 'email' },
    { label: '电话', value: 'phone' },
  ];

  // 添加字段
  const addField = (type: string) => {
    const newField = {
      id: `field_${Date.now()}`,
      type,
      label: `字段 ${fields.length + 1}`,
      name: `field_${fields.length + 1}`,
      required: false,
      placeholder: '',
      options: type === 'select' || type === 'radio' ? [] : undefined,
    };
    setFields([...fields, newField]);
    setSelectedField(newField);
    message.success('字段添加成功');
  };

  // 更新字段
  const updateField = (fieldId: string, updates: any) => {
    setFields(fields.map(f => f.id === fieldId ? { ...f, ...updates } : f));
  };

  // 删除字段
  const deleteField = (fieldId: string) => {
    setFields(fields.filter(f => f.id !== fieldId));
    if (selectedField?.id === fieldId) {
      setSelectedField(null);
    }
    message.success('字段删除成功');
  };

  // 保存表单
  const saveForm = async () => {
    if (!formName) {
      message.error('请输入表单名称');
      return;
    }

    const formData = {
      name: formName,
      description: formDescription,
      schema: JSON.stringify({
        title: formName,
        description: formDescription,
        type: 'object',
      }),
      fields: JSON.stringify(fields),
    };

    try {
      // 调用后端API保存表单
      const response = await fetch('/api/forms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        message.success('表单保存成功');
      } else {
        message.error('表单保存失败');
      }
    } catch (error) {
      message.error('保存失败，请检查网络连接');
    }
  };

  // 预览表单
  const previewForm = () => {
    message.info('预览功能开发中...');
  };

  return (
    <Layout style={{ height: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ color: '#fff', fontSize: '20px', fontWeight: 'bold' }}>
          云天佑 - 低代码表单设计器
        </div>
      </Header>
      
      <Layout>
        <Sider width={240} style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
          <div style={{ padding: '16px' }}>
            <h3>字段类型</h3>
            <Space direction="vertical" style={{ width: '100%' }}>
              {fieldTypes.map(type => (
                <Button
                  key={type.value}
                  block
                  onClick={() => addField(type.value)}
                  icon={<AppstoreAddOutlined />}
                >
                  {type.label}
                </Button>
              ))}
            </Space>
          </div>
        </Sider>

        <Content style={{ padding: '24px', background: '#f0f2f5' }}>
          <Card title="表单基本信息" style={{ marginBottom: '16px' }}>
            <Form layout="vertical">
              <Form.Item label="表单名称" required>
                <Input
                  value={formName}
                  onChange={e => setFormName(e.target.value)}
                  placeholder="请输入表单名称"
                />
              </Form.Item>
              <Form.Item label="表单描述">
                <Input.TextArea
                  value={formDescription}
                  onChange={e => setFormDescription(e.target.value)}
                  placeholder="请输入表单描述"
                  rows={3}
                />
              </Form.Item>
            </Form>
          </Card>

          <Card 
            title={`字段列表 (${fields.length})`}
            extra={
              <Space>
                <Button icon={<EyeOutlined />} onClick={previewForm}>
                  预览
                </Button>
                <Button type="primary" icon={<SaveOutlined />} onClick={saveForm}>
                  保存
                </Button>
              </Space>
            }
          >
            {fields.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                <FormOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <p>请从左侧选择字段类型添加到表单中</p>
              </div>
            ) : (
              <div>
                {fields.map((field, index) => (
                  <Card
                    key={field.id}
                    size="small"
                    style={{ marginBottom: '8px', cursor: 'pointer' }}
                    hoverable
                    onClick={() => setSelectedField(field)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <strong>{index + 1}. {field.label}</strong>
                        <span style={{ marginLeft: '8px', color: '#999' }}>
                          ({fieldTypes.find(t => t.value === field.type)?.label})
                        </span>
                      </div>
                      <Button danger size="small" onClick={(e) => {
                        e.stopPropagation();
                        deleteField(field.id);
                      }}>
                        删除
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </Card>

          {selectedField && (
            <Card title="字段属性" style={{ marginTop: '16px' }}>
              <Form layout="vertical">
                <Form.Item label="字段标签">
                  <Input
                    value={selectedField.label}
                    onChange={e => updateField(selectedField.id, { label: e.target.value })}
                  />
                </Form.Item>
                <Form.Item label="字段名称">
                  <Input
                    value={selectedField.name}
                    onChange={e => updateField(selectedField.id, { name: e.target.value })}
                  />
                </Form.Item>
                <Form.Item label="占位符">
                  <Input
                    value={selectedField.placeholder}
                    onChange={e => updateField(selectedField.id, { placeholder: e.target.value })}
                  />
                </Form.Item>
                <Form.Item label="是否必填">
                  <Select
                    value={selectedField.required ? 'yes' : 'no'}
                    onChange={value => updateField(selectedField.id, { required: value === 'yes' })}
                  >
                    <Option value="yes">是</Option>
                    <Option value="no">否</Option>
                  </Select>
                </Form.Item>
              </Form>
            </Card>
          )}
        </Layout>
      </Layout>
    </Layout>
  );
};

export default FormDesigner;
