@echo off
REM 地缘政治情报日报 - 定时任务批处理文件
REM 使用方法: 将此文件添加到Windows任务计划程序中

cd /d "C:\proj datamining\info_dyzz\geopolitical-analysis"

REM 设置中国时区 (UTC+8)
set TZ=Asia/Shanghai

echo [%date% %time%] Starting Geopolitical Intelligence Daily Workflow...

REM 使用虚拟环境中的Python
"%~dp0venv\Scripts\python.exe" run.py --run

if %errorlevel% equ 0 (
    echo [%date% %time%] Workflow completed successfully
) else (
    echo [%date% %time%] Workflow failed with error code %errorlevel%
)

echo [%date% %time%] Finished.
