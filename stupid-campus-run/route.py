"""
路线生成模块
包含跑道轨迹计算、距离计算等路线相关功能
实现三层模拟系统：
1. 几何模型层 - 标准跑道模型
2. 真实行为层 - 模拟人的真实跑步行为（状态、速度变化、变道、转弯习惯）
3. GPS传感器层 - 模拟GPS噪声、漂移、采样率
"""

import math
import random
from typing import Dict, Tuple, List
from enum import Enum
import time


class RunnerState(Enum):
    """跑者状态枚举"""
    RUNNING = "running"      # 跑步
    JOGGING = "jogging"      # 慢跑
    WALKING = "walking"      # 走路
    RESTING = "resting"      # 休息


class PerlinNoise:
    """柏林噪声生成器，用于平滑的随机漂移"""
    
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm *= 2
    
    def fade(self, t):
        """平滑插值函数"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, t, a, b):
        """线性插值"""
        return a + t * (b - a)
    
    def grad(self, hash_val, x):
        """梯度函数"""
        h = hash_val & 15
        grad = 1 + (h & 7)
        if h & 8:
            grad = -grad
        return grad * x
    
    def noise(self, x):
        """一维柏林噪声"""
        X = int(x) & 255
        x -= int(x)
        u = self.fade(x)
        return self.lerp(u, self.grad(self.perm[X], x), self.grad(self.perm[X + 1], x - 1))


class TrackGeometry:
    """第一层：跑道几何模型"""
    
    def __init__(self, straight_length=84.39, band_radius=36.5, rotation=90):
        """
        初始化跑道几何模型
        
        Args:
            straight_length: 直道长度（米）
            band_radius: 弯道半径（米）
            rotation: 跑道旋转角度（度）
        """
        self.straight_length = straight_length
        self.band_radius = band_radius
        self.rotation = rotation
        self.band_circumference = math.pi * band_radius
        self.total_circumference = 2 * straight_length + 2 * self.band_circumference
    
    def get_position_on_track(self, distance: float, lane_radius_offset: float = 0) -> Tuple[float, float]:
        """
        根据距离和车道偏移计算跑道上的位置（未旋转的局部坐标）
        
        Args:
            distance: 累计跑步距离（米）
            lane_radius_offset: 车道半径偏移（米，正值向外道，负值向内道）
            
        Returns:
            (x, y) 局部坐标（米）
        """
        distance = distance % self.total_circumference
        effective_radius = self.band_radius + lane_radius_offset
        
        x, y = 0, 0
        
        if distance <= self.straight_length:
            # 阶段1：右侧直道
            x = self.straight_length / 2 - distance
            y = -effective_radius
        elif distance <= self.straight_length + self.band_circumference:
            # 阶段2：上弯道
            arc_distance = distance - self.straight_length
            angle = arc_distance / self.band_radius
            x = -self.straight_length / 2 - effective_radius * math.sin(angle)
            y = -effective_radius * math.cos(angle)
        elif distance <= 2 * self.straight_length + self.band_circumference:
            # 阶段3：左侧直道
            straight2_distance = distance - (self.straight_length + self.band_circumference)
            x = -self.straight_length / 2 + straight2_distance
            y = effective_radius
        else:
            # 阶段4：下弯道
            arc_distance = distance - (2 * self.straight_length + self.band_circumference)
            angle = arc_distance / self.band_radius
            x = self.straight_length / 2 + effective_radius * math.sin(angle)
            y = effective_radius * math.cos(angle)
        
        return x, y
    
    def is_in_curve(self, distance: float) -> bool:
        """判断是否在弯道上"""
        distance = distance % self.total_circumference
        return (self.straight_length < distance <= self.straight_length + self.band_circumference) or \
               (distance > 2 * self.straight_length + self.band_circumference)
    
    def get_curve_exit_point(self, distance: float) -> float:
        """获取弯道出口点的距离"""
        distance = distance % self.total_circumference
        if self.straight_length < distance <= self.straight_length + self.band_circumference:
            # 上弯道，出口在左直道起点
            return self.straight_length + self.band_circumference
        else:
            # 下弯道，出口在右直道起点（即0点）
            return 0 if distance > 2 * self.straight_length + self.band_circumference else distance


class RealisticRunner:
    """第二层：真实人类行为模拟"""
    
    def __init__(self, track_geometry: TrackGeometry, base_speed=2.56):
        """
        初始化跑者模拟
        
        Args:
            track_geometry: 跑道几何模型
            base_speed: 基础速度（米/秒，默认约6.5分钟/公里）
        """
        self.track = track_geometry
        self.base_speed = base_speed
        
        # 状态相关
        self.state = RunnerState.RUNNING
        self.state_time = 0  # 当前状态持续时间
        self.state_durations = {
            RunnerState.RUNNING: (180, 420),   # 跑步：3-7分钟（保持更长时间）
            RunnerState.JOGGING: (15, 40),     # 慢跑：15-40秒
            RunnerState.WALKING: (5, 15),      # 走路：5-15秒（很短）
            RunnerState.RESTING: (10, 30)      # 休息：10-30秒（在3-5圈时触发）
        }
        self.next_state_change = random.uniform(*self.state_durations[self.state])
        
        # 速度相关 - 重新设计速度倍率
        # 基础速度：2.56 m/s (6.5 min/km)
        # 目标速度范围：
        #   - RUNNING: 4-5 min/km = 3.33-4.17 m/s (倍率: 1.30-1.63)
        #   - JOGGING: 5-6 min/km = 2.78-3.33 m/s (倍率: 1.08-1.30)
        #   - WALKING: 6-8 min/km = 2.08-2.78 m/s (倍率: 0.81-1.08)
        #   - RESTING: 0 m/s (完全停止)
        self.speed_multipliers = {
            RunnerState.RUNNING: 1.45,         # 平均4.5 min/km (约3.70 m/s)
            RunnerState.JOGGING: 1.15,         # 平均5.7 min/km (约2.94 m/s)
            RunnerState.WALKING: 0.85,         # 平均7.6 min/km (约2.18 m/s)
            RunnerState.RESTING: 0.0           # 完全停止
        }
        
        # 位置和距离
        self.true_x = 0
        self.true_y = 0
        self.cumulative_distance = 0
        
        # 起点到跑道的走路阶段
        self.walking_to_track = True  # 是否正在走向跑道
        self.start_position = None  # 起点位置（局部坐标）
        self.track_entry_position = None  # 跑道入口位置（局部坐标）
        self.walking_progress = 0  # 走向跑道的进度（0-1）
        self.walking_path_points = []  # 走向跑道的路径点
        self._initialize_start_position()
        
        # 车道漂移（柏林噪声）
        self.lane_noise = PerlinNoise(seed=int(time.time()))
        self.lane_offset = 0  # 当前车道偏移（米）
        self.target_lane_offset = 0  # 目标车道偏移（米）
        self.lane_change_speed = 0.15  # 换道速度（米/秒）
        self.lane_change_timer = 0  # 换道计时器
        self.next_lane_change_time = random.uniform(15, 45)  # 下次换道时间（秒）
        self.preferred_lane = random.choice([-1.5, -0.5, 0.5, 1.5])  # 偏好的跑道位置（米）
        
        # 每圈主要跑道选择
        self.current_lap = 0
        self.lap_main_lane = random.choice([-1.5, -0.5, 0.5, 1.5])  # 本圈主要跑道
        self.last_lap_distance = 0  # 上一圈的距离
        
        # 转弯行为
        self.curve_bias = -0.5  # 弯道内侧偏移（米）
        
        # 抄近道
        self.cutting_corner = False
        self.corner_start_pos = None
        self.corner_target_pos = None
        self.corner_progress = 0
        self.corner_path_points = []  # 抄近道的曲线路径点
        self.corner_cut_probability = 0.025  # 提高到2.5%概率（每圈约25%概率，即1/4）
        self.last_corner_cut_distance = -1000  # 上次抄近道的距离，避免频繁抄近道
        
        # 随机抄近道描述列表
        self.corner_cut_descriptions = [
            "鼠鼠偷懒",
            "鼠鼠少跑点",
            "鼠鼠开小差",
            "鼠鼠耍滑头",
        ]
        
        # 随机休息机制（3-5圈时触发）
        self.rest_enabled = False  # 是否启用休息
        self.rest_trigger_laps = random.randint(3, 5)  # 随机选择在第几圈触发休息
        self.rest_triggered_this_lap = False  # 本圈是否已触发休息
        self.has_rested_ever = False  # 是否已经休息过（整个跑步过程只休息一次）
        
        # 配速监控（确保不超过8分钟/公里 = 2.08米/秒）
        self.total_time = 0  # 总时间（秒）
        self.pace_check_interval = 10  # 每10秒检查一次配速（更频繁）
        self.last_pace_check_time = 0
        self.target_min_speed = 1000 / 8 / 60  # 8分钟/公里 = 2.08米/秒（最低速度）
        self.target_avg_speed = 1000 / 5 / 60  # 5分钟/公里 = 3.33米/秒（目标平均速度）
    
    def _initialize_start_position(self):
        """初始化起点位置（在跑道直边外侧）"""
        # 选择一条直道作为入口点（右直道或左直道）
        use_right_straight = random.choice([True, False])
        
        if use_right_straight:
            # 右侧直道（起跑点在直道中段）
            entry_distance = random.uniform(0.2, 0.8) * self.track.straight_length
            entry_x = self.track.straight_length / 2 - entry_distance
            entry_y = -self.track.band_radius
            
            # 起点在跑道外侧 5-15 米
            offset_distance = random.uniform(5, 15)
            self.start_position = (entry_x, entry_y - offset_distance)
            self.track_entry_position = (entry_x, entry_y)
        else:
            # 左侧直道
            entry_distance = random.uniform(0.2, 0.8) * self.track.straight_length
            entry_x = -self.track.straight_length / 2 + entry_distance
            entry_y = self.track.band_radius
            
            # 起点在跑道外侧 5-15 米
            offset_distance = random.uniform(5, 15)
            self.start_position = (entry_x, entry_y + offset_distance)
            self.track_entry_position = (entry_x, entry_y)
        
        # 设置初始位置
        self.true_x, self.true_y = self.start_position
        
        # 生成从起点到跑道的自然路径（带噪声）
        self._generate_walking_path()
        
        print(f"📍 起点位置: ({self.start_position[0]:.1f}, {self.start_position[1]:.1f})")
        print(f"🎯 跑道入口: ({self.track_entry_position[0]:.1f}, {self.track_entry_position[1]:.1f})")
    
    def _generate_walking_path(self):
        """生成从起点走到跑道的自然路径（使用贝塞尔曲线+噪声）"""
        start = self.start_position
        end = self.track_entry_position
        
        # 计算中间控制点
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # 添加随机偏移使路径更自然
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            # 垂直于起点-终点连线的方向
            perp_x = -dy / dist
            perp_y = dx / dist
            
            # 控制点偏移（随机左右偏移）
            offset = random.uniform(-dist * 0.15, dist * 0.15)
            control_x = mid_x + perp_x * offset
            control_y = mid_y + perp_y * offset
        else:
            control_x = mid_x
            control_y = mid_y
        
        # 生成贝塞尔曲线路径点，并添加噪声
        self.walking_path_points = []
        num_points = 30
        for i in range(num_points + 1):
            t = i / num_points
            # 二次贝塞尔曲线
            x = (1-t)**2 * start[0] + 2*(1-t)*t * control_x + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * control_y + t**2 * end[1]
            
            # 添加噪声（模拟走路时的左右摇摆）
            noise_x = random.gauss(0, 0.3)
            noise_y = random.gauss(0, 0.3)
            
            self.walking_path_points.append((x + noise_x, y + noise_y))
    
    def update(self, dt: float = 0.1):
        """
        更新跑者状态和位置（高频率调用，如每0.1秒）
        
        Args:
            dt: 时间步长（秒）
        """
        # 0. 如果正在走向跑道，使用慢速移动
        if self.walking_to_track:
            self._update_walking_to_track(dt)
            return  # 走向跑道阶段不执行正常跑步逻辑
        
        # 0. 更新总时间
        self.total_time += dt
        
        # 1. 实时配速检查（每10秒检查一次，立即响应配速过慢）
        if self.total_time - self.last_pace_check_time >= self.pace_check_interval:
            self.last_pace_check_time = self.total_time
            # 确保有足够的数据进行评估（至少跑了30秒）
            if self.total_time > 30 and self.cumulative_distance > 0:
                current_avg_speed = self.cumulative_distance / self.total_time
                current_pace = (self.total_time / 60) / (self.cumulative_distance / 1000) if self.cumulative_distance > 0 else 0
                
                # 如果平均速度低于2.08米/秒（8分钟/公里），立即强制切换到RUNNING
                if current_avg_speed < self.target_min_speed:
                    if self.state != RunnerState.RUNNING:
                        self.state = RunnerState.RUNNING
                        self.state_time = 0
                        self.next_state_change = random.uniform(*self.state_durations[self.state])
                        print(f"⚡ 配速过慢 ({current_pace:.1f} min/km)，立即切换到跑步状态")
                
                # 如果速度低于目标平均速度，倾向于保持RUNNING状态
                elif current_avg_speed < self.target_avg_speed:
                    # 如果是WALKING或RESTING，切换到JOGGING或RUNNING
                    if self.state in [RunnerState.WALKING, RunnerState.RESTING]:
                        self.state = random.choice([RunnerState.JOGGING, RunnerState.RUNNING])
                        self.state_time = 0
                        self.next_state_change = random.uniform(*self.state_durations[self.state])
        
        # 2. 检查是否触发随机休息（在指定圈数时）
        current_lap = int(self.cumulative_distance / self.track.total_circumference)
        if not self.has_rested_ever and current_lap == self.rest_trigger_laps:
            # 在这一圈的随机位置休息
            distance_in_lap = self.cumulative_distance % self.track.total_circumference
            
            # 如果还没标记本圈触发过，且在直道区域（便于休息）
            if not self.rest_triggered_this_lap:
                # 在直道的30%-70%位置随机触发休息（5%概率每次检查）
                if distance_in_lap <= self.track.straight_length:
                    # 右侧直道
                    straight_progress = distance_in_lap / self.track.straight_length
                    if 0.3 <= straight_progress <= 0.7 and random.random() < 0.05 * dt:
                        self._trigger_rest()
                elif self.track.straight_length + self.track.band_circumference < distance_in_lap <= 2 * self.track.straight_length + self.track.band_circumference:
                    # 左侧直道
                    straight_distance = distance_in_lap - (self.track.straight_length + self.track.band_circumference)
                    straight_progress = straight_distance / self.track.straight_length
                    if 0.3 <= straight_progress <= 0.7 and random.random() < 0.05 * dt:
                        self._trigger_rest()
        
        # 3. 更新状态
        self.state_time += dt
        if self.state_time >= self.next_state_change:
            self._change_state()
        
        # 4. 计算当前速度
        current_speed = self.base_speed * self.speed_multipliers[self.state]
        # 添加微小的速度波动
        speed_variation = 1.0 + random.uniform(-0.05, 0.05)
        current_speed *= speed_variation
        
    def _update_walking_to_track(self, dt: float):
        """更新走向跑道的过程"""
        # 计算路径总长度
        total_distance = 0
        for i in range(len(self.walking_path_points) - 1):
            dx = self.walking_path_points[i+1][0] - self.walking_path_points[i][0]
            dy = self.walking_path_points[i+1][1] - self.walking_path_points[i][1]
            total_distance += math.sqrt(dx**2 + dy**2)
        
        # 走路速度（慢速，约2公里/小时 = 0.56米/秒）
        walking_speed = 0.56
        
        # 更新进度
        if total_distance > 0:
            self.walking_progress += (walking_speed * dt) / total_distance
        
        if self.walking_progress >= 1.0:
            # 到达跑道，开始正式跑步
            self.walking_to_track = False
            self.true_x, self.true_y = self.track_entry_position
            print(f"✅ 到达跑道，开始跑步！")
        else:
            # 根据进度在路径上插值
            target_index = int(self.walking_progress * (len(self.walking_path_points) - 1))
            target_index = min(target_index, len(self.walking_path_points) - 1)
            
            if target_index < len(self.walking_path_points) - 1:
                # 在两个点之间插值
                p1 = self.walking_path_points[target_index]
                p2 = self.walking_path_points[target_index + 1]
                local_progress = (self.walking_progress * (len(self.walking_path_points) - 1)) - target_index
                
                self.true_x = p1[0] + (p2[0] - p1[0]) * local_progress
                self.true_y = p1[1] + (p2[1] - p1[1]) * local_progress
            else:
                self.true_x, self.true_y = self.walking_path_points[target_index]
    
    def _trigger_rest(self):
            can_cut = False
            
            # 情况1：在弯道中段（25%-75%位置）
            if self.track.is_in_curve(self.cumulative_distance):
                if self.track.straight_length < distance_in_lap <= self.track.straight_length + self.track.band_circumference:
                    # 上弯道
                    curve_progress = (distance_in_lap - self.track.straight_length) / self.track.band_circumference
                else:
                    # 下弯道
                    curve_progress = (distance_in_lap - 2 * self.track.straight_length - self.track.band_circumference) / self.track.band_circumference
                
                if 0.25 <= curve_progress <= 0.75:
                    can_cut = True
            
            # 情况2：在直道中段（20%-80%位置）- 可以斜穿到对面
            else:
                if distance_in_lap <= self.track.straight_length:
                    # 右侧直道
                    straight_progress = distance_in_lap / self.track.straight_length
                    if 0.2 <= straight_progress <= 0.8:
                        can_cut = True
                elif self.track.straight_length + self.track.band_circumference < distance_in_lap <= 2 * self.track.straight_length + self.track.band_circumference:
                    # 左侧直道
                    straight_distance = distance_in_lap - (self.track.straight_length + self.track.band_circumference)
                    straight_progress = straight_distance / self.track.straight_length
                    if 0.2 <= straight_progress <= 0.8:
                        can_cut = True
            
            # 触发抄近道
            if can_cut and random.random() < self.corner_cut_probability * dt:
                self._start_cutting_corner()
        
        # 7. 更新位置
        if self.cutting_corner:
            self._update_cutting_corner(dt, distance_delta)
        else:
            self._update_normal_position()
    
    def _trigger_rest(self):
        """触发休息"""
        self.state = RunnerState.RESTING
        self.state_time = 0
        self.next_state_change = random.uniform(*self.state_durations[RunnerState.RESTING])
        self.rest_triggered_this_lap = True
        self.has_rested_ever = True
        
        current_lap = int(self.cumulative_distance / self.track.total_circumference) + 1
        rest_duration = self.next_state_change
        print(f"💤 第{current_lap}圈，鼠鼠累了，休息 {rest_duration:.0f} 秒...")
    
    def _change_state(self):
        """切换跑者状态 - 保持4-5分钟/公里的配速，偶尔降到8分钟/公里"""
        # 状态转换概率权重（大幅倾向于保持在RUNNING状态）
        if self.state == RunnerState.RUNNING:
            # RUNNING状态：90%继续跑，8%慢跑，2%走路（很少走路）
            self.state = random.choices(
                [RunnerState.RUNNING, RunnerState.JOGGING, RunnerState.WALKING],
                weights=[90, 8, 2]
            )[0]
        elif self.state == RunnerState.JOGGING:
            # JOGGING状态：80%回到跑步，18%继续慢跑，2%走路
            self.state = random.choices(
                [RunnerState.RUNNING, RunnerState.JOGGING, RunnerState.WALKING],
                weights=[80, 18, 2]
            )[0]
        elif self.state == RunnerState.WALKING:
            # WALKING状态：85%立即回到跑步，15%慢跑（绝不自动进入休息）
            self.state = random.choices(
                [RunnerState.RUNNING, RunnerState.JOGGING],
                weights=[85, 15]
            )[0]
        else:  # RESTING - 休息结束后立即恢复跑步
            # 休息结束，立即切换到跑步状态
            self.state = RunnerState.RUNNING
            print(f"💪 休息结束，鼠鼠继续跑！")
        
        self.state_time = 0
        self.next_state_change = random.uniform(*self.state_durations[self.state])
    
    def _update_lane_offset(self, dt: float):
        """更新车道偏移（模拟无意识漂移和有意识换道）"""
        # 检查是否换圈，如果换圈则选择新的主跑道
        current_lap = int(self.cumulative_distance / self.track.total_circumference)
        if current_lap > self.current_lap:
            self.current_lap = current_lap
            # 选择新的主跑道（每圈随机，范围更大：-3米到+3米）
            # 使用更大的范围来增加每圈差异
            lane_options = [-3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
            self.lap_main_lane = random.choice(lane_options)
            self.preferred_lane = self.lap_main_lane
            
            # 随机决定是否启用更激进的弯道策略（有时贴内道，有时正常）
            self.curve_bias = random.choice([-1.2, -0.8, -0.5, -0.3])
            
            print(f"🔄 第{self.current_lap + 1}圈，主跑道: {self.lap_main_lane:.1f}米，弯道策略: {self.curve_bias:.1f}米")
        
        # 更新换道计时器
        self.lane_change_timer += dt
        
        # 定期在主跑道附近微调（模拟跑者在主跑道附近移动，范围扩大）
        if self.lane_change_timer >= self.next_lane_change_time:
            # 在主跑道附近±1.0米范围内随机移动（扩大变化范围）
            self.preferred_lane = self.lap_main_lane + random.uniform(-1.0, 1.0)
            
            # 重置计时器
            self.lane_change_timer = 0
            self.next_lane_change_time = random.uniform(15, 40)  # 15-40秒后再次微调
        
        # 无意识漂移（柏林噪声，范围扩大到±0.4米）
        noise_value = self.lane_noise.noise(self.cumulative_distance * 0.05)
        unconscious_drift = noise_value * 0.4
        
        # 弯道偏移（向内侧靠）
        curve_offset = 0
        if self.track.is_in_curve(self.cumulative_distance):
            curve_offset = self.curve_bias
        
        # 目标偏移 = 偏好跑道 + 无意识漂移 + 弯道偏移
        self.target_lane_offset = self.preferred_lane + unconscious_drift + curve_offset
        
        # 平滑过渡到目标偏移
        if abs(self.lane_offset - self.target_lane_offset) > 0.01:
            direction = 1 if self.target_lane_offset > self.lane_offset else -1
            self.lane_offset += direction * self.lane_change_speed * dt
        
        # 限制在合理范围（外道最多+3.5米，内道最多-3.5米）
        self.lane_offset = max(-3.5, min(3.5, self.lane_offset))
    
    def _start_cutting_corner(self):
        """开始抄近道"""
        self.cutting_corner = True
        self.corner_progress = 0
        
        # 记录当前位置作为起点
        self.corner_start_pos = (self.true_x, self.true_y)
        
        # 判断当前是在弯道还是直道
        distance_in_lap = self.cumulative_distance % self.track.total_circumference
        is_in_curve = self.track.is_in_curve(self.cumulative_distance)
        
        if is_in_curve:
            # 弯道抄近道：跳过部分弯道
            remaining_curve = (self.track.get_curve_exit_point(self.cumulative_distance) - distance_in_lap)
            if remaining_curve < 0:
                remaining_curve += self.track.total_circumference
            
            # 抄近道跳过30%-60%的弯道距离
            cut_ratio = random.uniform(0.3, 0.6)
            target_distance = self.cumulative_distance + remaining_curve * cut_ratio
            
            # 目标点偏向内侧
            exit_x, exit_y = self.track.get_position_on_track(target_distance, self.lane_offset * 0.4)
            self.corner_target_pos = (exit_x, exit_y)
            
        else:
            # 直道抄近道：斜穿到前方不同跑道位置
            # 跳过20-50米的距离
            skip_distance = random.uniform(20, 50)
            target_distance = self.cumulative_distance + skip_distance
            
            # 切换到不同的跑道（随机选择内侧或外侧）
            lane_offset_change = random.choice([-2.5, -2.0, -1.5, 1.5, 2.0, 2.5])
            target_lane_offset = max(-3.5, min(3.5, self.lane_offset + lane_offset_change))
            
            exit_x, exit_y = self.track.get_position_on_track(target_distance, target_lane_offset)
            self.corner_target_pos = (exit_x, exit_y)
        
        # 生成曲线路径点（贝塞尔曲线）
        self._generate_corner_cut_curve()
        
        # 记录抄近道位置
        self.last_corner_cut_distance = self.cumulative_distance
        
        # 随机选择抄近道描述
        description = random.choice(self.corner_cut_descriptions)
        location_type = "弯道" if is_in_curve else "直道"
        print(f"🏃 {description}中...（{location_type}）")
    
    def _generate_corner_cut_curve(self):
        """生成抄近道的曲线路径（贝塞尔曲线）"""
        start = self.corner_start_pos
        end = self.corner_target_pos
        
        # 计算中间控制点，使路径呈曲线
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # 添加随机偏移使曲线更自然
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            # 垂直于起点-终点连线的方向
            perp_x = -dy / dist
            perp_y = dx / dist
            
            # 控制点偏移（向内侧或外侧，随机）
            offset = random.uniform(-dist * 0.2, dist * 0.1)
            control_x = mid_x + perp_x * offset
            control_y = mid_y + perp_y * offset
        else:
            control_x = mid_x
            control_y = mid_y
        
        # 生成贝塞尔曲线路径点
        self.corner_path_points = []
        num_points = 50
        for i in range(num_points + 1):
            t = i / num_points
            # 二次贝塞尔曲线公式
            x = (1-t)**2 * start[0] + 2*(1-t)*t * control_x + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * control_y + t**2 * end[1]
            self.corner_path_points.append((x, y))
    
    def _update_cutting_corner(self, dt: float, distance_delta: float):
        """更新抄近道过程中的位置（沿曲线）"""
        # 计算总路径长度（近似）
        total_distance = 0
        for i in range(len(self.corner_path_points) - 1):
            dx = self.corner_path_points[i+1][0] - self.corner_path_points[i][0]
            dy = self.corner_path_points[i+1][1] - self.corner_path_points[i][1]
            total_distance += math.sqrt(dx**2 + dy**2)
        
        # 更新进度
        if total_distance > 0:
            self.corner_progress += distance_delta / total_distance
        
        if self.corner_progress >= 1.0:
            # 完成抄近道，回到跑道
            self.cutting_corner = False
            self.true_x, self.true_y = self.corner_target_pos
        else:
            # 根据进度在曲线上插值
            target_index = int(self.corner_progress * (len(self.corner_path_points) - 1))
            target_index = min(target_index, len(self.corner_path_points) - 1)
            
            if target_index < len(self.corner_path_points) - 1:
                # 在两个点之间插值
                p1 = self.corner_path_points[target_index]
                p2 = self.corner_path_points[target_index + 1]
                local_progress = (self.corner_progress * (len(self.corner_path_points) - 1)) - target_index
                
                self.true_x = p1[0] + (p2[0] - p1[0]) * local_progress
                self.true_y = p1[1] + (p2[1] - p1[1]) * local_progress
            else:
                self.true_x, self.true_y = self.corner_path_points[target_index]
            

    
    def _update_normal_position(self):
        """更新正常跑步时的位置"""
        self.true_x, self.true_y = self.track.get_position_on_track(
            self.cumulative_distance, 
            self.lane_offset
        )
    
    def get_position(self) -> Tuple[float, float]:
        """获取当前真实位置"""
        return self.true_x, self.true_y


class GPSSensor:
    """第三层：GPS传感器模拟"""
    
    def __init__(self, sampling_rate=1.0, noise_std=4.5, drift_factor=0.95):
        """
        初始化GPS传感器模拟
        
        Args:
            sampling_rate: 采样率（秒，默认1Hz）
            noise_std: GPS噪声标准差（米）- 增大到4.5米
            drift_factor: 漂移因子（0-1，越大漂移越明显）- 提高到0.95
        """
        self.sampling_rate = sampling_rate
        self.noise_std = noise_std
        self.drift_factor = drift_factor
        
        # 上次采样时间
        self.last_sample_time = 0
        
        # 漂移状态（保持噪声的自相关性）
        self.noise_x = 0
        self.noise_y = 0
        
        # 长期漂移（模拟卫星位置变化导致的系统性偏移）
        self.long_term_drift_x = random.gauss(0, 2.0)  # 初始长期漂移
        self.long_term_drift_y = random.gauss(0, 2.0)
        self.drift_change_timer = 0
        self.next_drift_change = random.uniform(30, 120)  # 30-120秒后漂移方向改变
    
    def should_sample(self, current_time: float) -> bool:
        """判断是否应该采样"""
        if current_time - self.last_sample_time >= self.sampling_rate:
            self.last_sample_time = current_time
            
            # 更新长期漂移（模拟卫星位置变化）
            self.drift_change_timer += self.sampling_rate
            if self.drift_change_timer >= self.next_drift_change:
                # 漂移方向缓慢改变
                self.long_term_drift_x += random.gauss(0, 0.5)
                self.long_term_drift_y += random.gauss(0, 0.5)
                # 限制漂移范围
                self.long_term_drift_x = max(-5, min(5, self.long_term_drift_x))
                self.long_term_drift_y = max(-5, min(5, self.long_term_drift_y))
                
                self.drift_change_timer = 0
                self.next_drift_change = random.uniform(30, 120)
            
            return True
        return False
    
    def get_gps_reading(self, true_x: float, true_y: float) -> Tuple[float, float]:
        """
        获取GPS读数（添加噪声和漂移）
        
        Args:
            true_x: 真实X坐标
            true_y: 真实Y坐标
            
        Returns:
            (gps_x, gps_y) GPS读数
        """
        # 生成新的随机噪声（短期波动）
        new_noise_x = random.gauss(0, self.noise_std)
        new_noise_y = random.gauss(0, self.noise_std)
        
        # 应用自相关漂移（短期）- 使噪声"记忆"上一次的值
        self.noise_x = self.drift_factor * self.noise_x + (1 - self.drift_factor) * new_noise_x
        self.noise_y = self.drift_factor * self.noise_y + (1 - self.drift_factor) * new_noise_y
        
        # 返回带噪声的GPS读数 = 真实位置 + 长期漂移 + 短期漂移
        gps_x = true_x + self.long_term_drift_x + self.noise_x
        gps_y = true_y + self.long_term_drift_y + self.noise_y
        
        return gps_x, gps_y


class RouteGenerator:
    """路线生成器类（整合三层模型）"""
    
    def __init__(self, track_config: Dict = None):
        """
        初始化路线生成器
        
        Args:
            track_config: 跑道配置参数
        """
        # 默认跑道配置
        self.track_config = track_config or {
            "center_lat": (31.318217 + 31.31997) / 2,  # 跑道中心纬度
            "center_lng": (121.392548 + 121.393845) / 2,  # 跑道中心经度
            "straight_length": 84.39,  # 直道长度（米）
            "band_radius": 36.5,  # 弯道半径（米）
            "total_circumference": 400,  # 总周长（米）
            "speed": 1000 / 6.5 / 60,  # 配速6.5分钟/公里（米/秒）
            "rotation": 90,  # 跑道旋转角度（度）
            "enable_realistic_simulation": True,  # 启用真实三层模拟
            "gps_sampling_rate": 1.0,  # GPS采样率（秒）
            "gps_noise_std": 4.5,  # GPS噪声标准差（米）- 增大漂移
            "gps_drift_factor": 0.95,  # GPS漂移因子（0-1）- 提高自相关性
            "simulation_dt": 0.1,  # 模拟时间步长（秒）
        }
        
        # 初始化三层模型
        self.track_geometry = TrackGeometry(
            straight_length=self.track_config["straight_length"],
            band_radius=self.track_config["band_radius"],
            rotation=self.track_config["rotation"]
        )
        
        self.runner = RealisticRunner(
            track_geometry=self.track_geometry,
            base_speed=self.track_config["speed"]
        )
        
        self.gps_sensor = GPSSensor(
            sampling_rate=self.track_config["gps_sampling_rate"],
            noise_std=self.track_config["gps_noise_std"],
            drift_factor=self.track_config["gps_drift_factor"]
        )
        
        # 模拟时间
        self.simulation_time = 0
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        计算两个经纬度坐标之间的直线距离（米）- 完全按照FitnessResolver的算法
        使用Haversine公式
        
        Args:
            lat1: 起点纬度
            lng1: 起点经度
            lat2: 终点纬度
            lng2: 终点经度
            
        Returns:
            距离（米）
        """
        # 地球半径（米，WGS84椭球模型近似值）
        earth_radius = 6371000

        # 将角度转换为弧度
        rad_lat1 = (lat1 * math.pi) / 180
        rad_lng1 = (lng1 * math.pi) / 180
        rad_lat2 = (lat2 * math.pi) / 180
        rad_lng2 = (lng2 * math.pi) / 180

        # 计算纬度差和经度差
        delta_lat = rad_lat2 - rad_lat1
        delta_lng = rad_lng2 - rad_lng1

        # Haversine公式核心计算
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(rad_lat1) * math.cos(rad_lat2) * 
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # 距离 = 地球半径 × 圆心角（弧度）
        distance = earth_radius * c

        return round(distance, 2)
    
    def generate_realistic_route(self, duration: float) -> List[Dict]:
        """
        生成真实的跑步轨迹（使用三层模拟模型）
        
        Args:
            duration: 跑步总时长（秒）
            
        Returns:
            GPS采样点列表，每个点包含：
            {
                "latitude": 纬度,
                "longitude": 经度,
                "timestamp": 时间戳（秒）,
                "speed": 瞬时速度（米/秒）,
                "state": 跑者状态
            }
        """
        gps_points = []
        dt = self.track_config["simulation_dt"]
        
        # 重置模拟状态
        self.simulation_time = 0
        self.runner = RealisticRunner(
            track_geometry=self.track_geometry,
            base_speed=self.track_config["speed"]
        )
        self.gps_sensor = GPSSensor(
            sampling_rate=self.track_config["gps_sampling_rate"],
            noise_std=self.track_config["gps_noise_std"],
            drift_factor=self.track_config["gps_drift_factor"]
        )
        
        # 高频模拟循环
        while self.simulation_time < duration:
            # 更新跑者状态和位置
            self.runner.update(dt)
            
            # 检查是否需要GPS采样
            if self.gps_sensor.should_sample(self.simulation_time):
                # 获取真实位置
                true_x, true_y = self.runner.get_position()
                
                # 获取GPS读数（带噪声）
                gps_x, gps_y = self.gps_sensor.get_gps_reading(true_x, true_y)
                
                # 转换为经纬度
                lat, lng = self._local_to_latlon(gps_x, gps_y)
                
                # 记录GPS点
                gps_points.append({
                    "latitude": lat,
                    "longitude": lng,
                    "timestamp": self.simulation_time,
                    "speed": self.runner.base_speed * self.runner.speed_multipliers[self.runner.state],
                    "state": self.runner.state.value,
                    "distance": self.runner.cumulative_distance
                })
            
            # 推进时间
            self.simulation_time += dt
        
        return gps_points
    
    def _local_to_latlon(self, x: float, y: float) -> Tuple[float, float]:
        """
        将局部坐标（米）转换为经纬度
        
        Args:
            x: 局部X坐标（米）
            y: 局部Y坐标（米）
            
        Returns:
            (latitude, longitude)
        """
        center_lat = self.track_config["center_lat"]
        center_lng = self.track_config["center_lng"]
        rotation = self.track_config["rotation"]
        
        # 应用旋转
        rotation_rad = rotation * math.pi / 180
        cos_rot = math.cos(rotation_rad)
        sin_rot = math.sin(rotation_rad)
        x_rotated = x * cos_rot - y * sin_rot
        y_rotated = x * sin_rot + y * cos_rot
        
        # 转换为经纬度偏移
        earth_radius = 6378137
        rad_lat = center_lat * math.pi / 180
        lng_per_meter = 1 / (earth_radius * math.cos(rad_lat))
        lat_per_meter = 1 / earth_radius
        
        latitude = center_lat + (y_rotated * lat_per_meter) * (180 / math.pi)
        longitude = center_lng + (x_rotated * lng_per_meter) * (180 / math.pi)
        
        return latitude, longitude
    
    def get_route_statistics(self, gps_points: List[Dict]) -> Dict:
        """
        计算轨迹统计信息
        
        Args:
            gps_points: GPS采样点列表
            
        Returns:
            统计信息字典
        """
        if not gps_points:
            return {}
        
        total_distance = 0
        for i in range(1, len(gps_points)):
            dist = self.calculate_distance(
                gps_points[i-1]["latitude"],
                gps_points[i-1]["longitude"],
                gps_points[i]["latitude"],
                gps_points[i]["longitude"]
            )
            total_distance += dist
        
        duration = gps_points[-1]["timestamp"] - gps_points[0]["timestamp"]
        avg_speed = total_distance / duration if duration > 0 else 0
        
        # 统计各状态时间
        state_times = {state.value: 0 for state in RunnerState}
        for i in range(1, len(gps_points)):
            dt = gps_points[i]["timestamp"] - gps_points[i-1]["timestamp"]
            state = gps_points[i-1]["state"]
            if state in state_times:
                state_times[state] += dt
        
        return {
            "total_distance": round(total_distance, 2),
            "duration": round(duration, 2),
            "average_speed": round(avg_speed, 2),
            "average_pace": round(1000 / (avg_speed * 60), 2) if avg_speed > 0 else 0,  # 分钟/公里
            "point_count": len(gps_points),
            "state_times": state_times
        }
    
    def get_track_position_with_rotation(self, t: int, center_lat: float = None, center_lng: float = None,
                                        rotation: float = None, offset_x: float = 0, offset_y: float = 0,
                                        add_noise: bool = True) -> Dict:
        """
        兼容方法：支持旋转的跑道位置计算（兼容main.py的调用方式）
        使用三层模拟模型生成真实的轨迹
        
        Args:
            t: 跑步时间（秒）
            center_lat: 跑道中心纬度（可选，未使用 - 使用配置中的值）
            center_lng: 跑道中心经度（可选，未使用 - 使用配置中的值）
            rotation: 跑道旋转角度（可选，未使用 - 使用配置中的值）
            offset_x: X偏移（米，未使用）
            offset_y: Y偏移（米，未使用）
            add_noise: 是否使用真实模拟（默认True，总是启用三层模拟）
            
        Returns:
            {"latitude": 纬度, "longitude": 经度}
        """
        # 使用三层模拟系统
        dt = self.track_config.get("simulation_dt", 0.1)
        
        # 如果时间跳跃太大，需要更新模拟状态
        time_diff = abs(t - self.simulation_time)
        if time_diff > dt * 2:  # 时间跳跃超过2个步长
            # 快进模拟到目标时间
            while self.simulation_time < t:
                self.runner.update(dt)
                self.simulation_time += dt
        
        # 获取真实位置
        true_x, true_y = self.runner.get_position()
        
        # 获取GPS读数（带噪声和漂移）
        if self.gps_sensor.should_sample(self.simulation_time):
            gps_x, gps_y = self.gps_sensor.get_gps_reading(true_x, true_y)
        else:
            # 如果不在采样点，强制采样
            gps_x, gps_y = self.gps_sensor.get_gps_reading(true_x, true_y)
        
        # 转换为经纬度
        latitude, longitude = self._local_to_latlon(gps_x, gps_y)
        
        return {
            "latitude": latitude,
            "longitude": longitude
        }
