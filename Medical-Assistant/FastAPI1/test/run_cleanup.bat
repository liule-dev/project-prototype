@echo off
chcp 65001 >nul
echo ============================================================
echo Qdrant 孤立向量清理工具 - Windows 启动脚本
echo ============================================================
echo.

cd /d "%~dp0"

echo 正在检查依赖...
python -c "import schedule" 2>nul
if errorlevel 1 (
    echo ⚠️  未安装 schedule 库，正在安装...
    pip install schedule
    if errorlevel 1 (
        echo ❌ 安装失败，请手动运行：pip install schedule
        pause
        exit /b 1
    )
    echo ✅ schedule 安装成功
) else (
    echo ✅ schedule 已安装
)

echo.
echo ============================================================
echo 请选择运行模式:
echo 1. 立即执行一次清理
echo 2. 启动定时服务（每天凌晨 2:00 自动执行）
echo 3. 仅测试，不实际执行
echo ============================================================
echo.

set /p choice="请输入选项 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 正在执行清理任务...
    python cleanup_orphan_vectors.py
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo 正在启动定时服务...
    python scheduler_cleanup.py
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo 正在测试配置...
    python scheduler_cleanup.py
    goto :end
)

echo ❌ 无效的选项

:end
echo.
pause
