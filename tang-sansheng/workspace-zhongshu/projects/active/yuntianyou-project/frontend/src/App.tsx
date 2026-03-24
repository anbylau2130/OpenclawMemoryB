import React, { useState, from 'react';
import { Layout, Menu, Typography, Avatar, Dropdown, Card, Row, Col, Statistic } from 'antd';
import {
  FormOutlined,
  DatabaseOutlined,
  SettingOutlined,
  CodeOutlined,
  UserOutlined,
  WorkflowOutlined,
} from '@ant-design/icons';
import FormManagementPage from './FormManagementPage';
import DataModelEditor from '../components/DataModelEditor';
import WorkflowPage from './pages/WorkflowPage';
import CodeGeneratorPage from './pages/CodeGeneratorPage';
import AuthPage from './pages/AuthPage';

const { Title, Sider } = Typography;

// 简单的用户状态（实际应从Redux或Context获取)
const mockUser = {
  userId: '1',
  username: 'admin',
  email: 'admin@example.com',
  role: 'admin'
};

const App: React.FC = () => {
  const [currentMenu, setCurrentMenu] = useState('forms');
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleLoginSuccess = (userData: any, token: string) => {
    setUser(userData);
    localStorage.setItem('token', token);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  // 如果未登录，显示登录页
  if (!user) {
    return <AuthPage onLoginSuccess={handleLoginSuccess} />;
  }

  const menuItems = [
    { key: 'forms', icon: <FormOutlined />, label: '表单管理' },
    { key: 'models', icon: <DatabaseOutlined />, label: '数据模型' },
    { key: 'workflows', icon: <WorkflowOutlined />, label: '工作流' },
    { key: 'codegen', icon: <CodeOutlined />, label: '代码生成' },
    { key: 'settings', icon: <SettingOutlined />, label: '系统设置' },
  ];

  const renderContent = () => {
    switch (currentMenu) {
      case 'forms':
        return <FormManagementPage />;
      case 'models':
        return <DataModelEditor />;
      case 'workflows':
        return <WorkflowPage />;
      case 'codegen':
        return <CodeGeneratorPage />;
      case 'settings':
        return (
          <Card>
            <Title level={4}>系统设置</Title>
            <p>系统设置页面开发中...</p>
          </Card>
        );
      default:
        return <FormManagementPage />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider width={220} style={{ background: '#fff' }}>
        <div style={{ padding: '20px 16px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={3} style={{ margin: 0 }}>☁️ 云天佑</Title>
          <Typography.Text type="secondary">低代码开发平台</Typography.Text>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[currentMenu]}
          onClick={(e) => setCurrentMenu(e.key)}
          items={menuItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: item.label,
          }))}
          style={{ borderRight: 'none' }}
        />
      </Sider>

      {/* 主内容区 */}
      <Layout>
        {/* 顶部导航栏 */}
        <Layout.Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={4} style={{ margin: 0 }}>
              {menuItems.find(m => m.key === currentMenu)?.label}
            </Title>
            <Dropdown overlay={<Menu>
              <Menu.Item key="profile" icon={<UserOutlined />}>
                个人中心
              </Menu.Item>
              <Menu.Item key="logout" onClick={handleLogout}>
                退出登录
              </Menu.Item>
            </Menu>}>
              <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                <Avatar style={{ marginRight: 8 }} icon={<UserOutlined />} />
                <span>{user?.username || '用户'}</span>
              </div>
            </Dropdown>
          </div>
        </Layout.Header>

        {/* 内容区域 */}
        <Layout.Content style={{ margin: '24px', background: '#f0f2f2' }}>
          {renderContent()}
        </Layout>
      </Layout>
    </Layout>
  );
};

export default App;
