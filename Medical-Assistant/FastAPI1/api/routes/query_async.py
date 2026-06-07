"""
异步问答接口
使用 Celery 任务处理耗时的 AI 推理
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from tasks.ai_tasks import generate_llm_response
from celery.result import AsyncResult
from core.celery_config import celery_app
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query/async", tags=["异步问答"])


class AsyncQueryRequest(BaseModel):
    """异步问答请求"""
    question: str
    session_id: str = "default_session"
    context_messages: list = []


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    result: dict = None
    error: str = None


@router.post("/", response_model=dict)
async def async_query(request: AsyncQueryRequest):
    """
    提交异步问答任务
    
    Args:
        request: 问答请求
        
    Returns:
        任务 ID 和状态
    """
    try:
        logger.info(f"📨 收到异步问答请求：{request.question[:50]}")
        
        # 提交 Celery 任务
        task = generate_llm_response.apply_async(
            args=[request.question, request.context_messages],
            queue='ai_queue',
            priority=9  # 高优先级
        )
        
        logger.info(f"✅ 任务已提交，Task ID: {task.id}")
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "任务已提交，请使用 task_id 查询结果"
        }
        
    except Exception as e:
        logger.error(f"❌ 提交异步任务失败：{e}")
        raise HTTPException(status_code=500, detail=f"提交任务失败：{str(e)}")


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    查询任务状态
    
    Args:
        task_id: 任务 ID
        
    Returns:
        任务状态和结果
    """
    try:
        # 获取任务结果
        result = AsyncResult(task_id, app=celery_app)
        
        if result.ready():
            # 任务完成
            if result.successful():
                return TaskStatusResponse(
                    task_id=task_id,
                    status="completed",
                    result=result.get()
                )
            else:
                return TaskStatusResponse(
                    task_id=task_id,
                    status="failed",
                    error=str(result.result)
                )
        else:
            # 任务进行中
            return TaskStatusResponse(
                task_id=task_id,
                status=result.state.lower() if result.state else "pending"
            )
        
    except Exception as e:
        logger.error(f"❌ 查询任务状态失败：{e}")
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")


@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """
    获取任务结果（阻塞等待）
    
    Args:
        task_id: 任务 ID
        
    Returns:
        任务结果
    """
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        # 等待结果（最多等待 60 秒）
        try:
            task_result = result.get(timeout=60)
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": task_result
            }
            
        except result.TimeoutError:
            return {
                "task_id": task_id,
                "status": "timeout",
                "message": "任务执行超时"
            }
        
    except Exception as e:
        logger.error(f"❌ 获取任务结果失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取结果失败：{str(e)}")
