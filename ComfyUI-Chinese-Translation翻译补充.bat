@echo off
chcp 65001 >nul
echo ========================================
echo   复制 zh-CN 到 ComfyUI-Chinese-Translation
echo ========================================
echo.

set "SOURCE_DIR=zh-CN"
set "TARGET_DIR=..\ComfyUI-Chinese-Translation"

if not exist "%SOURCE_DIR%" (
    echo [错误] 源目录不存在: %SOURCE_DIR%
    pause
    exit /b 1
)

if not exist "%TARGET_DIR%" (
    echo [错误] 目标目录不存在: %TARGET_DIR%
    pause
    exit /b 1
)

echo 源目录: %SOURCE_DIR%
echo 目标目录: %TARGET_DIR%
echo.

xcopy "%SOURCE_DIR%" "%TARGET_DIR%\zh-CN\" /E /I /Y /Q

if %errorlevel% equ 0 (
    echo.
    echo [成功] 复制完成!
) else (
    echo.
    echo [失败] 复制出错，错误代码: %errorlevel%
)

echo.
pause
