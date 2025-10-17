# 多平台二进制编译说明

本项目支持在多个平台上编译生成二进制可执行文件。

## 支持的平台和架构

| 平台 | 架构 | 文件名 | 说明 |
|------|------|--------|------|
| macOS | ARM64 | `CampusFly-macos-arm64` | Apple Silicon |
| macOS | x86_64 | `CampusFly-macos-x86_64` | Intel Mac |
| macOS | Universal | `CampusFly-macos-universal` | 通用二进制 |
| Linux | ARM64 | `CampusFly-linux-arm64` | ARM64 Linux |
| Linux | x86_64 | `CampusFly-linux-x86_64` | x86_64 Linux |
| Windows | x86_64 | `CampusFly-windows-x86_64.exe` | 64位Windows |
| Windows | ARM64 | `CampusFly-windows-ARM64.exe` | ARM64 Windows |

## 编译方法

### 1. 通用编译脚本（推荐）

```bash
# 自动检测系统并编译对应版本
./build_all.sh
```

### 2. 平台特定编译脚本

#### macOS
```bash
# 编译macOS版本（支持ARM64、x86_64、Universal）
./build_macos.sh
```

#### Linux
```bash
# 编译Linux版本（支持ARM64、x86_64）
./build_linux.sh
```

#### Windows
```cmd
# 编译Windows版本（支持x86_64、ARM64）
build_windows.bat
```

## 环境要求

### 通用要求
- Python 3.7+
- pip
- 网络连接（下载依赖）

### 平台特定要求

#### macOS
- Xcode Command Line Tools
- 对于交叉编译：Rosetta2（在ARM64 Mac上编译x86_64）

#### Linux
- 对于交叉编译：交叉编译工具链
  - ARM64: `sudo apt-get install gcc-aarch64-linux-gnu`
  - x86_64: `sudo apt-get install gcc-x86_64-linux-gnu`

#### Windows
- Visual Studio Build Tools（推荐）
- 对于ARM64：需要ARM64版本的Python

## 编译选项说明

- `--onefile`: 打包成单个可执行文件
- `--console`: 保留控制台窗口（用于TUI界面）
- `--name`: 指定输出文件名

## 输出文件

编译成功后，会在 `dist/` 目录中生成对应的可执行文件：

```
dist/
├── CampusFly-macos-arm64          # macOS ARM64
├── CampusFly-macos-x86_64         # macOS x86_64
├── CampusFly-macos-universal      # macOS Universal
├── CampusFly-linux-arm64          # Linux ARM64
├── CampusFly-linux-x86_64         # Linux x86_64
├── CampusFly-windows-x86_64.exe   # Windows x86_64
└── CampusFly-windows-ARM64.exe    # Windows ARM64
```

## 使用方法

### macOS
```bash
# 给执行权限
chmod +x dist/CampusFly-macos-<arch>

# 运行
./dist/CampusFly-macos-<arch>
```

### Linux
```bash
# 给执行权限
chmod +x dist/CampusFly-linux-<arch>

# 运行
./dist/CampusFly-linux-<arch>
```

### Windows
```cmd
# 直接运行
dist\CampusFly-windows-<arch>.exe
```

## 故障排除

### 编译失败
1. 检查Python版本是否为3.7+
2. 确保网络连接正常
3. 检查是否有足够的磁盘空间
4. 尝试以管理员权限运行

### 运行失败
1. 检查文件权限（Linux/macOS）
2. 确保目标系统有必要的运行时库
3. 检查杀毒软件是否阻止运行

### 交叉编译问题
1. 确保安装了正确的交叉编译工具链
2. 检查目标架构的Python环境
3. 某些平台可能需要特殊的编译环境

## 文件大小

典型的文件大小（仅供参考）：
- macOS: 15-25MB
- Linux: 15-25MB
- Windows: 20-30MB

## 注意事项

1. 首次运行可能需要较长时间（解压内部文件）
2. 杀毒软件可能会误报，请添加信任
3. 确保网络连接正常（程序需要访问API）
4. 建议在目标平台上测试运行
