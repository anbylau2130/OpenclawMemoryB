const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

// JWT认证中间件
const authenticate = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: '未提供认证令牌' });
  }

  const token = authHeader.substring(7);

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: '无效或过期的令牌' });
  }
};

// RBAC权限检查中间件
const checkPermission = (resource, action) => {
  return async (req, res, next) => {
    const userId = req.user.id;

    const query = `
      SELECT p.name 
      FROM permissions p
      JOIN role_permissions rp ON p.id = rp.permission_id
      JOIN user_roles ur ON rp.role_id = ur.role_id
      WHERE ur.user_id = ? AND p.resource = ? AND p.action = ?
    `;

    db.get(query, [userId, resource, action], (err, permission) => {
      if (err) {
        return res.status(500).json({ error: '权限检查失败' });
      }

      if (!permission) {
        return res.status(403).json({ error: '权限不足' });
      }

      next();
    });
  };
};

// 角色检查中间件
const checkRole = (...allowedRoles) => {
  return async (req, res, next) => {
    const userId = req.user.id;

    const query = `
      SELECT r.name 
      FROM roles r
      JOIN user_roles ur ON r.id = ur.role_id
      WHERE ur.user_id = ?
    `;

    db.all(query, [userId], (err, roles) => {
      if (err) {
        return res.status(500).json({ error: '角色检查失败' });
      }

      const userRoles = roles.map(r => r.name);
      const hasRole = allowedRoles.some(role => userRoles.includes(role));

      if (!hasRole) {
        return res.status(403).json({ error: '角色权限不足' });
      }

      next();
    });
  };
};

module.exports = { authenticate, checkPermission, checkRole };
