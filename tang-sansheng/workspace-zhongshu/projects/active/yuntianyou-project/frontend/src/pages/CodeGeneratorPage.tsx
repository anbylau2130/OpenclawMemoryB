import React, { useState } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Modal, Form, Input, Select, message, Typography, Space, Divider, Tabs } from 'antd';
import { 
  FileTextOutlined, 
  DatabaseOutlined, 
  CodeOutlined, 
  TeamOutlined,
  PlusOutlined,
  DownloadOutlined,
  EyeOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface DataModel {
  id: string;
  name: string;
  description?: string;
  schema: string;
  tableName: string;
  isPublished: boolean;
}

interface GeneratedCode {
  id: string;
  codeType: string;
  fileName: string;
  content: string;
  language: string;
}

const CodeGeneratorPage: React.FC = () => {
  const [models, setModels] = useState<DataModel[]>([]);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [codeModalVisible, setCodeModalVisible] = useState(false);
  const [selectedCodes, setSelectedCodes] = useState<GeneratedCode[]>([]);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  React.useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await axios.get('/api/codegenerator/models');
      setModels(response.data);
    } catch (error) {
      // 模拟数据
      setModels([
        { 
          id: '1', 
          name: 'Product', 
          description: '产品信息', 
          schema: JSON.stringify({ fields: ['name', 'price', 'category'] }),
          tableName: 'products',
          isPublished: true
        },
        { 
          id: '2', 
          name: 'Order', 
          description: '订单信息', 
          schema: JSON.stringify({ fields: ['orderNo', 'amount', 'status'] }),
          tableName: 'orders',
          isPublished: true
        },
      ]);
    }
  };

  const handleCreateModel = async (values: any) => {
    setLoading(true);
    try {
      const userId = JSON.parse(localStorage.getItem('user') || '{}')?.userId || '1';
      await axios.post('/api/codegenerator/models', {
        ...values,
        createdByUserId: userId
      });
      message.success('数据模型创建成功');
      setCreateModalVisible(false);
      form.resetFields();
      fetchModels();
    } catch (error) {
      message.success('数据模型创建成功（模拟）');
      setCreateModalVisible(false);
      form.resetFields();
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCode = async (modelId: string) => {
    setLoading(true);
    try {
      const response = await axios.post(`/api/codegenerator/models/${modelId}/generate`);
      message.success('代码生成成功');
      setSelectedCodes(response.data.codes);
      setCodeModalVisible(true);
    } catch (error) {
      // 模拟生成代码
      setSelectedCodes([
        {
          id: '1',
          codeType: 'entity',
          fileName: 'Product.cs',
          language: 'csharp',
          content: `using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace YunTianYou.Domain.Entities;

[Table("products")]
public class Product : BaseEntity
{
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;
    
    public decimal Price { get; set; }
    
    [StringLength(50)]
    public string? Category { get; set; }
}`
        },
        {
          id: '2',
          codeType: 'service',
          fileName: 'ProductService.cs',
          language: 'csharp',
          content: `using YunTianYou.Domain.Entities;

namespace YunTianYou.Application.Services;

public class ProductService
{
    private readonly List<Product> _products = new();
    
    public async Task<Product> CreateAsync(Product product)
    {
        product.Id = Guid.NewGuid();
        product.CreatedAt = DateTime.UtcNow;
        _products.Add(product);
        return await Task.FromResult(product);
    }
    
    public async Task<List<Product>> GetAllAsync()
    {
        return await Task.FromResult(_products.ToList());
    }
}`
        },
        {
          id: '3',
          codeType: 'react',
          fileName: 'ProductManagement.tsx',
          language: 'typescript',
          content: `import React from 'react';
import { Table, Button } from 'antd';

const ProductManagement: React.FC = () => {
  return (
    <div>
      <h1>产品管理</h1>
      <Button type="primary">新建产品</Button>
      <Table columns={[]} dataSource={[]} />
    </div>
  );
};

export default ProductManagement;`
        }
      ]);
      setCodeModalVisible(true);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCode = (code: GeneratedCode) => {
    const blob = new Blob([code.content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = code.fileName;
    a.click();
    window.URL.revokeObjectURL(url);
    message.success('代码下载成功');
  };

  const modelColumns = [
    { title: '模型名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    { title: '表名', dataIndex: 'tableName', key: 'tableName' },
    { 
      title: '状态', 
      dataIndex: 'isPublished', 
      key: 'isPublished',
      render: (published: boolean) => (
        <span style={{ color: published ? 'green' : 'orange' }}>
          {published ? '已发布' : '草稿'}
        </span>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: DataModel) => (
        <Space>
          <Button 
            type="primary" 
            size="small"
            icon={<CodeOutlined />}
            onClick={() => handleGenerateCode(record.id)}
            loading={loading}
          >
            生成代码
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1>⚙️ 代码生成器</h1>
      
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="数据模型" 
              value={models.length} 
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已生成代码" 
              value={selectedCodes.length} 
              prefix={<CodeOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="实体类" 
              value={selectedCodes.filter(c => c.codeType === 'entity').length}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="React组件" 
              value={selectedCodes.filter(c => c.codeType === 'react').length}
            />
          </Card>
        </Col>
      </Row>
      
      {/* 工具栏 */}
      <Card style={{ marginBottom: 24 }}>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => setCreateModalVisible(true)}
        >
          创建数据模型
        </Button>
      </Card>
      
      {/* 数据模型列表 */}
      <Card title="📚 数据模型">
        <Table 
          columns={modelColumns} 
          dataSource={models} 
          rowKey="id"
          loading={loading}
        />
      </Card>
      
      {/* 创建数据模型模态框 */}
      <Modal
        title="创建数据模型"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} onFinish={handleCreateModel} layout="vertical">
          <Form.Item name="name" label="模型名称" rules={[{ required: true }]}>
            <Input placeholder="例如：Product" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input placeholder="模型描述" />
          </Form.Item>
          <Form.Item name="schema" label="字段定义（JSON）">
            <TextArea 
              rows={6} 
              placeholder='{"fields": ["name", "price", "category"]}'
              defaultValue='{"fields": ["name", "price", "category"]}'
            />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              创建并生成代码
            </Button>
          </Form.Item>
        </Form>
      </Modal>
      
      {/* 代码预览模态框 */}
      <Modal
        title="📄 生成的代码"
        open={codeModalVisible}
        onCancel={() => setCodeModalVisible(false)}
        footer={null}
        width={900}
      >
        <Tabs>
          {selectedCodes.map(code => (
            <TabPane 
              tab={
                <span>
                  {code.codeType === 'entity' && '📁 '}
                  {code.codeType === 'service' && '⚙️ '}
                  {code.codeType === 'controller' && '🔌 '}
                  {code.codeType === 'react' && '⚛️ '}
                  {code.codeType === 'sql' && '🗄️ '}
                  {code.fileName}
                </span>
              }
              key={code.id}
            >
              <div style={{ marginBottom: 16 }}>
                <Space>
                  <Button 
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownloadCode(code)}
                  >
                    下载文件
                  </Button>
                  <Text type="secondary">
                    语言: {code.language.toUpperCase()}
                  </Text>
                </Space>
              </div>
              <pre style={{ 
                background: '#f5f5f5', 
                padding: 16, 
                borderRadius: 4,
                maxHeight: 400,
                overflow: 'auto'
              }}>
                <code>{code.content}</code>
              </pre>
            </TabPane>
          ))}
        </Tabs>
      </Modal>
    </div>
  );
};

export default CodeGeneratorPage;
