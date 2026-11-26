# FastAPI 后端约定（记事簿 / 多用户 / SQLite）

技术栈：FastAPI + SQLAlchemy 2.x 异步 + Pydantic v2 + SQLite(aiosqlite)

> 本文档是项目的长期约束，随项目复杂度提升逐步落地。
> 当前项目代码位于 `backend/src/`（src layout），模块从 `src` 为根解析。

## 一、两条硬约定

1. **路由只做三件事**：收参数 → 调 ORM 或业务函数 → 包装响应。不在路由里写多段业务编排。
2. **事务边界只有一处**：建 Session 的依赖函数负责 `commit / rollback / close`。路由和业务代码里**不写** `commit()`，失败一律 `raise`，不要 `return 错误响应` 代替异常。

### 为什么「失败必须 raise」

`get_db` 判断成功/失败的唯一依据是**有没有抛异常**，而不是返回值内容：

```
路由函数 return → 依赖 yield 后半段执行（commit）→ 发送响应
```


| 写法                       | 依赖的理解      | 结果                                |
| -------------------------- | --------------- | ----------------------------------- |
| `return Resp.error(...)`   | 正常返回 = 成功 | **commit**，之前 flush 的脏数据落库 |
| `raise HTTPException(...)` | 抛异常 = 失败   | rollback，转成错误响应              |

因此约定要求业务失败一律 `raise`，并且必须配套统一异常处理器（见第三节），否则前端收到的是 `{"detail": "..."}`，与 `Resp` 格式不一致。

## 二、依赖层参考实现

```python
# core/deps.py
from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import AsyncSessionLocal


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DbSession = Annotated[AsyncSession, Depends(get_db)]
```

```python
# 路由写法
from core.deps import DbSession


@router.post("/notes", response_model=Resp[NoteOut])
async def create_note(req: NoteCreate, db: DbSession, user: CurrentUser):
    note = Note(owner_id=user.id, title=req.title, content=req.content)
    db.add(note)
    await db.flush()          # 拿自增 id，事务未提交
    return Resp.success(data=NoteOut.model_validate(note))
```

要点：

- `flush()` 用于拿自增主键；`commit()` 由 `get_db` 统一执行。
- 同一请求内多处声明 `DbSession`，拿到的是同一个 Session（FastAPI 依赖缓存）。
- `AsyncSessionLocal` 必须保持 `expire_on_commit=False`。否则依赖 teardown 里 commit 之后对象会过期，后续访问 ORM 属性会触发异步懒加载，在已退出的上下文报 `MissingGreenlet`。
- Session 工厂只在 `db/session.py` 出现；路由层不出现 `AsyncSessionLocal`。

## 三、异常处理（必须配套）

```python
# core/exceptions.py 或 app/create_app.py 内
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from core.resp import Resp


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=Resp.error(errcode=exc.status_code, msg=exc.detail).model_dump(),
    )
```

约定「失败一律 raise」的前提是：raise 出去的异常要有统一出口，否则响应体格式会被破坏。

## 四、是否拆 service 层

**当前规模（记事簿 + SQLite + 单人维护）：不拆。**

推荐结构（够用即可，当前项目用 src layout）：

```text
backend/src/
├── main.py
├── core/{deps.py, resp.py, exceptions.py, security.py}
├── db/{session.py, base_model.py}
├── models/
├── schemas/
└── routers/
```

满足以下任一条件再抽 `services/`：

- 同一段逻辑要被路由 **和** 定时任务 / CLI / 消息消费复用；
- 一次操作写 3 张以上表且需要整体回滚；
- 相同逻辑在 3 个以上接口重复出现。

抽的时候只抽「业务函数」，签名用 `session: AsyncSession`，**不 import FastAPI 的 `Depends`**，由路由把注入的 session 传进去。

## 五、多用户安全底线（比分层更重要）

1. 所有业务表必须有 `owner_id`（外键 + 索引）。
2. 当前用户**只从 token 解析**，禁止信任前端传入的 `user_id`。
3. 所有查询都带 owner 条件：

```python
stmt = select(Note).where(Note.owner_id == user.id)
```

4. 单条资源校验归属，不匹配返回 **404**（不要返回 403，避免暴露资源是否存在）：

```python
note = await db.get(Note, note_id)
if note is None or note.owner_id != user.id:
    raise HTTPException(status_code=404)
```

5. 密码只存哈希（bcrypt/argon2），不返回任何密码字段。

## 六、SQLite 注意事项

- 异步驱动 `aiosqlite`；
- 启动时设置 `PRAGMA journal_mode=WAL`，提升多读单写体验；该 PRAGMA 必须**每个连接**设置一次，通常挂在 `engine.sync_engine` 的 `connect` 事件上，而不是建表时执行一次；
- 事务保持短：不要在事务里做耗时计算、文件 IO 或网络请求（`get_db` 会持有事务整个请求周期）；
- SQLite 是单写者，写操作频繁时考虑「写请求串行 + 读走缓存」；
- 后期若要换 MySQL/PostgreSQL，保持 ORM 写法规范即可平滑迁移，避免在代码里写 SQLite 方言 SQL。

## 七、自查清单

- [ ]  路由里没有 `commit()` / `rollback()`；
- [ ]  业务失败用 `raise`，没有「先 return 再继续」的分支；
- [ ]  每条查询都带 `owner_id` 过滤；
- [ ]  用户身份只来自 token，不接受前端传 uid；
- [ ]  越权访问返回 404；
- [ ]  已注册统一异常处理器，raise 后响应格式仍是 `Resp`；
- [ ]  Session 工厂保持 `expire_on_commit=False`；
- [ ]  没有为「以后可能用到」提前抽 service / 仓储层。

## 八、当前落地状态


| 约定项                     | 现状                                            | 待办                    |
| -------------------------- | ----------------------------------------------- | ----------------------- |
| 路由不写 commit / rollback | `routers/common/f_auth.py` 仍有 commit/rollback | 迁移到依赖后删除        |
| 失败一律 raise             | 仍用`return Resp.error(...)`                    | 改为 raise + 异常处理器 |
| 依赖负责 commit            | `db/session.py` 的 `get_db` 只 yield            | 补充 commit/rollback    |
| `DbSession` 依赖别名       | 尚未创建`core/deps.py`                          | 新建                    |
| service 层                 | 无（`src/servcies/` 为拼写错误的空目录）        | 暂缓，按条件触发        |
| owner_id / token           | 尚未实现（当前仅注册接口）                      | 多用户阶段实现          |

一句话原则：**先把事务边界和权限边界写对，分层等出现第二个调用方再补。**
