"""
WebSocket 流式问答接口（Celery 异步版本）
支持实时推送 Celery 任务进度
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from tasks.ai_tasks import generate_llm_response
from tasks.data_tasks import save_session_message, update_session_cache
from celery.result import AsyncResult
from core.celery_config import celery_app
from services.cache_service import cache_service
from services.session_service import session_service
from core import SessionLocal, settings
import logging
import asyncio
import json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket异步"])


@router.websocket("/query/stream/async")
async def async_stream_query(websocket: WebSocket):
    """
    异步流式问答接口
    
    使用 Celery 任务处理 AI 推理，实时推送进度
    """
    await websocket.accept()
    
    # 获取会话 ID
    query_params = dict(websocket.query_params)
    user_id = query_params.get("user_id", "1")
    session_id = query_params.get("session_id", f"session_{id(websocket)}")
    
    db = SessionLocal()
    history = []
    
    try:
        # 加载历史消息
        history = cache_service.get_session_history(session_id)
        if not history:
            history = session_service.get_session_messages(db, session_id)
            if history:
                cache_service.save_session_history(session_id, history)
        
        # 规范化 content 字段为字符串（防止数据库返回的列表格式导致后续处理报错）
        if history:
            for msg in history:
                if isinstance(msg.get("content"), list) and len(msg["content"]) > 0:
                    msg["content"] = msg["content"][0].get("text", "") if isinstance(msg["content"][0], dict) else str(msg["content"][0])
        
        logger.info(f"✅ WebSocket 连接建立，会话 ID: {session_id}")
        
        while True:
            # 接收消息
            data = await websocket.receive_json()
            
            # 处理加载历史消息事件
            event = data.get("event")
            if event == "load_history":
                # 返回历史消息给前端
                if history:
                    await websocket.send_json({
                        "event": "history",
                        "messages": [{
                            "role": msg["role"], 
                            "content": msg["content"][0]["text"] if isinstance(msg["content"], list) else msg["content"]
                        } for msg in history]
                    })
                else:
                    await websocket.send_json({
                        "event": "history",
                        "messages": []
                    })
                continue
            
            question = data.get("question", "").strip()
            image_base64 = data.get("image", None)
            
            if not question and not image_base64:
                await websocket.send_json({
                    "event": "error",
                    "message": "请输入问题或上传图片"
                })
                continue
            
            # 构建用户消息
            user_text = question
            if image_base64:
                user_text += " [图片]"
            
            history.append({"role": "user", "content": user_text})
            
            # 异步保存用户消息
            save_session_message.delay(
                user_id=int(user_id) if user_id.isdigit() else 1,
                session_id=session_id,
                role="user",
                content=user_text
            )
            
            await websocket.send_json({"event": "start"})
            await websocket.send_json({
                "event": "delta",
                "text": "🤔 正在分析您的问题..."
            })
            
            try:
                # 提交 Celery 任务
                task = generate_llm_response.apply_async(
                    args=[question, history[:-1]],  # 排除当前用户消息
                    queue='ai_queue',
                    priority=9
                )
                
                logger.info(f"📨 提交 Celery 任务，Task ID: {task.id}")
                
                # 轮询任务状态并推送进度
                progress_messages = [
                    "🔍 正在检索相关知识库...",
                    "🧠 正在分析医学文献...",
                    "✍️ 正在生成专业回答...",
                    "✅ 正在整理最终结果..."
                ]
                
                progress_idx = 0
                max_wait_time = 360  # 最大等待 360 秒（6 分钟）
                start_time = asyncio.get_event_loop().time()
                last_progress_time = start_time
                
                while not task.ready():
                    # 检查超时
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > max_wait_time:
                        await websocket.send_json({
                            "event": "error",
                            "message": "任务执行超时，请稍后重试"
                        })
                        break
                    
                    # 每隔 5 秒推送一次进度，防止连接假死
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_progress_time > 5 and progress_idx < len(progress_messages):
                        await websocket.send_json({
                            "event": "delta",
                            "text": progress_messages[progress_idx]
                        })
                        progress_idx += 1
                        last_progress_time = current_time
                    
                    # 等待 1 秒后再次检查（提高响应灵敏度）
                    await asyncio.sleep(1)
                
                # 获取任务结果
                if task.successful():
                    result = task.get()
                    
                    answer = result.get("answer", "")
                    images = result.get("images", [])
                    confidence = result.get("confidence", 0.5)
                    specialty = result.get("specialty", "unknown")
                    
                    # 如果置信度低，添加警告
                    if confidence < 0.8:
                        answer += "\n\n⚠️ 注：经系统评估，本回答可信度较低，建议咨询专业医生核实。"
                    
                    # 逐字推送回答（模拟流式效果）
                    chunk_size = 10
                    for i in range(0, len(answer), chunk_size):
                        chunk = answer[i:i + chunk_size]
                        await websocket.send_json({
                            "event": "delta",
                            "text": chunk
                        })
                        await asyncio.sleep(0.05)  # 控制推送速度
                    
                    # 发送结束消息
                    end_data = {"event": "end"}
                    
                    if images:
                        from services.minio_service import minio_service
                        from datetime import timedelta
                        
                        minio_urls = []
                        for img_meta in images:
                            bucket = img_meta.get('bucket_name')
                            obj_key = img_meta.get('object_name')
                            
                            try:
                                minio_url = minio_service.generate_presigned_url(
                                    object_name=obj_key,
                                    bucket_name=bucket,
                                    expires=timedelta(hours=1)
                                )
                                minio_urls.append({
                                    "url": minio_url,
                                    "similarity": img_meta.get('similarity', 0),
                                    "filename": img_meta.get('filename', '')
                                })
                            except Exception as e:
                                logger.warning(f"生成链接失败：{e}")
                        
                        end_data["images"] = minio_urls
                    
                    await websocket.send_json(end_data)
                    
                    # 保存助手回答到历史
                    history.append({"role": "assistant", "content": answer})
                    logger.info(f"💾 准备异步保存助手消息：Session {session_id}")
                    
                    # 异步保存助手消息
                    save_task = save_session_message.delay(
                        user_id=int(user_id) if user_id.isdigit() else 1,
                        session_id=session_id,
                        role="assistant",
                        content=answer,
                        confidence=confidence,
                        specialty=specialty
                    )
                    logger.info(f"📨 已提交保存任务，Task ID: {save_task.id}")
                    
                    # 异步更新缓存
                    update_session_cache.delay(
                        session_id=session_id,
                        messages=history
                    )
                    
                    logger.info(f"✅ 异步问答完成，置信度：{confidence:.2f}")
                    
                else:
                    # 任务失败
                    error_msg = str(task.result) if task.result else "未知错误"
                    await websocket.send_json({
                        "event": "error",
                        "message": f"处理失败：{error_msg}"
                    })
                    
            except Exception as e:
                logger.error(f"❌ 处理消息失败：{e}")
                await websocket.send_json({
                    "event": "error",
                    "message": f"处理失败：{str(e)}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket 连接断开：{session_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket 异常：{e}")
    finally:
        db.close()


@router.websocket("/query/task/{task_id}")
async def track_task_progress(websocket: WebSocket, task_id: str):
    """
    跟踪特定 Celery 任务的进度
    
    Args:
        task_id: Celery 任务 ID
    """
    await websocket.accept()
    
    try:
        logger.info(f"📊 开始跟踪任务进度：{task_id}")
        
        # 轮询任务状态
        while True:
            result = AsyncResult(task_id, app=celery_app)
            
            if result.ready():
                # 任务完成
                if result.successful():
                    await websocket.send_json({
                        "status": "completed",
                        "result": result.get()
                    })
                else:
                    await websocket.send_json({
                        "status": "failed",
                        "error": str(result.result)
                    })
                break
            else:
                # 任务进行中
                await websocket.send_json({
                    "status": result.state.lower(),
                    "progress": "processing"
                })
                
                # 等待 1 秒后再次检查
                await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        logger.info(f"进度跟踪连接断开：{task_id}")
    except Exception as e:
        logger.error(f"❌ 进度跟踪失败：{e}")
        await websocket.send_json({
            "status": "error",
            "error": str(e)
        })
