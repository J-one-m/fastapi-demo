# register.py用于注册路由、中间件、数据库等
from ast import parse
import pkgutil
import importlib
from fastapi import FastAPI, APIRouter


# ========== 路由动态注册 ==========
# 路由自动注册
# prefix：统一路由前缀，默认为 /api/v1
def auto_register_routers(app: FastAPI, package: str = "routers", prefix: str = "/api/v1")-> list[str]:
    """自动扫描并注册路由模块

    扫描 package 下所有模块，把名为 router 的 APIRouter 自动挂载到 app。
    
    约定：
    1. 每个路由模块必须导出 router: APIRouter；
    2. 模块内 prefix 只写资源段（如 /system_account），全局前缀由参数统一添加；
    3. 以 _ 开头的模块视为私有模块，直接跳过。

    ## importlib – 动态导入模块
    用途：在运行时按字符串名称导入 Python 模块或包。
    代码中的具体使用：
        - importlib.import_module(package)：导入整个包（例如 "routers"），返回包对象，以便后续获取其 __path__ 属性。
        - importlib.import_module(info.name)：导入包下的具体子模块（例如 "routers.system_account"），从而可以访问该模块中定义的 router 对象。
    ## pkgutil – 遍历包中的模块
    用途：提供工具函数来遍历包内的所有模块（包括子包），无需手动列出文件名。
    代码中的具体使用：
        - pkgutil.walk_packages(pkg.__path__, prefix=f"{package}.")：递归遍历包及其所有子包，逐个生成模块信息（ModuleInfo 对象），包含完整模块名（如 "routers.common.f_auth"）以及是否为包的标志 ispkg。
        - 遍历结果中 ispkg=True 的是子包本身，需要跳过；它的子模块会在后续递归中继续出现，从而支持按业务分组的路由目录。
    """
    # 通过字符串package（如 "routers"）导入包对象，后续利用其__path__属性来获取包所在的文件系统路径，供pkgutil扫描
    pkg = importlib.import_module(package)
    registered: list[str] = [] #创建一个空列表，存储所有成功注册的路由模块名称，供后续调试用

    for info in pkgutil.walk_packages(pkg.__path__, prefix=f"{package}."):
        # 子包本身不是路由模块，跳过（但它的子模块会被递归扫到）
        if info.ispkg:
            continue

        parts = info.name.split(".")[1:] #去掉顶层”routers“
        if any(p.startswith("_") for p in parts): # 如果模块名中包含以_开头的模块，跳过
            continue


        # 根据路径获取正确的模块名
        module_name = parts[-1]
        
        # 模块名需要f_开头的才进行自动注册
        if not module_name.startswith("f_"):
            continue

        module = importlib.import_module(info.name)
        """getattr(object, name[, default]) 是 Python 的内置函数，用于动态获取对象的属性。
            基本用法：
                参数：
                - object：要获取属性的对象（模块、类、实例等）。
                - name：要获取的属性名（字符串）。
                - default：可选参数，指定如果属性不存在时返回的默认值。
            返回值：
                - 如果属性存在，返回属性值；
                - 如果属性不存在，返回 default 参数的值（默认 None）。
            
            类似的函数还有：
                - hasattr(object, name)：检查对象是否有指定属性，其中name为要判断的属性名，返回值为布尔值。
                - setattr(object, name, value)：设置对象的属性值，其中name为要设置的属性名，value为要设置的属性值。
                - delattr(object, name)：删除对象的属性，其中name为要删除的属性名。
        """
        router = getattr(module, "router", None) #获取模块中的router属性，若没有则将其置为None，表明当前该模块不是路由模块，跳过

        if router is None:
            continue
        
        if not isinstance(router, APIRouter): # 验证router是否是APIRouter实例
            raise TypeError(f"{ info.name }.router 必须是APIRouter实例")

        # 挂载路由到应用
        app.include_router(router, prefix=prefix)
        # 记录成功注册的路由模块名称
        registered.append(info.name)
    #返回注册结果
    return registered



# 统一注册
def register_all(app: FastAPI)-> None:
    """统一注册所有路由、中间件、数据库等"""
    auto_register_routers(app)
    # 其他注册操作...
