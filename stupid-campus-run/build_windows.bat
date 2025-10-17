@echo off
echo ========================================
echo Windows 二进制编译脚本
echo 支持: x86_64, ARM64
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境，请先安装Python
    pause
    exit /b 1
)

echo 1. 检查Python环境...
python --version

echo.
echo 2. 安装/更新依赖...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo 3. 清理旧的构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo 4. 检测当前架构...
for /f "tokens=2 delims==" %%i in ('wmic os get osarchitecture /value') do set ARCH=%%i
echo 检测到架构: %ARCH%

echo.
echo 5. 开始编译...

REM 编译x86_64版本
echo ========================================
echo 编译 x86_64 版本...
echo ========================================
pyinstaller --onefile --console --name CampusFly-x86_64 tui.py

if exist "dist\CampusFly-x86_64.exe" (
    echo ✅ x86_64 版本编译成功
    echo 文件: dist\CampusFly-x86_64.exe
    for %%A in ("dist\CampusFly-x86_64.exe") do echo 大小: %%~zA 字节
) else (
    echo ❌ x86_64 版本编译失败
)

echo.
echo 是否要编译ARM64版本？
set /p choice="输入 y 继续，其他键跳过: "
if /i "%choice%"=="y" (
    echo ========================================
    echo 编译 ARM64 版本...
    echo ========================================
    
    REM 检查是否有ARM64 Python
    python -c "import platform; print(platform.machine())" | findstr /i "arm64" >nul
    if errorlevel 1 (
        echo 当前Python不是ARM64版本，尝试使用x86_64 Python编译ARM64版本...
        echo 注意: 这可能需要特殊的交叉编译环境
    )
    
    pyinstaller --onefile --console --name CampusFly-ARM64 tui.py
    
    if exist "dist\CampusFly-ARM64.exe" (
        echo ✅ ARM64 版本编译成功
        echo 文件: dist\CampusFly-ARM64.exe
        for %%A in ("dist\CampusFly-ARM64.exe") do echo 大小: %%~zA 字节
    ) else (
        echo ❌ ARM64 版本编译失败
    )
)

echo.
echo ========================================
echo 编译完成！
echo ========================================
echo 输出文件:
dir dist\
echo.
echo 使用方法:
echo   dist\CampusFly-<arch>.exe
echo.
pause
