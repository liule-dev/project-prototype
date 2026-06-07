@echo off
chcp 65001 >nul
echo ============================================================
echo Redis 缓存清理工具 - Windows 启动脚本
echo ============================================================
echo.

cd /d "%~dp0"

echo ============================================================
echo Redis 缓存清理工具
echo ============================================================
echo.
echo 可用的缓存类型:
echo   1. clip      - CLIP 文本/图片向量缓存
echo   2. minio     - MinIO 临时访问链接
echo   3. llm       - 大模型回答缓存
echo   4. history   - 会话历史记录
echo   5. all       - 清空所有缓存
echo ============================================================
echo.

set /p choice="请输入选项 (1/2/3/4/5): "

if "%choice%"=="1" (
    set type=clip
    goto :confirm
)

if "%choice%"=="2" (
    set type=minio
    goto :confirm
)

if "%choice%"=="3" (
    set type=llm
    goto :confirm
)

if "%choice%"=="4" (
    set type=history
    goto :confirm
)

if "%choice%"=="5" (
    set type=all
    goto :confirm_all
)

echo ❌ 无效的选项
goto :end

:confirm
echo.
set /p confirm="⚠️  确定要清理 %type% 缓存吗？(y/n): "
if /i "%confirm%"=="y" (
    echo.
    echo 正在执行清理...
    python clear_redis.py %type%
) else (
    echo 已取消操作
)
goto :end

:confirm_all
echo.
set /p confirm="⚠️  确定要清空所有缓存吗？此操作不可恢复！(y/n): "
if /i "%confirm%"=="y" (
    echo.
    echo 正在执行清理...
    python clear_redis.py all
) else (
    echo 已取消操作
)
goto :end

:end
echo.
pause
