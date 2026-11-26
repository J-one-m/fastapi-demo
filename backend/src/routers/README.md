# 路由分域说明

本文件用于界定各业务域的功能范围。新增接口前先在此对照，避免逻辑放错目录。

## 划分原则

**按「操作对象」分域，不按技术层次分。**

判断口诀：这个接口是在**证明我是谁**（auth），还是在**操作我的数据**（user / note）？

- 一个域 = 一个资源 / 聚合根
- 路由前缀 = 资源名（名词）
- 跨域共享的能力（依赖、安全、响应、分页）放 `core/`，不放进任何业务域
- 不提前搭空壳：目录里有真实接口时再建文件

---

## auth —— 认证明细

凡涉及「密码、token、凭证」的接口都归这里。

| 接口 | 说明 |
| --- | --- |
| `POST /auth/register` | 注册（返回 token，注册即登录） |
| `POST /auth/login` | 登录，签发 token |
| `POST /auth/logout` | 登出，使 token 失效 |
| `POST /auth/refresh` | 刷新 token |
| `POST /auth/change-password` | 修改密码（需校验旧密码，并使旧 token 失效） |

> 修改密码属于凭证操作，不是资料修改，因此归 auth 而非 user。

---

## user —— 用户资源本身

只处理「当前登录用户自己的资料」，不处理登录与凭证。

| 接口 | 说明 |
| --- | --- |
| `GET /users/me` | 获取当前登录用户资料 |
| `PATCH /users/me` | 修改昵称、性别、年龄、头像等 |
| `DELETE /users/me` | 注销账号 |
| `GET /users/me/settings` | 读取偏好设置（提醒方式等，后续） |
| `PUT /users/me/settings` | 更新偏好设置 |

> 统一用 `/me`，不使用 `/users/{id}`。当前用户只从 token 解析，
> 永远不接受前端传入的 user_id。

---

## note —— 记事本资源

| 接口 | 说明 |
| --- | --- |
| `POST /notes` | 新建笔记 |
| `GET /notes` | 列表（自动附加 owner_id 过滤） |
| `GET /notes/{id}` | 详情（归属不符返回 404） |
| `PATCH /notes/{id}` | 更新 |
| `DELETE /notes/{id}` | 删除 |

> 所有查询必须带 `owner_id` 条件；单条资源归属不符返回 404，
> 不返回 403，避免暴露资源是否存在。

---

## 边界争议点

| 问题 | 判断依据 | 当前结论 |
| --- | --- | --- |
| 计划提醒放哪 | 是否有独立生命周期（能单独增删查） | 附属属性留在 note；独立实体另建 reminder 域 |
| 标签（tag） | 是否需要独立的标签管理页 | 早期作为 note 的字段；需要筛选/管理时再拆 |
| 用户列表 `GET /users` | 是否存在管理员角色 | 个人应用不建 |

---

## 目录结构

```text
routers/
├── auth/
│   └── f_auth.py     # 注册、登录、登出、刷新、改密
├── user/
│   └── f_user.py     # /users/me 系列
├── note/
│   └── f_note.py     # /notes 系列
└── __init__.py
```

约定：

- 只有文件名以 `f_` 开头的模块会被自动注册为路由
- 每个路由模块必须导出 `router: APIRouter`
- 模块内 `prefix` 只写资源段（如 `/notes`），全局前缀 `/api/v1` 由注册器统一添加
- 各目录的 `__init__.py` 保持为空，仅作包标记

---

## 归属速查

| 操作 | 归域 |
| --- | --- |
| 注册 / 登录 / 登出 / 刷新 token / 改密码 | auth |
| 查看资料 / 改昵称 / 改偏好 / 注销账号 | user |
| 笔记增删改查 / 搜索 | note |
| 解析 token、获取当前用户 | `core/security.py` |
| 数据库会话依赖 | `core/deps.py` |
| 统一响应 / 分页 / 公共类型 | `core/` |
