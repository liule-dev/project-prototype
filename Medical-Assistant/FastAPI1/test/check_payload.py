"""检查 Qdrant 中的 payload 结构"""
from qdrant_client import QdrantClient

client = QdrantClient(host='localhost', port=6333, grpc_port=6334, prefer_grpc=True)

print("检查 medical_documents 集合的 payload 结构")
print("=" * 60)

# 不使用过滤器，直接检索所有数据
results = client.query_points(
    collection_name="medical_documents",
    query=[0.0] * 512,
    limit=2
)

print(f"\n找到 {len(results.points)} 条记录\n")

for i, point in enumerate(results.points):
    print(f"记录 {i+1}:")
    print(f"  ID: {point.id}")
    print(f"  Score: {point.score}")
    print(f"  Payload:")
    if point.payload:
        for key, value in point.payload.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"    {key}: {value[:100]}...")
            else:
                print(f"    {key}: {value}")
    print()

print("=" * 60)
