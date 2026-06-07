# 导入 redis 库
import redis

# 1. 创建 Redis 连接（适配你的 8.6.1 版本）
r = redis.Redis(
    host="127.0.0.1",  # 本地 Redis 地址
    port=6379,         # 默认端口
    db=0,              # 使用第 0 个数据库
    password="",       # 本地无密码，留空
    decode_responses=True  # 关键：自动将 bytes 转字符串，解决中文乱码
)

# 2. 测试连接（返回 True 表示连接成功）
print("Redis 连接状态：", r.ping())

# 3. 测试基础读写（中文正常）
r.set("test_user", "张三", ex=300)  # 设置缓存，5 分钟过期
print("读取缓存：", r.get("test_user"))  # 预期输出：张三

# 4. 测试复杂数据（字典/列表）
import json
user_info = {"id": 1001, "name": "李四", "地址": "北京市海淀区"}
# 序列化字典为 JSON 字符串存入 Redis（ensure_ascii=False 保留中文）
r.set("user_info:1001", json.dumps(user_info, ensure_ascii=False), ex=300)
# 读取并反序列化
user_cache = json.loads(r.get("user_info:1001"))
print("复杂中文数据：", user_cache)  # 预期输出：{'id': 1001, 'name': '李四', '地址': '北京市海淀区'}