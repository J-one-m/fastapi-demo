# fastapi


## sqlite 数据库

### 如何快速查看数据

```powershell
    uvx litecli 数据库文件名(db结尾) 进入交互式SLQ提示符
    .tables === 查看所有表
    .schema 表名 === 查看表结构
    .exit 或者 .quite === 退出数据库
```
==补充：==
`uvx` 第一次会下载依赖（几百 KB，已缓存），之后启动是秒开。如果以后想要图形界面，再手动去官网下 DB Browser for SQLite 的安装包（这台机器没有`winget` ，只能手动装）。












