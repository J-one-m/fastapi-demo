# 数据库会话使用说明

本文档说明 `AsyncSession`（路由参数中的 `db`）的常用方法与状态流转，用于日常增删改查。

## 一、`db` 是什么

`db` 是一个数据库会话（`AsyncSession`），本质是 **Unit of Work（工作单元）**：

- 你把对象「登记」进会话
- 会话攒着变更，等到 `flush` 时才统一发 SQL
- 事务的提交 / 回滚**不在这里做**，由 `core/deps.py` 的 `get_db` 统一负责

```text
routers → core/deps.get_db → db/session.AsyncSessionLocal → SQLite
```

## 二、对象状态机

| 状态 | 触发时机 | 数据库里有吗 | 有 SQL 发出吗 |
| --- | --- | --- | --- |
| transient | `User(...)` 刚构造 | 没有 | 没有 |
| pending | `db.add(user)` | 没有 | **没有** |
| persistent | `flush()` 之后 | 有 | INSERT 已发 |
| deleted | `db.delete(obj)` | 有（待删） | DELETE 待发 |
| detached | session 关闭后 | 有 | 不会再有 |

**关键**：`add` 只排队，`flush` 才执行。

## 三、三个核心动作的分工

| 动作 | 作用 | 发 SQL |
| --- | --- | --- |
| `db.add(obj)` | 登记到会话的待插入集合 | 否 |
| `await db.flush()` | 让会话把变更同步到数据库 | 是 |
| `await db.commit()` | 提交事务（**只在 `get_db` 中调用**） | 是（内部先 flush） |

`flush` 可能发出多条、多种语句：

- 新增对象 → INSERT
- 修改过的对象 → UPDATE
- 被 delete 的对象 → DELETE

存在外键依赖时会自动排序，例如先 INSERT 父表再 INSERT 子表。

## 四、查询方法对比

| 方法 | 返回 | 适用场景 |
| --- | --- | --- |
| `await db.get(Model, pk)` | 对象 或 `None` | 已知主键，最简写（命中 identity map 时不发 SQL） |
| `await db.scalar(select(...))` | 单个值 / 对象 / `None` | 查一条、判空、取标量 |
| `await db.scalars(select(...))` | `ScalarResult` | 查多条对象，再 `.all()` |
| `await db.execute(select(...))` | 原始 `Result` | 多列、聚合、联表 |

示例：

```python
# 按主键
note = await db.get(Note, note_id)

# 条件查一条 / 判空
exists = await db.scalar(select(User).where(User.account_name == name))

# 查多条
rows = await db.scalars(select(Note).where(Note.owner_id == user.id))
notes = rows.all()

# 多列 / 聚合
rows = await db.execute(select(Note.id, Note.title))
```

## 五、增删改查速查

### 查（Read）

```python
note = await db.get(Note, note_id)
notes = (await db.scalars(select(Note).where(Note.owner_id == user.id))).all()
```

### 增（Create）

```python
note = Note(owner_id=user.id, title=req.title, content=req.content)
db.add(note)
await db.flush()          # 发 INSERT，拿到自增 id

# 批量
db.add_all([n1, n2])
await db.flush()
```

### 改（Update）

```python
# 单条：改属性 + flush，SQLAlchemy 只更新变化的字段
note.title = req.title
await db.flush()

# 批量：不加载对象，直接执行 UPDATE
from sqlalchemy import update
await db.execute(update(Note).where(Note.owner_id == user.id).values(is_archived=True))
```

### 删（Delete）

```python
# 单条
await db.delete(note)
await db.flush()

# 批量
from sqlalchemy import delete
await db.execute(delete(Note).where(Note.owner_id == user.id))
```

## 六、典型 CRUD 路由

```python
@router.post("", response_model=Resp[NoteOut])
async def create_note(req: NoteCreate, db: DbSession, user: CurrentUser):
    note = Note(owner_id=user.id, title=req.title, content=req.content)
    db.add(note)
    await db.flush()
    return Resp[NoteOut].success(data=NoteOut.model_validate(note))


@router.get("/{note_id}", response_model=Resp[NoteOut])
async def get_note(note_id: int, db: DbSession, user: CurrentUser):
    note = await db.get(Note, note_id)
    if note is None or note.owner_id != user.id:
        raise HTTPException(404)
    return Resp[NoteOut].success(data=NoteOut.model_validate(note))


@router.patch("/{note_id}", response_model=Resp[NoteOut])
async def update_note(note_id: int, req: NoteUpdate, db: DbSession, user: CurrentUser):
    note = await db.get(Note, note_id)
    if note is None or note.owner_id != user.id:
        raise HTTPException(404)
    note.title = req.title or note.title
    await db.flush()
    return Resp[NoteOut].success(data=NoteOut.model_validate(note))


@router.delete("/{note_id}", response_model=Resp[None])
async def delete_note(note_id: int, db: DbSession, user: CurrentUser):
    note = await db.get(Note, note_id)
    if note is None or note.owner_id != user.id:
        raise HTTPException(404)
    await db.delete(note)
    await db.flush()
    return Resp[None].success(msg="已删除")
```

## 七、必须遵守的三条规则

1. **路由和业务函数里不写 `commit()` / `rollback()`**
   事务边界统一在 `core/deps.py` 的 `get_db`。业务失败一律 `raise`，
   不要用 `return 错误响应` 代替异常——依赖会把它当成成功并提交已有写入。

2. **查、改、删都要校验归属**
   `owner_id` 不匹配返回 **404**（不用 403，避免暴露资源是否存在）。

3. **写操作后按需 `flush()`**
   需要自增主键或服务端默认值时立即 `flush`，其余交给依赖统一提交。

## 八、两个有用的特性

**1. identity map**

同一会话内，同一主键只存在一个对象实例：

```python
a = await db.get(User, 1)
b = await db.get(User, 1)
a is b      # True，第二次不再查库
```

**2. 延迟写**

```python
user.account_name = "改名"
# 此刻数据库毫无变化
await db.flush()      # 这时才发 UPDATE
```

## 九、查看真实 SQL

`db/session.py` 中引擎为 `echo=settings.DEBUG`，把 `.env` 的 `DEBUG` 设为 `true`，
`flush` 时控制台会打印实际执行的语句：

```sql
INSERT INTO users (account_name, account, gender, age, password, create_time, update_time)
VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
[generated in 0.00021s] ('南风', '', '保密', 0, '...')
```
