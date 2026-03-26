const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const db = require('../database');
const { authenticate } = require('../middleware/auth');

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h';

// 用户注册
router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;

    // 验证输入
    if (!username || !email || !password) {
      return res.status(400).json({ error: '用户名、邮箱和密码为必填项' });
    }

    if (password.length < 6) {
      return res.status(400).json({ error: '密码长度至少为6位' });
    }

    // 检查用户是否已存在
    db.get('SELECT id FROM users WHERE username = ? OR email = ?', [username, email], async (err, user) => {
      if (err) {
        return res.status(500).json({ error: '数据库查询失败' });
      }

      if (user) {
        return res.status(409).json({ error: '用户名或邮箱已存在' });
      }

      // 加密密码
      const passwordHash = await bcrypt.hash(password, 10);

      // 创建用户
      db.run(
        'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
        [username, email, passwordHash],
        function(err) {
          if (err) {
            return res.status(500).json({ error: '用户创建失败' });
          }

          const userId = this.lastID;

          // 默认分配普通用户角色
          db.run(
            'INSERT INTO user_roles (user_id, role_id) VALUES (?, (SELECT id FROM roles WHERE name = ?))',
            [userId, 'user'],
            (err) => {
              if (err) {
                console.error('分配默认角色失败:', err);
              }
            }
          );

          // 生成JWT令牌
          const token = jwt.sign(
            { id: userId, username, email },
            JWT_SECRET,
            { expiresIn: JWT_EXPIRES_IN }
          );

          res.status(201).json({
            message: '注册成功',
            user: { id: userId, username, email },
            token
          });
        }
      );
    });
  } catch (error) {
    res.status(500).json({ error: '注册失败', message: error.message });
  }
});

// 用户登录
router.post('/login', (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: '用户名和密码为必填项' });
    }

    // 查找用户
    db.get('SELECT * FROM users WHERE username = ? OR email = ?', [username, username], async (err, user) => {
      if (err) {
        return res.status(500).json({ error: '数据库查询失败' });
      }

      if (!user) {
        return res.status(401).json({ error: '用户名或密码错误' });
      }

      // 验证密码
      const isValidPassword = await bcrypt.compare(password, user.password_hash);

      if (!isValidPassword) {
        return res.status(401).json({ error: '用户名或密码错误' });
      }

      // 查询用户角色
      db.all(
        'SELECT r.name FROM roles r JOIN user_roles ur ON r.id = ur.role_id WHERE ur.user_id = ?',
        [user.id],
        (err, roles) => {
          if (err) {
            console.error('查询角色失败:', err);
          }

          const roleNames = roles ? roles.map(r => r.name) : [];

          // 生成JWT令牌
          const token = jwt.sign(
            { id: user.id, username: user.username, email: user.email, roles: roleNames },
            JWT_SECRET,
            { expiresIn: JWT_EXPIRES_IN }
          );

          res.json({
            message: '登录成功',
            user: {
              id: user.id,
              username: user.username,
              email: user.email,
              roles: roleNames
            },
            token
          });
        }
      );
    });
  } catch (error) {
    res.status(500).json({ error: '登录失败', message: error.message });
  }
});

// 获取当前用户信息
router.get('/me', authenticate, (req, res) => {
  db.get('SELECT id, username, email, created_at FROM users WHERE id = ?', [req.user.id], (err, user) => {
    if (err) {
      return res.status(500).json({ error: '查询用户信息失败' });
    }

    if (!user) {
      return res.status(404).json({ error: '用户不存在' });
    }

    // 查询用户角色和权限
    db.all(
      `SELECT r.name as role_name, p.name as permission_name
       FROM roles r
       JOIN user_roles ur ON r.id = ur.role_id
       LEFT JOIN role_permissions rp ON r.id = rp.role_id
       LEFT JOIN permissions p ON rp.permission_id = p.id
       WHERE ur.user_id = ?`,
      [user.id],
      (err, results) => {
        if (err) {
          console.error('查询权限失败:', err);
        }

        const roles = [...new Set(results.map(r => r.role_name))];
        const permissions = [...new Set(results.filter(r => r.permission_name).map(r => r.permission_name))];

        res.json({
          user: {
            ...user,
            roles,
            permissions
          }
        });
      }
    );
  });
});

// 刷新令牌
router.post('/refresh', authenticate, (req, res) => {
  const token = jwt.sign(
    { id: req.user.id, username: req.user.username, email: req.user.email },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );

  res.json({ message: '令牌刷新成功', token });
});

module.exports = router;
