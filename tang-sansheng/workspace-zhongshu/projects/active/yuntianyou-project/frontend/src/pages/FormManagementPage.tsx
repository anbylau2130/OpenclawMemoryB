import React, { useState, useEffect } from 'react';
import { Layout, Menu, Table, Button, Modal, Form, Input, message, Space, Tag, Card } from 'antd';
import {
  DashboardOutlined,
  FormOutlined,
  DatabaseOutlined,
  SettingOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import axios from 'axios';

const { Header, Content, Sider } = Layout;

/**
 * 表单管理页面 - 低代码平台核心
 */
const FormManagementPage: React.FC = () => {
  const [forms, setForms] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingForm, setEditingForm] = useState<any>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadForms();
  }, []);

  // 加载表单列表
  const loadForms = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/forms');
      if (response.data.success) {
        setForms(response.data.data);
      }
    } catch (error) {
      message.error('加载表单列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 创建新表单
  const createForm = async (values: any) => {
    try {
      const response = await axios.post('/api/forms', values);
      if (response.data.success) {
        message.success('表单创建成功');
        setModalVisible(false);
        form.resetFields();
        loadForms();
      }
    } catch (error) {
      message.error('创建表单失败');
    }
  };

  // 更新表单
  const updateForm = async (id: string, values: any) => {
    try {
      const response = await axios.put(`/api/forms/${id}`, values);
      if (response.data.success) {
        message.success('表单更新成功');
        setModalVisible(false);
        setEditingForm(null);
        form.resetFields();
        loadForms();
      }
    } catch (error) {
      message.error('更新表单失败');
    }
  };

  // 删除表单
  const deleteForm = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个表单吗？此操作不可恢复。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await axios.delete(`/api/forms/${id}`);
          if (response.data.success) {
            message.success('表单删除成功');
            loadForms();
          }
        } catch (error) {
          message.error('删除表单失败');
        }
      },
    });
  };

  // 发布表单
  const publishForm = async (id: string) => {
    try {
      const response = await axios.post(`/api/forms/${id}/publish`);
      if (response.data.success) {
        message.success('表单发布成功');
        loadForms();
      }
    } catch (error) {
      message.error('发布表单失败');
    }
  };

  // 打开编辑模态框
  const openEditModal = (record: any) => {
    setEditingForm(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  // 表格列定义
  const columns = [
    {
      title: '表单名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <strong>{text}</strong>,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      render: (version: number) => <Tag color="blue">v{version}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'isPublished',
      key: 'isPublished',
      render: (isPublished: boolean) => (
        <Tag color={isPublished ? 'green' : 'orange'}>
          {isPublished ? '已发布' : '草稿'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '创建人',
      dataIndex: 'createdByUserName',
      key: 'createdByUserName',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => message.info('预览功能开发中')}
          >
            预览
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => openEditModal(record)}
          >
            编辑
          </Button>
          {!record.isPublished && (
            <Button
              type="link"
              onClick={() => publishForm(record.id)}
            >
              发布
            </Button>
          )}
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => deleteForm(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ color: '#fff', fontSize: '20px', fontWeight: 'bold' }}>
          云天佑 - 表单管理中心
        </div>
      </Header>
      
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            defaultSelectedKeys={['forms']}
            style={{ height: '100%', borderRight: 0 }}
          >
            <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
              仪表盘
            </Menu.Item>
            <Menu.Item key="forms" icon={<FormOutlined />}>
              表单管理
            </Menu.Item>
            <Menu.Item key="data" icon={<DatabaseOutlined />}>
              数据管理
            </Menu.Item>
            <Menu.Item key="settings" icon={<SettingOutlined />}>
              系统设置
            </Menu.Item>
          </Menu>
        </Sider>

        <Content style={{ padding: '24px', background: '#f0f2f5' }}>
          <Card>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
              <h2>表单列表</h2>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => {
                  setEditingForm(null);
                  form.resetFields();
                  setModalVisible(true);
                }}
              >
                新建表单
              </Button>
            </div>

            <Table
              columns={columns}
              dataSource={forms}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showTotal: (total) => `共 ${total} 个表单`,
              }}
            />
          </Card>
        </Content>
      </Layout>

      {/* 创建/编辑表单模态框 */}
      <Modal
        title={editingForm ? '编辑表单' : '创建表单'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingForm(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => {
            if (editingForm) {
              updateForm(editingForm.id, values);
            } else {
              createForm(values);
            }
          }}
        >
          <Form.Item
            name="name"
            label="表单名称"
            rules={[{ required: true, message: '请输入表单名称' }]}
          >
            <Input placeholder="请输入表单名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="表单描述"
          >
            <Input.TextArea rows={4} placeholder="请输入表单描述" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingForm ? '更新' : '创建'}
              </Button>
              <Button onClick={() => {
                setModalVisible(false);
                setEditingForm(null);
                form.resetFields();
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
};

export default FormManagementPage;
