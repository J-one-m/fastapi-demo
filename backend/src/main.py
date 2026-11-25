import uvicorn
import sys



def check_python_version(min_version: tuple[int, int] = (3, 12))-> None:
    if sys.version_info < min_version:
        sys.exit(f"需要Python {min_version[0]}.{min_version[1]}+, 当前 {sys.version.split()[0]}")



def main()-> None:
    check_python_version()
    uvicorn.run(
        "app.create_app:app",         #告诉uvicon去哪找FastAPI实例，main对应main.py，app对应文件里的app变量
        host="127.0.0.1",       #需要监听的网卡，当前值表示本机地址
        port=8000,              #定义端口号
        reload=False,           #是否启用热重载（即保存更改自动重启服务）（传对象时不能用reload）
        workers=1,              #工作进程数，默认1个
        access_log=True,        #是否打印访问日志，默认True
    )

# 此时main.py文件仅作为入口文件，不负责任何业务逻辑
if __name__ == "__main__":      #表示只有该文件被直接运行时才执行下面的代码，被别的文件通过import的方式导入时不执行
    main()