import requests
import json
import time
import hashlib
import math
import random
from typing import Dict, List, Tuple, Optional
import argparse
import sys

class CampusFly:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })
        
        # API配置
        self.base_urls = {
            "user": "https://user.ymq.me",
            "edu": "https://edu.ymq.me"
        }
        
        # 学校配置
        self.agency_ids = {
            "上海大学": "1977",
            "上海中医药大学": "1036"
        }
        self.agency_id = 1977  # 默认上海大学
        self.max_distance = 8000  # 8公里限制
        
        # 狠狠的抄冰火的跑道参数
        self.track_config = {
            "center_lat": (31.318217 + 31.31997) / 2,  # 跑道中心纬度
            "center_lng": (121.392548 + 121.393845) / 2,  # 跑道中心经度
            "straight_length": 84.39,  # 直道长度（米）
            "band_radius": 36.5,  # 弯道半径（米）
            "total_circumference": 400,  # 总周长（米）
            "speed": 1000 / 6.5 / 60,  # 配速6.5分钟/公里（米/秒）
            "rotation": 90  # 跑道旋转角度（度）
        }
        
        # 上海大学电子围栏坐标（7个区域）
        self.geo_fences = [
            {"name": "区域1", "lat": [31.19141, 31.193705], "lng": [121.594352, 121.596808]},
            {"name": "区域2", "lat": [31.052121, 31.053421], "lng": [121.752672, 121.753916]},
            {"name": "区域3", "lat": [31.221011, 31.222512], "lng": [121.630334, 121.632343]},
            {"name": "区域4", "lat": [31.318217, 31.31997], "lng": [121.392548, 121.393845]},
            {"name": "区域5", "lat": [31.318391, 31.320292], "lng": [121.396041, 121.39726]},
            {"name": "区域6", "lat": [31.275604, 31.277297], "lng": [121.456016, 121.457606]},
            {"name": "区域7", "lat": [31.376768, 31.378306], "lng": [121.248733, 121.250344]}
        ]
        
        # 认证信息
        self.auth_info = {
            "token": "",
            "fitnessId": "",
            "agencyId": self.agency_id,
            "strollRecordId": 0,
            "gradeType": 0
        }
        
        # 跑步状态
        self.running_state = {
            "positions": [],
            "distance": 0,
            "time": 0,
            "is_running": False
        }
    
    def generate_signature(self, params: Dict, timestamp: int, token: str) -> str:
        """生成API签名"""
        all_params = {
            "snTime": timestamp,
            "token": token
        }
        all_params.update(params)
        
        sorted_keys = sorted(all_params.keys())
        sign_string = "&".join([f"{key}={all_params[key]}" for key in sorted_keys])
        
        return hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    
    def make_request(self, url: str, data: Dict, token: str = "") -> Dict:
        """发送API请求"""
        timestamp = int(time.time() * 1000)
        signature = self.generate_signature(data, timestamp, token)
        
        request_body = {
            "body": data,
            "header": {
                "token": token,
                "snTime": timestamp,
                "sn": signature,
                "from": "wx"
            }
        }
        
        # 计算整个请求体的MD5签名
        import json
        request_json = json.dumps(request_body, separators=(',', ':'))
        request_signature = hashlib.md5(request_json.encode('utf-8')).hexdigest()
        
        headers = {
            "Accept": "*/*;",
            "Content-Type": "application/json; charset=UTF-8",
            "x-sn-verify": request_signature  # 注意是小写
        }
        
        try:
            response = self.session.post(url, data=request_json, headers=headers, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            return response_data
            
        except requests.exceptions.RequestException as e:
            error_info = {
                "status": -1, 
                "message": f"网络请求错误: {str(e)}",
                "error_type": "RequestException",
                "url": url,
                "request_data": request_body,
                "response_status": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                "response_text": getattr(e.response, 'text', None) if hasattr(e, 'response') else None
            }
            return error_info
        except json.JSONDecodeError as e:
            error_info = {
                "status": -1,
                "message": f"JSON解析错误: {str(e)}",
                "error_type": "JSONDecodeError",
                "url": url,
                "response_text": response.text if hasattr(response, 'text') else "无法获取响应文本"
            }
            return error_info
        except Exception as e:
            error_info = {
                "status": -1,
                "message": f"未知错误: {str(e)}",
                "error_type": "UnknownError",
                "url": url,
                "request_data": request_body
            }
            return error_info
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[str], Dict]:
        """用户登录"""
        url = f"{self.base_urls['user']}/public/public/login"
        data = {
            "identifier": username,
            "credential": password,
            "client_id": 1000,
            "identity_type": 1
        }
        
        print(f"🔐 正在登录用户: {username}")
        response = self.make_request(url, data)
        
        if response.get("code") == 1:
            token = response.get("userinfo", {}).get("token")
            if token:
                print("✅ 登录成功！")
                return True, token, response
            else:
                print("❌ 登录响应中未找到token")
                return False, None, response
        else:
            print(f"❌ 登录失败: {response.get('message', '未知错误')}")
            return False, None, response
    
    def query_fitness_plans(self, token: str) -> Tuple[bool, List[Dict], Dict]:
        """查询体测计划"""
        url = f"{self.base_urls['edu']}/webservice/wechat/student/fitness/queryOneStudentFitness.do"
        data = {
            "agencyId": str(self.agency_id),  # 使用当前设置的agency_id
            "page": 1,
            "rows": 999
        }
        
        print(f"📋 正在查询体测计划...")
        response = self.make_request(url, data, token)
        
        if response.get("status") == 0:
            detail = response.get("detail", {})
            current = detail.get("current", [])
            history = detail.get("history", [])
            
            # 优先使用当前计划，如果没有则使用历史计划
            all_plans = current + history
            
            if all_plans:
                print(f"✅ 找到 {len(current)} 个当前计划，{len(history)} 个历史计划")
                
                # 优先选择当前计划，与FitnessResolver保持一致
                if current:
                    selected_plan = current[0]
                else:
                    selected_plan = history[0]
                
                return True, [selected_plan], response
            else:
                print("❌ 未找到体测计划")
                return False, [], response
        else:
            print(f"❌ 查询体测计划失败: {response.get('message', '未知错误')}")
            return False, [], response
    
    def verify_token(self, token: str) -> bool:
        """验证token有效性 - 参考FitnessResolver，直接返回True"""
        # FitnessResolver没有单独的token验证步骤，直接使用登录后的token
        print(f"🔍 跳过token验证，直接使用token: {token[:20]}...")
        return True
    
    def get_track_position_with_rotation(self, t: int, center_lat: float = None, center_lng: float = None, 
                                       rotation: float = None, offset_x: float = 0, offset_y: float = 0) -> Dict:
        """
        支持旋转的跑道位置计算函数（完全按照FitnessResolver的算法）
        """
        if center_lat is None:
            center_lat = self.track_config["center_lat"]
        if center_lng is None:
            center_lng = self.track_config["center_lng"]
        if rotation is None:
            rotation = self.track_config["rotation"]
        
        # 1. 标准跑道参数（内圈）
        straight_length = 84.39  # 单段直道长度（米）
        band_radius = 36.5       # 弯道半径（米）
        band_circumference = math.pi * band_radius  # 单段弯道长度（≈114.66米）
        total_circumference = 2 * straight_length + 2 * band_circumference  # ≈400米

        # 2. 速度参数（1公里/6.5分钟）
        speed = 1000 / 6.5 / 60  # ≈153.846米/分钟
        distance = (speed * t) % total_circumference  # 累计移动距离

        # 3. 计算原始相对坐标（未旋转，默认东西向长轴）
        x, y = 0, 0
        if distance <= straight_length:
            # 阶段1：右侧直道（东西向时，向右为X正方向）
            x = straight_length / 2 - distance
            y = -band_radius
        elif distance <= straight_length + band_circumference:
            # 阶段2：上弯道
            arc_distance = distance - straight_length
            angle = arc_distance / band_radius  # 0→π弧度（顺时针）
            x = -straight_length / 2 - band_radius * math.sin(angle)
            y = -band_radius * math.cos(angle)
        elif distance <= 2 * straight_length + band_circumference:
            # 阶段3：左侧直道
            straight2_distance = distance - (straight_length + band_circumference)
            x = -straight_length / 2 + straight2_distance
            y = band_radius
        else:
            # 阶段4：下弯道
            arc_distance = distance - (2 * straight_length + band_circumference)
            angle = arc_distance / band_radius  # 0→π弧度（顺时针）
            x = straight_length / 2 + band_radius * math.sin(angle)
            y = band_radius * math.cos(angle)

        # 4. 叠加偏移量
        x += offset_x
        y += offset_y

        # 5. 坐标旋转（核心：将东西向转换为南北向或自定义角度）
        rotation_rad = rotation * math.pi / 180  # 角度转弧度
        cos_rot = math.cos(rotation_rad)
        sin_rot = math.sin(rotation_rad)
        # 旋转公式：x' = x*cosθ - y*sinθ；y' = x*sinθ + y*cosθ
        x_rotated = x * cos_rot - y * sin_rot
        y_rotated = x * sin_rot + y * cos_rot

        # 6. 旋转后的坐标转换为经纬度
        earth_radius = 6378137  # 地球赤道半径（米）
        rad_lat = center_lat * math.pi / 180
        lng_per_meter = 1 / (earth_radius * math.cos(rad_lat))  # 1米对应的经度差（弧度）
        lat_per_meter = 1 / earth_radius  # 1米对应的纬度差（弧度）

        return {
            "latitude": center_lat + (y_rotated * lat_per_meter) * (180 / math.pi),
            "longitude": center_lng + (x_rotated * lng_per_meter) * (180 / math.pi)
        }
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """计算两个经纬度坐标之间的直线距离（米）- 完全按照FitnessResolver的算法"""
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
    
    def start_running(self) -> bool:
        """开始跑步"""
        url = f"{self.base_urls['edu']}/webservice/wechat/student/stroll/makeStroll.do"
        data = {"fitnessId": self.auth_info["fitnessId"]}
        
        print("🏃 正在开始跑步...")
        response = self.make_request(url, data, self.auth_info["token"])
        
        if response.get("status") == 0:
            detail = response.get("detail", {})
            self.auth_info["gradeType"] = detail.get("gradeType", 0)
            self.auth_info["strollRecordId"] = detail.get("strollRecordId", 0)
            
            print("✅ 跑步开始成功")
            return True
        else:
            print(f"❌ 开始跑步失败: {response.get('message')}")
            return False
    
    def heartbeat(self, keep_running: bool = True) -> bool:
        """心跳包（实时更新跑步数据）- 完全按照FitnessResolver的逻辑"""
        # 生成当前位置
        pos = self.get_track_position_with_rotation(self.running_state["time"])
        
        # 计算距离 - 按照FitnessResolver的逻辑
        if len(self.running_state["positions"]) > 0:
            last_pos = self.running_state["positions"][-1]
            distance_increment = self.calculate_distance(
                pos["latitude"], pos["longitude"],
                last_pos["latitude"], last_pos["longitude"]
            )
            # 使用Math.ceil()的等价操作
            self.running_state["distance"] += math.ceil(distance_increment)
        
        # 添加位置点
        self.running_state["positions"].append(pos)
        self.running_state["time"] += 1
        
        # 构造数据
        data = self.construct_running_data()
        
        # 发送心跳包
        url = f"{self.base_urls['edu']}/webservice/wechat/student/stroll/saveStroll.do"
        response = self.make_request(url, data, self.auth_info["token"])
        
        # 更新显示
        self.update_display()
        
        return response.get("status") == 0
    
    def end_running(self) -> bool:
        """结束跑步"""
        print("🏁 正在结束跑步...")
        
        # 发送最后一次心跳包
        self.heartbeat(keep_running=False)
        
        # 提交最终数据
        data = self.construct_running_data()
        url = f"{self.base_urls['edu']}/webservice/wechat/student/stroll/submitStroll.do"
        response = self.make_request(url, data, self.auth_info["token"])
        
        if response.get("status") == 0:
            print("✅ 跑步结束成功")
            return True
        else:
            print(f"❌ 结束跑步失败: {response.get('message')}")
            return False
    
    def construct_running_data(self) -> Dict:
        """构造跑步数据 - 完全按照FitnessResolver的格式"""
        return {
            "fitnessId": self.auth_info["fitnessId"],
            "gradeType": self.auth_info["gradeType"],
            "strollDistance": int(self.running_state["distance"]),
            "submitTimestamp": int(time.time() * 1000),
            "strollRecordId": self.auth_info["strollRecordId"],
            "strollDetail": json.dumps({
                "map": [
                    {"x": pos["longitude"], "y": pos["latitude"]} 
                    for pos in self.running_state["positions"]
                ]
            })
        }
    
    def update_display(self):
        """更新显示信息 - 按照FitnessResolver的格式"""
        time_str = self.format_time(self.running_state["time"])
        distance_km = self.running_state["distance"] / 1000
        # 按照FitnessResolver的配速计算：Math.floor((time / 60) / (distance / 1000) * 100) / 100
        pace = math.floor((self.running_state["time"] / 60) / (distance_km) * 100) / 100 if distance_km > 0 else 0
        
        print(f"\r⏱️  时长: {time_str} | 📏 距离: {math.floor(self.running_state['distance']) / 1000:.2f}千米 | 🏃 配速: {pace:.2f}min/km", end="", flush=True)
    
    def format_time(self, seconds: int) -> str:
        """格式化时间显示 - 完全按照FitnessResolver的算法"""
        if seconds is None or seconds <= 0:
            return "00:00:00"
        
        seconds = math.floor(seconds)
        hour = math.floor(seconds / 3600)
        hour_str = f"0{hour}" if hour < 10 else str(hour)
        
        minute = seconds % 3600
        minute_val = math.floor(minute / 60)
        minute_str = f"0{minute_val}" if minute_val < 10 else str(minute_val)
        
        second_val = minute % 60
        second_str = f"0{second_val}" if second_val < 10 else str(second_val)
        
        return f"{hour_str}:{minute_str}:{second_str}"
    
    def run_campus_fly(self, username: str, password: str, target_distance: int = 5000, 
                      school: str = "上海大学", mode: str = "track"):
        """运行校园跑程序"""
        print("=" * 60)
        print("🏃‍♂️ 校园跑程序启动")
        print("=" * 60)
        print(f"用户名: {username}")
        print(f"目标距离: {target_distance/1000:.1f}km")
        print(f"学校: {school}")
        print(f"模式: {'跑道轨迹' if mode == 'track' else '随机轨迹'}")
        print("=" * 60)
        
        # 设置学校ID
        if school in self.agency_ids:
            self.agency_id = int(self.agency_ids[school])
            self.auth_info["agencyId"] = self.agency_id
        else:
            print(f"❌ 不支持的学校: {school}")
            return False
        
        try:
            # 步骤1: 登录
            success, token, _ = self.login(username, password)
            if not success:
                return False
            
            self.auth_info["token"] = token
            
            # 步骤2: 查询体测计划（与FitnessResolver保持一致，跳过token验证）
            success, plans, _ = self.query_fitness_plans(token)
            if not success or not plans:
                print("❌ 未找到体测计划")
                return False
            
            # 确保fitnessId是整数类型，与FitnessResolver保持一致
            fitness_id = int(plans[0]["fitnessId"])
            self.auth_info["fitnessId"] = fitness_id
            print(f"✅ 找到体测计划: {plans[0]['fitnessName']} (ID: {fitness_id})")
            print(f"🔍 fitnessId类型: {type(fitness_id)}")
            
            # 步骤3: 开始跑步
            if not self.start_running():
                return False
            
            # 步骤4: 模拟跑步过程
            print(f"\n🏃 开始模拟跑步，目标距离: {target_distance/1000:.1f}km")
            if mode == "track":
                print("💡 使用跑道轨迹生成算法，配速6.5分钟/公里")
            else:
                print("💡 使用随机轨迹生成算法")
            print("按 Ctrl+C 可以提前结束跑步")
            
            self.running_state["is_running"] = True
            start_time = time.time()
            
            try:
                while self.running_state["distance"] < target_distance and self.running_state["is_running"]:
                    self.heartbeat(keep_running=True)
                    time.sleep(1)  # 每秒更新一次
                    
                    # 检查是否达到目标距离
                    if self.running_state["distance"] >= target_distance:
                        break
                        
            except KeyboardInterrupt:
                print("\n\n⏹️  用户中断跑步")
                self.running_state["is_running"] = False
            
            # 步骤5: 结束跑步
            print(f"\n\n🏁 跑步完成！")
            print(f"总时长: {self.format_time(self.running_state['time'])}")
            print(f"总距离: {self.running_state['distance']/1000:.2f}km")
            print(f"平均配速: {(self.running_state['time']/60)/(self.running_state['distance']/1000):.2f}min/km")
            
            if self.end_running():
                print("🎉 校园跑完成并成功提交！")
                return True
            else:
                print("❌ 提交跑步数据失败")
                return False
                
        except Exception as e:
            print(f"❌ 程序执行异常: {str(e)}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="校园跑程序")
    parser.add_argument("--username", required=True, help="用户名（手机号）")
    parser.add_argument("--password", required=True, help="密码")
    parser.add_argument("--distance", type=int, default=5000, help="目标距离(米，默认5000)")
    parser.add_argument("--school", choices=["上海大学", "上海中医药大学"], default="上海大学", help="学校选择")
    parser.add_argument("--mode", choices=["track", "random"], default="track", help="轨迹模式：track=跑道轨迹，random=随机轨迹")
    
    args = parser.parse_args()
    
    # 创建程序实例
    campus_fly = CampusFly()
    
    # 运行程序
    success = campus_fly.run_campus_fly(
        username=args.username,
        password=args.password,
        target_distance=args.distance,
        school=args.school,
        mode=args.mode
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
