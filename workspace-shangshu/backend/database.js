const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'app.db');

// 创建数据库连接
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('数据库连接失败:', err.message);
  } else {
    console.log('✅ 数据库连接成功:', dbPath);
  }
});

// 初始化数据库表
db.serialize(() => {
  // 1. 用户表
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  console.log('✅ 用户表创建成功');

  // 2. 角色表
  db.run(`
    CREATE TABLE IF NOT EXISTS roles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      description TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  console.log('✅ 角色表创建成功');

  // 3. 权限表
  db.run(`
    CREATE TABLE IF NOT EXISTS permissions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      resource TEXT NOT NULL,
      action TEXT NOT NULL,
      description TEXT
    )
  `);
  console.log('✅ 权限表创建成功');

  // 4. 用户角色关联表
  db.run(`
    CREATE TABLE IF NOT EXISTS user_roles (
      user_id INTEGER NOT NULL,
      role_id INTEGER NOT NULL,
      assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (user_id, role_id),
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
      FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
    )
  `);
  console.log('✅ 用户角色关联表创建成功');

  // 5. 角色权限关联表
  db.run(`
    CREATE TABLE IF NOT EXISTS role_permissions (
      role_id INTEGER NOT NULL,
      permission_id INTEGER NOT NULL,
      granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (role_id, permission_id),
      FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
      FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
    )
  `);
  console.log('✅ 角色权限关联表创建成功');

  // 初始化角色数据
  const roles = [
    ['admin', '系统管理员'],
    ['user', '普通用户'],
    ['manager', '管理者']
  ];

  const insertRole = db.prepare('INSERT OR IGNORE INTO roles (name, description) VALUES (?, ?)');
  roles.forEach(role => insertRole.run(role));
  insertRole.finalize();
  console.log('✅ 初始角色数据插入成功');

  // 初始化权限数据
  const permissions = [
    ['users:read', 'users', 'read', '查看用户'],
    ['users:write', 'users', 'write', '编辑用户'],
    ['users:delete', 'users', 'delete', '删除用户'],
    ['roles:read', 'roles', 'read', '查看角色'],
    ['roles:write', 'roles', 'write', '编辑角色']
  ];

  const insertPerm = db.prepare('INSERT OR IGNORE INTO permissions (name, resource, action, description) VALUES (?, ?, ?, ?)');
  permissions.forEach(perm => insertPerm.run(perm));
  insertPerm.finalize();
  console.log('✅ 初始权限数据插入成功');
});

module.exports = db;
