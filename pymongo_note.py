# -*- coding: utf-8 -*-
# PyMongo 官方文档阅读简记
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

# 1.首先创建MongoClient
client = MongoClient()  # 默认创建
client = MongoClient('localhost', 27017)  # 指定host 和 port
client = MongoClient('mongodb://localhost:27017/')  # 使用 MongoDB URI format

# 2. 创建数据库
'''
一个MongoClient对象可以创建多个数据库, 可以通过属性访问方式来获取实例
'''
db = client.test_database
# 如果数据库名特殊比如有间隔线无法使用属性访问方式时可以使用字典访问方式:
db = client['test-database']

# 3.获取集合
# 集合是MongoDB中用来存储文档的容器, 可以类比关系数据库中的表
# 和访问数据库一样，集合也可以通过属性访问和字典访问两种形式:
collection = db.test_collection
collection = db['test-collection']

# TODO: 注意一点，MongoDB中创建数据库和集合的都是懒操作, 上面这些语句不会创建
# TODO: 数据库和集合, 只有第一次在集合中进行文档插入或者创建索引的时候才会创建

# 3.文档

# MongoDB 使用 JSON类型文档来表示和存储数据, 在PyMongo中我们使用字典来表示一个文档
# 实例如下

post = {
    "author": "Mike",
    "text": "My First blog post!",
    "tags": ["mongoDB", "python", "pymongo"],
    "date": datetime.datetime.utcnow()
}
# TODO: 文档中包含的 Python 自带数据类型datetime 将会自动转换为合适的BSON类型

# 插入文档

# 通过insert_one插入一条文档
posts = db.post
post_id = posts.insert_one(post).inserted_id  # 返回插入后自动生成的_id

# TODO: 如果没有_id字段, MongoDB将会自动进行创建, insert_one 返回一个 InsertOneResult实例
# TODO: 插入数据后post集合才会被真正创建,可以通过如下方式来查看数据库中的所有集合

db.collection_names(include_system_collections=False)

# 获取文档: find_one 与find_many
# find_one返回一个匹配到的一条文档或者返回第一条文档,如果没有匹配返回None
# 其返回格式是一个字典,和我们上面插入的数据格式一致
# 返回文档中的第一条数据
posts.find_one()
# 返回符合查询条件的第一条数据
posts.find_one({"author": "Eliot"})
# 查询多条数据, 通过find方法和相关的过滤条件可以一次性查询多条数据
# 返回一个Cursor进行结果遍历, 如下
for post in posts.find({"author": "Mike"}):
    print(post)  # 通过obekct_id进行查询

posts.find_one({"_id": post_id})


# TODO:在应用中我们通常得到的是string类型的id, 需要转换为ObjectId类型
# 如下, 通过ObjectId将post_id从string类型转换为ObjectId类型
def get(post_id):
    document = client.db.collection.find_one({'_id': ObjectId(post_id)})


# 字符串编码

# mongoDB使用BSON格式的数据进行存储, 都是以UTF-8进行编码。 PyMongo也要保证被存储的所有数据
# 都要以UTF-8数据编码。正常str类型的字符串被存储正常, 但是如果是unicode类型的字符串, 会被用UTF-8
# 进行一次编码,

# 多行插入
# 除了insert_one之外我们还可以通过insert_many一次性插入大量数据,
new_posts = [{"author": "Mike",
              "text": "Another post!",
              "tags": ["bulk", "insert"],
              "date": datetime.datetime(2009, 11, 12, 11, 14)},
             {"author": "Eliot",
              "title": "MongoDB is fun",
              "text": "and pretty easy too!",
              "date": datetime.datetime(2009, 11, 10, 10, 45)}]
result = posts.insert_many(new_posts)
result.insert_ids  # [ObjectId('...'), ObjectId('...')]

# TODO 注意上面两个文档数据, 其数据字段是不同的, 这是mongodb的一个特性

# 计数: 计算集合中文档的个数
posts.count()
posts.find({"author": "Mike"}).count()

# 范围查询
d = datetime.datetime(2009, 11, 12, 12)
# 查询date字段中小于d的内容并按照author进行排序
for post in posts.find({"date": {"$lt": d}}).sort("author"):
    print(post)

# 索引
# 创建user_id索引且值不允许重复, 当再次插入重复值的时候就会报错
result = db.profiles.create_index([('user_id', pymongo.ASCENDING)],unique=True)
# 索引非常有利于检索, 比如文本搜索, 可以通过添加text类型的索引


#
'''
总结
实例
数据库创建, 集合获取
find/find_one
insert_one/insert_many
ObjectId
count()
create_index(unique=True)
范围查询 $lt

遗留任务: 翻译编码文章

'''