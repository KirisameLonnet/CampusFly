#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园跑欺骗程序 - 基于API的自动化跑步系统
基于华体运动会逆向分析结果开发

作者: AI Assistant
日期: 2025年1月
"""

import requests
import json
import time
import hashlib
import random
import math
from urllib.parse import urlencode
from typing import Dict, List, Tuple, Optional
import argparse
import sys

class CampusFlyCheat:
    """校园跑欺骗程序主类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })
        
        # 硬编码的API域名配置
        self.base_urls = {
            "fitness": "https://fitness.iyundong.me",
            "fitUrl": "https://edu.ymq.me", 
            "user": "https://user.iyundong.me",
            "userymq": "https://user.ymq.me"
        }
        
        # 上海大学配置
        self.agency_id = 1977  # 上海大学
        self.max_distance = 8000  # 8公里限制
        
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
    
    def generate_signature(self, params: Dict, timestamp: int, token: str) -> str:
        """生成API签名（MD5）"""
        # 合并参数
        all_params = {
            "snTime": timestamp,
            "token": token
        }
        all_params.update(params)
        
        # 按键排序并拼接
        sorted_keys = sorted(all_params.keys())
        sign_string = "&".join([f"{key}={all_params[key]}" for key in sorted_keys])
        
        # MD5加密
        return hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    
    def make_request(self, url: str, data: Dict, token: str = "") -> Dict:
        """发送API请求"""
        timestamp = int(time.time() * 1000)
        
        # 生成签名
        signature = self.generate_signature(data, timestamp, token)
        
        # 构造请求头
        headers = {
            "Accept": "*/*;",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Sn-Verify": signature
        }
        
        # 构造请求体
        request_body = {
            "body": data,
            "header": {
                "token": token,
                "snTime": timestamp,
                "sn": signature,
                "from": "wx"
            }
        }
        
        try:
            response = self.session.post(url, json=request_body, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API请求失败: {e}")
            return {"status": -1, "message": str(e)}
    
    def get_login_url(self) -> str:
        """获取登录页面URL"""
        timestamp = int(time.time() * 1000)
        return f"https://edu.ymq.me/wechat/#/user/mobile/user/mini?agencyId={self.agency_id}&t={timestamp}"
    
    def verify_token(self, token: str) -> bool:
        """验证token有效性"""
        url = f"{self.base_urls['userymq']}/public/token/renewal"
        data = {"token": token}
        
        response = self.make_request(url, data, token)
        return response.get("status") == 0
    
    def check_stroll_abnormal(self, token: str, fitness_id: str) -> Dict:
        """检查跑步异常状态"""
        url = f"{self.base_urls['fitUrl']}/webservice/wechat/student/stroll/checkStrollAbnormal.do"
        data = {"fitnessId": fitness_id}
        
        return self.make_request(url, data, token)
    
    def make_stroll(self, token: str, fitness_id: str) -> Dict:
        """创建/恢复跑步记录"""
        url = f"{self.base_urls['fitUrl']}/webservice/wechat/student/stroll/makeStroll.do"
        data = {"fitnessId": fitness_id}
        
        return self.make_request(url, data, token)
    
    def save_stroll(self, token: str, stroll_data: Dict) -> Dict:
        """保存跑步数据（中途保存）"""
        url = f"{self.base_urls['fitUrl']}/webservice/wechat/student/stroll/saveStroll.do"
        return self.make_request(url, stroll_data, token)
    
    def submit_stroll(self, token: str, stroll_data: Dict) -> Dict:
        """提交跑步记录（最终提交）"""
        url = f"{self.base_urls['fitUrl']}/webservice/wechat/student/stroll/submitStroll.do"
        return self.make_request(url, stroll_data, token)
    
    def is_in_geo_fence(self, lat: float, lng: float) -> bool:
        """判断坐标是否在电子围栏内"""
        for fence in self.geo_fences:
            if (fence["lat"][0] < lat < fence["lat"][1] and 
                fence["lng"][0] < lng < fence["lng"][1]):
                return True
        return False
    
    def generate_route_points(self, target_distance: int = 5000) -> List[Dict]:
        """生成符合电子围栏规则的跑步路线点"""
        print(f"正在生成 {target_distance/1000:.1f}km 的跑步路线...")
        
        # 选择一个围栏区域作为主要跑步区域
        main_fence = random.choice(self.geo_fences)
        print(f"选择主要跑步区域: {main_fence['name']}")
        
        # 在围栏内生成起点
        start_lat = random.uniform(main_fence["lat"][0] + 0.0001, main_fence["lat"][1] - 0.0001)
        start_lng = random.uniform(main_fence["lng"][0] + 0.0001, main_fence["lng"][1] - 0.0001)
        
        points = [{"y": start_lat, "x": start_lng}]
        current_lat, current_lng = start_lat, start_lng
        total_distance = 0
        
        # 生成路线点（每10米一个点）
        point_interval = 0.0001  # 大约10米的经纬度差
        points_needed = target_distance // 10
        
        for i in range(points_needed):
            # 随机选择方向（保持大部分点在围栏内）
            if random.random() < 0.8:  # 80%概率在围栏内
                # 在围栏内移动
                lat_offset = random.uniform(-point_interval, point_interval)
                lng_offset = random.uniform(-point_interval, point_interval)
            else:  # 20%概率在围栏外（但不超过50%）
                # 在围栏外移动
                lat_offset = random.uniform(-point_interval * 2, point_interval * 2)
                lng_offset = random.uniform(-point_interval * 2, point_interval * 2)
            
            new_lat = current_lat + lat_offset
            new_lng = current_lng + lng_offset
            
            # 确保新点在围栏内（如果80%概率选择围栏内）
            if random.random() < 0.8:
                while not self.is_in_geo_fence(new_lat, new_lng):
                    lat_offset = random.uniform(-point_interval, point_interval)
                    lng_offset = random.uniform(-point_interval, point_interval)
                    new_lat = current_lat + lat_offset
                    new_lng = current_lng + lng_offset
            
            points.append({"y": new_lat, "x": new_lng})
            current_lat, current_lng = new_lat, new_lng
            
            # 计算距离（简化计算）
            total_distance += 10
        
        print(f"生成了 {len(points)} 个路线点，总距离约 {total_distance/1000:.1f}km")
        return points
    
    def calculate_distance(self, points: List[Dict]) -> int:
        """计算路线总距离（米）"""
        if len(points) < 2:
            return 0
        
        total_distance = 0
        for i in range(1, len(points)):
            lat1, lng1 = points[i-1]["y"], points[i-1]["x"]
            lat2, lng2 = points[i]["y"], points[i]["x"]
            
            # 简化的距离计算
            lat_diff = lat2 - lat1
            lng_diff = lng2 - lng1
            distance = math.sqrt(lat_diff**2 + lng_diff**2) * 111000  # 转换为米
            total_distance += distance
        
        return int(total_distance)
    
    def create_stroll_data(self, points: List[Dict], distance: int) -> Dict:
        """创建跑步数据"""
        return {
            "fitnessId": self.auth_info["fitnessId"],
            "gradeType": self.auth_info["gradeType"],
            "strollDistance": min(distance, self.max_distance),  # 限制最大距离
            "submitTimestamp": int(time.time() * 1000),
            "strollRecordId": self.auth_info["strollRecordId"],
            "strollDetail": json.dumps({"map": points})
        }
    
    def simulate_running(self, target_distance: int = 5000) -> bool:
        """模拟跑步过程"""
        print(f"\n开始模拟跑步，目标距离: {target_distance/1000:.1f}km")
        
        # 生成路线点
        points = self.generate_route_points(target_distance)
        actual_distance = self.calculate_distance(points)
        
        print(f"实际生成距离: {actual_distance/1000:.1f}km")
        
        # 创建跑步数据
        stroll_data = self.create_stroll_data(points, actual_distance)
        
        # 中途保存（模拟跑步过程）
        print("正在保存跑步数据...")
        save_result = self.save_stroll(self.auth_info["token"], stroll_data)
        if save_result.get("status") != 0:
            print(f"保存跑步数据失败: {save_result.get('message')}")
            return False
        
        # 最终提交
        print("正在提交跑步记录...")
        submit_result = self.submit_stroll(self.auth_info["token"], stroll_data)
        if submit_result.get("status") != 0:
            print(f"提交跑步记录失败: {submit_result.get('message')}")
            return False
        
        print("✅ 跑步完成并成功提交！")
        print(f"提交距离: {stroll_data['strollDistance']/1000:.1f}km")
        print(f"轨迹点数: {len(points)}")
        
        return True
    
    def run_cheat(self, phone_number: str, fitness_id: str, target_distance: int = 5000):
        """运行欺骗程序主流程"""
        print("=" * 60)
        print("🏃‍♂️ 校园跑欺骗程序启动")
        print("=" * 60)
        print(f"手机号: {phone_number}")
        print(f"体测计划ID: {fitness_id}")
        print(f"目标距离: {target_distance/1000:.1f}km")
        print(f"学校: 上海大学 (ID: {self.agency_id})")
        print("=" * 60)
        
        # 步骤1: 显示登录URL
        login_url = self.get_login_url()
        print(f"\n📱 请使用手机号 {phone_number} 登录:")
        print(f"登录URL: {login_url}")
        print("\n请在浏览器中打开上述URL，完成登录后获取token")
        
        # 步骤2: 获取token
        token = input("\n请输入获取到的token: ").strip()
        if not token:
            print("❌ 未提供token，程序退出")
            return False
        
        # 步骤3: 验证token
        print("\n🔐 验证token有效性...")
        if not self.verify_token(token):
            print("❌ Token验证失败，请重新登录")
            return False
        
        print("✅ Token验证成功！")
        self.auth_info["token"] = token
        self.auth_info["fitnessId"] = fitness_id
        
        # 步骤4: 检查跑步状态
        print("\n🔍 检查跑步异常状态...")
        abnormal_check = self.check_stroll_abnormal(token, fitness_id)
        if abnormal_check.get("status") != 0:
            print(f"❌ 检查跑步状态失败: {abnormal_check.get('message')}")
            return False
        
        print("✅ 跑步状态检查完成")
        
        # 步骤5: 创建跑步记录
        print("\n🏃 创建跑步记录...")
        make_result = self.make_stroll(token, fitness_id)
        if make_result.get("status") != 0:
            print(f"❌ 创建跑步记录失败: {make_result.get('message')}")
            return False
        
        # 保存跑步记录信息
        detail = make_result.get("detail", {})
        self.auth_info["strollRecordId"] = detail.get("strollRecordId", 0)
        self.auth_info["gradeType"] = detail.get("gradeType", 0)
        
        print("✅ 跑步记录创建成功")
        
        # 步骤6: 模拟跑步
        success = self.simulate_running(target_distance)
        
        if success:
            print("\n🎉 校园跑欺骗完成！")
            print("=" * 60)
        else:
            print("\n❌ 校园跑欺骗失败")
        
        return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="校园跑欺骗程序")
    parser.add_argument("--phone", required=True, help="手机号")
    parser.add_argument("--fitness-id", required=True, help="体测计划ID")
    parser.add_argument("--distance", type=int, default=5000, help="目标距离(米，默认5000)")
    
    args = parser.parse_args()
    
    # 创建欺骗程序实例
    cheat = CampusFlyCheat()
    
    # 运行欺骗程序
    success = cheat.run_cheat(args.phone, args.fitness_id, args.distance)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
