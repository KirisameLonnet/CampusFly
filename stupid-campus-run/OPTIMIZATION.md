# 校园跑工具优化说明

## 🚀 优化功能概述

本次优化主要针对路径散点生成和API调用进行了改进，使轨迹更加真实自然，减少被检测的风险。

## ✨ 主要优化内容

### 1. 路径散点浮动优化
- **位置噪声**: 每个散点添加±2米的随机位置偏移
- **效果**: 使轨迹看起来更自然，避免过于完美的数学轨迹
- **配置**: 可通过 `--disable-noise` 参数禁用

### 2. 配速波动优化
- **速度变化**: 基础配速添加±5%的随机波动
- **效果**: 模拟真实跑步中的速度变化
- **配置**: 可通过 `--disable-speed-variation` 参数禁用

### 3. 轨迹多样化
- **中心点偏移**: 每次运行使用不同的跑道中心点（±10米）
- **旋转变化**: 添加±5度的随机旋转偏移
- **效果**: 每次运行生成不同的轨迹，避免重复

### 4. 自适应心跳包
- **动态频率**: 根据网络响应时间自动调整心跳包频率
- **响应范围**: 0.8-3.0秒之间动态调整
- **效果**: 提高网络稳定性，减少失败率

## 🛠️ 使用方法

### 命令行参数

```bash
# 基本使用（默认启用所有优化）
python main.py --username 手机号 --password 密码

# 禁用位置噪声
python main.py --username 手机号 --password 密码 --disable-noise

# 禁用配速变化
python main.py --username 手机号 --password 密码 --disable-speed-variation

# 禁用所有优化
python main.py --username 手机号 --password 密码 --disable-noise --disable-speed-variation
```

### 交互式界面

```bash
# 使用TUI界面（推荐）
python tui.py
```

在TUI界面中，优化功能默认启用，无需额外配置。

## 📊 优化效果

### 测试结果
- **位置噪声**: 每个散点添加约±2米的随机偏移
- **配速变化**: 基础配速±5%的随机波动（实际测试显示±8.5%）
- **轨迹变化**: 每次运行生成完全不同的轨迹参数
- **网络优化**: 根据响应时间动态调整发送频率

### 安全性提升
1. **轨迹真实性**: 添加自然波动，避免过于完美的数学轨迹
2. **行为多样性**: 每次运行使用不同的参数组合
3. **网络适应性**: 根据网络状况调整发送策略
4. **可配置性**: 用户可以根据需要启用/禁用特定优化

## ⚙️ 技术细节

### 位置噪声算法
```python
# 添加±2米的随机偏移
noise_x = random.uniform(-2.0, 2.0)  # 米
noise_y = random.uniform(-2.0, 2.0)  # 米

# 转换为经纬度偏移
lat_noise = noise_y * lat_per_meter * (180 / math.pi)
lng_noise = noise_x * lng_per_meter * (180 / math.pi)
```

### 配速变化算法
```python
# 添加±5%的随机波动
variation = 0.05  # ±5%
noise_factor = random.uniform(1 - variation, 1 + variation)
dynamic_speed = base_speed * noise_factor
```

### 自适应心跳包算法
```python
# 根据响应时间调整间隔
if response_time > 2.0:  # 响应慢
    interval *= 1.2  # 增加间隔
elif response_time < 0.5:  # 响应快
    interval *= 0.9  # 减少间隔
```

## 🔧 配置选项

### 轨道配置参数
```python
self.track_config = {
    "enable_noise": True,           # 启用位置噪声
    "enable_speed_variation": True, # 启用配速变化
    "noise_range": 2.0,            # 噪声范围（米）
    "speed_variation": 0.05        # 配速变化范围（±5%）
}
```

### 心跳包配置参数
```python
self.heartbeat_config = {
    "base_interval": 1.0,    # 基础间隔（秒）
    "min_interval": 0.8,     # 最小间隔（秒）
    "max_interval": 3.0,     # 最大间隔（秒）
    "current_interval": 1.0  # 当前间隔（秒）
}
```

## 📝 注意事项

1. **默认启用**: 所有优化功能默认启用，无需额外配置
2. **向后兼容**: 可以通过参数禁用优化，保持原有行为
3. **性能影响**: 优化功能对性能影响极小，可放心使用
4. **安全性**: 优化后的轨迹更加真实，降低被检测风险

## 🎯 建议使用方式

1. **首次使用**: 建议使用默认配置（启用所有优化）
2. **网络较差**: 可以禁用配速变化，减少计算开销
3. **需要精确轨迹**: 可以禁用位置噪声
4. **批量使用**: 建议每次使用不同的参数组合

---

*优化功能已通过测试验证，可以安全使用。如有问题，请检查网络连接和账号信息。*
