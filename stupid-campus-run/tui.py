#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园跑程序 - 完善版交互式界面
不使用任何外部库，纯Python实现
"""

import sys
import os
import threading
import time
import signal
import json
import logging
import base64
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import CampusFly

class SimpleUI:
    """完善版交互式界面"""
    
    def __init__(self):
        self.campus_fly = CampusFly()
        self.running = False
        self.log_messages = []
        self.current_status = "准备中"
        self.config_file = "user_config.json"
        self.log_file = f"campus_fly_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 设置日志
        self.setup_logging()
        
        # 加载用户配置
        self.user_config = self.load_user_config()
        
        # 密码加密密钥（基于机器特征生成）
        self.password_key = self.generate_password_key()
        
        self.setup_signal_handlers()
        
    def setup_logging(self):
        """设置日志记录"""
        # 创建日志目录
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_path = os.path.join(log_dir, self.log_file)
        
        # 配置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("校园跑程序启动")
        
    def generate_password_key(self) -> str:
        """生成密码加密密钥（基于机器特征）"""
        import platform
        import getpass
        
        # 使用机器特征生成密钥
        machine_info = f"{platform.node()}{platform.system()}{getpass.getuser()}"
        key = hashlib.sha256(machine_info.encode()).digest()[:16]  # 使用16字节密钥
        return base64.b64encode(key).decode()
    
    def encrypt_password(self, password: str) -> str:
        """加密密码"""
        try:
            from cryptography.fernet import Fernet
            key = base64.urlsafe_b64encode(self.password_key.encode()[:32].ljust(32, b'0'))
            f = Fernet(key)
            encrypted = f.encrypt(password.encode())
            return base64.b64encode(encrypted).decode()
        except ImportError:
            # 如果没有cryptography库，使用简单的base64编码（不够安全，但可用）
            self.logger.warning("cryptography库未安装，使用简单编码（不够安全）")
            return base64.b64encode(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """解密密码"""
        try:
            from cryptography.fernet import Fernet
            key = base64.urlsafe_b64encode(self.password_key.encode()[:32].ljust(32, b'0'))
            f = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_password.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except ImportError:
            # 如果没有cryptography库，使用简单的base64解码
            return base64.b64decode(encrypted_password.encode()).decode()
        except Exception as e:
            self.logger.error(f"密码解密失败: {e}")
            return ""
    
    def load_user_config(self) -> Dict[str, Any]:
        """加载用户配置"""
        default_config = {
            "last_username": "",
            "last_password": "",  # 加密存储的密码
            "last_school": "上海大学",
            "last_distance": 5000,
            "last_mode": "track",
            "remember_credentials": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保所有键都存在
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                self.logger.warning(f"加载配置文件失败: {e}")
                return default_config
        else:
            return default_config
    
    def save_user_config(self, config: Dict[str, Any]):
        """保存用户配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.logger.info("用户配置已保存")
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """信号处理器"""
        if self.running:
            print("\n\n⏹️ 检测到中断信号，正在停止跑步...")
            self.running = False
            if hasattr(self.campus_fly, 'running_state'):
                self.campus_fly.running_state["is_running"] = False
        else:
            print("\n\n👋 再见!")
            sys.exit(0)
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """打印头部"""
        print("=" * 60)
        print("校园跑模拟器，只是模拟器，不是真的（")
        print("=" * 60)
        
    def print_footer(self):
        """打印底部"""
        print("=" * 60)
        
    def add_log(self, message, level="INFO"):
        """添加日志消息"""
        timestamp = time.strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.log_messages.append(log_message)
        print(log_message)
        
        # 记录到日志文件
        if hasattr(self, 'logger'):
            if level == "ERROR":
                self.logger.error(message)
            elif level == "WARNING":
                self.logger.warning(message)
            elif level == "DEBUG":
                self.logger.debug(message)
            else:
                self.logger.info(message)
        
    def validate_phone(self, phone):
        """验证手机号格式"""
        if not phone:
            return False, phone, "手机号不能为空"
        if not phone.isdigit():
            return False, phone, "手机号只能包含数字"
        if len(phone) != 11:
            return False, phone, "手机号必须是11位数字"
        return True, phone, "手机号格式正确"
        
    def validate_password(self, password):
        """验证密码"""
        if not password:
            return False, password, "密码不能为空"
        if len(password) < 6:
            return False, password, "密码长度至少6位"
        return True, password, "密码格式正确"
        
    def validate_distance(self, distance_str):
        """验证距离输入"""
        if not distance_str:
            return True, 5000, "使用默认距离5000米"
        try:
            distance = int(distance_str)
            if distance < 100:
                return False, 0, "距离不能少于100米"
            if distance > 20000:
                return False, 0, "距离不能超过20000米"
            return True, distance, "距离设置成功"
        except ValueError:
            return False, 0, "距离必须是数字"
            
    def get_input_with_validation(self, prompt, validator, error_msg="输入无效", allow_empty=False):
        """获取带验证的输入"""
        while True:
            try:
                value = input(prompt).strip()
                
                # 如果允许空值且输入为空，直接返回空字符串
                if allow_empty and not value:
                    return ""
                
                is_valid, result, message = validator(value)
                if is_valid:
                    print(f"✅ {message}")
                    return result
                else:
                    print(f"❌ {message}")
            except (EOFError, KeyboardInterrupt):
                return None
                
    def show_login_screen(self):
        """显示登录界面"""
        while True:
            self.clear_screen()
            self.print_header()
            print("请输入您的登录信息:")
            print()
            
            # 显示记忆的用户名
            default_username = self.user_config.get("last_username", "")
            username_prompt = f"用户名（手机号）{'[' + default_username + ']' if default_username else ''}: "
            
            # 获取用户名
            username = self.get_input_with_validation(
                username_prompt, 
                self.validate_phone,
                allow_empty=True
            )
            if username is None:
                return None
                
            # 如果用户直接按回车，使用记忆的用户名
            if not username and default_username:
                username = default_username
                self.add_log(f"使用记忆的用户名: {username}")
            elif not username:
                print("❌ 用户名不能为空")
                continue
                
            # 获取密码
            default_password = ""
            if self.user_config.get("remember_credentials", False) and self.user_config.get("last_password"):
                try:
                    default_password = self.decrypt_password(self.user_config["last_password"])
                    password_prompt = f"密码 [已记忆]: "
                except:
                    password_prompt = "密码: "
            else:
                password_prompt = "密码: "
            
            password = self.get_input_with_validation(
                password_prompt, 
                self.validate_password,
                allow_empty=True
            )
            if password is None:
                return None
                
            # 如果用户直接按回车，使用记忆的密码
            if not password and default_password:
                password = default_password
                self.add_log(f"使用记忆的密码")
            elif not password:
                print("❌ 密码不能为空")
                continue
                
            # 选择学校
            print("\n请选择学校:")
            print("1. 上海大学")
            print("2. 上海中医药大学")
            
            # 显示记忆的学校
            last_school = self.user_config.get("last_school", "上海大学")
            default_choice = "1" if last_school == "上海大学" else "2"
            
            while True:
                try:
                    school_choice = input(f"请输入学校编号 (默认{default_choice}): ").strip()
                    if not school_choice:
                        school_choice = default_choice
                        self.add_log(f"使用记忆的学校: {last_school}")
                    
                    if school_choice == "1":
                        school = "上海大学"
                        break
                    elif school_choice == "2":
                        school = "上海中医药大学"
                        break
                    else:
                        print("❌ 请输入1或2")
                except (EOFError, KeyboardInterrupt):
                    return None
                    
            # 选择距离
            last_distance = self.user_config.get("last_distance", 5000)
            distance_prompt = f"请输入跑步距离(米，默认{last_distance}): "
            distance = self.get_input_with_validation(
                distance_prompt,
                self.validate_distance,
                allow_empty=True
            )
            if distance is None:
                return None
                
            # 如果用户直接按回车，使用记忆的距离
            if not distance and last_distance:
                distance = last_distance
                self.add_log(f"使用记忆的距离: {distance}米")
                
            # 选择模式
            print("\n请选择轨迹模式:")
            print("1. 跑道轨迹（推荐，配速6.5分钟/公里）")
            print("2. 随机轨迹")
            
            # 显示记忆的模式
            last_mode = self.user_config.get("last_mode", "track")
            default_mode_choice = "1" if last_mode == "track" else "2"
            
            while True:
                try:
                    mode_choice = input(f"请输入模式编号 (默认{default_mode_choice}): ").strip()
                    if not mode_choice:
                        mode_choice = default_mode_choice
                        self.add_log(f"使用记忆的模式: {last_mode}")
                    
                    if mode_choice == "1":
                        mode = "track"
                        break
                    elif mode_choice == "2":
                        mode = "random"
                        break
                    else:
                        print("❌ 请输入1或2")
                except (EOFError, KeyboardInterrupt):
                    return None
            
            # 确认配置
            print(f"\n📋 配置确认:")
            print(f"  用户名: {username}")
            print(f"  学校: {school}")
            print(f"  距离: {distance}米")
            print(f"  模式: {'跑道轨迹' if mode == 'track' else '随机轨迹'}")
            
            # 询问是否保存配置
            save_config = input("\n是否保存此配置供下次使用? (y/n) [默认y]: ").strip().lower()
            if not save_config:  # 如果直接按回车，默认为y
                save_config = 'y'
            if save_config == 'y':
                # 询问是否记住密码
                remember_password = input("是否记住密码? (y/n) [默认n]: ").strip().lower()
                if not remember_password:  # 如果直接按回车，默认为n
                    remember_password = 'n'
                
                # 准备保存的配置
                config_to_save = {
                    "last_username": username,
                    "last_school": school,
                    "last_distance": distance,
                    "last_mode": mode,
                    "remember_credentials": remember_password == 'y'
                }
                
                # 如果选择记住密码，加密保存
                if remember_password == 'y':
                    encrypted_password = self.encrypt_password(password)
                    config_to_save["last_password"] = encrypted_password
                    self.add_log("密码已加密保存")
                else:
                    # 清除已保存的密码
                    config_to_save["last_password"] = ""
                
                self.user_config.update(config_to_save)
                self.save_user_config(self.user_config)
                self.add_log("配置已保存")
            
            confirm = input("\n确认开始跑步? (y/n) [默认y]: ").strip().lower()
            if not confirm:  # 如果直接按回车，默认为y
                confirm = 'y'
            if confirm == 'y':
                return {
                    "username": username,
                    "password": password,
                    "school": school,
                    "distance": distance,
                    "mode": mode
                }
            elif confirm == 'n':
                continue
            else:
                print("❌ 请输入y或n")
                input("按Enter键继续...")
        
    def draw_progress_bar(self, progress, width=50):
        """绘制进度条"""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {progress:.1f}%"
    
    def draw_loading_spinner(self, step, total_steps, message=""):
        """绘制加载动画"""
        spinner_chars = "|/-\\"
        spinner = spinner_chars[step % len(spinner_chars)]
        progress = int((step / total_steps) * 100) if total_steps > 0 else 0
        return f"{spinner} {message} ({progress}%)"
    
    def show_operation_progress(self, operation, step, total_steps, message=""):
        """显示操作进度"""
        self.clear_screen()
        self.print_header()
        
        # 显示当前操作
        print(f"🔄 {operation}")
        print()
        
        # 显示进度条
        if total_steps > 0:
            progress = (step / total_steps) * 100
            print(f"进度: {self.draw_progress_bar(progress)}")
        else:
            spinner = self.draw_loading_spinner(step, 0, message)
            print(f"状态: {spinner}")
        
        print()
        print(f"📝 {message}")
        print()
        print("请稍候...")
    
    def show_running_progress(self, current_distance, target_distance, current_time, pace):
        """显示跑步进度"""
        self.clear_screen()
        self.print_header()
        
        # 计算进度和预计剩余时间
        progress = min(100, (current_distance / target_distance) * 100)
        remaining_distance = max(0, target_distance - current_distance)
        
        if pace > 0 and remaining_distance > 0:
            remaining_time_seconds = (remaining_distance / 1000) * pace * 60
            eta_str = self.campus_fly.format_time(int(remaining_time_seconds))
        else:
            eta_str = "计算中..."
        
        # 显示跑步状态
        print("🏃‍♂️ 正在跑步中...")
        print()
        
        # 显示进度条
        print(f"📊 跑步进度: {self.draw_progress_bar(progress)}")
        print()
        
        # 显示跑步数据
        time_str = self.campus_fly.format_time(current_time)
        distance_km = current_distance / 1000
        target_km = target_distance / 1000
        
        print(f"⏱️  当前时长: {time_str}")
        print(f"📏 跑步距离: {distance_km:.2f}km / {target_km:.1f}km")
        print(f"🏃 当前配速: {pace:.2f}min/km")
        print(f"⏰ 预计剩余: {eta_str}")
        print()
        
        # 显示提示信息
        print("💡 提示: 按 Ctrl+C 可以提前结束并提交跑步数据")
        print()
        print("⌨️  按 Ctrl+C 中断并提交跑步")
        
    def show_running_screen(self, config):
        """显示跑步界面"""
        self.clear_screen()
        self.print_header()
        print("🏃 正在跑步中...")
        print()
        
        # 在后台线程中运行跑步程序
        def run_campus_fly():
            try:
                # 前期准备阶段 - 详细进度条
                preparation_steps = [
                    ("初始化", "正在设置学校信息..."),
                    ("登录", f"正在登录用户: {config['username']}"),
                    ("查询计划", "正在获取您的体测计划..."),
                    ("开始跑步", "正在启动跑步...")
                ]
                
                for i, (step_name, step_desc) in enumerate(preparation_steps, 1):
                    self.current_status = step_name
                    self.show_operation_progress(f"前期准备 - {step_name}", i, len(preparation_steps), step_desc)
                    time.sleep(0.3)  # 减少延迟，让进度条更流畅
                
                # 步骤1: 初始化
                if config["school"] in self.campus_fly.agency_ids:
                    self.campus_fly.agency_id = int(self.campus_fly.agency_ids[config["school"]])
                    self.campus_fly.auth_info["agencyId"] = self.campus_fly.agency_id
                
                # 步骤2: 登录
                try:
                    login_result = self.campus_fly.login(
                        config["username"], 
                        config["password"]
                    )
                    if len(login_result) != 3:
                        self.current_status = "登录失败"
                        return
                    success, token, response = login_result
                    
                except Exception as e:
                    self.logger.error(f"登录异常: {str(e)}", exc_info=True)
                    self.current_status = "登录失败"
                    return
                    
                if not success:
                    error_msg = response.get('message', '未知错误') if response else '登录失败'
                    self.logger.error(f"登录失败: {error_msg}")
                    self.current_status = "登录失败"
                    return
                
                self.campus_fly.auth_info["token"] = token
                self.logger.info("登录成功")
                
                # 步骤3: 查询体测计划
                try:
                    plans_result = self.campus_fly.query_fitness_plans(token)
                    if len(plans_result) != 3:
                        self.current_status = "查询失败"
                        return
                    success, plans, response = plans_result
                    
                except Exception as e:
                    self.logger.error(f"查询体测计划异常: {str(e)}", exc_info=True)
                    self.current_status = "查询失败"
                    return
                    
                if not success or not plans:
                    error_msg = response.get('message', '未找到体测计划') if response else '未找到体测计划'
                    self.logger.error(f"未找到体测计划: {error_msg}")
                    self.current_status = "无体测计划"
                    return
                
                # 选择体测计划
                selected_plan = plans[0]
                self.campus_fly.auth_info["fitnessId"] = selected_plan["fitnessId"]
                self.logger.info(f"使用体测计划: {selected_plan['fitnessName']} (ID: {selected_plan['fitnessId']})")
                
                # 步骤4: 开始跑步
                if not self.campus_fly.start_running():
                    self.logger.error("开始跑步失败")
                    self.current_status = "开始失败"
                    return
                
                self.logger.info("跑步开始成功")
                
                mode_text = "跑道轨迹" if config["mode"] == "track" else "随机轨迹"
                self.logger.info(f"使用{mode_text}模式，目标距离: {config['distance']}米")
                
                # 模拟跑步过程
                self.campus_fly.running_state["is_running"] = True
                self.running = True
                self.current_status = "跑步中"
                
                while (self.campus_fly.running_state["distance"] < config["distance"] and 
                       self.campus_fly.running_state["is_running"] and self.running):
                    
                    # 更新跑步数据
                    self.campus_fly.heartbeat(keep_running=True)
                    time.sleep(1)
                    
                    if self.campus_fly.running_state["distance"] >= config["distance"]:
                        break
                
                # 步骤5: 结束跑步
                self.current_status = "结束跑步"
                self.show_operation_progress("结束跑步", 5, 5, "正在提交跑步数据...")
                time.sleep(0.5)
                
                if self.campus_fly.end_running():
                    self.logger.info("校园跑完成并成功提交")
                    self.current_status = "完成"
                    
                    # 记录跑步统计
                    if hasattr(self.campus_fly, 'running_state'):
                        stats = {
                            "总时长": self.campus_fly.format_time(self.campus_fly.running_state["time"]),
                            "总距离": f"{self.campus_fly.running_state['distance']/1000:.2f}km",
                            "平均配速": f"{(self.campus_fly.running_state['time']/60)/(self.campus_fly.running_state['distance']/1000):.2f}min/km"
                        }
                        self.logger.info(f"跑步统计: {stats}")
                else:
                    self.logger.error("提交跑步数据失败")
                    self.current_status = "提交失败"
                    
            except Exception as e:
                self.logger.error(f"程序执行异常: {str(e)}", exc_info=True)
                self.current_status = "异常"
            finally:
                self.running = False
                self.logger.info("跑步程序结束")
                
        # 启动后台线程
        thread = threading.Thread(target=run_campus_fly)
        thread.daemon = True
        thread.start()
        
        # 显示跑步状态
        self.show_running_status(config["distance"])
        
    def update_running_display(self, target_distance):
        """更新跑步显示"""
        if hasattr(self.campus_fly, 'running_state'):
            time_str = self.campus_fly.format_time(self.campus_fly.running_state["time"])
            distance_km = self.campus_fly.running_state["distance"] / 1000
            pace = (self.campus_fly.running_state["time"] / 60) / distance_km if distance_km > 0 else 0
            progress = min(100, (self.campus_fly.running_state["distance"] / target_distance) * 100)
            
            print(f"\r⏱️  时长: {time_str} | 📏 距离: {distance_km:.2f}km | 🏃 配速: {pace:.2f}min/km | 📊 进度: {progress:.1f}%", end="", flush=True)
            
    def show_running_status(self, target_distance):
        """显示跑步状态"""
        try:
            while self.running or self.current_status in ["完成", "提交失败", "异常"]:
                # 根据状态显示不同界面
                if self.current_status == "跑步中" and hasattr(self.campus_fly, 'running_state') and self.campus_fly.running_state["time"] > 0:
                    # 显示跑步进度条
                    current_time = self.campus_fly.running_state["time"]
                    current_distance = self.campus_fly.running_state["distance"]
                    distance_km = current_distance / 1000
                    pace = (current_time / 60) / distance_km if distance_km > 0 else 0
                    
                    self.show_running_progress(current_distance, target_distance, current_time, pace)
                else:
                    # 显示其他状态
                    self.clear_screen()
                    self.print_header()
                    
                    # 显示当前状态
                    status_emoji = {
                        "初始化中": "🔄",
                        "登录中": "🔐",
                        "查询计划": "📋",
                        "开始跑步": "🏃",
                        "跑步中": "🏃‍♂️",
                        "结束跑步": "🏁",
                        "完成": "✅",
                        "登录失败": "❌",
                        "查询失败": "❌",
                        "无体测计划": "❌",
                        "开始失败": "❌",
                        "提交失败": "❌",
                        "异常": "💥"
                    }
                    
                    print(f"{status_emoji.get(self.current_status, '🔄')} 状态: {self.current_status}")
                    print()
                    
                    # 显示状态信息
                    if self.current_status == "完成":
                        print("🎉 跑步完成！数据已成功提交")
                    elif self.current_status in ["登录失败", "查询失败", "无体测计划", "开始失败", "提交失败", "异常"]:
                        print(f"❌ 操作失败，请检查网络连接和账号信息")
                    else:
                        print("请稍候...")
                    
                    print()
                    print("⌨️  按 Ctrl+C 中断并提交跑步")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ 用户中断跑步，正在提交数据...")
            self.running = False
            if hasattr(self.campus_fly, 'running_state'):
                self.campus_fly.running_state["is_running"] = False
                
            # 提交跑步数据
            if hasattr(self.campus_fly, 'end_running'):
                try:
                    if self.campus_fly.end_running():
                        print("✅ 跑步数据已成功提交")
                    else:
                        print("❌ 提交跑步数据失败")
                except Exception as e:
                    print(f"❌ 提交数据时出错: {e}")
                
        # 显示最终结果
        self.clear_screen()
        self.print_header()
        
        if self.current_status == "完成":
            print("🎉 校园跑完成！")
            if hasattr(self.campus_fly, 'running_state'):
                time_str = self.campus_fly.format_time(self.campus_fly.running_state["time"])
                distance_km = self.campus_fly.running_state["distance"] / 1000
                pace = (self.campus_fly.running_state["time"] / 60) / distance_km if distance_km > 0 else 0
                print(f"总时长: {time_str}")
                print(f"总距离: {distance_km:.2f}km")
                print(f"平均配速: {pace:.2f}min/km")
        else:
            print(f"❌ 跑步未完成，状态: {self.current_status}")
            
        self.print_footer()
        input("按Enter键返回主菜单...")
        
    def show_main_menu(self):
        """显示主菜单"""
        self.clear_screen()
        self.print_header()
        print("欢迎使用校园跑程序！")
        print()
        print("请选择操作:")
        print("1. 开始跑步")
        print("2. 修改密码")
        print("3. 查看帮助")
        print("4. 退出程序")
        print()
        
        while True:
            try:
                choice = input("请输入选项编号 (1-4): ").strip()
                if choice == "1":
                    return "run"
                elif choice == "2":
                    return "change_password"
                elif choice == "3":
                    return "help"
                elif choice == "4":
                    return "exit"
                else:
                    print("❌ 请输入1、2、3或4")
            except (EOFError, KeyboardInterrupt):
                return "exit"
                
    def show_change_password(self):
        """显示修改密码界面"""
        self.clear_screen()
        self.print_header()
        print("🔐 修改密码")
        print()
        print("首次使用需要修改密码！")
        print()
        print("密码要求:")
        print("• 长度应大于等于12位")
        print("• 同时包含大小写字母")
        print("• 包含数字")
        print("• 包含特殊符号")
        print()
        print("修改密码步骤:")
        print("1. 点击下方链接打开密码修改页面")
        print("2. 使用您的手机号登录")
        print("3. 按照要求设置新密码")
        print("4. 修改完成后返回程序")
        print()
        
        # 检查是否在支持的环境中
        import webbrowser
        import platform
        
        try:
            print("🌐 正在打开密码修改页面...")
            webbrowser.open("https://edu.ymq.me/wechat/#/wechat/user/mobile/user/reset")
            print("✅ 密码修改页面已在浏览器中打开")
        except Exception as e:
            print("❌ 无法自动打开浏览器")
            print("请手动访问以下链接:")
            print("https://edu.ymq.me/wechat/#/wechat/user/mobile/user/reset")
            print(f"错误信息: {e}")
        
        print()
        print("📱 密码修改页面链接:")
        print("https://edu.ymq.me/wechat/#/wechat/user/mobile/user/reset")
        print()
        print("💡 提示:")
        print("• 如果页面无法打开，请复制链接到浏览器中访问")
        print("• 修改密码后，请使用新密码登录程序")
        print("• 建议使用强密码以确保账号安全")
        print()
        
        input("按Enter键返回主菜单...")
    
    def show_help(self):
        """显示帮助信息"""
        self.clear_screen()
        self.print_header()
        print("📖 帮助信息")
        print()
        print("🏃‍♂️ 校园跑程序使用说明:")
        print()
        print("1. 登录信息:")
        print("   - 用户名: 您的华体运动会账号手机号")
        print("   - 密码: 您的华体运动会账号密码")
        print()
        print("2. 学校选择:")
        print("   - 上海大学 (机构ID: 1977)")
        print("   - 上海中医药大学 (机构ID: 1036)")
        print()
        print("3. 跑步设置:")
        print("   - 距离: 100-20000米")
        print("   - 模式: 跑道轨迹或随机轨迹")
        print()
        print("4. 轨迹模式:")
        print("   - 跑道轨迹: 基于标准400米跑道，配速6.5分钟/公里")
        print("   - 随机轨迹: 基于电子围栏生成随机路线")
        print()
        print("5. 操作说明:")
        print("   - 按Ctrl+C可以随时停止跑步")
        print("   - 程序会自动处理所有认证和提交过程")
        print()
        print("6. 密码修改:")
        print("   - 首次使用需要修改密码")
        print("   - 密码要求: 12位以上，包含大小写字母、数字和特殊符号")
        print("   - 修改链接: https://edu.ymq.me/wechat/#/wechat/user/mobile/user/reset")
        print()
        print("⚠️ 注意事项:")
        print("   - 请确保网络连接正常")
        print("   - 请确保有有效的体测计划")
        print("   - 请遵守学校相关规定")
        print()
        input("按Enter键返回主菜单...")
        
    def run(self):
        """运行界面"""
        while True:
            try:
                # 显示主菜单
                choice = self.show_main_menu()
                
                if choice == "run":
                    # 显示登录界面
                    config = self.show_login_screen()
                    if config is None:
                        continue
                        
                    # 开始跑步
                    self.show_running_screen(config)
                    
                elif choice == "change_password":
                    # 显示修改密码界面
                    self.show_change_password()
                    
                elif choice == "help":
                    # 显示帮助
                    self.show_help()
                    
                elif choice == "exit":
                    # 退出程序
                    self.clear_screen()
                    print("👋 感谢使用校园跑程序，再见！")
                    break
                
            except KeyboardInterrupt:
                print("\n\n👋 再见!")
                break
            except Exception as e:
                print(f"\n❌ 程序异常: {e}")
                input("按Enter键继续...")

def main():
    """主函数"""
    ui = SimpleUI()
    ui.run()

if __name__ == "__main__":
    main()
