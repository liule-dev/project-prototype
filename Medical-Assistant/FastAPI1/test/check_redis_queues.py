import redis

r = redis.Redis(host='localhost', port=6379, db=1)

print("🔍 检查 Redis 中的所有 Celery 相关键:")
print("=" * 60)

# 检查所有队列
queues = ['celery', 'ai_queue', 'file_queue', 'data_queue']
for queue in queues:
    length = r.llen(queue)
    print(f"{queue}: {length} 个任务")
    if length > 0:
        print(f"  内容: {r.lrange(queue, 0, 2)}")

print()

# 检查 unacked
unacked_keys = r.keys('unacked*')
print(f"Unacked keys: {len(unacked_keys)}")
for k in unacked_keys[:5]:
    print(f"  {k.decode()}: {r.type(k).decode()}")

print()

# 检查所有键
all_keys = r.keys('*')
print(f"Redis DB1 总键数: {len(all_keys)}")
print("前20个键:")
for k in sorted(all_keys)[:20]:
    print(f"  {k.decode()}")
