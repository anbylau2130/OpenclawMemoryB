import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, message, Tag, Space, Steps, List, Comment } from 'antd';
import { PlayCircleOutlined, CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TextArea } = Input;
const { Option } = Select;

interface Workflow {
  id: string;
  name: string;
  description?: string;
  isActive: boolean;
  version: number;
}

interface WorkflowInstance {
  id: string;
  workflowId: string;
  status: string;
  currentNode: string;
  data: string;
  startedAt?: string;
  completedAt?: string;
}

const WorkflowPage: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [instances, setInstances] = useState<WorkflowInstance[]>([]);
  const [pendingTasks, setPendingTasks] = useState<WorkflowInstance[]>([]);
  const [loading, setLoading] = useState(false);
  const [startModalVisible, setStartModalVisible] = useState(false);
  const [approveModalVisible, setApproveModalVisible] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [selectedInstance, setSelectedInstance] = useState<WorkflowInstance | null>(null);
  const [form] = Form.useForm();
  const [approveForm] = Form.useForm();

  useEffect(() => {
    fetchWorkflows();
    fetchPendingTasks();
  }, []);

  const fetchWorkflows = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/workflows');
      setWorkflows(response.data);
    } catch (error) {
      // 模拟数据
      setWorkflows([
        { id: '1', name: '请假审批流程', description: '员工请假审批', isActive: true, version: 1 },
        { id: '2', name: '报销审批流程', description: '费用报销审批', isActive: true, version: 1 },
        { id: '3', name: '合同审批流程', description: '合同签订审批', isActive: true, version: 1 },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingTasks = async () => {
    try {
      const userId = JSON.parse(localStorage.getItem('user') || '{}')?.userId || '1';
      const response = await axios.get(`/api/workflows/pending/${userId}`);
      setPendingTasks(response.data);
    } catch (error) {
      // 模拟待办数据
      setPendingTasks([
        { 
          id: '101', 
          workflowId: '1', 
          status: 'pending_approval', 
          currentNode: 'manager_approve',
          data: JSON.stringify({ type: '事假', days: 2, reason: '家中有事' }),
          startedAt: new Date().toISOString()
        },
      ]);
    }
  };

  const handleStartWorkflow = async (values: any) => {
    try {
      const userId = JSON.parse(localStorage.getItem('user') || '{}')?.userId || '1';
      await axios.post(`/api/workflows/${selectedWorkflow?.id}/start`, {
        data: JSON.stringify(values),
        initiatedByUserId: userId
      });
      message.success('流程已启动');
      setStartModalVisible(false);
      form.resetFields();
      fetchPendingTasks();
    } catch (error) {
      message.success('流程已启动（模拟）');
      setStartModalVisible(false);
      form.resetFields();
    }
  };

  const handleApprove = async (values: any) => {
    try {
      const userId = JSON.parse(localStorage.getItem('user') || '{}')?.userId || '1';
      await axios.post(`/api/workflows/instances/${selectedInstance?.id}/approve`, {
        approvedByUserId: userId,
        action: values.action,
        comment: values.comment
      });
      message.success('审批成功');
      setApproveModalVisible(false);
      approveForm.resetFields();
      fetchPendingTasks();
    } catch (error) {
      message.success('审批成功（模拟）');
      setApproveModalVisible(false);
      approveForm.resetFields();
      fetchPendingTasks();
    }
  };

  const getStatusTag = (status: string) => {
    const statusMap: any = {
      pending: <Tag icon={<ClockCircleOutlined />} color="default">待处理</Tag>,
      running: <Tag icon={<PlayCircleOutlined />} color="processing">进行中</Tag>,
      pending_approval: <Tag icon={<ClockCircleOutlined />} color="warning">待审批</Tag>,
      approved: <Tag icon={<CheckCircleOutlined />} color="success">已通过</Tag>,
      rejected: <Tag icon={<CloseCircleOutlined />} color="error">已拒绝</Tag>,
      completed: <Tag icon={<CheckCircleOutlined />} color="success">已完成</Tag>,
    };
    return statusMap[status] || <Tag>{status}</Tag>;
  };

  const workflowColumns = [
    { title: '流程名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    { title: '版本', dataIndex: 'version', key: 'version' },
    { 
      title: '状态', 
      dataIndex: 'isActive', 
      key: 'isActive',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'red'}>{active ? '启用' : '禁用'}</Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Workflow) => (
        <Button 
          type="primary" 
          size="small"
          onClick={() => {
            setSelectedWorkflow(record);
            setStartModalVisible(true);
          }}
        >
          发起流程
        </Button>
      )
    }
  ];

  const pendingColumns = [
    { title: '流程实例ID', dataIndex: 'id', key: 'id', width: 100 },
    { 
      title: '流程数据', 
      dataIndex: 'data', 
      key: 'data',
      render: (data: string) => {
        try {
          const parsed = JSON.parse(data);
          return <span>{parsed.type || '数据'} - {parsed.reason || ''}</span>;
        } catch {
          return data;
        }
      }
    },
    { title: '当前节点', dataIndex: 'currentNode', key: 'currentNode' },
    { 
      title: '状态', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => getStatusTag(status)
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: WorkflowInstance) => (
        <Space>
          <Button 
            type="primary" 
            size="small"
            onClick={() => {
              setSelectedInstance(record);
              approveForm.setFieldsValue({ action: 'approved' });
              setApproveModalVisible(true);
            }}
          >
            审批
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1>🔄 工作流管理</h1>
      
      {/* 待办任务 */}
      <Card title="📋 我的待办" style={{ marginBottom: 24 }}>
        <Table 
          columns={pendingColumns} 
          dataSource={pendingTasks} 
          rowKey="id"
          loading={loading}
          pagination={false}
        />
      </Card>
      
      {/* 流程定义 */}
      <Card title="📚 流程定义">
        <Table 
          columns={workflowColumns} 
          dataSource={workflows} 
          rowKey="id"
          loading={loading}
        />
      </Card>
      
      {/* 发起流程模态框 */}
      <Modal
        title={`发起流程：${selectedWorkflow?.name}`}
        open={startModalVisible}
        onCancel={() => setStartModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleStartWorkflow} layout="vertical">
          <Form.Item name="type" label="类型" rules={[{ required: true }]}>
            <Select placeholder="请选择">
              <Option value="事假">事假</Option>
              <Option value="病假">病假</Option>
              <Option value="年假">年假</Option>
            </Select>
          </Form.Item>
          <Form.Item name="days" label="天数" rules={[{ required: true }]}>
            <Input type="number" placeholder="请输入天数" />
          </Form.Item>
          <Form.Item name="reason" label="原因" rules={[{ required: true }]}>
            <TextArea rows={3} placeholder="请输入原因" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              提交
            </Button>
          </Form.Item>
        </Form>
      </Modal>
      
      {/* 审批模态框 */}
      <Modal
        title="审批流程"
        open={approveModalVisible}
        onCancel={() => setApproveModalVisible(false)}
        footer={null}
      >
        <Form form={approveForm} onFinish={handleApprove} layout="vertical">
          <Form.Item name="action" label="审批结果" rules={[{ required: true }]}>
            <Select>
              <Option value="approved">通过</Option>
              <Option value="rejected">拒绝</Option>
            </Select>
          </Form.Item>
          <Form.Item name="comment" label="审批意见">
            <TextArea rows={3} placeholder="请输入审批意见" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              提交审批
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WorkflowPage;
