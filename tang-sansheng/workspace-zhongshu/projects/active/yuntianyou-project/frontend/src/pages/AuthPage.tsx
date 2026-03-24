import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Typography } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

interface AuthProps {
  onLoginSuccess: (user: any, token: string) => void;
}

const AuthPage: React.FC<AuthProps> = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const response = await axios.post(endpoint, values);
      
      const { token, ...user } = response.data;
      
      // 保存token
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      message.success(isLogin ? '登录成功！' : '注册成功！');
      onLoginSuccess(user, token);
    } catch (error: any) {
      message.error(error.response?.data?.error || '操作失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ margin: 0 }}>☁️ 云天佑</Title>
          <Text type="secondary">低代码开发平台</Text>
        </div>
        
        <Title level={4} style={{ textAlign: 'center' }}>
          {isLogin ? '登录' : '注册'}
        </Title>
        
        <Form
          name="auth"
          onFinish={onFinish}
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="用户名" 
              size="large"
            />
          </Form.Item>
          
          {!isLogin && (
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '邮箱格式不正确' }
              ]}
            >
              <Input 
                prefix={<MailOutlined />} 
                placeholder="邮箱" 
                size="large"
              />
            </Form.Item>
          )}
          
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password 
              prefix={<LockOutlined />} 
              placeholder="密码" 
              size="large"
            />
          </Form.Item>
          
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              size="large"
              block
            >
              {isLogin ? '登录' : '注册'}
            </Button>
          </Form.Item>
        </Form>
        
        <div style={{ textAlign: 'center' }}>
          <Button type="link" onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? '没有账号？立即注册' : '已有账号？立即登录'}
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default AuthPage;
