# REST API接口

<cite>
**本文档引用的文件**   
- [reply_server.py](file://reply_server.py)
- [config.py](file://config.py)
- [README.md](file://README.md)
- [db_manager.py](file://db_manager.py)
- [cookie_manager.py](file://cookie_manager.py)
- [XianyuAutoAsync.py](file://XianyuAutoAsync.py)
</cite>

## 目录
1. [简介](#简介)
2. [认证机制](#认证机制)
3. [用户管理接口](#用户管理接口)
4. [账号管理接口](#账号管理接口)
5. [消息回复配置接口](#消息回复配置接口)
6. [自动发货设置接口](#自动发货设置接口)
7. [通知系统配置接口](#通知系统配置接口)
8. [系统设置接口](#系统设置接口)
9. [文件管理接口](#文件管理接口)
10. [商品管理接口](#商品管理接口)
11. [卡券与发货规则接口](#卡券与发货规则接口)
12. [备份与恢复接口](#备份与恢复接口)
13. [错误处理与状态码](#错误处理与状态码)

## 简介
本API文档详细描述了闲鱼自动回复系统的所有REST API端点。系统基于FastAPI框架构建，提供完整的用户认证、账号管理、消息回复、自动发货、通知配置等功能。所有接口均采用JWT（JSON Web Token）进行认证和授权，确保系统的安全性和数据隔离性。

系统支持多用户架构，每个用户的数据完全隔离，管理员拥有最高权限。API设计遵循RESTful原则，使用标准的HTTP方法和状态码。所有请求和响应数据均采用JSON格式，便于客户端集成和处理。

**Section sources**
- [reply_server.py](file://reply_server.py#L308-L314)
- [README.md](file://README.md#L13-L15)

## 认证机制
系统采用基于JWT的令牌认证机制，所有需要权限的API端点都要求在HTTP请求头中包含有效的Bearer Token。认证流程包括登录、验证、登出三个核心接口，支持多种登录方式。

### JWT认证流程
1. **登录获取Token**：用户通过`/login`接口进行身份验证，成功后服务器返回一个JWT Token。
2. **请求携带Token**：后续所有需要认证的请求，必须在`Authorization`头中包含`Bearer <token>`。
3. **Token验证**：服务器通过`verify_token`函数验证Token的有效性和过期时间。
4. **登出失效Token**：用户通过`/logout`接口登出，服务器将Token从有效会话中移除。

Token的有效期为24小时，过期后需要重新登录获取新Token。系统通过中间件自动记录每个API请求的用户信息和处理时间，便于审计和监控。

**Section sources**
- [reply_server.py](file://reply_server.py#L48-L219)
- [reply_server.py](file://reply_server.py#L330-L357)

### /login - 用户登录
此接口用于用户登录系统，支持多种登录方式，包括用户名密码、邮箱密码和邮箱验证码登录。

**HTTP方法**: `POST`  
**URL路径**: `/login`

**请求参数 (Body)**:
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "verification_code": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `username` | string | 否 | 用户名，与密码一起用于用户名密码登录 |
| `password` | string | 否 | 密码，与用户名或邮箱一起使用 |
| `email` | string | 否 | 邮箱地址，用于邮箱密码或邮箱验证码登录 |
| `verification_code` | string | 否 | 验证码，与邮箱一起用于邮箱验证码登录 |

**请求体JSON结构**:
- 用户名密码登录: `{"username": "admin", "password": "admin123"}`
- 邮箱密码登录: `{"email": "user@example.com", "password": "password123"}`
- 邮箱验证码登录: `{"email": "user@example.com", "verification_code": "123456"}`

**响应格式**:
```json
{
  "success": true,
  "token": "string",
  "message": "string",
  "user_id": 0,
  "username": "string",
  "is_admin": true
}
```

**状态码**:
- `200 OK`: 登录成功，返回Token和用户信息
- `401 Unauthorized`: 认证失败，用户名或密码错误
- `400 Bad Request`: 请求参数无效

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**JavaScript调用示例**:
```javascript
fetch('/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    localStorage.setItem('authToken', data.token);
    console.log('登录成功');
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L542-L659)
- [reply_server.py](file://reply_server.py#L112-L127)

### /verify - 验证Token
此接口用于验证当前用户的Token是否有效，常用于前端在页面加载时检查用户登录状态。

**HTTP方法**: `GET`  
**URL路径**: `/verify`

**请求参数 (Header)**:
- `Authorization`: Bearer Token，格式为 `Bearer <token>`

**响应格式**:
```json
{
  "authenticated": true,
  "user_id": 0,
  "username": "string",
  "is_admin": true
}
```

**状态码**:
- `200 OK`: Token有效，返回用户信息
- `401 Unauthorized`: Token无效或已过期

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/verify" \
  -H "Authorization: Bearer your-jwt-token-here"
```

**JavaScript调用示例**:
```javascript
fetch('/verify', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
})
.then(response => response.json())
.then(data => {
  if (data.authenticated) {
    console.log(`欢迎, ${data.username}!`);
  } else {
    window.location.href = '/login.html';
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L663-L672)

### /logout - 用户登出
此接口用于用户登出系统，使当前Token失效。

**HTTP方法**: `POST`  
**URL路径**: `/logout`

**请求参数 (Header)**:
- `Authorization`: Bearer Token，格式为 `Bearer <token>`

**响应格式**:
```json
{
  "message": "已登出"
}
```

**状态码**:
- `200 OK`: 登出成功

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/logout" \
  -H "Authorization: Bearer your-jwt-token-here"
```

**JavaScript调用示例**:
```javascript
fetch('/logout', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(() => {
  localStorage.removeItem('authToken');
  window.location.href = '/login.html';
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L676-L680)

### /change-admin-password - 修改管理员密码
此接口用于修改管理员密码，需要管理员权限才能调用。

**HTTP方法**: `POST`  
**URL路径**: `/change-admin-password`

**请求参数 (Body)**:
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `current_password` | string | 是 | 当前密码 |
| `new_password` | string | 是 | 新密码 |

**响应格式**:
```json
{
  "success": true,
  "message": "string"
}
```

**状态码**:
- `200 OK`: 密码修改成功
- `401 Unauthorized`: 未授权访问，Token无效
- `403 Forbidden`: 权限不足，非管理员用户
- `400 Bad Request`: 当前密码错误

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/change-admin-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-admin-token" \
  -d '{"current_password": "admin123", "new_password": "newpassword456"}'
```

**JavaScript调用示例**:
```javascript
fetch('/change-admin-password', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({
    current_password: 'admin123',
    new_password: 'newpassword456'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    alert('密码修改成功');
  } else {
    alert('密码修改失败: ' + data.message);
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L684-L705)

## 用户管理接口
系统提供完整的用户注册和管理功能，支持邮箱验证码注册和图形验证码保护，防止恶意注册和暴力破解。

### /register - 用户注册
此接口用于新用户注册，需要提供邮箱验证码进行验证。

**HTTP方法**: `POST`  
**URL路径**: `/register`

**请求参数 (Body)**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "verification_code": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `username` | string | 是 | 用户名，必须唯一 |
| `email` | string | 是 | 邮箱地址，用于接收验证码 |
| `password` | string | 是 | 用户密码 |
| `verification_code` | string | 是 | 邮箱收到的验证码 |

**响应格式**:
```json
{
  "success": true,
  "message": "string"
}
```

**状态码**:
- `200 OK`: 注册成功
- `400 Bad Request`: 参数无效或注册失败
- `403 Forbidden`: 注册功能已关闭

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123",
    "verification_code": "654321"
  }'
```

**JavaScript调用示例**:
```javascript
fetch('/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'newuser',
    email: 'newuser@example.com',
    password: 'password123',
    verification_code: '654321'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    alert('注册成功，请登录');
    window.location.href = '/login.html';
  } else {
    alert('注册失败: ' + data.message);
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L844-L905)

### /send-verification-code - 发送验证码
此接口用于发送邮箱验证码，需要先通过图形验证码验证。

**HTTP方法**: `POST`  
**URL路径**: `/send-verification-code`

**请求参数 (Body)**:
```json
{
  "email": "string",
  "session_id": "string",
  "type": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `email` | string | 是 | 接收验证码的邮箱地址 |
| `session_id` | string | 否 | 图形验证码会话ID |
| `type` | string | 否 | 验证码类型，`register`或`login` |

**响应格式**:
```json
{
  "success": true,
  "message": "string"
}
```

**状态码**:
- `200 OK`: 验证码发送成功
- `400 Bad Request`: 参数无效或发送失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/send-verification-code" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "type": "register"}'
```

**JavaScript调用示例**:
```javascript
fetch('/send-verification-code', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    type: 'register'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    alert('验证码已发送到您的邮箱');
  } else {
    alert('发送验证码失败: ' + data.message);
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L776-L840)

### /generate-captcha - 生成图形验证码
此接口用于生成图形验证码，用于保护注册和登录等敏感操作。

**HTTP方法**: `POST`  
**URL路径**: `/generate-captcha`

**请求参数 (Body)**:
```json
{
  "session_id": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `session_id` | string | 是 | 验证码会话ID |

**响应格式**:
```json
{
  "success": true,
  "captcha_image": "string",
  "session_id": "string",
  "message": "string"
}
```

**状态码**:
- `200 OK`: 验证码生成成功
- `400 Bad Request`: 生成失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/generate-captcha" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session123"}'
```

**JavaScript调用示例**:
```javascript
fetch('/generate-captcha', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id: 'session123' })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    document.getElementById('captcha-img').src = data.captcha_image;
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L708-L747)

### /verify-captcha - 验证图形验证码
此接口用于验证用户输入的图形验证码是否正确。

**HTTP方法**: `POST`  
**URL路径**: `/verify-captcha`

**请求参数 (Body)**:
```json
{
  "session_id": "string",
  "captcha_code": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `session_id` | string | 是 | 验证码会话ID |
| `captcha_code` | string | 是 | 用户输入的验证码 |

**响应格式**:
```json
{
  "success": true,
  "message": "string"
}
```

**状态码**:
- `200 OK`: 验证码正确
- `400 Bad Request`: 验证码错误或已过期

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/verify-captcha" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session123", "captcha_code": "ABCD"}'
```

**JavaScript调用示例**:
```javascript
fetch('/verify-captcha', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'session123',
    captcha_code: 'ABCD'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    alert('验证码验证成功');
  } else {
    alert('验证码错误');
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L751-L772)

## 账号管理接口
账号管理接口允许用户添加、更新、删除和管理闲鱼账号，包括Cookie管理、状态控制和备注信息。

### /cookies - 管理账号Cookie
此接口集合用于管理用户的闲鱼账号Cookie，包括添加、更新、删除和获取账号列表。

#### GET /cookies - 获取账号列表
获取当前用户的所有账号ID列表。

**HTTP方法**: `GET`  
**URL路径**: `/cookies`

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
["account1", "account2"]
```

**状态码**:
- `200 OK`: 成功获取账号列表

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/cookies" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch('/cookies', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(accounts => {
  console.log('账号列表:', accounts);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L1141-L1150)

#### GET /cookies/details - 获取账号详细信息
获取所有账号的详细信息，包括Cookie值、启用状态、自动确认设置和备注。

**HTTP方法**: `GET`  
**URL路径**: `/cookies/details`

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
[
  {
    "id": "string",
    "value": "string",
    "enabled": true,
    "auto_confirm": true,
    "remark": "string",
    "pause_duration": 10
  }
]
```

**状态码**:
- `200 OK`: 成功获取详细信息

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/cookies/details" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch('/cookies/details', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(details => {
  console.log('账号详情:', details);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L1153-L1180)

#### POST /cookies - 添加新账号
添加一个新的闲鱼账号。

**HTTP方法**: `POST`  
**URL路径**: `/cookies`

**请求参数 (Body)**:
```json
{
  "id": "string",
  "value": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 账号ID，必须唯一 |
| `value` | string | 是 | Cookie值 |

**响应格式**:
```json
{
  "msg": "success"
}
```

**状态码**:
- `200 OK`: 账号添加成功
- `400 Bad Request`: 参数无效或ID冲突

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/cookies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"id": "newaccount", "value": "cookie=value;"}'
```

**JavaScript调用示例**:
```javascript
fetch('/cookies', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    id: 'newaccount',
    value: 'cookie=value;'
  })
})
.then(response => response.json())
.then(data => {
  if (data.msg === 'success') {
    alert('账号添加成功');
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L1183-L1215)

#### PUT /cookies/{cid} - 更新账号Cookie
更新指定账号的Cookie值。

**HTTP方法**: `PUT`  
**URL路径**: `/cookies/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "id": "string",
  "value": "string"
}
```

**响应格式**:
```json
{
  "msg": "updated"
}
```

**状态码**:
- `200 OK`: Cookie更新成功
- `403 Forbidden`: 无权限操作该账号
- `400 Bad Request`: 更新失败

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/cookies/account1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"id": "account1", "value": "new-cookie=value;"}'
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    id: accountId,
    value: newCookieValue
  })
})
.then(response => response.json())
.then(data => {
  if (data.msg === 'updated') {
    alert('Cookie更新成功');
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L1217-L1252)

#### DELETE /cookies/{cid} - 删除账号
删除指定的闲鱼账号。

**HTTP方法**: `DELETE`  
**URL路径**: `/cookies/{cid}`

**路径参数**:
- `cid`: 要删除的账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "msg": "removed"
}
```

**状态码**:
- `200 OK`: 账号删除成功
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X DELETE "http://localhost:8080/cookies/account1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  if (data.msg === 'removed') {
    alert('账号删除成功');
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2796-L2815)

### /cookies/{cid}/status - 账号状态管理
管理账号的启用/禁用状态。

#### PUT /cookies/{cid}/status - 更新账号状态
更新指定账号的启用或禁用状态。

**HTTP方法**: `PUT`  
**URL路径**: `/cookies/{cid}/status`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "enabled": true
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `enabled` | boolean | 是 | 是否启用账号 |

**响应格式**:
```json
{
  "msg": "status updated",
  "enabled": true
}
```

**状态码**:
- `200 OK`: 状态更新成功
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/cookies/account1/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"enabled": false}'
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}/status`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({ enabled: false })
})
.then(response => response.json())
.then(data => {
  alert(`账号状态已${data.enabled ? '启用' : '禁用'}`);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2337-L2357)

### /cookies/{cid}/remark - 账号备注管理
管理账号的备注信息，便于用户识别和管理多个账号。

#### PUT /cookies/{cid}/remark - 更新账号备注
更新指定账号的备注信息。

**HTTP方法**: `PUT`  
**URL路径**: `/cookies/{cid}/remark`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "remark": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `remark` | string | 是 | 备注内容 |

**响应格式**:
```json
{
  "message": "备注更新成功",
  "remark": "string"
}
```

**状态码**:
- `200 OK`: 备注更新成功
- `403 Forbidden`: 无权限操作该账号
- `500 Internal Server Error`: 更新失败

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/cookies/account1/remark" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"remark": "主账号，用于重要交易"}'
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}/remark`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({ remark: '主账号，用于重要交易' })
})
.then(response => response.json())
.then(data => {
  alert('备注更新成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2889-L2917)

#### GET /cookies/{cid}/remark - 获取账号备注
获取指定账号的备注信息。

**HTTP方法**: `GET`  
**URL路径**: `/cookies/{cid}/remark`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "remark": "string",
  "message": "获取备注成功"
}
```

**状态码**:
- `200 OK`: 成功获取备注
- `403 Forbidden`: 无权限访问该账号
- `404 Not Found`: 账号不存在

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/cookies/account1/remark" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}/remark`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  console.log('账号备注:', data.remark);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2919-L2946)

### /cookies/{cid}/auto-confirm - 自动确认发货设置
管理账号的自动确认发货功能，控制是否自动确认买家付款。

#### PUT /cookies/{cid}/auto-confirm - 更新自动确认设置
更新指定账号的自动确认发货设置。

**HTTP方法**: `PUT`  
**URL路径**: `/cookies/{cid}/auto-confirm`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "auto_confirm": true
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `auto_confirm` | boolean | 是 | 是否启用自动确认 |

**响应格式**:
```json
{
  "msg": "success",
  "auto_confirm": true,
  "message": "自动确认发货已开启"
}
```

**状态码**:
- `200 OK`: 设置更新成功
- `403 Forbidden`: 无权限操作该账号
- `500 Internal Server Error`: 更新失败

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/cookies/account1/auto-confirm" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"auto_confirm": true}'
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}/auto-confirm`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({ auto_confirm: true })
})
.then(response => response.json())
.then(data => {
  alert(data.message);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2829-L2861)

#### GET /cookies/{cid}/auto-confirm - 获取自动确认设置
获取指定账号的自动确认发货设置。

**HTTP方法**: `GET`  
**URL路径**: `/cookies/{cid}/auto-confirm`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "auto_confirm": true,
  "message": "自动确认发货当前开启"
}
```

**状态码**:
- `200 OK`: 成功获取设置
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/cookies/account1/auto-confirm" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}/auto-confirm`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  console.log('自动确认设置:', data.auto_confirm);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2863-L2887)

### /cookies/{cid}/pause-duration - 自动回复暂停时间
管理账号的自动回复暂停时间，控制在特定时间段内暂停自动回复。

#### PUT /cookies/{cid}/pause-duration - 更新暂停时间
更新指定账号的自动回复暂停时间。

**HTTP方法**: `PUT`  
**URL路径**: `/cookies/{cid}/pause-duration`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "pause_duration": 30
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `pause_duration` | integer | 是 | 暂停时间（分钟），0-60 |

**响应格式**:
```json
{
  "message": "暂停时间更新成功",
  "pause_duration": 30
}
```

**状态码**:
- `200 OK`: 暂停时间更新成功
- `400 Bad Request`: 暂停时间超出范围
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/cookies/account1/pause-duration" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"pause_duration": 30}'
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}/pause-duration`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({ pause_duration: 30 })
})
.then(response => response.json())
.then(data => {
  alert('暂停时间更新成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2948-L2979)

#### GET /cookies/{cid}/pause-duration - 获取暂停时间
获取指定账号的自动回复暂停时间。

**HTTP方法**: `GET`  
**URL路径**: `/cookies/{cid}/pause-duration`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "pause_duration": 30,
  "message": "获取暂停时间成功"
}
```

**状态码**:
- `200 OK`: 成功获取暂停时间
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/cookies/account1/pause-duration" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/cookies/${accountId}/pause-duration`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  console.log('暂停时间:', data.pause_duration, '分钟');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2982-L3005)

## 消息回复配置接口
消息回复配置接口允许用户为每个闲鱼账号设置关键词回复规则，包括通用关键词、商品专用关键词和默认回复。

### /keywords/{cid} - 关键词管理
管理指定账号的关键词回复规则。

#### GET /keywords/{cid} - 获取关键词列表
获取指定账号的所有关键词回复规则。

**HTTP方法**: `GET`  
**URL路径**: `/keywords/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
[
  {
    "keyword": "string",
    "reply": "string",
    "item_id": "string",
    "type": "string"
  }
]
```

**状态码**:
- `200 OK`: 成功获取关键词列表
- `403 Forbidden`: 无权限访问该账号

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/keywords/account1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/keywords/${accountId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(keywords => {
  console.log('关键词列表:', keywords);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3017-L3043)

#### POST /keywords/{cid} - 更新关键词列表
更新指定账号的关键词回复规则。

**HTTP方法**: `POST`  
**URL路径**: `/keywords/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "keywords": {
    "关键词1": "回复1",
    "关键词2": "回复2"
  }
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `keywords` | object | 是 | 关键词到回复的映射 |

**响应格式**:
```json
{
  "msg": "updated",
  "count": 2
}
```

**状态码**:
- `200 OK`: 关键词更新成功
- `403 Forbidden`: 无权限操作该账号
- `400 Bad Request`: 更新失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/keywords/account1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"keywords": {"你好": "您好！", "价格": "99元"}}'
```

**JavaScript调用示例**:
```javascript
fetch(`/keywords/${accountId}`, {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    keywords: {
      '你好': '您好！',
      '价格': '99元'
    }
  })
})
.then(response => response.json())
.then(data => {
  alert(`关键词更新成功，共${data.count}条`);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3077-L3097)

### /keywords-with-item-id/{cid} - 商品专用关键词
管理指定账号的商品专用关键词，为特定商品设置专门的回复规则。

#### GET /keywords-with-item-id/{cid} - 获取商品专用关键词
获取包含商品ID的关键词列表。

**HTTP方法**: `GET`  
**URL路径**: `/keywords-with-item-id/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
[
  {
    "keyword": "string",
    "reply": "string",
    "item_id": "string",
    "type": "string",
    "image_url": "string"
  }
]
```

**状态码**:
- `200 OK`: 成功获取商品专用关键词
- `403 Forbidden`: 无权限访问该账号

**curl command示例**:
```bash
curl -X GET "http://localhost:8080/keywords-with-item-id/account1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/keywords-with-item-id/${accountId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(keywords => {
  console.log('商品专用关键词:', keywords);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3046-L3074)

#### POST /keywords-with-item-id/{cid} - 更新商品专用关键词
更新包含商品ID的关键词列表。

**HTTP方法**: `POST`  
**URL路径**: `/keywords-with-item-id/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "keywords": [
    {
      "keyword": "string",
      "reply": "string",
      "item_id": "string"
    }
  ]
}
```

**响应格式**:
```json
{
  "msg": "updated",
  "count": 1
}
```

**状态码**:
- `200 OK`: 更新成功
- `400 Bad Request`: 数据格式错误或关键词冲突
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/keywords-with-item-id/account1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "keywords": [
      {"keyword": "优惠", "reply": "现在有优惠活动", "item_id": "123456"}
    ]
  }'
```

**JavaScript调用示例**:
```javascript
fetch(`/keywords-with-item-id/${accountId}`, {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    keywords: [
      {
        keyword: '优惠',
        reply: '现在有优惠活动',
        item_id: '123456'
      }
    ]
  })
})
.then(response => response.json())
.then(data => {
  alert('商品专用关键词更新成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3099-L3182)

### /default-replies/{cid} - 默认回复设置
管理指定账号的默认回复设置，当没有匹配的关键词时使用默认回复。

#### GET /default-replies/{cid} - 获取默认回复
获取指定账号的默认回复设置。

**HTTP方法**: `GET`  
**URL路径**: `/default-replies/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "enabled": true,
  "reply_content": "string",
  "reply_once": false
}
```

**状态码**:
- `200 OK`: 成功获取默认回复设置

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/default-replies/account1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/default-replies/${accountId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(settings => {
  console.log('默认回复设置:', settings);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2361-L2378)

#### PUT /default-replies/{cid} - 更新默认回复
更新指定账号的默认回复设置。

**HTTP方法**: `PUT`  
**URL路径**: `/default-replies/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "enabled": true,
  "reply_content": "string",
  "reply_once": false
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `enabled` | boolean | 是 | 是否启用默认回复 |
| `reply_content` | string | 否 | 默认回复内容 |
| `reply_once` | boolean | 否 | 是否只回复一次 |

**响应格式**:
```json
{
  "msg": "default reply updated",
  "enabled": true,
  "reply_once": false
}
```

**状态码**:
- `200 OK`: 设置更新成功
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/default-replies/account1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "enabled": true,
    "reply_content": "亲爱的{send_user_name}，您好！",
    "reply_once": true
  }'
```

**JavaScript调用示例**:
```javascript
fetch(`/default-replies/${accountId}`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    enabled: true,
    reply_content: '亲爱的{send_user_name}，您好！',
    reply_once: true
  })
})
.then(response => response.json())
.then(data => {
  alert('默认回复设置已更新');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2384-L2399)

#### DELETE /default-replies/{cid} - 删除默认回复
删除指定账号的默认回复设置。

**HTTP方法**: `DELETE`  
**URL路径**: `/default-replies/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "msg": "default reply deleted"
}
```

**状态码**:
- `200 OK`: 删除成功
- `403 Forbidden`: 无权限操作该账号
- `400 Bad Request`: 删除失败

**curl命令示例**:
```bash
curl -X DELETE "http://localhost:8080/default-replies/account1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/default-replies/${accountId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  alert('默认回复已删除');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2421-L2438)

#### POST /default-replies/{cid}/clear-records - 清空回复记录
清空指定账号的默认回复记录，允许再次回复已回复过的对话。

**HTTP方法**: `POST`  
**URL路径**: `/default-replies/{cid}/clear-records`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "msg": "default reply records cleared"
}
```

**状态码**:
- `200 OK`: 记录清空成功
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/default-replies/account1/clear-records" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/default-replies/${accountId}/clear-records`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  alert('回复记录已清空');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2444-L2458)

### /keywords-export/{cid} 和 /keywords-import/{cid} - 关键词导入导出
提供关键词的Excel文件导入和导出功能，便于批量管理。

#### GET /keywords-export/{cid} - 导出关键词
将指定账号的关键词导出为Excel文件。

**HTTP方法**: `GET`  
**URL路径**: `/keywords-export/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**: Excel文件（application/vnd.openxmlformats-officedocument.spreadsheetml.sheet）

**状态码**:
- `200 OK`: 文件导出成功
- `500 Internal Server Error`: 导出失败

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/keywords-export/account1" \
  -H "Authorization: Bearer your-token" \
  -o keywords.xlsx
```

**JavaScript调用示例**:
```javascript
fetch(`/keywords-export/${accountId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `keywords_${accountId}.xlsx`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3225-L3305)

#### POST /keywords-import/{cid} - 导入关键词
从Excel文件导入关键词到指定账号。

**HTTP方法**: `POST`  
**URL路径**: `/keywords-import/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Form Data)**:
- `file`: Excel文件（.xlsx或.xls）

**响应格式**:
```json
{
  "msg": "导入成功",
  "total": 5,
  "added": 3,
  "updated": 2
}
```

**状态码**:
- `200 OK`: 导入成功
- `400 Bad Request`: 文件类型错误或数据无效
- `500 Internal Server Error`: 导入失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/keywords-import/account1" \
  -H "Authorization: Bearer your-token" \
  -F "file=@keywords.xlsx"
```

**JavaScript调用示例**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch(`/keywords-import/${accountId}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` },
  body: formData
})
.then(response => response.json())
.then(data => {
  alert(`导入成功，新增${data.added}条，更新${data.updated}条`);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3312-L3400)

### /keywords/{cid}/image - 图片关键词管理
管理图片类型的关键词回复，支持上传图片作为回复内容。

#### POST /keywords/{cid}/image - 添加图片关键词
为指定账号添加图片关键词。

**HTTP方法**: `POST`  
**URL路径**: `/keywords/{cid}/image`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Form Data)**:
- `keyword`: 关键词文本
- `item_id`: 商品ID（可选）
- `image`: 图片文件

**响应格式**:
```json
{
  "msg": "图片关键词添加成功",
  "keyword": "string",
  "image_url": "string",
  "item_id": "string"
}
```

**状态码**:
- `200 OK`: 图片关键词添加成功
- `400 Bad Request`: 参数无效或文件类型错误
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/keywords/account1/image" \
  -H "Authorization: Bearer your-token" \
  -F "keyword=图片" \
  -F "image=@image.jpg"
```

**JavaScript调用示例**:
```javascript
const formData = new FormData();
formData.append('keyword', '图片');
formData.append('image', imageFile);

fetch(`/keywords/${accountId}/image`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` },
  body: formData
})
.then(response => response.json())
.then(data => {
  alert('图片关键词添加成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3403-L3475)

#### DELETE /keywords/{cid}/{index} - 删除关键词
根据索引删除指定账号的关键词。

**HTTP方法**: `DELETE`  
**URL路径**: `/keywords/{cid}/{index}`

**路径参数**:
- `cid`: 账号ID
- `index`: 关键词索引

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "msg": "删除成功"
}
```

**状态码**:
- `200 OK`: 删除成功
- `400 Bad Request`: 索引无效
- `403 Forbidden`: 无权限操作该账号

**curl命令示例**:
```bash
curl -X DELETE "http://localhost:8080/keywords/account1/0" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/keywords/${accountId}/${index}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  alert('关键词删除成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3540-L3569)

## 自动发货设置接口
自动发货设置接口允许用户配置自动发货规则，包括卡券管理和发货规则设置。

### /cards - 卡券管理
管理用于自动发货的卡券，支持文本、数据、API和图片等多种类型。

#### GET /cards - 获取卡券列表
获取当前用户的所有卡券。

**HTTP方法**: `GET`  
**URL路径**: `/cards`

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
[
  {
    "id": 1,
    "name": "string",
    "type": "string",
    "text_content": "string",
    "image_url": "string",
    "enabled": true,
    "delay_seconds": 0,
    "is_multi_spec": false
  }
]
```

**状态码**:
- `200 OK`: 成功获取卡券列表

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/cards" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch('/cards', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(cards => {
  console.log('卡券列表:', cards);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3608-L3617)

#### POST /cards - 创建卡券
创建一个新的卡券。

**HTTP方法**: `POST`  
**URL路径**: `/cards`

**请求参数 (Body)**:
```json
{
  "name": "string",
  "type": "string",
  "text_content": "string",
  "image_url": "string",
  "delay_seconds": 0,
  "enabled": true,
  "is_multi_spec": false,
  "spec_name": "string",
  "spec_value": "string"
}
```

**响应格式**:
```json
{
  "id": 1,
  "message": "卡券创建成功"
}
```

**状态码**:
- `200 OK`: 卡券创建成功
- `500 Internal Server Error`: 创建失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/cards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "name": "优惠卡券",
    "type": "text",
    "text_content": "您的优惠码是: ABC123",
    "enabled": true
  }'
```

**JavaScript调用示例**:
```javascript
fetch('/cards', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    name: '优惠卡券',
    type: 'text',
    text_content: '您的优惠码是: ABC123',
    enabled: true
  })
})
.then(response => response.json())
.then(data => {
  alert('卡券创建成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3620-L3657)

#### GET /cards/{card_id} - 获取卡券详情
获取指定卡券的详细信息。

**HTTP方法**: `GET`  
**URL路径**: `/cards/{card_id}`

**路径参数**:
- `card_id`: 卡券ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**: 卡券详细信息对象

**状态码**:
- `200 OK`: 成功获取卡券详情
- `404 Not Found`: 卡券不存在

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/cards/1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/cards/${cardId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(card => {
  console.log('卡券详情:', card);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3659-L3672)

#### PUT /cards/{card_id} - 更新卡券
更新指定卡券的信息。

**HTTP方法**: `PUT`  
**URL路径**: `/cards/{card_id}`

**路径参数**:
- `card_id`: 卡券ID

**请求参数 (Body)**: 同创建卡券的请求体

**响应格式**:
```json
{
  "message": "卡券更新成功"
}
```

**状态码**:
- `200 OK`: 卡券更新成功
- `404 Not Found`: 卡券不存在
- `500 Internal Server Error`: 更新失败

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/cards/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "name": "更新的优惠卡券",
    "text_content": "您的优惠码是: XYZ789"
  }'
```

**JavaScript调用示例**:
```javascript
fetch(`/cards/${cardId}`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    name: '更新的优惠卡券',
    text_content: '您的优惠码是: XYZ789'
  })
})
.then(response => response.json())
.then(data => {
  alert('卡券更新成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3674-L3706)

#### PUT /cards/{card_id}/image - 更新带图片的卡券
更新卡券并上传新的图片。

**HTTP方法**: `PUT`  
**URL路径**: `/cards/{card_id}/image`

**路径参数**:
- `card_id`: 卡券ID

**请求参数 (Form Data)**:
- `image`: 新的图片文件
- 其他卡券字段

**响应格式**:
```json
{
  "message": "卡券更新成功",
  "image_url": "string"
}
```

**状态码**:
- `200 OK`: 更新成功
- `400 Bad Request`: 文件类型错误
- `404 Not Found`: 卡券不存在

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/cards/1/image" \
  -H "Authorization: Bearer your-token" \
  -F "image=@new_image.jpg" \
  -F "name=图片卡券"
```

**JavaScript调用示例**:
```javascript
const formData = new FormData();
formData.append('image', newImageFile);
formData.append('name', '图片卡券');

fetch(`/cards/${cardId}/image`, {
  method: 'PUT',
  headers: { 'Authorization': `Bearer ${authToken}` },
  body: formData
})
.then(response => response.json())
.then(data => {
  alert('带图片的卡券更新成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3708-L3775)

#### DELETE /cards/{card_id} - 删除卡券
删除指定的卡券。

**HTTP方法**: `DELETE`  
**URL路径**: `/cards/{card_id}`

**路径参数**:
- `card_id`: 要删除的卡券ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "message": "卡券删除成功"
}
```

**状态码**:
- `200 OK`: 卡券删除成功
- `404 Not Found`: 卡券不存在

**curl命令示例**:
```bash
curl -X DELETE "http://localhost:8080/cards/1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/cards/${cardId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  alert('卡券删除成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3848-L3859)

### /delivery-rules - 发货规则管理
管理自动发货规则，将关键词与卡券关联，实现智能自动发货。

#### GET /delivery-rules - 获取发货规则列表
获取当前用户的所有发货规则。

**HTTP方法**: `GET`  
**URL路径**: `/delivery-rules`

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
[
  {
    "id": 1,
    "keyword": "string",
    "card_id": 1,
    "delivery_count": 1,
    "enabled": true,
    "description": "string"
  }
]
```

**状态码**:
- `200 OK`: 成功获取发货规则列表

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/delivery-rules" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch('/delivery-rules', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(rules => {
  console.log('发货规则列表:', rules);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3779-L3787)

#### POST /delivery-rules - 创建发货规则
创建一个新的发货规则。

**HTTP方法**: `POST`  
**URL路径**: `/delivery-rules`

**请求参数 (Body)**:
```json
{
  "keyword": "string",
  "card_id": 1,
  "delivery_count": 1,
  "enabled": true,
  "description": "string"
}
```

**响应格式**:
```json
{
  "id": 1,
  "message": "发货规则创建成功"
}
```

**状态码**:
- `200 OK`: 发货规则创建成功
- `500 Internal Server Error`: 创建失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/delivery-rules" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "keyword": "购买",
    "card_id": 1,
    "delivery_count": 1,
    "enabled": true
  }'
```

**JavaScript调用示例**:
```javascript
fetch('/delivery-rules', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    keyword: '购买',
    card_id: 1,
    delivery_count: 1,
    enabled: true
  })
})
.then(response => response.json())
.then(data => {
  alert('发货规则创建成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3791-L3808)

#### GET /delivery-rules/{rule_id} - 获取发货规则详情
获取指定发货规则的详细信息。

**HTTP方法**: `GET`  
**URL路径**: `/delivery-rules/{rule_id}`

**路径参数**:
- `rule_id`: 发货规则ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**: 发货规则详细信息对象

**状态码**:
- `200 OK`: 成功获取发货规则详情
- `404 Not Found`: 发货规则不存在

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/delivery-rules/1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/delivery-rules/${ruleId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(rule => {
  console.log('发货规则详情:', rule);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3810-L3821)

#### PUT /delivery-rules/{rule_id} - 更新发货规则
更新指定的发货规则。

**HTTP方法**: `PUT`  
**URL路径**: `/delivery-rules/{rule_id}`

**路径参数**:
- `rule_id`: 发货规则ID

**请求参数 (Body)**: 同创建发货规则的请求体

**响应格式**:
```json
{
  "message": "发货规则更新成功"
}
```

**状态码**:
- `200 OK`: 发货规则更新成功
- `404 Not Found`: 发货规则不存在
- `500 Internal Server Error`: 更新失败

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/delivery-rules/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "keyword": "立即购买",
    "card_id": 1,
    "delivery_count": 2
  }'
```

**JavaScript调用示例**:
```javascript
fetch(`/delivery-rules/${ruleId}`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    keyword: '立即购买',
    card_id: 1,
    delivery_count: 2
  })
})
.then(response => response.json())
.then(data => {
  alert('发货规则更新成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3826-L3845)

#### DELETE /delivery-rules/{rule_id} - 删除发货规则
删除指定的发货规则。

**HTTP方法**: `DELETE`  
**URL路径**: `/delivery-rules/{rule_id}`

**路径参数**:
- `rule_id`: 要删除的发货规则ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "message": "发货规则删除成功"
}
```

**状态码**:
- `200 OK`: 发货规则删除成功
- `404 Not Found`: 发货规则不存在

**curl命令示例**:
```bash
curl -X DELETE "http://localhost:8080/delivery-rules/1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/delivery-rules/${ruleId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  alert('发货规则删除成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3862-L3873)

## 通知系统配置接口
通知系统配置接口允许用户设置消息通知渠道和规则，支持QQ、钉钉、飞书、Bark、邮件等多种通知方式。

### /notification-channels - 通知渠道管理
管理用户的消息通知渠道，包括创建、更新和删除。

#### GET /notification-channels - 获取通知渠道列表
获取当前用户的所有通知渠道。

**HTTP方法**: `GET`  
**URL路径**: `/notification-channels`

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
[
  {
    "id": 1,
    "name": "string",
    "type": "string",
    "config": "string",
    "enabled": true
  }
]
```

**状态码**:
- `200 OK`: 成功获取通知渠道列表

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/notification-channels" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch('/notification-channels', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(channels => {
  console.log('通知渠道列表:', channels);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2466-L2475)

#### POST /notification-channels - 创建通知渠道
创建一个新的通知渠道。

**HTTP方法**: `POST`  
**URL路径**: `/notification-channels`

**请求参数 (Body)**:
```json
{
  "name": "string",
  "type": "string",
  "config": "string"
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 渠道名称 |
| `type` | string | 是 | 渠道类型（qq, dingtalk, feishu, bark, email等） |
| `config` | string | 是 | 渠道配置（JSON字符串） |

**响应格式**:
```json
{
  "msg": "notification channel created",
  "id": 1
}
```

**状态码**:
- `200 OK`: 通知渠道创建成功
- `400 Bad Request`: 参数无效

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/notification-channels" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "name": "我的QQ",
    "type": "qq",
    "config": "{\"qq_number\": \"123456789\"}"
  }'
```

**JavaScript调用示例**:
```javascript
fetch('/notification-channels', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    name: '我的QQ',
    type: 'qq',
    config: JSON.stringify({ qq_number: '123456789' })
  })
})
.then(response => response.json())
.then(data => {
  alert('通知渠道创建成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2477-L2492)

#### GET /notification-channels/{channel_id} - 获取通知渠道详情
获取指定通知渠道的详细信息。

**HTTP方法**: `GET`  
**URL路径**: `/notification-channels/{channel_id}`

**路径参数**:
- `channel_id`: 渠道ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**: 通知渠道详细信息对象

**状态码**:
- `200 OK`: 成功获取通知渠道详情
- `404 Not Found`: 通知渠道不存在

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/notification-channels/1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/notification-channels/${channelId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(channel => {
  console.log('通知渠道详情:', channel);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2494-L2507)

#### PUT /notification-channels/{channel_id} - 更新通知渠道
更新指定的通知渠道。

**HTTP方法**: `PUT`  
**URL路径**: `/notification-channels/{channel_id}`

**路径参数**:
- `channel_id`: 渠道ID

**请求参数 (Body)**:
```json
{
  "name": "string",
  "config": "string",
  "enabled": true
}
```

**响应格式**:
```json
{
  "msg": "notification channel updated"
}
```

**状态码**:
- `200 OK`: 通知渠道更新成功
- `404 Not Found`: 通知渠道不存在

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/notification-channels/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "name": "更新的QQ",
    "config": "{\"qq_number\": \"987654321\"}",
    "enabled": true
  }'
```

**JavaScript调用示例**:
```javascript
fetch(`/notification-channels/${channelId}`, {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    name: '更新的QQ',
    config: JSON.stringify({ qq_number: '987654321' }),
    enabled: true
  })
})
.then(response => response.json())
.then(data => {
  alert('通知渠道更新成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2509-L2528)

#### DELETE /notification-channels/{channel_id} - 删除通知渠道
删除指定的通知渠道。

**HTTP方法**: `DELETE`  
**URL路径**: `/notification-channels/{channel_id}`

**路径参数**:
- `channel_id`: 要删除的渠道ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "msg": "notification channel deleted"
}
```

**状态码**:
- `200 OK`: 通知渠道删除成功
- `404 Not Found`: 通知渠道不存在

**curl命令示例**:
```bash
curl -X DELETE "http://localhost:8080/notification-channels/1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/notification-channels/${channelId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  alert('通知渠道删除成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2530-L2543)

### /message-notifications - 消息通知配置
管理账号的消息通知规则，控制哪些消息触发通知。

#### GET /message-notifications - 获取所有消息通知配置
获取当前用户所有账号的消息通知配置。

**HTTP方法**: `GET`  
**URL路径**: `/message-notifications`

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "account1": [
    {
      "id": 1,
      "channel_id": 1,
      "enabled": true
    }
  ]
}
```

**状态码**:
- `200 OK`: 成功获取消息通知配置

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/message-notifications" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch('/message-notifications', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(notifications => {
  console.log('消息通知配置:', notifications);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2548-L2563)

#### GET /message-notifications/{cid} - 获取账号通知配置
获取指定账号的消息通知配置。

**HTTP方法**: `GET`  
**URL路径**: `/message-notifications/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
[
  {
    "id": 1,
    "channel_id": 1,
    "enabled": true
  }
]
```

**状态码**:
- `200 OK`: 成功获取账号通知配置
- `403 Forbidden`: 无权限访问该账号

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/message-notifications/account1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/message-notifications/${accountId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(notifications => {
  console.log('账号通知配置:', notifications);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2565-L2582)

#### POST /message-notifications/{cid} - 设置消息通知
设置指定账号的消息通知。

**HTTP方法**: `POST`  
**URL路径**: `/message-notifications/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Body)**:
```json
{
  "channel_id": 1,
  "enabled": true
}
```

**响应格式**:
```json
{
  "msg": "message notification set"
}
```

**状态码**:
- `200 OK`: 消息通知设置成功
- `403 Forbidden`: 无权限操作该账号
- `404 Not Found`: 通知渠道不存在

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/message-notifications/account1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"channel_id": 1, "enabled": true}'
```

**JavaScript调用示例**:
```javascript
fetch(`/message-notifications/${accountId}`, {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    channel_id: 1,
    enabled: true
  })
})
.then(response => response.json())
.then(data => {
  alert('消息通知设置成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2584-L2610)

#### DELETE /message-notifications/account/{cid} - 删除账号通知配置
删除指定账号的所有消息通知配置。

**HTTP方法**: `DELETE`  
**URL路径**: `/message-notifications/account/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "msg": "account notifications deleted"
}
```

**状态码**:
- `200 OK`: 账号通知配置删除成功
- `404 Not Found`: 账号通知配置不存在

**curl命令示例**:
```bash
curl -X DELETE "http://localhost:8080/message-notifications/account/account1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/message-notifications/account/${accountId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  alert('账号通知配置已删除');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2612-L2625)

#### DELETE /message-notifications/{notification_id} - 删除消息通知
删除指定的消息通知配置。

**HTTP方法**: `DELETE`  
**URL路径**: `/message-notifications/{notification_id}`

**路径参数**:
- `notification_id`: 通知配置ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "msg": "message notification deleted"
}
```

**状态码**:
- `200 OK`: 消息通知删除成功
- `404 Not Found`: 通知配置不存在

**curl命令示例**:
```bash
curl -X DELETE "http://localhost:8080/message-notifications/1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/message-notifications/${notificationId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  alert('消息通知已删除');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2628-L2642)

## 系统设置接口
系统设置接口允许管理员管理全局系统设置，包括注册开关、登录信息显示等。

### /system-settings - 系统设置管理
管理全局系统设置，仅管理员有权限访问。

#### GET /system-settings - 获取系统设置
获取所有系统设置（排除敏感信息）。

**HTTP方法**: `GET`  
**URL路径**: `/system-settings`

**请求参数 (Header)**:
- `Authorization`: Bearer Token（管理员）

**响应格式**:
```json
{
  "registration_enabled": "true",
  "show_default_login_info": "true"
}
```

**状态码**:
- `200 OK`: 成功获取系统设置

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/system-settings" \
  -H "Authorization: Bearer admin-token"
```

**JavaScript调用示例**:
```javascript
fetch('/system-settings', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})
.then(response => response.json())
.then(settings => {
  console.log('系统设置:', settings);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2646-L2658)

#### PUT /system-settings/{key} - 更新系统设置
更新指定的系统设置。

**HTTP方法**: `PUT`  
**URL路径**: `/system-settings/{key}`

**路径参数**:
- `key`: 设置项键名

**请求参数 (Body)**:
```json
{
  "value": "string",
  "description": "string"
}
```

**响应格式**:
```json
{
  "msg": "system setting updated"
}
```

**状态码**:
- `200 OK`: 系统设置更新成功
- `400 Bad Request`: 不能直接修改密码哈希

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/system-settings/registration_enabled" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{"value": "false", "description": "关闭用户注册"}'
```

**JavaScript调用示例**:
```javascript
fetch('/system-settings/registration_enabled', {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({
    value: 'false',
    description: '关闭用户注册'
  })
})
.then(response => response.json())
.then(data => {
  alert('系统设置更新成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2663-L2681)

### /registration-status - 注册状态
获取用户注册功能的开关状态，此接口无需认证。

**HTTP方法**: `GET`  
**URL路径**: `/registration-status`

**响应格式**:
```json
{
  "enabled": true,
  "message": "注册功能已开启"
}
```

**状态码**:
- `200 OK`: 成功获取注册状态

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/registration-status"
```

**JavaScript调用示例**:
```javascript
fetch('/registration-status')
.then(response => response.json())
.then(data => {
  if (data.enabled) {
    console.log('注册功能已开启');
  } else {
    console.log('注册功能已关闭');
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2685-L2710)

### /login-info-status - 登录信息显示状态
获取默认登录信息的显示状态，此接口无需认证。

**HTTP方法**: `GET`  
**URL路径**: `/login-info-status`

**响应格式**:
```json
{
  "enabled": true
}
```

**状态码**:
- `200 OK`: 成功获取登录信息显示状态

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/login-info-status"
```

**JavaScript调用示例**:
```javascript
fetch('/login-info-status')
.then(response => response.json())
.then(data => {
  if (data.enabled) {
    console.log('显示默认登录信息');
  }
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2712-L2731)

### /registration-settings - 更新注册设置
更新用户注册功能的开关设置，仅管理员有权限。

**HTTP方法**: `PUT`  
**URL路径**: `/registration-settings`

**请求参数 (Body)**:
```json
{
  "enabled": true
}
```

**响应格式**:
```json
{
  "success": true,
  "enabled": true,
  "message": "注册功能已开启"
}
```

**状态码**:
- `200 OK`: 注册设置更新成功
- `403 Forbidden`: 权限不足

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/registration-settings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{"enabled": false}'
```

**JavaScript调用示例**:
```javascript
fetch('/registration-settings', {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({ enabled: false })
})
.then(response => response.json())
.then(data => {
  alert(data.message);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2741-L2766)

### /login-info-settings - 更新登录信息显示设置
更新默认登录信息的显示设置，仅管理员有权限。

**HTTP方法**: `PUT`  
**URL路径**: `/login-info-settings`

**请求参数 (Body)**:
```json
{
  "enabled": true
}
```

**响应格式**:
```json
{
  "success": true,
  "enabled": true,
  "message": "默认登录信息显示已开启"
}
```

**状态码**:
- `200 OK`: 登录信息显示设置更新成功
- `403 Forbidden`: 权限不足

**curl命令示例**:
```bash
curl -X PUT "http://localhost:8080/login-info-settings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{"enabled": true}'
```

**JavaScript调用示例**:
```javascript
fetch('/login-info-settings', {
  method: 'PUT',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({ enabled: true })
})
.then(response => response.json())
.then(data => {
  alert(data.message);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L2767-L2791)

## 文件管理接口
文件管理接口提供图片上传和管理功能，支持将图片用于关键词回复和卡券。

### /upload-image - 上传图片
上传图片文件，用于关键词回复或卡券。

**HTTP方法**: `POST`  
**URL路径**: `/upload-image`

**请求参数 (Form Data)**:
- `image`: 图片文件

**响应格式**:
```json
{
  "message": "图片上传成功",
  "image_url": "string"
}
```

**状态码**:
- `200 OK`: 图片上传成功
- `400 Bad Request`: 文件类型错误
- `500 Internal Server Error`: 上传失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/upload-image" \
  -H "Authorization: Bearer your-token" \
  -F "image=@photo.jpg"
```

**JavaScript调用示例**:
```javascript
const formData = new FormData();
formData.append('image', imageFile);

fetch('/upload-image', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` },
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('图片上传成功:', data.image_url);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3483-L3519)

## 商品管理接口
商品管理接口提供商品信息的获取和管理功能，支持商品搜索和信息查看。

### /items/{cid} - 获取商品列表
获取指定账号的商品列表。

**HTTP方法**: `GET`  
**URL路径**: `/items/{cid}`

**路径参数**:
- `cid`: 账号ID

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "items": [
    {
      "item_id": "string",
      "item_title": "string",
      "item_price": "string",
      "created_at": "string"
    }
  ],
  "count": 1
}
```

**状态码**:
- `200 OK`: 成功获取商品列表
- `403 Forbidden`: 无权限访问该账号
- `500 Internal Server Error`: 获取失败

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/items/account1" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch(`/items/${accountId}`, {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  console.log('商品列表:', data.items);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3184-L3223)

### /items - 获取所有商品信息
获取当前用户的所有商品信息。

**HTTP方法**: `GET`  
**URL路径**: `/items`

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**:
```json
{
  "items": [
    {
      "item_id": "string",
      "item_title": "string",
      "item_price": "string",
      "created_at": "string",
      "cookie_id": "string"
    }
  ]
}
```

**状态码**:
- `200 OK`: 成功获取所有商品信息

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/items" \
  -H "Authorization: Bearer your-token"
```

**JavaScript调用示例**:
```javascript
fetch('/items', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.json())
.then(data => {
  console.log('所有商品:', data.items);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3961-L3977)

### /items/search - 搜索商品
搜索闲鱼商品，支持分页。

**HTTP方法**: `POST`  
**URL路径**: `/items/search`

**请求参数 (Body)**:
```json
{
  "keyword": "string",
  "page": 1,
  "page_size": 20
}
```

**响应格式**:
```json
{
  "success": true,
  "total": 100,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "item_id": "string",
      "title": "string",
      "price": "string",
      "image_url": "string",
      "location": "string",
      "user_nick": "string",
      "wants_count": 0
    }
  ]
}
```

**状态码**:
- `200 OK`: 搜索成功
- `500 Internal Server Error`: 搜索失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/items/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"keyword": "手机", "page": 1, "page_size": 10}'
```

**JavaScript调用示例**:
```javascript
fetch('/items/search', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    keyword: '手机',
    page: 1,
    page_size: 10
  })
})
.then(response => response.json())
.then(data => {
  console.log('搜索结果:', data.items);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3991-L4140)

## 卡券与发货规则接口
提供卡券和发货规则的批量操作接口。

### /cards 和 /delivery-rules 批量操作
通过GET和POST方法实现卡券和发货规则的批量获取和创建。

**Section sources**
- [reply_server.py](file://reply_server.py#L3608-L3873)

## 备份与恢复接口
提供系统数据的备份和恢复功能，确保数据安全。

### /backup/export - 导出备份
导出用户数据备份。

**HTTP方法**: `GET`  
**URL路径**: `/backup/export`

**请求参数 (Header)**:
- `Authorization`: Bearer Token

**响应格式**: JSON文件（application/json）

**状态码**:
- `200 OK`: 备份导出成功
- `500 Internal Server Error`: 导出失败

**curl命令示例**:
```bash
curl -X GET "http://localhost:8080/backup/export" \
  -H "Authorization: Bearer your-token" \
  -o backup.json
```

**JavaScript调用示例**:
```javascript
fetch('/backup/export', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'backup.json';
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3879-L3902)

### /backup/import - 导入备份
从文件导入用户数据备份。

**HTTP方法**: `POST`  
**URL路径**: `/backup/import`

**请求参数 (Form Data)**:
- `file`: JSON备份文件

**响应格式**:
```json
{
  "message": "备份导入成功"
}
```

**状态码**:
- `200 OK`: 备份导入成功
- `400 Bad Request`: 文件格式无效
- `500 Internal Server Error`: 导入失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/backup/import" \
  -H "Authorization: Bearer your-token" \
  -F "file=@backup.json"
```

**JavaScript调用示例**:
```javascript
const formData = new FormData();
formData.append('file', backupFile);

fetch('/backup/import', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` },
  body: formData
})
.then(response => response.json())
.then(data => {
  alert('备份导入成功');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3905-L3940)

### /system/reload-cache - 重新加载缓存
手动刷新系统缓存，同步数据库变更。

**HTTP方法**: `POST`  
**URL路径**: `/system/reload-cache`

**请求参数 (Header)**:
- `Authorization`: Bearer Token（管理员）

**响应格式**:
```json
{
  "message": "系统缓存已刷新",
  "success": true
}
```

**状态码**:
- `200 OK`: 缓存刷新成功
- `500 Internal Server Error`: 刷新失败

**curl命令示例**:
```bash
curl -X POST "http://localhost:8080/system/reload-cache" \
  -H "Authorization: Bearer admin-token"
```

**JavaScript调用示例**:
```javascript
fetch('/system/reload-cache', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${adminToken}` }
})
.then(response => response.json())
.then(data => {
  alert('系统缓存已刷新');
});
```

**Section sources**
- [reply_server.py](file://reply_server.py#L3942-L3957)

## 错误处理与状态码
本系统遵循标准的HTTP状态码规范，提供清晰的错误信息和处理策略。

### 常见状态码含义
| 状态码 | 含义 | 说明 |
|--------|------|------|
| `200 OK` | 成功 | 请求成功处理 |
| `400 Bad Request` | 错误请求 | 请求参数无效或格式错误 |
| `401 Unauthorized` | 未授权 | Token无效或缺失 |
| `403 Forbidden` | 禁止访问 | 用户无权限操作该资源 |
| `404 Not Found` | 未找到 | 请求的资源不存在 |
| `422 Unprocessable Entity` | 无法处理的实体 | 请求格式正确但语义错误 |
| `500 Internal Server Error` | 内部服务器错误 | 服务器处理请求时发生错误 |

### 错误响应格式
所有错误响应均采用统一的JSON格式：
```json
{
  "detail": "错误详细信息"
}
```

### 错误处理策略
1. **客户端验证**：在发送请求前，客户端应验证所有参数的有效性，避免不必要的服务器请求。
2. **Token管理**：客户端应妥善管理Token，处理Token过期情况，引导用户重新登录。
3. **重试机制**：对于临时性错误（如500），客户端可实现指数退避重试机制。
4. **用户友好提示**：将技术性错误信息转换为用户友好的提示，提升用户体验。

**Section sources**
- [reply_server.py](file://reply_server.py#L54-L219)
- [reply_server.py](file://reply_server.py#L330-L357)