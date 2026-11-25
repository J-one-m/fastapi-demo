# # 列表
# list1 = [1, 2, 3, 4, 5]
#
# list1.append(6)
# print(list1)
# list1.remove(5)
# print(list1)
# list1.extend([7, 8, 9])
# print(list1)
# list1.insert(1, 10)
# print(list1)
# list1.pop(1)
# print(list1)
# print(list1.index(8))
# print(list1.count(8)) #count用于统计元素出现的次数
# list1.sort(reverse=True)
# print(list1)

# # 字典
# dict1 = {
#     'name': '张三',
#     'age': 28,
# }
# print(dict1.get('name')) #通过键名获取，也可以在获取时指定默认值，但是默认为None，如下：
# print(dict1.get('gender','male'))
# dict1.setdefault('id', '001') # 当键名不存在时设置默认值，若键名存在则不修改，而是返回原先存在的值
# print(dict1)
# dict1_pop = dict1.pop('idd', 'id不存在') # 删除并返回删掉的键名对应的值，建议指定默认值，否则删除不存在的键以及对应的值会报错
# print(dict1_pop)
# dict_pop_item = dict1.popitem() # 删除最后一个键值对，以元组的形式返回：(k, v)
# print(dict_pop_item)
# dict_update = dict1.update({'address':'武汉'}) # 批量增改，其中的参数必须是一个可迭代对象，且是以键值对的形式存在（长度为二）
# ## 字典视图操作，返回
# print( dict1.keys(),'\n',dict1.values(),'\n',dict1.items())  # 会返回三个视图类的实例
# print(dict1)
#
# # 元组
# ##元组的创建的方式有以下5种方式（倒不如说是存在方式）
# tuple1 = ()                     #空元组
# tuple2 = (1,)                   #单元素（逗号不可省略）
# tuple3 = (1, 2, 3)              #多元素
# tuple4 = 1, 2, 3                #省略掉括号也可以创建元组，但是都好不可省略
# tuple5 = tuple([1, 2, 3, 4])    #从可迭代对象转换

# ##索引与切片
# t = (1 , 20, 90, 23, 45)
# t_str = ('11', '14', '12', '13', 'a')
# print(t_str)
# print(t[1])
# print(t[1:4])
# print('反转：',t[::-1])
# ### 拼接与重复
# print('拼接：',(11, 12) + t)
# print('重复:',(13, 14) * 2)
# ### 成员检测
# print(1 in t)
# print(11 in t)
# ### 长度、最大值、最小值、和
# print('长度：', len(t))
# print('最大值：',max(t))
# print('最小值：', min(t_str))
# print('和：', sum(t))
# ### 解包
# a, b, c = (1, 2, 3)          # a=1, b=2, c=3
# head, *rest = (1, 2, 3, 4)   # head=1, rest=[2,3,4]
# *_, last = (1, 2, 3)         # last=3
# ### 方法
# print('统计元素出现次数：',t.count(2))
# print('统计第一次匹配到索引，不存在则会抛出错误：',t.index(20))
# ### 比较运算：按元素依次比较（类似字符串的字典序）：
# print('比较运算：',(1, 2) < (1, 3))   # True
# print('比较运算：',(1, 2) == (1, 2))  # True
# ### 因为元组不可变，所以可以用作字典的键
#
# dict1 = {
#     "a": 1,
#     "b": 2,
#     "c": 3,
# }
#
# for k in dict1.keys():
#     print(k, dict1[k])

# python类

## 类定义：

# ### 语法结构
# """
# class Demo1(base1 = None, base2 = None):
#     文档字符串(需使用多行注释包裹)
#     class_attr = 1 #类属性
#
#     def __init__(self, x): #实例方法
#         #以下为创建属性
#         self.x = x
#
#     @classmethod # 类方法
#     def cls_method(cls): #其中cls表示类本身
#
#     @staticmethod #静态方法
#     def static_method():
#
#     @property #属性
#     def prop(self):
# """
# class Demo:
#     def __init__(self):
#         self._x = 0
#
#     @property
#     def x(self):
#         return self._x
#
#     @x.setter
#     def x(self, v):
#         self._x = max(0, v)
# print(Demo().x)


class Base:
    class_attr = "base-class"

    #其中**kwargs表示任意数量的参数
    def __init__(self, x, **kwargs):
        self.x = x
        self._protected = "protected"
        self.__private = "private"           # → _Base__private

        #对于任意数量的参数可以通过setattr来进行批量设置为实例的属性
        #等价写法：self.__dict__.update(kwargs) #直接更新实例的__dict__
        for k, v in kwargs.items():
            setattr(self, k, v)


    def instance_method(self):
        return f"instance: x={self.x}"

    @classmethod
    def class_method(cls):
        return f"class: {cls.__name__}"

    @staticmethod
    def static_method(a, b):
        return a + b

    @property
    def doubled(self):
        return self.x * 2

    @doubled.setter
    def doubled(self, v):
        self.x = max(0, v // 2)


class Child(Base):
    def try_private(self):
        try:
            return self.__private             # mangle 成 _Child__private，找不到
        except AttributeError as e:
            return f"AttributeError: {e}"

    def get_parent_private(self):
        return self._Base__private            # 强访问


b = Base(10)
c = Child(20)

print("=== 1. 四种方法 ===")
print(b.instance_method())     # instance: x=10
print(b.class_method())        # class: Base
print(c.class_method())        # class: Child（cls 动态指向子类）
print(b.static_method(1, 2))   # 3
print(b.doubled)               # 20
b.doubled = 100
print(b.x)                     # 50（setter 钳制逻辑）

print("\n=== 2. 类调 vs 实例调 ===")
print(Base.class_method())     # class: Base
print(Base.instance_method(b)) # instance: x=50（手动传 self）
print(Base.doubled)            # <property object>，不触发 getter
print(Base.instance_method)    # <function>，裸函数
print(b.instance_method)       # <bound method>，self 已绑定

print("\n=== 3. 属性查找 ===")
print(b.class_attr)            # base-class（回落到类）
print(b.__dict__)              # {'x': 50, '_protected': ..., '_Base__private': ...}
# print(Base.x)                # ❌ AttributeError，类上没有实例属性

print("\n=== 4. 私有 ===")
print(b._protected)            # protected
# print(b.__private)           # ❌ AttributeError
print(b._Base__private)        # private
print(c.try_private())         # AttributeError: ... '_Child__private'
print(c.get_parent_private())  # private

print("\n=== 5. 继承与 MRO ===")
print(Child.__mro__)           # (Child, Base, object)
print(isinstance(c, Base))     # True
print(type(c) is Base)         # False（严格相等）


# 参数的几种进阶写法

## 1.位置 + 关键字混用
class Person:
    def __init__(self, name, age, *, city='北京', job='工程师'):
        #                         ⬆ 星号后面的必须使用关键字
        self.name = name
        self.age = age
        self.city = city
        self.job = job
#创建实例
p1 = Person("张三", 25)                       # ✅
p2 = Person("张三", 25, city="上海")           # ✅
# p3 = Person("张三", 25, "上海")                         # ❌ TypeError：city 只能用关键字

## 2.接收任意参数 *args / **kwargs
class Config:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

cfg = Config(host="127.0.0.1", port=8080, debug=True)
print(cfg.host)    # 127.0.0.1
print(cfg.port)    # 8080

## 3.解包传参
data = {"name": "张三", "age": 25}
p = Person(**data)           # 等价 Person(name="张三", age=25)

args = ["张三", 25]
p = Person(*args)            # 等价 Person("张三", 25)