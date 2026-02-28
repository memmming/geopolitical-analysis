# PowerShell脚本：创建Windows任务计划程序任务
# 使用方法: 以管理员身份运行 PowerShell，然后执行：
# .\setup_task.ps1

$ErrorActionPreference = "Stop"

# 配置参数
$taskName = "地缘政治情报日报"
$scriptPath = "C:\proj datamining\info_dyzz\geopolitical-analysis\run_daily.bat"
$workingDir = "C:\proj datamining\info_dyzz\geopolitical-analysis"

# 检查批处理文件是否存在
if (-not (Test-Path $scriptPath)) {
    Write-Error "批处理文件不存在: $scriptPath"
    exit 1
}

Write-Host "正在创建任务计划程序任务..." -ForegroundColor Green

# 获取当前用户的凭据（用于交互式登录）
$credential = Get-Credential

# 创建任务动作
$action = New-ScheduledTaskAction `
    -Execute "$env:windir\System32\cmd.exe" `
    -Argument "/c `"$scriptPath`"" `
    -WorkingDirectory $workingDir

# 创建触发器（每天12:00运行）
$trigger = New-ScheduledTaskTrigger -Daily -At 12:00

# 创建任务设置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# 注册任务
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -User $credential.UserName `
        -Password $credential.GetNetworkCredential().Password `
        -RunLevel Highest `
        -Force

    Write-Host "✓ 任务创建成功!" -ForegroundColor Green
    Write-Host "任务名称: $taskName" -ForegroundColor Cyan
    Write-Host "执行时间: 每天 12:00" -ForegroundColor Cyan
    Write-Host "脚本路径: $scriptPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "如需修改任务，请打开任务计划程序 (taskschd.msc)" -ForegroundColor Yellow

} catch {
    Write-Error "创建任务失败: $_"
    exit 1
}
