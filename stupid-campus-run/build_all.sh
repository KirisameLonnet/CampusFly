#!/bin/bash

echo "========================================"
echo "通用多平台二进制编译脚本"
echo "支持: macOS, Linux, Windows"
echo "========================================"
echo

# 检测操作系统
OS=$(uname -s)
ARCH=$(uname -m)

echo "检测到系统: $OS $ARCH"

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

# 创建输出目录
mkdir -p dist

# 编译函数
build_for_platform() {
    local platform=$1
    local arch=$2
    local ext=$3
    
    echo
    echo "========================================"
    echo "编译 $platform $arch 版本..."
    echo "========================================"
    
    local output_name="CampusFly-$platform-$arch$ext"
    
    # 根据平台设置编译参数
    case $platform in
        "macos")
            if [ "$arch" = "universal" ]; then
                # 创建Universal Binary
                if [ -f "dist/CampusFly-macos-arm64" ] && [ -f "dist/CampusFly-macos-x86_64" ]; then
                    lipo -create -output "dist/$output_name" "dist/CampusFly-macos-arm64" "dist/CampusFly-macos-x86_64"
                    if [ -f "dist/$output_name" ]; then
                        echo "✅ Universal Binary 创建成功"
                        echo "文件: dist/$output_name"
                        echo "大小: $(ls -lh dist/$output_name | awk '{print $5}')"
                        echo "架构: $(lipo -info dist/$output_name)"
                    else
                        echo "❌ Universal Binary 创建失败"
                    fi
                else
                    echo "❌ 需要先编译ARM64和x86_64版本"
                fi
            else
                pyinstaller --onefile --console --name "CampusFly-$platform-$arch" tui.py
            fi
            ;;
        "linux")
            pyinstaller --onefile --console --name "CampusFly-$platform-$arch" tui.py
            ;;
        "windows")
            echo "Windows版本需要在Windows系统上编译"
            echo "请运行: build_windows.bat"
            return
            ;;
    esac
    
    if [ -f "dist/$output_name" ]; then
        echo "✅ $platform $arch 版本编译成功"
        echo "文件: dist/$output_name"
        echo "大小: $(ls -lh dist/$output_name | awk '{print $5}')"
    else
        echo "❌ $platform $arch 版本编译失败"
    fi
}

# 根据操作系统编译
case $OS in
    "Darwin")
        echo "macOS系统，编译macOS版本..."
        
        # 编译当前架构
        if [ "$ARCH" = "arm64" ]; then
            build_for_platform "macos" "arm64" ""
            
            echo
            echo "是否要编译x86_64版本？(需要Rosetta2)"
            read -p "输入 y 继续，其他键跳过: " choice
            if [ "$choice" = "y" ]; then
                arch -x86_64 pyinstaller --onefile --console --name "CampusFly-macos-x86_64" tui.py
            fi
        else
            build_for_platform "macos" "x86_64" ""
        fi
        
        # 创建Universal Binary
        if [ -f "dist/CampusFly-macos-arm64" ] && [ -f "dist/CampusFly-macos-x86_64" ]; then
            build_for_platform "macos" "universal" ""
        fi
        ;;
    "Linux")
        echo "Linux系统，编译Linux版本..."
        
        if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
            build_for_platform "linux" "arm64" ""
        else
            build_for_platform "linux" "x86_64" ""
        fi
        ;;
    *)
        echo "不支持的操作系统: $OS"
        echo "请使用对应的编译脚本:"
        echo "  macOS: ./build_macos.sh"
        echo "  Linux: ./build_linux.sh"
        echo "  Windows: build_windows.bat"
        exit 1
        ;;
esac

echo
echo "========================================"
echo "编译完成！"
echo "========================================"
echo "输出文件:"
ls -la dist/
echo
echo "使用方法:"
echo "  macOS: ./dist/CampusFly-macos-<arch>"
echo "  Linux: ./dist/CampusFly-linux-<arch>"
echo "  Windows: dist\\CampusFly-windows-<arch>.exe"
echo
