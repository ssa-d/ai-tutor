@echo off
chcp 65001 >nul
title AI Tutor - 一键提交推送
cd /d "%~dp0"

echo ============================================
echo   AI Tutor  一键提交并推送 GitHub
echo ============================================
echo.

REM ---- 0. 安全检查：确保 .env 不会被提交 ----
if exist ".env" (
    echo [安全] 检测到 .env 存在。确认它已被 .gitignore 忽略...
    git check-ignore .env >nul 2>&1
    if errorlevel 1 (
        echo [警告] .env 不在 .gitignore 中！为了安全，不执行提交，请先检查。
        echo        请确保 .gitignore 里有 ".env" 这一行。
        pause
        exit /b 1
    )
)
echo [安全] .env 已被忽略，可以安全提交。OK
echo.

REM ---- 1. 初始化 git（若还没建仓库）----
if not exist ".git" (
    echo [步骤 1/4] 正在初始化 git 仓库...
    git init
)

REM ---- 2. 关联远程仓库（若还没设置）----
set "REMOTE_URL=git remote get-url origin"
FOR /F %%i IN ('2^>nul git remote get-url origin') DO SET "HASREMOTE=yes"
if not defined HASREMOTE (
    echo.
    echo [步骤 2/4] 还没配置远程仓库。
    echo        请在下面粘贴你的 GitHub 仓库地址（形如 https://github.com/你的用户名/ai-tutor.git）：
    echo        你可以到 github.com 新建仓库后复制地址，或直接回车跳过（之后手动配置）。
    set /p REMOTE=远程地址:
    if not "%REMOTE%"=="" git remote add origin "%REMOTE%"
) else (
    echo [步骤 2/4] 已配置远程仓库。
)

REM ---- 3. 提交改动 ----
echo [步骤 3/4] 提交改动...
git add .
set /p MSG=提交说明(直接回车用默认):
if "%MSG%"=="" set "MSG=AI Tutor 更新"
git commit -m "%MSG%"

REM ---- 4. 推送 ----
echo [步骤 4/4] 推送到 GitHub...
echo.（若失败，常见原因：远程仓库未配置、或未登录。可先手动配置远程后再运行。）
git push -u origin main 2>nul
if errorlevel 1 (
    echo.
    echo [提示] 当前默认分支可能是 master，尝试用 master 推送...
    git push -u origin master 2>nul
)
echo.
echo ============================================
echo   完成！已提交并推送（如无报错）。
echo ============================================
pause
