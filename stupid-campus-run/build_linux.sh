#!/bin/bash

echo "========================================"
echo "Linux 二进制编译脚本"
echo "支持: x86_64, ARM64"
echo "========================================"
echo

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3环境，请先安装Python3"
    exit 1
fi

echo "1. 检查Python环境..."
python3 --version

echo
echo "2. 安装/更新依赖..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo
echo "3. 清理旧的构建文件..."
rm -rf dist build __pycache__

# 检测当前架构
ARCH=$(uname -m)
echo "4. 检测到当前架构: $ARCH"

# 编译函数
build_for_arch() {
    local arch=$1
    local arch_name=$2
    
    echo
    echo "========================================"
    echo "编译 $arch_name 版本..."
    echo "========================================"
    
    # 编译
    pyinstaller --onefile --console --name "CampusFly-$arch_name" tui.py
    
    if [ -f "dist/CampusFly-$arch_name" ]; then
        echo "✅ $arch_name 版本编译成功"
        echo "文件: dist/CampusFly-$arch_name"
        echo "大小: $(ls -lh dist/CampusFly-$arch_name | awk '{print $5}')"
        echo "架构: $(file dist/CampusFly-$arch_name)"
    else
        echo "❌ $arch_name 版本编译失败"
    fi
}

# 根据当前架构编译
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    echo "当前为ARM64架构，编译ARM64版本..."
    build_for_arch "aarch64" "arm64"
    
    echo
    echo "是否要编译x86_64版本？(需要交叉编译工具链)"
    read -p "输入 y 继续，其他键跳过: " choice
    if [ "$choice" = "y" ]; then
        echo "检查交叉编译工具链..."
        if command -v gcc-x86_64-linux-gnu &> /dev/null; then
            echo "使用gcc-x86_64-linux-gnu编译x86_64版本..."
            CC=gcc-x86_64-linux-gnu pyinstaller --onefile --console --name "CampusFly-x86_64" tui.py
        else
            echo "未找到交叉编译工具链，跳过x86_64版本编译"
            echo "安装方法: sudo apt-get install gcc-x86_64-linux-gnu"
        fi
    fi
    
elif [ "$ARCH" = "x86_64" ]; then
    echo "当前为x86_64架构，编译x86_64版本..."
    build_for_arch "x86_64" "x86_64"
    
    echo
    echo "是否要编译ARM64版本？(需要交叉编译工具链)"
    read -p "输入 y 继续，其他键跳过: " choice
    if [ "$choice" = "y" ]; then
        echo "检查交叉编译工具链..."
        if command -v aarch64-linux-gnu-gcc &> /dev/null; then
            echo "使用aarch64-linux-gnu-gcc编译ARM64版本..."
            CC=aarch64-linux-gnu-gcc pyinstaller --onefile --console --name "CampusFly-arm64" tui.py
        else
            echo "未找到交叉编译工具链，跳过ARM64版本编译"
            echo "安装方法: sudo apt-get install gcc-aarch64-linux-gnu"
        fi
    fi
else
    echo "未知架构: $ARCH"
    echo "尝试编译当前架构版本..."
    build_for_arch "$ARCH" "$ARCH"
fi

echo
echo "========================================"
echo "编译完成！"
echo "========================================"
echo "输出文件:"
ls -la dist/
echo
echo "使用方法:"
echo "  ./dist/CampusFly-<arch>"
echo
