# # 创建
# ## 字面量
# users = ["张三", "李四", "王五"]
#
# ## 空列表
# empty = []
# empty2 = list()
#
# ## 从其他可迭代对象转换
# chars = list("abc")          # ['a', 'b', 'c']
# nums = list(range(5))        # [0, 1, 2, 3, 4]
#
# ## 重复
# zeros = [0] * 3              # [0, 0, 0]
#
# ## 推导式（最常用）
# squares = [x * x for x in range(5)]        # [0, 1, 4, 9, 16]
# evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]
#
# # print(users)
#
#
# # 增
# a: list[int] = [1, 2, 3]
#
# a.append(4)          # [1, 2, 3, 4]        尾部加一个
# a.extend([5, 6])     # [1, 2, 3, 4, 5, 6]  尾部加一批（等价 a += [5, 6]）
# a.insert(0, 0)       # [0, 1, 2, 3, 4, 5, 6]  在索引 0 插入
#
# ## append vs extend 的区别
# b: list[object] = [1]
# b.append([2, 3])     # [1, [2, 3]]   把整个 list 当一个元素
# c: list[int] = [1]
# c.extend([2, 3])     # [1, 2, 3]     把元素逐个加入

# # 删
#
# a = [1, 2, 3, 4, 5]
#
# a.pop()       # 删最后一个，返回 5      → a = [1, 2, 3, 4]
# a.pop(0)      # 删索引 0，返回 1        → a = [2, 3, 4]
# a.remove(3)   # 删第一个值为 3 的元素   → a = [2, 4]
# del a[0]      # 删索引 0                → a = [4]
# a.clear()     # 清空                    → a = []

# # 查 / 改
#
# a = [10, 20, 30, 40, 50]
#
# a[0]         # 10
# a[-1]        # 50     负索引，倒数第一个
# a[1:3]       # [20, 30]     切片，左闭右开
# a[:2]        # [10, 20]
# a[2:]        # [30, 40, 50]
# a[::-1]      # [50, 40, 30, 20, 10]   反转
# a[::2]       # [10, 30, 50]           步长 2
#
# a[0] = 100   # 改索引 0 → [100, 20, 30, 40, 50]
#
# 20 in a      # True      判断存在
# a.index(30)  # 2         找索引，找不到报 ValueError
# a.count(20)  # 1         计数
# len(a)       # 5
#
# # 排序 / 反转 / 复制
#
# a = [3, 1, 2]
#
# a.sort()                  # 原地排序 → [1, 2, 3]
# a.sort(reverse=True)      # 降序 → [3, 2, 1]
# sorted(a)                 # 返回新 list，不改原 list
# a.reverse()               # 原地反转
#
# # 按 key 排序（最常用）
# users = [{"name": "张三", "age": 30}, {"name": "李四", "age": 20}]
# users.sort(key=lambda u: u["age"])     # 按年龄升序
# sorted(users, key=lambda u: u["age"], reverse=True)   # 降序，返回新 list
# # sort vs sorted：sort 原地改、返回 None；sorted 返回新 list、不改原 list。a = a.sort() 是经典错误，a 会变成 None。


# # test
# a = [1, 3, 4, 7, 5]
# a.append(10)
# a.extend([11, 12, 13, 14, 15])
# a.pop()
# print(a)
# a.insert(1, 6)
# a.insert(6, 2)
# b = a.sort() # sort排序方法会将排序后的结果返回给自身，而sorted
# c = sorted(a)
#
# print('a:', a, 'b:', b, 'c:', c)

# # test1 字典
# user = { 'name': '张三', 'user_id': '001', 'age': 21 }
# # 空字典的两种形式
# user1 = {}
# user2 = dict()
# # 从键值对构造
# user3 = dict(uid = 1, name = '张三') # 键值对必须是合法标识符
# user4 = dict([("uid", '001'), ("gender", 'male')]) # 从列表的元组构造
# print('user3:', user3,'\n', 'user4:', user4)
#
# # 推导式
# squares = {x: x * x for x in range(5)}
# print(squares)
#
# # 从两个列表中获取 zip（zip的作用？）
# """
# zip是python内置的函数：拉链函数————将多个可迭代对象按位置一一配对，可使用*操作符进行“解压操作”，其中矩阵转置就是这个原理：
# matrix = [[1, 2, 3], [4, 5, 6]]
# list(zip(*matrix))
# => [(1, 4), (2, 5), (3, 6)]   ← 3 行 2 列，转成 2 行 3 列
# """
# keys = ['a', 'b', 'c', 'd']
# vals = [1, 2, 3, 4]
# d = dict(zip(keys, vals))
# print(d)
#
# # 字典增 / 改
# eDict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
# eDict['e'] = 5 # 增
# eDict['a'] = 100 # 改已有
#
# # 批量增改（不存在则新增，存在则修改）
# eDict.update({'e': 6, 'f': 7, 'g': 8})
# print(eDict)
# # setdefault：键不存在时设默认值，存在时返回已有值
# d = {}
# d.setdefault("count", 0)      # 返回 0，d = {'count': 0}
# d.setdefault("count", 99)     # 返回 0，不覆盖，d 不变
# d["count"] += 1               # 常见计数模式
#
# # 删 利用pop关键字进行删除操作
# f = {"a": 1, "b": 2, "c": 3}
# f.pop("a")              # 删并返回 1 → {'b': 2, 'c': 3}
# val = f.pop("x", "默认")       # 键不存在返回默认值，不报错
# del f["b"]              # 删 → {'c': 3}
# f.popitem()             # 删并返回最后一个键值对 (LIFO)
# f.clear()               # 清空
# # 注意：d.pop("x") 键不存在会报 KeyError，不确定时用 d.pop("x", None) 或先 if "x" in d:。
# print(val)
#
# # 查
# g = {"a": 1, "b": 2}
#
# g["a"]              # 1    键不存在报 KeyError
# g.get("a")          # 1
# g.get("x")          # None    键不存在返回 None，不报错
# g.get("x", 0)       # 0       指定默认值
#
# "a" in d            # True    判断键存在
# "x" not in d        # True
#
# len(g)              # 2
#
# # 视图（动态反映 dict 变化）
# g.keys()            # dict_keys(['a', 'b'])
# g.values()          # dict_values([1, 2])
# g.items()           # dict_items([('a', 1), ('b', 2)])
# list(g.keys())      # ['a', 'b']    转 list
#
# # 注意：d["x"] vs d.get("x")：前者键不存在抛 KeyError，后者返回 None。外部数据（JSON、请求参数）永远用 get，内部确定有键才用 []。
#
# # 遍历
# d = {"a": 1, "b": 2, "c": 3}
#
# # 只遍历键（默认）
# for k in d:
#     print(k)                 # a b c
#
# # 遍历键值对（最常用）
# for k, v in d.items():
#     print(k, v)              # a 1 / b 2 / c 3
#
# # 只遍历值
# for v in d.values():
#     print(v)                 # 1 2 3
#
# # 带索引
# for i, (k, v) in enumerate(d.items()):
#     print(i, k, v)           # 0 a 1 / 1 b 2 / 2 c 3
#
# # 注意： 别在遍历时改 dict 大小：for k in d: del d[k] 会报 RuntimeError。要删就先 list(d.items()) 或收集键再删。




# class Base:
#     def __init__(self):
#         self.__private = "private"
#
# b = Base()
# # print(b.__private)
# print(b._Base__private)
#
# from collections import Counter
#
# c = Counter()
# c['在职'] += 1
# c['在职'] += 1
# print(c)





# 对于dataclass中的field（与Pydantic中的Field完全不同）




