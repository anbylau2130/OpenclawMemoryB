# 金蝶云苍穹WebSocket接口文档

**版本**: 金蝶云苍穹 v8.x  
**文档ID**: JJC-20260320-002-iteration8  
**创建时间**: 2026-03-20

---

## 📋 概述

本文档详细说明金蝶云苍穹的WebSocket接口，包括实时通信、消息格式、连接管理等内容。

---

## 🔌 WebSocket连接

### 1. 连接地址

**连接URL**:
```
ws://hostname:port/ws
wss://hostname:port/ws  (SSL)
```

**认证方式**:
```javascript
// 方式1：URL参数
ws://hostname:port/ws?token=YOUR_TOKEN

// 方式2：消息认证
{
  "type": "auth",
  "token": "YOUR_TOKEN"
}
```

### 2. 连接管理

**JavaScript客户端**:
```javascript
class K3CloudWebSocket {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      ...options
    };
    
    this.ws = null;
    this.reconnectAttempts = 0;
    this.heartbeatTimer = null;
    this.subscriptions = new Map();
    this.eventHandlers = new Map();
  }
  
  // 连接
  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.emit('connected');
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.emit('error', error);
          reject(error);
        };
        
        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.stopHeartbeat();
          this.emit('disconnected');
          this.handleReconnect();
        };
        
      } catch (error) {
        reject(error);
      }
    });
  }
  
  // 断开连接
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.stopHeartbeat();
  }
  
  // 处理重连
  handleReconnect() {
    if (this.reconnectAttempts < this.options.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      
      setTimeout(() => {
        this.connect().catch(console.error);
      }, this.options.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('reconnect_failed');
    }
  }
  
  // 开始心跳
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' });
    }, this.options.heartbeatInterval);
  }
  
  // 停止心跳
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
  
  // 发送消息
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.ws.send(message);
    }
  }
  
  // 处理消息
  handleMessage(data) {
    try {
      const message = JSON.parse(data);
      
      switch (message.type) {
        case 'pong':
          // 心跳响应
          break;
          
        case 'auth':
          this.handleAuthResponse(message);
          break;
          
        case 'subscribe':
          this.handleSubscribeResponse(message);
          break;
          
        case 'notification':
          this.handleNotification(message);
          break;
          
        case 'data':
          this.handleData(message);
          break;
          
        case 'error':
          this.handleError(message);
          break;
          
        default:
          console.warn('Unknown message type:', message.type);
      }
      
    } catch (error) {
      console.error('Parse message error:', error);
    }
  }
  
  // 认证
  authenticate(token) {
    this.send({
      type: 'auth',
      token: token
    });
  }
  
  // 处理认证响应
  handleAuthResponse(message) {
    if (message.success) {
      this.emit('authenticated');
    } else {
      this.emit('auth_failed', message.error);
    }
  }
  
  // 订阅
  subscribe(topic, callback) {
    const subscriptionId = this.generateId();
    
    this.subscriptions.set(subscriptionId, { topic, callback });
    
    this.send({
      type: 'subscribe',
      subscriptionId: subscriptionId,
      topic: topic
    });
    
    return subscriptionId;
  }
  
  // 取消订阅
  unsubscribe(subscriptionId) {
    if (this.subscriptions.has(subscriptionId)) {
      this.subscriptions.delete(subscriptionId);
      
      this.send({
        type: 'unsubscribe',
        subscriptionId: subscriptionId
      });
    }
  }
  
  // 处理订阅响应
  handleSubscribeResponse(message) {
    const { subscriptionId, success, error } = message;
    
    if (!success) {
      console.error('Subscribe failed:', error);
      this.subscriptions.delete(subscriptionId);
    }
  }
  
  // 处理数据
  handleData(message) {
    const { subscriptionId, data } = message;
    const subscription = this.subscriptions.get(subscriptionId);
    
    if (subscription && subscription.callback) {
      subscription.callback(data);
    }
  }
  
  // 处理通知
  handleNotification(message) {
    this.emit('notification', message.data);
  }
  
  // 处理错误
  handleError(message) {
    console.error('Server error:', message.error);
    this.emit('error', message.error);
  }
  
  // 事件监听
  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(handler);
  }
  
  // 移除事件监听
  off(event, handler) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }
  
  // 触发事件
  emit(event, data) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).forEach(handler => {
        handler(data);
      });
    }
  }
  
  // 生成ID
  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }
}

// 使用示例
const ws = new K3CloudWebSocket('wss://k3cloud.example.com/ws');

ws.on('connected', () => {
  console.log('Connected to server');
  ws.authenticate('YOUR_TOKEN');
});

ws.on('authenticated', () => {
  console.log('Authenticated successfully');
  
  // 订阅单据状态变更
  const subscriptionId = ws.subscribe('bill.status.changed', (data) => {
    console.log('Bill status changed:', data);
  });
  
  // 订阅消息通知
  ws.subscribe('notification', (notification) => {
    console.log('New notification:', notification);
  });
});

ws.on('notification', (notification) => {
  // 显示通知
  showNotification(notification);
});

ws.connect().catch(console.error);
```

