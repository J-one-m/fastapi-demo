import importlib
import pkgutil

# ===== 第一步：使用 pkgutil 遍历自定义包 mypackage =====
print("=== 使用 pkgutil 遍历 mypackage 包 ===")
import mypackage  # 先导入包，获取其 __path__


print('__path__：',mypackage.__name__,'\n')
for info in pkgutil.iter_modules(mypackage.__path__, prefix="mypackage."):
    # 跳过以 _ 开头的模块（私有模块）
    module_name = info.name.rsplit(".", 1)[-1]
    if module_name.startswith("_"):
        print(f"  跳过私有模块: {info.name}")
        continue
    print(f"  发现模块: {info.name} (是包? {info.ispkg})")

print("\n")

# ===== 第二步：使用 importlib 动态导入发现的模块 =====
print("=== 使用 importlib 动态导入并调用函数 ===")
# 手动指定要导入的模块（也可以用上面遍历的结果）
modules_to_import = ["mypackage.module_a", "mypackage.module_b"]

for mod_name in modules_to_import:
    mod = importlib.import_module(mod_name)
    print(f"  成功导入: {mod_name}")
    # 调用模块中的函数
    if hasattr(mod, "greet"):
        print(f"    -> greet('World') = {mod.greet('World')}")
    if hasattr(mod, "farewell"):
        print(f"    -> farewell('World') = {mod.farewell('World')}")
    # 访问模块中的常量
    if hasattr(mod, "PI"):
        print(f"    -> PI = {mod.PI}")
    if hasattr(mod, "E"):
        print(f"    -> E = {mod.E}")

print("\n")

# ===== 第三步：尝试导入私有模块（虽然它存在，但我们故意不跳过） =====
print("=== 尝试导入私有模块（不跳过） ===")
private_mod = importlib.import_module("mypackage._private")
print(f"  私有模块的 SECRET = {private_mod.SECRET}")