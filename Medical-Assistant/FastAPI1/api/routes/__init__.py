# 路由模块导出
from api.routes.upload import router as upload_router
from api.routes.auth import router as auth_router

# 异步路由模块
from api.routes import query_async
from api.routes import websocket_async

__all__ = ['upload_router', 'auth_router', 'query_async', 'websocket_async']
