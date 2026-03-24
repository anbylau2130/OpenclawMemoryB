import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Space, Tag, message, Switch, Tabs } from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  CodeOutlined,
  BugOutlined,
} from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;
const { TextArea } = Input;

/**
 * 插件管理页面 - 低代码平台插件系统
 */
const PluginManagementPage: React.FC = () => {
  const [plugins, setPlugins] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPlugin, setEditingPlugin] = useState<any>(null);
  const [testModalVisible, setTestModalVisible] = useState(false);
  const [testingPlugin, setTestingPlugin] = useState<any>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/plugins');
      if (response.data.success) {
        setPlugins(response.data.data);
      }
    } catch (error) {
      message.error('加载插件列表失败');
    } finally {
      setLoading(false);
    }
  };

  const createPlugin = async (values: any) => {
    try {
      const response = await axios.post('/api/plugins', values);
      if (response.data.success) {
        message.success('插件创建成功');
        setModalVisible(false);
        form.resetFields();
        loadPlugins();
      }
    } catch (error) {
      message.error('创建插件失败');
    }
  };

  const updatePlugin = async (id: string, values: any) => {
    try {
      const response = await axios.put(`/api/plugins/${id}`, values);
      if (response.data.success) {
        message.success('插件更新成功');
        setModalVisible(false);
        setEditingPlugin(null);
        form.resetFields();
        loadPlugins();
      }
    } catch (error) {
      message.error('更新插件失败');
    }
  };

  const deletePlugin = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个插件吗？',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await axios.delete(`/api/plugins/${id}`);
          if (response.data.success) {
            message.success('插件删除成功');
            loadPlugins();
          }
        } catch (error) {
          message.error('删除插件失败');
        }
      },
    });
  };

  const togglePlugin = async (id: string, enable: boolean) => {
    try {
      const url = enable ? `/api/plugins/${id}/enable` : `/api/plugins/${id}/disable`;
      const response = await axios.post(url);
      if (response.data.success) {
        message.success(enable ? '插件已启用' : '插件已禁用');
        loadPlugins();
      }
    } catch (error) {
      message.error('操作失败');
    }
  };

  const testPlugin = async (id: string, testData: any) => {
    try {
      const response = await axios.post(`/api/plugins/${id}/execute`, testData);
      message.success('插件执行成功');
      console.log('执行结果:', response.data);
    } catch (error) {
      message.error('插件执行失败');
    }
  };

  const columns = [
    {
      title: '插件名称',
      dataIndex: 'displayName',
      key: 'displayName',
    },
    {
      title: '标识',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <code>{text}</code>,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (text: string) => {
        const colors: any = {
          form: 'blue',
          list: 'green',
          operation: 'orange',
          workflow: 'purple',
        };
        return <Tag color={colors[text] || 'default'}>{text}</Tag>;
      },
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: '状态',
      dataIndex: 'isEnabled',
      key: 'isEnabled',
      render: (enabled: boolean, record: any) => (
        <Switch
          checked={enabled}
          onChange={(checked) => togglePlugin(record.id, checked)}
          disabled={record.isSystem}
        />
      ),
    },
    {
      title: '系统插件',
      dataIndex: 'isSystem',
      key: 'isSystem',
      render: (isSystem: boolean) => isSystem ? <Tag color="red">系统</Tag> : <Tag>自定义</Tag>,
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingPlugin(record);
              form.setFieldsValue(record);
              setModalVisible(true);
            }}
          >
            编辑
          </Button>
          <Button
            type="link"
            icon={<PlayCircleOutlined />}
            onClick={() => {
              setTestingPlugin(record);
              setTestModalVisible(true);
            }}
          >
            测试
          </Button>
          {!record.isSystem && (
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              onClick={() => deletePlugin(record.id)}
            >
              删除
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card title={
        <Space>
          <BugOutlined />
          <span>插件管理</span>
        </Space>
      }>
        <div style={{ marginBottom: '16px' }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingPlugin(null);
              form.resetFields();
              setModalVisible(true);
            }}
          >
            新建插件
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={plugins}
          rowKey="id"
          loading={loading}
        />
      </Card>

      {/* 创建/编辑插件模态框 */}
      <Modal
        title={editingPlugin ? '编辑插件' : '创建插件'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingPlugin(null);
          form.resetFields();
        }}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => {
            if (editingPlugin) {
              updatePlugin(editingPlugin.id, values);
            } else {
              createPlugin(values);
            }
          }}
        >
          <Form.Item
            name="name"
            label="插件标识"
            rules={[{ required: true }]}
          >
            <Input placeholder="如: MyCustomPlugin" disabled={!!editingPlugin} />
          </Form.Item>

          <Form.Item
            name="displayName"
            label="显示名称"
            rules={[{ required: true }]}
          >
            <Input placeholder="如: 我的自定义插件" />
          </Form.Item>

          <Form.Item name="type" label="插件类型" rules={[{ required: true }]}>
            <Select>
              <Option value="form">表单插件</Option>
              <Option value="list">列表插件</Option>
              <Option value="operation">操作插件</Option>
              <Option value="workflow">工作流插件</Option>
            </Select>
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item name="script" label="插件脚本" rules={[{ required: true }]}>
            <TextArea
              rows={10}
              placeholder="// JavaScript 代码&#10;function execute(context) {&#10;  // 插件逻辑&#10;  return result;&#10;}"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingPlugin ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 测试插件模态框 */}
      <Modal
        title="测试插件"
        open={testModalVisible}
        onCancel={() => setTestModalVisible(false)}
        onOk={() => {
          // 执行测试
          setTestModalVisible(false);
        }}
      >
        <p>测试功能开发中...</p>
      </Modal>
    </div>
  );
};

export default PluginManagementPage;