---

## 📨 消息格式

### 1. 消息类型

**认证消息**:
```json
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

// 认证成功响应
{
  "type": "auth",
  "success": true,
  "userId": "1001",
  "username": "admin"
}

// 认证失败响应
{
  "type": "auth",
  "success": false,
  "error": "Invalid token"
}
```

**订阅消息**:
```json
{
  "type": "subscribe",
  "subscriptionId": "abc123",
  "topic": "bill.status.changed",
  "filter": {
    "billId": "1001"
  }
}

// 订阅成功响应
{
  "type": "subscribe",
  "subscriptionId": "abc123",
  "success": true
}

// 订阅失败响应
{
  "type": "subscribe",
  "subscriptionId": "abc123",
  "success": false,
  "error": "Topic not found"
}
```

**数据消息**:
```json
{
  "type": "data",
  "subscriptionId": "abc123",
  "data": {
    "billId": "1001",
    "billNo": "SO20260320001",
    "oldStatus": "SUBMITTED",
    "newStatus": "AUDITED",
    "operator": "admin",
    "operateTime": "2026-03-20T10:30:00Z"
  }
}
```

**通知消息**:
```json
{
  "type": "notification",
  "data": {
    "id": "n001",
    "title": "单据审核通过",
    "content": "您的销售订单 SO20260320001 已审核通过",
    "type": "SUCCESS",
    "userId": "1001",
    "createTime": "2026-03-20T10:30:00Z"
  }
}
```

**心跳消息**:
```json
// Ping
{
  "type": "ping"
}

// Pong
{
  "type": "pong"
}
```

### 2. 订阅主题

**支持的订阅主题**:

| 主题 | 说明 | 过滤条件 |
|-----|------|---------|
| bill.status.changed | 单据状态变更 | billId, billType, status |
| bill.created | 单据创建 | billType, creatorId |
| bill.deleted | 单据删除 | billId, billType |
| notification | 系统通知 | userId, type |
| message | 即时消息 | userId, groupId |
| data.sync | 数据同步 | entityType, entityId |

---

## 🔧 服务端实现

**Spring WebSocket配置**:
```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(k3CloudWebSocketHandler(), "/ws")
            .addInterceptors(new WebSocketAuthInterceptor())
            .setAllowedOrigins("*");
    }
    
    @Bean
    public K3CloudWebSocketHandler k3CloudWebSocketHandler() {
        return new K3CloudWebSocketHandler();
    }
}
```

