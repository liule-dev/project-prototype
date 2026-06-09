from core.database import SessionLocal
from models.schemas import ChatSession, ChatMessage

db = SessionLocal()

print("=" * 60)
print("📊 数据库状态检查")
print("=" * 60)

# 查询会话总数
session_count = db.query(ChatSession).count()
print(f"\n💬 会话总数: {session_count}")

# 查询消息总数
message_count = db.query(ChatMessage).count()
print(f"📝 消息总数: {message_count}")

# 查询最新的10条消息
print("\n 最新10条消息:")
latest_messages = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(10).all()
for i, msg in enumerate(latest_messages, 1):
    content_preview = msg.content[:60] if len(msg.content) > 60 else msg.content
    print(f"  {i}. [{msg.role}] {content_preview}...")
    print(f"     创建时间: {msg.created_at}")
    print(f"     会话ID: {msg.session_id}")
    print()

db.close()
