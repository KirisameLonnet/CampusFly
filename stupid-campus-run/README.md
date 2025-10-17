## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd stupid-campus-run
```

### 2. 创建虚拟环境
```bash
python -m venv venv
```

### 3. 激活虚拟环境
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 运行程序

#### 命令行模式
```bash
python main.py --username 手机号 --password 密码 --distance 5000
```

#### 交互式界面
```bash
python tui.py
```

## 参数说明

- `--username`: 华体运动会账号（手机号）
- `--password`: 账号密码
- `--distance`: 目标距离（米，默认5000）
- `--school`: 学校选择（上海大学/上海中医药大学，默认上海大学）
- `--mode`: 轨迹模式（track/random，默认track）

## 使用示例

```bash
# 使用交互式界面
python tui.py
```

## 注意事项

- 请确保网络连接正常
- 请确保有有效的体测计划
- 请遵守学校相关规定
- 程序仅用于学习和研究目的

## 项目结构

```
stupid-campus-run/
├── main.py          # 核心逻辑
├── tui.py           # 交互式界面
├── config_manager.py # 配置管理
├── requirements.txt  # 依赖列表
└── README.md        # 说明文档
```

本项目中不少内容借鉴了 [FitnessResolver](https://github.com/ThunderEnvoy/FitnessResolver) 基于tarui的项目，做的相当好

## 许可证

本项目完全用于学习逆向工程和网络安全，不可以用于校园跑等任何用途，遵循GPLv3
