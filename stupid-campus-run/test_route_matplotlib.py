"""
使用 matplotlib 可视化测试 route.py 的跑圈路线结果
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np
from route import TrackGeometry, RealisticRunner


class TrackVisualizer:
    """跑道可视化工具 (使用 matplotlib)"""
    
    def __init__(self):
        """Initialize visualization tool"""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_aspect('equal')
        self.ax.set_title("Track Route Visualization Test", fontsize=16, fontweight='bold')
        self.ax.set_xlabel("X (meters)", fontsize=12)
        self.ax.set_ylabel("Y (meters)", fontsize=12)
        self.ax.grid(True, alpha=0.3)
        
        # 存储图形元素
        self.track_lines = []
        self.route_line = None
        self.runner_marker = None
        self.info_text = None
    
    def draw_track(self, track_geometry: TrackGeometry):
        """绘制跑道"""
        # 生成跑道轮廓点
        steps = 200
        
        # 内道
        inner_x, inner_y = [], []
        for i in range(steps + 1):
            distance = (i / steps) * track_geometry.total_circumference
            x, y = track_geometry.get_position_on_track(distance, 0)
            inner_x.append(x)
            inner_y.append(y)
        
        # 外道
        outer_x, outer_y = [], []
        for i in range(steps + 1):
            distance = (i / steps) * track_geometry.total_circumference
            x, y = track_geometry.get_position_on_track(distance, 1.22)  # 标准跑道道宽
            outer_x.append(x)
            outer_y.append(y)
        
        # Draw track
        self.ax.fill(inner_x, inner_y, color='lightgreen', alpha=0.3, label='Track')
        self.ax.plot(inner_x, inner_y, 'gray', linewidth=2, label='Inner Lane')
        self.ax.plot(outer_x, outer_y, 'lightgray', linewidth=1, linestyle='--', label='Outer Lane')
        
        # Draw center line
        center_x, center_y = [], []
        for i in range(steps + 1):
            distance = (i / steps) * track_geometry.total_circumference
            x, y = track_geometry.get_position_on_track(distance, 0.61)  # Middle of lane
            center_x.append(x)
            center_y.append(y)
        self.ax.plot(center_x, center_y, 'blue', linewidth=1, linestyle=':', alpha=0.5, label='Center Line')
        
        # Mark start point
        start_x, start_y = track_geometry.get_position_on_track(0, 0)
        self.ax.plot(start_x, start_y, 'go', markersize=15, label='Start', zorder=10)
        
        # 设置坐标轴范围
        all_x = inner_x + outer_x
        all_y = inner_y + outer_y
        margin = 10
        self.ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        self.ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        
        self.ax.legend(loc='upper right', fontsize=10)
    
    def draw_route(self, positions, color="blue", label="跑步路线", linewidth=2):
        """
        绘制跑步路线
        
        Args:
            positions: 位置列表 [(x, y), ...]
            color: 路线颜色
            label: 路线标签
            linewidth: 线宽
        """
        if not positions:
            return
        
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
        
        line, = self.ax.plot(x_coords, y_coords, color=color, linewidth=linewidth, 
                            label=label, alpha=0.7, zorder=5)
        return line
    
    def add_runner_marker(self, x, y):
        """添加跑者位置标记"""
        if self.runner_marker:
            self.runner_marker.remove()
        self.runner_marker, = self.ax.plot(x, y, 'ro', markersize=10, zorder=15)
        return self.runner_marker
    
    def add_info_text(self, info_dict):
        """添加信息文本"""
        if self.info_text:
            self.info_text.remove()
        
        info_str = "\n".join([f"{key}: {value}" for key, value in info_dict.items()])
        self.info_text = self.ax.text(0.02, 0.98, info_str, transform=self.ax.transAxes,
                                     verticalalignment='top', fontsize=10,
                                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        return self.info_text
    
    def show(self):
        """显示图形"""
        plt.tight_layout()
        plt.show()
    
    def save(self, filename):
        """Save figure to file"""
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Figure saved to: {filename}")


def simulate_run(duration_seconds=60, dt=0.1, speed=2.56, animated=False):
    """
    模拟跑步并可视化
    
    Args:
        duration_seconds: 模拟时长（秒）
        dt: 时间步长（秒）
        speed: 基础速度（米/秒）
        animated: 是否使用动画模式
    """
    # 创建跑道和跑者
    track = TrackGeometry(straight_length=84.39, band_radius=36.5, rotation=90)
    runner = RealisticRunner(track, base_speed=speed)
    
    # 创建可视化工具
    visualizer = TrackVisualizer()
    
    # 绘制跑道
    visualizer.draw_track(track)
    
    # 收集路径点
    positions = []
    
    # Simulation loop
    steps = int(duration_seconds / dt)
    print(f"Starting simulation for {duration_seconds} seconds...")
    print(f"Base speed: {speed} m/s")
    print(f"Time step: {dt} seconds")
    print(f"Total steps: {steps}")
    
    if animated:
        # Animation mode - simplified and more stable
        print("Note: Animation mode may be slow. Consider using static mode for better performance.")
        
        # Pre-run simulation to collect all data
        print("Pre-calculating route...")
        for step in range(steps):
            runner.update(dt)
            positions.append((runner.true_x, runner.true_y))
            if step % 100 == 0:
                print(f"Progress: {step}/{steps} ({step/steps*100:.1f}%)")
        
        # Draw complete path
        visualizer.draw_route(positions, color='lightblue', label='Full Route', linewidth=1)
        
        # Animate runner marker along the path
        runner_marker, = visualizer.ax.plot([], [], 'ro', markersize=10, label='Runner', zorder=15)
        
        def init():
            runner_marker.set_data([], [])
            return [runner_marker]
        
        def animate(frame):
            if frame < len(positions):
                x, y = positions[frame]
                runner_marker.set_data([x], [y])
            if frame % 50 == 0:
                print(f"Animation: {frame}/{len(positions)}")
            return [runner_marker]
        
        # Create animation
        anim = animation.FuncAnimation(visualizer.fig, animate, init_func=init,
                                      frames=len(positions), interval=dt*1000, 
                                      blit=True, repeat=False)
        
        # Add final info
        total_distance = runner.cumulative_distance
        laps = total_distance / track.total_circumference
        avg_speed = total_distance / duration_seconds
        
        info = {
            "Total Time": f"{duration_seconds} s",
            "Total Distance": f"{total_distance:.2f} m",
            "Laps": f"{laps:.2f}",
            "Avg Speed": f"{avg_speed:.2f} m/s",
            "Pace": f"{1000 / avg_speed / 60:.2f} min/km",
            "Path Points": len(positions)
        }
        visualizer.add_info_text(info)
        
        visualizer.show()
    else:
        # Static mode - run full simulation then draw all at once
        for step in range(steps):
            runner.update(dt)
            positions.append((runner.true_x, runner.true_y))
            
            if step % 100 == 0:
                print(f"Progress: {step}/{steps} ({step/steps*100:.1f}%)")
        
        # Draw complete path
        print("\nDrawing complete path...")
        visualizer.draw_route(positions, color='blue', label='Running Route')
        
        # Mark end point
        visualizer.add_runner_marker(runner.true_x, runner.true_y)
        
        # Add info
        total_distance = runner.cumulative_distance
        laps = total_distance / track.total_circumference
        avg_speed = total_distance / duration_seconds
        
        info = {
            "Total Time": f"{duration_seconds} s",
            "Total Distance": f"{total_distance:.2f} m",
            "Laps": f"{laps:.2f}",
            "Avg Speed": f"{avg_speed:.2f} m/s",
            "Pace": f"{1000 / avg_speed / 60:.2f} min/km",
            "Path Points": len(positions)
        }
        visualizer.add_info_text(info)
        
        print(f"\n=== Simulation Complete ===")
        for key, value in info.items():
            print(f"{key}: {value}")
        
        visualizer.show()


def compare_routes():
    """Compare routes with different parameters"""
    track = TrackGeometry(straight_length=84.39, band_radius=36.5, rotation=90)
    visualizer = TrackVisualizer()
    
    # Draw track
    visualizer.draw_track(track)
    
    # Test different speeds
    speeds = [2.0, 2.56, 3.0]  # Slow, medium, fast
    colors = ["blue", "green", "red"]
    labels = ["Slow (2.0 m/s)", "Medium (2.56 m/s)", "Fast (3.0 m/s)"]
    
    print("Comparing routes at different speeds...")
    
    for speed, color, label in zip(speeds, colors, labels):
        runner = RealisticRunner(track, base_speed=speed)
        positions = []
        
        # Simulate 30 seconds
        for _ in range(300):  # 30s / 0.1s
            runner.update(0.1)
            positions.append((runner.true_x, runner.true_y))
        
        # Draw path
        visualizer.draw_route(positions, color=color, label=label)
        print(f"{label}: Distance {runner.cumulative_distance:.2f} m")
    
    visualizer.ax.legend(loc='upper right', fontsize=10)
    visualizer.show()


def test_track_geometry():
    """Test track geometry model"""
    track = TrackGeometry(straight_length=84.39, band_radius=36.5, rotation=90)
    visualizer = TrackVisualizer()
    
    print("Testing track geometry model...")
    print(f"Straight length: {track.straight_length} m")
    print(f"Curve radius: {track.band_radius} m")
    print(f"Curve circumference: {track.band_circumference:.2f} m")
    print(f"Total circumference: {track.total_circumference:.2f} m")
    
    # Draw track
    visualizer.draw_track(track)
    
    # Mark key points
    key_distances = [
        (0, "Start/Finish"),
        (track.straight_length, "Curve 1 Start"),
        (track.straight_length + track.band_circumference, "Straight 2 Start"),
        (2 * track.straight_length + track.band_circumference, "Curve 2 Start"),
    ]
    
    for distance, label in key_distances:
        x, y = track.get_position_on_track(distance, 0)
        visualizer.ax.plot(x, y, 'ro', markersize=10, zorder=10)
        visualizer.ax.annotate(label, xy=(x, y), xytext=(10, 10),
                             textcoords='offset points', fontsize=9,
                             bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        print(f"{label}: Distance={distance:.2f}m, Position=({x:.2f}, {y:.2f})")
    
    visualizer.show()


def save_route_comparison():
    """Save route comparison figure"""
    track = TrackGeometry(straight_length=84.39, band_radius=36.5, rotation=90)
    
    # Create 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Track Route Test - Multi-Scenario Comparison", fontsize=16, fontweight='bold')
    
    scenarios = [
        {"duration": 30, "speed": 2.56, "title": "Standard Speed 30s"},
        {"duration": 60, "speed": 2.56, "title": "Standard Speed 60s"},
        {"duration": 30, "speed": 2.0, "title": "Slow Speed 30s"},
        {"duration": 30, "speed": 3.5, "title": "Fast Speed 30s"},
    ]
    
    for idx, (ax, scenario) in enumerate(zip(axes.flat, scenarios)):
        print(f"\nScenario {idx+1}: {scenario['title']}")
        
        # Setup subplot
        ax.set_aspect('equal')
        ax.set_title(scenario['title'], fontsize=12, fontweight='bold')
        ax.set_xlabel("X (meters)", fontsize=10)
        ax.set_ylabel("Y (meters)", fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Draw track
        steps = 200
        inner_x, inner_y = [], []
        for i in range(steps + 1):
            distance = (i / steps) * track.total_circumference
            x, y = track.get_position_on_track(distance, 0)
            inner_x.append(x)
            inner_y.append(y)
        
        ax.fill(inner_x, inner_y, color='lightgreen', alpha=0.3)
        ax.plot(inner_x, inner_y, 'gray', linewidth=1)
        
        # Simulate running
        runner = RealisticRunner(track, base_speed=scenario['speed'])
        positions = []
        
        duration = scenario['duration']
        for _ in range(int(duration / 0.1)):
            runner.update(0.1)
            positions.append((runner.true_x, runner.true_y))
        
        # Draw route
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
        ax.plot(x_coords, y_coords, 'b-', linewidth=2, alpha=0.7)
        
        # Mark start and end points
        ax.plot(positions[0][0], positions[0][1], 'go', markersize=8, label='Start')
        ax.plot(positions[-1][0], positions[-1][1], 'ro', markersize=8, label='End')
        
        # Add statistics
        info_text = (f"Distance: {runner.cumulative_distance:.2f} m\n"
                    f"Laps: {runner.cumulative_distance / track.total_circumference:.2f}\n"
                    f"Avg Speed: {runner.cumulative_distance / duration:.2f} m/s")
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               verticalalignment='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax.legend(loc='upper right', fontsize=8)
        
        print(f"  Distance: {runner.cumulative_distance:.2f} m")
        print(f"  Laps: {runner.cumulative_distance / track.total_circumference:.2f}")
    
    plt.tight_layout()
    filename = "route_comparison.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nComparison saved to: {filename}")
    plt.show()


def main():
    """Main function"""
    print("=" * 50)
    print("Track Route Visualization Test (Matplotlib)")
    print("=" * 50)
    
    duration = float(input("\nSimulation duration (seconds): "))
    speed = float(input("Base speed (m/s, recommended 2-4): "))
    animated = input("Use animation mode? (y/n, default: n): ").strip().lower() == 'y'
    
    simulate_run(duration_seconds=duration, dt=0.1, speed=speed, animated=animated)


if __name__ == "__main__":
    main()