**WebSocket处理器**:
```java
@Component
@Slf4j
public class K3CloudWebSocketHandler extends TextWebSocketHandler {
    
    private final ConcurrentHashMap<String, WebSocketSession> sessions = 
        new ConcurrentHashMap<>();
    
    private final ConcurrentHashMap<String, Set<Subscription>> subscriptions = 
        new ConcurrentHashMap<>();
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Autowired
    private MessageService messageService;
    
    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        String sessionId = session.getId();
        sessions.put(sessionId, session);
        subscriptions.put(sessionId, new HashSet<>());
        
        log.info("WebSocket connected: {}", sessionId);
    }
    
    @Override
    protected void handleTextMessage(WebSocketSession session, 
                                      TextMessage message) throws Exception {
        String payload = message.getPayload();
        JsonNode jsonNode = objectMapper.readTree(payload);
        String type = jsonNode.get("type").asText();
        
        switch (type) {
            case "auth":
                handleAuth(session, jsonNode);
                break;
            case "subscribe":
                handleSubscribe(session, jsonNode);
                break;
            case "unsubscribe":
                handleUnsubscribe(session, jsonNode);
                break;
            case "ping":
                handlePing(session);
                break;
            default:
                log.warn("Unknown message type: {}", type);
        }
    }
    
    @Override
    public void afterConnectionClosed(WebSocketSession session, 
                                       CloseStatus status) {
        String sessionId = session.getId();
        sessions.remove(sessionId);
        subscriptions.remove(sessionId);
        
        log.info("WebSocket disconnected: {}", sessionId);
    }
    
    @Override
    public void handleTransportError(WebSocketSession session, 
                                      Throwable exception) {
        log.error("WebSocket transport error: {}", session.getId(), exception);
    }
    
    // 处理认证
    private void handleAuth(WebSocketSession session, JsonNode jsonNode) 
            throws Exception {
        String token = jsonNode.get("token").asText();
        
        try {
            // 验证token
            UserInfo userInfo = authService.validateToken(token);
            
            // 保存用户信息到session
            session.getAttributes().put("userInfo", userInfo);
            
            // 发送认证成功响应
            sendMessage(session, Map.of(
                "type", "auth",
                "success", true,
                "userId", userInfo.getUserId(),
                "username", userInfo.getUsername()
            ));
            
        } catch (Exception e) {
            // 发送认证失败响应
            sendMessage(session, Map.of(
                "type", "auth",
                "success", false,
                "error", e.getMessage()
            ));
        }
    }
    
    // 处理订阅
    private void handleSubscribe(WebSocketSession session, JsonNode jsonNode) 
            throws Exception {
        String subscriptionId = jsonNode.get("subscriptionId").asText();
        String topic = jsonNode.get("topic").asText();
        JsonNode filter = jsonNode.get("filter");
        
        // 检查权限
        UserInfo userInfo = (UserInfo) session.getAttributes().get("userInfo");
        if (!checkPermission(userInfo, topic)) {
            sendMessage(session, Map.of(
                "type", "subscribe",
                "subscriptionId", subscriptionId,
                "success", false,
                "error", "Permission denied"
            ));
            return;
        }
        
        // 添加订阅
        Subscription subscription = new Subscription(
            subscriptionId, topic, filter, userInfo.getUserId());
        
        subscriptions.get(session.getId()).add(subscription);
        
        // 发送订阅成功响应
        sendMessage(session, Map.of(
            "type", "subscribe",
            "subscriptionId", subscriptionId,
            "success", true
        ));
    }
    
    // 处理取消订阅
    private void handleUnsubscribe(WebSocketSession session, JsonNode jsonNode) 
            throws Exception {
        String subscriptionId = jsonNode.get("subscriptionId").asText();
        
        Set<Subscription> sessionSubscriptions = subscriptions.get(session.getId());
        sessionSubscriptions.removeIf(sub -> 
            sub.getSubscriptionId().equals(subscriptionId));
    }
    
    // 处理心跳
    private void handlePing(WebSocketSession session) throws Exception {
        sendMessage(session, Map.of("type", "pong"));
    }
    
    // 发送消息
    private void sendMessage(WebSocketSession session, Object message) 
            throws Exception {
        String json = objectMapper.writeValueAsString(message);
        session.sendMessage(new TextMessage(json));
    }
    
    // 广播消息
    public void broadcast(String topic, Object data, 
                          Predicate<Subscription> filter) {
        subscriptions.forEach((sessionId, subs) -> {
            subs.stream()
                .filter(sub -> sub.getTopic().equals(topic))
                .filter(filter)
                .forEach(sub -> {
                    WebSocketSession session = sessions.get(sessionId);
                    if (session != null && session.isOpen()) {
                        try {
                            sendMessage(session, Map.of(
                                "type", "data",
                                "subscriptionId", sub.getSubscriptionId(),
                                "data", data
                            ));
                        } catch (Exception e) {
                            log.error("Send message error", e);
                        }
                    }
                });
        });
    }
}
```

---

## 📚 相关文档

- [REST API参考](01-REST API参考.md)
- [GraphQL接口](02-GraphQL接口.md)
- [前端开发进阶](../二开文档/16-前端开发进阶.md)

---

**文档版本**: v1.0  
**最后更新**: 2026-03-20  
**维护者**: 尚书省·工部
