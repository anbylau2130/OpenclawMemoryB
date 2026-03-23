# 代码模式标准库

这是项目的代码模式标准库，定义了通用的代码模式和最佳实践。

---

## 错误处理

### API 错误处理

```typescript
// ✅ 推荐
try {
  const response = await fetch('/api/endpoint');
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.message || 'Request failed');
  }
  
  return { success: true, data };
} catch (error) {
  console.error('API Error:', error);
  return { 
    success: false, 
    error: error instanceof Error ? error.message : 'Unknown error' 
  };
}
```

### 组件错误边界

```typescript
// ✅ 推荐
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong</div>;
    }
    return this.props.children;
  }
}
```

---

## 日志记录

### 日志工具

```typescript
// ✅ 推荐
const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data);
  },
  
  error: (message: string, error?: Error) => {
    console.error(`[ERROR] ${message}`, error);
  },
  
  warn: (message: string, data?: any) => {
    console.warn(`[WARN] ${message}`, data);
  }
};

// 使用
logger.info('User logged in', { userId: '123' });
logger.error('API call failed', error);
```

---

## 测试模式

### 单元测试

```typescript
// ✅ 推荐
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('should validate email format', async () => {
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText(/email/i);
    await userEvent.type(emailInput, 'invalid-email');
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    await userEvent.click(submitButton);
    
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  });
  
  it('should submit valid form', async () => {
    const mockSubmit = jest.fn();
    render(<LoginForm onSubmit={mockSubmit} />);
    
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    
    expect(mockSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });
});
```

---

## API 调用

### Fetch 封装

```typescript
// ✅ 推荐
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

async function apiCall<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.message || 'Request failed',
      };
    }

    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

// 使用
const result = await apiCall<User>('/api/user/123');
if (result.success) {
  console.log(result.data);
} else {
  console.error(result.error);
}
```

---

## 表单处理

### React Hook Form + Zod

```typescript
// ✅ 推荐
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginForm) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      
      <input type="password" {...register('password')} />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">Login</button>
    </form>
  );
}
```

---

## 状态管理

### React Context

```typescript
// ✅ 推荐
import { createContext, useContext, useState, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = (user: User) => setUser(user);
  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

---

## 代码规范

### 函数长度
- ✅ **推荐**：函数不超过 50 行
- ⚠️ **警告**：函数超过 35 行时考虑拆分
- ❌ **禁止**：函数超过 100 行

### 命名约定
- 组件：PascalCase（`LoginForm`）
- 函数：camelCase（`handleSubmit`）
- 常量：UPPER_SNAKE_CASE（`MAX_RETRIES`）
- 文件：kebab-case（`login-form.tsx`）

### 注释
- ✅ 复杂逻辑添加注释
- ✅ 公共 API 添加 JSDoc
- ❌ 显而易见的代码不注释

---

_持续更新，根据项目需要添加新模式_
